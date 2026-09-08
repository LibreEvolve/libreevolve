from fractions import Fraction

import pytest
from libreevolve.population.map_elites import (
    MAPElites,
    MAP_ELITES_DESCRIPTOR_READINESS_SCHEMA,
    MAP_ELITES_OBJECTIVE_ARCHIVE_READINESS_SCHEMA,
    MAP_ELITES_OBJECTIVE_ARCHIVE_POLICY_SCHEMA,
    _descriptor_text,
    validate_map_elites_objective_archive_policy,
)
from libreevolve.population.program import Program

def _p(code="x=1", fitness=0.5):
    return Program(code=code, fitness=fitness, evaluation={"is_valid": True})

def _pm(code="x=1", fitness=0.5, selection_score=0.5):
    return Program(
        code=code,
        fitness=fitness,
        evaluation={"is_valid": True},
        metadata={"selection_score": selection_score},
    )

def _po(code, fitness, metrics):
    return Program(
        code=code,
        fitness=fitness,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": fitness,
            "normalized_metrics": metrics,
        },
    )

def test_best_none_when_empty():
    assert MAPElites().best() is None


@pytest.mark.parametrize("bins", [0, -1, True, 1.5, "10"])
def test_rejects_invalid_bins(bins):
    with pytest.raises(ValueError, match="bins must be a positive integer"):
        MAPElites(bins=bins)


@pytest.mark.parametrize("elite_archive_size", [0, -1, True, 1.5, "50"])
def test_rejects_invalid_elite_archive_size(elite_archive_size):
    with pytest.raises(ValueError, match="elite_archive_size must be a positive integer"):
        MAPElites(elite_archive_size=elite_archive_size)


@pytest.mark.parametrize("complexity_max_chars", [0, -1, True, 1.5, "100"])
def test_rejects_invalid_complexity_max_chars(complexity_max_chars):
    with pytest.raises(ValueError, match="complexity_max_chars must be a positive integer"):
        MAPElites(complexity_max_chars=complexity_max_chars)


@pytest.mark.parametrize(
    "descriptor_axes",
    [
        [],
        ["performance", "complexity"],
        ["performance", "complexity", "bad"],
        ["performance", "performance", "diversity"],
        ["metric:bad role", "complexity", "diversity"],
    ],
)
def test_rejects_invalid_descriptor_axes(descriptor_axes):
    with pytest.raises(ValueError, match="descriptor_axes"):
        MAPElites(descriptor_axes=descriptor_axes)


@pytest.mark.parametrize(
    "perf_bounds",
    [(1.0, 1.0), (2.0, 1.0), (0.0, float("inf")), (True, 1.0), (0.0,), "bad"],
)
def test_rejects_invalid_perf_bounds(perf_bounds):
    with pytest.raises(ValueError, match="perf_bounds"):
        MAPElites(perf_bounds=perf_bounds)


def test_add_and_best():
    a = MAPElites(); event = a.add(_p(fitness=0.7))
    assert a.best().fitness == 0.7
    assert event["admitted"] is True
    assert event["entered_cell"] is True
    assert event["cell_admitted"] is True
    assert event["elite_retained"] is True
    assert event["search_state_changed"] is True
    assert event["sampling_eligible"] is True
    assert event["reason"] == "empty_cell"
    assert event["cell"] is not None
    assert set(event["descriptors"]) == {"performance", "complexity", "diversity"}

def test_replacement_only_when_higher():
    a = MAPElites(bins=1)
    first = _p(code="x=1", fitness=0.3)
    a.add(first)
    second = _p(code="x=1", fitness=0.8)
    event = a.add(second)
    assert a._grid[(0, 0, 0)].fitness == 0.8
    assert event["cell_replaced"] is True
    assert event["previous_occupant_id"] == first.id

def test_lower_does_not_replace():
    a = MAPElites(bins=1)
    a.add(_p(code="x=1", fitness=0.8))
    event = a.add(_p(code="x=1", fitness=0.3))
    assert a._grid[(0, 0, 0)].fitness == 0.8
    assert event["entered_cell"] is False
    assert event["cell_admitted"] is False
    assert event["reason"] in {"elite_only", "not_improving_cell"}


def test_non_admitted_candidate_does_not_mutate_complexity_scale():
    a = MAPElites(bins=1, elite_archive_size=1, complexity_max_chars=10_000)
    first = _p(code="x=1", fitness=1.0)
    a.add(first)
    first_complexity = a._cell_with_descriptors(first)[1]["complexity"]

    long_rejected = _p(code="x" * 4000, fitness=0.0)
    rejected = a.add(long_rejected)

    assert rejected["admitted"] is False
    assert rejected["reason"] == "not_improving_cell"

    short = _p(code="y=1", fitness=0.5)
    cell, descriptors = a._cell_with_descriptors(short)

    assert cell == (0, 0, 0)
    assert descriptors["complexity"] == first_complexity


