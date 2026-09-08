from __future__ import annotations
import math, random
import copy
from libreevolve.core.config import Config
from libreevolve.population.map_elites import MAPElites, _selection_key
from libreevolve.population.program import (
    Program,
    validate_program_identity,
    validate_program_metrics,
)
from libreevolve.population.sampling import validate_exclude_ids, validate_sample_count

ISLAND_STATE_RESUME_STATUS_LEGACY_CURSOR_ONLY = (
    "snapshot_persisted_cursor_restore_available_full_archive_restore_not_implemented"
)
ISLAND_STATE_RESUME_STATUS_RESTORE_SUPPORTED = (
    "snapshot_persisted_cursor_and_full_archive_restore_supported"
)
ISLAND_STATE_ACCEPTED_RESUME_STATUSES = {
    ISLAND_STATE_RESUME_STATUS_LEGACY_CURSOR_ONLY,
    ISLAND_STATE_RESUME_STATUS_RESTORE_SUPPORTED,
}
ISLAND_ARCHIVE_CONTENTS_RESTORE_STATUS = (
    "snapshot_persisted_full_archive_restore_supported"
)
ISLAND_MIGRATION_REPLAY_SCHEMA = "libreevolve.island_migration_replay_policy.v1"
ISLAND_MIGRATION_REPLAY_STATUS = "not_applied_as_restore_engine"
ISLAND_MIGRATION_REPLAY_POLICY = (
    "archive_contents_snapshot_restores_current_placements_without_replaying_migration_events"
)
ISLAND_TOPOLOGY_POLICY_SCHEMA = "libreevolve.island_topology_policy.v1"
ISLAND_TOPOLOGY_STATUS = "configured_synchronous_ring_topology"
ISLAND_TOPOLOGY_POLICY = (
    "config_n_islands_controls_local_synchronous_ring_migration_default_five"
)


