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
