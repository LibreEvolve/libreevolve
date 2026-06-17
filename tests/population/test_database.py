from fractions import Fraction
import hashlib
import json, math, os, subprocess, sys, tempfile
import random
from pathlib import Path
import pytest
from libreevolve.core.artifact_schema import (
    ARCHIVE_EVENT_RECORD_SCHEMA,
    ARTIFACT_SCHEMA_VERSION,
    EVALUATOR_RESULT_RECORD_SCHEMA,
    FAILURE_RECORD_SCHEMA,
    HISTORY_RECORD_SCHEMA,
    LLM_CALL_RECORD_SCHEMA,
    LLM_REWARD_RECORD_SCHEMA,
    PROMPT_HISTORY_RECORD_SCHEMA,
    QUARANTINE_RECORD_SCHEMA,
    RUN_ARTIFACT_NAMES as SCHEMA_RUN_ARTIFACT_NAMES,
    RUN_MANIFEST_SCHEMA,
    generated_run_artifact_inventory,
    paper_artifact_subpath_schema,
    run_artifact_schema,
)
from libreevolve.core.config import Config, ConfigError
from libreevolve.core.database import (
    ArchiveEventRestoreError,
    ArchiveStateRestoreError,
    HistoryRestoreError,
    RUN_ARTIFACT_NAMES,
    archive_event_replay_audit,
    audit_archive_event_records,
    load_archive_restore_bundle,
    ProgramDatabase as _ProgramDatabase,
    load_archive_event_records,
    load_accepted_history_index,
    load_failure_history_records,
    load_runtime_archive_state_snapshot,
    _program_from_history_record,
    validate_archive_event_replay_audit,
    validate_archive_state_snapshot,
    validate_candidate_language_policy,
    validate_resurfacing_index_summary,
    validate_run_directory_path,
)
from libreevolve.core.jsonl import StrictJsonlError
from libreevolve.core.evaluator import _validator_boundary_metadata
from libreevolve.core.prompt import PromptSampler
from libreevolve.population.program import Program
from libreevolve.problems.loader import Problem

def _objective_schema():
    return {
        "metrics": [
            {
                "name": "score",
                "direction": "maximize",
                "primary": True,
                "bounds": [0.0, 1.0],
            }
        ],
        "primary_metric": "score",
        "primary_bounds": [0.0, 1.0],
        "metric_count": 1,
    }

def ProgramDatabase(config, **kwargs):
    kwargs.setdefault("objective_schema", _objective_schema())
    return _ProgramDatabase(config, **kwargs)

def _db():
    return ProgramDatabase(
        Config(log_dir=tempfile.mkdtemp(), problem_name="t"),
    )

def _p(code="x=1", fitness=0.5):
    return Program(code=code, fitness=fitness, evaluation={"is_valid": True})


def _problem():
    return Problem(
        name="demo",
        task_description="Improve solve().",
        metrics=[{"name": "score", "primary": True, "bounds": [0.0, 1.0]}],
        primary_metric="score",
        primary_bounds=(0.0, 1.0),
        validate_path=Path("validate.py"),
        initial_programs=["x=1"],
        problem_dir=Path("."),
    )

def test_log_always_appends():
    db = _db(); db.log(_p(fitness=-0.4))
    assert len(db.all_programs()) == 1


def test_objective_frontier_snapshot_keeps_non_dominated_declared_metrics(tmp_path):
    schema = {
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
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
        objective_schema=schema,
    )

    def program(program_id: str, accuracy: float, latency: float) -> Program:
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

    for candidate in [
        program("accuracy_leader", 0.95, 0.20),
        program("latency_leader", 0.20, 0.95),
        program("balanced", 0.80, 0.80),
        program("dominated", 0.50, 0.50),
    ]:
        db.log(candidate)

    snapshot = db.objective_frontier_snapshot()

    assert snapshot["schema"] == "libreevolve.objective_frontier.v1"
    assert snapshot["metric_order"] == ["accuracy", "latency"]
    assert snapshot["program_count_considered"] == 4
    assert snapshot["frontier_size"] == 3
    assert {record["program_id"] for record in snapshot["programs"]} == {
        "accuracy_leader",
        "latency_leader",
        "balanced",
    }
    assert "dominated" not in {
        record["program_id"] for record in snapshot["programs"]
    }


def test_resurfacing_index_summary_validates_rank_fusion_snapshot(tmp_path):
    db = ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))
    first = Program(
        id="first",
        code="x = 1\n",
        fitness=0.9,
        metrics={"score": 0.9},
        evaluation={"is_valid": True},
        metadata={"normalized_metrics": {"score": 0.9}, "selection_score": 0.9},
    )
    second = Program(
        id="second",
        code="x = 2\n",
        fitness=0.5,
        metrics={"score": 0.5},
        evaluation={"is_valid": True},
        metadata={"normalized_metrics": {"score": 0.5}, "selection_score": 0.5},
    )
    db.log(first)
    db.log(second)

    snapshot = db.resurfacing_index_snapshot()
    validation = validate_resurfacing_index_summary(snapshot)

    assert snapshot["schema"] == "libreevolve.resurfacing_index.v1"
    assert validation["ok"] is True
    assert validation["resurfacing_ready"] is True
    assert validation["durable_database_ready"] is False
    assert validation["program_count"] == len(snapshot["programs"])
    assert validation["metric_order"] == ["score"]
    assert validation["issues"] == []


def test_resurfacing_index_summary_rejects_overclaims_and_bad_rank_data(tmp_path):
    db = ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))
    for index, score in enumerate([0.9, 0.5]):
        db.log(
            Program(
                id=f"candidate_{index}",
                code=f"x = {index}\n",
                fitness=score,
                metrics={"score": score},
                evaluation={"is_valid": True},
                metadata={
                    "normalized_metrics": {"score": score},
                    "selection_score": score,
                },
            )
        )
    snapshot = db.resurfacing_index_snapshot()
    snapshot["policy"] = "persisted_cross_run_embedding_database"
    snapshot["limitations"] = []
    snapshot["source_counts"]["score"] = 0
    snapshot["programs"] = list(reversed(snapshot["programs"]))
    snapshot["programs"][0]["resurfacing_score"] = 999.0

    validation = validate_resurfacing_index_summary(snapshot)
    codes = {issue["code"] for issue in validation["issues"]}

    assert validation["ok"] is False
    assert validation["resurfacing_ready"] is False
    assert validation["durable_database_ready"] is False
    assert "invalid_policy" in codes
    assert "missing_limitations" in codes
    assert "source_count_below_retained_sources" in codes
    assert "resurfacing_score_mismatch" in codes
    assert "programs_not_ranked" in codes


def test_objective_metric_leaders_snapshot_reports_declared_metric_elites(tmp_path):
    schema = {
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
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
        objective_schema=schema,
    )

    def program(program_id: str, accuracy: float, latency: float) -> Program:
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

    for candidate in [
        program("accuracy_leader", 0.95, 0.20),
        program("latency_leader", 0.20, 0.95),
        program("balanced", 0.80, 0.80),
    ]:
        db.log(candidate)

    snapshot = db.objective_metric_leaders_snapshot()

    assert snapshot["schema"] == "libreevolve.objective_metric_leaders.v1"
    assert snapshot["policy"] == "best_program_per_declared_normalized_metric"
    assert snapshot["metric_order"] == ["accuracy", "latency"]
    assert snapshot["leader_count"] == 2
    assert snapshot["leaders"] == [
        {
            "metric": "accuracy",
            "program_id": "accuracy_leader",
            "generation": 0,
            "normalized_metric": 0.95,
            "selection_score": 0.575,
            "normalized_metrics": {"accuracy": 0.95, "latency": 0.20},
        },
        {
            "metric": "latency",
            "program_id": "latency_leader",
            "generation": 0,
            "normalized_metric": 0.95,
            "selection_score": 0.575,
            "normalized_metrics": {"accuracy": 0.20, "latency": 0.95},
        },
    ]


def test_objective_metric_archives_snapshot_reports_top_declared_metric_programs(
    tmp_path,
):
    schema = {
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
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
        objective_schema=schema,
    )

    def program(program_id: str, accuracy: float, latency: float) -> Program:
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

    for candidate in [
        program("accuracy_leader", 0.95, 0.20),
        program("balanced", 0.80, 0.80),
        program("latency_leader", 0.20, 0.95),
        program("invalid_metric", 1.50, 0.10),
        Program(
            id="invalid_eval",
            code="x = 1\n",
            fitness=1.0,
            metrics={"accuracy": 1.0, "latency": 1.0},
            evaluation={"is_valid": False},
            metadata={
                "normalized_metrics": {"accuracy": 1.0, "latency": 1.0},
                "selection_score": 1.0,
            },
        ),
    ]:
        db.log(candidate)

    snapshot = db.objective_metric_archives_snapshot()

    assert snapshot["schema"] == "libreevolve.objective_metric_archives.v1"
    assert snapshot["policy"] == "top_programs_per_declared_normalized_metric"
    assert snapshot["metric_order"] == ["accuracy", "latency"]
    assert snapshot["archive_count"] == 2
    assert snapshot["retention_limit"] == 10
    assert [
        record["program_id"]
        for record in snapshot["archives"][0]["programs"]
    ] == ["accuracy_leader", "balanced", "latency_leader"]
    assert [
        record["program_id"]
        for record in snapshot["archives"][1]["programs"]
    ] == ["latency_leader", "balanced", "accuracy_leader", "invalid_metric"]
    assert snapshot["archives"][0]["program_count_considered"] == 3
    assert snapshot["archives"][0]["retained_count"] == 3
    assert snapshot["archives"][1]["program_count_considered"] == 4
    assert snapshot["archives"][1]["retained_count"] == 4


def test_score_index_snapshot_reports_top_valid_programs_by_selection_score(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
    )
    high_fitness_low_score = Program(
        id="high-fitness-low-score",
        code="x = 1\n",
        fitness=0.95,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.2},
    )
    balanced = Program(
        id="balanced",
        code="x = 2\n",
        fitness=0.8,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.8,
            "normalized_metrics": {"score": 0.8},
            "archive_admission": {
                "admitted": True,
                "reason": "new_cell",
                "cell_admitted": True,
                "elite_retained": True,
                "sampling_eligible": True,
                "search_state_changed": True,
                "island_id": 0,
                "archive_sequence": 3,
                "cell": [7, 2, 1],
            },
        },
    )
    top = Program(
        id="top",
        code="x = 3\n",
        fitness=0.7,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9},
    )
    invalid = Program(
        id="invalid",
        code="x = 4\n",
        fitness=1.0,
        evaluation={"is_valid": False},
        metadata={"selection_score": 1.0},
    )
    for candidate in (high_fitness_low_score, balanced, top, invalid):
        db.log(candidate)

    snapshot = db.score_index_snapshot()

    assert snapshot["schema"] == "libreevolve.score_index.v1"
    assert snapshot["policy"] == "top_valid_programs_by_selection_score_then_fitness"
    assert snapshot["program_count_considered"] == 3
    assert [program["program_id"] for program in snapshot["programs"]] == [
        top.id,
        balanced.id,
        high_fitness_low_score.id,
    ]
    assert snapshot["programs"][1]["objective_vector"] == {
        "policy": "normalized_declared_metric_vector_v1",
        "normalized_metrics": {"score": 0.8},
    }
    assert snapshot["programs"][1]["archive_admission"] == {
        "admitted": True,
        "cell_admitted": True,
        "elite_retained": True,
        "sampling_eligible": True,
        "search_state_changed": True,
        "reason": "new_cell",
        "island_id": 0,
        "archive_sequence": 3,
        "cell": [7, 2, 1],
    }
    assert invalid.id not in {program["program_id"] for program in snapshot["programs"]}


def test_lineage_index_snapshot_groups_valid_programs_by_root(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
    )
    root_a = Program(
        id="root-a",
        code="x = 1\n",
        fitness=0.2,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.2},
    )
    weaker_child_a = Program(
        id="weaker-child-a",
        code="x = 2\n",
        fitness=0.5,
        parent_id=root_a.id,
        lineage=[root_a.id],
        generation=1,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.5},
    )
    best_child_a = Program(
        id="best-child-a",
        code="x = 3\n",
        fitness=0.9,
        parent_id=root_a.id,
        lineage=[root_a.id],
        generation=1,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.9,
            "normalized_metrics": {"score": 0.9},
        },
    )
    root_b = Program(
        id="root-b",
        code="x = 4\n",
        fitness=0.7,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.7},
    )
    invalid = Program(
        id="invalid-child",
        code="x = 5\n",
        fitness=1.0,
        parent_id=root_a.id,
        lineage=[root_a.id],
        generation=2,
        evaluation={"is_valid": False},
        metadata={"selection_score": 1.0},
    )
    for program in (root_a, weaker_child_a, best_child_a, root_b, invalid):
        db.log(program)

    snapshot = db.lineage_index_snapshot()

    assert snapshot["schema"] == "libreevolve.lineage_index.v1"
    assert snapshot["policy"] == "best_valid_programs_grouped_by_root_lineage"
    assert snapshot["program_count_considered"] == 4
    assert snapshot["lineage_count"] == 2
    assert snapshot["retained_lineage_count"] == 2
    assert [lineage["lineage_root_id"] for lineage in snapshot["lineages"]] == [
        root_a.id,
        root_b.id,
    ]
    assert snapshot["lineages"][0]["program_count"] == 3
    assert snapshot["lineages"][0]["best_program"]["program_id"] == best_child_a.id
    assert snapshot["lineages"][0]["best_program"]["objective_vector"] == {
        "policy": "normalized_declared_metric_vector_v1",
        "normalized_metrics": {"score": 0.9},
    }
    assert [program["program_id"] for program in snapshot["lineages"][0]["programs"]] == [
        best_child_a.id,
        weaker_child_a.id,
        root_a.id,
    ]
    assert invalid.id not in {
        program["program_id"]
        for lineage in snapshot["lineages"]
        for program in lineage["programs"]
    }


def test_descriptor_index_snapshot_reports_top_archive_descriptor_programs(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
    )

    def program(program_id: str, selection_score: float, descriptors: dict) -> Program:
        return Program(
            id=program_id,
            code="x = 1\n",
            fitness=selection_score,
            evaluation={"is_valid": True},
            metadata={
                "selection_score": selection_score,
                "archive_admission": {
                    "admitted": True,
                    "descriptors": descriptors,
                },
            },
        )

    high_diversity = program(
        "high-diversity",
        0.4,
        {"diversity": 0.95, "complexity": 0.30},
    )
    high_score = program(
        "high-score",
        0.9,
        {"diversity": 0.50, "complexity": 0.60},
    )
    invalid_descriptor = program(
        "invalid-descriptor",
        1.0,
        {"diversity": "bad", "complexity": 0.10},
    )
    invalid_evaluation = Program(
        id="invalid-eval",
        code="x = 1\n",
        fitness=1.0,
        evaluation={"is_valid": False},
        metadata={
            "selection_score": 1.0,
            "archive_admission": {
                "admitted": False,
                "descriptors": {"diversity": 1.0},
            },
        },
    )
    for candidate in (
        high_diversity,
        high_score,
        invalid_descriptor,
        invalid_evaluation,
    ):
        db.log(candidate)

    snapshot = db.descriptor_index_snapshot()

    assert snapshot["schema"] == "libreevolve.descriptor_index.v1"
    assert snapshot["policy"] == "top_valid_programs_per_archive_descriptor"
    assert snapshot["descriptor_count"] == 2
    assert snapshot["retention_limit"] == 10
    assert [entry["descriptor"] for entry in snapshot["descriptors"]] == [
        "complexity",
        "diversity",
    ]
    complexity = snapshot["descriptors"][0]
    diversity = snapshot["descriptors"][1]
    assert [program["program_id"] for program in complexity["programs"]] == [
        high_score.id,
        high_diversity.id,
        invalid_descriptor.id,
    ]
    assert [program["program_id"] for program in diversity["programs"]] == [
        high_diversity.id,
        high_score.id,
    ]
    assert diversity["programs"][0] == {
        "descriptor": "diversity",
        "program_id": high_diversity.id,
        "lineage_root_id": high_diversity.id,
        "generation": 0,
        "descriptor_value": 0.95,
        "selection_score": 0.4,
        "fitness": 0.4,
    }
    assert invalid_evaluation.id not in {
        program["program_id"]
        for entry in snapshot["descriptors"]
        for program in entry["programs"]
    }


def test_feedback_index_snapshot_groups_feedback_records_by_grader(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
    )
    strong = Program(
        id="strong",
        code="x = 1\n",
        fitness=0.9,
        evaluation={
            "is_valid": True,
            "metadata": {
                "llm_feedback": [
                    {
                        "name": "simplicity",
                        "metric": "simplicity_score",
                        "score": 0.9,
                        "normalized_score": 0.9,
                        "weighted_delta": 0.18,
                        "feedback": "clear and compact",
                        "feedback_retention": {
                            "policy": "redact_bound_hash_v1",
                            "retention_mode": "redacted",
                            "sha256": "a" * 64,
                            "chars": 17,
                            "stored_chars": 17,
                            "redacted": False,
                            "truncated": False,
                        },
                    }
                ],
            },
        },
        metadata={"selection_score": 0.9},
    )
    weak = Program(
        id="weak",
        code="x = 2\n",
        fitness=0.4,
        evaluation={
            "is_valid": True,
            "metadata": {
                "llm_feedback": [
                    {
                        "name": "simplicity",
                        "metric": "simplicity_score",
                        "score": 0.2,
                        "normalized_score": 0.2,
                        "weighted_delta": 0.04,
                        "discard": True,
                        "error": "llm_feedback_discard",
                    },
                    {
                        "name": "style",
                        "metric": "style_score",
                        "error": "llm_feedback_failed",
                        "failure_delta": -0.1,
                    },
                ],
            },
        },
        metadata={"selection_score": 0.4},
    )
    no_feedback = Program(
        id="no-feedback",
        code="x = 3\n",
        fitness=1.0,
        evaluation={"is_valid": True},
        metadata={"selection_score": 1.0},
    )
    for candidate in (weak, strong, no_feedback):
        db.log(candidate)

    snapshot = db.feedback_index_snapshot()

    assert snapshot["schema"] == "libreevolve.feedback_index.v1"
    assert snapshot["policy"] == "top_program_feedback_records_by_grader"
    assert snapshot["feedback_grader_count"] == 2
    assert snapshot["record_count"] == 3
    assert [grader["feedback_name"] for grader in snapshot["graders"]] == [
        "simplicity",
        "style",
    ]
    simplicity = snapshot["graders"][0]
    assert [program["program_id"] for program in simplicity["programs"]] == [
        strong.id,
        weak.id,
    ]
    assert simplicity["programs"][0]["feedback_text"] == {
        "policy": "bounded_redacted_feedback_preview_v1",
        "chars": 17,
        "sha256": hashlib.sha256(b"clear and compact").hexdigest(),
        "preview": "clear and compact",
        "preview_chars": 17,
        "truncated": False,
        "redacted": False,
    }
    assert simplicity["programs"][0]["retention"]["feedback_retention"] == {
        "policy": "redact_bound_hash_v1",
        "retention_mode": "redacted",
        "sha256": "a" * 64,
        "chars": 17,
        "stored_chars": 17,
        "redacted": False,
        "truncated": False,
    }
    assert snapshot["graders"][1]["programs"][0]["error"] == "llm_feedback_failed"
    assert no_feedback.id not in {
        program["program_id"]
        for grader in snapshot["graders"]
        for program in grader["programs"]
    }


def test_resurfacing_index_snapshot_fuses_queryable_program_sources(tmp_path):
    schema = {
        "metrics": [
            {
                "name": "accuracy",
                "direction": "maximize",
                "primary": True,
                "bounds": [0.0, 1.0],
            },
            {
                "name": "latency",
                "direction": "maximize",
                "primary": False,
                "bounds": [0.0, 1.0],
            },
        ],
        "primary_metric": "accuracy",
        "primary_bounds": [0.0, 1.0],
        "metric_count": 2,
    }
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
        objective_schema=schema,
    )

    def program(
        program_id: str,
        *,
        accuracy: float,
        latency: float,
        selection_score: float,
        feedback_score: float | None = None,
        descriptor: float | None = None,
        valid: bool = True,
    ) -> Program:
        metadata = {
            "selection_score": selection_score,
            "normalized_metrics": {"accuracy": accuracy, "latency": latency},
        }
        if descriptor is not None:
            metadata["archive_admission"] = {
                "admitted": True,
                "reason": "empty_cell",
                "descriptors": {"diversity": descriptor},
            }
        evaluation = {"is_valid": valid}
        if feedback_score is not None:
            evaluation["metadata"] = {
                "llm_feedback": [
                    {
                        "name": "reviewer",
                        "score": feedback_score,
                        "normalized_score": feedback_score,
                    }
                ],
            }
        return Program(
            id=program_id,
            code=f"{program_id} = 1\n",
            fitness=selection_score,
            evaluation=evaluation,
            metadata=metadata,
        )

    balanced = program(
        "balanced",
        accuracy=0.80,
        latency=0.80,
        selection_score=0.80,
        descriptor=0.95,
    )
    accuracy_leader = program(
        "accuracy-leader",
        accuracy=0.95,
        latency=0.20,
        selection_score=0.60,
    )
    feedback_leader = program(
        "feedback-leader",
        accuracy=0.30,
        latency=0.30,
        selection_score=0.30,
        feedback_score=0.99,
    )
    invalid_feedback = program(
        "invalid-feedback",
        accuracy=1.0,
        latency=1.0,
        selection_score=1.0,
        feedback_score=1.0,
        valid=False,
    )
    for candidate in (
        feedback_leader,
        invalid_feedback,
        accuracy_leader,
        balanced,
    ):
        db.log(candidate)

    snapshot = db.resurfacing_index_snapshot()

    assert snapshot["schema"] == "libreevolve.resurfacing_index.v1"
    assert snapshot["metric_order"] == ["accuracy", "latency"]
    assert snapshot["program_count_considered"] == 3
    assert snapshot["candidate_count"] == 3
    assert snapshot["source_counts"]["score"] == 3
    assert snapshot["source_counts"]["metric"] == 6
    assert snapshot["source_counts"]["feedback"] == 1
    programs = {record["program_id"]: record for record in snapshot["programs"]}
    assert set(programs) == {
        balanced.id,
        accuracy_leader.id,
        feedback_leader.id,
    }
    assert invalid_feedback.id not in programs
    assert snapshot["programs"][0]["program_id"] == balanced.id
    assert {
        (source["source"], source["source_key"])
        for source in programs[balanced.id]["sources"]
    } >= {
        ("score", "selection_score"),
        ("frontier", "declared_objective_vector"),
        ("metric", "accuracy"),
        ("metric", "latency"),
        ("descriptor", "diversity"),
    }
    assert {
        source["source"] for source in programs[feedback_leader.id]["sources"]
    } >= {"feedback", "score"}
    assert snapshot["limitations"] == [
        "manifest_visible_resurfacing_index_not_persisted_database_table",
        "uses_deterministic_rank_fusion_not_learned_embedding_search",
        "valid_history_programs_only",
        "rebuilt_from_current_history_records_at_runtime_summary_time",
    ]


def test_hypothesis_index_snapshot_reports_captured_proposals(tmp_path):
    db = ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))
    strong = Program(
        id="strong-hypothesis",
        code="x = 1\n",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.9,
            "proposal": {
                "idea": "Use a tile cache.",
                "rationale": "Reduce duplicate products.",
                "hypothesis": "Tile cache improves matrix rank search.",
            },
        },
    )
    weak = Program(
        id="weak-hypothesis",
        code="x = 2\n",
        fitness=0.2,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.2,
            "proposal": {
                "hypothesis": "Try a slower fallback.",
            },
        },
    )
    invalid = Program(
        id="invalid-hypothesis",
        code="x = 3\n",
        fitness=1.0,
        evaluation={"is_valid": False},
        metadata={
            "selection_score": 1.0,
            "proposal": {
                "hypothesis": "Invalid candidates stay out of the index.",
            },
        },
    )
    for candidate in (weak, invalid, strong):
        db.log(candidate)

    snapshot = db.hypothesis_index_snapshot()

    assert snapshot["schema"] == "libreevolve.hypothesis_index.v1"
    assert snapshot["policy"] == "top_valid_programs_with_proposal_hypothesis_metadata"
    assert snapshot["program_count_considered"] == 2
    assert [program["program_id"] for program in snapshot["programs"]] == [
        strong.id,
        weak.id,
    ]
    assert snapshot["programs"][0]["proposal"]["hypothesis"] == {
        "policy": "bounded_redacted_proposal_text_v1",
        "chars": 39,
        "sha256": hashlib.sha256(
            b"Tile cache improves matrix rank search."
        ).hexdigest(),
        "preview": "Tile cache improves matrix rank search.",
        "preview_chars": 39,
        "truncated": False,
        "redacted": False,
    }
    resurfacing = db.resurfacing_index_snapshot()
    surfaced = {
        record["program_id"]: record for record in resurfacing["programs"]
    }
    assert {
        source["source"] for source in surfaced[strong.id]["sources"]
    } >= {"score", "hypothesis"}
    assert invalid.id not in surfaced


def test_artifact_index_snapshot_reports_evaluator_artifact_evidence(tmp_path):
    db = ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))
    strong = Program(
        id="strong-artifact",
        code="x = 1\n",
        fitness=0.9,
        evaluation={
            "is_valid": True,
            "metadata": {
                "artifacts": {
                    "collection_id": "abc123",
                    "artifact_dir_name": "evaluator_artifacts",
                    "total_bytes": 17,
                    "stage": {"name": "validate", "sample_index": 0, "attempt": 1},
                    "files": [
                        {
                            "path": "reports/result.json",
                            "artifact_path": "evaluator_artifacts/abc123/reports/result.json",
                            "artifact_path_root": "artifact_dir_parent",
                            "artifact_relative_path": "abc123/reports/result.json",
                            "bytes": 17,
                            "source_bytes": 17,
                            "sha256": hashlib.sha256(b'{"ok": true}').hexdigest(),
                            "redacted": False,
                            "redaction_status": "unchanged",
                            "stage_name": "validate",
                            "sample_index": 0,
                            "attempt": 1,
                            "content_excerpt_policy": "stored_utf8_artifact_excerpt_v1",
                            "content_excerpt_status": "included",
                            "content_excerpt": '{"ok": true}',
                            "content_excerpt_chars": 12,
                            "content_excerpt_truncated": False,
                            "content_excerpt_max_chars": 2000,
                        }
                    ],
                    "skipped": [{"path": "large.bin", "reason": "max_bytes"}],
                }
            },
        },
        metadata={"selection_score": 0.9},
    )
    invalid = Program(
        id="invalid-artifact",
        code="x = 2\n",
        fitness=1.0,
        evaluation={
            "is_valid": False,
            "metadata": {
                "artifacts": {
                    "files": [
                        {
                            "path": "invalid.txt",
                            "artifact_path": "evaluator_artifacts/def/invalid.txt",
                            "bytes": 7,
                            "sha256": hashlib.sha256(b"invalid").hexdigest(),
                        }
                    ]
                }
            },
        },
        metadata={"selection_score": 1.0},
    )
    no_artifacts = Program(
        id="no-artifact",
        code="x = 3\n",
        fitness=0.1,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.1},
    )
    for candidate in (no_artifacts, invalid, strong):
        db.log(candidate)

    snapshot = db.artifact_index_snapshot()

    assert snapshot["schema"] == "libreevolve.artifact_index.v1"
    assert snapshot["policy"] == "top_programs_with_evaluator_artifact_evidence"
    assert snapshot["program_count_considered"] == 2
    assert [program["program_id"] for program in snapshot["programs"]] == [
        invalid.id,
        strong.id,
    ]
    strong_record = {
        program["program_id"]: program for program in snapshot["programs"]
    }[strong.id]
    assert strong_record["collection_id"] == "abc123"
    assert strong_record["stage"] == {
        "name": "validate",
        "sample_index": 0,
        "attempt": 1,
    }
    assert strong_record["artifact_count"] == 1
    assert strong_record["retained_file_count"] == 1
    assert strong_record["skipped"] == [{"path": "large.bin", "reason": "max_bytes"}]
    file_record = strong_record["files"][0]
    assert file_record["path"] == "reports/result.json"
    assert file_record["artifact_relative_path"] == "abc123/reports/result.json"
    assert file_record["sha256"] == hashlib.sha256(b'{"ok": true}').hexdigest()
    assert file_record["content_excerpt"] == {
        "policy": "bounded_redacted_artifact_excerpt_v1",
        "chars": 12,
        "sha256": hashlib.sha256(b'{"ok": true}').hexdigest(),
        "preview": '{"ok": true}',
        "preview_chars": 12,
        "truncated": False,
        "redacted": False,
    }

    resurfacing = db.resurfacing_index_snapshot()
    surfaced = {
        record["program_id"]: record for record in resurfacing["programs"]
    }
    assert {
        source["source"] for source in surfaced[strong.id]["sources"]
    } >= {"score", "artifact"}
    assert invalid.id not in surfaced