class IslandModel:
    """Configurable independent MAP-Elites archives with ring-topology migration.

    Inspired by island population models; this is a synchronous local archive
    rotation and migration policy.
    """

    def __init__(
        self,
        config: Config,
        perf_bounds: tuple[float, float] = (0.0, 1.0),
        metric_order: list[str] | None = None,
        rng: random.Random | None = None,
    ):
        self.n_islands = config.n_islands
        self._migration_ratio = config.migration_ratio
        self._metric_order = list(metric_order or [])
        self._rng = rng if rng is not None else random.Random()
        self._sequence = 0
        self._archive_sequences: dict[str, int] = {}
        self._migration_sequence = 0
        self._metric_sample_index = 0
        self._frontier_sample_index = 0
        self._lineage_sample_index = 0
        self._last_sample_metadata: dict = {}
        self.islands: list[MAPElites] = [
            MAPElites(
                bins=config.map_elites_bins,
                elite_archive_size=config.elite_archive_size,
                perf_bounds=perf_bounds,
                complexity_max_chars=config.map_elites_complexity_max_chars,
                descriptor_axes=config.map_elites_descriptor_axes,
                metric_order=self._metric_order,
                rng=self._rng,
            )
            for _ in range(self.n_islands)
        ]
        self._current = 0

    def add(self, program: Program) -> dict:
        validate_program_identity(program.id, program.parent_id, program.lineage)
        _validate_program_generation(program)
        program.metrics = validate_program_metrics(program.metrics)
        self._sequence += 1
        program.metadata = dict(program.metadata)
        program.metadata["archive_sequence"] = self._sequence
        island_id = self._current
        event = self.islands[island_id].add(program)
        event["island_id"] = island_id
        event["archive_sequence"] = self._sequence
        if event.get("search_state_changed") is True:
            self._archive_sequences[program.id] = self._sequence
            self._current = (self._current + 1) % self.n_islands
        return event

    def sample(self, strategy: str = "exploit") -> Program | None:
        self._last_sample_metadata = {"strategy": strategy}
        if strategy == "exploit":
            cands = [i.best() for i in self.islands if i.best()]
            selected = max(cands, key=_selection_key) if cands else None
            self._record_sample_metadata(strategy, selected)
            return selected
        if strategy == "explore":
            pool = [p for i in self.islands for p in i.occupied_cells()]
            selected = self._rng.choice(pool) if pool else None
            self._record_sample_metadata(strategy, selected)
            return selected
        if strategy == "metric":
            entries = _metric_leader_entries(self._retained_programs(), self._metric_order)
            if not entries:
                selected = self.sample("exploit")
                self._last_sample_metadata = {
                    "strategy": strategy,
                    "fallback_strategy": "exploit",
                    "selected_program_id": selected.id if selected is not None else None,
                    "target_metric": None,
                    "metric_target_count": 0,
                }
                return selected
            target_index = self._metric_sample_index % len(entries)
            self._metric_sample_index += 1
            target_metric, selected = entries[target_index]
            self._last_sample_metadata = {
                "strategy": strategy,
                "selected_program_id": selected.id,
                "target_metric": target_metric,
                "metric_target_index": target_index,
                "metric_target_count": len(entries),
            }
            return selected
        if strategy == "frontier":
            frontier = _frontier_programs(
                self._retained_programs(), self._metric_order
            )
            if not frontier:
                selected = self.sample("exploit")
                self._last_sample_metadata = {
                    "strategy": strategy,
                    "fallback_strategy": "exploit",
                    "selected_program_id": selected.id if selected is not None else None,
                    "frontier_size": 0,
                    "metric_order": list(self._metric_order),
                }
                return selected
            target_index = self._frontier_sample_index % len(frontier)
            self._frontier_sample_index += 1
            selected = frontier[target_index]
            self._last_sample_metadata = {
                "strategy": strategy,
                "selected_program_id": selected.id,
                "frontier_index": target_index,
                "frontier_size": len(frontier),
                "metric_order": list(self._metric_order),
            }
            return selected
        if strategy == "lineage":
            representatives = _lineage_representatives(self._retained_programs())
            if not representatives:
                selected = self.sample("exploit")
                self._last_sample_metadata = {
                    "strategy": strategy,
                    "fallback_strategy": "exploit",
                    "selected_program_id": selected.id if selected is not None else None,
                    "lineage_count": 0,
                }
                return selected
            target_index = self._lineage_sample_index % len(representatives)
            self._lineage_sample_index += 1
            lineage_root_id, selected = representatives[target_index]
            self._last_sample_metadata = {
                "strategy": strategy,
                "selected_program_id": selected.id,
                "lineage_root_id": lineage_root_id,
                "lineage_index": target_index,
                "lineage_count": len(representatives),
            }
            return selected
        if strategy == "novelty":
            pool = self._retained_programs()
            selected = max(pool, key=_novelty_key) if pool else None
            self._record_sample_metadata(strategy, selected)
            return selected
        if strategy == "recency":
            pool = self._retained_programs()
            selected = max(pool, key=self._recency_key) if pool else None
            self._record_sample_metadata(strategy, selected)
            return selected
        raise ValueError(f"Unknown strategy: {strategy!r}")

    def last_sample_metadata(self) -> dict:
        return dict(self._last_sample_metadata)

    def state_snapshot(self) -> dict:
        return {
            "schema": "libreevolve.island_state.v1",
            "resume_status": ISLAND_STATE_RESUME_STATUS_RESTORE_SUPPORTED,
            "cursor_policy": "advance_only_on_search_state_changed",
            "n_islands": self.n_islands,
            "next_island_id": self._current,
            "archive_sequence": self._sequence,
            "migration_sequence": self._migration_sequence,
            "metric_sample_index": self._metric_sample_index,
            "frontier_sample_index": self._frontier_sample_index,
            "lineage_sample_index": self._lineage_sample_index,
            "topology_policy": island_topology_policy(self.n_islands),
            "migration_replay": _migration_replay_policy(self._migration_sequence),
            "archive_sequence_by_program_id": dict(
                sorted(self._archive_sequences.items())
            ),
            "islands": [
                    {
                        "island_id": island_id,
                        "occupied_cell_count": len(island.occupied_cells()),
                        "elite_count": len(island.elite_archive()),
                        "pareto_frontier_count": len(
                            island.pareto_frontier_archive()
                        ),
                        "metric_cell_archive_count": len(
                            island.metric_cell_archive()
                        ),
                    }
                    for island_id, island in enumerate(self.islands)
                ],
            "archive_contents": {
                "schema": "libreevolve.island_archive_contents.v1",
                "restore_status": ISLAND_ARCHIVE_CONTENTS_RESTORE_STATUS,
                "islands": [
                    {
                        "island_id": island_id,
                        "archive": island.state_snapshot(),
                    }
                    for island_id, island in enumerate(self.islands)
                ],
            },
        }

    def restore_cursor_state(self, snapshot: dict) -> dict:
        """Restore compact cursor/counter state without archive cell contents."""
        restored = _validate_cursor_state_snapshot(snapshot, self.n_islands)
        self._current = restored["next_island_id"]
        self._sequence = restored["archive_sequence"]
        self._migration_sequence = restored["migration_sequence"]
        self._metric_sample_index = restored["metric_sample_index"]
        self._frontier_sample_index = restored["frontier_sample_index"]
        self._lineage_sample_index = restored["lineage_sample_index"]
        self._archive_sequences = dict(restored["archive_sequence_by_program_id"])
        topology_policy = dict(restored["topology_policy"])
        migration_replay = dict(restored["migration_replay"])
        self._last_sample_metadata = {}
        return {
            "status": "cursor_state_restored",
            "archive_contents_restored": False,
            "full_archive_restore_required": True,
            "next_island_id": self._current,
            "archive_sequence": self._sequence,
            "migration_sequence": self._migration_sequence,
            "metric_sample_index": self._metric_sample_index,
            "frontier_sample_index": self._frontier_sample_index,
            "lineage_sample_index": self._lineage_sample_index,
            "archive_sequence_by_program_id": dict(
                sorted(self._archive_sequences.items())
            ),
            "topology_policy": topology_policy,
            "migration_replay": migration_replay,
        }

    def restore_archive_state(
        self,
        snapshot: dict,
        programs_by_id: dict[str, Program],
    ) -> dict:
        """Restore cursor/counter state and replayable per-island archive contents."""
        cursor = self.restore_cursor_state(snapshot)
        contents = _validate_archive_contents_snapshot(
            snapshot.get("archive_contents"),
            self.n_islands,
        )
        restored_islands = []
        for island_record in contents["islands"]:
            island_id = island_record["island_id"]
            restored = self.islands[island_id].restore_state_snapshot(
                island_record["archive"],
                programs_by_id,
            )
            restored_islands.append({"island_id": island_id, **restored})
        self._last_sample_metadata = {}
        return {
            **cursor,
            "status": "archive_state_restored",
            "archive_contents_restored": True,
            "full_archive_restore_required": False,
            "restored_islands": restored_islands,
        }

    def sample_diverse(
        self, k: int, exclude_ids: set[str] | None = None, strategy: str = "mixed"
    ) -> list[Program]:
        k = validate_sample_count(k, "island sample count")
        exclude_ids = validate_exclude_ids(exclude_ids, "island exclude_ids")
        if k <= 0:
            self._record_diverse_sample_metadata(strategy, [], k, exclude_ids)
            return []
        if strategy == "random":
            candidates = self._occupied_programs(exclude_ids)
            if not candidates:
                self._record_diverse_sample_metadata(strategy, [], k, exclude_ids)
                return []
            selected = self._rng.sample(candidates, min(k, len(candidates)))
            self._record_diverse_sample_metadata(strategy, selected, k, exclude_ids)
            return selected
        candidates = self._retained_programs(exclude_ids)
        if not candidates:
            self._record_diverse_sample_metadata(strategy, [], k, exclude_ids)
            return []
        if strategy == "selection":
            selected = sorted(candidates, key=_selection_key, reverse=True)[:k]
            self._record_diverse_sample_metadata(strategy, selected, k, exclude_ids)
            return selected
        if strategy == "metric":
            leader_entries = _metric_leader_entries(candidates, self._metric_order)
            selected = _first_unique(
                [program for _, program in leader_entries]
                + sorted(candidates, key=_selection_key, reverse=True),
                k,
            )
            self._record_diverse_sample_metadata(
                strategy,
                selected,
                k,
                exclude_ids,
                target_metrics=[
                    {"metric": metric, "program_id": program.id}
                    for metric, program in leader_entries
                ],
            )
            return selected
        if strategy == "frontier":
            frontier = _frontier_programs(candidates, self._metric_order)
            if not frontier:
                selected = sorted(candidates, key=_selection_key, reverse=True)[:k]
                self._record_diverse_sample_metadata(
                    strategy,
                    selected,
                    k,
                    exclude_ids,
                    fallback_strategy="selection",
                    frontier_size=0,
                    metric_order=list(self._metric_order),
                )
                return selected
            selected = frontier[:k]
            self._record_diverse_sample_metadata(
                strategy,
                selected,
                k,
                exclude_ids,
                frontier_size=len(frontier),
                metric_order=list(self._metric_order),
            )
            return selected
        if strategy == "lineage":
            representatives = _lineage_representatives(candidates)
            selected = _first_unique(
                [program for _, program in representatives]
                + sorted(candidates, key=_selection_key, reverse=True),
                k,
            )
            self._record_diverse_sample_metadata(
                strategy,
                selected,
                k,
                exclude_ids,
                lineages=[
                    {"lineage_root_id": lineage_root_id, "program_id": program.id}
                    for lineage_root_id, program in representatives
                ],
            )
            return selected
        if strategy == "novelty":
            selected = sorted(candidates, key=_novelty_key, reverse=True)[:k]
            self._record_diverse_sample_metadata(strategy, selected, k, exclude_ids)
            return selected
        if strategy == "recency":
            selected = sorted(candidates, key=self._recency_key, reverse=True)[:k]
            self._record_diverse_sample_metadata(strategy, selected, k, exclude_ids)
            return selected
        if strategy == "mixed":
            random_tail = self._rng.sample(candidates, len(candidates))
            selected = _first_unique(
                _metric_leaders(candidates, self._metric_order)
                + sorted(candidates, key=_novelty_key, reverse=True)
                + sorted(candidates, key=_selection_key, reverse=True)
                + random_tail,
                k,
            )
            self._record_diverse_sample_metadata(strategy, selected, k, exclude_ids)
            return selected
        raise ValueError(f"Unknown inspiration strategy: {strategy!r}")

    def _occupied_programs(
        self, exclude_ids: set[str] | None = None
    ) -> list[Program]:
        exclude_ids = validate_exclude_ids(exclude_ids, "island exclude_ids")
        pool: dict[str, Program] = {}
        for island in self.islands:
            for program in island.occupied_cells():
                if program.id not in exclude_ids:
                    pool.setdefault(program.id, program)
        return list(pool.values())

    def _retained_programs(
        self, exclude_ids: set[str] | None = None
    ) -> list[Program]:
        exclude_ids = validate_exclude_ids(exclude_ids, "island exclude_ids")
        pool: dict[str, Program] = {}
        for island in self.islands:
            for program in (
                island.occupied_cells()
                + island.elite_archive()
                + island.pareto_frontier_archive()
                + island.metric_cell_archive()
            ):
                if program.id not in exclude_ids:
                    pool.setdefault(program.id, program)
        return list(pool.values())

    def best(self) -> Program | None:
        cands = [i.best() for i in self.islands if i.best()]
        return max(cands, key=_selection_key) if cands else None

    def migrate(self) -> list[dict]:
        """Ring: island i copies top migrants to island (i+1) % n.

        Snapshot all elite archives first so that migrants added during this
        round are not themselves propagated in the same step (i.e. island 0
        does not indirectly reach island 2 via island 1 in a single call).

        Migration uses canonical candidate ids: target islands receive
        additional placement references to the same Program object, not cloned
        candidates with new ids. A target island that already contains that
        candidate id is skipped.
        """
        events: list[dict] = []
        if self._migration_ratio <= 0:
            return events
        self._migration_sequence += 1
        snapshots = [src.elite_archive() for src in self.islands]
        for i, elites in enumerate(snapshots):
            if not elites:
                continue
            dst_id = (i + 1) % self.n_islands
            dst = self.islands[dst_id]
            target_ids = _island_program_ids(dst)
            n = max(1, math.ceil(len(elites) * self._migration_ratio))
            for program in elites[:n]:
                if program.id in target_ids:
                    events.append(
                        _migration_event(
                            self._migration_sequence,
                            i,
                            dst_id,
                            program,
                            admitted=False,
                            reason="already_present",
                        )
                    )
                    continue
                event = dst.add(program)
                target_ids.add(program.id)
                if event.get("search_state_changed") is True:
                    self._sequence += 1
                    self._archive_sequences[program.id] = self._sequence
                placement = _migration_event(
                    self._migration_sequence,
                    i,
                    dst_id,
                    program,
                    admitted=bool(event.get("search_state_changed")),
                    reason=str(event.get("reason", "unknown")),
                    cell=event.get("cell"),
                    selection_score=event.get("selection_score"),
                )
                _record_migration_placement(program, placement)
                events.append(placement)
        return events

    def _recency_key(self, program: Program) -> tuple:
        return (
            self._archive_sequences.get(program.id, 0),
            program.generation,
            *_selection_key(program),
        )

    def _record_sample_metadata(
        self, strategy: str, selected: Program | None, **extra: object
    ) -> None:
        self._last_sample_metadata = {
            "strategy": strategy,
            "selected_program_id": selected.id if selected is not None else None,
            **extra,
        }

    def _record_diverse_sample_metadata(
        self,
        strategy: str,
        selected: list[Program],
        requested_count: int,
        exclude_ids: set[str],
        **extra: object,
    ) -> None:
        self._last_sample_metadata = {
            "strategy": strategy,
            "sample_kind": "diverse",
            "requested_count": requested_count,
            "selected_count": len(selected),
            "selected_program_ids": [program.id for program in selected],
            "excluded_count": len(exclude_ids),
            **extra,
        }


