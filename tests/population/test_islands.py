from fractions import Fraction

import pytest
from libreevolve.core.config import Config
from libreevolve.population.islands import (
    ISLAND_MIGRATION_REPLAY_SCHEMA,
    ISLAND_TOPOLOGY_POLICY_SCHEMA,
    IslandModel,
)
from libreevolve.population.program import Program

def _m(n=3): return IslandModel(Config(n_islands=n, migration_interval=5))
def _p(code="x=1", fitness=0.5):
    return Program(code=code, fitness=fitness, evaluation={"is_valid": True})
def _pm(code="x=1", fitness=0.5, selection_score=0.5):
    return Program(
        code=code,
        fitness=fitness,
        evaluation={"is_valid": True},
        metadata={"selection_score": selection_score},
    )
def _pmeta(code="x=1", fitness=0.5, generation=0, metrics=None, diversity=0.0):
    return Program(
        code=code,
        fitness=fitness,
        generation=generation,
        evaluation={"is_valid": True},
        metadata={
            "selection_score": fitness,
            "normalized_metrics": metrics or {},
            "archive_admission": {"descriptors": {"diversity": diversity}},
        },
    )

def _plineage(
    program_id,
    *,
    code,
    fitness,
    selection_score,
    parent_id=None,
    lineage=None,
    generation=0,
):
    return Program(
        id=program_id,
        code=code,
        fitness=fitness,
        generation=generation,
        parent_id=parent_id,
        lineage=list(lineage or []),
        evaluation={"is_valid": True},
        metadata={
            "selection_score": selection_score,
            "archive_admission": {"descriptors": {"diversity": 0.0}},
        },
    )

def test_best_returns_highest():
    m = _m(); m.add(_p(fitness=0.3)); m.add(_p(fitness=0.7))
    assert m.best().fitness == 0.7

def test_add_reports_island_id_and_rotates():
    m = IslandModel(Config(n_islands=2, migration_interval=5))
    first = m.add(_p(fitness=0.3))
    second = m.add(_p(fitness=0.7))
    assert first["island_id"] == 0
    assert second["island_id"] == 1


def test_island_archives_use_configured_complexity_bound():
    config = Config(
        n_islands=2,
        migration_interval=5,
        map_elites_complexity_max_chars=17,
    )
    model = IslandModel(config)

    assert [archive._complexity_max_chars for archive in model.islands] == [17, 17]


def test_island_archives_use_configured_descriptor_axes():
    config = Config(
        n_islands=2,
        migration_interval=5,
        map_elites_descriptor_axes=[
            "performance",
            "metric:accuracy",
            "candidate_metadata:archive.score",
        ],
    )
    model = IslandModel(config)

    assert [archive._descriptor_axes for archive in model.islands] == [
        (
            "performance",
            "metric:accuracy",
            "candidate_metadata:archive.score",
        ),
        (
            "performance",
            "metric:accuracy",
            "candidate_metadata:archive.score",
        ),
    ]


def test_non_admitted_add_does_not_advance_island_cursor():
    m = IslandModel(
        Config(
            n_islands=2,
            migration_interval=5,
            map_elites_bins=1,
            elite_archive_size=1,
        )
    )
    first = _pm(code="island0", fitness=0.9, selection_score=0.9)
    second = _pm(code="island1", fitness=0.8, selection_score=0.8)
    weak = _pm(code="weak", fitness=0.1, selection_score=0.1)
    replacement = _pm(code="replacement", fitness=1.0, selection_score=1.0)

    first_event = m.add(first)
    second_event = m.add(second)
    weak_event = m.add(weak)
    replacement_event = m.add(replacement)

    assert first_event["island_id"] == 0
    assert second_event["island_id"] == 1
    assert weak_event["island_id"] == 0
    assert weak_event["reason"] == "not_improving_cell"
    assert weak_event["search_state_changed"] is False
    assert weak_event["admitted"] is False
    assert replacement_event["island_id"] == 0
    assert replacement_event["reason"] == "cell_replaced"
    assert replacement_event["previous_occupant_id"] == first.id