def test_program_output_index_snapshot_reports_evaluator_output_evidence(tmp_path):
    db = ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))
    payload = {"answer": 42, "status": "ok"}
    payload_text = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    strong = Program(
        id="strong-output",
        code="x = 1\n",
        fitness=0.9,
        evaluation={
            "is_valid": True,
            "metadata": {
                "program_outputs": {
                    "source_key": "program_output",
                    "policy": "strict_json_redact_bound",
                    "max_json_chars": 4000,
                    "json_chars": len(payload_text),
                    "sha256": hashlib.sha256(payload_text.encode("utf-8")).hexdigest(),
                    "redacted": False,
                    "truncated_strings": 0,
                    "value": payload,
                    "omitted": False,
                }
            },
        },
        metadata={"selection_score": 0.9},
    )
    omitted = Program(
        id="omitted-output",
        code="x = 2\n",
        fitness=1.0,
        evaluation={
            "is_valid": True,
            "metadata": {
                "program_outputs": {
                    "source_key": "outputs",
                    "policy": "strict_json_redact_bound",
                    "max_json_chars": 4000,
                    "json_chars": 8001,
                    "sha256": "a" * 64,
                    "redacted": False,
                    "truncated_strings": 0,
                    "value": None,
                    "omitted": True,
                    "preview": '{"blob":"' + ("x" * 500) + '"}',
                }
            },
        },
        metadata={"selection_score": 1.0},
    )
    invalid = Program(
        id="invalid-output",
        code="x = 3\n",
        fitness=0.1,
        evaluation={
            "is_valid": False,
            "metadata": {
                "program_outputs": {
                    "source_key": "program_output",
                    "policy": "strict_json_redact_bound",
                    "max_json_chars": 4000,
                    "json_chars": len(payload_text),
                    "sha256": hashlib.sha256(payload_text.encode("utf-8")).hexdigest(),
                    "redacted": False,
                    "truncated_strings": 0,
                    "value": payload,
                    "omitted": False,
                }
            },
        },
        metadata={"selection_score": 0.1},
    )
    no_output = Program(
        id="no-output",
        code="x = 4\n",
        fitness=0.2,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.2},
    )
    for candidate in (no_output, invalid, omitted, strong):
        db.log(candidate)

    snapshot = db.program_output_index_snapshot()

    assert snapshot["schema"] == "libreevolve.program_output_index.v1"
    assert snapshot["policy"] == "top_programs_with_evaluator_program_output_evidence"
    assert snapshot["program_count_considered"] == 3
    assert snapshot["limitations"] == [
        "runtime_manifest_program_output_index_not_cross_run_database_table",
        "uses_evaluation_metadata_program_outputs_only",
        "bounded_output_metadata_not_full_output_similarity_search",
        "rebuilt_from_current_runtime_history_records",
    ]
    assert [program["program_id"] for program in snapshot["programs"]] == [
        strong.id,
        invalid.id,
        omitted.id,
    ]
    strong_record = snapshot["programs"][0]
    assert strong_record["source_key"] == "program_output"
    assert strong_record["sha256"] == hashlib.sha256(
        payload_text.encode("utf-8")
    ).hexdigest()
    assert strong_record["omitted"] is False
    assert strong_record["value_summary"] == {
        "policy": "bounded_redacted_program_output_value_preview_v1",
        "value_type": "object",
        "chars": len(payload_text),
        "preview": payload_text,
        "preview_chars": len(payload_text),
        "truncated": False,
        "redacted": False,
    }
    omitted_record = snapshot["programs"][2]
    assert omitted_record["omitted"] is True
    assert omitted_record["value_summary"]["value_type"] == "omitted"
    assert omitted_record["value_summary"]["truncated"] is True

    resurfacing = db.resurfacing_index_snapshot()
    surfaced = {
        record["program_id"]: record for record in resurfacing["programs"]
    }
    assert {
        source["source"] for source in surfaced[strong.id]["sources"]
    } >= {"score", "program_output"}
    assert invalid.id not in surfaced

    assert [program.id for program in db.resurface_by_program_output(k=3)] == [
        strong.id,
        omitted.id,
    ]
    assert [
        program.id
        for program in db.resurface_by_program_output(
            k=3,
            source_key="program_output",
        )
    ] == [strong.id]
    assert [
        program.id
        for program in db.resurface_by_program_output(
            k=3,
            source_key="outputs",
            include_omitted=False,
        )
    ] == []
    assert [
        program.id
        for program in db.resurface_by_program_output(
            k=3,
            output_sha256=hashlib.sha256(payload_text.encode("utf-8")).hexdigest(),
        )
    ] == [strong.id]
    assert [
        program.id
        for program in db.resurface_by_program_output(k=3, exclude_ids={strong.id})
    ] == [omitted.id]
    output_program = db.resurface_by_program_output(k=1)[0]
    output_program.code = "mutated"
    assert db.all_programs()[3].code == "x = 1\n"


def test_resurface_candidates_returns_defensive_ranked_programs(tmp_path):
    db = ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))
    top = Program(
        id="top",
        code="x = 1\n",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9},
    )
    second = Program(
        id="second",
        code="x = 2\n",
        fitness=0.8,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.8},
    )
    db.log(top)
    db.log(second)

    surfaced = db.resurface_candidates(k=1, exclude_ids={top.id})

    assert [program.id for program in surfaced] == [second.id]
    surfaced[0].code = "mutated"
    assert db.all_programs()[1].code == "x = 2\n"


def test_resurface_candidates_can_target_declared_objective_metric(tmp_path):
    schema = {
        "metrics": [
            {
                "name": "score",
                "direction": "maximize",
                "primary": True,
                "bounds": [0.0, 1.0],
            },
            {
                "name": "latency",
                "direction": "maximize",
                "primary": False,
                "bounds": [0.0, 1.0],
            },
        ],
        "primary_metric": "score",
        "primary_bounds": [0.0, 1.0],
        "metric_count": 2,
    }
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
        objective_schema=schema,
    )

    balanced = Program(
        id="balanced",
        code="balanced = 1\n",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.9,
            "normalized_metrics": {"score": 0.9, "latency": 0.6},
        },
    )
    latency_leader = Program(
        id="latency-leader",
        code="latency = 1\n",
        fitness=0.4,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.4,
            "normalized_metrics": {"score": 0.4, "latency": 0.98},
        },
    )
    score_leader = Program(
        id="score-leader",
        code="score = 1\n",
        fitness=1.0,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 1.0,
            "normalized_metrics": {"score": 1.0, "latency": 0.1},
        },
    )
    for candidate in (balanced, latency_leader, score_leader):
        db.log(candidate)

    surfaced = db.resurface_candidates(k=2, target_metric="latency")

    assert [program.id for program in surfaced] == [
        latency_leader.id,
        balanced.id,
    ]
    surfaced[0].code = "mutated"
    assert db.all_programs()[1].code == "latency = 1\n"
    assert [
        program.id
        for program in db.resurface_candidates(
            k=2,
            target_metric="latency",
            exclude_ids={latency_leader.id},
        )
    ] == [balanced.id, score_leader.id]


def test_resurface_candidates_can_query_metric_lineage_descriptor_and_feedback(tmp_path):
    schema = {
        "metrics": [
            {
                "name": "score",
                "direction": "maximize",
                "primary": True,
                "bounds": [0.0, 1.0],
            }
        ],
        "primary_metric": "score",
        "primary_bounds": [0.0, 1.0],
        "metric_count": 1,
    }
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
        objective_schema=schema,
    )

    def candidate(
        program_id: str,
        *,
        score: float,
        selection_score: float,
        lineage: list[str] | None = None,
        parent_id: str | None = None,
        diversity: float | None = None,
        feedback_name: str | None = None,
        feedback_score: float | None = None,
    ) -> Program:
        metadata = {
            "selection_score": selection_score,
            "normalized_metrics": {"score": score},
        }
        if diversity is not None:
            metadata["archive_admission"] = {
                "admitted": True,
                "descriptors": {"diversity": diversity},
            }
        evaluation = {"is_valid": True}
        if feedback_name is not None and feedback_score is not None:
            evaluation["metadata"] = {
                "llm_feedback": [
                    {
                        "name": feedback_name,
                        "score": feedback_score,
                        "normalized_score": feedback_score,
                    }
                ]
            }
        return Program(
            id=program_id,
            code=f"{program_id.replace('-', '_')} = 1\n",
            fitness=selection_score,
            parent_id=parent_id,
            lineage=lineage or [],
            evaluation=evaluation,
            metadata=metadata,
        )

    root_a = candidate("root-a", score=0.20, selection_score=0.20)
    child_a = candidate(
        "child-a",
        score=0.70,
        selection_score=0.70,
        parent_id=root_a.id,
        lineage=[root_a.id],
        diversity=0.70,
        feedback_name="reviewer",
        feedback_score=0.40,
    )
    best_child_a = candidate(
        "best-child-a",
        score=0.80,
        selection_score=0.90,
        parent_id=root_a.id,
        lineage=[root_a.id],
        diversity=0.40,
        feedback_name="reviewer",
        feedback_score=0.90,
    )
    root_b = candidate(
        "root-b",
        score=0.95,
        selection_score=0.60,
        diversity=0.95,
        feedback_name="style",
        feedback_score=0.80,
    )
    invalid = Program(
        id="invalid",
        code="invalid = 1\n",
        fitness=1.0,
        evaluation={"is_valid": False},
        metadata={
            "selection_score": 1.0,
            "normalized_metrics": {"score": 1.0},
            "archive_admission": {
                "admitted": False,
                "descriptors": {"diversity": 1.0},
            },
        },
    )
    for program in (root_a, child_a, best_child_a, root_b, invalid):
        db.log(program)

    assert [program.id for program in db.resurface_by_metric("score", k=2)] == [
        root_b.id,
        best_child_a.id,
    ]
    assert [program.id for program in db.resurface_by_lineage(root_a.id, k=2)] == [
        best_child_a.id,
        child_a.id,
    ]
    assert [
        program.id
        for program in db.resurface_by_descriptor(
            "diversity",
            k=2,
            exclude_ids={root_b.id},
        )
    ] == [child_a.id, best_child_a.id]
    assert [program.id for program in db.resurface_by_novelty(k=2)] == [
        root_b.id,
        child_a.id,
    ]
    assert [program.id for program in db.resurface_by_feedback("reviewer", k=2)] == [
        best_child_a.id,
        child_a.id,
    ]
    assert [program.id for program in db.resurface_by_feedback("style", k=2)] == [
        root_b.id
    ]

    surfaced = db.resurface_by_feedback("reviewer", k=1)
    surfaced[0].code = "mutated"
    assert db.all_programs()[2].code == "best_child_a = 1\n"
    assert invalid.id not in {
        program.id for program in db.resurface_by_novelty(k=10)
    }


def test_resurface_query_methods_validate_keys(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
        objective_schema=_objective_schema(),
    )

    with pytest.raises(ValueError, match="target_metric"):
        db.resurface_by_metric("unknown", k=1)
    with pytest.raises(ValueError, match="lineage_root_id"):
        db.resurface_by_lineage("../escape", k=1)
    with pytest.raises(ValueError, match="descriptor"):
        db.resurface_by_descriptor("", k=1)
    with pytest.raises(ValueError, match="feedback_name"):
        db.resurface_by_feedback("sk-" + "proj_sensitive_1234567890abcdef", k=1)
    with pytest.raises(ValueError, match="source_key"):
        db.resurface_by_program_output(k=1, source_key="unsafe")
    with pytest.raises(ValueError, match="output_sha256"):
        db.resurface_by_program_output(k=1, output_sha256="not-a-sha")
    with pytest.raises(ValueError, match="include_omitted"):
        db.resurface_by_program_output(k=1, include_omitted="yes")


def test_resurface_candidates_rejects_unknown_target_metric(tmp_path):
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t"),
        objective_schema=_objective_schema(),
    )

    with pytest.raises(ValueError, match="target_metric"):
        db.resurface_candidates(k=1, target_metric="unknown")


def test_history_records_preserve_static_file_metadata(tmp_path):
    db = ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))
    program = Program(
        files={"main.py": "x = 1\n"},
        primary_file="main.py",
        fitness=1.0,
        evaluation={"is_valid": True},
        static_files=[
            {"path": "fixture.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 4}
        ],
    )

    db.log(program)

    record = json.loads((tmp_path / "t" / "history.jsonl").read_text().splitlines()[0])
    assert record["static_files"] == [
        {
            "path": "fixture.bin",
            "kind": "binary",
            "sha256": "a" * 64,
            "bytes": 4,
            "source_kind": "unknown",
            "mutation_policy": "immutable",
        }
    ]
    restored = _program_from_history_record(record, line_label="candidate")
    assert restored.static_files == program.static_files


def test_manifest_revalidates_mutated_plugin_labels_before_write(tmp_path):
    config = Config(log_dir=str(tmp_path), problem_name="t")
    config.plugins = ["api_key=sk-proj_secret_1234567890"]  # pragma: allowlist secret

    with pytest.raises(ConfigError, match="manifest-safe plugin label"):
        ProgramDatabase(config)

    assert not (tmp_path / "t" / "manifest.json").exists()


def test_manifest_revalidates_mutated_backend_model_before_write(tmp_path):
    config = Config(log_dir=str(tmp_path), problem_name="t")
    config.backends[0]["model"] = "gpt-4o-mini\napi_key=sk-proj_secret_1234567890"  # pragma: allowlist secret

    with pytest.raises(ConfigError, match="manifest-safe model identifier"):
        ProgramDatabase(config)

    assert not (tmp_path / "t" / "manifest.json").exists()


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (lambda config: setattr(config, "problem_name", "../escape"), "problem_name"),
        (lambda config: setattr(config, "run_id", "mutated\nrun"), "run_id"),
        (
            lambda config: setattr(config, "run_id", "sk-proj_runidsecret_1234567890abcdef"),
            "run_id",
        ),
        (lambda config: setattr(config, "max_generations", -99), "max_generations"),
        (lambda config: setattr(config, "max_runtime_seconds", 0), "max_runtime_seconds"),
        (
            lambda config: config.eval_stages.append({"name": "syntax"}),
            "reserved for a built-in eval stage",
        ),
        (
            lambda config: config.backends[0].__setitem__("max_tokens", 0),
            "max_tokens",
        ),
    ],
)
def test_manifest_revalidates_mutated_runtime_config_before_write(tmp_path, mutation, message):
    config = Config(log_dir=str(tmp_path), problem_name="t")
    mutation(config)

    with pytest.raises(ConfigError, match=message):
        ProgramDatabase(config)

    assert not (tmp_path / "t" / "manifest.json").exists()

def test_add_updates_best():
    db = _db(); p = _p(fitness=0.8); db.log(p); db.add(p)
    assert db.best().fitness == 0.8


def test_raw_add_rejects_invalid_evaluation_without_archive_mutation():
    db = _db()
    program = _p(fitness=1.0)
    program.evaluation = {"is_valid": False}

    event = db.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_evaluation"
    assert program.metadata["archive_admission"]["reason"] == "invalid_evaluation"
    assert program.metadata["archive_admission"]["threshold"] == 0.0
    assert db.best() is None


def test_public_add_records_archive_event_on_program_metadata_and_history():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    program = _p(fitness=0.8)

    event = db.add(program)
    db.log(program)

    assert event["admitted"] is True
    assert event["threshold"] == 0.0
    assert program.metadata["archive_admission"]["program_id"] == program.id
    assert program.metadata["archive_admission"]["threshold"] == 0.0
    [record] = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    assert record["metadata"]["archive_admission"]["program_id"] == program.id
    assert record["metadata"]["archive_admission"]["admitted"] is True


def test_archive_and_log_store_program_snapshots_not_live_aliases():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    program = Program(
        id="snapshot-1",
        files={"main.py": "x = 1\n", "helper.py": "VALUE = 1\n"},
        primary_file="main.py",
        fitness=0.8,
        generation=2,
        parent_id="parent-1",
        lineage=["root-1", "parent-1"],
        metadata={"note": {"value": "original"}},
        metrics={"score": 0.8},
        evaluation={"is_valid": True, "metadata": {"stage": "original"}},
    )

    db.add(program)
    db.log(program)

    program.code = "x = 999\n"
    program.files["main.py"] = "x = 999\n"
    program.metrics["score"] = 0.1
    program.metadata["note"]["value"] = "mutated"
    program.metadata["archive_admission"]["reason"] = "mutated"
    program.evaluation["is_valid"] = False
    program.evaluation["metadata"]["stage"] = "mutated"
    program.lineage.append("mutated")

    logged = db.all_programs()[0]
    best = db.best()

    assert logged.code == "x = 1\n"
    assert logged.files["main.py"] == "x = 1\n"
    assert logged.metrics["score"] == 0.8
    assert logged.metadata["note"]["value"] == "original"
    assert logged.metadata["archive_admission"]["reason"] != "mutated"
    assert logged.evaluation["is_valid"] is True
    assert logged.evaluation["metadata"]["stage"] == "original"
    assert logged.lineage == ["root-1", "parent-1"]
    assert best is not None
    assert best.code == "x = 1\n"
    assert best.files["helper.py"] == "VALUE = 1\n"
    assert best.metrics["score"] == 0.8

    logged.files["main.py"] = "changed returned log snapshot\n"
    best.metrics["score"] = 0.0
    best.metadata["archive_admission"]["reason"] = "changed returned best"

    assert db.all_programs()[0].files["main.py"] == "x = 1\n"
    assert db.best().metrics["score"] == 0.8
    assert db.best().metadata["archive_admission"]["reason"] != "changed returned best"


def test_public_add_enforces_default_admission_threshold():
    db = _db()
    program = _p(fitness=-0.25)
    program.evaluation = {"is_valid": True}

    event = db.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "below_threshold"
    assert event["threshold"] == 0.0
    assert program.metadata["archive_admission"]["reason"] == "below_threshold"
    assert db.best() is None


def test_raw_add_rejects_duplicate_archive_ids_before_island_mutation():
    db = _db()
    first = Program(id="same", code="x=1", fitness=0.8, evaluation={"is_valid": True})
    duplicate = Program(id="same", code="x=2", fitness=0.9, evaluation={"is_valid": True})

    event = db.add(first)

    assert event["admitted"] is True
    with pytest.raises(ValueError, match="duplicate archive program id"):
        db.add(duplicate)

    assert db.best().code == "x=1"
    assert "archive_admission" not in duplicate.metadata


def test_admit_rejects_duplicate_archive_ids_across_islands():
    db = ProgramDatabase(Config(log_dir=tempfile.mkdtemp(), problem_name="t", n_islands=2))
    first = Program(id="same", code="x=1", fitness=0.8, evaluation={"is_valid": True})
    duplicate = Program(id="same", code="x=2", fitness=0.9, evaluation={"is_valid": True})

    db.admit(first)

    with pytest.raises(ValueError, match="duplicate archive program id"):
        db.admit(duplicate)

    occupied = [
        program
        for island in db._islands.islands
        for program in island.occupied_cells()
    ]
    assert [program.id for program in occupied] == ["same"]
    assert occupied[0].code == "x=1"


def test_archive_rejects_different_object_with_logged_id():
    db = _db()
    logged = Program(id="same", code="x=logged", fitness=0.4, evaluation={"is_valid": True})
    duplicate = Program(id="same", code="x=archive", fitness=0.8, evaluation={"is_valid": True})

    db.log(logged)

    with pytest.raises(ValueError, match="duplicate archive program id"):
        db.add(duplicate)

    assert db.best() is None


def test_archive_allows_same_logged_object_to_be_admitted_once():
    db = _db()
    program = Program(id="same", code="x=1", fitness=0.8, evaluation={"is_valid": True})

    db.log(program)
    event = db.add(program)

    assert event["admitted"] is True
    assert db.best().id == "same"


@pytest.mark.parametrize("metrics", [{"score": "bad"}, {"score": True}, {"score": math.nan}])
def test_invalid_evaluation_with_malformed_metrics_returns_structured_rejection(metrics):
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": False, "error": "domain_invalid"}
    program.metrics = metrics

    event = db.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_evaluation"
    assert event["evaluation_is_valid"] is False
    assert program.metadata["archive_admission"]["reason"] == "invalid_evaluation"
    assert db.best() is None


def test_admit_records_archive_event_on_program_metadata():
    db = _db()
    p = _p(fitness=0.8)
    p.evaluation = {"is_valid": True}
    event = db.admit(p, threshold=0.0)
    assert event["admitted"] is True
    assert event["cell_admitted"] is True
    assert event["elite_retained"] is True
    assert event["search_state_changed"] is True
    assert event["sampling_eligible"] is True
    assert p.metadata["archive_admission"]["program_id"] == p.id
    assert p.metadata["archive_admission"]["island_id"] == 0
    assert p.metadata["archive_admission"]["threshold"] == 0.0


def test_admit_non_improving_candidate_does_not_advance_island_cursor():
    db = ProgramDatabase(
        Config(
            log_dir=tempfile.mkdtemp(),
            problem_name="t",
            n_islands=2,
            map_elites_bins=1,
            elite_archive_size=1,
        )
    )
    first = Program(
        code="island0",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9},
    )
    second = Program(
        code="island1",
        fitness=0.8,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.8},
    )
    weak = Program(
        code="weak",
        fitness=0.1,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.1},
    )
    replacement = Program(
        code="replacement",
        fitness=1.0,
        evaluation={"is_valid": True},
        metadata={"selection_score": 1.0},
    )

    first_event = db.admit(first)
    second_event = db.admit(second)
    weak_event = db.admit(weak)
    replacement_event = db.admit(replacement)

    assert first_event["island_id"] == 0
    assert second_event["island_id"] == 1
    assert weak_event["island_id"] == 0
    assert weak_event["reason"] == "not_improving_cell"
    assert weak_event["search_state_changed"] is False
    assert weak.metadata["archive_admission"]["admitted"] is False
    assert replacement_event["island_id"] == 0
    assert replacement_event["reason"] == "cell_replaced"
    assert replacement_event["previous_occupant_id"] == first.id

def test_admit_below_threshold_does_not_archive():
    db = _db()
    p = _p(fitness=-0.1)
    p.evaluation = {"is_valid": True}
    event = db.admit(p, threshold=0.0)
    assert event["admitted"] is False
    assert event["reason"] == "below_threshold"
    assert event["cell_admitted"] is False
    assert event["elite_retained"] is False
    assert event["search_state_changed"] is False
    assert event["sampling_eligible"] is False
    assert event["evaluation_is_valid"] is True
    assert event["island_id"] is None
    assert db.best() is None

def test_admit_invalid_evaluation_does_not_archive_even_with_high_fitness():
    db = _db()
    p = _p(fitness=1.0)
    p.evaluation = {"is_valid": False}
    event = db.admit(p, threshold=0.0)
    assert event["admitted"] is False
    assert event["reason"] == "invalid_evaluation"
    assert event["evaluation_is_valid"] is False
    assert db.best() is None


@pytest.mark.parametrize("fitness", [float("nan"), float("inf"), float("-inf")])
def test_admit_rejects_non_finite_fitness_before_archive(fitness):
    db = _db()
    p = _p(fitness=1.0)
    p.fitness = fitness
    p.evaluation = {"is_valid": True}
    p.metadata["selection_score"] = 0.5

    event = db.admit(p, threshold=0.0)

    assert event["admitted"] is False
    assert event["reason"] == "non_finite_fitness"
    assert event["evaluation_is_valid"] is True
    assert db.best() is None


@pytest.mark.parametrize("fitness", [True, False, "1.0"])
def test_admit_rejects_invalid_fitness_type_before_archive(fitness):
    db = _db()
    p = _p(fitness=1.0)
    p.fitness = fitness
    p.evaluation = {"is_valid": True}

    event = db.admit(p, threshold=0.0)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_fitness_type"
    assert event["evaluation_is_valid"] is True
    assert db.best() is None


@pytest.mark.parametrize("is_valid", [None, "false", 1])
def test_admit_requires_exact_boolean_validity(is_valid):
    db = _db()
    p = _p(fitness=1.0)
    p.evaluation = {} if is_valid is None else {"is_valid": is_valid}

    event = db.admit(p, threshold=0.0)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_evaluation"
    assert event["evaluation_is_valid"] is False
    assert db.best() is None


def test_admit_cannot_receive_malformed_evolve_block_program():
    with pytest.raises(ValueError, match="main.py:malformed_evolve_blocks:orphan_end"):
        Program(
            files={"main.py": "# EVOLVE-BLOCK-END\n"},
            evaluation={"is_valid": True},
            fitness=1.0,
        )


def test_program_construction_rejects_non_mapping_evaluation():
    with pytest.raises(ValueError, match="Program evaluation must be a JSON-safe evaluation mapping"):
        Program(code="x=1", fitness=1.0, evaluation=[])


def test_admit_prevalidates_history_record_before_archive_mutation():
    db = _db()
    p = _p(fitness=1.0)
    p.evaluation = {"is_valid": True}
    p.metadata["bad"] = {"not", "json"}

    with pytest.raises(ValueError, match="Program metadata.bad must be JSON-safe metadata"):
        db.admit(p, threshold=0.0)

    assert db.best() is None
    assert db.all_programs() == []


def test_log_revalidates_mutated_program_metadata_before_history_write():
    db = _db()
    p = _p(fitness=0.5)
    p.metadata = []

    with pytest.raises(ValueError, match="Program metadata must be a JSON-safe metadata mapping"):
        db.log(p)

    assert db.all_programs() == []
    assert not Path(db._jsonl).exists() or Path(db._jsonl).read_text(encoding="utf-8") == ""