def _metric_leaders(
    candidates: list[Program], metric_order: list[str] | None = None
) -> list[Program]:
    return _first_unique(
        [program for _, program in _metric_leader_entries(candidates, metric_order)],
        len(candidates),
    )


def _metric_leader_entries(
    candidates: list[Program], metric_order: list[str] | None = None
) -> list[tuple[str, Program]]:
    declared_names = set(metric_order or [])
    observed_names = {
        name
        for program in candidates
        for name in _normalized_metrics(program, declared_names).keys()
    }
    configured_names = [
        name
        for name in (metric_order or [])
        if name in observed_names
    ]
    names = configured_names + sorted(
        {
            name for name in observed_names if name not in set(configured_names)
        }
    )
    leaders: list[tuple[str, Program]] = []
    for name in names:
        eligible = [
            program
            for program in candidates
            if name in _normalized_metrics(program, declared_names)
        ]
        if eligible:
            leaders.append(
                (
                    name,
                    max(
                        eligible,
                        key=lambda program: (
                            _normalized_metrics(program, declared_names)[name],
                            *_selection_key(program),
                        ),
                    ),
                )
            )
    return leaders


def _lineage_representatives(candidates: list[Program]) -> list[tuple[str, Program]]:
    by_root: dict[str, Program] = {}
    for program in candidates:
        root_id = _lineage_root_id(program)
        current = by_root.get(root_id)
        if current is None or _selection_key(program) > _selection_key(current):
            by_root[root_id] = program
    return sorted(
        by_root.items(),
        key=lambda item: _selection_key(item[1]),
        reverse=True,
    )