def test_state_snapshot_persists_round_robin_cursor_after_non_admitted_attempt():
    m = IslandModel(
        Config(
            n_islands=2,
            migration_interval=5,
            map_elites_bins=1,
            elite_archive_size=1,
        )
    )
    first = _pm(code="island0", fitness=0.9, selection_score=0.9)
    second = _pm(code="island1", fitness=0.8, selection_score=0.8)
    weak = _pm(code="weak", fitness=0.1, selection_score=0.1)

    m.add(first)
    m.add(second)
    weak_event = m.add(weak)
    snapshot = m.state_snapshot()

    assert weak_event["search_state_changed"] is False
    assert snapshot["schema"] == "libreevolve.island_state.v1"
    assert snapshot["resume_status"] == (
        "snapshot_persisted_cursor_and_full_archive_restore_supported"
    )
    assert snapshot["cursor_policy"] == "advance_only_on_search_state_changed"
    assert snapshot["n_islands"] == 2
    assert snapshot["next_island_id"] == 0
    assert snapshot["archive_sequence"] == 3
    assert snapshot["migration_sequence"] == 0
    assert snapshot["metric_sample_index"] == 0
    assert snapshot["frontier_sample_index"] == 0
    assert snapshot["lineage_sample_index"] == 0
    assert snapshot["topology_policy"] == {
        "schema": ISLAND_TOPOLOGY_POLICY_SCHEMA,
        "status": "configured_synchronous_ring_topology",
        "policy": "config_n_islands_controls_local_synchronous_ring_migration_default_five",
        "configured_n_islands": 2,
        "default_n_islands": 5,
        "island_count_configurable": True,
        "migration_topology": "ring",
        "migration_execution": "synchronous_local_generation_boundary",
        "adaptive_island_count_supported": False,
        "non_ring_topologies_supported": False,
        "alphaevolve_policy_ready": False,
        "limitations": [
            "no_adaptive_island_count_policy",
            "no_non_ring_migration_topology",
            "no_topology_specific_ablation_evidence",
            "not_claimed_as_alphaevolve_identical_policy",
        ],
    }
    assert snapshot["migration_replay"] == {
        "schema": ISLAND_MIGRATION_REPLAY_SCHEMA,
        "status": "not_applied_as_restore_engine",
        "policy": (
            "archive_contents_snapshot_restores_current_placements_without_replaying_migration_events"
        ),
        "migration_sequence": 0,
        "replay_engine_supported": False,
        "archive_contents_restore_covers_current_placements": True,
        "limitations": [
            "migration_event_order_not_applied_as_restore_engine",
            "migration_skip_events_not_reconstructed",
            "controller_pending_work_not_restored",
        ],
    }
    assert snapshot["archive_sequence_by_program_id"] == {
        first.id: 1,
        second.id: 2,
    }
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


def test_restore_cursor_state_applies_next_island_and_sequences():
    source = IslandModel(Config(n_islands=2, migration_interval=5))
    first = _pm(code="island0", fitness=0.9, selection_score=0.9)
    second = _pm(code="island1", fitness=0.8, selection_score=0.8)
    source.add(first)
    source.add(second)
    snapshot = source.state_snapshot()
    snapshot["metric_sample_index"] = 4
    snapshot["frontier_sample_index"] = 5
    snapshot["lineage_sample_index"] = 6

    restored = IslandModel(Config(n_islands=2, migration_interval=5))
    result = restored.restore_cursor_state(snapshot)
    next_program = _pm(code="next", fitness=1.0, selection_score=1.0)
    event = restored.add(next_program)

    assert result["status"] == "cursor_state_restored"
    assert result["archive_contents_restored"] is False
    assert result["full_archive_restore_required"] is True
    assert result["topology_policy"] == snapshot["topology_policy"]
    assert result["migration_replay"] == snapshot["migration_replay"]
    assert event["island_id"] == snapshot["next_island_id"]
    assert event["archive_sequence"] == snapshot["archive_sequence"] + 1
    assert restored.state_snapshot()["metric_sample_index"] == 4
    assert restored.state_snapshot()["frontier_sample_index"] == 5
    assert restored.state_snapshot()["lineage_sample_index"] == 6
    assert restored.state_snapshot()["archive_sequence_by_program_id"][first.id] == 1


def test_restore_archive_state_rehydrates_cells_and_elites():
    source = IslandModel(
        Config(n_islands=2, migration_interval=5, map_elites_bins=1)
    )
    first = _pm(code="island0", fitness=0.9, selection_score=0.9)
    second = _pm(code="island1", fitness=0.8, selection_score=0.8)
    source.add(first)
    source.add(second)
    snapshot = source.state_snapshot()

    restored = IslandModel(
        Config(n_islands=2, migration_interval=5, map_elites_bins=1)
    )
    result = restored.restore_archive_state(
        snapshot,
        {first.id: first, second.id: second},
    )

    assert snapshot["archive_contents"]["schema"] == (
        "libreevolve.island_archive_contents.v1"
    )
    assert result["status"] == "archive_state_restored"
    assert result["archive_contents_restored"] is True
    assert result["full_archive_restore_required"] is False
    assert result["restored_islands"] == [
        {
            "island_id": 0,
            "status": "map_elites_state_restored",
            "occupied_cell_count": 1,
            "elite_count": 1,
            "pareto_frontier_count": 0,
            "metric_cell_archive_count": 0,
        },
        {
            "island_id": 1,
            "status": "map_elites_state_restored",
            "occupied_cell_count": 1,
            "elite_count": 1,
            "pareto_frontier_count": 0,
            "metric_cell_archive_count": 0,
        },
    ]
    assert restored.best().id == first.id
    assert {
        program.id for program in restored.sample_diverse(k=2, strategy="random")
    } == {first.id, second.id}