def test_admit_revalidates_mutated_program_metadata_before_archive_write():
    db = _db()
    p = _p(fitness=1.0)
    p.metadata = ["bad"]

    with pytest.raises(ValueError, match="Program metadata must be a JSON-safe metadata mapping"):
        db.admit(p, threshold=0.0)

    assert db.best() is None
    assert db.all_programs() == []
    assert "archive_admission" not in getattr(p, "metadata", {})


@pytest.mark.parametrize("evaluation", [[], {"bad": object()}])
def test_admit_revalidates_mutated_program_evaluation_before_archive_write(evaluation):
    db = _db()
    p = _p(fitness=1.0)
    p.evaluation = evaluation

    with pytest.raises(ValueError, match="Program evaluation"):
        db.admit(p, threshold=0.0)

    assert db.best() is None
    assert db.all_programs() == []
    assert "archive_admission" not in getattr(p, "metadata", {})


def test_log_failure_revalidates_mutated_program_metadata_before_side_effects():
    db = _db()
    parent = _p()
    child = _p()
    child.metadata = {"bad": object()}

    with pytest.raises(ValueError, match="Program metadata.bad must be JSON-safe metadata"):
        db.log_failure(child, parent, "mutation", diff_error="bad_diff")

    assert "failure_record" not in getattr(child, "metadata", {})


@pytest.mark.parametrize("evaluation", [[], {"bad": object()}])
def test_log_revalidates_mutated_program_evaluation_before_history_write(evaluation):
    db = _db()
    p = _p(fitness=0.5)
    p.evaluation = evaluation

    with pytest.raises(ValueError, match="Program evaluation"):
        db.log(p)

    assert db.all_programs() == []
    assert not Path(db._jsonl).exists() or Path(db._jsonl).read_text(encoding="utf-8") == ""


@pytest.mark.parametrize("evaluation", [[], {"bad": object()}])
def test_log_failure_revalidates_mutated_program_evaluation_before_side_effects(evaluation):
    db = _db()
    parent = _p()
    child = _p()
    child.evaluation = evaluation

    with pytest.raises(ValueError, match="Program evaluation"):
        db.log_failure(child, parent, "mutation", diff_error="bad_diff")

    assert "failure_record" not in child.metadata
    assert db._failure_counts == {}


@pytest.mark.parametrize("threshold", [math.nan, math.inf, "0"])
def test_admit_rejects_invalid_threshold_before_archive_mutation(threshold):
    db = _db()
    p = _p(fitness=1.0)
    p.evaluation = {"is_valid": True}

    with pytest.raises(ValueError, match="archive admission threshold"):
        db.admit(p, threshold=threshold)

    assert db.best() is None
    assert "archive_admission" not in p.metadata


def test_rejected_non_finite_selection_score_is_history_safe():
    db = _db()
    p = _p(fitness=1.0)
    p.fitness = math.inf
    p.evaluation = {"is_valid": False}

    event = db.admit(p, threshold=0.0)

    assert event["admitted"] is False
    assert event["selection_score"] is None
    assert p.metadata["archive_admission"]["selection_score"] is None


def test_log_without_add_not_in_archive():
    db = _db(); db.log(_p(fitness=-0.3))
    assert db.best() is None

def test_sample_exploit():
    db = _db()
    for f in (0.3, 0.7):
        p = _p(fitness=f); db.log(p); db.add(p)
    assert db.sample("exploit").fitness == 0.7

def test_sample_diverse_excludes_program_ids():
    db = _db()
    p = _p(fitness=0.7); db.log(p); db.add(p)
    assert db.sample_diverse(k=3, exclude_ids={p.id}) == []


def test_sample_diverse_normalizes_exclude_id_sequences():
    db = _db()
    p = _p(fitness=0.7)
    db.add(p)

    assert db.sample_diverse(k=3, exclude_ids=[p.id, p.id]) == []
    assert db.sample_diverse(k=3, exclude_ids=(p.id,)) == []


@pytest.mark.parametrize(
    "exclude_ids",
    [
        "program-id",
        {"program-id": True},
        {1},
        ["bad id"],
        ["api_key=sk-proj_exclude_secret_1234567890"],  # pragma: allowlist secret
    ],
)
def test_sample_diverse_rejects_invalid_exclude_ids(exclude_ids):
    db = _db()
    db.add(_p(fitness=0.7))

    with pytest.raises(ValueError, match="database exclude_ids"):
        db.sample_diverse(k=3, exclude_ids=exclude_ids)


def test_sample_diverse_accepts_zero_and_oversized_counts():
    db = _db()
    for index in range(2):
        program = _p(code=f"x={index}", fitness=index * 0.1)
        db.admit(program)

    assert db.sample_diverse(k=0) == []
    assert len(db.sample_diverse(k=10)) <= 2


def test_database_random_sampling_uses_local_rng_not_process_global():
    db = ProgramDatabase(
        Config(log_dir=tempfile.mkdtemp(), problem_name="t", n_islands=1),
        rng=random.Random(42),
    )
    for index in range(3):
        db.admit(_p(code=f"x={index}", fitness=0.4 + index * 0.1))

    random.seed(123)
    expected_after_sampling = random.Random(123).random()

    assert db.sample("explore") is not None
    assert db.sample_diverse(k=2, strategy="random")
    assert random.random() == expected_after_sampling


@pytest.mark.parametrize("k", ["2", True, 1.5, -1])
def test_sample_diverse_rejects_invalid_counts(k):
    db = _db()
    p = _p(fitness=0.7)
    db.add(p)

    with pytest.raises(ValueError, match="database sample count"):
        db.sample_diverse(k=k)


def test_metric_sampling_cycles_objective_schema_metric_targets_primary_first():
    tmpdir = tempfile.mkdtemp()
    schema = {
        "metrics": [
            {
                "name": "latency",
                "direction": "maximize",
                "primary": False,
                "bounds": [0.0, 1.0],
            },
            {
                "name": "primary",
                "direction": "maximize",
                "primary": True,
                "bounds": [0.0, 1.0],
            },
        ],
        "primary_metric": "primary",
        "primary_bounds": [0.0, 1.0],
        "metric_count": 2,
    }
    db = ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t", n_islands=1),
        objective_schema=schema,
    )
    latency_leader = Program(
        code="latency",
        fitness=0.1,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.1,
            "normalized_metrics": {"primary": 0.1, "latency": 0.95},
        },
    )
    primary_leader = Program(
        code="primary",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.9,
            "normalized_metrics": {"primary": 0.9, "latency": 0.1},
        },
    )
    db.admit(latency_leader)
    db.admit(primary_leader)

    assert db.sample("metric").id == primary_leader.id
    assert db.last_sample_metadata() == {
        "strategy": "metric",
        "selected_program_id": primary_leader.id,
        "target_metric": "primary",
        "metric_target_index": 0,
        "metric_target_count": 2,
    }
    assert db.sample("metric").id == latency_leader.id
    assert db.last_sample_metadata()["target_metric"] == "latency"
    assert db.sample("metric").id == primary_leader.id
    assert [p.id for p in db.sample_diverse(k=1, strategy="metric")] == [
        primary_leader.id
    ]


def test_elite_only_archive_rows_resurface_through_public_retained_strategies():
    db = ProgramDatabase(
        Config(
            log_dir=tempfile.mkdtemp(),
            problem_name="t",
            n_islands=1,
            map_elites_bins=1,
        )
    )
    occupied = Program(
        code="occupied",
        fitness=0.9,
        generation=1,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9, "normalized_metrics": {"score": 0.1}},
    )
    elite_only = Program(
        code="elite_only",
        fitness=0.1,
        generation=9,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.1, "normalized_metrics": {"score": 0.95}},
    )

    occupied_event = db.admit(occupied)
    elite_event = db.admit(elite_only)

    assert occupied_event["sampling_eligible"] is True
    assert elite_event["reason"] == "elite_only"
    assert elite_event["elite_retained"] is True
    assert elite_event["sampling_eligible"] is False
    assert db.sample("explore").id == occupied.id
    assert db.sample("metric").id == elite_only.id
    assert db.sample("recency").id == elite_only.id
    assert [p.id for p in db.sample_diverse(k=1, strategy="metric")] == [
        elite_only.id
    ]
    assert [p.id for p in db.sample_diverse(k=2, strategy="selection")] == [
        occupied.id,
        elite_only.id,
    ]
    assert [p.id for p in db.sample_diverse(k=2, strategy="random")] == [
        occupied.id
    ]


def test_archive_sequence_is_persisted_and_drives_recency_sampling():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t", n_islands=1))
    older_high_score = Program(
        code="older",
        fitness=0.9,
        generation=0,
        evaluation={"is_valid": True},
    )
    newer_low_score = Program(
        code="newer",
        fitness=0.1,
        generation=0,
        evaluation={"is_valid": True},
    )

    db.admit(older_high_score)
    db.log(older_high_score)
    db.admit(newer_low_score)
    db.log(newer_low_score)

    assert db.sample("recency").id == newer_low_score.id
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "history.jsonl").read_text().splitlines()
    ]
    assert records[0]["metadata"]["archive_sequence"] == 1
    assert records[0]["metadata"]["archive_admission"]["archive_sequence"] == 1
    assert records[1]["metadata"]["archive_sequence"] == 2
    assert records[1]["metadata"]["archive_admission"]["archive_sequence"] == 2


def test_archive_state_snapshot_exposes_island_cursor_for_runtime_manifest():
    db = ProgramDatabase(
        Config(
            log_dir=tempfile.mkdtemp(),
            problem_name="t",
            n_islands=2,
            map_elites_bins=1,
            elite_archive_size=1,
        )
    )
    first = Program(
        code="island0",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9},
    )
    second = Program(
        code="island1",
        fitness=0.8,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.8},
    )
    weak = Program(
        code="weak",
        fitness=0.1,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.1},
    )

    db.admit(first)
    db.admit(second)
    weak_event = db.admit(weak)

    snapshot = db.archive_state_snapshot()
    assert weak_event["search_state_changed"] is False
    assert snapshot["schema"] == "libreevolve.island_state.v1"
    assert snapshot["resume_status"] == (
        "snapshot_persisted_cursor_and_full_archive_restore_supported"
    )
    assert snapshot["next_island_id"] == 0
    assert snapshot["archive_sequence"] == 3
    assert snapshot["frontier_sample_index"] == 0
    assert snapshot["archive_sequence_by_program_id"] == {
        first.id: 1,
        second.id: 2,
    }
    assert snapshot["topology_policy"]["schema"] == "libreevolve.island_topology_policy.v1"
    assert snapshot["topology_policy"]["configured_n_islands"] == 2
    assert snapshot["topology_policy"]["default_n_islands"] == 5
    assert snapshot["topology_policy"]["island_count_configurable"] is True
    assert snapshot["topology_policy"]["migration_topology"] == "ring"
    assert snapshot["topology_policy"]["adaptive_island_count_supported"] is False
    assert snapshot["topology_policy"]["non_ring_topologies_supported"] is False
    assert snapshot["topology_policy"]["alphaevolve_policy_ready"] is False
    assert snapshot["migration_replay"]["status"] == "not_applied_as_restore_engine"
    assert snapshot["migration_replay"]["replay_engine_supported"] is False
    assert snapshot["migration_replay"]["migration_sequence"] == 0
    assert snapshot["islands"] == [
        {
            "island_id": 0,
            "occupied_cell_count": 1,
            "elite_count": 1,
            "pareto_frontier_count": 0,
            "metric_cell_archive_count": 0,
        },
        {
            "island_id": 1,
            "occupied_cell_count": 1,
            "elite_count": 1,
            "pareto_frontier_count": 0,
            "metric_cell_archive_count": 0,
        },
    ]


def test_archive_state_snapshot_rejects_migration_replay_overclaim():
    snapshot = _archive_state_snapshot()
    snapshot["migration_replay"] = {
        "schema": "libreevolve.island_migration_replay_policy.v1",
        "status": "not_applied_as_restore_engine",
        "policy": (
            "archive_contents_snapshot_restores_current_placements_without_replaying_migration_events"
        ),
        "migration_sequence": snapshot["migration_sequence"],
        "replay_engine_supported": True,
        "archive_contents_restore_covers_current_placements": True,
        "limitations": ["migration_event_order_not_replayed"],
    }

    with pytest.raises(ArchiveStateRestoreError, match="must not claim"):
        validate_archive_state_snapshot(snapshot)


def test_archive_state_snapshot_rejects_topology_policy_overclaim():
    snapshot = _archive_state_snapshot()
    snapshot["topology_policy"] = {
        "schema": "libreevolve.island_topology_policy.v1",
        "status": "configured_synchronous_ring_topology",
        "policy": "config_n_islands_controls_local_synchronous_ring_migration_default_five",
        "configured_n_islands": 2,
        "default_n_islands": 5,
        "island_count_configurable": True,
        "migration_topology": "ring",
        "migration_execution": "synchronous_local_generation_boundary",
        "adaptive_island_count_supported": True,
        "non_ring_topologies_supported": False,
        "alphaevolve_policy_ready": False,
        "limitations": ["no_adaptive_island_count_policy"],
    }

    with pytest.raises(ArchiveStateRestoreError, match="adaptive island"):
        validate_archive_state_snapshot(snapshot)


def test_database_constructor_restores_compact_island_cursor_state(tmp_path):
    snapshot = _archive_state_snapshot()
    db = ProgramDatabase(
        Config(log_dir=str(tmp_path), problem_name="t", n_islands=2),
        archive_state_snapshot=snapshot,
    )
    program = Program(
        id="new_program",
        code="x=1",
        fitness=0.7,
        evaluation={"is_valid": True},
    )

    event = db.admit(program)
    manifest = json.loads((tmp_path / "t" / "manifest.json").read_text())

    assert event["island_id"] == snapshot["next_island_id"]
    assert event["archive_sequence"] == snapshot["archive_sequence"] + 1
    restored = manifest["policies"]["archive_cursor_restore"]
    assert restored["status"] == "cursor_state_restored"
    assert restored["archive_contents_restored"] is False
    assert restored["full_archive_restore_required"] is True
    assert restored["next_island_id"] == snapshot["next_island_id"]
    assert restored["archive_sequence"] == snapshot["archive_sequence"]
    assert restored["frontier_sample_index"] == snapshot["frontier_sample_index"]
    assert restored["archive_sequence_by_program_id"] == {
        "p1": 1,
        "p2": 3,
    }


def test_database_constructor_restores_replayable_archive_contents(tmp_path):
    source_dir = tmp_path / "source"
    source = ProgramDatabase(
        Config(
            log_dir=str(source_dir),
            problem_name="t",
            n_islands=2,
            map_elites_bins=1,
        )
    )
    first = Program(
        id="p1",
        code="island0",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9},
    )
    second = Program(
        id="p2",
        code="island1",
        fitness=0.8,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.8},
    )
    source.admit(first)
    source.log(first)
    source.admit(second)
    source.log(second)
    archive_state = source.archive_state_snapshot()
    source.update_manifest_runtime({"history": {"archive_state": archive_state}})

    bundle = load_archive_restore_bundle(
        source_dir / "t" / "manifest.json",
        source_dir / "t" / "history.jsonl",
    )
    restored = ProgramDatabase(
        Config(
            log_dir=str(tmp_path / "restored"),
            problem_name="t",
            n_islands=2,
            map_elites_bins=1,
        ),
        **bundle,
    )
    manifest = json.loads((tmp_path / "restored" / "t" / "manifest.json").read_text())

    assert archive_state["archive_contents"]["restore_status"] == (
        "snapshot_persisted_full_archive_restore_supported"
    )
    assert manifest["policies"]["archive_cursor_restore"]["status"] == (
        "archive_state_restored"
    )
    assert manifest["policies"]["archive_cursor_restore"]["archive_contents_restored"] is True
    assert manifest["policies"]["archive_cursor_restore"]["full_archive_restore_required"] is False
    assert restored.best().id == "p1"
    assert {program.id for program in restored.sample_diverse(k=2, strategy="random")} == {
        "p1",
        "p2",
    }


def test_database_full_archive_restore_uses_restored_cursor_for_next_admission(tmp_path):
    source_dir = tmp_path / "source"
    source = ProgramDatabase(
        Config(
            log_dir=str(source_dir),
            problem_name="t",
            n_islands=2,
            map_elites_bins=1,
            elite_archive_size=1,
        )
    )
    first = Program(
        id="p1",
        code="island0",
        fitness=0.9,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.9},
    )
    second = Program(
        id="p2",
        code="island1",
        fitness=0.8,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.8},
    )
    source.admit(first)
    source.log(first)
    source.admit(second)
    source.log(second)
    weak = Program(
        id="weak",
        code="weak",
        fitness=0.1,
        evaluation={"is_valid": True},
        metadata={"selection_score": 0.1},
    )
    weak_event = source.admit(weak)
    archive_state = source.archive_state_snapshot()
    source.update_manifest_runtime({"history": {"archive_state": archive_state}})

    bundle = load_archive_restore_bundle(
        source_dir / "t" / "manifest.json",
        source_dir / "t" / "history.jsonl",
    )
    restored = ProgramDatabase(
        Config(
            log_dir=str(tmp_path / "restored"),
            problem_name="t",
            n_islands=2,
            map_elites_bins=1,
            elite_archive_size=1,
        ),
        **bundle,
    )
    replacement = Program(
        id="replacement",
        code="replacement",
        fitness=1.0,
        evaluation={"is_valid": True},
        metadata={"selection_score": 1.0},
    )

    event = restored.admit(replacement)

    assert weak_event["search_state_changed"] is False
    assert archive_state["next_island_id"] == 0
    assert event["island_id"] == 0
    assert event["archive_sequence"] == archive_state["archive_sequence"] + 1
    assert event["previous_occupant_id"] == "p1"
    assert event["search_state_changed"] is True


def test_database_constructor_rejects_cursor_snapshot_for_wrong_island_count(tmp_path):
    snapshot = _archive_state_snapshot()

    with pytest.raises(ValueError, match="n_islands must match"):
        ProgramDatabase(
            Config(log_dir=str(tmp_path), problem_name="t", n_islands=3),
            archive_state_snapshot=snapshot,
        )


def test_log_quarantines_mutated_invalid_generation():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    program = _p(fitness=0.5)
    program.generation = "api_key=sk-proj_secret_1234567890"

    with pytest.raises(StrictJsonlError, match="generation must be"):
        db.log(program)

    run_dir = Path(tmpdir) / "t"
    assert not (run_dir / "history.jsonl").exists()
    assert "generation must be" in (run_dir / "history_invalid.jsonl").read_text()


@pytest.mark.parametrize("metrics", [{"score": "bad"}, {"score": True}, {"score": Fraction(1, 2)}])
def test_log_quarantines_mutated_invalid_metrics(metrics):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    program = _p(fitness=0.5)
    program.metrics = metrics

    with pytest.raises(StrictJsonlError, match="Program metric values"):
        db.log(program)

    run_dir = Path(tmpdir) / "t"
    assert not (run_dir / "history.jsonl").exists()
    assert "Program metric values" in (run_dir / "history_invalid.jsonl").read_text()


@pytest.mark.parametrize(
    "metrics",
    [
        {"api_key=sk-proj_metric_key_secret_1234567890": 0.2},  # pragma: allowlist secret
        {"score\u202e": 0.2},
        {"score-secret": 0.2},
    ],
)
def test_log_quarantines_mutated_unsafe_metric_names(metrics):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    program = _p(fitness=0.5)
    program.metrics = metrics

    with pytest.raises(StrictJsonlError, match="Program metric names"):
        db.log(program)

    run_dir = Path(tmpdir) / "t"
    assert not (run_dir / "history.jsonl").exists()
    text = (run_dir / "history_invalid.jsonl").read_text()
    assert "Program metric names" in text
    assert "sk-proj_metric_key_secret" not in text


def test_admit_rejects_mutated_invalid_generation_before_archive():
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": True}
    program.generation = -10

    with pytest.raises(StrictJsonlError, match="generation must be"):
        db.admit(program)

    assert db.best() is None


def test_admit_rejects_mutated_invalid_metrics_before_archive():
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": True}
    program.metrics = {"score": True}

    with pytest.raises(ValueError, match="Program metric values"):
        db.admit(program)

    assert db.best() is None


def test_admit_rejects_mutated_unsafe_metric_names_before_archive():
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": True}
    program.metrics = {"score\u202e": 0.2}

    with pytest.raises(ValueError, match="Program metric names"):
        db.admit(program)

    assert db.best() is None
    assert db.all_programs() == []


def test_admit_rejects_non_json_native_metrics_before_archive():
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": True}
    program.metrics = {"score": Fraction(1, 2), "is_valid": True}

    with pytest.raises(ValueError, match="JSON-native finite numbers"):
        db.admit(program)

    assert db.best() is None
    assert db.all_programs() == []


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda program: setattr(program, "id", "api_key=sk-proj_candidate_secret_1234567890\nnext"), "Program id"),  # pragma: allowlist secret
        (lambda program: setattr(program, "parent_id", "parent\nnext"), "Program parent_id"),
        (lambda program: setattr(program, "lineage", ["root", "bad\nnext"]), r"Program lineage\[1\]"),
    ],
)
def test_admit_rejects_mutated_unsafe_program_identity_before_archive(mutate, message):
    db = _db()
    program = _p(fitness=0.5)
    program.evaluation = {"is_valid": True}
    mutate(program)

    with pytest.raises(StrictJsonlError, match=message):
        db.admit(program)

    assert db.best() is None


def test_log_quarantines_mutated_unsafe_program_identity():
    db = _db()
    program = _p(fitness=0.5)
    program.id = "api_key=sk-proj_candidate_secret_1234567890\nnext"  # pragma: allowlist secret

    with pytest.raises(StrictJsonlError, match="Program id"):
        db.log(program)

    run_dir = Path(db._jsonl).parent
    assert not (run_dir / "history.jsonl").exists()
    assert "Program id" in (run_dir / "history_invalid.jsonl").read_text()