def _lineage_root_id(program: Program) -> str:
    if program.lineage:
        return program.lineage[0]
    return program.id


def _frontier_programs(
    candidates: list[Program], metric_order: list[str] | None = None
) -> list[Program]:
    metric_order = [
        name for name in (metric_order or []) if isinstance(name, str) and name
    ]
    if not metric_order:
        return []
    declared_names = set(metric_order)
    records: list[tuple[Program, dict[str, float]]] = []
    for program in candidates:
        metrics = _normalized_metrics(program, declared_names)
        if all(name in metrics for name in metric_order):
            records.append((program, {name: metrics[name] for name in metric_order}))
    frontier = [
        program
        for index, (program, metrics) in enumerate(records)
        if not any(
            other_index != index
            and _frontier_dominates(other_metrics, metrics, metric_order)
            for other_index, (_, other_metrics) in enumerate(records)
        )
    ]
    return sorted(frontier, key=_selection_key, reverse=True)


def _frontier_dominates(
    left: dict[str, float],
    right: dict[str, float],
    metric_order: list[str],
) -> bool:
    return all(left[name] >= right[name] for name in metric_order) and any(
        left[name] > right[name] for name in metric_order
    )


def _normalized_metrics(program: Program, declared_names: set[str] | None = None) -> dict[str, float]:
    raw = program.metadata.get("normalized_metrics")
    if not isinstance(raw, dict):
        return {}
    declared_names = declared_names or set()
    normalized: dict[str, float] = {}
    for name, value in raw.items():
        if not isinstance(name, str):
            continue
        if declared_names and name not in declared_names:
            continue
        if _is_valid_normalized_metric(value):
            normalized[name] = float(value)
    return normalized