def test_restore_cursor_state_rejects_mismatched_island_count():
    source = IslandModel(Config(n_islands=2, migration_interval=5))
    snapshot = source.state_snapshot()
    restored = IslandModel(Config(n_islands=3, migration_interval=5))

    with pytest.raises(ValueError, match="n_islands"):
        restored.restore_cursor_state(snapshot)


def test_restore_cursor_state_rejects_migration_replay_overclaim():
    source = IslandModel(Config(n_islands=2, migration_interval=5))
    snapshot = source.state_snapshot()
    snapshot["migration_replay"]["replay_engine_supported"] = True
    restored = IslandModel(Config(n_islands=2, migration_interval=5))

    with pytest.raises(ValueError, match="must not claim replay engine support"):
        restored.restore_cursor_state(snapshot)


def test_restore_cursor_state_rejects_topology_policy_overclaim():
    source = IslandModel(Config(n_islands=2, migration_interval=5))
    snapshot = source.state_snapshot()
    snapshot["topology_policy"]["alphaevolve_policy_ready"] = True
    restored = IslandModel(Config(n_islands=2, migration_interval=5))

    with pytest.raises(ValueError, match="must not claim AlphaEvolve parity"):
        restored.restore_cursor_state(snapshot)


def test_sample_exploit_returns_best():
    m = _m(); m.add(_p(fitness=0.3)); m.add(_p(fitness=0.9))
    assert m.sample("exploit").fitness == 0.9

def test_sample_exploit_uses_selection_score():
    m = _m()
    primary_best = _pm(code="x=1", fitness=0.9, selection_score=0.2)
    balanced = _pm(code="x=2", fitness=0.4, selection_score=0.8)
    m.add(primary_best)
    m.add(balanced)
    assert m.sample("exploit").id == balanced.id
    assert m.best().id == balanced.id

def test_sample_metric_uses_individual_metric_leaders():
    m = _m()
    fast = _pmeta(code="fast", fitness=0.4, metrics={"speed": 0.9, "quality": 0.2})
    good = _pmeta(code="good", fitness=0.5, metrics={"speed": 0.1, "quality": 0.8})
    m.add(fast)
    m.add(good)
    assert m.sample("metric").id == good.id
    assert m.last_sample_metadata()["target_metric"] == "quality"
    assert m.sample("metric").id == fast.id
    assert m.last_sample_metadata()["target_metric"] == "speed"
    assert m.sample("metric").id == good.id


def test_metric_sampling_cycles_configured_metric_targets_primary_first():
    m = IslandModel(
        Config(n_islands=1, migration_interval=5),
        metric_order=["primary", "latency"],
    )
    primary_leader = _pmeta(
        code="primary",
        fitness=0.9,
        metrics={"primary": 0.9, "latency": 0.1},
    )
    latency_leader = _pmeta(
        code="latency",
        fitness=0.1,
        metrics={"primary": 0.1, "latency": 0.95},
    )
    m.add(latency_leader)
    m.add(primary_leader)

    assert m.sample("metric").id == primary_leader.id
    assert m.last_sample_metadata() == {
        "strategy": "metric",
        "selected_program_id": primary_leader.id,
        "target_metric": "primary",
        "metric_target_index": 0,
        "metric_target_count": 2,
    }
    assert m.sample("metric").id == latency_leader.id
    assert m.last_sample_metadata()["target_metric"] == "latency"
    assert m.sample("metric").id == primary_leader.id
    assert [p.id for p in m.sample_diverse(k=1, strategy="metric")] == [
        primary_leader.id
    ]
    assert [p.id for p in m.sample_diverse(k=2, strategy="metric")] == [
        primary_leader.id,
        latency_leader.id,
    ]
    assert m.last_sample_metadata() == {
        "strategy": "metric",
        "sample_kind": "diverse",
        "requested_count": 2,
        "selected_count": 2,
        "selected_program_ids": [primary_leader.id, latency_leader.id],
        "excluded_count": 0,
        "target_metrics": [
            {"metric": "primary", "program_id": primary_leader.id},
            {"metric": "latency", "program_id": latency_leader.id},
        ],
    }


