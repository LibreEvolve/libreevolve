import tempfile
import hashlib
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest
from libreevolve.core.candidate import CandidateWorkspace
from libreevolve.core.config import Config
from libreevolve.core.loop import evolve, VALID_THRESHOLD
from libreevolve.plugins.deep_research import DeepResearchPlugin
from libreevolve.problems.loader import Problem

def _problem(src="def evaluate(c): return {'score':1.0,'is_valid':True}"):
    d = Path(tempfile.mkdtemp())
    (d/"validate.py").write_text(src)
    return Problem(name="t", task_description="t",
                   metrics=[{"name":"score","primary":True,"bounds":[0.0,1.0]}],
                   primary_metric="score", primary_bounds=(0.0,1.0),
                   validate_path=d/"validate.py", initial_programs=["x=1"], problem_dir=d)

def _llm(diff="<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"):
    m = MagicMock(); m.generate.return_value = (diff, 0); return m


class _TelemetryLLM:
    def __init__(self, diff="<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"):
        self.diff = diff
        self.last_call = None
        self.calls = []

    def generate(self, prompt, role="mutation"):
        self.last_call = {
            "id": f"call-{len(self.calls)}",
            "role": role,
            "backend_idx": 0,
            "backend_name": "fake/model",
            "prompt_chars": len(prompt),
            "output_chars": len(self.diff),
            "status": "ok",
        }
        self.calls.append(self.last_call)
        return self.diff, 0

    def record_reward(self, idx, reward):
        pass


def test_returns_program():
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        best = evolve(_problem(), Config(max_generations=2,
                                        log_dir=tempfile.mkdtemp(), problem_name="t"))
    assert best is not None and isinstance(best.fitness, float)


def test_loop_logs_llm_call_telemetry_on_candidate():
    tmpdir = tempfile.mkdtemp()
    llm = _TelemetryLLM()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["metadata"]["llm_calls"][0]["role"] == "mutation"
    assert child["metadata"]["llm_calls"][0]["backend_name"] == "fake/model"


def test_loop_records_proposal_metadata_when_enabled():
    tmpdir = tempfile.mkdtemp()
    response = """IDEA: Change x to the accepted value.
RATIONALE: The validator expects x=2.
HYPOTHESIS: The candidate should remain valid.
<<<SEARCH
x=1
===
x=2
>>>REPLACE"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                capture_proposal_metadata=True,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["metadata"]["proposal"]["idea"] == "Change x to the accepted value."
    assert child["metadata"]["proposal"]["rationale"] == "The validator expects x=2."
    assert child["metadata"]["proposal"]["hypothesis"] == "The candidate should remain valid."
    assert "IDEA:" in child["metadata"]["prompt"]


def test_loop_strips_proposal_metadata_before_full_replacement():
    tmpdir = tempfile.mkdtemp()
    response = """IDEA: Replace the whole primary file.