def test_retained_candidate_does_not_change_complexity_scale():
    a = MAPElites(bins=1, elite_archive_size=2, complexity_max_chars=10_000)
    first = _p(code="x=1", fitness=1.0)
    a.add(first)
    first_complexity = a._cell_with_descriptors(first)[1]["complexity"]
    long_elite = _p(code="x" * 4000, fitness=0.0)

    event = a.add(long_elite)

    assert event["admitted"] is True
    assert event["reason"] == "elite_only"
    assert a._cell_with_descriptors(first)[1]["complexity"] == first_complexity


def test_complexity_descriptor_is_clamped_to_configured_bound():
    a = MAPElites(bins=10, complexity_max_chars=10)

    event = a.add(_p(code="x" * 100, fitness=0.5))

    assert event["descriptors"]["complexity"] == 1.0


def test_configured_metric_descriptor_axis_uses_normalized_metrics():
    archive = MAPElites(
        bins=10,
        descriptor_axes=["performance", "metric:accuracy", "diversity"],
    )
    program = Program(
        code="x=1",
        fitness=0.5,
        metrics={"accuracy": 42.0},
        evaluation={"is_valid": True},
        metadata={
            "selection_score": 0.5,
            "normalized_metrics": {"accuracy": 0.73},
        },
    )

    event = archive.add(program)

    assert event["descriptors"]["metric:accuracy"] == 0.73
    assert event["cell"][1] == 7
    assert archive.state_snapshot()["descriptor_model"]["axes"] == [
        "performance",
        "metric:accuracy",
        "diversity",
    ]


def test_configured_metadata_descriptor_axes_read_numeric_paths():
    archive = MAPElites(
        bins=10,
        descriptor_axes=[
            "evaluation_metadata:behavior.novelty",
            "candidate_metadata:archive.score",
            "complexity",
        ],
    )
    program = Program(
        code="x=1",
        fitness=0.5,
        evaluation={
            "is_valid": True,
            "metadata": {"behavior": {"novelty": 0.21}},
        },
        metadata={"archive": {"score": 0.91}},
    )

    event = archive.add(program)

    assert event["descriptors"]["evaluation_metadata:behavior.novelty"] == 0.21
    assert event["descriptors"]["candidate_metadata:archive.score"] == 0.91
    assert event["cell"][0] == 2
    assert event["cell"][1] == 9


def test_elite_only_retention_is_not_cell_sampling_eligible():
    a = MAPElites(bins=1, elite_archive_size=50)
    first = _p(code="x=1", fitness=0.9)
    a.add(first)

    second = _p(code="x=1", fitness=0.1)
    event = a.add(second)

    assert event["admitted"] is True
    assert event["reason"] == "elite_only"
    assert event["entered_cell"] is False
    assert event["entered_elite"] is True
    assert event["cell_admitted"] is False
    assert event["elite_retained"] is True
    assert event["search_state_changed"] is True
    assert event["sampling_eligible"] is False
    assert second in a.elite_archive()
    assert second not in a.occupied_cells()
    assert second not in a.sample_diverse(k=10)


def test_pareto_frontier_retains_non_dominated_non_scalar_elite():
    archive = MAPElites(
        bins=1,
        elite_archive_size=2,
        metric_order=["accuracy", "latency"],
    )
    balanced = _po("balanced", 0.9, {"accuracy": 0.80, "latency": 0.80})
    latency = _po("latency", 0.8, {"accuracy": 0.70, "latency": 0.95})
    accuracy = _po("accuracy", 0.1, {"accuracy": 0.95, "latency": 0.70})
    archive.add(balanced)
    archive.add(latency)

    event = archive.add(accuracy)

    assert event["entered_cell"] is False
    assert event["entered_elite"] is False
    assert event["pareto_frontier_retained"] is True
    assert event["pareto_frontier_reason"] == "non_dominated_objective_vector"
    assert event["pareto_frontier_size"] == 2
    assert event["pareto_frontier_replaced_ids"] == [balanced.id]
    assert event["admitted"] is True
    assert event["reason"] == "pareto_frontier_only"
    assert archive.elite_archive() == [balanced, latency]
    assert archive.pareto_frontier_archive() == [latency, accuracy]