def test_log_rejects_duplicate_program_ids():
    db = _db()
    first = _p(fitness=0.5)
    second = _p(code="x=2", fitness=0.4)
    second.id = first.id
    db.log(first)

    with pytest.raises(StrictJsonlError, match="duplicate program id"):
        db.log(second)

    run_dir = Path(db._jsonl).parent
    accepted = [
        json.loads(line)
        for line in (run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    quarantine = [
        json.loads(line)
        for line in (run_dir / "history_invalid.jsonl").read_text(encoding="utf-8").splitlines()
    ]
    assert [record["id"] for record in accepted] == [first.id]
    assert len(quarantine) == 1
    assert "duplicate program id" in quarantine[0]["message"]
    assert second.code in quarantine[0]["record_repr"]
    assert db._ids == {first.id}
    assert [program.code for program in db.all_programs()] == [first.code]


def test_log_honors_quarantine_snapshot_hash_only_retention():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(
        Config(
            log_dir=tmpdir,
            problem_name="t",
            quarantine_snapshot_retention_mode="hash_only",
        )
    )
    first = _p(code="x=1", fitness=0.5)
    second = _p(
        code="api_key=sk-proj_quarantine_snapshot_secret_123456",
        fitness=0.4,
    )
    second.id = first.id
    db.log(first)

    with pytest.raises(StrictJsonlError, match="duplicate program id"):
        db.log(second)

    run_dir = Path(tmpdir) / "t"
    [record] = [
        json.loads(line)
        for line in (run_dir / "history_invalid.jsonl").read_text(
            encoding="utf-8"
        ).splitlines()
    ]
    assert "record_repr" not in record
    assert "record_repr_truncated" not in record
    retention = record["record_repr_retention"]
    assert retention["retention_mode"] == "hash_only"
    assert retention["sha256"]
    assert retention["stored_chars"] == 0
    assert "sk-proj_" not in json.dumps(record)


def test_failure_history_quarantines_mutated_unsafe_program_identity():
    db = _db()
    parent = _p(fitness=0.5)
    child = _p(fitness=-0.1)
    child.id = "api_key=sk-proj_candidate_secret_1234567890\nnext"  # pragma: allowlist secret

    with pytest.raises(StrictJsonlError, match="Program id"):
        db.log_failure(child, parent, "mutation", "diff failed")

    run_dir = Path(db._jsonl).parent
    assert not (run_dir / "failure_history.jsonl").exists()
    assert "Program id" in (run_dir / "failure_history_invalid.jsonl").read_text()


def test_failure_history_quarantines_mutated_invalid_generation():
    db = _db()
    parent = _p(fitness=0.5)
    child = _p(fitness=-0.1)
    child.generation = "bad"

    with pytest.raises(StrictJsonlError, match="generation must be"):
        db.log_failure(child, parent, "mutation", "diff failed")

    run_dir = Path(db._jsonl).parent
    assert not (run_dir / "failure_history.jsonl").exists()
    assert "generation must be" in (run_dir / "failure_history_invalid.jsonl").read_text()


def test_log_writes_jsonl():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(_p(fitness=0.5))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["fitness"] == 0.5


def test_run_artifacts_include_current_schema_markers():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=0.5)
    child = _p(fitness=-0.1)
    db.log(parent)
    db.log_failure(child, parent, "mutation", "diff failed")
    db.log_llm_call(
        {
            "id": "call-1",
            "sequence_id": 1,
            "role": "mutation",
            "backend_idx": 0,
            "backend_name": "backend",
            "prompt_chars": 1,
            "prompt_sha256": "0" * 64,
            "status": "ok",
            "output_chars": 1,
            "output_sha256": "1" * 64,
            "counts_before": [0],
            "counts_after": [1],
            "will_retry": False,
            "will_fallback": False,
        }
    )
    db.log_llm_call(
        {
            "record_type": "reward",
            "call_id": "call-1",
            "backend_idx": 0,
            "reward": 0.5,
            "reward_raw": 0.5,
            "rewarded": True,
        }
    )

    run_dir = Path(tmpdir) / "t"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    history = json.loads((run_dir / "history.jsonl").read_text(encoding="utf-8").splitlines()[0])
    failure = json.loads(
        (run_dir / "failure_history.jsonl").read_text(encoding="utf-8").splitlines()[0]
    )
    llm_call, llm_reward = [
        json.loads(line)
        for line in (run_dir / "llm_calls.jsonl").read_text(encoding="utf-8").splitlines()
    ]

    assert manifest["schema_version"] == ARTIFACT_SCHEMA_VERSION
    assert manifest["artifact_schema"]["name"] == RUN_MANIFEST_SCHEMA
    assert manifest["artifact_schema"]["jsonl_records"]["history.jsonl"] == HISTORY_RECORD_SCHEMA
    assert (
        manifest["artifact_schema"]["jsonl_records"]["evaluator_results.jsonl"]
        == EVALUATOR_RESULT_RECORD_SCHEMA
    )
    assert (
        manifest["artifact_schema"]["jsonl_records"]["archive_events.jsonl"]
        == ARCHIVE_EVENT_RECORD_SCHEMA
    )
    quarantine_schema = manifest["artifact_schema"]["quarantine_jsonl_records"]
    assert sorted(quarantine_schema) == [
        "archive_events_invalid.jsonl",
        "controller_budget_events_invalid.jsonl",
        "failure_history_invalid.jsonl",
        "history_invalid.jsonl",
        "llm_calls_invalid.jsonl",
        "manifest_invalid.jsonl",
        "prompt_history_invalid.jsonl",
    ]
    assert quarantine_schema["history_invalid.jsonl"] == {
        "source_stream": "history.jsonl",
        "source_record_schema": HISTORY_RECORD_SCHEMA,
        "diagnostic_record_schema": QUARANTINE_RECORD_SCHEMA,
        "diagnostic_fields": {
            "error": "exception class name",
            "message": "bounded redacted serialization or repair diagnostic",
            "record_type": "original record Python type label",
            "record_repr_retention": "redacted|hash_only|off",
            "record_repr": "optional retained rejected-record snapshot",
            "record_repr_truncated": "optional retained snapshot truncation flag",
            "record_repr_error": "optional safe snapshot-construction diagnostic",
        },
        "retention_mode_field": "config.quarantine_snapshot_retention_mode",
        "lifecycle_status": "optional_diagnostic_lifecycle_managed",
    }
    assert (
        quarantine_schema["prompt_history_invalid.jsonl"]["source_record_schema"]
        == PROMPT_HISTORY_RECORD_SCHEMA
    )
    assert (
        quarantine_schema["manifest_invalid.jsonl"]["source_record_schema"]
        == RUN_MANIFEST_SCHEMA
    )
    assert quarantine_schema["llm_calls_invalid.jsonl"]["source_record_schema"] == {
        "call": LLM_CALL_RECORD_SCHEMA,
        "reward": LLM_REWARD_RECORD_SCHEMA,
    }
    non_jsonl_schema = manifest["artifact_schema"]["non_jsonl_artifacts"]
    assert sorted(non_jsonl_schema) == [
        "best.py",
        "best_workspace",
        "evaluator_artifacts",
        "manifest.json",
        "paper_artifacts",
        "plugin_artifacts",
        "task_specification.json",
    ]
    assert set(non_jsonl_schema) <= RUN_ARTIFACT_NAMES
    assert non_jsonl_schema["manifest.json"]["runtime_pointer_location"] == "self"
    assert non_jsonl_schema["best.py"]["kind"] == "file"
    assert non_jsonl_schema["best.py"]["hash_policy"] == "file_sha256_when_present"
    assert (
        non_jsonl_schema["best.py"]["runtime_pointer_location"]
        == 'runtime.artifacts["best.py"]'
    )
    for artifact_name in (
        "best_workspace",
        "evaluator_artifacts",
        "plugin_artifacts",
        "paper_artifacts",
    ):
        artifact = non_jsonl_schema[artifact_name]
        assert artifact["kind"] == "directory"
        assert artifact["hash_policy"] == "tree_hash_when_present"
        assert (
            artifact["lifecycle_status"]
            == "known_artifact_collision_checked_and_overwrite_managed"
        )
    assert (
        non_jsonl_schema["task_specification.json"]["runtime_pointer_location"]
        == "runtime.history.task_spec_artifact_resolution_report."
        "standalone_task_spec_artifact"
    )
    assert history["schema_version"] == ARTIFACT_SCHEMA_VERSION
    assert history["record_schema"] == HISTORY_RECORD_SCHEMA
    assert failure["record_schema"] == FAILURE_RECORD_SCHEMA
    assert llm_call["record_schema"] == LLM_CALL_RECORD_SCHEMA
    assert llm_reward["record_schema"] == LLM_REWARD_RECORD_SCHEMA


def test_generated_run_artifact_inventory_covers_cleanup_and_schema_surfaces():
    inventory = generated_run_artifact_inventory()
    manifest_schema = run_artifact_schema()
    schema_declared = (
        set(manifest_schema["jsonl_records"])
        | set(manifest_schema["quarantine_jsonl_records"])
        | set(manifest_schema["non_jsonl_artifacts"])
    )

    assert RUN_ARTIFACT_NAMES is SCHEMA_RUN_ARTIFACT_NAMES
    assert set(inventory) == RUN_ARTIFACT_NAMES
    assert set(inventory) == schema_declared
    assert all(record["cleanup_managed"] is True for record in inventory.values())
    assert all(
        record["lifecycle_status"]
        == "known_artifact_collision_checked_and_overwrite_managed"
        for record in inventory.values()
    )
    assert inventory["prompt_current_binding_table.jsonl"] == {
        "path": "prompt_current_binding_table.jsonl",
        "artifact_kind": "jsonl_record_stream",
        "schema_pointer": (
            'artifact_schema.jsonl_records["prompt_current_binding_table.jsonl"]'
        ),
        "record_schema": "libreevolve.prompt_current_binding_table.v1",
        "writer_owner": "prompt current-binding table finalizer",
        "reader_owner": "prompt current-binding reports and cross-run analysis",
        "lifecycle_status": "known_artifact_collision_checked_and_overwrite_managed",
        "cleanup_managed": True,
        "runtime_pointer_location": (
            'runtime.artifacts["prompt_current_binding_table.jsonl"]'
        ),
        "restore_show_handling": "accepted stream reader or summary report input",
    }
    assert inventory["manifest_invalid.jsonl"]["source_stream"] == "manifest.json"
    assert inventory["paper_artifacts"]["restore_show_handling"] == (
        "paper-source report validators and docs"
    )


def test_non_jsonl_artifact_inventory_anchors_resolve_to_source():
    inventory = generated_run_artifact_inventory()
    non_jsonl_names = set(run_artifact_schema()["non_jsonl_artifacts"])

    for artifact_name in sorted(non_jsonl_names):
        artifact = inventory[artifact_name]
        anchors = artifact.get("implementation_anchors")
        assert isinstance(anchors, dict), artifact_name
        assert set(anchors) == {"writer", "runtime_pointer", "show_restore_reader"}
        for phase, records in anchors.items():
            assert isinstance(records, list) and records, (artifact_name, phase)
            for record in records:
                path = Path(record["path"])
                assert path.is_file(), (artifact_name, phase, path)
                source = path.read_text(encoding="utf-8")
                assert record["required_text"] in source, (
                    artifact_name,
                    phase,
                    record,
                )


def test_paper_artifact_subpath_schema_covers_known_families():
    schema = paper_artifact_subpath_schema()
    manifest_schema = run_artifact_schema()
    inventory = generated_run_artifact_inventory()

    assert manifest_schema["paper_artifact_subpaths"] == schema
    assert schema["schema"] == "libreevolve.paper_artifact_subpaths.v1"
    assert schema["root_artifact"] == "paper_artifacts"
    assert (
        inventory["paper_artifacts"]["subpath_schema_pointer"]
        == "artifact_schema.paper_artifact_subpaths"
    )
    assert set(schema["families"]) == {
        "marker_spelling",
        "process_exhibit",
        "table1_capability_comparison",
    }
    paths = [
        record["path"]
        for family in schema["families"].values()
        for record in family["path_records"]
    ]
    assert len(paths) == len(set(paths))
    assert all(path.startswith("paper_artifacts/") for path in paths)
    assert "paper_artifacts/process_exhibit/figure_1.mmd" in paths
    assert "paper_artifacts/table1_capability_comparison/table_1.md" in paths
    assert (
        "paper_artifacts/marker_spelling/alphaevolve_page_4_text.txt"
        in paths
    )


def test_log_writes_metrics_and_evaluation():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(_p(fitness=0.5))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert "metrics" in records[0]
    assert "evaluation" in records[0]

def test_log_writes_candidate_files():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(Program(
        files={"main.py": "x=1", "helper.py": "y=2"},
        primary_file="main.py",
        fitness=0.0,
    ))
    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["primary_file"] == "main.py"
    assert records[0]["files"]["helper.py"] == "y=2"


def test_log_writes_canonical_empty_candidate_files():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(Program(fitness=0.0))

    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["primary_file"] == "main.py"
    assert records[0]["files"] == {"main.py": ""}
    assert records[0]["code"] == ""


def test_log_writes_workspace_primary_as_code_when_legacy_code_disagrees():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    db.log(Program(
        code='x = "legacy"\n',
        files={"main.py": 'x = "workspace"\n', "helper.py": "y = 2\n"},
        primary_file="main.py",
        fitness=0.0,
    ))

    records = [json.loads(l) for l in (Path(tmpdir)/"t"/"history.jsonl").read_text().splitlines()]
    assert records[0]["code"] == 'x = "workspace"\n'
    assert records[0]["files"]["main.py"] == 'x = "workspace"\n'

def test_log_failure_writes_queryable_failure_record():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = Program(
        id="parent",
        files={"main.py": "from helper import value\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
        fitness=1.0,
    )
    child = Program(
        files={"main.py": "from helper import value\n", "helper.py": "value = 0\n"},
        primary_file="main.py",
        parent_id=parent.id,
        fitness=-0.4,
        evaluation={
            "is_valid": False,
            "error": "wrong",
            "stdout": "bad",
            "metadata": {
                "validator_boundary": _validator_boundary_metadata("host")
            },
        },
    )

    record = db.log_failure(child, parent, "<<<FILE helper.py\nvalue = 0\n>>>FILE", None)

    assert record["changed_files"] == ["helper.py"]
    assert record["file_deltas"] == [{"path": "helper.py", "change": "modified"}]
    assert record["failure_fingerprint"]["schema"] == "failure_fingerprint_v1"
    assert record["failure_fingerprint"]["record_type"] == "generated"
    assert record["failure_fingerprint"]["parent_id"] == "parent"
    assert record["failure_fingerprint"]["mutation_sha256"] == record["mutation_sha256"]
    assert record["failure_fingerprint"]["changed_files"] == ["helper.py"]
    assert len(record["failure_fingerprint"]["sha256"]) == 64
    assert record["repetition_count"] == 1
    assert child.metadata["failure_record"]["program_id"] == child.id
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert records[0]["evaluation"]["stdout"] == "bad"
    assert records[0]["evaluation"]["metadata"]["validator_boundary"]["network_policy"] == "host"


@pytest.mark.parametrize(
    ("payload", "payload_type", "rendered"),
    [
        (None, "NoneType", "None"),
        (7, "int", "7"),
        (["bad"], "list", "['bad']"),
        ({"patch": "bad"}, "dict", "{'patch': 'bad'}"),
    ],
)
def test_log_failure_records_non_text_mutation_payload_schema(payload, payload_type, rendered):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    child = _p(fitness=-0.4)
    child.evaluation = {"is_valid": False, "error": "mutation rejected"}

    record = db.log_failure(child, parent, payload, "non_text_mutation_payload")

    assert record["mutation_text"] == rendered
    assert record["mutation_payload_type"] == payload_type
    assert record["mutation_payload_text"] is False
    assert record["diff_error"] == "non_text_mutation_payload"
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert records[0]["mutation_payload_type"] == payload_type
    assert records[0]["mutation_payload_text"] is False


def test_log_failure_redacts_persisted_snippets_and_evaluator_summaries():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    child = _p(fitness=-0.4)
    child.evaluation = {
        "is_valid": False,
        "error": "api_key=sk-proj_failure_error_secret_1234567890",  # pragma: allowlist secret
        "stdout": "token=ghp_abcdefghijklmnopqrstuvwxyz123456",
        "stderr": "Authorization: Bearer hf_abcdefghijklmnopqrstuvwxyz",
        "stages": [
            {
                "name": "validate",
                "passed": False,
                "score": 0.0,
                "error": "password=sk-proj_stage_error_secret_1234567890",  # pragma: allowlist secret
            }
        ],
        "metadata": {
            "llm_feedback": [
                {
                    "name": "reviewer",
                    "score": 0.1,
                    "normalized_score": 0.1,
                    "discard": True,
                    "error": "llm_feedback_discard",
                    "feedback": "reject api_key=sk-proj_feedback_failure_secret_1234567890",  # pragma: allowlist secret
                    "raw_response": '{"score": 0.1, "feedback": "reject"}',
                    "feedback_retention": {
                        "retention_mode": "redacted",
                        "sha256": "a" * 64,
                        "chars": 57,
                        "stored_chars": 17,
                    },
                    "llm_call": {
                        "call_id": "call-1",
                        "role": "feedback:reviewer",
                        "backend_idx": 0,
                        "provider_attempts": 1,
                        "total_tokens": 12,
                        "latency_sec": 0.5,
                    },
                }
            ]
        },
    }
    mutation = "mutate token sk-proj-mutationsecret1234567890\nprint(1)"  # pragma: allowlist secret

    record = db.log_failure(child, parent, mutation, "diff token=ghp_diffsecret1234567890")  # pragma: allowlist secret

    persisted = json.loads(
        (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()[0]
    )
    serialized = json.dumps(persisted, sort_keys=True)
    assert "sk-proj_failure_error_secret_1234567890" not in serialized
    assert "ghp_abcdefghijklmnopqrstuvwxyz123456" not in serialized
    assert "hf_abcdefghijklmnopqrstuvwxyz" not in serialized
    assert "sk-proj_stage_error_secret_1234567890" not in serialized
    assert "sk-proj_feedback_failure_secret_1234567890" not in serialized
    assert "sk-proj-mutationsecret1234567890" not in serialized
    assert "ghp_diffsecret1234567890" not in serialized
    assert serialized.count("[REDACTED]") >= 5
    feedback = persisted["evaluation"]["llm_feedback"][0]
    assert feedback["name"] == "reviewer"
    assert feedback["score"] == 0.1
    assert feedback["normalized_score"] == 0.1
    assert feedback["discard"] is True
    assert feedback["feedback"] == "reject api_key=[REDACTED]"
    assert feedback["raw_response"] == '{"score": 0.1, "feedback": "reject"}'
    assert feedback["retention"]["feedback_retention"]["sha256"] == "a" * 64
    assert feedback["llm_call"]["role"] == "feedback:reviewer"
    assert feedback["llm_call"]["total_tokens"] == 12
    assert persisted["mutation_sha256"]
    assert record == persisted
    assert child.metadata["failure_record"] == persisted
    prompt = PromptSampler().build(
        parent,
        [],
        _problem(),
        extra_context="",
        recent_failures=[persisted],
    )
    assert "sk-proj-mutationsecret1234567890" not in prompt
    assert "ghp_abcdefghijklmnopqrstuvwxyz123456" not in prompt
    assert "sk-proj_feedback_failure_secret_1234567890" not in prompt
    assert "llm_feedback=" in prompt
    assert 'name="reviewer"' in prompt
    assert "[REDACTED]" in prompt


def test_log_failure_writes_archive_admission_when_available():
    db = _db()
    parent = _p(fitness=1.0)
    child = Program(
        files={"main.py": "x=2\n"},
        primary_file="main.py",
        parent_id=parent.id,
        fitness=-0.1,
        evaluation={"is_valid": True},
    )
    admission = db.admit(child, threshold=0.0)

    record = db.log_failure(child, parent, "bad diff", None, admission)

    assert record["admission_reason"] == "below_threshold"
    assert record["archive_admission"]["threshold"] == 0.0
    assert child.metadata["failure_record"]["admission_reason"] == "below_threshold"


def test_log_failure_preserves_invalid_candidate_with_malformed_metrics():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(code="x=1", fitness=1.0)
    db.admit(parent)
    child = _p(code="x=2", fitness=-1.0)
    child.evaluation = {"is_valid": False, "error": "domain_invalid"}
    child.metrics = {"score": "bad"}
    admission = db.admit(child, threshold=0.0)

    record = db.log_failure(child, parent, "bad diff", "domain_invalid", admission)

    assert admission["reason"] == "invalid_evaluation"
    assert record["admission_reason"] == "invalid_evaluation"
    assert record["archive_admission"]["reason"] == "invalid_evaluation"
    assert child.metadata["failure_record"]["admission_reason"] == "invalid_evaluation"
    persisted = json.loads(
        (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()[0]
    )
    assert persisted["archive_admission"]["reason"] == "invalid_evaluation"


def test_log_failure_counts_repetitions():
    db = _db()
    parent = _p(fitness=1.0)
    first_child = Program(id="failed-1", code="x=1", fitness=-0.4)
    second_child = Program(id="failed-2", code="x=1", fitness=-0.4)
    first = db.log_failure(first_child, parent, "bad diff", "no_diff_blocks")
    second = db.log_failure(second_child, parent, "bad diff", "no_diff_blocks")
    assert first["repetition_count"] == 1
    assert second["repetition_count"] == 2


def test_failure_index_snapshot_groups_repeated_failure_fingerprints():
    db = _db()
    parent = Program(
        id="parent",
        files={"main.py": "from helper import value\n", "helper.py": "value = 1\n"},
        primary_file="main.py",
        fitness=1.0,
    )
    first_child = Program(
        id="failed-1",
        files={"main.py": "from helper import value\n", "helper.py": "value = 0\n"},
        primary_file="main.py",
        parent_id=parent.id,
        generation=1,
        fitness=-0.4,
        evaluation={
            "is_valid": False,
            "error": "wrong answer",
            "stdout": "bad output",
            "stages": [{"error": "stage failed"}],
        },
    )
    second_child = Program(
        id="failed-2",
        files={"main.py": "from helper import value\n", "helper.py": "value = 0\n"},
        primary_file="main.py",
        parent_id=parent.id,
        generation=2,
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "wrong answer"},
    )
    first = db.log_failure(first_child, parent, "bad diff", "no_diff_blocks")
    second = db.log_failure(second_child, parent, "bad diff", "no_diff_blocks")

    snapshot = db.failure_index_snapshot()

    assert snapshot["schema"] == "libreevolve.failure_index.v1"
    assert snapshot["policy"] == "failure_records_grouped_by_fingerprint_repetition_and_recency"
    assert snapshot["failure_record_count"] == 2
    assert snapshot["fingerprint_count"] == 1
    assert snapshot["retained_fingerprint_count"] == 1
    [fingerprint] = snapshot["fingerprints"]
    assert fingerprint["fingerprint_sha256"] == first["failure_fingerprint"]["sha256"]
    assert fingerprint["fingerprint_sha256"] == second["failure_fingerprint"]["sha256"]
    assert fingerprint["occurrence_count"] == 2
    assert fingerprint["max_repetition_count"] == 2
    assert fingerprint["changed_files"] == ["helper.py"]
    assert fingerprint["latest_record"]["program_id"] == second_child.id
    assert fingerprint["latest_record"]["repetition_count"] == 2
    assert fingerprint["records"][1]["program_id"] == first_child.id
    assert fingerprint["records"][1]["evaluation"]["stage_errors"] == [
        "stage failed"
    ]
    assert snapshot["limitations"] == [
        "runtime_manifest_failure_index_not_cross_run_database_table",
        "groups_by_failure_fingerprint_without_semantic_similarity",
        "retains_bounded_records_per_fingerprint",
        "rebuilt_from_current_runtime_failure_records",
    ]


def test_log_records_recent_hypothesis_context():
    db = _db()
    program = _p()
    program.id = "child-hypothesis"
    program.generation = 1
    program.metadata = {
        "proposal": {
            "idea": "Add a tile cache.",
            "rationale": "Reduce duplicate matrix products.",
            "hypothesis": "Tile cache improves matrix rank search.",
        },
        "archive_admission": {
            "admitted": True,
            "reason": None,
        },
    }

    db.log(program)

    assert db.retrieval_hypothesis_context == [
        {
            "schema": "libreevolve.retrieval_hypothesis_context.v1",
            "program_id": "child-hypothesis",
            "generation": 1,
            "archive_admitted": True,
            "admission_reason": None,
            "idea": "Add a tile cache.",
            "rationale": "Reduce duplicate matrix products.",
            "hypothesis": "Tile cache improves matrix rank search.",
        }
    ]


def test_log_failure_quarantines_duplicate_failed_program_ids():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    first_child = Program(id="dupchild", code="x=2", fitness=-0.4)
    second_child = Program(id="dupchild", code="x=3", fitness=-0.5)

    db.log_failure(first_child, parent, "bad diff", "no_diff_blocks")
    with pytest.raises(StrictJsonlError, match="duplicate failed program id 'dupchild'"):
        db.log_failure(second_child, parent, "other diff", "different")

    run_dir = Path(tmpdir) / "t"
    assert len((run_dir / "failure_history.jsonl").read_text().splitlines()) == 1
    quarantine = (run_dir / "failure_history_invalid.jsonl").read_text()
    assert "duplicate failed program id 'dupchild'" in quarantine


def test_log_failure_repetition_key_uses_full_mutation_fingerprint():
    db = _db()
    parent = _p(fitness=1.0)
    child_a = _p(code="x=2", fitness=-0.4)
    child_a.parent_id = parent.id
    child_a.evaluation = {"is_valid": False, "error": "same"}
    child_b = _p(code="x=2", fitness=-0.4)
    child_b.parent_id = parent.id
    child_b.evaluation = {"is_valid": False, "error": "same"}
    mutation_a = "x" * 500 + "a"
    mutation_b = "x" * 500 + "b"

    first = db.log_failure(child_a, parent, mutation_a, "no_diff_blocks")
    second = db.log_failure(child_b, parent, mutation_b, "no_diff_blocks")

    assert first["mutation_text"] != second["mutation_text"]
    assert first["mutation_sha256"] != second["mutation_sha256"]
    assert first["failure_fingerprint"]["sha256"] != second["failure_fingerprint"]["sha256"]
    assert first["repetition_count"] == 1
    assert second["repetition_count"] == 1


def test_log_failure_repetition_key_separates_parent_error_and_changed_files():
    db = _db()
    parent_a = Program(id="parent-a", code="x=1", fitness=1.0)
    parent_b = Program(id="parent-b", code="x=1", fitness=1.0)
    base_child = Program(
        id="child-base",
        code="x=2",
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "same"},
    )

    first = db.log_failure(base_child, parent_a, "bad diff", "no_diff_blocks")
    parent_child = Program(
        id="child-parent",
        code="x=2",
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "same"},
    )
    parent_changed = db.log_failure(parent_child, parent_b, "bad diff", "no_diff_blocks")
    error_changed = Program(
        id="child-error",
        code="x=2",
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "different"},
    )
    error_record = db.log_failure(error_changed, parent_a, "bad diff", "no_diff_blocks")
    files_changed = Program(
        id="child-files",
        files={"main.py": "x=2", "helper.py": "value = 1"},
        primary_file="main.py",
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "same"},
    )
    files_record = db.log_failure(files_changed, parent_a, "bad diff", "no_diff_blocks")

    assert first["repetition_count"] == 1
    assert parent_changed["repetition_count"] == 1
    assert error_record["repetition_count"] == 1
    assert files_record["repetition_count"] == 1
    fingerprints = {
        first["failure_fingerprint"]["sha256"],
        parent_changed["failure_fingerprint"]["sha256"],
        error_record["failure_fingerprint"]["sha256"],
        files_record["failure_fingerprint"]["sha256"],
    }
    assert len(fingerprints) == 4


def test_log_seed_failure_writes_queryable_seed_record():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    helper_code = "value = 12345\n"
    seed = Program(
        files={"main.py": "from helper import value\n", "helper.py": helper_code},
        primary_file="main.py",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "bad seed", "stdout": "nope"},
    )
    admission = db.admit(seed, threshold=0.0)

    record = db.log_seed_failure(seed, admission)

    assert record["record_type"] == "seed"
    assert record["parent_id"] is None
    assert record["admission_reason"] == "invalid_evaluation"
    assert record["changed_files"] == ["helper.py", "main.py"]
    assert record["file_deltas"] == [
        {"path": "helper.py", "change": "seed"},
        {"path": "main.py", "change": "seed"},
    ]
    assert record["failure_fingerprint"]["schema"] == "failure_fingerprint_v1"
    assert record["failure_fingerprint"]["record_type"] == "seed"
    assert record["failure_fingerprint"]["parent_id"] is None
    assert record["failure_fingerprint"]["mutation_sha256"] == record["mutation_sha256"]
    assert record["failure_fingerprint"]["changed_files"] == ["helper.py", "main.py"]
    assert len(record["failure_fingerprint"]["sha256"]) == 64
    assert record["mutation_text"].startswith("[initial seed workspace]")
    assert "--- helper.py (support) ---" in record["mutation_text"]
    assert helper_code.strip() in record["mutation_text"]
    assert record["seed_workspace"]["primary_file"] == "main.py"
    assert record["seed_workspace"]["file_count"] == 2
    assert record["seed_workspace"]["files"] == [
        {
            "path": "helper.py",
            "role": "support",
            "bytes": len(helper_code.encode("utf-8")),
            "sha256": hashlib.sha256(helper_code.encode("utf-8")).hexdigest(),
            "snippet": helper_code,
            "snippet_truncated": False,
        },
        {
            "path": "main.py",
            "role": "primary",
            "bytes": len("from helper import value\n".encode("utf-8")),
            "sha256": hashlib.sha256(
                "from helper import value\n".encode("utf-8")
            ).hexdigest(),
            "snippet": "from helper import value\n",
            "snippet_truncated": False,
        },
    ]
    assert seed.metadata["failure_record"]["record_type"] == "seed"
    records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()
    ]
    assert records[0]["evaluation"]["stdout"] == "nope"
    assert records[0]["seed_workspace"] == record["seed_workspace"]


def test_log_seed_failure_quarantines_duplicate_failed_program_ids():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    first = Program(
        id="seed-dup",
        code="x=1",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "bad seed"},
    )
    second = Program(
        id="seed-dup",
        code="x=2",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "different seed"},
    )
    first_admission = db.admit(first, threshold=0.0)
    second_admission = db.admit(second, threshold=0.0)

    db.log_seed_failure(first, first_admission)
    with pytest.raises(StrictJsonlError, match="duplicate failed program id 'seed-dup'"):
        db.log_seed_failure(second, second_admission)

    run_dir = Path(tmpdir) / "t"
    assert len((run_dir / "failure_history.jsonl").read_text().splitlines()) == 1
    quarantine = (run_dir / "failure_history_invalid.jsonl").read_text()
    assert "duplicate failed program id 'seed-dup'" in quarantine


def test_log_seed_failure_preserves_invalid_seed_with_malformed_metrics():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    seed = _p(fitness=-1.0)
    seed.evaluation = {"is_valid": False, "error": "domain_invalid"}
    seed.metrics = {"score": "bad"}
    admission = db.admit(seed, threshold=0.0)

    record = db.log_seed_failure(seed, admission)

    assert admission["reason"] == "invalid_evaluation"
    assert record["admission_reason"] == "invalid_evaluation"
    assert seed.metadata["failure_record"]["admission_reason"] == "invalid_evaluation"