def test_metric_sampling_ignores_out_of_range_normalized_metrics():
    m = IslandModel(
        Config(n_islands=1, migration_interval=5),
        metric_order=["score"],
    )
    honest = _pmeta(code="honest", fitness=0.9, metrics={"score": 0.9})
    poisoned = _pmeta(
        code="poisoned",
        fitness=0.1,
        metrics={"score": 999.0},
    )
    m.add(poisoned)
    m.add(honest)

    assert m.sample("metric").id == honest.id
    assert [p.id for p in m.sample_diverse(k=2, strategy="metric")] == [
        honest.id,
        poisoned.id,
    ]


def test_metric_sampling_ignores_undeclared_normalized_metrics():
    m = IslandModel(
        Config(n_islands=1, migration_interval=5),
        metric_order=["score"],
    )
    honest = _pmeta(code="honest", fitness=0.8, metrics={"score": 0.8})
    undeclared = _pmeta(
        code="undeclared",
        fitness=0.1,
        metrics={"score": 0.1, "plugin_quality": 1.0},
    )
    m.add(undeclared)
    m.add(honest)

    assert m.sample("metric").id == honest.id
    assert [p.id for p in m.sample_diverse(k=1, strategy="metric")] == [honest.id]


def test_frontier_parent_sampling_cycles_non_dominated_programs():
    m = IslandModel(
        Config(n_islands=1, migration_interval=5),
        metric_order=["accuracy", "latency"],
    )
    accuracy_leader = _pmeta(
        code="accuracy",
        fitness=0.70,
        metrics={"accuracy": 0.95, "latency": 0.20},
    )
    latency_leader = _pmeta(
        code="latency",
        fitness=0.60,
        metrics={"accuracy": 0.20, "latency": 0.95},
    )
    balanced = _pmeta(
        code="balanced",
        fitness=0.80,
        metrics={"accuracy": 0.80, "latency": 0.80},
    )
    dominated = _pmeta(
        code="dominated",
        fitness=0.90,
        metrics={"accuracy": 0.50, "latency": 0.50},
    )
    for program in (dominated, latency_leader, accuracy_leader, balanced):
        m.add(program)

    assert [m.sample("frontier").id for _ in range(4)] == [
        balanced.id,
        accuracy_leader.id,
        latency_leader.id,
        balanced.id,
    ]
    assert m.last_sample_metadata() == {
        "strategy": "frontier",
        "selected_program_id": balanced.id,
        "frontier_index": 0,
        "frontier_size": 3,
        "metric_order": ["accuracy", "latency"],
    }


def test_frontier_sampling_includes_pareto_only_archive_retention():
    m = IslandModel(
        Config(n_islands=1, migration_interval=5, map_elites_bins=1, elite_archive_size=2),
        metric_order=["accuracy", "latency"],
    )
    balanced = _pmeta(
        code="balanced",
        fitness=0.90,
        metrics={"accuracy": 0.70, "latency": 0.70},
    )
    latency = _pmeta(
        code="latency",
        fitness=0.80,
        metrics={"accuracy": 0.70, "latency": 0.95},
    )
    accuracy = _pmeta(
        code="accuracy",
        fitness=0.10,
        metrics={"accuracy": 0.95, "latency": 0.70},
    )
    m.add(balanced)
    m.add(latency)
    event = m.add(accuracy)

    assert event["reason"] == "pareto_frontier_only"
    assert event["pareto_frontier_retained"] is True
    assert [program.id for program in m.sample_diverse(k=2, strategy="frontier")] == [
        latency.id,
        accuracy.id,
    ]
    assert m.last_sample_metadata() == {
        "strategy": "frontier",
        "sample_kind": "diverse",
        "requested_count": 2,
        "selected_count": 2,
        "selected_program_ids": [latency.id, accuracy.id],
        "excluded_count": 0,
        "frontier_size": 2,
        "metric_order": ["accuracy", "latency"],
    }