def test_metric_cell_archive_retains_per_metric_cell_replacements():
    archive = MAPElites(
        bins=1,
        elite_archive_size=1,
        metric_order=["accuracy", "latency"],
    )
    accuracy = _po("accuracy", 0.9, {"accuracy": 0.95, "latency": 0.10})
    latency = _po("latency", 0.1, {"accuracy": 0.10, "latency": 0.95})
    archive.add(accuracy)

    event = archive.add(latency)

    assert event["entered_cell"] is False
    assert event["entered_elite"] is False
    assert event["metric_cell_retained"] is True
    assert event["metric_cell_reason"] == "metric_cell_retained"
    assert event["reason"] == "metric_cell_only"
    assert event["admitted"] is True
    assert event["search_state_changed"] is True
    assert event["metric_cell_replacements"] == [
        {
            "metric": "accuracy",
            "cell": [0, 0, 0],
            "retained": False,
            "candidate_value": 0.1,
            "previous_occupant_id": accuracy.id,
            "previous_value": 0.95,
            "cell_replaced": False,
        },
        {
            "metric": "latency",
            "cell": [0, 0, 0],
            "retained": True,
            "candidate_value": 0.95,
            "previous_occupant_id": accuracy.id,
            "previous_value": 0.1,
            "cell_replaced": True,
        },
    ]
    assert archive.occupied_cells() == [accuracy]
    assert archive.elite_archive() == [accuracy]
    assert archive.metric_cell_archive() == [accuracy, latency]


