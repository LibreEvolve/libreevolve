import copy
import json

from libreevolve.core.config import Config
from libreevolve.core.database import ProgramDatabase
from libreevolve.population.objective_history import (
    OBJECTIVE_HISTORY_POLICY,
    validate_objective_history_summary,
)
from libreevolve.population.program import Program


def _objective_schema():
    return {
        "metrics": [
            {
                "name": "accuracy",
                "direction": "maximize",
                "primary": True,
                "bounds": [0.0, 1.0],
            },
            {
                "name": "latency",
                "direction": "minimize",
                "primary": False,
                "bounds": [0.0, 100.0],
            },
        ],
        "primary_metric": "accuracy",
        "primary_bounds": [0.0, 1.0],
        "metric_count": 2,
    }


def _program(program_id: str, accuracy: float, latency: float) -> Program:
    selection_score = (accuracy + latency) / 2.0
    return Program(
        id=program_id,
        code="x = 1\n",
        fitness=selection_score,
        metrics={"accuracy": accuracy, "latency": latency},
        evaluation={"is_valid": True},
        metadata={
            "normalized_metrics": {"accuracy": accuracy, "latency": latency},
            "selection_score": selection_score,
        },
    )


def _history(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
        objective_schema=_objective_schema(),
    )
    for candidate in [
        _program("accuracy_leader", 0.95, 0.20),
        _program("latency_leader", 0.20, 0.95),
        _program("balanced", 0.80, 0.80),
        _program("dominated", 0.50, 0.50),
    ]:
        db.log(candidate)
    return {
        "objective_frontier": db.objective_frontier_snapshot(),
        "objective_metric_leaders": db.objective_metric_leaders_snapshot(),
        "objective_metric_archives": db.objective_metric_archives_snapshot(),
    }


def test_objective_history_summary_validates_runtime_snapshots(tmp_path):
    history = _history(tmp_path)

    validation = validate_objective_history_summary(history)

    assert validation.ok is True
    assert validation.diagnostic_ready is True
    assert validation.primary_archive_policy_ready is False
    assert validation.metric_order == ["accuracy", "latency"]
    assert validation.frontier_program_count == 3
    assert validation.leader_count == 2
    assert validation.archive_count == 2
    assert validation.issues == []
    assert OBJECTIVE_HISTORY_POLICY == "diagnostic_declared_normalized_metric_history"


def test_objective_history_summary_loads_manifest_json(tmp_path):
    manifest = {"runtime": {"history": _history(tmp_path)}}
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")

    validation = validate_objective_history_summary(path)

    assert validation.ok is True
    assert validation.metric_order == ["accuracy", "latency"]


def test_objective_history_summary_rejects_frontier_overclaim(tmp_path):
    history = _history(tmp_path)
    history["objective_frontier"]["policy"] = "primary_archive_replacement_policy"
    history["objective_frontier"]["limitations"] = ["primary_archive_replacement"]
    history["objective_frontier"]["programs"].append(
        {
            "program_id": "dominated_retained",
            "generation": 0,
            "selection_score": 0.1,
            "normalized_metrics": {"accuracy": 0.1, "latency": 0.1},
        }
    )
    history["objective_frontier"]["retained_frontier_size"] += 1

    validation = validate_objective_history_summary(history)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.primary_archive_policy_ready is False
    assert "invalid_objective_frontier_policy" in codes
    assert "missing_objective_frontier_limitations" in codes
    assert "objective_frontier_contains_dominated_program" in codes


def test_objective_history_summary_rejects_metric_order_mismatch(tmp_path):
    history = _history(tmp_path)
    history["objective_metric_leaders"]["metric_order"] = ["latency", "accuracy"]
    history["objective_metric_archives"]["metric_order"] = ["accuracy"]

    validation = validate_objective_history_summary(history)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "objective_metric_leaders_metric_order_mismatch" in codes
    assert "objective_metric_archives_metric_order_mismatch" in codes


def test_objective_history_summary_rejects_archive_count_errors(tmp_path):
    history = copy.deepcopy(_history(tmp_path))
    archive = history["objective_metric_archives"]["archives"][0]
    archive["retained_count"] = 99
    archive["retention_limit"] = 1
    archive["program_count_considered"] = 0
    archive["programs"][0]["normalized_metric"] = 0.0

    validation = validate_objective_history_summary(history)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "objective_metric_archive_retained_count_mismatch" in codes
    assert "objective_metric_archive_retention_limit_exceeded" in codes
    assert "objective_metric_archive_considered_count_mismatch" in codes
    assert "objective_metric_archives_archives_0_programs_0_metric_value_mismatch" in codes


def test_objective_history_summary_rejects_invalid_program_records(tmp_path):
    history = _history(tmp_path)
    history["objective_metric_leaders"]["leaders"][0]["program_id"] = "../escape"
    history["objective_metric_leaders"]["leaders"][0]["generation"] = -1
    history["objective_metric_leaders"]["leaders"][0]["selection_score"] = 1.5
    history["objective_metric_leaders"]["leaders"][0]["normalized_metrics"][
        "extra"
    ] = 0.1

    validation = validate_objective_history_summary(history)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_objective_metric_leaders_leaders_0_program_id" in codes
    assert "invalid_objective_metric_leaders_leaders_0_generation" in codes
    assert "invalid_objective_metric_leaders_leaders_0_selection_score" in codes
    assert "objective_metric_leaders_leaders_0_unknown_metric" in codes