def test_frontier_inspiration_sampling_uses_non_dominated_programs_with_exclusions():
    m = IslandModel(
        Config(n_islands=1, migration_interval=5),
        metric_order=["accuracy", "latency"],
    )
    accuracy_leader = _pmeta(
        code="accuracy",
        fitness=0.70,
        metrics={"accuracy": 0.95, "latency": 0.20},
    )
    latency_leader = _pmeta(
        code="latency",
        fitness=0.60,
        metrics={"accuracy": 0.20, "latency": 0.95},
    )
    balanced = _pmeta(
        code="balanced",
        fitness=0.80,
        metrics={"accuracy": 0.80, "latency": 0.80},
    )
    dominated = _pmeta(
        code="dominated",
        fitness=0.90,
        metrics={"accuracy": 0.50, "latency": 0.50},
    )
    for program in (dominated, latency_leader, accuracy_leader, balanced):
        m.add(program)

    selected = m.sample_diverse(
        k=3, exclude_ids={balanced.id}, strategy="frontier"
    )

    assert [program.id for program in selected] == [
        dominated.id,
        accuracy_leader.id,
        latency_leader.id,
    ]
    assert m.last_sample_metadata() == {
        "strategy": "frontier",
        "sample_kind": "diverse",
        "requested_count": 3,
        "selected_count": 3,
        "selected_program_ids": [
            dominated.id,
            accuracy_leader.id,
            latency_leader.id,
        ],
        "excluded_count": 1,
        "frontier_size": 3,
        "metric_order": ["accuracy", "latency"],
    }


def test_frontier_sampling_falls_back_without_declared_metrics():
    m = _m()
    weaker = _pmeta(code="weaker", fitness=0.4)
    stronger = _pmeta(code="stronger", fitness=0.9)
    m.add(weaker)
    m.add(stronger)

    assert m.sample("frontier").id == stronger.id
    assert m.last_sample_metadata() == {
        "strategy": "frontier",
        "fallback_strategy": "exploit",
        "selected_program_id": stronger.id,
        "frontier_size": 0,
        "metric_order": [],
    }
    assert [p.id for p in m.sample_diverse(k=1, strategy="frontier")] == [
        stronger.id
    ]
    assert m.last_sample_metadata()["fallback_strategy"] == "selection"


def test_lineage_parent_sampling_cycles_best_root_representatives():
    m = IslandModel(Config(n_islands=1, migration_interval=5))
    root_a = _plineage(
        "root-a",
        code="root_a",
        fitness=0.20,
        selection_score=0.20,
    )
    weak_child_a = _plineage(
        "weak-child-a",
        code="weak_child_a",
        fitness=0.40,
        selection_score=0.40,
        parent_id=root_a.id,
        lineage=[root_a.id],
        generation=1,
    )
    best_child_a = _plineage(
        "best-child-a",
        code="best_child_a",
        fitness=0.90,
        selection_score=0.90,
        parent_id=root_a.id,
        lineage=[root_a.id],
        generation=1,
    )
    root_b = _plineage(
        "root-b",
        code="root_b",
        fitness=0.70,
        selection_score=0.70,
    )
    child_b = _plineage(
        "child-b",
        code="child_b",
        fitness=0.50,
        selection_score=0.50,
        parent_id=root_b.id,
        lineage=[root_b.id],
        generation=1,
    )
    for program in (root_a, weak_child_a, best_child_a, root_b, child_b):
        m.add(program)

    assert [m.sample("lineage").id for _ in range(3)] == [
        best_child_a.id,
        root_b.id,
        best_child_a.id,
    ]
    assert m.last_sample_metadata() == {
        "strategy": "lineage",
        "selected_program_id": best_child_a.id,
        "lineage_root_id": root_a.id,
        "lineage_index": 0,
        "lineage_count": 2,
    }
    assert m.state_snapshot()["lineage_sample_index"] == 3


def test_lineage_inspiration_sampling_best_per_root_then_selection_fill():
    m = IslandModel(Config(n_islands=1, migration_interval=5))
    root_a = _plineage(
        "root-a",
        code="root_a",
        fitness=0.20,
        selection_score=0.20,
    )
    best_child_a = _plineage(
        "best-child-a",
        code="best_child_a",
        fitness=0.90,
        selection_score=0.90,
        parent_id=root_a.id,
        lineage=[root_a.id],
        generation=1,
    )
    weaker_child_a = _plineage(
        "weaker-child-a",
        code="weaker_child_a",
        fitness=0.60,
        selection_score=0.60,
        parent_id=root_a.id,
        lineage=[root_a.id],
        generation=1,
    )
    root_b = _plineage(
        "root-b",
        code="root_b",
        fitness=0.70,
        selection_score=0.70,
    )
    root_c = _plineage(
        "root-c",
        code="root_c",
        fitness=0.40,
        selection_score=0.40,
    )
    for program in (root_a, best_child_a, weaker_child_a, root_b, root_c):
        m.add(program)

    selected = m.sample_diverse(
        k=4,
        exclude_ids={best_child_a.id},
        strategy="lineage",
    )

    assert [program.id for program in selected] == [
        root_b.id,
        weaker_child_a.id,
        root_c.id,
        root_a.id,
    ]
    assert m.last_sample_metadata() == {
        "strategy": "lineage",
        "sample_kind": "diverse",
        "requested_count": 4,
        "selected_count": 4,
        "selected_program_ids": [
            root_b.id,
            weaker_child_a.id,
            root_c.id,
            root_a.id,
        ],
        "excluded_count": 1,
        "lineages": [
            {"lineage_root_id": root_b.id, "program_id": root_b.id},
            {"lineage_root_id": root_a.id, "program_id": weaker_child_a.id},
            {"lineage_root_id": root_c.id, "program_id": root_c.id},
        ],
    }