def _novelty_key(program: Program) -> tuple[float, float, float]:
    return (_descriptor_value(program, "diversity"), *_selection_key(program))


def _validate_program_generation(program: Program) -> None:
    if (
        isinstance(program.generation, bool)
        or not isinstance(program.generation, int)
        or program.generation < 0
    ):
        raise ValueError("Program generation must be a non-negative integer")


def _descriptor_value(program: Program, name: str) -> float:
    admission = program.metadata.get("archive_admission")
    if not isinstance(admission, dict):
        return 0.0
    descriptors = admission.get("descriptors")
    if not isinstance(descriptors, dict):
        return 0.0
    raw = descriptors.get(name)
    return float(raw) if _is_finite_number(raw) else 0.0


def _is_finite_number(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _is_valid_normalized_metric(value: object) -> bool:
    return _is_finite_number(value) and 0.0 <= float(value) <= 1.0


def _island_program_ids(island: MAPElites) -> set[str]:
    programs = (
        island.occupied_cells()
        + island.elite_archive()
        + island.metric_cell_archive()
    )
    return {
        program.id
        for program in programs
    }


def _migration_event(
    sequence: int,
    source_island: int,
    target_island: int,
    program: Program,
    *,
    admitted: bool,
    reason: str,
    cell: object = None,
    selection_score: object = None,
) -> dict:
    event = {
        "migration_sequence": sequence,
        "program_id": program.id,
        "canonical_program_id": program.id,
        "source_island": source_island,
        "target_island": target_island,
        "identity_policy": "canonical_id_reference",
        "clone_id": None,
        "admitted": admitted,
        "reason": reason,
        "cell": cell if isinstance(cell, list) else None,
    }
    if _is_finite_number(selection_score):
        event["selection_score"] = float(selection_score)
    else:
        event["selection_score"] = None
    event["objective_vector"] = _migration_objective_vector(program)
    return event


def _migration_objective_vector(program: Program) -> dict | None:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    normalized_metrics = metadata.get("normalized_metrics")
    if not isinstance(normalized_metrics, dict):
        return None
    metrics: dict[str, float] = {}
    for name, value in sorted(normalized_metrics.items()):
        if isinstance(name, str) and _is_finite_number(value):
            numeric = float(value)
            if 0.0 <= numeric <= 1.0:
                metrics[name] = numeric
    if not metrics:
        return None
    record: dict[str, object] = {
        "policy": "normalized_declared_metric_vector_v1",
        "normalized_metrics": metrics,
    }
    selection_policy = metadata.get("selection_policy")
    if isinstance(selection_policy, dict):
        record["selection_policy"] = copy.deepcopy(selection_policy)
    return record


def _record_migration_placement(program: Program, placement: dict) -> None:
    metadata = dict(program.metadata)
    placements = metadata.get("migration_placements")
    if not isinstance(placements, list):
        placements = []
    metadata["migration_placements"] = placements + [dict(placement)]
    program.metadata = metadata


def _validate_cursor_state_snapshot(snapshot: object, n_islands: int) -> dict:
    if not isinstance(snapshot, dict):
        raise ValueError("island cursor state snapshot must be an object")
    if snapshot.get("schema") != "libreevolve.island_state.v1":
        raise ValueError("island cursor state snapshot schema is unsupported")
    if snapshot.get("resume_status") not in ISLAND_STATE_ACCEPTED_RESUME_STATUSES:
        raise ValueError("island cursor state snapshot resume status is unsupported")
    if snapshot.get("cursor_policy") != "advance_only_on_search_state_changed":
        raise ValueError("island cursor state snapshot cursor policy is unsupported")
    if snapshot.get("n_islands") != n_islands:
        raise ValueError("island cursor state snapshot n_islands must match model")
    next_island_id = _validate_snapshot_non_negative_int(
        snapshot.get("next_island_id"),
        "next_island_id",
    )
    if next_island_id >= n_islands:
        raise ValueError("island cursor state snapshot next_island_id is out of range")
    archive_sequence = _validate_snapshot_non_negative_int(
        snapshot.get("archive_sequence"),
        "archive_sequence",
    )
    migration_sequence = _validate_snapshot_non_negative_int(
        snapshot.get("migration_sequence"),
        "migration_sequence",
    )
    metric_sample_index = _validate_snapshot_non_negative_int(
        snapshot.get("metric_sample_index"),
        "metric_sample_index",
    )
    frontier_sample_index = _validate_snapshot_non_negative_int(
        snapshot.get("frontier_sample_index", 0),
        "frontier_sample_index",
    )
    lineage_sample_index = _validate_snapshot_non_negative_int(
        snapshot.get("lineage_sample_index", 0),
        "lineage_sample_index",
    )
    archive_sequences = _validate_cursor_archive_sequences(
        snapshot.get("archive_sequence_by_program_id"),
        archive_sequence,
    )
    topology_policy = validate_island_topology_policy(
        snapshot.get("topology_policy"),
        n_islands,
    )
    migration_replay = _validate_migration_replay_policy(
        snapshot.get("migration_replay"),
        migration_sequence,
    )
    _validate_cursor_island_summaries(snapshot.get("islands"), n_islands)
    return {
        "next_island_id": next_island_id,
        "archive_sequence": archive_sequence,
        "migration_sequence": migration_sequence,
        "metric_sample_index": metric_sample_index,
        "frontier_sample_index": frontier_sample_index,
        "lineage_sample_index": lineage_sample_index,
        "archive_sequence_by_program_id": archive_sequences,
        "topology_policy": topology_policy,
        "migration_replay": migration_replay,
    }


def _validate_archive_contents_snapshot(value: object, n_islands: int) -> dict:
    if not isinstance(value, dict):
        raise ValueError("island archive contents snapshot must be an object")
    required = {"schema", "restore_status", "islands"}
    missing = required - set(value)
    if missing:
        raise ValueError(
            f"island archive contents snapshot missing fields: {sorted(missing)}"
        )
    unsupported = set(value) - required
    if unsupported:
        raise ValueError(
            f"island archive contents snapshot has unsupported fields: {sorted(unsupported)}"
        )
    if value["schema"] != "libreevolve.island_archive_contents.v1":
        raise ValueError("island archive contents snapshot schema is unsupported")
    if value["restore_status"] != ISLAND_ARCHIVE_CONTENTS_RESTORE_STATUS:
        raise ValueError("island archive contents snapshot restore status is unsupported")
    islands = value["islands"]
    if not isinstance(islands, list) or len(islands) != n_islands:
        raise ValueError("island archive contents snapshot islands length must match n_islands")
    restored = []
    for index, island in enumerate(islands):
        if not isinstance(island, dict):
            raise ValueError(
                f"island archive contents snapshot islands[{index}] must be an object"
            )
        required_island = {"island_id", "archive"}
        missing_island = required_island - set(island)
        if missing_island:
            raise ValueError(
                "island archive contents snapshot islands"
                f"[{index}] missing fields: {sorted(missing_island)}"
            )
        unsupported_island = set(island) - required_island
        if unsupported_island:
            raise ValueError(
                "island archive contents snapshot islands"
                f"[{index}] has unsupported fields: {sorted(unsupported_island)}"
            )
        if island["island_id"] != index:
            raise ValueError(
                "island archive contents snapshot islands"
                f"[{index}].island_id must equal {index}"
            )
        restored.append(
            {
                "island_id": index,
                "archive": island["archive"],
            }
        )
    return {"islands": restored}


def _validate_cursor_archive_sequences(value: object, archive_sequence: int) -> dict[str, int]:
    if not isinstance(value, dict):
        raise ValueError("island cursor state archive_sequence_by_program_id must be an object")
    restored: dict[str, int] = {}
    for program_id, sequence in value.items():
        validate_program_identity(program_id)
        sequence = _validate_snapshot_positive_int(
            sequence,
            f"archive_sequence_by_program_id.{program_id}",
        )
        if sequence > archive_sequence:
            raise ValueError(
                "island cursor state archive_sequence_by_program_id value "
                "must be <= archive_sequence"
            )
        restored[program_id] = sequence
    return dict(sorted(restored.items()))


def _validate_cursor_island_summaries(value: object, n_islands: int) -> None:
    if not isinstance(value, list) or len(value) != n_islands:
        raise ValueError("island cursor state islands length must match n_islands")
    for index, island in enumerate(value):
        if not isinstance(island, dict):
            raise ValueError(f"island cursor state islands[{index}] must be an object")
        if island.get("island_id") != index:
            raise ValueError(f"island cursor state islands[{index}].island_id must equal {index}")
        _validate_snapshot_non_negative_int(
            island.get("occupied_cell_count"),
            f"islands[{index}].occupied_cell_count",
        )
        _validate_snapshot_non_negative_int(
            island.get("elite_count"),
            f"islands[{index}].elite_count",
        )


def _migration_replay_policy(migration_sequence: int) -> dict:
    return {
        "schema": ISLAND_MIGRATION_REPLAY_SCHEMA,
        "status": ISLAND_MIGRATION_REPLAY_STATUS,
        "policy": ISLAND_MIGRATION_REPLAY_POLICY,
        "migration_sequence": migration_sequence,
        "replay_engine_supported": False,
        "archive_contents_restore_covers_current_placements": True,
        "limitations": [
            "migration_event_order_not_applied_as_restore_engine",
            "migration_skip_events_not_reconstructed",
            "controller_pending_work_not_restored",
        ],
    }


def island_topology_policy(n_islands: int) -> dict:
    return {
        "schema": ISLAND_TOPOLOGY_POLICY_SCHEMA,
        "status": ISLAND_TOPOLOGY_STATUS,
        "policy": ISLAND_TOPOLOGY_POLICY,
        "configured_n_islands": n_islands,
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


def validate_island_topology_policy(value: object, n_islands: int) -> dict:
    if value is None:
        return island_topology_policy(n_islands)
    if not isinstance(value, dict):
        raise ValueError("island topology policy must be an object")
    required = {
        "schema",
        "status",
        "policy",
        "configured_n_islands",
        "default_n_islands",
        "island_count_configurable",
        "migration_topology",
        "migration_execution",
        "adaptive_island_count_supported",
        "non_ring_topologies_supported",
        "alphaevolve_policy_ready",
        "limitations",
    }
    missing = required - set(value)
    if missing:
        raise ValueError(f"island topology policy missing fields: {sorted(missing)}")
    unsupported = set(value) - required
    if unsupported:
        raise ValueError(
            f"island topology policy has unsupported fields: {sorted(unsupported)}"
        )
    if value["schema"] != ISLAND_TOPOLOGY_POLICY_SCHEMA:
        raise ValueError("island topology policy schema is unsupported")
    if value["status"] != ISLAND_TOPOLOGY_STATUS:
        raise ValueError("island topology policy status is unsupported")
    if value["policy"] != ISLAND_TOPOLOGY_POLICY:
        raise ValueError("island topology policy is unsupported")
    if value["configured_n_islands"] != n_islands:
        raise ValueError("island topology policy configured_n_islands must match model")
    if value["default_n_islands"] != 5:
        raise ValueError("island topology policy default_n_islands must remain five")
    if value["island_count_configurable"] is not True:
        raise ValueError("island topology policy must preserve configurable island count")
    if value["migration_topology"] != "ring":
        raise ValueError("island topology policy migration_topology is unsupported")
    if value["migration_execution"] != "synchronous_local_generation_boundary":
        raise ValueError("island topology policy migration_execution is unsupported")
    if value["adaptive_island_count_supported"] is not False:
        raise ValueError("island topology policy must not claim adaptive island counts")
    if value["non_ring_topologies_supported"] is not False:
        raise ValueError("island topology policy must not claim non-ring topologies")
    if value["alphaevolve_policy_ready"] is not False:
        raise ValueError("island topology policy must not claim AlphaEvolve parity")
    limitations = value["limitations"]
    if not isinstance(limitations, list) or not limitations:
        raise ValueError("island topology policy limitations must be a non-empty list")
    for index, limitation in enumerate(limitations):
        if not isinstance(limitation, str) or not limitation.strip():
            raise ValueError(
                f"island topology policy limitations[{index}] must be non-empty text"
            )
    return {
        "schema": value["schema"],
        "status": value["status"],
        "policy": value["policy"],
        "configured_n_islands": value["configured_n_islands"],
        "default_n_islands": value["default_n_islands"],
        "island_count_configurable": value["island_count_configurable"],
        "migration_topology": value["migration_topology"],
        "migration_execution": value["migration_execution"],
        "adaptive_island_count_supported": value["adaptive_island_count_supported"],
        "non_ring_topologies_supported": value["non_ring_topologies_supported"],
        "alphaevolve_policy_ready": value["alphaevolve_policy_ready"],
        "limitations": list(limitations),
    }


def _validate_migration_replay_policy(value: object, migration_sequence: int) -> dict:
    if value is None:
        return _migration_replay_policy(migration_sequence)
    if not isinstance(value, dict):
        raise ValueError("island migration replay policy must be an object")
    required = {
        "schema",
        "status",
        "policy",
        "migration_sequence",
        "replay_engine_supported",
        "archive_contents_restore_covers_current_placements",
        "limitations",
    }
    missing = required - set(value)
    if missing:
        raise ValueError(
            f"island migration replay policy missing fields: {sorted(missing)}"
        )
    unsupported = set(value) - required
    if unsupported:
        raise ValueError(
            f"island migration replay policy has unsupported fields: {sorted(unsupported)}"
        )
    if value["schema"] != ISLAND_MIGRATION_REPLAY_SCHEMA:
        raise ValueError("island migration replay policy schema is unsupported")
    if value["status"] != ISLAND_MIGRATION_REPLAY_STATUS:
        raise ValueError("island migration replay policy status is unsupported")
    if value["policy"] != ISLAND_MIGRATION_REPLAY_POLICY:
        raise ValueError("island migration replay policy is unsupported")
    if value["migration_sequence"] != migration_sequence:
        raise ValueError(
            "island migration replay policy migration_sequence must match snapshot"
        )
    if value["replay_engine_supported"] is not False:
        raise ValueError(
            "island migration replay policy must not claim replay engine support"
        )
    if value["archive_contents_restore_covers_current_placements"] is not True:
        raise ValueError(
            "island migration replay policy must preserve archive-content restore coverage"
        )
    limitations = value["limitations"]
    if not isinstance(limitations, list) or not limitations:
        raise ValueError("island migration replay policy limitations must be a non-empty list")
    for index, limitation in enumerate(limitations):
        if not isinstance(limitation, str) or not limitation.strip():
            raise ValueError(
                f"island migration replay policy limitations[{index}] must be non-empty text"
            )
    return {
        "schema": value["schema"],
        "status": value["status"],
        "policy": value["policy"],
        "migration_sequence": value["migration_sequence"],
        "replay_engine_supported": value["replay_engine_supported"],
        "archive_contents_restore_covers_current_placements": value[
            "archive_contents_restore_covers_current_placements"
        ],
        "limitations": list(limitations),
    }


def _validate_snapshot_positive_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"island cursor state {field} must be a positive integer")
    return value


def _validate_snapshot_non_negative_int(value: object, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"island cursor state {field} must be a non-negative integer")
    return value


def _first_unique(programs: list[Program], k: int) -> list[Program]:
    result: list[Program] = []
    seen: set[str] = set()
    for program in programs:
        if program.id in seen:
            continue
        seen.add(program.id)
        result.append(program)
        if len(result) >= k:
            break
    return result
