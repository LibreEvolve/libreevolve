from __future__ import annotations

import json
import random
import threading
from pathlib import Path
from unittest.mock import patch

import pytest

import libreevolve.core.loop as loop_module
from libreevolve.core.config import Config
from libreevolve.core.loop import evolve
from libreevolve.plugins.base import PluginBase
from libreevolve.problems.loader import Problem


DIFF = "<<<SEARCH\nx=1\n===\nx=2\n>>>REPLACE"


def _problem(tmp_path: Path, *, score_by_code: bool = True) -> Problem:
    problem_dir = tmp_path / "problem"
    problem_dir.mkdir(parents=True)
    (problem_dir / "validate.py").write_text(
        "def evaluate(code):\n"
        "    valid = 'INVALID' not in code\n"
        "    score = 1.0 if 'x=2' in code else 0.2 if 'x=1.0' in code else 0.25\n"
        "    return {'score': score, 'is_valid': valid}\n",
        encoding="utf-8",
    )
    if not score_by_code:
        (problem_dir / "validate.py").write_text(
            "def evaluate(code):\n"
            "    return {'score': 1.0, 'is_valid': True}\n",
            encoding="utf-8",
        )
    return Problem(
        name="characterization",
        task_description="Improve x.",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=problem_dir / "validate.py",
        initial_programs=["x=1\n"],
        problem_dir=problem_dir,
    )


def _config(tmp_path: Path, name: str, **overrides) -> Config:
    values = {
        "max_generations": 1,
        "mutation_mode": "diff",
        "log_dir": str(tmp_path / "runs"),
        "problem_name": name,
    }
    values.update(overrides)
    return Config(**values)


def _rows(run_dir: Path, filename: str) -> list[dict]:
    path = run_dir / filename
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


class _FakeLLM:
    def __init__(self, responses=(DIFF,)):
        self.responses = list(responses)
        self.response_index = 0
        self.call_history: list[dict] = []
        self.last_call = None
        self._sink = None
        self._lock = threading.Lock()
        self.namespace = "fake"

    @property
    def call_history_retention(self):
        return {"total_records": len(self.call_history), "dropped_records": 0}

    def set_call_record_sink(self, sink):
        self._sink = sink

    def set_call_id_namespace(self, namespace):
        self.namespace = namespace

    def generate(self, prompt, role="mutation"):
        response = self.responses[min(self.response_index, len(self.responses) - 1)]
        self.response_index += 1
        with self._lock:
            sequence = len(self.call_history) + 1
            call = {
                "id": f"{self.namespace}:call:{sequence}",
                "sequence_id": sequence,
                "role": role,
                "backend_idx": 0,
                "status": "ok",
                "prompt_chars": len(prompt),
                "output_chars": len(response),
            }
            self.call_history.append(call)
            self.last_call = call
        if self._sink is not None:
            self._sink(call)
        return response, 0

    def record_reward(self, idx, reward, call_id=None):
        return {
            "record_type": "reward",
            "call_id": call_id,
            "backend_idx": idx,
            "reward": reward,
            "reward_raw": reward,
            "rewarded": True,
        }


class _TracePlugin(PluginBase):
    def __init__(self, trace):
        self.trace = trace

    def on_generation_start(self, generation, db):
        self.trace.append(("generation_start", generation))

    def build_extra_context(self, parent, inspirations):
        self.trace.append(("context", parent.id))
        return "trace context"

    def on_evaluated(self, program, score):
        self.trace.append(("evaluated", program.id))
        return score

    def on_generation_end(self, generation, best):
        self.trace.append(("generation_end", generation))


def test_zero_generation_has_seed_only_terminal_trace(tmp_path):
    problem = _problem(tmp_path)
    run_dir = tmp_path / "runs" / "zero"

    with patch.object(loop_module, "build_llm", side_effect=AssertionError("provider")):
        best = evolve(problem, _config(tmp_path, "zero", max_generations=0))

    history = _rows(run_dir, "history.jsonl")
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    runtime = manifest["runtime"]

    assert best.id == history[0]["id"]
    assert len(history) == 1
    assert history[0]["generation"] == 0
    assert runtime["status"] == "completed"
    assert runtime["consumed"]["generations_started"] == 0
    assert runtime["history"]["controller_state"]["pending_work"] == {
        "queued_proposals": 0,
        "running_proposals": 0,
        "queued_evaluations": 0,
        "running_evaluations": 0,
        "in_flight_llm_calls": 0,
        "pending_archive_admissions": 0,
        "partially_completed_generation": False,
    }


