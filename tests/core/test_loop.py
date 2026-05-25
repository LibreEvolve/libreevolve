import tempfile
import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from libreevolve.core.config import Config
from libreevolve.core.loop import evolve, VALID_THRESHOLD
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

def test_returns_program():
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        best = evolve(_problem(), Config(max_generations=2,
                                        log_dir=tempfile.mkdtemp(), problem_name="t"))
    assert best is not None and isinstance(best.fitness, float)

def test_threshold_is_zero():
    assert VALID_THRESHOLD == 0.0

def test_invalid_diff_not_archived():
    with patch("libreevolve.core.loop.build_llm", return_value=_llm("no diff here")):
        best = evolve(_problem(), Config(max_generations=1,
                                        log_dir=tempfile.mkdtemp(), problem_name="t"))
    assert best.fitness == 1.0  # seed still best

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


def test_loop_logs_prompt_program_id_and_prompt_history():
    tmpdir = tempfile.mkdtemp()
    with patch("libreevolve.core.loop.build_llm", return_value=_llm()):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    run_dir = Path(tmpdir) / "t"
    records = [json.loads(l) for l in (run_dir / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert "prompt_program_id" in child["metadata"]
    assert (run_dir / "prompt_history.jsonl").exists()


def test_loop_logs_mutation_backend_index():
    tmpdir = tempfile.mkdtemp()
    llm = _llm()
    llm.generate.return_value = ("<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE", 2)
    with patch("libreevolve.core.loop.build_llm", return_value=llm):
        evolve(_problem(), Config(max_generations=1, log_dir=tmpdir, problem_name="t"))

    records = [json.loads(l) for l in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()]
    child = records[-1]
    assert child["metadata"]["backend_idx"] == 2


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