def test_sample_novelty_and_recency_strategies():
    m = _m()
    old_novel = _pmeta(code="novel", fitness=0.3, generation=1, diversity=0.9)
    new_plain = _pmeta(code="recent", fitness=0.4, generation=5, diversity=0.1)
    m.add(old_novel)
    m.add(new_plain)
    assert m.sample("novelty").id == old_novel.id
    assert m.sample("recency").id == new_plain.id


def test_elite_only_programs_resurface_through_retained_archive_strategies():
    m = IslandModel(
        Config(n_islands=1, migration_interval=5, map_elites_bins=1),
        metric_order=["score"],
    )
    occupied = _pmeta(
        code="occupied",
        fitness=0.9,
        generation=1,
        metrics={"score": 0.1},
        diversity=0.1,
    )
    elite_only = _pmeta(
        code="elite_only",
        fitness=0.1,
        generation=9,
        metrics={"score": 0.95},
        diversity=0.95,
    )

    occupied_event = m.add(occupied)
    elite_event = m.add(elite_only)

    assert occupied_event["sampling_eligible"] is True
    assert elite_event["reason"] == "elite_only"
    assert elite_event["sampling_eligible"] is False
    assert m.sample("explore").id == occupied.id
    assert m.sample("metric").id == elite_only.id
    assert m.sample("novelty").id == elite_only.id
    assert m.sample("recency").id == elite_only.id
    assert [p.id for p in m.sample_diverse(k=1, strategy="metric")] == [
        elite_only.id
    ]
    assert [p.id for p in m.sample_diverse(k=1, strategy="novelty")] == [
        elite_only.id
    ]
    assert [p.id for p in m.sample_diverse(k=1, strategy="recency")] == [
        elite_only.id
    ]
    assert [p.id for p in m.sample_diverse(k=2, strategy="selection")] == [
        occupied.id,
        elite_only.id,
    ]
    assert [p.id for p in m.sample_diverse(k=2, strategy="mixed")] == [
        elite_only.id,
        occupied.id,
    ]
    assert [p.id for p in m.sample_diverse(k=2, strategy="random")] == [
        occupied.id
    ]


def test_recency_uses_archive_sequence_before_score_for_same_generation():
    m = IslandModel(Config(n_islands=1, migration_interval=5))
    older_high_score = _pmeta(code="older", fitness=0.9, generation=0)
    newer_low_score = _pmeta(code="newer", fitness=0.1, generation=0)

    first = m.add(older_high_score)
    second = m.add(newer_low_score)

    assert first["archive_sequence"] == 1
    assert second["archive_sequence"] == 2
    assert older_high_score.metadata["archive_sequence"] == 1
    assert newer_low_score.metadata["archive_sequence"] == 2
    assert m.sample("recency").id == newer_low_score.id
    assert [p.id for p in m.sample_diverse(k=2, strategy="recency")] == [
        newer_low_score.id,
        older_high_score.id,
    ]


def test_recency_ignores_mutated_archive_sequence_metadata():
    m = IslandModel(Config(n_islands=1, migration_interval=5))
    older_high_score = _pmeta(code="older", fitness=0.9, generation=0)
    newer_low_score = _pmeta(code="newer", fitness=0.1, generation=0)
    m.add(older_high_score)
    m.add(newer_low_score)

    older_high_score.metadata["archive_sequence"] = 999999

    assert m.sample("recency").id == newer_low_score.id
    assert [p.id for p in m.sample_diverse(k=2, strategy="recency")] == [
        newer_low_score.id,
        older_high_score.id,
    ]