def test_multiple_proposals_preserve_hook_and_stream_order(tmp_path):
    trace = []
    llm = _FakeLLM(
        (DIFF, "<<<SEARCH\nx=2\n===\nx=3\n>>>REPLACE")
    )
    problem = _problem(tmp_path)
    config = _config(tmp_path, "multiple", proposals_per_generation=2)

    with patch.object(loop_module, "build_llm", return_value=llm):
        evolve(problem, config, plugins=[_TracePlugin(trace)])

    run_dir = tmp_path / "runs" / "multiple"
    history = _rows(run_dir, "history.jsonl")
    prompt_history = _rows(run_dir, "prompt_history.jsonl")
    budget_events = _rows(run_dir, "controller_budget_events.jsonl")

    assert [row["generation"] for row in history] == [0, 1, 1]
    assert [row["metadata"]["proposal_batch"]["proposal_index"] for row in history[1:]] == [0, 1]
    assert [kind for kind, _ in trace] == [
        "generation_start",
        "context",
        "evaluated",
        "context",
        "evaluated",
        "generation_end",
    ]
    assert [event["kind"] for event in budget_events] == [
        "seed_evaluation",
        "generation_started",
        "llm_call",
        "candidate_evaluation",
        "llm_call",
        "candidate_evaluation",
        "generation_completed",
        "stop",
    ]
    assert [event["event"] for event in prompt_history if "event" in event] == [
        "add",
        "score",
        "score",
    ]


@pytest.mark.parametrize(
    ("mode", "extra"),
    [
        ("sync", {}),
        ("evaluation", {"async_candidate_evaluation": True}),
        ("sampler", {"async_llm_sampling": True}),
        (
            "combined",
            {"async_candidate_evaluation": True, "async_llm_sampling": True},
        ),
    ],
)
def test_async_modes_keep_submission_and_admission_order(tmp_path, mode, extra):
    problem = _problem(tmp_path)
    config = _config(tmp_path, mode, proposals_per_generation=2, **extra)
    created = []

    def make_llm(config):
        llm = _FakeLLM()
        created.append(llm)
        return llm

    with patch.object(loop_module, "build_llm", side_effect=make_llm):
        evolve(problem, config)

    run_dir = tmp_path / "runs" / mode
    history = _rows(run_dir, "history.jsonl")
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    runtime_history = manifest["runtime"]["history"]

    assert len(history) == 3
    assert [row["metadata"]["proposal_batch"]["proposal_index"] for row in history[1:]] == [0, 1]
    if extra.get("async_candidate_evaluation"):
        controller = runtime_history["async_candidate_evaluation_controller"]
        assert controller["validation"]["ok"] is True
        assert [row["submission_order"] for row in controller["admission_records"]] == [0, 1]
    if extra.get("async_llm_sampling"):
        sampler = runtime_history["async_llm_sampler_controller"]
        assert sampler["validation"]["ok"] is True
        assert [row["submission_order"] for row in sampler["merge_records"]] == [0, 1]
        assert len(created) == 1 + config.async_llm_sampler_workers


def test_admission_states_remain_distinct_and_rewards_follow_contract(tmp_path):
    cases = [
        ("invalid", DIFF, "invalid_evaluation", False, False, True),
        ("below", DIFF, "below_threshold", False, False, True),
        ("not_improving", "<<<SEARCH\nx=1\n===\nx=1.0\n>>>REPLACE", "not_improving_cell", False, False, False),
        ("retained", DIFF, "empty_cell", True, True, False),
    ]
    for name, response, reason, admitted, rewardable, failure_expected in cases:
        problem = _problem(tmp_path / name)
        trace_plugin = None
        if name == "invalid":
            class InvalidPlugin(PluginBase):
                def on_evaluated(self, program, score):
                    program.evaluation["is_valid"] = False
                    return score

            trace_plugin = InvalidPlugin()
        elif name == "below":
            class BelowPlugin(PluginBase):
                def on_evaluated(self, program, score):
                    return -0.25

            trace_plugin = BelowPlugin()
        response_llm = _FakeLLM((response,))
        with patch.object(loop_module, "build_llm", return_value=response_llm):
            options = {}
            if name == "not_improving":
                options.update(n_islands=1, map_elites_bins=1, elite_archive_size=1)
            evolve(
                problem,
                _config(tmp_path / name, name, **options),
                plugins=[trace_plugin] if trace_plugin is not None else None,
            )

        run_dir = tmp_path / name / "runs" / name
        child = _rows(run_dir, "history.jsonl")[-1]
        admission = child["metadata"]["archive_admission"]
        reward = child["metadata"]["backend_reward"]
        failures = _rows(run_dir, "failure_history.jsonl")

        assert admission["admitted"] is admitted, (name, admission)
        assert admission["cell_admitted"] is admitted
        assert admission["sampling_eligible"] is admitted
        assert admission["reason"] == reason
        assert reward["eligible"] is rewardable
        assert reward["reward"] == (0.75 if rewardable else 0.0)
        assert bool(failures) is failure_expected