def test_state_snapshot_restores_cells_and_elite_archive():
    source = MAPElites(
        bins=1,
        elite_archive_size=2,
        metric_order=["accuracy", "latency"],
    )
    occupied = _pm(code="occupied", fitness=0.9, selection_score=0.9)
    occupied.metadata["normalized_metrics"] = {"accuracy": 0.8, "latency": 0.8}
    elite_only = _pm(code="elite_only", fitness=0.1, selection_score=0.1)
    elite_only.metadata["normalized_metrics"] = {"accuracy": 0.1, "latency": 0.9}
    source.add(occupied)
    source.add(elite_only)

    snapshot = source.state_snapshot()
    restored = MAPElites(
        bins=1,
        elite_archive_size=2,
        metric_order=["accuracy", "latency"],
    )
    result = restored.restore_state_snapshot(
        snapshot,
        {occupied.id: occupied, elite_only.id: elite_only},
    )

    assert snapshot["schema"] == "libreevolve.map_elites_state.v1"
    assert snapshot["descriptor_axes"] == ["performance", "complexity", "diversity"]
    assert len(snapshot["cells"]) == 1
    assert snapshot["cells"][0]["cell"] == [0, 0, 0]
    assert snapshot["cells"][0]["program_id"] == occupied.id
    assert snapshot["cells"][0]["selection_score"] == 0.9
    assert snapshot["cells"][0]["descriptors"]["performance"] == 0.9
    assert snapshot["cells"][0]["descriptors"]["diversity"] == 0.5
    assert 0.0 <= snapshot["cells"][0]["descriptors"]["complexity"] <= 1.0
    occupied_descriptors = snapshot["cells"][0]["descriptors"]
    assert snapshot["elite_program_ids"] == [occupied.id, elite_only.id]
    assert [record["program_id"] for record in snapshot["elite_descriptor_records"]] == [
        occupied.id,
        elite_only.id,
    ]
    assert snapshot["elite_descriptor_records"][0]["descriptors"] == (
        occupied_descriptors
    )
    assert snapshot["elite_descriptor_records"][1]["descriptors"]["performance"] == 0.1
    assert (
        0.0
        <= snapshot["elite_descriptor_records"][1]["descriptors"]["diversity"]
        <= 1.0
    )
    assert snapshot["pareto_frontier_program_ids"] == [occupied.id, elite_only.id]
    assert [
        record["program_id"]
        for record in snapshot["pareto_frontier_descriptor_records"]
    ] == [occupied.id, elite_only.id]
    assert snapshot["pareto_frontier_descriptor_records"][0]["descriptors"] == (
        occupied_descriptors
    )
    assert snapshot["metric_cell_archives"] == [
        {
            "metric": "accuracy",
            "cells": [
                {
                    "cell": [0, 0, 0],
                    "program_id": occupied.id,
                    "metric_value": 0.8,
                    "descriptors": occupied_descriptors,
                    "selection_score": 0.9,
                }
            ],
        },
        {
            "metric": "latency",
            "cells": [
                {
                    "cell": [0, 0, 0],
                    "program_id": elite_only.id,
                    "metric_value": 0.9,
                    "descriptors": snapshot["elite_descriptor_records"][1][
                        "descriptors"
                    ],
                    "selection_score": 0.1,
                }
            ],
        },
    ]
    assert snapshot["objective_archive_policy"] == {
        "schema": MAP_ELITES_OBJECTIVE_ARCHIVE_POLICY_SCHEMA,
        "status": "bounded_non_dominated_archive_retention",
        "metric_order": ["accuracy", "latency"],
        "candidate_vector": "complete_normalized_declared_metrics_required",
        "dominance": "all_metrics_greater_or_equal_and_one_strictly_greater",
        "bound": 2,
        "trim_policy": "crowding_distance_then_selection_score_then_fitness",
        "sampling_policy": (
            "eligible_for_metric_frontier_and_metric_cell_sampling_via_island_retained_pool"
        ),
        "cell_replacement_policy": (
            "scalar_primary_cells_plus_metric_specific_cell_overlays"
        ),
        "readiness": {
            "schema": MAP_ELITES_OBJECTIVE_ARCHIVE_READINESS_SCHEMA,
            "primary_pareto_archive_replacement": False,
            "frontier_dominance_cell_replacement": False,
            "durable_cross_run_metric_database": False,
            "metric_target_persistence_tables": False,
            "llm_feedback_calibration_runner": False,
            "remaining_gap": [
                "primary_pareto_archive_replacement",
                "frontier_dominance_cell_replacement",
                "durable_cross_run_metric_database",
                "metric_target_persistence_tables",
                "llm_feedback_calibration_runner",
            ],
        },
    }
    assert snapshot["descriptor_policy"]["rebin_policy"] == (
        "no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots"
    )
    assert snapshot["descriptor_model"] == {
        "schema": "libreevolve.map_elites_descriptor_model.v1",
        "revision": 2,
        "revision_policy": "increments_on_search_state_change",
        "axes": ["performance", "complexity", "diversity"],
        "performance_bounds": [0.0, 1.0],
        "complexity_max_chars": 100_000,
        "diversity_reference_program_ids": [occupied.id, elite_only.id],
        "dynamic_diversity_reference": True,
        "rebin_policy": (
            "no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots"
        ),
        "readiness": {
            "schema": MAP_ELITES_DESCRIPTOR_READINESS_SCHEMA,
            "stable_task_behavior_descriptor_contract": False,
            "learned_descriptor_model": False,
            "evaluator_provided_descriptor_model": False,
            "full_archive_rebin_engine": False,
            "partial_archive_rebin_engine": False,
            "descriptor_training_inputs_recorded": False,
            "restore_compatible_descriptor_revisioning": False,
            "remaining_gap": [
                "stable_task_behavior_descriptor_contract",
                "learned_descriptor_model",
                "evaluator_provided_descriptor_model",
                "full_archive_rebin_engine",
                "partial_archive_rebin_engine",
                "descriptor_training_inputs_recorded",
                "restore_compatible_descriptor_revisioning",
            ],
        },
    }
    assert result == {
        "status": "map_elites_state_restored",
        "occupied_cell_count": 1,
        "elite_count": 2,
        "pareto_frontier_count": 2,
        "metric_cell_archive_count": 2,
    }
    assert restored.best() is occupied
    assert restored.occupied_cells() == [occupied]
    assert restored.state_snapshot()["cells"][0]["descriptors"] == (
        snapshot["cells"][0]["descriptors"]
    )
    assert restored.state_snapshot()["elite_descriptor_records"] == (
        snapshot["elite_descriptor_records"]
    )
    assert restored.state_snapshot()["pareto_frontier_descriptor_records"] == (
        snapshot["pareto_frontier_descriptor_records"]
    )
    assert restored.state_snapshot()["metric_cell_archives"] == (
        snapshot["metric_cell_archives"]
    )
    assert restored.elite_archive() == [occupied, elite_only]
    assert restored.pareto_frontier_archive() == [occupied, elite_only]
    assert restored.metric_cell_archive() == [occupied, elite_only]


def test_restore_state_snapshot_rejects_missing_program_reference():
    source = MAPElites()
    program = _pm(code="x=1", fitness=0.5, selection_score=0.5)
    source.add(program)

    with pytest.raises(ValueError, match="missing program id"):
        MAPElites().restore_state_snapshot(source.state_snapshot(), {})


def test_restore_state_snapshot_rejects_missing_metric_cell_program_reference():
    source = MAPElites(
        bins=1,
        elite_archive_size=1,
        metric_order=["accuracy"],
    )
    program = _po("x=1", 0.5, {"accuracy": 0.7})
    source.add(program)
    snapshot = source.state_snapshot()
    snapshot["metric_cell_archives"][0]["cells"][0]["program_id"] = "missing"

    with pytest.raises(ValueError, match="metric cell references missing program id"):
        MAPElites(
            bins=1,
            elite_archive_size=1,
            metric_order=["accuracy"],
        ).restore_state_snapshot(snapshot, {program.id: program})