RATIONALE: Full mode should apply code only.
HYPOTHESIS: The stored candidate code should omit metadata.
x=2
"""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm(response)):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
                capture_proposal_metadata=True,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["code"] == "x=2"
    assert child["metadata"]["diff"] == response
    assert child["metadata"]["proposal"]["idea"] == "Replace the whole primary file."


def test_loop_records_normalized_metrics_and_selection_score():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c): return {'accuracy': 0.8, 'latency': 20.0, 'is_valid': True}\n",
        encoding="utf-8",
    )
    problem = Problem(
        name="t",
        task_description="balance metrics",
        metrics=[
            {"name": "accuracy", "primary": True, "bounds": [0.0, 1.0]},
            {"name": "latency", "direction": "minimize", "bounds": [0.0, 100.0]},
        ],
        primary_metric="accuracy",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(problem, Config(max_generations=0, log_dir=tmpdir, problem_name="t"))

    record = json.loads((Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()[0])
    assert record["metadata"]["normalized_metrics"] == {"accuracy": 0.8, "latency": 0.8}
    assert record["metadata"]["selection_score"] == 0.8
    assert record["metadata"]["selection_policy"]["type"] == "mean_normalized_declared_metrics"
    assert record["metadata"]["archive_admission"]["selection_score"] == 0.8


def test_evaluation_budget_stops_before_llm_mutation():
    tmpdir = tempfile.mkdtemp()
    llm = _llm()

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        best = evolve(
            _problem(),
            Config(
                max_generations=5,
                max_evaluations=1,
                log_dir=tmpdir,
                problem_name="t",
            ),
        )

    assert best is not None
    llm.generate.assert_not_called()
    run_dir = Path(tmpdir) / "t"
    records = [json.loads(line) for line in (run_dir / "history.jsonl").read_text().splitlines()]
    assert len(records) == 1
    assert records[0]["metadata"]["budget"]["consumed"]["evaluations"] == 1
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["config"]["max_evaluations"] == 1
    assert manifest["runtime"]["stop_reason"] == "max_evaluations"
    assert manifest["runtime"]["consumed"]["evaluations"] == 1
    assert manifest["runtime"]["consumed"]["seed_evaluations"] == 1
    assert manifest["runtime"]["consumed"]["candidate_evaluations"] == 0

def test_threshold_is_zero():
    assert VALID_THRESHOLD == 0.0

def test_invalid_diff_not_archived():
    tmpdir = tempfile.mkdtemp()
    with patch("libreevolve.core.loop.build_llm", return_value=_llm("no diff here")):
        best = evolve(_problem(), Config(max_generations=1,
                                        log_dir=tmpdir, problem_name="t"))
    assert best.fitness == 1.0  # seed still best
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    assert child["metadata"]["archive_admission"]["admitted"] is False
    assert child["metadata"]["archive_admission"]["reason"] == "invalid_evaluation"
    failure_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failure_records[-1]["diff_error"] == "no_diff_blocks"
    assert child["metadata"]["failure_record"]["diff_error"] == "no_diff_blocks"


def test_failed_mutation_memory_is_rendered_in_next_prompt():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("no diff here", 0),
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=2, log_dir=tmpdir, problem_name="t"))

    second_prompt = llm.generate.call_args_list[1].args[0]
    assert "RECENTLY FAILED" in second_prompt
    assert "diff_error=no_diff_blocks" in second_prompt


def test_loop_logs_non_primary_workspace_failure():
    tmpdir = tempfile.mkdtemp()
    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "from pathlib import Path\n"
        "def evaluate(code, workspace_path):\n"
        "    helper = Path(workspace_path, 'helper.py').read_text()\n"
        "    return {'score': 1.0 if 'value = 1' in helper else -1.0, "
        "'is_valid': 'value = 1' in helper}\n"
    )
    problem = Problem(
        name="t",
        task_description="keep helper valid",
        metrics=[{"name": "score", "primary": True, "bounds": [-1.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(-1.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["from helper import value\n"],
        problem_dir=d,
        initial_workspaces=[
            CandidateWorkspace(
                files={"main.py": "from helper import value\n", "helper.py": "value = 1\n"},
                primary_file="main.py",
            )
        ],
    )
    llm = _llm("<<<FILE helper.py\nvalue = 0\n>>>FILE")

    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t", mutation_mode="full"),
        )

    failure_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert failure_records[-1]["changed_files"] == ["helper.py"]
    assert failure_records[-1]["score"] == -0.1

def test_plugins_called():
    from libreevolve.plugins.base import PluginBase
    calls = []
    class T(PluginBase):
        def on_generation_start(self, g, db): calls.append(("start", g))
        def on_generation_end(self, g, b): calls.append(("end", g))
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(_problem(), Config(max_generations=2,
                                  log_dir=tempfile.mkdtemp(), problem_name="t"),
               plugins=[T()])
    assert ("start", 0) in calls and ("end", 0) in calls


def test_plugin_score_composition_is_logged_for_multiple_plugins():
    tmpdir = tempfile.mkdtemp()

    class AddMetricPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            program.metrics["plugin_metric"] = 1
            return score + 0.1

    class PenalizePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            return score - 0.2

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[AddMetricPlugin(), PenalizePlugin()],
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    composition = records[-1]["metadata"]["score_composition"]
    assert composition["initial_fitness"] == 1.0
    assert composition["final_fitness"] == pytest.approx(0.9)
    assert composition["diverged_from_evaluation"] is True
    assert [p["plugin"] for p in composition["plugins"]] == ["AddMetricPlugin", "PenalizePlugin"]
    assert composition["plugins"][0]["metrics_added"] == ["plugin_metric"]


def test_invalid_plugin_score_is_rejected_and_logged():
    tmpdir = tempfile.mkdtemp()

    class BadScorePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            return float("inf")

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[BadScorePlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    plugin_record = child["metadata"]["score_composition"]["plugins"][0]
    assert child["fitness"] == 1.0
    assert plugin_record["accepted"] is False
    assert plugin_record["error"] == "non_finite_plugin_score"


def test_plugin_boosted_invalid_candidate_is_not_archived():
    tmpdir = tempfile.mkdtemp()

    class BoostPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            return 1.0

    with patch("libreevolve.core.loop.build_llm", return_value=_llm("no diff here")):
        best = evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[BoostPlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert best.id == records[0]["id"]
    assert child["fitness"] == 1.0
    assert child["evaluation"]["is_valid"] is False
    assert child["metadata"]["archive_admission"]["admitted"] is False
    assert child["metadata"]["archive_admission"]["reason"] == "invalid_evaluation"


def test_plugin_penalized_valid_candidate_below_threshold_not_archived():
    tmpdir = tempfile.mkdtemp()

    class PenalizePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            return -0.5

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[PenalizePlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert child["evaluation"]["is_valid"] is True
    assert child["metadata"]["archive_admission"]["admitted"] is False
    assert child["metadata"]["archive_admission"]["reason"] == "below_threshold"


def test_loop_logs_prompt_program_id_and_prompt_history():
    tmpdir = tempfile.mkdtemp()
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(l) for l in (run_dir / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert "prompt_program_id" in child["metadata"]
    assert (run_dir / "prompt_history.jsonl").exists()


def test_loop_logs_normalized_prompt_reward_policy_metadata():
    tmpdir = tempfile.mkdtemp()
    problem = _problem(
        "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.5,"
        "'is_valid': True}"
    )
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                prompt_reward_mode="improvement",
                prompt_reward_bounds=[-1.0, 1.0],
                prompt_explore_coeff=0.0,
            ),
        )

    run_dir = Path(tmpdir) / "t"
    events = [
        json.loads(line)
        for line in (run_dir / "prompt_history.jsonl").read_text().splitlines()
    ]
    score_event = next(event for event in events if event["event"] == "score")
    reward = score_event["program"]["metadata"]["last_prompt_reward"]
    assert reward["mode"] == "improvement"
    assert reward["raw"] == 0.5
    assert reward["normalized"] == 0.75
    assert reward["bounds"] == [-1.0, 1.0]
    assert score_event["program"]["metadata"]["last_candidate_score"] == 1.0
    assert score_event["program"]["metadata"]["last_parent_score"] == 0.5
    manifest = json.loads((run_dir / "manifest.json").read_text())
    assert manifest["config"]["prompt_reward_mode"] == "improvement"
    assert manifest["config"]["prompt_reward_bounds"] == [-1.0, 1.0]
    assert manifest["config"]["prompt_explore_coeff"] == 0.0
    evaluator_source = manifest["problem"]["evaluator_sources"][0]
    assert evaluator_source["relative_path"] == "validate.py"
    expected_hash = hashlib.sha256((problem.problem_dir / "validate.py").read_bytes()).hexdigest()
    assert evaluator_source["sha256"] == expected_hash
    assert manifest["provenance"]["problem"]["tree_hash"]
    assert manifest["provenance"]["source"]["tree_hash"]
    assert "git" in manifest["provenance"]


def test_prompt_reward_uses_plugin_adjusted_score_with_multiple_metrics():
    tmpdir = tempfile.mkdtemp()

    class BoostPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def build_extra_context(self, parent, inspirations): return ""
        def on_evaluated(self, program, score):
            program.metrics["plugin_bonus"] = 0.25
            return score + 0.25

    d = Path(tempfile.mkdtemp())
    (d / "validate.py").write_text(
        "def evaluate(c): return {'score': 0.4, 'aux': 0.2, 'is_valid': True}"
    )
    problem = Problem(
        name="t",
        task_description="t",
        metrics=[
            {"name": "score", "primary": True, "bounds": [0.0, 1.0]},
            {"name": "aux", "bounds": [0.0, 1.0]},
        ],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=d / "validate.py",
        initial_programs=["x=1"],
        problem_dir=d,
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            problem,
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[BoostPlugin()],
        )

    events = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "prompt_history.jsonl").read_text().splitlines()
    ]
    score_event = next(event for event in events if event["event"] == "score")
    reward = score_event["program"]["metadata"]["last_prompt_reward"]
    assert reward["raw"] == 0.65
    assert reward["normalized"] == 0.65
    assert score_event["program"]["metadata"]["last_candidate_score"] == 0.65


def test_loop_logs_mutation_backend_index():
    tmpdir = tempfile.mkdtemp()
    llm = _llm()
    llm.generate.return_value = ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 2)
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert child["metadata"]["backend_idx"] == 2


def test_loop_logs_archive_admission_for_seed_and_child():
    tmpdir = tempfile.mkdtemp()
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    seed_admission = records[0]["metadata"]["archive_admission"]
    child_admission = records[-1]["metadata"]["archive_admission"]
    assert seed_admission["admitted"] is True
    assert seed_admission["island_id"] == 0
    assert seed_admission["cell"] is not None
    assert child_admission["admitted"] is True
    assert child_admission["program_id"] == records[-1]["id"]


def test_loop_excludes_selected_parent_from_inspirations():
    tmpdir = tempfile.mkdtemp()
    seen = []

    class CapturePlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            seen.append((parent.id, [program.id for program in inspirations]))
            return ""

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[CapturePlugin()],
        )

    assert seen
    parent_id, inspiration_ids = seen[0]
    assert parent_id not in inspiration_ids


def test_loop_records_per_plugin_prompt_context():
    tmpdir = tempfile.mkdtemp()

    class ContextPlugin:
        def on_generation_start(self, g, db): pass
        def on_generation_end(self, g, b): pass
        def on_evaluated(self, program, score): return score
        def build_extra_context(self, parent, inspirations):
            return "[PLUGIN CONTEXT]\nPrefer the simple branch.\n"
        def prompt_context_metadata(self):
            return {"strategy": "static_guidance"}

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[ContextPlugin()],
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    plugin_context = child["metadata"]["plugin_context"]

    assert "[PLUGIN CONTEXT]" in child["metadata"]["prompt"]
    assert plugin_context[0]["plugin"] == "ContextPlugin"
    assert plugin_context[0]["module"] == __name__
    assert plugin_context[0]["parent_id"] == child["parent_id"]
    assert plugin_context[0]["context"] == "[PLUGIN CONTEXT]\nPrefer the simple branch.\n"
    assert plugin_context[0]["chars"] == len(plugin_context[0]["context"])
    assert plugin_context[0]["sha256"] == hashlib.sha256(
        plugin_context[0]["context"].encode("utf-8")
    ).hexdigest()
    assert plugin_context[0]["emitted"] is True
    assert plugin_context[0]["metadata"] == {"strategy": "static_guidance"}


def test_manifest_summarizes_retrieval_events():
    tmpdir = tempfile.mkdtemp()
    plugin = DeepResearchPlugin(
        search_fn=lambda q: {
            "status": "ok",
            "synthesis": "retrieved context",
            "sources": [{"id": "paper-1"}, {"id": "paper-2"}],
        }
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[plugin],
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    retrieval = manifest["runtime"]["retrieval"]
    assert retrieval["events"] == 1
    assert retrieval["by_plugin"]["DeepResearchPlugin"] == {
        "events": 1,
        "ok": 1,
        "empty": 0,
        "error": 0,
        "sources": 2,
    }
    summary = retrieval["event_summaries"][0]
    assert summary["plugin"] == "DeepResearchPlugin"
    assert summary["provider"] == "custom"
    assert summary["status"] == "ok"
    assert summary["source_count"] == 2
    assert summary["synthesis_sha256"]


def test_manifest_summarizes_retrieval_error_types():
    tmpdir = tempfile.mkdtemp()
    plugin = DeepResearchPlugin(
        search_fn=lambda q: {
            "status": "error",
            "error_type": "network_error",
            "error": "offline",
        }
    )

    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(
            _problem(),
            Config(max_generations=1, log_dir=tmpdir, problem_name="t"),
            plugins=[plugin],
        )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    summary = manifest["runtime"]["retrieval"]["event_summaries"][0]
    assert summary["status"] == "error"
    assert summary["error_type"] == "network_error"
    assert summary["error"] == "offline"


def test_loop_renders_full_mode_prompt_instructions():
    tmpdir = tempfile.mkdtemp()
    llm = _llm("x=2")
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                mutation_mode="full",
            ),
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert child["metadata"]["mutation_mode"] == "full"
    assert "Mutation mode: full" in child["metadata"]["prompt"]
    assert "Return full replacement code, not SEARCH/REPLACE diffs." in child["metadata"]["prompt"]


def test_meta_prompt_evolution_adds_mutated_prompt_template():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        ("[SYSTEM]\n{task}\n{context}\n{parent_score}\n{parent_metrics}\n{parent_feedback}\n{parent_code}\n{inspirations}\n{extra_context}\n{recent_failures}", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(
            max_generations=1,
            log_dir=tmpdir,
            problem_name="t",
            meta_prompt_evolution=True,
            meta_prompt_interval=1,
        ))

    events = [
        json.loads(l)["event"]
        for l in (Path(tmpdir) / "t" / "prompt_history.jsonl").read_text().splitlines()
    ]
    assert events.count("add") == 2


def test_meta_prompt_evolution_rejects_invalid_mutated_prompt_template():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        ("[SYSTEM]\n{unknown}", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(
            max_generations=1,
            log_dir=tmpdir,
            problem_name="t",
            meta_prompt_evolution=True,
            meta_prompt_interval=1,
        ))

    run_dir = Path(tmpdir) / "t"
    events = [
        json.loads(l)["event"]
        for l in (run_dir / "prompt_history.jsonl").read_text().splitlines()
    ]
    invalid = [
        json.loads(l)
        for l in (run_dir / "prompt_history_invalid.jsonl").read_text().splitlines()
    ]
    assert events == ["add", "score", "penalty"]
    assert invalid[0]["event"] == "reject"
    assert "unknown" in invalid[0]["error"]


def test_critique_revises_mutation_before_evaluation():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=0\n>>>REPLACE", 0),
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        problem = _problem(
            "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.5,"
            "'is_valid':True}"
        )
        best = evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                critique_enabled=True,
            ),
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert best.code == "x=2"
    assert child["metadata"]["critique"]["original_diff"].endswith("x=0\n>>>REPLACE")
    assert child["metadata"]["critique"]["accepted_revision"] is True
    assert child["metadata"]["critique"]["selected_diff"] == "revised"


def test_invalid_critique_revision_falls_back_to_original_mutation():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        ("this is not a mutation", 0),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        problem = _problem(
            "def evaluate(c): return {'score': 1.0 if 'x=2' in c else 0.0,"
            "'is_valid':True}"
        )
        best = evolve(
            problem,
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                critique_enabled=True,
            ),
        )

    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    child = records[-1]
    critique = child["metadata"]["critique"]
    assert best.code == "x=2"
    assert child["metadata"]["diff"].endswith("x=2\n>>>REPLACE")
    assert critique["accepted_revision"] is False
    assert critique["selected_diff"] == "original"
    assert critique["revised_diff_error"] == "no_diff_blocks"
    assert critique["original_diff_error"] is None
    assert critique["fallback_reason"] == "invalid_revised_diff"


def test_loop_applies_llm_feedback_to_candidate_score():
    tmpdir = tempfile.mkdtemp()
    llm = MagicMock()
    llm.generate.side_effect = [
        ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 0),
        ('{"score": 0.5, "feedback": "simple"}', 1),
    ]
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        best = evolve(
            _problem(),
            Config(
                max_generations=1,
                log_dir=tmpdir,
                problem_name="t",
                llm_feedback=[
                    {"name": "simplicity", "metric": "simplicity", "weight": 0.2}
                ],
            ),
        )

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert best.fitness == 1.1
    assert child["metrics"]["simplicity"] == 0.5
    assert child["evaluation"]["metadata"]["llm_feedback"][0]["name"] == "simplicity"