def test_async_fatal_commit_closes_controller_and_persists_abort(tmp_path):
    class FailingPlugin(PluginBase):
        def on_evaluated(self, program, score):
            raise RuntimeError("commit fault")

    problem = _problem(tmp_path)
    config = _config(tmp_path, "async_abort", async_candidate_evaluation=True)
    with (
        patch.object(loop_module, "build_llm", return_value=_FakeLLM()),
        pytest.raises(RuntimeError, match="commit fault"),
    ):
        evolve(problem, config, plugins=[FailingPlugin()])

    manifest = json.loads(
        (tmp_path / "runs" / "async_abort" / "manifest.json").read_text(encoding="utf-8")
    )
    runtime = manifest["runtime"]
    controller = runtime["history"]["async_candidate_evaluation_controller"]

    assert runtime["status"] == "aborted"
    assert runtime["abort"]["exception_type"] == "RuntimeError"
    assert runtime["abort"]["phase"] == "generation:0:async_evaluation_drain"
    assert controller["pending_work"] == {
        "queued_evaluations": 0,
        "running_evaluations": 0,
        "pending_admissions": 0,
    }


def test_finalization_fault_is_recorded_as_terminal_abort_metadata(tmp_path):
    problem = _problem(tmp_path)
    config = _config(tmp_path, "export_fault")
    with (
        patch.object(loop_module, "build_llm", return_value=_FakeLLM()),
        patch.object(loop_module, "export_best_artifacts", side_effect=OSError("export fault")),
        pytest.raises(OSError, match="export fault"),
    ):
        evolve(problem, config)

    runtime = json.loads(
        (tmp_path / "runs" / "export_fault" / "manifest.json").read_text(encoding="utf-8")
    )["runtime"]
    assert runtime["status"] == "aborted"
    assert runtime["abort"]["phase"] == "normal_finalization"
    assert runtime["abort"]["exception_type"] == "OSError"
    assert "export fault" in runtime["abort"]["message"]


def test_runtime_rng_restore_isolated_from_process_global_random(tmp_path):
    source = random.Random(73)
    source.random()
    snapshot = loop_module._runtime_rng_state(source, 73)
    expected = random.Random()
    expected.setstate(source.getstate())
    global_state = random.getstate()

    restored, status = loop_module._initial_run_rng(
        Config(max_generations=0, seed=73, log_dir=str(tmp_path)), snapshot
    )

    assert status == "snapshot_restored_into_evolve"
    assert random.getstate() == global_state
    assert restored.random() == expected.random()
    with pytest.raises(ValueError, match="seed must match"):
        loop_module._initial_run_rng(
            Config(max_generations=0, seed=74, log_dir=str(tmp_path)), snapshot
        )


def test_durable_streams_and_runtime_summary_are_ordered_and_joinable(tmp_path):
    problem = _problem(tmp_path)
    with patch.object(loop_module, "build_llm", return_value=_FakeLLM()):
        evolve(problem, _config(tmp_path, "durable"))

    run_dir = tmp_path / "runs" / "durable"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    runtime = manifest["runtime"]
    history = _rows(run_dir, "history.jsonl")
    prompt_history = _rows(run_dir, "prompt_history.jsonl")
    budget_events = _rows(run_dir, "controller_budget_events.jsonl")

    assert [row["generation"] for row in history] == [0, 1]
    assert runtime["status"] == "completed"
    assert runtime["history"]["programs_logged"] == len(history)
    assert runtime["consumed"]["candidate_evaluations"] == 1
    assert [row["event"] for row in prompt_history] == ["add", "score"]
    assert [row["kind"] for row in budget_events][-1] == "stop"
    assert runtime["history"]["controller_state"]["validation"]["ok"] is True
    assert runtime["run_artifact_bundle_report"]["validation"]["ok"] is True