def test_log_seed_failure_redacts_seed_code_and_evaluator_summaries():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    seed = Program(
        files={
            "main.py": 'OPENAI_API_KEY="sk-proj_seed_code_secret_1234567890"\n',  # pragma: allowlist secret
            "helper.py": 'token="ghp_seed_helper_secret_1234567890"\n',
        },
        primary_file="main.py",
        fitness=-1.0,
        evaluation={
            "is_valid": False,
            "error": "secret=sk-proj_seed_error_secret_1234567890",  # pragma: allowlist secret
            "stdout": "token=ghp_seedstdoutsecret1234567890",
            "stderr": "api_key=sk-proj_seed_stderr_secret_1234567890",  # pragma: allowlist secret
            "stages": [
                {
                    "name": "validate",
                    "passed": False,
                    "score": 0.0,
                    "error": "token=ghp_seedstagesecret1234567890",
                }
            ],
        },
    )
    admission = db.admit(seed, threshold=0.0)

    record = db.log_seed_failure(seed, admission)

    persisted = json.loads(
        (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()[0]
    )
    serialized = json.dumps(persisted, sort_keys=True)
    assert "sk-proj_seed_code_secret_1234567890" not in serialized
    assert "sk-proj_seed_error_secret_1234567890" not in serialized
    assert "ghp_seedstdoutsecret1234567890" not in serialized
    assert "sk-proj_seed_stderr_secret_1234567890" not in serialized
    assert "ghp_seedstagesecret1234567890" not in serialized
    assert "ghp_seed_helper_secret_1234567890" not in serialized
    assert persisted["seed_workspace"]["files"][0]["snippet"] == 'token="[REDACTED]"\n'
    assert serialized.count("[REDACTED]") >= 6
    assert persisted["mutation_sha256"]
    assert record == persisted
    assert seed.metadata["failure_record"] == persisted


def test_log_rejects_non_finite_records_with_quarantine():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    p = _p(fitness=1.0)
    p.fitness = math.inf
    with pytest.raises(StrictJsonlError):
        db.log(p)
    assert db.all_programs() == []
    assert not (Path(tmpdir)/"t"/"history.jsonl").exists()
    quarantine = Path(tmpdir)/"t"/"history_invalid.jsonl"
    record = json.loads(quarantine.read_text().splitlines()[0])
    assert "inf" in record["message"]


@pytest.mark.parametrize("fitness", [True, False, "1.0"])
def test_log_rejects_invalid_fitness_types_with_quarantine(fitness):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    p = _p(fitness=1.0)
    p.fitness = fitness

    with pytest.raises(StrictJsonlError, match="fitness must be a finite"):
        db.log(p)

    assert db.all_programs() == []
    assert not (Path(tmpdir)/"t"/"history.jsonl").exists()
    quarantine = Path(tmpdir)/"t"/"history_invalid.jsonl"
    record = json.loads(quarantine.read_text().splitlines()[0])
    assert "fitness must be a finite" in record["message"]


def test_log_failure_uses_failure_history_quarantine():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    child = _p(fitness=1.0)
    child.fitness = math.inf
    with pytest.raises(StrictJsonlError):
        db.log_failure(child, parent, "bad diff", "no_diff_blocks")
    run_dir = Path(tmpdir) / "t"
    assert not (run_dir / "failure_history.jsonl").exists()
    assert not (run_dir / "history_invalid.jsonl").exists()
    quarantine = run_dir / "failure_history_invalid.jsonl"
    record = json.loads(quarantine.read_text().splitlines()[0])
    assert "inf" in record["message"]
    assert "failure_record" not in child.metadata
    assert db._failure_counts == {}


def test_log_failure_normalizes_rejected_non_finite_score_with_admission():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    db.admit(parent)
    child = _p(code="x=2", fitness=1.0)
    child.fitness = math.inf
    child.metrics = {"score": math.inf}
    child.evaluation = {"is_valid": False, "error": "domain_invalid"}
    admission = db.admit(child, threshold=0.0)

    record = db.log_failure(child, parent, "bad diff", "domain_invalid", admission)

    run_dir = Path(tmpdir) / "t"
    assert admission["reason"] == "invalid_evaluation"
    assert admission["selection_score"] is None
    assert record["score"] is None
    assert record["score_diagnostic"] == {
        "reason": "non_finite_or_invalid_number",
        "value_type": "float",
        "value_repr": "inf",
    }
    assert record["evaluation"]["fitness"] is None
    assert record["evaluation"]["fitness_diagnostic"] == {
        "reason": "non_finite_or_invalid_number",
        "value_type": "float",
        "value_repr": "inf",
    }
    assert record["archive_admission"]["reason"] == "invalid_evaluation"
    persisted = json.loads((run_dir / "failure_history.jsonl").read_text())
    assert persisted == record
    assert not (run_dir / "failure_history_invalid.jsonl").exists()


def test_log_failure_failed_append_does_not_advance_repetition_count():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    child = _p(fitness=-0.4)

    with pytest.raises(StrictJsonlError):
        db.log_failure(child, parent, "bad diff", {"bad": {1, 2}})

    assert "failure_record" not in child.metadata
    assert db._failure_counts == {}

    record = db.log_failure(child, parent, "bad diff", "no_diff_blocks")

    assert record["repetition_count"] == 1
    assert child.metadata["failure_record"]["repetition_count"] == 1


@pytest.mark.parametrize("stages", [{"name": "bad"}, "bad", 1])
def test_log_failure_tolerates_malformed_evaluation_stages(stages):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    parent = _p(fitness=1.0)
    child = Program(
        code="x=1",
        fitness=-0.4,
        evaluation={"is_valid": False, "error": "bad", "stages": stages},
    )

    record = db.log_failure(child, parent, "bad diff", "no_diff_blocks")

    assert record["evaluation"]["stages"] == []
    assert record["evaluation"]["stages_diagnostic"]["reason"] == "malformed_stages"
    assert record["evaluation"]["stages_diagnostic"]["actual_type"] == type(stages).__name__
    persisted = json.loads(
        (Path(tmpdir) / "t" / "failure_history.jsonl").read_text().splitlines()[0]
    )
    assert persisted["evaluation"]["stages_diagnostic"]["reason"] == "malformed_stages"


def test_log_failure_skips_malformed_stage_entries_with_diagnostic():
    db = _db()
    parent = _p(fitness=1.0)
    child = Program(
        code="x=1",
        fitness=-0.4,
        evaluation={
            "is_valid": False,
            "stages": [
                {"name": "syntax", "passed": False, "score": -0.2, "error": "bad"},
                "bad-stage",
            ],
        },
    )

    record = db.log_failure(child, parent, "bad diff", "no_diff_blocks")

    assert record["evaluation"]["stages"] == [
        {"name": "syntax", "passed": False, "score": -0.2, "error": "bad"}
    ]
    assert record["evaluation"]["stages_diagnostic"] == {
        "reason": "malformed_stage_entries",
        "skipped_count": 1,
    }


def test_log_seed_failure_failed_append_does_not_mutate_metadata_or_counts():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    seed = Program(
        files={"main.py": "x=1\n"},
        primary_file="main.py",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "bad seed"},
    )
    bad_admission = {"reason": "invalid_evaluation", "bad": {1, 2}}

    with pytest.raises(StrictJsonlError):
        db.log_seed_failure(seed, bad_admission)

    assert "failure_record" not in seed.metadata
    assert db._failure_counts == {}

    record = db.log_seed_failure(seed, {"reason": "invalid_evaluation"})

    assert record["repetition_count"] == 1
    assert seed.metadata["failure_record"]["repetition_count"] == 1


@pytest.mark.parametrize("evaluation", [[], {"bad": object()}])
def test_log_seed_failure_revalidates_mutated_program_evaluation_before_side_effects(evaluation):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    seed = Program(
        files={"main.py": "x=1\n"},
        primary_file="main.py",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "bad seed"},
    )
    seed.evaluation = evaluation

    with pytest.raises(ValueError, match="Program evaluation"):
        db.log_seed_failure(seed, {"reason": "invalid_evaluation"})

    assert "failure_record" not in seed.metadata
    assert db._failure_counts == {}
    assert not (Path(tmpdir) / "t" / "failure_history.jsonl").exists()


def test_log_seed_failure_tolerates_malformed_evaluation_stages():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))
    seed = Program(
        files={"main.py": "x=1\n"},
        primary_file="main.py",
        fitness=-1.0,
        evaluation={"is_valid": False, "error": "bad seed", "stages": {"name": "bad"}},
    )

    record = db.log_seed_failure(seed, {"reason": "invalid_evaluation"})

    assert record["evaluation"]["stages"] == []
    assert record["evaluation"]["stages_diagnostic"] == {
        "reason": "malformed_stages",
        "expected": "list",
        "actual_type": "dict",
    }


def test_manifest_written():
    tmpdir = tempfile.mkdtemp()
    stdin_secret = "sk-proj_manifest_stdin_secret_1234567890"  # pragma: allowlist secret
    ProgramDatabase(Config(
        log_dir=tmpdir,
        problem_name="t",
        mutation_mode="full",
        max_evaluations=12,
        max_evaluator_seconds=4.5,
        max_evaluator_subprocess_attempts=99,
        max_evaluator_stage_samples=44,
        max_evaluator_retry_attempts=11,
        max_evaluator_timeouts=7,
        max_evaluator_sample_budget_exhaustions=5,
        max_evaluator_stage_budget_exhaustions=3,
        max_runtime_seconds=30.0,
        run_id="run-123",
        validator_env_allowlist=[" benchmark_data_dir ", "BENCHMARK_DATA_DIR"],
        evaluator_artifact_include=["*.json"],
        evaluator_artifact_exclude=["secret/*"],
        evaluator_artifact_max_files=3,
        evaluator_artifact_max_bytes=1234,
        evaluator_artifact_redact_secrets=False,
        evaluator_stdin_text=stdin_secret,
        max_candidate_workspace_files=7,
        max_candidate_file_chars=123,
        max_candidate_total_chars=456,
        max_candidate_static_file_bytes=321,
        max_candidate_total_static_bytes=654,
        eval_stages=[
            {
                "name": "stdin_stage",
                "stdin_file": "private/stage-input.txt",
            }
        ],
        map_elites_complexity_max_chars=789,
        map_elites_descriptor_axes=[
            "performance",
            "metric:score",
            "candidate_metadata:archive.score",
        ],
        llm_max_call_attempts=9,
        llm_max_response_chars=12345,
        llm_call_history_max=77,
    ))
    manifest = json.loads((Path(tmpdir)/"t"/"manifest.json").read_text())
    assert manifest["config"]["mutation_mode"] == "full"
    assert manifest["config"]["max_evaluations"] == 12
    assert manifest["config"]["max_evaluator_seconds"] == 4.5
    assert manifest["config"]["max_evaluator_subprocess_attempts"] == 99
    assert manifest["config"]["max_evaluator_stage_samples"] == 44
    assert manifest["config"]["max_evaluator_retry_attempts"] == 11
    assert manifest["config"]["max_evaluator_timeouts"] == 7
    assert manifest["config"]["max_evaluator_sample_budget_exhaustions"] == 5
    assert manifest["config"]["max_evaluator_stage_budget_exhaustions"] == 3
    assert manifest["config"]["max_runtime_seconds"] == 30.0
    assert manifest["config"]["parent_selection_strategy"] == "mixed"
    assert manifest["config"]["inspiration_strategy"] == "mixed"
    assert manifest["config"]["run_id"] == "run-123"
    assert manifest["config"]["run_collision_policy"] == "fail"
    assert manifest["config"]["validator_env_allowlist"] == ["BENCHMARK_DATA_DIR"]
    assert manifest["config"]["validator_network_policy"] == "host"
    assert manifest["config"]["evaluator_artifact_include"] == ["*.json"]
    assert manifest["config"]["evaluator_artifact_exclude"] == ["secret/*"]
    assert manifest["config"]["evaluator_artifact_max_files"] == 3
    assert manifest["config"]["evaluator_artifact_max_bytes"] == 1234
    assert manifest["config"]["evaluator_artifact_redact_secrets"] is False
    assert manifest["config"]["evaluator_stdin"] == {
        "policy": "configured_text",
        "encoding": "utf-8",
        "chars": len(stdin_secret),
        "bytes": len(stdin_secret.encode("utf-8")),
        "sha256": hashlib.sha256(stdin_secret.encode("utf-8")).hexdigest(),
        "redacted": True,
        "text_retained": False,
        "max_chars": 100_000,
    }
    assert manifest["config"]["max_candidate_workspace_files"] == 7
    assert manifest["config"]["max_candidate_file_chars"] == 123
    assert manifest["config"]["max_candidate_total_chars"] == 456
    assert manifest["config"]["max_candidate_static_file_bytes"] == 321
    assert manifest["config"]["max_candidate_total_static_bytes"] == 654
    assert manifest["config"]["eval_stages"] == [
        {
            "name": "stdin_stage",
            "stdin": {
                "policy": "configured_file",
                "source": "problem_local_file",
                "configured_path_sha256": hashlib.sha256(
                    b"private/stage-input.txt"
                ).hexdigest(),
                "path_retained": False,
                "text_retained": False,
                "max_chars": 100_000,
            },
        }
    ]
    manifest_text = json.dumps(manifest)
    assert stdin_secret not in manifest_text
    assert '"stdin_text":' not in manifest_text
    assert '"stdin_file":' not in manifest_text
    assert "private/stage-input.txt" not in manifest_text
    assert manifest["config"]["map_elites_complexity_max_chars"] == 789
    assert manifest["config"]["map_elites_descriptor_axes"] == [
        "performance",
        "metric:score",
        "candidate_metadata:archive.score",
    ]
    assert manifest["config"]["llm_max_retries"] == 0
    assert manifest["config"]["llm_max_call_attempts"] == 9
    assert manifest["config"]["llm_fallback"] is True
    assert manifest["config"]["llm_max_response_chars"] == 12345
    assert manifest["config"]["llm_call_history_max"] == 77
    assert manifest["config"]["llm_prompt_roles"] == {}
    assert manifest["config"]["llm_prompt_roles_metadata"] == {}
    assert manifest["config"]["capture_proposal_metadata"] is False
    assert manifest["config"]["log_dir"] == "<absolute-log-dir>"
    assert manifest["config"]["log_dir_metadata"]["is_absolute"] is True
    assert manifest["config"]["log_dir_metadata"]["redacted"] is True
    assert len(manifest["config"]["log_dir_metadata"]["sha256"]) == 64
    assert manifest["policies"]["redaction"]["schema"] == "libreevolve.redaction.v2"
    assert manifest["policies"]["redaction"]["engine"] == "ordered_regex_substitution"
    assert [rule["id"] for rule in manifest["policies"]["redaction"]["rules"]] == [
        "private_key_block",
        "secret_assignment",
        "authorization_bearer",
        "url_basic_auth_password",
        "provider_token_prefix",
        "aws_access_key_id",
    ]
    assert manifest["policies"]["seed_post_processing"] == {
        "policy": "raw_evaluator_baseline",
        "llm_feedback": "not_applied",
        "plugin_score_composition": "not_applied",
        "reason": (
            "Initial seeds are evaluated before mutation LLMs, feedback graders, "
            "and plugin score-composition hooks."
        ),
    }
    assert manifest["policies"]["validator_stdin"] == {
        "policy": "fixture_only_validator_stdin_v1",
        "default": {
            "policy": "devnull",
            "stdin": "subprocess.DEVNULL",
            "interactive_input": "unsupported",
            "generated_input": "unsupported",
        },
        "configured_text": {
            "supported": True,
            "encoding": "utf-8",
            "max_chars": 100_000,
            "raw_text_persisted": False,
            "metadata": [
                "policy",
                "encoding",
                "chars",
                "bytes",
                "sha256",
                "redacted",
                "text_retained",
                "max_chars",
            ],
        },
        "configured_file": {
            "supported": True,
            "scope": "problem_local_file",
            "encoding": "utf-8",
            "max_chars": 100_000,
            "raw_path_in_manifest_config": False,
            "raw_text_persisted": False,
            "metadata": [
                "policy",
                "source",
                "path",
                "path_hash",
                "file_bytes",
                "file_sha256",
                "sha256",
                "text_retained",
                "max_chars",
            ],
        },
        "generated_input": {
            "supported": False,
            "policy": "unsupported_until_replayable_source_artifacts_exist",
        },
        "interactive_input": {
            "supported": False,
            "policy": "unsupported_non_interactive_validator_subprocesses",
        },
        "stage_overrides": "configured_stage_stdin_replaces_top_level_fixture",
        "stage_config_persistence": "stdin_text_and_stdin_file_replaced_by_hash_only_metadata",
    }
    assert manifest["policies"]["validator_execution"] == {
        "schema": "libreevolve.validator_execution_policy.v1",
        "policy": "local_subprocess_boundary_v1",
        "execution": "temporary_local_subprocess",
        "security_sandbox": "unsupported",
        "container": "unsupported",
        "filesystem_capability_model": (
            "candidate_root_plus_declared_problem_files"
        ),
        "filesystem_scope": {
            "cwd": "materialized_candidate_root",
            "candidate_files": "materialized_under_temporary_candidate_root",
            "problem_local_files": (
                "declared_entrypoint_companion_and_data_provenance_only"
            ),
            "host_filesystem_sandbox": "unsupported",
        },
        "filesystem_capabilities": {
            "schema": "libreevolve.validator_filesystem_capabilities.v1",
            "policy": "candidate_root_plus_declared_problem_files",
            "enforcement": "python_runner_problem_local_provenance_checks",
            "cwd": {
                "path": "materialized_candidate_root",
                "read": True,
                "write": True,
                "execute": True,
                "lifetime": "temporary_per_attempt",
            },
            "candidate_workspace": {
                "scope": "materialized_candidate_files",
                "read": True,
                "write": True,
                "execute": True,
                "host_filesystem_sandbox": "unsupported",
            },
            "declared_problem_files": {
                "scope": "entrypoint_companion_data_and_stdin_provenance",
                "read": True,
                "write": False,
                "execute": True,
                "undeclared_problem_local_reads": (
                    "python_open_and_import_checks_denied"
                ),
            },
            "evaluator_artifacts": {
                "write": "bounded_include_globs",
                "copy_out": "hashed_redacted_optional",
                "symlink_policy": "link_metadata_not_unbounded_follow",
            },
            "host_filesystem": {
                "os_sandbox": "unsupported",
                "ambient_access_possible": True,
                "undeclared_host_paths": "not_capability_enforced",
            },
        },
        "network_policy": "host",
        "network_egress": "host_inherited_not_sandboxed",
        "network_denial": "unsupported",
        "network_denial_scope": "python_socket_api_only_not_kernel_or_container",
        "resource_limits": {
            "wall_clock_timeout": "configured_stage_or_sample_timeout",
            "cpu": "unsupported",
            "memory": "unsupported",
            "gpu": "unsupported",
            "disk": "unsupported",
            "process_count": "unsupported",
        },
        "resource_limit_policy": {
            "schema": "libreevolve.validator_resource_limit_policy.v1",
            "policy": "wall_clock_timeout_only",
            "enforcement": "local_subprocess_timeout_cleanup",
            "wall_clock_timeout": {
                "supported": True,
                "source": "configured_stage_or_sample_timeout",
                "cleanup": "process_group_or_windows_job_object_plus_tree_kill",
            },
            "cpu": {"supported": False, "quota": "unsupported"},
            "memory": {"supported": False, "quota": "unsupported"},
            "gpu": {"supported": False, "quota": "unsupported"},
            "disk": {"supported": False, "quota": "unsupported"},
            "process_count": {"supported": False, "quota": "unsupported"},
            "container_runtime_limits": "unsupported",
            "remaining_gap": (
                "CPU/memory/GPU/disk/process quotas require an external sandbox "
                "or worker runtime"
            ),
        },
        "secret_boundary": "minimal_environment_allowlist_with_redacted_diagnostics",
        "startup_manifest_only": True,
        "per_evaluation_metadata": "evaluation.metadata.validator_boundary",
        "boundary_consistency_validator": (
            "validate_validator_boundary_consistency.v1"
        ),
        "boundary_consistency_fields": [
            "policy",
            "execution",
            "security_sandbox",
            "container",
            "filesystem_capability_model",
            "filesystem_capabilities",
            "network_policy",
            "network_egress",
            "network_denial",
            "network_denial_scope",
            "resource_limits",
            "resource_limit_policy",
            "secret_boundary",
        ],
        "remaining_gap": (
            "configurable sandbox/container enforcement, OS filesystem "
            "capabilities, CPU/memory/GPU/disk/process quotas, and distributed "
            "worker state"
        ),
    }
    assert manifest["policies"]["validator_network"] == {
        "schema": "libreevolve.validator_network_policy.v1",
        "configured_policy": "host",
        "allowed_policies": ["host", "deny"],
        "network_egress": "host_inherited_not_sandboxed",
        "network_denial": "unsupported",
        "network_denial_scope": "python_socket_api_only_not_kernel_or_container",
        "applies_to": [
            "validator_preflight_subprocess",
            "validator_evaluation_subprocess",
        ],
        "os_container_network_sandbox": "unsupported",
        "native_extension_or_child_process_denial": "unsupported",
        "provider_secret_boundary": (
            "validator_env_allowlist_controls_environment_values; "
            "diagnostics_and_artifacts_use_redaction_policy"
        ),
        "remaining_gap": (
            "OS/container-grade validator network egress isolation and "
            "network-mediated secret-boundary audit"
        ),
    }
    candidate_language = manifest["policies"]["candidate_language"]
    assert candidate_language == {
        "schema": "libreevolve.candidate_language_policy.v1",
        "policy": "python_primary_text_workspace_v1",
        "candidate_representation": (
            "bounded_utf8_text_workspace_with_typed_static_members"
        ),
        "primary_language": "python",
        "primary_file_policy": "python_primary_file_required_for_seed_and_best_py",
        "text_member_policy": {
            "python_files": "evolve_block_markers_supported",
            "non_python_text_files": "allowed_as_unmarked_workspace_members",
            "non_python_marker_like_declarations": "rejected_fail_closed",
        },
        "static_member_policy": {
            "encoded_static_binary": "bounded_base64_metadata",
            "verified_source_copy_static_asset": "copy_only_after_hash_and_size_check",
            "raw_binary_workspace_records": "normalized_to_static_members",
        },
        "runner_policy": {
            "validator_runner": "python_subprocess_entrypoint",
            "validator_entrypoints": "problem_local_python_files_or_packages",
            "arbitrary_language_runners": "unsupported",
            "build_system_runners": "unsupported",
            "problem_defined_solution_abstractions": "unsupported",
        },
        "runner_declarations": {
            "declaration_status": "not_configured",
            "language_runner_declarations": [],
            "build_system_declarations": [],
            "execution_status": "unsupported",
            "declaration_scope": "manifest_metadata_only_not_executed",
        },
        "alphaevolve_divergence": (
            "LibreEvolve currently evolves bounded Python-primary workspace "
            "file sets instead of arbitrary language/codebase solution objects."
        ),
        "language_runner_ready": False,
        "remaining_gap": [
            "language_or_runner_declarations_for_non_python_candidates",
            "language_aware_evolve_block_marker_grammars",
            "problem_defined_candidate_abstraction_hooks",
            "build_system_and_arbitrary_language_runner_contracts",
        ],
    }
    candidate_language_validation = validate_candidate_language_policy(
        candidate_language
    )
    assert candidate_language_validation == {
        "schema": "libreevolve.candidate_language_policy.v1",
        "ok": True,
        "language_runner_ready": False,
        "primary_language": "python",
        "issues": [],
    }
    assert manifest["policies"]["prompt_config_retention"] == {
        "policy": "redact_and_hash_prompt_bearing_config",
        "fields": [
            "prompt_variants",
            "prompt_format_options.*.text",
            "critique_prompt",
            "llm_feedback[].prompt",
            "llm_prompt_roles.*.system",
            "llm_prompt_roles.*.developer",
        ],
        "default_max_retained_chars": 4000,
        "hash": "sha256_of_original_text",
    }
    prompt_data_retention = manifest["policies"]["prompt_data_retention"]
    assert prompt_data_retention["schema"] == "libreevolve.prompt_data_retention.v1"
    assert prompt_data_retention["policy"] == (
        "mixed_configurable_and_fixed_bounded_prompt_retention"
    )
    assert prompt_data_retention["redaction_policy"] == "libreevolve.redaction.v2"
    assert prompt_data_retention["surfaces"]["mutation_prompt"] == {
        "retention_mode": "redacted",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_original_rendered_prompt_when_policy_allows",
        "default": "redacted",
    }
    assert prompt_data_retention["surfaces"]["explicit_context_text"] == {
        "retention_mode": "redacted",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_original_rendered_context_when_policy_allows",
        "default": "redacted",
        "note": (
            "applies to explicit context spans inside persisted rendered "
            "mutation prompts"
        ),
    }
    assert prompt_data_retention["surfaces"]["critique_prompt"] == {
        "retention_mode": "redacted",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_original_prompt",
        "max_retained_chars": 6000,
    }
    assert prompt_data_retention["surfaces"]["feedback_raw_response"] == {
        "retention_mode": "redacted",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_original_response",
    }
    assert prompt_data_retention["surfaces"]["failure_memory_llm_feedback"] == {
        "retention_mode": "redacted",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_original_field_text",
        "max_retained_chars": 500,
        "note": (
            "failure_history evaluation summaries retain selected bounded "
            "LLM-grader fields for prompt-visible failure memory"
        ),
    }
    assert prompt_data_retention["surfaces"]["validator_artifact_content"] == {
        "retention_mode": "excerpt",
        "configurable": True,
        "modes": ["excerpt", "bounded_file", "off"],
        "hash": "sha256_of_stored_artifact_bytes",
        "max_read_bytes": 4096,
        "max_rendered_chars": 1000,
        "path_policy": "run_local_relative_artifact_paths_only",
        "note": (
            "bounded_file reopens copied UTF-8 evaluator artifacts under the "
            "run directory for prompt feedback rendering"
        ),
    }
    assert prompt_data_retention["surfaces"]["llm_call_prompt_text"] == {
        "retention_mode": "hash_and_char_counts_only",
        "configurable": False,
        "hash": "sha256_of_prompt",
    }
    assert prompt_data_retention["surfaces"]["llm_call_output_text"] == {
        "retention_mode": "hash_only",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_output_on_success_also_retained_as_call_telemetry",
    }
    assert prompt_data_retention["surfaces"]["provider_error_text"] == {
        "retention_mode": "redacted",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_original_error_text_when_policy_allows",
        "max_retained_chars": 500,
    }
    assert prompt_data_retention["surfaces"]["plugin_context_text"] == {
        "retention_mode": "redacted",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_original_rendered_plugin_context_when_policy_allows",
        "max_retained_chars": 4000,
        "note": (
            "mutation_prompt_retention_mode separately controls persisted rendered "
            "prompts that may include plugin context"
        ),
    }
    assert prompt_data_retention["surfaces"]["meta_prompt_evidence"] == {
        "retention_mode": "hash_only",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_original_evidence_json_when_policy_allows",
        "max_retained_chars": 1000,
        "note": (
            "provider-visible meta-prompt evidence remains redacted and bounded "
            "separately"
        ),
    }
    assert prompt_data_retention["surfaces"]["deep_research_retrieval_bodies"] == {
        "retention_mode": "plugin_option:retrieval_body_retention_mode",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_original_retrieval_body_when_policy_allows",
        "default": "redacted",
        "note": (
            "selected mode is recorded in runtime.plugin_state.loaded_specs "
            "for DeepResearchPlugin instances"
        ),
    }
    assert prompt_data_retention["surfaces"]["quarantine_record_snapshots"] == {
        "retention_mode": "redacted",
        "configurable": True,
        "modes": ["full", "redacted", "hash_only", "off"],
        "hash": "sha256_of_original_record_repr_or_fragment_when_policy_allows",
        "default": "redacted",
        "max_retained_chars": 4000,
        "note": (
            "applies to framework-owned *_invalid.jsonl record_repr snapshots "
            "and torn JSONL fragment previews"
        ),
    }
    assert prompt_data_retention["remaining_gap"] == [
        "replay retention policy for restored historical prompt-bearing artifacts"
    ]
    assert manifest["policies"]["candidate_workspace_size"] == {
        "policy": "reject_oversized_text_and_static_workspace",
        "max_files": 7,
        "max_file_chars": 123,
        "max_total_chars": 456,
        "max_static_file_bytes": 321,
        "max_total_static_bytes": 654,
        "spillover": "not_implemented",
        "summary_only_persistence": "not_used",
    }
    assert manifest["policies"]["candidate_artifacts"] == {
        "policy": "text_workspace_with_typed_static_metadata",
        "candidate_member_types": [
            "utf8_text_file",
            "typed_static_metadata",
            "encoded_static_binary",
            "verified_source_copy_static_asset",
            "raw_binary_direct_workspace_record",
        ],
        "binary_candidate_members": (
            "encoded_static_members_materialized_when_content_b64_present"
        ),
        "raw_binary_direct_workspace_records": (
            "bytes_values_normalized_to_immutable_binary_static_members"
        ),
        "source_copy_static_assets": (
            "source_copy_path_materialized_after_size_and_sha256_verification"
        ),
        "static_asset_mutation": (
            "generated_and_existing_llm_editable_static_members_via_bounded_base64"
        ),
        "seed_workspace_binary_policy": (
            "encode_bounded_non_utf8_seed_files_as_static_members_when_text_primary_exists_else_skip"
        ),
        "generated_artifact_policy": (
            "validator_outputs_collected_by_evaluator_artifacts"
        ),
        "hash_scope": "candidate_text_files_and_typed_static_metadata",
        "remaining_gap": None,
    }
    assert manifest["policies"]["archive_identity"] == {
        "program_id_policy": "run_local_unique_canonical_program_id",
        "duplicate_archive_ids": "rejected_before_island_mutation",
        "migration_policy": "canonical_id_reference",
        "migration_clone_ids": "not_created",
        "migration_duplicate_target_policy": "skip_existing_target_id",
        "resume_status": "manifest_archive_state_restore_supported",
        "restore_surfaces": [
            "round_robin_cursor",
            "archive_sequence_counters",
            "map_elites_cells",
            "elite_archives",
        ],
        "migration_event_replay": "audit_only_not_restore_engine",
    }
    assert manifest["policies"]["openai_api_mode"] == {
        "policy": "explicit_or_auto_openai_api_mode",
        "auto_policy": "responses_when_reasoning_effort_is_configured_else_chat_completions",
        "records": [],
    }
    assert manifest["policies"]["provider_capability_lookup"] == {
        "schema": "libreevolve.provider_capability_lookup_policy.v1",
        "policy": "local_static_validation_no_live_provider_lookup",
        "live_lookup": "unsupported",
        "offline_operation": "supported",
        "network_calls_before_run": "none_for_capability_discovery",
        "provider_model_registry": "not_queried",
        "provider_service_api_version": "not_queried",
        "provider_account_availability": "not_checked",
        "capability_readiness": {
            "schema": "libreevolve.provider_capability_lookup_readiness.v1",
            "live_model_registry_lookup": False,
            "provider_service_api_version_lookup": False,
            "provider_account_availability_validation": False,
            "remaining_gap": [
                "live_model_registry_lookup",
                "provider_service_api_version_lookup",
                "provider_account_availability_validation",
            ],
        },
        "record_count": 1,
        "records_sha256": (
            "b1dc311e056f6adcc09881ea7250451266eff4962210b6eb04f3f1511f17e5f9"
        ),
        "records": [
            {
                "backend_index": 0,
                "provider": "anthropic",
                "model": "claude-sonnet-4-6",
                "live_model_registry_lookup": False,
                "provider_service_api_version_lookup": False,
                "provider_account_availability_check": False,
                "offline_compatible": True,
                "local_validation": [
                    "backend_type_and_supported_key_schema",
                    "manifest_safe_model_identifier",
                    "manifest_safe_client_context_fields",
                ],
            }
        ],
        "remaining_gap": (
            "live provider model registry, service API-version, account "
            "availability, and capability evidence"
        ),
    }
    assert manifest["run_directory"] == {
        "foreign_entry_policy": "preserved_outside_run_contract",
        "foreign_entry_count": 0,
        "foreign_entries": [],
    }