@pytest.mark.parametrize("generation", ["bad", -1, True])
def test_archive_rejects_mutated_invalid_generation_before_sampling(generation):
    m = IslandModel(Config(n_islands=1, migration_interval=5))
    program = _pmeta(code="bad-generation", fitness=0.5)
    program.generation = generation

    with pytest.raises(
        ValueError, match="Program generation must be a non-negative integer"
    ):
        m.add(program)

    assert m.sample("recency") is None


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda program: setattr(program, "id", "api_key=sk-proj_island_id_secret_1234567890\nnext"), "Program id"),  # pragma: allowlist secret
        (lambda program: setattr(program, "parent_id", "bad\nparent"), "Program parent_id"),
        (lambda program: setattr(program, "lineage", ["root", "bad\nlineage"]), r"Program lineage\[1\]"),
    ],
)
def test_archive_rejects_mutated_unsafe_identity_before_sampling(mutate, message):
    m = IslandModel(Config(n_islands=2, migration_interval=5))
    program = _pmeta(code="bad-identity", fitness=0.5)
    mutate(program)

    with pytest.raises(ValueError, match=message):
        m.add(program)

    assert m.best() is None
    assert m.sample("exploit") is None
    assert m._sequence == 0
    assert m._current == 0


@pytest.mark.parametrize("metrics", [{"score": "bad"}, {"score": True}, {"score": Fraction(1, 2)}])
def test_archive_rejects_mutated_invalid_metrics_before_sampling(metrics):
    m = IslandModel(Config(n_islands=1, migration_interval=5))
    program = _pmeta(code="bad-metrics", fitness=0.5)
    program.metrics = metrics

    with pytest.raises(ValueError, match="Program metric values"):
        m.add(program)

    assert m.sample("exploit") is None


def test_migration_copies_not_moves():
    m = IslandModel(Config(n_islands=2, migration_ratio=1.0, elite_archive_size=10))
    m.islands[0].add(_p(fitness=1.0))
    before = len(m.islands[0].occupied_cells())
    events = m.migrate()
    assert len(m.islands[0].occupied_cells()) == before
    assert m.islands[1].best() is not None
    assert events[0]["identity_policy"] == "canonical_id_reference"
    assert events[0]["clone_id"] is None

def test_zero_migration_ratio_selects_no_migrants():
    m = IslandModel(Config(n_islands=2, migration_ratio=0.0, elite_archive_size=10))
    m.islands[0].add(_p(fitness=1.0))
    assert m.migrate() == []
    assert m.islands[1].best() is None


def test_migration_records_canonical_reference_placements():
    m = IslandModel(Config(n_islands=2, migration_ratio=1.0, elite_archive_size=10))
    p = _p(code="x=1", fitness=1.0)
    m.islands[0].add(p)

    events = m.migrate()

    assert events == [
        {
            "migration_sequence": 1,
            "program_id": p.id,
            "canonical_program_id": p.id,
            "source_island": 0,
            "target_island": 1,
            "identity_policy": "canonical_id_reference",
            "clone_id": None,
            "admitted": True,
            "reason": "empty_cell",
            "cell": events[0]["cell"],
            "selection_score": 1.0,
            "objective_vector": None,
        }
    ]
    assert m.islands[1].best() is p
    assert p.metadata["migration_placements"] == events

    repeated = m.migrate()

    assert {event["reason"] for event in repeated} == {"already_present"}
    assert p.metadata["migration_placements"] == events

def test_sample_diverse_returns_list():
    m = _m()
    for i in range(5): m.add(_p(code=f"x={i}", fitness=i*0.1))
    samples = m.sample_diverse(k=3)
    assert isinstance(samples, list) and len(samples) <= 3


def test_sample_diverse_accepts_zero_and_oversized_counts():
    m = _m()
    for i in range(2):
        m.add(_p(code=f"x={i}", fitness=i * 0.1))

    assert m.sample_diverse(k=0) == []
    assert len(m.sample_diverse(k=10)) <= 2


@pytest.mark.parametrize("k", ["2", True, 1.5, -1])
def test_sample_diverse_rejects_invalid_counts(k):
    m = _m()
    m.add(_p())

    with pytest.raises(ValueError, match="island sample count"):
        m.sample_diverse(k=k)

def test_sample_diverse_excludes_program_ids():
    m = _m()
    p = _p(code="x=1", fitness=0.5)
    m.add(p)
    assert m.sample_diverse(k=3, exclude_ids={p.id}) == []