def test_objective_archive_policy_validator_accepts_snapshot_policy():
    archive = MAPElites(metric_order=["accuracy", "latency"], elite_archive_size=3)
    archive.add(_po("balanced", 0.7, {"accuracy": 0.7, "latency": 0.7}))
    policy = archive.state_snapshot()["objective_archive_policy"]

    validation = validate_map_elites_objective_archive_policy(
        policy,
        metric_order=["accuracy", "latency"],
        elite_archive_size=3,
    )

    assert validation.ok is True
    assert validation.archive_policy_ready is True
    assert validation.primary_pareto_replacement_ready is False
    assert validation.metric_order == ["accuracy", "latency"]
    assert validation.bound == 3
    assert validation.issues == []
    assert policy["schema"] == MAP_ELITES_OBJECTIVE_ARCHIVE_POLICY_SCHEMA
    assert policy["readiness"]["schema"] == MAP_ELITES_OBJECTIVE_ARCHIVE_READINESS_SCHEMA
    assert policy["readiness"]["primary_pareto_archive_replacement"] is False
    assert policy["readiness"]["frontier_dominance_cell_replacement"] is False
    assert policy["readiness"]["durable_cross_run_metric_database"] is False
    assert policy["readiness"]["metric_target_persistence_tables"] is False
    assert policy["readiness"]["llm_feedback_calibration_runner"] is False