def test_validate_candidate_language_policy_rejects_runner_overclaims():
    policy = {
        "schema": "libreevolve.candidate_language_policy.v1",
        "policy": "python_primary_text_workspace_v1",
        "candidate_representation": (
            "bounded_utf8_text_workspace_with_typed_static_members"
        ),
        "primary_language": "python",
        "primary_file_policy": "python_primary_file_required_for_seed_and_best_py",
        "text_member_policy": {
            "python_files": "evolve_block_markers_supported",
            "non_python_text_files": "allowed_as_unmarked_workspace_members",
            "non_python_marker_like_declarations": "rejected_fail_closed",
        },
        "static_member_policy": {
            "encoded_static_binary": "bounded_base64_metadata",
            "verified_source_copy_static_asset": "copy_only_after_hash_and_size_check",
            "raw_binary_workspace_records": "normalized_to_static_members",
        },
        "runner_policy": {
            "validator_runner": "python_subprocess_entrypoint",
            "validator_entrypoints": "problem_local_python_files_or_packages",
            "arbitrary_language_runners": "supported",
            "build_system_runners": "supported",
            "problem_defined_solution_abstractions": "supported",
        },
        "runner_declarations": {
            "declaration_status": "metadata_only_no_execution",
            "language_runner_declarations": [
                {
                    "language": "rust",
                    "candidate_role": "supporting_text_workspace_member",
                    "file_patterns": ["src/*.rs"],
                    "marker_grammar": "unsupported",
                    "runner_command": ["cargo", "test"],
                    "execution_status": "supported",
                    "notes": "",
                }
            ],
            "build_system_declarations": [],
            "execution_status": "supported",
            "declaration_scope": "manifest_metadata_only_not_executed",
        },
        "alphaevolve_divergence": "overclaimed",
        "language_runner_ready": True,
        "remaining_gap": [],
    }

    validation = validate_candidate_language_policy(policy)

    codes = {issue["code"] for issue in validation["issues"]}
    assert validation["ok"] is False
    assert validation["language_runner_ready"] is False
    assert "runner_policy_arbitrary_language_runners_mismatch" in codes
    assert "arbitrary_language_runners_overclaim" in codes
    assert "build_system_runners_overclaim" in codes
    assert "problem_defined_solution_abstractions_overclaim" in codes
    assert "runner_declaration_execution_overclaim" in codes
    assert "language_runner_declaration_execution_overclaim" in codes
    assert "language_runner_ready_overclaim" in codes
    assert "missing_remaining_gap" in codes


def test_manifest_records_candidate_language_runner_declarations():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(
            log_dir=tmpdir,
            problem_name="t",
            candidate_language_runners=[
                {
                    "language": "rust",
                    "candidate_role": "supporting_text_workspace_member",
                    "file_patterns": ["src/*.rs"],
                    "marker_grammar": "custom_declared_unsupported",
                    "runner_command": ["cargo", "test"],
                    "notes": "declared for future runner support",
                }
            ],
            candidate_build_systems=[
                {
                    "name": "cargo",
                    "build_files": ["Cargo.toml"],
                    "build_command": ["cargo", "build"],
                    "artifact_patterns": ["target/debug/*"],
                }
            ],
        )
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())

    assert manifest["config"]["candidate_language_runners"][0]["language"] == "rust"
    assert manifest["config"]["candidate_build_systems"][0]["name"] == "cargo"
    policy = manifest["policies"]["candidate_language"]
    declarations = policy["runner_declarations"]
    assert declarations["declaration_status"] == "metadata_only_no_execution"
    assert declarations["execution_status"] == "unsupported"
    assert declarations["language_runner_declarations"][0]["runner_command"] == [
        "cargo",
        "test",
    ]
    assert declarations["build_system_declarations"][0]["build_files"] == [
        "Cargo.toml"
    ]
    validation = validate_candidate_language_policy(policy)
    assert validation["ok"] is True
    assert "runner_execution_for_declared_candidate_language_or_build_system" in (
        policy["remaining_gap"]
    )


def test_manifest_records_validator_network_deny_policy():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(
            log_dir=tmpdir,
            problem_name="t",
            validator_network_policy="deny",
        )
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())

    assert manifest["config"]["validator_network_policy"] == "deny"
    assert manifest["policies"]["validator_execution"]["network_policy"] == "deny"
    assert manifest["policies"]["validator_execution"]["network_egress"] == (
        "python_socket_denied_not_os_sandbox"
    )
    assert manifest["policies"]["validator_execution"]["network_denial"] == (
        "python_socket_monkeypatch"
    )
    assert manifest["policies"]["validator_network"] == {
        "schema": "libreevolve.validator_network_policy.v1",
        "configured_policy": "deny",
        "allowed_policies": ["host", "deny"],
        "network_egress": "python_socket_denied_not_os_sandbox",
        "network_denial": "python_socket_monkeypatch",
        "network_denial_scope": "python_socket_api_only_not_kernel_or_container",
        "applies_to": [
            "validator_preflight_subprocess",
            "validator_evaluation_subprocess",
        ],
        "os_container_network_sandbox": "unsupported",
        "native_extension_or_child_process_denial": "unsupported",
        "provider_secret_boundary": (
            "validator_env_allowlist_controls_environment_values; "
            "diagnostics_and_artifacts_use_redaction_policy"
        ),
        "remaining_gap": (
            "OS/container-grade validator network egress isolation and "
            "network-mediated secret-boundary audit"
        ),
    }


def test_manifest_records_effective_openai_api_mode_policy():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(
            log_dir=tmpdir,
            problem_name="t",
            backends=[
                {"type": "openai", "model": "gpt-5.1"},
                {
                    "type": "openai",
                    "model": "gpt-5.2",
                    "reasoning_effort": "minimal",
                },
                {"type": "openai", "model": "gpt-5.1", "api_mode": "responses"},
            ],
        )
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())

    assert manifest["policies"]["openai_api_mode"] == {
        "policy": "explicit_or_auto_openai_api_mode",
        "auto_policy": "responses_when_reasoning_effort_is_configured_else_chat_completions",
        "records": [
            {
                "backend_index": 0,
                "model": "gpt-5.1",
                "configured_api_mode": "auto",
                "effective_api_mode": "chat_completions",
                "reasoning_effort_configured": False,
                "reasoning_effort": None,
                "auto_policy": (
                    "responses_when_reasoning_effort_is_configured_else_chat_completions"
                ),
            },
            {
                "backend_index": 1,
                "model": "gpt-5.2",
                "configured_api_mode": "auto",
                "effective_api_mode": "responses",
                "reasoning_effort_configured": True,
                "reasoning_effort": "minimal",
                "auto_policy": (
                    "responses_when_reasoning_effort_is_configured_else_chat_completions"
                ),
            },
            {
                "backend_index": 2,
                "model": "gpt-5.1",
                "configured_api_mode": "responses",
                "effective_api_mode": "responses",
                "reasoning_effort_configured": False,
                "reasoning_effort": None,
                "auto_policy": (
                    "responses_when_reasoning_effort_is_configured_else_chat_completions"
                ),
            },
        ],
    }
    provider_policy = manifest["policies"]["provider_capability_lookup"]
    assert provider_policy["policy"] == "local_static_validation_no_live_provider_lookup"
    assert provider_policy["provider_model_registry"] == "not_queried"
    assert provider_policy["provider_service_api_version"] == "not_queried"
    assert provider_policy["provider_account_availability"] == "not_checked"
    assert provider_policy["network_calls_before_run"] == "none_for_capability_discovery"
    assert provider_policy["capability_readiness"] == {
        "schema": "libreevolve.provider_capability_lookup_readiness.v1",
        "live_model_registry_lookup": False,
        "provider_service_api_version_lookup": False,
        "provider_account_availability_validation": False,
        "remaining_gap": [
            "live_model_registry_lookup",
            "provider_service_api_version_lookup",
            "provider_account_availability_validation",
        ],
    }
    assert provider_policy["records"] == [
        {
            "backend_index": 0,
            "provider": "openai",
            "model": "gpt-5.1",
            "live_model_registry_lookup": False,
            "provider_service_api_version_lookup": False,
            "provider_account_availability_check": False,
            "offline_compatible": True,
            "local_validation": [
                "backend_type_and_supported_key_schema",
                "manifest_safe_model_identifier",
                "manifest_safe_client_context_fields",
                "openai_api_mode_enum_and_reasoning_effort_route",
                "openai_model_family_reasoning_effort_static_compatibility",
            ],
            "api_mode_policy_ref": "policies.openai_api_mode",
        },
        {
            "backend_index": 1,
            "provider": "openai",
            "model": "gpt-5.2",
            "live_model_registry_lookup": False,
            "provider_service_api_version_lookup": False,
            "provider_account_availability_check": False,
            "offline_compatible": True,
            "local_validation": [
                "backend_type_and_supported_key_schema",
                "manifest_safe_model_identifier",
                "manifest_safe_client_context_fields",
                "openai_api_mode_enum_and_reasoning_effort_route",
                "openai_model_family_reasoning_effort_static_compatibility",
            ],
            "api_mode_policy_ref": "policies.openai_api_mode",
        },
        {
            "backend_index": 2,
            "provider": "openai",
            "model": "gpt-5.1",
            "live_model_registry_lookup": False,
            "provider_service_api_version_lookup": False,
            "provider_account_availability_check": False,
            "offline_compatible": True,
            "local_validation": [
                "backend_type_and_supported_key_schema",
                "manifest_safe_model_identifier",
                "manifest_safe_client_context_fields",
                "openai_api_mode_enum_and_reasoning_effort_route",
                "openai_model_family_reasoning_effort_static_compatibility",
            ],
            "api_mode_policy_ref": "policies.openai_api_mode",
        },
    ]


def test_database_rejects_programs_exceeding_configured_workspace_budget():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t", max_candidate_total_chars=5)
    )
    program = Program(code="x = 1\n", fitness=1.0, metrics={"score": 1.0})

    with pytest.raises(ValueError, match="max_candidate_total_chars"):
        db.admit(program)


def test_database_rejects_programs_exceeding_configured_static_workspace_budget():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t", max_candidate_static_file_bytes=3)
    )
    program = Program(
        code="x = 1\n",
        fitness=1.0,
        metrics={"score": 1.0},
        static_files=[
            {"path": "fixture.bin", "kind": "binary", "sha256": "a" * 64, "bytes": 4}
        ],
    )

    with pytest.raises(ValueError, match="max_candidate_static_file_bytes"):
        db.admit(program)


def test_secret_like_artifact_selectors_fail_before_manifest_write(tmp_path):
    with pytest.raises(ConfigError, match="manifest-safe glob patterns"):
        Config(
            log_dir=tmp_path,
            problem_name="t",
            evaluator_artifact_include=[
                "api_key=sk-proj_ARTIFACT_INCLUDE_SECRET_1234567890/*.txt"  # pragma: allowlist secret
            ],
        )

    assert not (tmp_path / "t" / "manifest.json").exists()


def test_path_unsafe_artifact_selectors_fail_before_manifest_write(tmp_path):
    with pytest.raises(ConfigError, match="path-safe glob patterns"):
        Config(
            log_dir=tmp_path,
            problem_name="t",
            evaluator_artifact_include=["../secret/*.txt"],
        )

    assert not (tmp_path / "t" / "manifest.json").exists()


def test_manifest_requires_objective_schema_before_write():
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(ValueError, match="objective_schema is required"):
        _ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


@pytest.mark.parametrize(
    ("schema", "message"),
    [
        ({}, "missing required fields"),
        (
            {
                "metrics": [
                    {
                        "name": "is_valid",
                        "direction": "sideways",
                        "primary": "yes",
                        "bounds": [1.0, 0.0],
                    }
                ],
                "primary_metric": "missing",
                "primary_bounds": [1.0, 0.0],
                "metric_count": 99,
            },
            "direction|reserved|primary_metric|primary must be boolean|bounds",
        ),
        (
            {
                "metrics": [
                    {
                        "name": "score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [0.0, 1.0],
                    }
                ],
                "primary_metric": "score",
                "primary_bounds": [1.0, 2.0],
                "metric_count": 1,
            },
            "primary_bounds must match",
        ),
        (
            {
                "metrics": [
                    {
                        "name": "score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [False, True],
                    }
                ],
                "primary_metric": "score",
                "primary_bounds": [0.0, 1.0],
                "metric_count": 1,
            },
            "bounds must be numeric",
        ),
        (
            {
                "metrics": [
                    {
                        "name": "score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [0.0, 1.0],
                    }
                ],
                "primary_metric": "score",
                "primary_bounds": [False, True],
                "metric_count": 1,
            },
            "primary_bounds must be numeric",
        ),
        (
            {
                "metrics": [
                    {
                        "name": "score",
                        "direction": "maximize",
                        "primary": True,
                        "bounds": [0.0, 1.0],
                    }
                ],
                "primary_metric": "score",
                "primary_bounds": [0.0, 1.0],
                "metric_count": 2,
            },
            "metric_count must match",
        ),
    ],
)
def test_manifest_rejects_invalid_objective_schema_before_write(schema, message):
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(ValueError, match=message):
        _ProgramDatabase(
            Config(log_dir=tmpdir, problem_name="t"),
            objective_schema=schema,
        )

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_manifest_normalizes_objective_schema_at_database_boundary():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        objective_schema={
            "metrics": [
                {
                    "name": "quality",
                    "direction": "maximize",
                    "bounds": (0, 10),
                },
                {
                    "name": "runtime_ms",
                    "direction": "minimize",
                    "primary": True,
                    "bounds": [0, 100],
                },
            ],
            "primary_metric": "runtime_ms",
            "primary_bounds": (0, 100),
            "metric_count": 2,
        },
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["problem"]["objective_schema"] == {
        "metrics": [
            {
                "name": "quality",
                "direction": "maximize",
                "bounds": [0.0, 10.0],
                "primary": False,
                "source": "evaluator",
                "weight": 1.0,
            },
            {
                "name": "runtime_ms",
                "direction": "minimize",
                "primary": True,
                "bounds": [0.0, 100.0],
                "source": "evaluator",
                "weight": 1.0,
            },
        ],
        "primary_metric": "runtime_ms",
        "primary_bounds": [0.0, 100.0],
        "metric_count": 2,
    }


def test_manifest_does_not_persist_secret_like_log_dir(tmp_path):
    secret = "sk-proj_LOGDIRSECRET_1234567890"
    log_dir = tmp_path / f"api_key={secret}" / "runs"

    ProgramDatabase(Config(log_dir=str(log_dir), problem_name="t"))

    manifest_text = (log_dir / "t" / "manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)
    assert secret not in manifest_text
    assert str(log_dir) not in manifest_text
    assert manifest["config"]["log_dir"] == "<absolute-log-dir>"
    assert manifest["config"]["log_dir_metadata"]["reason"] == "absolute_path"
    assert manifest["config"]["log_dir_metadata"]["sha256"]


def test_manifest_redacts_prompt_bearing_config_and_keeps_hash_metadata():
    tmpdir = tempfile.mkdtemp()
    secret = "api_key=sk-proj_PROMPTCONFIGSECRET_1234567890"  # pragma: allowlist secret
    ProgramDatabase(
        Config(
            log_dir=tmpdir,
            problem_name="t",
            prompt_variants=[f"Task: {{task}}\n{secret}\n[[prompt:tone]]"],
            prompt_variant_semantic_policy="compatibility",
            prompt_format_options={
                "tone": [
                    {"text": f"Use secret {secret}", "weight": 2.0},
                ]
            },
            critique_prompt=f"Critique with {secret}",
            llm_feedback=[
                {
                    "name": "review",
                    "prompt": f"Grade with {secret}",
                }
            ],
            llm_prompt_roles={
                "mutation": {
                    "system": f"System with {secret}",
                    "developer": f"Developer with {secret}",
                }
            },
        )
    )

    manifest_text = (Path(tmpdir) / "t" / "manifest.json").read_text(encoding="utf-8")
    manifest = json.loads(manifest_text)

    assert secret not in manifest_text
    assert "api_key=[REDACTED]" in manifest["config"]["prompt_variants"][0]
    assert (
        "api_key=[REDACTED]"
        in manifest["config"]["prompt_format_options"]["tone"][0]["text"]
    )
    assert "api_key=[REDACTED]" in manifest["config"]["critique_prompt"]
    assert "api_key=[REDACTED]" in manifest["config"]["llm_feedback"][0]["prompt"]
    assert (
        "api_key=[REDACTED]"
        in manifest["config"]["llm_prompt_roles"]["mutation"]["system"]
    )
    assert (
        "api_key=[REDACTED]"
        in manifest["config"]["llm_prompt_roles"]["mutation"]["developer"]
    )
    for metadata in (
        manifest["config"]["prompt_variants_metadata"][0],
        manifest["config"]["prompt_format_options_metadata"]["tone"][0],
        manifest["config"]["critique_prompt_metadata"],
        manifest["config"]["llm_feedback_metadata"][0]["prompt"],
        manifest["config"]["llm_prompt_roles_metadata"]["mutation"]["system"],
        manifest["config"]["llm_prompt_roles_metadata"]["mutation"]["developer"],
    ):
        assert metadata["retention"] == "redacted_truncated_with_hash"
        assert metadata["redacted"] is True
        assert metadata["truncated"] is False
        assert metadata["chars"] > metadata["retained_chars"]
        assert len(metadata["sha256"]) == 64


def test_manifest_keeps_safe_relative_log_dir():
    tmpdir = tempfile.mkdtemp()
    cwd = Path.cwd()
    try:
        os.chdir(tmpdir)
        ProgramDatabase(Config(log_dir="runs", problem_name="t"))
        manifest = json.loads((Path("runs") / "t" / "manifest.json").read_text())
    finally:
        os.chdir(cwd)

    assert manifest["config"]["log_dir"] == "runs"
    assert manifest["config"]["log_dir_metadata"]["redacted"] is False
    assert manifest["config"]["log_dir_metadata"]["reason"] == "as_configured"


def test_manifest_writes_context_source_provenance():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        context_sources=[{"path": "nested/notes.md", "sha256": "abc"}],
        context_policy={"selected_count": 1, "skipped": [{"path": "skip.md"}]},
        objective_schema={
            "metrics": [
                {
                    "name": "score",
                    "direction": "maximize",
                    "primary": True,
                    "bounds": [0.0, 1.0],
                }
            ],
            "primary_metric": "score",
            "primary_bounds": [0.0, 1.0],
            "metric_count": 1,
        },
        evaluator_sources=[{"relative_path": "validate.py", "sha256": "def"}],
        run_provenance={"problem": {"tree_hash": "123"}},
    )
    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["problem"]["context_sources"] == [
        {"path": "nested/notes.md", "sha256": "abc"}
    ]
    assert manifest["problem"]["context_policy"] == {
        "selected_count": 1,
        "skipped": [{"path": "skip.md"}],
    }
    assert manifest["problem"]["objective_schema"] == {
        "metrics": [
            {
                "name": "score",
                "direction": "maximize",
                "primary": True,
                "bounds": [0.0, 1.0],
                "source": "evaluator",
                "weight": 1.0,
            }
        ],
        "primary_metric": "score",
        "primary_bounds": [0.0, 1.0],
        "metric_count": 1,
    }
    assert manifest["problem"]["evaluator_sources"] == [
        {"relative_path": "validate.py", "sha256": "def"}
    ]
    assert manifest["provenance"] == {"problem": {"tree_hash": "123"}}


def test_manifest_writes_valid_seed_source_provenance():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        seed_sources=[
            {
                "seed_index": 0,
                "seed_source_kind": "file",
                "seed_source_path": "initial_programs/seed.py",
                "primary_file": "seed.py",
                "file_count": 1,
                "files": ["seed.py"],
            }
        ],
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["problem"]["seed_sources"] == [
        {
            "seed_index": 0,
            "seed_source_kind": "file",
            "seed_source_path": "initial_programs/seed.py",
            "primary_file": "seed.py",
            "file_count": 1,
            "files": ["seed.py"],
        }
    ]
    assert manifest["problem"]["seed_skipped"] == []


def test_manifest_writes_seed_idea_provenance_metadata():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        seed_sources=[
            {
                "seed_index": 0,
                "seed_source_kind": "file",
                "seed_source_path": "initial_programs/seed.py",
                "primary_file": "seed.py",
                "file_count": 1,
                "files": ["seed.py"],
                "seed_variant_id": "matrix.seed:v1",
                "seed_idea_origin": "researcher_idea",
                "seed_idea_label": "stochastic evaluation seed",
                "seed_idea_summary": "Adds stochastic scoring before evolution.",
                "seed_contribution_roles": [
                    "human_seed_author",
                    "researcher_idea",
                ],
                "seed_prior_technique": "stochastic candidate evaluation",
                "seed_background_refs": ["context/matrix_notes.md"],
            }
        ],
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    source = manifest["problem"]["seed_sources"][0]
    assert source["seed_variant_id"] == "matrix.seed:v1"
    assert source["seed_idea_origin"] == "researcher_idea"
    assert source["seed_idea_label"] == "stochastic evaluation seed"
    assert source["seed_contribution_roles"] == [
        "human_seed_author",
        "researcher_idea",
    ]
    assert source["seed_background_refs"] == ["context/matrix_notes.md"]


def test_manifest_writes_seed_policy_and_reserved_seed_source_allowlist():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        seed_policy={
            "policy": "skip_reserved_seed_paths_by_default",
            "reserved_components": ["dot-prefixed", "__pycache__"],
            "source": "seed_policy.yaml",
            "include": [".seed.py"],
            "exclude": [],
            "exclude_precedence": True,
        },
        seed_sources=[
            {
                "seed_index": 0,
                "seed_source_kind": "file",
                "seed_source_path": "initial_programs/.seed.py",
                "primary_file": ".seed.py",
                "file_count": 1,
                "files": [".seed.py"],
                "allowed_reserved_paths": [".seed.py"],
            }
        ],
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["problem"]["seed_policy"]["source"] == "seed_policy.yaml"
    assert manifest["problem"]["seed_sources"] == [
        {
            "seed_index": 0,
            "seed_source_kind": "file",
            "seed_source_path": "initial_programs/.seed.py",
            "primary_file": ".seed.py",
            "file_count": 1,
            "files": [".seed.py"],
            "allowed_reserved_paths": [".seed.py"],
        }
    ]


def test_manifest_writes_seed_skipped_diagnostics():
    tmpdir = tempfile.mkdtemp()
    ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        seed_skipped=[
            {
                "seed_source_path": "initial_programs/.secret.py",
                "reason": "top_level_hidden_seed_entry",
                "entry_type": "file",
            }
        ],
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["problem"]["seed_skipped"] == [
        {
            "seed_source_path": "initial_programs/.secret.py",
            "reason": "top_level_hidden_seed_entry",
            "entry_type": "file",
        }
    ]


def test_manifest_redacts_secret_like_seed_skipped_path():
    tmpdir = tempfile.mkdtemp()
    token = "sk-proj_seedskippedpathsecret1234567890"  # pragma: allowlist secret
    ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        seed_skipped=[
            {
                "seed_source_path": f"initial_programs/api_key={token}.py",
                "reason": "unsupported_top_level_seed_file",
                "entry_type": "file",
            }
        ],
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    rendered = json.dumps(manifest["problem"]["seed_skipped"], sort_keys=True)
    assert token not in rendered
    assert "[REDACTED]" in rendered