def test_sample_diverse_normalizes_exclude_id_sequences():
    m = _m()
    p = _p(code="x=1", fitness=0.5)
    m.add(p)

    assert m.sample_diverse(k=3, exclude_ids=[p.id, p.id]) == []
    assert m.sample_diverse(k=3, exclude_ids=(p.id,)) == []


class _ExcludesEverything:
    def __contains__(self, item):
        return True


@pytest.mark.parametrize(
    "exclude_ids",
    [
        "program-id",
        {"program-id": True},
        _ExcludesEverything(),
        {1},
        ["bad id"],
        ["api_key=sk-proj_exclude_secret_1234567890"],  # pragma: allowlist secret
    ],
)
def test_sample_diverse_rejects_invalid_exclude_ids(exclude_ids):
    m = _m()
    m.add(_p())

    with pytest.raises(ValueError, match="island exclude_ids"):
        m.sample_diverse(k=3, exclude_ids=exclude_ids)


def test_sample_diverse_deduplicates_migrated_program_ids():
    m = IslandModel(Config(n_islands=2, migration_ratio=1.0, elite_archive_size=10))
    p = _p(code="x=1", fitness=1.0)
    m.islands[0].add(p)
    m.migrate()
    samples = m.sample_diverse(k=10)
    assert [sample.id for sample in samples] == [p.id]

def test_sample_diverse_selection_metric_novelty_recency_strategies():
    m = _m()
    top = _pmeta(code="top", fitness=0.9, generation=1, metrics={"score": 0.9}, diversity=0.2)
    metric = _pmeta(code="metric", fitness=0.4, generation=2, metrics={"other": 0.95}, diversity=0.3)
    novel = _pmeta(code="novel", fitness=0.3, generation=3, metrics={"score": 0.2}, diversity=0.95)
    recent = _pmeta(code="recent", fitness=0.2, generation=9, metrics={"score": 0.1}, diversity=0.1)
    for program in (top, metric, novel, recent):
        m.add(program)

    assert [p.id for p in m.sample_diverse(k=2, strategy="selection")] == [top.id, metric.id]
    assert {p.id for p in m.sample_diverse(k=2, strategy="metric")} == {top.id, metric.id}
    assert m.sample_diverse(k=1, strategy="novelty")[0].id == novel.id
    assert m.sample_diverse(k=1, strategy="recency")[0].id == recent.id
    mixed = m.sample_diverse(k=3, strategy="mixed")
    assert len({p.id for p in mixed}) == 3


def test_mixed_inspiration_strategy_is_documented_priority_cascade():
    m = IslandModel(
        Config(n_islands=1, migration_interval=5),
        metric_order=["score"],
    )
    metric_leader = _pmeta(
        code="metric",
        fitness=0.5,
        metrics={"score": 0.9},
        diversity=0.1,
    )
    novel = _pmeta(
        code="novel",
        fitness=0.4,
        metrics={"score": 0.2},
        diversity=0.95,
    )
    selection_leader = _pmeta(
        code="selection",
        fitness=0.8,
        metrics={"score": 0.3},
        diversity=0.2,
    )
    for program in (selection_leader, novel, metric_leader):
        m.add(program)

    for _ in range(5):
        assert [p.id for p in m.sample_diverse(k=1, strategy="mixed")] == [
            metric_leader.id
        ]
        assert [p.id for p in m.sample_diverse(k=2, strategy="mixed")] == [
            metric_leader.id,
            novel.id,
        ]
        assert [p.id for p in m.sample_diverse(k=3, strategy="mixed")] == [
            metric_leader.id,
            novel.id,
            selection_leader.id,
        ]
    excluded = m.sample_diverse(
        k=3, exclude_ids={metric_leader.id}, strategy="mixed"
    )
    assert metric_leader.id not in {program.id for program in excluded}


def test_ring_topology():
    m = IslandModel(Config(n_islands=3, migration_ratio=1.0, elite_archive_size=10))
    m.islands[0].add(_p(code="i0", fitness=1.0))
    m.migrate()
    assert m.islands[1].best() is not None
    assert m.islands[2].best() is None  # 0 does not reach 2 directly

def test_migration_snapshot_prevents_cascade():
    """With pre-populated islands, island 0 should not reach island 2 in one migrate()."""
    m = IslandModel(Config(n_islands=3, migration_ratio=1.0, elite_archive_size=10))
    m.islands[0].add(_p(code="i0", fitness=1.0))
    m.islands[1].add(_p(code="i1", fitness=0.5))
    m.migrate()
    # Island 2 should get island 1's original program (fitness 0.5), not island 0's (fitness 1.0)
    best2 = m.islands[2].best()
    assert best2 is not None and best2.fitness == 0.5