def test_objective_archive_policy_validator_rejects_primary_pareto_overclaim():
    archive = MAPElites(metric_order=["accuracy", "latency"], elite_archive_size=3)
    policy = archive.state_snapshot()["objective_archive_policy"]
    policy["metric_order"] = ["accuracy"]
    policy["bound"] = 4
    policy["cell_replacement_policy"] = "pareto_frontier_primary_cell_replacement"

    validation = validate_map_elites_objective_archive_policy(
        policy,
        metric_order=["accuracy", "latency"],
        elite_archive_size=3,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.archive_policy_ready is False
    assert validation.primary_pareto_replacement_ready is False
    assert validation.metric_order == ["accuracy"]
    assert validation.bound == 4
    assert "metric_order_mismatch" in codes
    assert "bound_mismatch" in codes
    assert "primary_pareto_replacement_overclaim" in codes


def test_objective_archive_policy_validator_rejects_readiness_overclaim():
    archive = MAPElites(metric_order=["accuracy", "latency"], elite_archive_size=3)
    policy = archive.state_snapshot()["objective_archive_policy"]
    policy["readiness"]["primary_pareto_archive_replacement"] = True

    validation = validate_map_elites_objective_archive_policy(
        policy,
        metric_order=["accuracy", "latency"],
        elite_archive_size=3,
    )
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.archive_policy_ready is False
    assert validation.primary_pareto_replacement_ready is False
    assert "primary_pareto_archive_replacement_overclaim" in codes


def test_restore_state_snapshot_accepts_legacy_objective_policy_without_readiness():
    source = MAPElites(metric_order=["accuracy", "latency"], elite_archive_size=2)
    program = _po("balanced", 0.7, {"accuracy": 0.7, "latency": 0.7})
    source.add(program)
    snapshot = source.state_snapshot()
    del snapshot["objective_archive_policy"]["readiness"]

    result = MAPElites(
        metric_order=["accuracy", "latency"],
        elite_archive_size=2,
    ).restore_state_snapshot(snapshot, {program.id: program})

    assert result["status"] == "map_elites_state_restored"


def test_restore_state_snapshot_accepts_legacy_cells_without_descriptor_values():
    source = MAPElites()
    program = _pm(code="x=1", fitness=0.5, selection_score=0.5)
    source.add(program)
    snapshot = source.state_snapshot()
    del snapshot["cells"][0]["descriptors"]

    restored = MAPElites()
    result = restored.restore_state_snapshot(snapshot, {program.id: program})

    assert result["status"] == "map_elites_state_restored"
    assert restored.state_snapshot()["cells"][0]["descriptors"] == {}


def test_restore_state_snapshot_rejects_invalid_cell_descriptor_values():
    source = MAPElites()
    program = _pm(code="x=1", fitness=0.5, selection_score=0.5)
    source.add(program)
    snapshot = source.state_snapshot()
    snapshot["cells"][0]["descriptors"]["diversity"] = float("inf")

    with pytest.raises(ValueError, match="descriptors\\['diversity'\\]"):
        MAPElites().restore_state_snapshot(snapshot, {program.id: program})


def test_restore_state_snapshot_rejects_elite_descriptor_record_drift():
    source = MAPElites()
    program = _pm(code="x=1", fitness=0.5, selection_score=0.5)
    source.add(program)
    snapshot = source.state_snapshot()
    snapshot["elite_descriptor_records"][0]["program_id"] = "other"

    with pytest.raises(ValueError, match="elite_descriptor_records\\[0\\]"):
        MAPElites().restore_state_snapshot(snapshot, {program.id: program})


def test_restore_state_snapshot_rejects_metric_cell_descriptor_drift():
    source = MAPElites(metric_order=["accuracy"])
    program = _po("x=1", 0.5, {"accuracy": 0.7})
    source.add(program)
    snapshot = source.state_snapshot()
    snapshot["metric_cell_archives"][0]["cells"][0]["descriptors"].pop("diversity")

    with pytest.raises(ValueError, match="metric_cell_archives\\[0\\]"):
        MAPElites(metric_order=["accuracy"]).restore_state_snapshot(
            snapshot,
            {program.id: program},
        )


def test_restore_state_snapshot_rejects_objective_policy_readiness_overclaim():
    source = MAPElites(metric_order=["accuracy", "latency"], elite_archive_size=2)
    program = _po("balanced", 0.7, {"accuracy": 0.7, "latency": 0.7})
    source.add(program)
    snapshot = source.state_snapshot()
    snapshot["objective_archive_policy"]["readiness"][
        "frontier_dominance_cell_replacement"
    ] = True

    with pytest.raises(ValueError, match="frontier_dominance_cell_replacement"):
        MAPElites(
            metric_order=["accuracy", "latency"],
            elite_archive_size=2,
        ).restore_state_snapshot(snapshot, {program.id: program})


def test_descriptor_model_revision_only_advances_on_search_state_change():
    archive = MAPElites(bins=1, elite_archive_size=1)
    first = _pm(code="best", fitness=1.0, selection_score=1.0)
    weak = _pm(code="weak", fitness=0.1, selection_score=0.1)

    assert archive.state_snapshot()["descriptor_model"]["revision"] == 0
    first_event = archive.add(first)
    revision_after_first = archive.state_snapshot()["descriptor_model"]["revision"]
    weak_event = archive.add(weak)

    assert first_event["search_state_changed"] is True
    assert revision_after_first == 1
    assert weak_event["search_state_changed"] is False
    assert weak_event["reason"] == "not_improving_cell"
    assert archive.state_snapshot()["descriptor_model"]["revision"] == 1


def test_dynamic_diversity_policy_does_not_rebin_existing_cells():
    archive = MAPElites(bins=10, elite_archive_size=3)
    first = _pm(code="a = 1\n", fitness=0.9, selection_score=0.9)
    second = _pm(code="b = 'different text'\n", fitness=0.8, selection_score=0.8)

    first_event = archive.add(first)
    original_cells = archive.state_snapshot()["cells"]
    second_event = archive.add(second)
    updated = archive.state_snapshot()

    assert first_event["entered_cell"] is True
    assert second_event["search_state_changed"] is True
    assert updated["descriptor_model"]["revision"] == 2
    assert updated["descriptor_model"]["diversity_reference_program_ids"] == [
        first.id,
        second.id,
    ]
    assert original_cells[0] in updated["cells"]
    assert updated["descriptor_model"]["rebin_policy"] == (
        "no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots"
    )
    assert updated["descriptor_model"]["readiness"] == {
        "schema": MAP_ELITES_DESCRIPTOR_READINESS_SCHEMA,
        "stable_task_behavior_descriptor_contract": False,
        "learned_descriptor_model": False,
        "evaluator_provided_descriptor_model": False,
        "full_archive_rebin_engine": False,
        "partial_archive_rebin_engine": False,
        "descriptor_training_inputs_recorded": False,
        "restore_compatible_descriptor_revisioning": False,
        "remaining_gap": [
            "stable_task_behavior_descriptor_contract",
            "learned_descriptor_model",
            "evaluator_provided_descriptor_model",
            "full_archive_rebin_engine",
            "partial_archive_rebin_engine",
            "descriptor_training_inputs_recorded",
            "restore_compatible_descriptor_revisioning",
        ],
    }


def test_restore_state_snapshot_rejects_descriptor_model_rebin_overclaim():
    source = MAPElites()
    program = _pm(code="x=1", fitness=0.5, selection_score=0.5)
    source.add(program)
    snapshot = source.state_snapshot()
    snapshot["descriptor_model"]["rebin_policy"] = "full_rebin"

    with pytest.raises(ValueError, match="descriptor_model.rebin_policy"):
        MAPElites().restore_state_snapshot(snapshot, {program.id: program})


def test_restore_state_snapshot_accepts_legacy_descriptor_model_without_readiness():
    source = MAPElites()
    program = _pm(code="x=1", fitness=0.5, selection_score=0.5)
    source.add(program)
    snapshot = source.state_snapshot()
    del snapshot["descriptor_model"]["readiness"]

    result = MAPElites().restore_state_snapshot(snapshot, {program.id: program})

    assert result["status"] == "map_elites_state_restored"


def test_restore_state_snapshot_rejects_descriptor_readiness_overclaim():
    source = MAPElites()
    program = _pm(code="x=1", fitness=0.5, selection_score=0.5)
    source.add(program)
    snapshot = source.state_snapshot()
    snapshot["descriptor_model"]["readiness"]["learned_descriptor_model"] = True

    with pytest.raises(ValueError, match="must not claim learned_descriptor_model"):
        MAPElites().restore_state_snapshot(snapshot, {program.id: program})


def test_restore_state_snapshot_rejects_descriptor_axis_mismatch():
    source = MAPElites(
        descriptor_axes=["performance", "metric:accuracy", "diversity"]
    )
    program = Program(
        code="x=1",
        fitness=0.5,
        metrics={"accuracy": 1.0},
        evaluation={"is_valid": True},
        metadata={"normalized_metrics": {"accuracy": 1.0}},
    )
    source.add(program)

    with pytest.raises(ValueError, match="descriptor_axes"):
        MAPElites().restore_state_snapshot(source.state_snapshot(), {program.id: program})


def test_occupied_cells_nonempty():
    a = MAPElites(); a.add(_p())
    assert len(a.occupied_cells()) >= 1

def test_sample_diverse_up_to_k():
    a = MAPElites()
    for i in range(5): a.add(_p(code=f"x={i}", fitness=i*0.1))
    assert 1 <= len(a.sample_diverse(k=3)) <= 3


def test_sample_diverse_accepts_zero_and_oversized_counts():
    a = MAPElites()
    for i in range(2):
        a.add(_p(code=f"x={i}", fitness=i * 0.1))

    assert a.sample_diverse(k=0) == []
    assert len(a.sample_diverse(k=10)) <= 2


@pytest.mark.parametrize("k", ["2", True, 1.5, -1])
def test_sample_diverse_rejects_invalid_counts(k):
    a = MAPElites()
    a.add(_p())

    with pytest.raises(ValueError, match="MAP-Elites sample count"):
        a.sample_diverse(k=k)


def test_sample_diverse_excludes_program_ids():
    a = MAPElites()
    p = _p(code="x=1", fitness=0.5)
    a.add(p)
    assert a.sample_diverse(k=3, exclude_ids={p.id}) == []


def test_sample_diverse_normalizes_exclude_id_sequences():
    a = MAPElites()
    p = _p(code="x=1", fitness=0.5)
    a.add(p)

    assert a.sample_diverse(k=3, exclude_ids=[p.id, p.id]) == []
    assert a.sample_diverse(k=3, exclude_ids=(p.id,)) == []


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
    a = MAPElites()
    a.add(_p())

    with pytest.raises(ValueError, match="MAP-Elites exclude_ids"):
        a.sample_diverse(k=3, exclude_ids=exclude_ids)


def test_elite_archive_capped():
    a = MAPElites(elite_archive_size=3)
    for i in range(10): a.add(_p(code=f"x={i}", fitness=i*0.1))
    assert len(a.elite_archive()) <= 3

def test_add_reports_elite_displacement():
    a = MAPElites(bins=1, elite_archive_size=1)
    low = _p(code="x=1", fitness=0.1)
    a.add(low)
    event = a.add(_p(code="x=2", fitness=0.9))
    assert event["entered_elite"] is True
    assert event["displaced_elite_ids"] == [low.id]

def test_diversity_no_crash_on_first():
    a = MAPElites()
    a.add(_p(code="def foo(): return 42", fitness=0.5))
    assert a.best() is not None


def test_short_distinct_programs_do_not_collapse_to_default_diversity():
    a = MAPElites(bins=10)
    first = _p(code="x", fitness=0.5)
    a.add(first)

    second = _p(code="y", fitness=0.6)
    event = a.add(second)

    assert event["descriptors"]["diversity"] > 0.0


def test_empty_code_diversity_compares_workspace_structure():
    a = MAPElites()
    a.add(_p(code="", fitness=0.5))

    event = a.add(_p(code="", fitness=0.6))

    assert event["descriptors"]["diversity"] == 0.0


def test_workspace_descriptor_includes_supporting_files():
    single_file = Program(
        code="x=1",
        fitness=0.5,
        evaluation={"is_valid": True},
    )
    workspace = Program(
        files={
            "main.py": "x=1",
            "helpers/math_tools.py": "def scale(value):\n    return value * 2\n",
        },
        primary_file="main.py",
        fitness=0.5,
        evaluation={"is_valid": True},
    )

    assert single_file.code == workspace.code
    assert _descriptor_text(single_file) != _descriptor_text(workspace)
    assert "helpers/math_tools.py" in _descriptor_text(workspace)


def test_workspace_diversity_uses_supporting_files_not_only_primary_code():
    archive = MAPElites(bins=10)
    base = Program(
        files={
            "main.py": "from helper import value\nscore = value()\n",
            "helper.py": "def value():\n    return 1\n",
        },
        primary_file="main.py",
        fitness=0.5,
        evaluation={"is_valid": True},
    )
    archive.add(base)

    changed_helper = Program(
        files={
            "main.py": "from helper import value\nscore = value()\n",
            "helper.py": "def value():\n    return 999\n",
        },
        primary_file="main.py",
        fitness=0.6,
        evaluation={"is_valid": True},
    )
    event = archive.add(changed_helper)

    assert base.code == changed_helper.code
    assert event["descriptors"]["diversity"] > 0.0


def test_performance_bounds_affect_cell():
    a = MAPElites(bins=10, perf_bounds=(0.0, 100.0))
    p = _p(fitness=50.0)
    assert a._cell(p)[0] == 5


def test_selection_score_drives_replacement_and_best():
    a = MAPElites(bins=1)
    primary_best = _pm(code="x=1", fitness=0.9, selection_score=0.2)
    a.add(primary_best)

    balanced = _pm(code="x=2", fitness=0.4, selection_score=0.8)
    event = a.add(balanced)

    assert event["cell_replaced"] is True
    assert event["selection_score"] == 0.8
    assert a.best().id == balanced.id
    assert a._grid[(0, 0, 0)].id == balanced.id


def test_rejects_non_finite_fitness_even_with_finite_selection_score():
    a = MAPElites()
    program = _pm(fitness=0.5, selection_score=0.5)
    program.fitness = float("nan")
    event = a.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "non_finite_fitness"
    assert a.best() is None


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda program: setattr(program, "id", "api_key=sk-proj_archive_id_secret_1234567890\nnext"), "Program id"),  # pragma: allowlist secret
        (lambda program: setattr(program, "parent_id", "bad\nparent"), "Program parent_id"),
        (lambda program: setattr(program, "lineage", ["root", "bad\nlineage"]), r"Program lineage\[1\]"),
    ],
)
def test_add_rejects_mutated_unsafe_identity_before_archive_mutation(mutate, message):
    archive = MAPElites()
    program = _p(fitness=0.9)
    mutate(program)

    with pytest.raises(ValueError, match=message):
        archive.add(program)

    assert archive.best() is None
    assert archive.occupied_cells() == []
    assert archive.elite_archive() == []