@pytest.mark.parametrize(
    ("seed_sources", "message"),
    [
        (["bad-source-record"], "seed_sources\\[0\\] must be a mapping"),
        ([{1: "bad"}], "seed_sources\\[0\\] keys must be strings"),
        ([{"unknown": "bad"}], "seed_sources\\[0\\] has unsupported fields"),
        ([{"seed_index": 1}], "seed_sources\\[0\\]\\.seed_index must match"),
        ([{"seed_source_kind": "direct"}], "seed_sources\\[0\\]\\.seed_source_kind"),
        (
            [{"seed_source_kind": "file"}],
            "seed_sources\\[0\\]\\.seed_source_path is required",
        ),
        (
            [{"seed_source_kind": "workspace", "files": ["main.py"], "file_count": 2}],
            "seed_sources\\[0\\]\\.file_count must match files length",
        ),
        (
            [{"seed_source_kind": "workspace", "primary_file": "missing.py", "files": ["main.py"]}],
            "seed_sources\\[0\\]\\.primary_file must be present",
        ),
        (
            [{"seed_source_kind": "workspace", "files": ["main.py", "main.py"]}],
            "seed_sources\\[0\\]\\.files must not contain duplicates",
        ),
        (
            [{"seed_source_kind": "workspace", "allowed_reserved_paths": ["main.py"]}],
            "seed_sources\\[0\\]\\.allowed_reserved_paths\\[0\\] must name a reserved path",
        ),
        (
            [{"seed_source_kind": "workspace", "primary_file": ".seed.py", "files": [".seed.py"]}],
            "seed_sources\\[0\\]\\.primary_file must be a safe path label",
        ),
        (
            [{"seed_idea_origin": "invented"}],
            "seed_sources\\[0\\]\\.seed_idea_origin",
        ),
        (
            [{"seed_variant_id": "bad token"}],
            "seed_sources\\[0\\]\\.seed_variant_id",
        ),
        (
            [{"seed_contribution_roles": ["unsupported_role"]}],
            "seed_sources\\[0\\]\\.seed_contribution_roles\\[0\\]",
        ),
        (
            [{"seed_background_refs": "context.md"}],
            "seed_sources\\[0\\]\\.seed_background_refs must be a list",
        ),
    ],
)
def test_manifest_rejects_malformed_seed_source_provenance(seed_sources, message):
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(StrictJsonlError, match=message):
        ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"), seed_sources=seed_sources)

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_manifest_rejects_secret_like_seed_source_path_without_leak():
    tmpdir = tempfile.mkdtemp()
    token = "sk-proj_seedsourcepathsecret1234567890"  # pragma: allowlist secret

    with pytest.raises(StrictJsonlError, match="seed_sources\\[0\\]\\.seed_source_path") as excinfo:
        ProgramDatabase(
            Config(log_dir=tmpdir, problem_name="t"),
            seed_sources=[
                {
                    "seed_source_kind": "file",
                    "seed_source_path": f"initial_programs/api_key={token}.py",
                }
            ],
        )

    assert token not in str(excinfo.value)
    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_manifest_redacts_secret_like_context_provenance():
    tmpdir = tempfile.mkdtemp()
    source_secret = "sk-proj_context_source_secret_1234567890"  # pragma: allowlist secret
    policy_secret = "sk-proj_context_policy_secret_1234567890"  # pragma: allowlist secret

    ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        context_sources=[{"path": f"api_key={source_secret}.md", "sha256": "abc"}],
        context_policy={
            "selected_count": 1,
            "skipped": [{"path": f"token={policy_secret}.md"}],
        },
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    rendered = json.dumps(manifest["problem"], sort_keys=True)
    assert source_secret not in rendered
    assert policy_secret not in rendered
    assert manifest["problem"]["context_sources"][0]["path"] == "api_key=[REDACTED]"
    assert manifest["problem"]["context_policy"]["skipped"][0]["path"] == "token=[REDACTED]"


def test_manifest_rejects_non_json_context_policy_before_manifest_write():
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(
        StrictJsonlError,
        match=r"context_policy\.skipped\[0\]\.reason must be JSON-safe context provenance",
    ):
        ProgramDatabase(
            Config(log_dir=tmpdir, problem_name="t"),
            context_policy={"present": True, "skipped": [{"reason": {"bad"}}]},
        )

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_manifest_rejects_malformed_context_sources_schema():
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(StrictJsonlError, match="context_sources must be a list of mappings"):
        ProgramDatabase(
            Config(log_dir=tmpdir, problem_name="t"),
            context_sources=[{"path": "ok.md"}, "not-a-source"],
        )

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_manifest_rejects_oversized_context_policy_payload():
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(StrictJsonlError, match="context_policy JSON exceeds"):
        ProgramDatabase(
            Config(log_dir=tmpdir, problem_name="t"),
            context_policy={"items": ["x" * 1000] * 250},
        )

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_retrieval_query_context_preserves_local_paper_metadata():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(
        Config(log_dir=tmpdir, problem_name="t"),
        retrieval_query_context={
            "task_description": "Use MAP-Elites for archive coverage.",
            "context_files": {"notes.md": "Prefer local paper grounding."},
            "local_papers": [
                {
                    "id": "1504.04909",
                    "title": "MAP_Elites",
                    "url": "https://arxiv.org/pdf/1504.04909.pdf",
                    "file": "papers/1504.04909__MAP_Elites.pdf",
                    "sha256": "0" * 64,
                    "ok": True,
                    "bytes": 123,
                }
            ],
        },
    )

    assert db.retrieval_query_context["local_papers"] == [
        {
            "id": "1504.04909",
            "title": "MAP_Elites",
            "url": "https://arxiv.org/pdf/1504.04909.pdf",
            "file": "papers/1504.04909__MAP_Elites.pdf",
            "sha256": "0" * 64,
            "ok": True,
            "bytes": 123,
        }
    ]


def test_retrieval_query_context_rejects_malformed_local_paper_metadata():
    tmpdir = tempfile.mkdtemp()

    with pytest.raises(
        StrictJsonlError,
        match=r"retrieval_query_context\.local_papers\[0\]\.bytes",
    ):
        ProgramDatabase(
            Config(log_dir=tmpdir, problem_name="t"),
            retrieval_query_context={
                "local_papers": [
                    {
                        "id": "1504.04909",
                        "title": "MAP_Elites",
                        "bytes": -1,
                    }
                ],
            },
        )

    assert not (Path(tmpdir) / "t" / "manifest.json").exists()


def test_manifest_runtime_can_be_updated():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))

    db.update_manifest_runtime(
        {
            "stop_reason": "max_evaluations",
            "consumed": {"evaluations": 1},
        }
    )

    manifest = json.loads((Path(tmpdir) / "t" / "manifest.json").read_text())
    assert manifest["runtime"]["stop_reason"] == "max_evaluations"
    assert manifest["runtime"]["consumed"]["evaluations"] == 1


def test_manifest_runtime_update_preserves_previous_manifest_on_invalid_payload():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t", run_id="run-123"))
    manifest_path = Path(tmpdir) / "t" / "manifest.json"
    original = manifest_path.read_text(encoding="utf-8")

    with pytest.raises(StrictJsonlError, match="Could not serialize strict JSON"):
        db.update_manifest_runtime({"stop_reason": "bad", "payload": object()})

    assert manifest_path.read_text(encoding="utf-8") == original
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["config"]["run_id"] == "run-123"
    diagnostic = json.loads((Path(tmpdir) / "t" / "manifest_invalid.jsonl").read_text().splitlines()[0])
    assert diagnostic["record_type"] == "dict"
    assert "runtime_update" in diagnostic["record_repr"]


def test_manifest_runtime_update_preserves_previous_manifest_on_non_finite_payload():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t", run_id="run-123"))
    manifest_path = Path(tmpdir) / "t" / "manifest.json"
    original = manifest_path.read_text(encoding="utf-8")

    with pytest.raises(StrictJsonlError, match=r"non-finite values: \$.runtime.elapsed"):
        db.update_manifest_runtime({"stop_reason": "bad", "elapsed": math.nan})

    assert manifest_path.read_text(encoding="utf-8") == original
    assert json.loads(manifest_path.read_text(encoding="utf-8"))["config"]["run_id"] == "run-123"
    diagnostic = json.loads((Path(tmpdir) / "t" / "manifest_invalid.jsonl").read_text().splitlines()[0])
    assert "non-finite values: $.runtime.elapsed" in diagnostic["message"]


@pytest.mark.parametrize(
    ("corrupt_bytes", "expected_error"),
    [
        (b'{"config": ', "JSONDecodeError"),
        (b"", "JSONDecodeError"),
        (b"\xff\xfe\x00", "UnicodeDecodeError"),
    ],
)
def test_manifest_runtime_update_recovers_from_unreadable_current_manifest(
    corrupt_bytes,
    expected_error,
):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t", run_id="run-123"))
    manifest_path = Path(tmpdir) / "t" / "manifest.json"
    manifest_path.write_bytes(corrupt_bytes)

    db.update_manifest_runtime({"status": "completed", "stop_reason": "max_generations"})

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["config"]["run_id"] == "run-123"
    assert manifest["runtime"] == {"status": "completed", "stop_reason": "max_generations"}
    diagnostic = json.loads(
        (Path(tmpdir) / "t" / "manifest_invalid.jsonl").read_text().splitlines()[0]
    )
    assert diagnostic["error"] == expected_error
    assert "runtime_update_current_manifest_unreadable" in diagnostic["record_repr"]
    assert "startup_manifest" in diagnostic["record_repr"]


@pytest.mark.parametrize(
    "manifest_text",
    [
        '{"config": {"run_id": "first"}, "config": {"run_id": "second"}}',
        '{"config": {"run_id": "run-123", "run_id": "shadowed"}}',
    ],
)
def test_manifest_runtime_update_rejects_duplicate_json_names_without_rewrite(manifest_text):
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t", run_id="run-123"))
    manifest_path = Path(tmpdir) / "t" / "manifest.json"
    manifest_path.write_text(manifest_text, encoding="utf-8")

    with pytest.raises(StrictJsonlError, match="ambiguous manifest\\.json"):
        db.update_manifest_runtime({"status": "completed"})

    assert manifest_path.read_text(encoding="utf-8") == manifest_text
    diagnostic = json.loads(
        (Path(tmpdir) / "t" / "manifest_invalid.jsonl").read_text().splitlines()[0]
    )
    assert diagnostic["error"] == "_DuplicateManifestJsonNameError"
    assert "duplicate object name" in diagnostic["message"]
    assert "runtime_update_current_manifest_ambiguous" in diagnostic["record_repr"]
    assert "startup_manifest" not in diagnostic["record_repr"]


def test_manifest_runtime_recovery_still_quarantines_invalid_replacement_runtime():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(Config(log_dir=tmpdir, problem_name="t", run_id="run-123"))
    manifest_path = Path(tmpdir) / "t" / "manifest.json"
    manifest_path.write_text('{"config": ', encoding="utf-8")

    with pytest.raises(StrictJsonlError, match="Could not serialize strict JSON"):
        db.update_manifest_runtime({"status": "completed", "bad": object()})

    assert manifest_path.read_text(encoding="utf-8") == '{"config": '
    diagnostics = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "manifest_invalid.jsonl")
        .read_text()
        .splitlines()
    ]
    assert diagnostics[0]["error"] == "JSONDecodeError"
    assert "runtime_update_current_manifest_unreadable" in diagnostics[0]["record_repr"]
    assert diagnostics[1]["error"] == "StrictJsonlError"
    assert "runtime_update" in diagnostics[1]["record_repr"]


def test_startup_manifest_payload_validates_before_overwrite_cleanup():
    tmpdir = tempfile.mkdtemp()
    run_dir = Path(tmpdir) / "t"
    run_dir.mkdir()
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")

    with pytest.raises(StrictJsonlError, match="Could not serialize strict JSON"):
        ProgramDatabase(
            Config(log_dir=tmpdir, problem_name="t", run_collision_policy="overwrite"),
            run_provenance={"bad": object()},
        )

    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == "{}\n"
    assert not (run_dir / "manifest.json").exists()


def test_startup_manifest_rejects_non_finite_payload_before_overwrite_cleanup():
    tmpdir = tempfile.mkdtemp()
    run_dir = Path(tmpdir) / "t"
    run_dir.mkdir()
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")

    with pytest.raises(StrictJsonlError, match=r"context_policy\.bad must be finite"):
        ProgramDatabase(
            Config(log_dir=tmpdir, problem_name="t", run_collision_policy="overwrite"),
            context_policy={"bad": math.nan},
        )

    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == "{}\n"
    assert not (run_dir / "manifest.json").exists()


def test_database_fails_when_run_artifacts_already_exist():
    tmpdir = tempfile.mkdtemp()
    run_dir = Path(tmpdir) / "t"
    run_dir.mkdir()
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")

    with pytest.raises(FileExistsError, match="already contains run artifacts"):
        ProgramDatabase(Config(log_dir=tmpdir, problem_name="t"))


def test_database_existing_artifact_error_uses_safe_run_path_context(tmp_path):
    log_root = tmp_path / "api_key=sk-proj_rundir_secret_1234567890"  # pragma: allowlist secret
    run_dir = log_root / "t"
    run_dir.mkdir(parents=True)
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")

    with pytest.raises(FileExistsError) as excinfo:
        ProgramDatabase(Config(log_dir=str(log_root), problem_name="t"))

    message = str(excinfo.value)
    assert "already contains run artifacts" in message
    assert "history.jsonl" in message
    assert "run_dir=<absolute>/t" in message
    assert "path_hash=" in message
    assert "path_redacted=True" in message
    assert "sk-proj_rundir_secret" not in message
    assert str(log_root) not in message


def test_run_directory_path_must_resolve_under_log_root(tmp_path):
    log_root = tmp_path / "runs"
    outside = tmp_path / "outside"

    validate_run_directory_path(log_root, log_root / "safe")

    with pytest.raises(ValueError, match="resolves outside log_dir"):
        validate_run_directory_path(log_root, outside / "run")


def test_run_directory_containment_error_uses_safe_path_context(tmp_path):
    log_root = tmp_path / "runs"
    outside = tmp_path / "api_key=sk-proj_rundir_secret_1234567890"  # pragma: allowlist secret
    outside.mkdir()

    with pytest.raises(ValueError) as excinfo:
        validate_run_directory_path(log_root, outside / "run")

    message = str(excinfo.value)
    assert "Run directory resolves outside log_dir" in message
    assert "run_dir=<absolute>/run" in message
    assert "resolved_run=<absolute>/run" in message
    assert "log_dir=<absolute>/runs" in message
    assert "path_hash=" in message
    assert "path_redacted=True" in message
    assert str(outside) not in message
    assert "sk-proj_rundir_secret" not in message


def test_database_rejects_linked_run_directory_escape_before_overwrite(tmp_path):
    log_root = tmp_path / "runs"
    outside = tmp_path / "outside"
    log_root.mkdir()
    outside.mkdir()
    (outside / "history.jsonl").write_text("{}\n", encoding="utf-8")
    linked_run = log_root / "linked"
    try:
        linked_run.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink creation is unavailable: {exc}")

    with pytest.raises(ValueError, match="resolves outside log_dir"):
        ProgramDatabase(
            Config(
                log_dir=str(log_root),
                problem_name="linked",
                run_collision_policy="overwrite",
            )
        )

    assert (outside / "history.jsonl").read_text(encoding="utf-8") == "{}\n"


def test_database_rejects_windows_junction_run_directory_escape_before_overwrite(tmp_path):
    if sys.platform != "win32":
        pytest.skip("Windows junction test")

    log_root = tmp_path / "runs"
    outside = tmp_path / "outside"
    log_root.mkdir()
    outside.mkdir()
    (outside / "history.jsonl").write_text("{}\n", encoding="utf-8")
    linked_run = log_root / "linked"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(linked_run), str(outside)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation is unavailable: {result.stderr or result.stdout}")

    with pytest.raises(ValueError, match="resolves outside log_dir"):
        ProgramDatabase(
            Config(
                log_dir=str(log_root),
                problem_name="linked",
                run_collision_policy="overwrite",
            )
        )

    assert (outside / "history.jsonl").read_text(encoding="utf-8") == "{}\n"


def test_database_overwrite_clears_known_run_artifacts_only():
    tmpdir = tempfile.mkdtemp()
    run_dir = Path(tmpdir) / "t"
    run_dir.mkdir()
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")
    (run_dir / "prompt_history.jsonl").write_text("{}\n", encoding="utf-8")
    (run_dir / "prompt_current_binding_table.jsonl").write_text("{}\n", encoding="utf-8")
    (run_dir / "prompt_prior_score_table.jsonl").write_text("{}\n", encoding="utf-8")
    (run_dir / "manifest_invalid.jsonl").write_text("{}\n", encoding="utf-8")
    (run_dir / "best_workspace").mkdir()
    (run_dir / "best_workspace" / "old.py").write_text("old", encoding="utf-8")
    (run_dir / "evaluator_artifacts").mkdir()
    (run_dir / "evaluator_artifacts" / "old.txt").write_text("old", encoding="utf-8")
    (run_dir / "plugin_artifacts").mkdir()
    (run_dir / "plugin_artifacts" / "old.jsonl").write_text("old", encoding="utf-8")
    (run_dir / "paper_artifacts").mkdir()
    (run_dir / "paper_artifacts" / "old.txt").write_text("old", encoding="utf-8")
    (run_dir / "notes.txt").write_text("keep", encoding="utf-8")

    ProgramDatabase(Config(
        log_dir=tmpdir,
        problem_name="t",
        run_collision_policy="overwrite",
    ))

    assert not (run_dir / "history.jsonl").exists()
    assert not (run_dir / "prompt_history.jsonl").exists()
    assert not (run_dir / "prompt_current_binding_table.jsonl").exists()
    assert not (run_dir / "prompt_prior_score_table.jsonl").exists()
    assert not (run_dir / "manifest_invalid.jsonl").exists()
    assert not (run_dir / "best_workspace").exists()
    assert not (run_dir / "evaluator_artifacts").exists()
    assert not (run_dir / "plugin_artifacts").exists()
    assert not (run_dir / "paper_artifacts").exists()
    assert (run_dir / "manifest.json").exists()
    assert (run_dir / "notes.txt").read_text(encoding="utf-8") == "keep"
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_directory"]["foreign_entry_policy"] == "preserved_outside_run_contract"
    assert manifest["run_directory"]["foreign_entry_count"] == 1
    assert manifest["run_directory"]["foreign_entries"][0]["type"] == "file"
    assert "notes.txt" not in json.dumps(manifest["run_directory"])


def test_database_records_foreign_run_directory_entries_without_raw_names(tmp_path):
    run_dir = tmp_path / "t"
    run_dir.mkdir()
    (run_dir / "foreign.txt").write_text("keep", encoding="utf-8")
    (run_dir / "foreign_dir").mkdir()

    ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_directory"]["foreign_entry_policy"] == "preserved_outside_run_contract"
    assert manifest["run_directory"]["foreign_entry_count"] == 2
    assert sorted(entry["type"] for entry in manifest["run_directory"]["foreign_entries"]) == [
        "directory",
        "file",
    ]
    assert "foreign.txt" not in json.dumps(manifest["run_directory"])
    assert (run_dir / "foreign.txt").read_text(encoding="utf-8") == "keep"


def test_database_records_unreadable_foreign_run_directory_listing(tmp_path, monkeypatch):
    run_dir = tmp_path / "t"
    run_dir.mkdir()
    real_iterdir = Path.iterdir

    def fake_iterdir(path):
        if path == run_dir:
            raise PermissionError("cannot list api_key=sk-proj_foreignlistsecret1234567890")
        return real_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)

    ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))

    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["run_directory"]["foreign_entry_count"] == 1
    [entry] = manifest["run_directory"]["foreign_entries"]
    assert entry["status"] == "unreadable"
    assert entry["type"] == "unknown"
    assert entry["policy"] == "preserved_unlisted"
    assert entry["error_type"] == "PermissionError"
    assert "[REDACTED]" in entry["error"]
    assert "sk-proj_foreignlistsecret1234567890" not in json.dumps(manifest)


def test_database_overwrite_preserves_unreadable_foreign_listing_diagnostic(tmp_path, monkeypatch):
    run_dir = tmp_path / "t"
    run_dir.mkdir()
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")
    real_iterdir = Path.iterdir

    def fake_iterdir(path):
        if path == run_dir:
            raise PermissionError("cannot list api_key=sk-proj_foreignlistsecret1234567890")
        return real_iterdir(path)

    monkeypatch.setattr(Path, "iterdir", fake_iterdir)

    ProgramDatabase(
        Config(
            log_dir=str(tmp_path),
            problem_name="t",
            run_collision_policy="overwrite",
        )
    )

    assert not (run_dir / "history.jsonl").exists()
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    [entry] = manifest["run_directory"]["foreign_entries"]
    assert entry["status"] == "unreadable"
    assert entry["policy"] == "preserved_unlisted"


def test_database_rejects_linked_known_artifact_before_partial_overwrite(tmp_path):
    log_root = tmp_path / "runs"
    run_dir = log_root / "t"
    outside = tmp_path / "outside"
    run_dir.mkdir(parents=True)
    outside.mkdir()
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")
    (outside / "old.py").write_text("outside", encoding="utf-8")
    linked_artifact = run_dir / "best_workspace"
    try:
        linked_artifact.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink creation is unavailable: {exc}")

    with pytest.raises(ValueError, match="linked run artifacts"):
        ProgramDatabase(
            Config(
                log_dir=str(log_root),
                problem_name="t",
                run_collision_policy="overwrite",
            )
        )

    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == "{}\n"
    assert linked_artifact.is_symlink()
    assert (outside / "old.py").read_text(encoding="utf-8") == "outside"


def test_database_linked_artifact_error_uses_safe_run_path_context(tmp_path):
    log_root = tmp_path / "api_key=sk-proj_rundir_secret_1234567890"  # pragma: allowlist secret
    run_dir = log_root / "t"
    outside = tmp_path / "outside"
    run_dir.mkdir(parents=True)
    outside.mkdir()
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")
    linked_artifact = run_dir / "best_workspace"
    try:
        linked_artifact.symlink_to(outside, target_is_directory=True)
    except OSError as exc:
        pytest.skip(f"directory symlink creation is unavailable: {exc}")

    with pytest.raises(ValueError) as excinfo:
        ProgramDatabase(
            Config(
                log_dir=str(log_root),
                problem_name="t",
                run_collision_policy="overwrite",
            )
        )

    message = str(excinfo.value)
    assert "linked run artifacts" in message
    assert "best_workspace" in message
    assert "run_dir=<absolute>/t" in message
    assert "path_hash=" in message
    assert "sk-proj_rundir_secret" not in message
    assert str(log_root) not in message
    assert linked_artifact.is_symlink()


def _accepted_history_row(program_id: str, fitness: float = 1.0, **extra) -> dict:
    row = {
        "id": program_id,
        "code": "x=1\n",
        "fitness": fitness,
        "generation": 0,
        "metrics": {"score": fitness},
        "evaluation": {"is_valid": True},
    }
    row.update(extra)
    return row


def _write_accepted_history(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def _archive_state_snapshot() -> dict:
    return {
        "schema": "libreevolve.island_state.v1",
        "resume_status": "snapshot_persisted_cursor_restore_available_full_archive_restore_not_implemented",
        "cursor_policy": "advance_only_on_search_state_changed",
        "n_islands": 2,
        "next_island_id": 1,
        "archive_sequence": 3,
        "migration_sequence": 1,
        "metric_sample_index": 2,
        "frontier_sample_index": 4,
        "archive_sequence_by_program_id": {"p1": 1, "p2": 3},
        "islands": [
            {
                "island_id": 0,
                "occupied_cell_count": 1,
                "elite_count": 2,
                "pareto_frontier_count": 0,
                "metric_cell_archive_count": 0,
            },
            {
                "island_id": 1,
                "occupied_cell_count": 0,
                "elite_count": 0,
                "pareto_frontier_count": 0,
                "metric_cell_archive_count": 0,
            },
        ],
    }


def _archive_state_snapshot_with_contents(
    *,
    island0_cells: list[dict] | None = None,
    island1_cells: list[dict] | None = None,
) -> dict:
    snapshot = _archive_state_snapshot()
    snapshot["resume_status"] = "snapshot_persisted_cursor_and_full_archive_restore_supported"
    snapshot["archive_contents"] = {
        "schema": "libreevolve.island_archive_contents.v1",
        "restore_status": "snapshot_persisted_full_archive_restore_supported",
        "islands": [
            {"island_id": 0, "archive": _map_elites_snapshot(island0_cells or [])},
            {"island_id": 1, "archive": _map_elites_snapshot(island1_cells or [])},
        ],
    }
    return snapshot


def _map_elites_snapshot(cells: list[dict]) -> dict:
    return {
        "schema": "libreevolve.map_elites_state.v1",
        "bins": 10,
        "elite_archive_size": 50,
        "perf_bounds": [0.0, 1.0],
        "complexity_max_chars": 100000,
        "descriptor_axes": ["performance", "complexity", "diversity"],
        "cells": cells,
        "elite_program_ids": [cell["program_id"] for cell in cells],
        "descriptor_policy": {
            "schema": "libreevolve.map_elites_descriptor_policy.v1",
            "axes": ["performance", "complexity", "diversity"],
            "performance": "selection_score_normalized_by_fixed_perf_bounds",
            "complexity": "workspace_descriptor_chars_clamped_to_configured_bound",
            "diversity": "tfidf_char_ngram_distance_to_current_elite_archive",
            "metric": "normalized_metrics_axis_else_raw_metric_clamped_to_unit_interval",
            "evaluation_metadata": "numeric_evaluation_metadata_path_clamped_to_unit_interval",
            "candidate_metadata": "numeric_candidate_metadata_path_clamped_to_unit_interval",
            "diversity_reference_program_ids": [],
            "diversity_update_policy": "reference_updates_after_search_state_change",
            "rebin_policy": "no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots",
        },
        "descriptor_model": {
            "schema": "libreevolve.map_elites_descriptor_model.v1",
            "revision": 0,
            "revision_policy": "increments_on_search_state_change",
            "axes": ["performance", "complexity", "diversity"],
            "performance_bounds": [0.0, 1.0],
            "complexity_max_chars": 100000,
            "diversity_reference_program_ids": [],
            "dynamic_diversity_reference": True,
            "rebin_policy": "no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots",
        },
    }


def _archive_event_row(program_id: str = "p1", **extra) -> dict:
    row = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "record_schema": ARCHIVE_EVENT_RECORD_SCHEMA,
        "event_type": "migration",
        "migration_sequence": 1,
        "program_id": program_id,
        "canonical_program_id": program_id,
        "source_island": 0,
        "target_island": 1,
        "identity_policy": "canonical_id_reference",
        "clone_id": None,
        "admitted": True,
        "reason": "empty_cell",
        "cell": [0, 1, 2],
        "selection_score": 0.5,
        "objective_vector": {
            "policy": "normalized_declared_metric_vector_v1",
            "normalized_metrics": {"score": 0.5},
            "selection_policy": {
                "type": "mean_normalized_declared_metrics",
                "metrics": ["score"],
            },
        },
    }
    row.update(extra)
    return row