def test_rejects_invalid_evaluation_without_archive_mutation():
    a = MAPElites()
    program = _p(fitness=1.0)
    program.evaluation = {"is_valid": False}

    event = a.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_evaluation"
    assert event["evaluation_is_valid"] is False
    assert a.best() is None


@pytest.mark.parametrize("metrics", [{"score": "bad"}, {"score": True}, {"score": Fraction(1, 2)}])
def test_invalid_evaluation_with_malformed_metrics_returns_structured_rejection(metrics):
    a = MAPElites()
    program = _p(fitness=1.0)
    program.evaluation = {"is_valid": False}
    program.metrics = metrics

    event = a.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_evaluation"
    assert event["evaluation_is_valid"] is False
    assert a.best() is None


def test_rejects_invalid_fitness_type_without_archive_mutation():
    a = MAPElites()
    program = _pm(fitness=1.0, selection_score=0.5)
    program.fitness = True
    event = a.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_fitness_type"
    assert event["selection_score"] == 0.5
    assert a.best() is None


def test_rejects_non_numeric_fitness_without_raw_type_error():
    a = MAPElites()
    program = _p(fitness=1.0)
    program.fitness = "1.0"
    event = a.add(program)

    assert event["admitted"] is False
    assert event["reason"] == "invalid_fitness_type"
    assert event["selection_score"] is None
    assert a.best() is None


@pytest.mark.parametrize("metrics", [{"score": "bad"}, {"score": True}, {"score": Fraction(1, 2)}])
def test_rejects_invalid_metric_vector_before_archive_mutation(metrics):
    a = MAPElites()
    program = _p(fitness=1.0)
    program.metrics = metrics

    with pytest.raises(ValueError, match="Program metric values"):
        a.add(program)

    assert a.best() is None