def _archive_admission_event_row(program_id: str = "p1", **extra) -> dict:
    row = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "record_schema": ARCHIVE_EVENT_RECORD_SCHEMA,
        "event_type": "admission",
        "admission_sequence": 1,
        "program_id": program_id,
        "canonical_program_id": program_id,
        "archive_sequence": 1,
        "island_id": 0,
        "admitted": True,
        "reason": "empty_cell",
        "cell": [0, 1, 2],
        "selection_score": 0.5,
        "threshold": 0.0,
        "evaluation_is_valid": True,
        "cell_admitted": True,
        "elite_retained": True,
        "sampling_eligible": True,
        "search_state_changed": True,
        "descriptors": {"performance": 0.5},
        "previous_occupant_id": None,
        "objective_vector": {
            "policy": "normalized_declared_metric_vector_v1",
            "normalized_metrics": {"score": 0.5},
            "selection_policy": {
                "type": "mean_normalized_declared_metrics",
                "metrics": ["score"],
            },
        },
    }
    row.update(extra)
    return row


def _write_archive_events(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def _failure_history_row(program_id: str = "p1", **extra) -> dict:
    mutation_text = extra.pop("mutation_text", "bad mutation")
    mutation_sha256 = extra.pop(
        "mutation_sha256",
        hashlib.sha256(mutation_text.encode("utf-8")).hexdigest(),
    )
    parent_id = extra.pop("parent_id", "parent")
    changed_files = extra.pop("changed_files", ["main.py"])
    payload_text = extra.pop("mutation_payload_text", True)
    payload_type = extra.pop("mutation_payload_type", "str")
    row = {
        "schema_version": ARTIFACT_SCHEMA_VERSION,
        "record_schema": FAILURE_RECORD_SCHEMA,
        "program_id": program_id,
        "parent_id": parent_id,
        "generation": 1,
        "score": None,
        "is_valid": False,
        "error": "mutation_failed",
        "diff_error": "no_diff_blocks",
        "changed_files": changed_files,
        "file_deltas": [{"path": path, "change": "modified"} for path in changed_files],
        "mutation_text": mutation_text,
        "mutation_truncated": False,
        "mutation_sha256": mutation_sha256,
        "mutation_payload_type": payload_type,
        "mutation_payload_text": payload_text,
        "failure_fingerprint": {
            "schema": "failure_fingerprint_v1",
            "record_type": "generated",
            "parent_id": parent_id,
            "diff_error_sha256": hashlib.sha256(b"no_diff_blocks").hexdigest(),
            "evaluator_error_sha256": hashlib.sha256(b"mutation_failed").hexdigest(),
            "mutation_sha256": mutation_sha256,
            "mutation_payload_type": payload_type,
            "mutation_payload_text": payload_text,
            "changed_files": changed_files,
            "file_deltas_sha256": hashlib.sha256(b"file_deltas").hexdigest(),
            "sha256": hashlib.sha256(b"fingerprint").hexdigest(),
        },
        "evaluation": {"is_valid": False, "error": "mutation_failed", "stages": []},
        "repetition_count": 1,
    }
    row.update(extra)
    return row


def _write_failure_history(path: Path, rows: list[dict]) -> None:
    path.write_text(
        "\n".join(json.dumps(row) for row in rows) + "\n",
        encoding="utf-8",
    )


def test_load_accepted_history_index_validates_and_indexes_rows(tmp_path):
    history = tmp_path / "history.jsonl"
    _write_accepted_history(
        history,
        [
            _accepted_history_row("seed", 0.5),
            _accepted_history_row("child", 0.9, parent_id="seed", lineage=["seed"]),
        ],
    )

    index = load_accepted_history_index(history)

    assert list(index) == ["seed", "child"]
    assert index["child"]["parent_id"] == "seed"
    assert index["child"]["metrics"]["score"] == 0.9
    index["child"]["metrics"]["score"] = 0.0
    fresh = load_accepted_history_index(history)
    assert fresh["child"]["metrics"]["score"] == 0.9


def test_validate_archive_state_snapshot_returns_defensive_copy():
    snapshot = _archive_state_snapshot()

    restored = validate_archive_state_snapshot(snapshot)
    restored["archive_sequence_by_program_id"]["p1"] = 99
    restored["islands"][0]["occupied_cell_count"] = 99

    fresh = validate_archive_state_snapshot(snapshot)
    assert fresh["archive_sequence_by_program_id"]["p1"] == 1
    assert fresh["islands"][0]["occupied_cell_count"] == 1


def test_load_runtime_archive_state_snapshot_validates_manifest_runtime(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text(
        json.dumps({"runtime": {"history": {"archive_state": _archive_state_snapshot()}}}),
        encoding="utf-8",
    )

    restored = load_runtime_archive_state_snapshot(manifest)

    assert restored["schema"] == "libreevolve.island_state.v1"
    assert restored["archive_sequence_by_program_id"] == {"p1": 1, "p2": 3}
    assert restored["islands"][0]["island_id"] == 0


def test_load_runtime_archive_state_snapshot_rejects_missing_archive_state(tmp_path):
    manifest = tmp_path / "manifest.json"
    manifest.write_text('{"runtime": {"history": {}}}', encoding="utf-8")

    with pytest.raises(ArchiveStateRestoreError, match="missing archive_state"):
        load_runtime_archive_state_snapshot(manifest)


def test_validate_archive_state_snapshot_rejects_invalid_island_order():
    snapshot = _archive_state_snapshot()
    snapshot["islands"][1]["island_id"] = 0

    with pytest.raises(ArchiveStateRestoreError, match="islands\\[1\\]\\.island_id"):
        validate_archive_state_snapshot(snapshot)


def test_validate_archive_state_snapshot_rejects_unsafe_program_sequence_id():
    snapshot = _archive_state_snapshot()
    snapshot["archive_sequence_by_program_id"] = {
        "api_key=sk-proj_restore_secret": 1,
    }

    with pytest.raises(ArchiveStateRestoreError, match="invalid id"):
        validate_archive_state_snapshot(snapshot)


def test_load_archive_event_records_validates_current_schema_rows(tmp_path):
    events = tmp_path / "archive_events.jsonl"
    _write_archive_events(
        events,
        [
            _archive_event_row("p1", migration_sequence=1),
            _archive_event_row("p2", migration_sequence=1, admitted=False, cell=None),
            _archive_event_row("p3", migration_sequence=2, selection_score=None),
        ],
    )

    records = load_archive_event_records(events)
    records[0]["program_id"] = "mutated"

    assert records[0]["record_schema"] == ARCHIVE_EVENT_RECORD_SCHEMA
    assert records[1]["admitted"] is False
    assert records[2]["selection_score"] is None
    assert records[0]["objective_vector"]["normalized_metrics"] == {"score": 0.5}
    assert load_archive_event_records(events)[0]["program_id"] == "p1"


def test_load_archive_event_records_accepts_admission_rows(tmp_path):
    events = tmp_path / "archive_events.jsonl"
    _write_archive_events(
        events,
        [
            _archive_admission_event_row("p1", admission_sequence=1),
            _archive_event_row("p1", migration_sequence=1),
            _archive_admission_event_row(
                "p2",
                admission_sequence=2,
                admitted=False,
                archive_sequence=None,
                island_id=None,
                cell=None,
                reason="not_improving_cell",
                cell_admitted=False,
                elite_retained=False,
                sampling_eligible=False,
                search_state_changed=False,
            ),
        ],
    )

    records = load_archive_event_records(events)

    assert [record["event_type"] for record in records] == [
        "admission",
        "migration",
        "admission",
    ]
    assert records[0]["admission_sequence"] == 1
    assert records[2]["archive_sequence"] is None
    assert records[2]["admitted"] is False


def test_program_database_add_logs_archive_admission_event(tmp_path):
    db = ProgramDatabase(Config(log_dir=str(tmp_path), problem_name="t"))
    admitted = Program(
        id="accepted",
        code="x = 1\n",
        fitness=0.7,
        metrics={"score": 0.7},
        evaluation={"is_valid": True},
        metadata={"normalized_metrics": {"score": 0.7}, "selection_score": 0.7},
    )

    event = db.add(admitted)
    records = load_archive_event_records(tmp_path / "t" / "archive_events.jsonl")

    assert event["program_id"] == "accepted"
    assert len(records) == 1
    record = records[0]
    assert record["schema_version"] == ARTIFACT_SCHEMA_VERSION
    assert record["record_schema"] == ARCHIVE_EVENT_RECORD_SCHEMA
    assert record["event_type"] == "admission"
    assert record["admission_sequence"] == 1
    assert record["program_id"] == "accepted"
    assert record["canonical_program_id"] == "accepted"
    assert record["archive_sequence"] == 1
    assert record["island_id"] == 0
    assert record["admitted"] is True
    assert record["reason"] == "empty_cell"
    assert record["cell"] == event["cell"]
    assert record["selection_score"] == 0.7
    assert record["threshold"] == 0.0
    assert record["evaluation_is_valid"] is True
    assert record["cell_admitted"] is True
    assert record["elite_retained"] is True
    assert record["sampling_eligible"] is True
    assert record["search_state_changed"] is True
    assert record["previous_occupant_id"] is None
    assert record["objective_vector"]["normalized_metrics"] == {"score": 0.7}
    assert record["descriptors"] == event["descriptors"]


def test_load_archive_event_records_accepts_legacy_rows_without_objective_vector(
    tmp_path,
):
    events = tmp_path / "archive_events.jsonl"
    row = _archive_event_row("p1")
    row.pop("objective_vector")
    _write_archive_events(events, [row])

    assert load_archive_event_records(events)[0]["program_id"] == "p1"


def test_load_archive_event_records_rejects_malformed_objective_vector(tmp_path):
    events = tmp_path / "archive_events.jsonl"
    _write_archive_events(
        events,
        [
            _archive_event_row(
                objective_vector={
                    "policy": "normalized_declared_metric_vector_v1",
                    "normalized_metrics": {"score": 1.5},
                }
            )
        ],
    )

    with pytest.raises(ArchiveEventRestoreError, match="objective_vector"):
        load_archive_event_records(events)


def test_load_archive_event_records_rejects_duplicate_json_object_names(tmp_path):
    events = tmp_path / "archive_events.jsonl"
    events.write_text(
        (
            '{"schema_version":1,"record_schema":"libreevolve.archive_event.v1",'
            '"event_type":"migration","event_type":"other"}\n'
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        ArchiveEventRestoreError,
        match="duplicate JSON object name 'event_type'",
    ):
        load_archive_event_records(events)


def test_load_archive_event_records_rejects_decreasing_migration_sequence(tmp_path):
    events = tmp_path / "archive_events.jsonl"
    _write_archive_events(
        events,
        [
            _archive_event_row("p2", migration_sequence=2),
            _archive_event_row("p1", migration_sequence=1),
        ],
    )

    with pytest.raises(ArchiveEventRestoreError, match="non-decreasing"):
        load_archive_event_records(events)


def test_load_archive_event_records_rejects_unsafe_program_id(tmp_path):
    events = tmp_path / "archive_events.jsonl"
    _write_archive_events(
        events,
        [_archive_event_row("api_key=sk-proj_archive_event_secret")],
    )

    with pytest.raises(ArchiveEventRestoreError, match="program_id"):
        load_archive_event_records(events)


def test_load_archive_event_records_rejects_malformed_cell(tmp_path):
    events = tmp_path / "archive_events.jsonl"
    _write_archive_events(events, [_archive_event_row(cell=[0, -1, 2])])

    with pytest.raises(ArchiveEventRestoreError, match=r"cell\[1\]"):
        load_archive_event_records(events)


def test_archive_event_replay_audit_verifies_current_migration_placements(tmp_path):
    events = tmp_path / "archive_events.jsonl"
    _write_archive_events(
        events,
        [
            _archive_event_row("p1", migration_sequence=1),
            _archive_event_row("p2", migration_sequence=2, cell=[3, 2, 1]),
        ],
    )
    snapshot = _archive_state_snapshot_with_contents(
        island1_cells=[
            {"cell": [0, 1, 2], "program_id": "p1", "selection_score": 0.5},
            {"cell": [3, 2, 1], "program_id": "p2", "selection_score": 0.5},
        ],
    )

    audit = archive_event_replay_audit(events, snapshot)

    assert audit["schema"] == "libreevolve.archive_event_replay_audit.v1"
    assert audit["status"] == "verified_against_archive_contents"
    assert audit["audit_only"] is True
    assert audit["replay_engine_supported"] is False
    assert audit["event_count"] == 2
    assert audit["admitted_event_count"] == 2
    assert audit["final_replayed_placement_count"] == 2
    assert audit["matched_placement_count"] == 2
    assert audit["superseded_or_missing_count"] == 0
    assert audit["mismatches"] == []
    assert validate_archive_event_replay_audit(audit) == audit


def test_archive_event_replay_audit_reports_superseded_migration_placement():
    snapshot = _archive_state_snapshot_with_contents(
        island1_cells=[
            {"cell": [0, 1, 2], "program_id": "replacement", "selection_score": 0.9},
        ],
    )

    audit = audit_archive_event_records([_archive_event_row("p1")], snapshot)

    assert audit["status"] == "superseded_or_missing_migration_placements"
    assert audit["matched_placement_count"] == 0
    assert audit["superseded_or_missing_count"] == 1
    assert audit["mismatches"] == [
        {
            "island_id": 1,
            "cell": [0, 1, 2],
            "expected_program_id": "p1",
            "actual_program_id": "replacement",
            "migration_sequence": 1,
            "reason": "migration_placement_not_current_in_archive_contents",
        }
    ]
    assert validate_archive_event_replay_audit(audit) == audit


def test_archive_event_replay_audit_reports_absent_stream(tmp_path):
    audit = archive_event_replay_audit(
        tmp_path / "archive_events.jsonl",
        _archive_state_snapshot_with_contents(),
    )

    assert audit["status"] == "archive_events_absent"
    assert audit["event_count"] == 0
    assert audit["limitations"] == [
        "audit_replays_migration_rows_only_admission_rows_are_not_restore_engine",
        "audit_does_not_restore_controller_pending_work",
        "superseded_non_migration_cell_replacements_report_as_mismatches",
        "archive_contents_snapshot_remains_restore_source",
    ]
    assert validate_archive_event_replay_audit(audit) == audit


def test_validate_archive_event_replay_audit_rejects_restore_overclaim():
    audit = audit_archive_event_records(
        [_archive_event_row("p1")],
        _archive_state_snapshot_with_contents(
            island1_cells=[
                {"cell": [0, 1, 2], "program_id": "p1", "selection_score": 0.5},
            ],
        ),
    )
    audit["audit_only"] = False
    audit["replay_engine_supported"] = True

    with pytest.raises(ArchiveEventRestoreError, match="audit-only"):
        validate_archive_event_replay_audit(audit)

    audit["audit_only"] = True
    with pytest.raises(ArchiveEventRestoreError, match="restore-engine"):
        validate_archive_event_replay_audit(audit)


def test_validate_archive_event_replay_audit_rejects_count_mismatch():
    audit = audit_archive_event_records(
        [_archive_event_row("p1"), _archive_event_row("p2", admitted=False, cell=None)],
        _archive_state_snapshot_with_contents(
            island1_cells=[
                {"cell": [0, 1, 2], "program_id": "p1", "selection_score": 0.5},
            ],
        ),
    )
    audit["event_count"] = 99

    with pytest.raises(ArchiveEventRestoreError, match="event counts"):
        validate_archive_event_replay_audit(audit)

    audit["event_count"] = 2
    audit["final_replayed_placement_count"] = 99
    with pytest.raises(ArchiveEventRestoreError, match="placement counts"):
        validate_archive_event_replay_audit(audit)


def test_validate_archive_event_replay_audit_rejects_malformed_mismatch():
    audit = audit_archive_event_records(
        [_archive_event_row("p1")],
        _archive_state_snapshot_with_contents(
            island1_cells=[
                {"cell": [0, 1, 2], "program_id": "replacement", "selection_score": 0.9},
            ],
        ),
    )
    audit["mismatches"][0]["actual_program_id"] = "../escape"

    with pytest.raises(ArchiveEventRestoreError, match="program id"):
        validate_archive_event_replay_audit(audit)

    audit = audit_archive_event_records(
        [_archive_event_row("p1")],
        _archive_state_snapshot_with_contents(
            island1_cells=[
                {"cell": [0, 1, 2], "program_id": "replacement", "selection_score": 0.9},
            ],
        ),
    )
    audit["mismatches"][0]["cell"] = [0, -1, 2]
    with pytest.raises(ArchiveEventRestoreError, match=r"cell\[1\]"):
        validate_archive_event_replay_audit(audit)


def test_archive_event_replay_audit_rejects_admitted_event_without_cell():
    with pytest.raises(ArchiveEventRestoreError, match="must include cell"):
        audit_archive_event_records(
            [_archive_event_row("p1", cell=None)],
            _archive_state_snapshot_with_contents(),
        )


def test_load_accepted_history_index_accepts_current_and_legacy_schema_rows(tmp_path):
    history = tmp_path / "history.jsonl"
    current = _accepted_history_row(
        "current",
        0.5,
        schema_version=ARTIFACT_SCHEMA_VERSION,
        record_schema=HISTORY_RECORD_SCHEMA,
    )
    legacy = _accepted_history_row("legacy", 0.7)
    _write_accepted_history(history, [current, legacy])

    index = load_accepted_history_index(history)

    assert index["current"]["record_schema"] == HISTORY_RECORD_SCHEMA
    assert "record_schema" not in index["legacy"]


@pytest.mark.parametrize(
    ("field", "value", "message"),
    [
        ("schema_version", 999, "unsupported schema_version"),
        ("record_schema", "libreevolve.other.v1", "unsupported record_schema"),
    ],
)
def test_load_accepted_history_index_rejects_unsupported_declared_schema(
    tmp_path,
    field,
    value,
    message,
):
    history = tmp_path / "history.jsonl"
    row = _accepted_history_row(
        "p1",
        0.5,
        schema_version=ARTIFACT_SCHEMA_VERSION,
        record_schema=HISTORY_RECORD_SCHEMA,
    )
    row[field] = value
    _write_accepted_history(history, [row])

    with pytest.raises(HistoryRestoreError, match=message):
        load_accepted_history_index(history)


@pytest.mark.parametrize(
    "rows",
    [
        [_accepted_history_row("dup"), _accepted_history_row("dup")],
        [_accepted_history_row("dup", 0.1), _accepted_history_row("dup", 0.9)],
    ],
)
def test_load_accepted_history_index_rejects_duplicate_program_ids(tmp_path, rows):
    history = tmp_path / "history.jsonl"
    _write_accepted_history(history, rows)

    with pytest.raises(HistoryRestoreError, match="duplicate program id 'dup'"):
        load_accepted_history_index(history)


@pytest.mark.parametrize(
    ("program_id", "message"),
    [
        ("bad\nid", "Program id"),
        ("api_key=sk-proj_restore_id_secret_1234567890", "Program id"),  # pragma: allowlist secret
        ("rtl\u202egnp", "Program id"),
    ],
)
def test_load_accepted_history_index_rejects_unsafe_program_ids(
    tmp_path, program_id, message
):
    history = tmp_path / "history.jsonl"
    _write_accepted_history(history, [_accepted_history_row(program_id)])

    with pytest.raises(HistoryRestoreError, match=message):
        load_accepted_history_index(history)


def test_load_accepted_history_index_rejects_duplicate_json_object_names(tmp_path):
    history = tmp_path / "history.jsonl"
    history.write_text(
        '{"id":"p1","id":"p2","fitness":1.0,"generation":0}\n',
        encoding="utf-8",
    )

    with pytest.raises(HistoryRestoreError, match="duplicate JSON object name 'id'"):
        load_accepted_history_index(history)


@pytest.mark.parametrize(
    ("payload", "message"),
    [
        (b"\xff\n", "line 1: invalid UTF-8"),
        (
            json.dumps(_accepted_history_row("ok")).encode("utf-8") + b"\n\xff\n",
            "line 2: invalid UTF-8",
        ),
    ],
)
def test_load_accepted_history_index_reports_invalid_utf8_by_line(
    tmp_path,
    payload,
    message,
):
    history = tmp_path / "history.jsonl"
    history.write_bytes(payload)

    with pytest.raises(HistoryRestoreError, match=message):
        load_accepted_history_index(history)


@pytest.mark.parametrize("fitness", [math.inf, -math.inf, math.nan, True, "1.0"])
def test_load_accepted_history_index_rejects_invalid_fitness(tmp_path, fitness):
    history = tmp_path / "history.jsonl"
    _write_accepted_history(history, [_accepted_history_row("p1", fitness)])

    with pytest.raises(HistoryRestoreError, match="fitness must be a finite number"):
        load_accepted_history_index(history)


def test_load_failure_history_records_rejects_duplicate_json_object_names(tmp_path):
    failures = tmp_path / "failure_history.jsonl"
    failures.write_text(
        (
            '{"record_schema":"libreevolve.failure_history.v1",'
            '"metadata":{"reason":"a","reason":"b"}}\n'
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        HistoryRestoreError,
        match="Malformed failure_history.jsonl at line 1: duplicate JSON object name 'reason'",
    ):
        load_failure_history_records(failures)


def test_load_failure_history_records_accepts_current_schema_rows(tmp_path):
    failures = tmp_path / "failure_history.jsonl"
    _write_failure_history(failures, [_failure_history_row()])

    records = load_failure_history_records(failures)

    assert records[0]["record_schema"] == FAILURE_RECORD_SCHEMA
    assert records[0]["mutation_payload_replay"] == {
        "policy": "diagnostic_only_do_not_reapply",
        "payload_kind": "text",
        "payload_type": "str",
        "mutation_text": "bounded_redacted_diagnostic",
        "mutation_sha256": records[0]["mutation_sha256"],
        "queryable": True,
    }
    records[0]["program_id"] = "mutated"
    assert load_failure_history_records(failures)[0]["program_id"] == "p1"


def test_load_failure_history_records_keeps_non_text_payload_rows_queryable(tmp_path):
    failures = tmp_path / "failure_history.jsonl"
    mutation_text = "{'bad': <object object>}"
    mutation_sha256 = hashlib.sha256(mutation_text.encode("utf-8")).hexdigest()
    _write_failure_history(
        failures,
        [
            _failure_history_row(
                mutation_text=mutation_text,
                mutation_sha256=mutation_sha256,
                mutation_payload_text=False,
                mutation_payload_type="dict",
                diff_error="non_text_mutation_payload",
            )
        ],
    )

    [record] = load_failure_history_records(failures)

    assert record["mutation_text"] == mutation_text
    assert record["mutation_payload_replay"]["payload_kind"] == "non_text"
    assert record["mutation_payload_replay"]["queryable"] is True
    assert record["mutation_payload_replay"]["policy"] == "diagnostic_only_do_not_reapply"


@pytest.mark.parametrize(
    ("mutation", "message"),
    [
        (
            lambda row: row.__setitem__("program_id", "bad\nid"),
            "Program id must be a manifest-safe identifier",
        ),
        (
            lambda row: row.__setitem__("generation", -1),
            "generation must be a non-negative integer",
        ),
        (
            lambda row: row.__setitem__("mutation_text", {"not": "text"}),
            "mutation_text must be a bounded diagnostic string",
        ),
        (
            lambda row: row.__setitem__("mutation_payload_text", "false"),
            "mutation_payload_text must be boolean",
        ),
        (
            lambda row: row.__setitem__("mutation_sha256", "not-a-sha"),
            "mutation_sha256 must be a SHA-256 hex digest",
        ),
        (
            lambda row: row["failure_fingerprint"].__setitem__(
                "mutation_sha256", hashlib.sha256(b"other").hexdigest()
            ),
            "failure_fingerprint.mutation_sha256 must match",
        ),
        (
            lambda row: row.__setitem__("changed_files", ["../escape.py"]),
            "Unsafe candidate path",
        ),
    ],
)
def test_load_failure_history_records_rejects_malformed_payload_evidence(
    tmp_path, mutation, message
):
    failures = tmp_path / "failure_history.jsonl"
    row = _failure_history_row()
    mutation(row)
    _write_failure_history(failures, [row])

    with pytest.raises(HistoryRestoreError, match=message):
        load_failure_history_records(failures)


def test_load_failure_history_records_rejects_duplicate_failed_program_ids(tmp_path):
    failures = tmp_path / "failure_history.jsonl"
    _write_failure_history(
        failures,
        [
            _failure_history_row("dup"),
            _failure_history_row("dup", mutation_text="other mutation"),
        ],
    )

    with pytest.raises(HistoryRestoreError, match="duplicate failed program id 'dup'"):
        load_failure_history_records(failures)


def test_database_rejects_windows_junction_known_artifact_before_overwrite(tmp_path):
    if sys.platform != "win32":
        pytest.skip("Windows junction test")

    log_root = tmp_path / "runs"
    run_dir = log_root / "t"
    outside = tmp_path / "outside"
    run_dir.mkdir(parents=True)
    outside.mkdir()
    (run_dir / "history.jsonl").write_text("{}\n", encoding="utf-8")
    (outside / "old.py").write_text("outside", encoding="utf-8")
    linked_artifact = run_dir / "evaluator_artifacts"
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(linked_artifact), str(outside)],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        pytest.skip(f"junction creation is unavailable: {result.stderr or result.stdout}")

    with pytest.raises(ValueError, match="linked run artifacts"):
        ProgramDatabase(
            Config(
                log_dir=str(log_root),
                problem_name="t",
                run_collision_policy="overwrite",
            )
        )

    assert (run_dir / "history.jsonl").read_text(encoding="utf-8") == "{}\n"
    assert (outside / "old.py").read_text(encoding="utf-8") == "outside"


def test_maybe_migrate_triggers_on_interval():
    tmpdir = tempfile.mkdtemp()
    db = ProgramDatabase(
        Config(migration_interval=5, n_islands=2, log_dir=tmpdir, problem_name="t")
    )
    p = _p(); db.log(p); db.add(p)
    # Before interval: island 1 has nothing
    assert db._islands.islands[1].best() is None
    assert db.maybe_migrate(4) == []  # not a multiple of 5 — no migration
    assert db._islands.islands[1].best() is None
    events = db.maybe_migrate(5)  # multiple of 5 — migration fires
    assert db._islands.islands[1].best() is not None
    assert events[0]["program_id"] == p.id
    assert events[0]["identity_policy"] == "canonical_id_reference"
    assert db.best().metadata["migration_placements"] == events
    archive_records = [
        json.loads(line)
        for line in (Path(tmpdir) / "t" / "archive_events.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
    ]
    [record] = [
        row for row in archive_records if row.get("event_type") == "migration"
    ]
    [admission_record] = [
        row for row in archive_records if row.get("event_type") == "admission"
    ]
    assert admission_record["program_id"] == p.id
    assert record["schema_version"] == ARTIFACT_SCHEMA_VERSION
    assert record["record_schema"] == ARCHIVE_EVENT_RECORD_SCHEMA
    assert record["event_type"] == "migration"
    assert record["program_id"] == p.id
    assert record["migration_sequence"] == events[0]["migration_sequence"]
    assert record["source_island"] == events[0]["source_island"]
    assert record["target_island"] == events[0]["target_island"]
