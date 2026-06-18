from __future__ import annotations
import random
import math
from dataclasses import dataclass
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from libreevolve.population.program import (
    Program,
    validate_program_identity,
    validate_program_metrics,
)
from libreevolve.population.sampling import validate_exclude_ids, validate_sample_count

MAP_ELITES_OBJECTIVE_ARCHIVE_POLICY_SCHEMA = (
    "libreevolve.map_elites_objective_archive_policy.v1"
)
MAP_ELITES_OBJECTIVE_ARCHIVE_READINESS_SCHEMA = (
    "libreevolve.map_elites_objective_archive_readiness.v1"
)
MAP_ELITES_DESCRIPTOR_READINESS_SCHEMA = (
    "libreevolve.map_elites_descriptor_readiness.v1"
)
_OBJECTIVE_ARCHIVE_POLICY_REQUIRED_FIELDS = {
    "schema",
    "status",
    "metric_order",
    "candidate_vector",
    "dominance",
    "bound",
    "trim_policy",
    "sampling_policy",
    "cell_replacement_policy",
}
_OBJECTIVE_ARCHIVE_POLICY_OPTIONAL_FIELDS = {"readiness"}
_OBJECTIVE_ARCHIVE_SAMPLING_POLICIES = {
    "eligible_for_metric_and_frontier_sampling_via_island_retained_pool",
    "eligible_for_metric_frontier_and_metric_cell_sampling_via_island_retained_pool",
}
_OBJECTIVE_ARCHIVE_CELL_REPLACEMENT_POLICIES = {
    "map_elites_cells_still_replace_by_scalar_selection_key",
    "scalar_primary_cells_plus_metric_specific_cell_overlays",
}


@dataclass(frozen=True)
class ObjectiveArchivePolicyIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ObjectiveArchivePolicyValidation:
    ok: bool
    archive_policy_ready: bool
    primary_pareto_replacement_ready: bool
    metric_order: list[str]
    bound: int | None
    issues: list[ObjectiveArchivePolicyIssue]


def validate_map_elites_objective_archive_policy(
    policy: object,
    *,
    metric_order: list[str] | tuple[str, ...] | None = None,
    elite_archive_size: int | None = None,
) -> ObjectiveArchivePolicyValidation:
    """Validate the MAP-Elites objective archive policy without restoring state."""
    issues: list[ObjectiveArchivePolicyIssue] = []
    expected_metric_order: tuple[str, ...] | None = None
    if metric_order is not None:
        try:
            expected_metric_order = _validate_metric_order(metric_order)
        except ValueError as exc:
            issues.append(
                ObjectiveArchivePolicyIssue(
                    "invalid_expected_metric_order",
                    str(exc),
                )
            )
    if elite_archive_size is not None and (
        isinstance(elite_archive_size, bool)
        or not isinstance(elite_archive_size, int)
        or elite_archive_size < 1
    ):
        issues.append(
            ObjectiveArchivePolicyIssue(
                "invalid_expected_elite_archive_size",
                "elite_archive_size must be a positive integer",
            )
        )
        elite_archive_size = None
    if not isinstance(policy, dict):
        return ObjectiveArchivePolicyValidation(
            ok=False,
            archive_policy_ready=False,
            primary_pareto_replacement_ready=False,
            metric_order=[],
            bound=None,
            issues=[
                *issues,
                ObjectiveArchivePolicyIssue(
                    "invalid_shape",
                    "objective archive policy must be an object",
                ),
            ],
        )

    missing = _OBJECTIVE_ARCHIVE_POLICY_REQUIRED_FIELDS - set(policy)
    if missing:
        issues.append(
            ObjectiveArchivePolicyIssue(
                "missing_fields",
                f"objective archive policy missing fields: {sorted(missing)}",
            )
        )
    unsupported = (
        set(policy)
        - _OBJECTIVE_ARCHIVE_POLICY_REQUIRED_FIELDS
        - _OBJECTIVE_ARCHIVE_POLICY_OPTIONAL_FIELDS
    )
    if unsupported:
        issues.append(
            ObjectiveArchivePolicyIssue(
                "unsupported_fields",
                f"objective archive policy has unsupported fields: {sorted(unsupported)}",
            )
        )
    if policy.get("schema") != MAP_ELITES_OBJECTIVE_ARCHIVE_POLICY_SCHEMA:
        issues.append(
            ObjectiveArchivePolicyIssue(
                "invalid_schema",
                "objective archive policy schema is unsupported",
            )
        )
    if policy.get("status") != "bounded_non_dominated_archive_retention":
        issues.append(
            ObjectiveArchivePolicyIssue(
                "invalid_status",
                "objective archive policy status is unsupported",
            )
        )

    actual_metric_order: tuple[str, ...] = ()
    try:
        actual_metric_order = _validate_metric_order(policy.get("metric_order"))
    except ValueError as exc:
        issues.append(
            ObjectiveArchivePolicyIssue(
                "invalid_metric_order",
                str(exc),
            )
        )
    if (
        expected_metric_order is not None
        and actual_metric_order
        and actual_metric_order != expected_metric_order
    ):
        issues.append(
            ObjectiveArchivePolicyIssue(
                "metric_order_mismatch",
                "objective archive policy metric_order must match the archive",
            )
        )
    if policy.get("candidate_vector") != "complete_normalized_declared_metrics_required":
        issues.append(
            ObjectiveArchivePolicyIssue(
                "invalid_candidate_vector",
                "objective archive policy candidate_vector is unsupported",
            )
        )
    if (
        policy.get("dominance")
        != "all_metrics_greater_or_equal_and_one_strictly_greater"
    ):
        issues.append(
            ObjectiveArchivePolicyIssue(
                "invalid_dominance",
                "objective archive policy dominance is unsupported",
            )
        )
    bound = policy.get("bound")
    normalized_bound: int | None = None
    if isinstance(bound, bool) or not isinstance(bound, int) or bound < 1:
        issues.append(
            ObjectiveArchivePolicyIssue(
                "invalid_bound",
                "objective archive policy bound must be a positive integer",
            )
        )
    else:
        normalized_bound = bound
        if elite_archive_size is not None and bound != elite_archive_size:
            issues.append(
                ObjectiveArchivePolicyIssue(
                    "bound_mismatch",
                    "objective archive policy bound must match elite_archive_size",
                )
            )
    if policy.get("trim_policy") != "crowding_distance_then_selection_score_then_fitness":
        issues.append(
            ObjectiveArchivePolicyIssue(
                "invalid_trim_policy",
                "objective archive policy trim_policy is unsupported",
            )
        )
    if policy.get("sampling_policy") not in _OBJECTIVE_ARCHIVE_SAMPLING_POLICIES:
        issues.append(
            ObjectiveArchivePolicyIssue(
                "invalid_sampling_policy",
                "objective archive policy sampling_policy is unsupported",
            )
        )
    cell_policy = policy.get("cell_replacement_policy")
    if cell_policy not in _OBJECTIVE_ARCHIVE_CELL_REPLACEMENT_POLICIES:
        code = "invalid_cell_replacement_policy"
        if isinstance(cell_policy, str) and (
            "pareto" in cell_policy or "frontier" in cell_policy
        ):
            code = "primary_pareto_replacement_overclaim"
        issues.append(
            ObjectiveArchivePolicyIssue(
                code,
                "objective archive policy cell_replacement_policy is unsupported",
            )
        )
    issues.extend(
        _objective_archive_readiness_issues(
            policy.get("readiness"),
            issue_type=ObjectiveArchivePolicyIssue,
        )
    )
    return ObjectiveArchivePolicyValidation(
        ok=not issues,
        archive_policy_ready=not issues,
        primary_pareto_replacement_ready=False,
        metric_order=list(actual_metric_order),
        bound=normalized_bound,
        issues=issues,
    )


def map_elites_objective_archive_readiness() -> dict:
    return {
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
    }


def _objective_archive_readiness_issues(
    value: object,
    *,
    issue_type: type[ObjectiveArchivePolicyIssue],
) -> list[ObjectiveArchivePolicyIssue]:
    if value is None:
        return []
    issues: list[ObjectiveArchivePolicyIssue] = []
    if not isinstance(value, dict):
        return [
            issue_type(
                "invalid_readiness_shape",
                "objective archive policy readiness must be an object",
            )
        ]
    expected = map_elites_objective_archive_readiness()
    required = set(expected)
    missing = required - set(value)
    if missing:
        issues.append(
            issue_type(
                "readiness_missing_fields",
                f"objective archive policy readiness missing fields: {sorted(missing)}",
            )
        )
    unsupported = set(value) - required
    if unsupported:
        issues.append(
            issue_type(
                "readiness_unsupported_fields",
                f"objective archive policy readiness has unsupported fields: {sorted(unsupported)}",
            )
        )
    if value.get("schema") != MAP_ELITES_OBJECTIVE_ARCHIVE_READINESS_SCHEMA:
        issues.append(
            issue_type(
                "readiness_invalid_schema",
                "objective archive policy readiness schema is unsupported",
            )
        )
    for field in (
        "primary_pareto_archive_replacement",
        "frontier_dominance_cell_replacement",
        "durable_cross_run_metric_database",
        "metric_target_persistence_tables",
        "llm_feedback_calibration_runner",
    ):
        if value.get(field) is not False:
            issues.append(
                issue_type(
                    f"{field}_overclaim",
                    f"objective archive policy readiness must not claim {field}",
                )
            )
    remaining_gap = value.get("remaining_gap")
    if not isinstance(remaining_gap, list) or not remaining_gap:
        issues.append(
            issue_type(
                "readiness_invalid_remaining_gap",
                "objective archive policy readiness remaining_gap must be a non-empty list",
            )
        )
    elif any(not isinstance(gap, str) or not gap.strip() for gap in remaining_gap):
        issues.append(
            issue_type(
                "readiness_invalid_remaining_gap",
                "objective archive policy readiness remaining_gap entries must be non-empty text",
            )
        )
    return issues


class MAPElites:
    """3D MAP-Elites: selection score x workspace complexity x diversity.

    This is a fixed local quality-diversity heuristic, not a canonical
    user-defined behavior descriptor implementation.
    """

    def __init__(
        self,
        bins: int = 10,
        elite_archive_size: int = 50,
        perf_bounds: tuple[float, float] = (0.0, 1.0),
        complexity_max_chars: int = 100_000,
        descriptor_axes: list[str] | tuple[str, ...] | None = None,
        metric_order: list[str] | tuple[str, ...] | None = None,
        rng: random.Random | None = None,
    ):
        if isinstance(bins, bool) or not isinstance(bins, int) or bins < 1:
            raise ValueError("MAP-Elites bins must be a positive integer")
        if (
            isinstance(elite_archive_size, bool)
            or not isinstance(elite_archive_size, int)
            or elite_archive_size < 1
        ):
            raise ValueError("MAP-Elites elite_archive_size must be a positive integer")
        perf_bounds = _validate_perf_bounds(perf_bounds)
        complexity_max_chars = _validate_complexity_max_chars(complexity_max_chars)
        descriptor_axes = _validate_descriptor_axes(descriptor_axes)
        metric_order = _validate_metric_order(metric_order)
        self.bins = bins
        self._perf_min, self._perf_max = perf_bounds
        self._grid: dict[tuple[int, int, int], Program] = {}
        self._cell_descriptors: dict[tuple[int, int, int], dict[str, float]] = {}
        self._program_descriptors: dict[str, dict[str, float]] = {}
        self._complexity_max_chars: int = complexity_max_chars
        self._descriptor_axes: tuple[str, str, str] = descriptor_axes
        self._metric_order: tuple[str, ...] = metric_order
        self._metric_cell_elites: dict[str, dict[tuple[int, int, int], Program]] = {
            metric: {} for metric in self._metric_order
        }
        self._elite: list[Program] = []
        self._pareto_elite: list[Program] = []
        self._elite_size = elite_archive_size
        self._rng = rng if rng is not None else random.Random()
        self._descriptor_model_revision = 0

    def _norm_perf(self, fitness: float) -> float:
        rng = self._perf_max - self._perf_min
        if rng == 0: return 0.5
        return max(0.0, min(1.0, (fitness - self._perf_min) / rng))

    def _norm_complexity(self, descriptor_text: str) -> float:
        n = len(descriptor_text)
        return max(0.0, min(1.0, n / self._complexity_max_chars))

    def _commit_descriptor_state(self, program: Program) -> None:
        self._descriptor_model_revision += 1

    def _diversity(self, descriptor_text: str) -> float:
        """Mean TF-IDF char-ngram cosine distance to global elite archive."""
        if not self._elite: return 0.5
        corpus = [_descriptor_text(p) for p in self._elite] + [descriptor_text]
        ngram_size = _char_ngram_size(corpus)
        if ngram_size is None:
            return 0.5
        try:
            mat = TfidfVectorizer(
                analyzer="char",
                ngram_range=(ngram_size, ngram_size),
            ).fit_transform(corpus)
        except ValueError:
            return 0.5
        sims = cosine_similarity(mat[-1], mat[:-1])[0]
        return max(0.0, min(1.0, float(np.mean(1.0 - sims))))

    def _cell_with_descriptors(
        self, p: Program
    ) -> tuple[tuple[int, int, int], dict[str, float]]:
        descriptor_text = _descriptor_text(p)
        base_descriptors = {
            "performance": self._norm_perf(_selection_score(p)),
            "complexity": self._norm_complexity(descriptor_text),
            "diversity": self._diversity(descriptor_text),
        }
        descriptors = {
            axis: _descriptor_axis_value(axis, p, base_descriptors)
            for axis in self._descriptor_axes
        }
        c = lambda x: max(0, min(self.bins - 1, int(x * self.bins)))
        return (
            c(descriptors[self._descriptor_axes[0]]),
            c(descriptors[self._descriptor_axes[1]]),
            c(descriptors[self._descriptor_axes[2]]),
        ), descriptors

    def _cell(self, p: Program) -> tuple[int, int, int]:
        return self._cell_with_descriptors(p)[0]

    def add(self, program: Program) -> dict:
        validate_program_identity(program.id, program.parent_id, program.lineage)
        event = {
            "program_id": program.id,
            "admitted": False,
            "reason": "invalid_evaluation",
            "evaluation_is_valid": program.evaluation.get("is_valid") is True,
            "cell": None,
            "descriptors": {},
            "previous_occupant_id": None,
            "cell_replaced": False,
            "entered_cell": False,
            "entered_elite": False,
            "cell_admitted": False,
            "elite_retained": False,
            "search_state_changed": False,
            "sampling_eligible": False,
            "displaced_elite_ids": [],
            "pareto_frontier_retained": False,
            "pareto_frontier_replaced_ids": [],
            "pareto_frontier_reason": "not_evaluated",
            "pareto_frontier_size": 0,
            "metric_cell_retained": False,
            "metric_cell_replacements": [],
            "metric_cell_reason": "not_evaluated",
        }
        selection_score = _selection_score(program)
        event["selection_score"] = selection_score if math.isfinite(selection_score) else None
        if event["evaluation_is_valid"] is not True:
            return event
        program.metrics = validate_program_metrics(program.metrics)
        event["reason"] = "non_finite_fitness"
        if not _is_finite_real(program.fitness):
            event["reason"] = _fitness_rejection_reason(program.fitness)
            return event
        if not math.isfinite(selection_score):
            return event
        cell, descriptors = self._cell_with_descriptors(program)
        event["cell"] = list(cell)
        event["descriptors"] = descriptors
        self._program_descriptors[program.id] = dict(descriptors)
        occ = self._grid.get(cell)
        event["previous_occupant_id"] = occ.id if occ else None
        if occ is None or _selection_key(program) > _selection_key(occ):
            self._grid[cell] = program
            self._cell_descriptors[cell] = dict(descriptors)
            event["entered_cell"] = True
            event["cell_replaced"] = occ is not None
        self._elite.append(program)
        self._elite.sort(key=_selection_key, reverse=True)
        before_trim_ids = [p.id for p in self._elite]
        self._elite = self._elite[:self._elite_size]
        elite_ids = {p.id for p in self._elite}
        event["entered_elite"] = program.id in elite_ids
        event["displaced_elite_ids"] = [
            program_id for program_id in before_trim_ids[self._elite_size :]
        ]
        metric_cell_event = self._retain_metric_cells(program, cell)
        event.update(metric_cell_event)
        pareto_event = self._retain_pareto_frontier(program)
        event.update(pareto_event)
        event["cell_admitted"] = event["entered_cell"]
        event["elite_retained"] = event["entered_elite"]
        event["search_state_changed"] = (
            event["cell_admitted"]
            or event["elite_retained"]
            or event["metric_cell_retained"]
            or event["pareto_frontier_retained"]
            or bool(event["pareto_frontier_replaced_ids"])
        )
        if event["search_state_changed"]:
            self._commit_descriptor_state(program)
        event["sampling_eligible"] = event["entered_cell"]
        event["admitted"] = event["search_state_changed"]
        if event["cell_replaced"]:
            event["reason"] = "cell_replaced"
        elif event["entered_cell"]:
            event["reason"] = "empty_cell"
        elif event["entered_elite"]:
            event["reason"] = "elite_only"
        elif event["pareto_frontier_retained"]:
            event["reason"] = "pareto_frontier_only"
        elif event["metric_cell_retained"]:
            event["reason"] = "metric_cell_only"
        else:
            event["reason"] = "not_improving_cell"
        return event

    def _retain_metric_cells(
        self,
        program: Program,
        cell: tuple[int, int, int],
    ) -> dict:
        event = {
            "metric_cell_retained": False,
            "metric_cell_replacements": [],
            "metric_cell_reason": "no_declared_objective_metrics",
        }
        vector = _objective_vector(program, self._metric_order)
        if vector is None:
            if self._metric_order:
                event["metric_cell_reason"] = "incomplete_objective_vector"
            return event
        replacements = []
        for metric in self._metric_order:
            metric_cells = self._metric_cell_elites.setdefault(metric, {})
            previous = metric_cells.get(cell)
            previous_vector = (
                _objective_vector(previous, self._metric_order)
                if previous is not None
                else None
            )
            previous_value = (
                previous_vector.get(metric)
                if isinstance(previous_vector, dict)
                else None
            )
            candidate_key = (vector[metric], *_selection_key(program))
            previous_key = (
                (float(previous_value), *_selection_key(previous))
                if previous is not None and _is_finite_real(previous_value)
                else None
            )
            replaced = previous_key is None or candidate_key > previous_key
            if replaced:
                metric_cells[cell] = program
            replacements.append(
                {
                    "metric": metric,
                    "cell": list(cell),
                    "retained": replaced,
                    "candidate_value": vector[metric],
                    "previous_occupant_id": previous.id if previous else None,
                    "previous_value": (
                        float(previous_value)
                        if _is_finite_real(previous_value)
                        else None
                    ),
                    "cell_replaced": previous is not None and replaced,
                }
            )
        event["metric_cell_replacements"] = replacements
        event["metric_cell_retained"] = any(
            record["retained"] for record in replacements
        )
        event["metric_cell_reason"] = (
            "metric_cell_retained"
            if event["metric_cell_retained"]
            else "not_improving_metric_cell"
        )
        return event

    def _retain_pareto_frontier(self, program: Program) -> dict:
        event = {
            "pareto_frontier_retained": False,
            "pareto_frontier_replaced_ids": [],
            "pareto_frontier_reason": "no_declared_objective_metrics",
            "pareto_frontier_size": len(self._pareto_elite),
        }
        vector = _objective_vector(program, self._metric_order)
        if vector is None:
            if self._metric_order:
                event["pareto_frontier_reason"] = "incomplete_objective_vector"
            return event
        records = [
            (candidate, candidate_vector)
            for candidate in self._pareto_elite
            if candidate.id != program.id
            if (candidate_vector := _objective_vector(candidate, self._metric_order))
            is not None
        ]
        previous_ids = {candidate.id for candidate, _ in records}
        if any(
            _objective_vector_dominates(candidate_vector, vector, self._metric_order)
            for _, candidate_vector in records
        ):
            event["pareto_frontier_reason"] = "dominated_objective_vector"
            return event
        replaced_ids = [
            candidate.id
            for candidate, candidate_vector in records
            if _objective_vector_dominates(vector, candidate_vector, self._metric_order)
        ]
        retained = [
            candidate for candidate, _ in records if candidate.id not in set(replaced_ids)
        ]
        retained.append(program)
        retained = _trim_pareto_frontier(retained, self._metric_order, self._elite_size)
        self._pareto_elite = retained
        retained_ids = {candidate.id for candidate in self._pareto_elite}
        event["pareto_frontier_retained"] = program.id in retained_ids
        event["pareto_frontier_replaced_ids"] = sorted(
            program_id
            for program_id in previous_ids | set(replaced_ids)
            if program_id not in retained_ids
        )
        event["pareto_frontier_size"] = len(self._pareto_elite)
        if event["pareto_frontier_retained"]:
            event["pareto_frontier_reason"] = "non_dominated_objective_vector"
        else:
            event["pareto_frontier_reason"] = "bounded_archive_trimmed_candidate"
        return event

    def best(self) -> Program | None:
        return self._elite[0] if self._elite else None

    def sample_diverse(
        self, k: int, exclude_ids: set[str] | None = None
    ) -> list[Program]:
        k = validate_sample_count(k, "MAP-Elites sample count")
        exclude_ids = validate_exclude_ids(exclude_ids, "MAP-Elites exclude_ids")
        cells = [p for p in self._grid.values() if p.id not in exclude_ids]
        return self._rng.sample(cells, min(k, len(cells))) if cells else []

    def occupied_cells(self) -> list[Program]:
        return list(self._grid.values())

    def elite_archive(self) -> list[Program]:
        return list(self._elite)

    def pareto_frontier_archive(self) -> list[Program]:
        return list(self._pareto_elite)

    def metric_cell_archive(self) -> list[Program]:
        pool: dict[str, Program] = {}
        for metric in self._metric_order:
            for program in self._metric_cell_elites.get(metric, {}).values():
                pool.setdefault(program.id, program)
        return list(pool.values())

    def state_snapshot(self) -> dict:
        return {
            "schema": "libreevolve.map_elites_state.v1",
            "bins": self.bins,
            "elite_archive_size": self._elite_size,
            "perf_bounds": [self._perf_min, self._perf_max],
            "complexity_max_chars": self._complexity_max_chars,
            "descriptor_axes": list(self._descriptor_axes),
            "cells": [
                {
                    "cell": list(cell),
                    "program_id": program.id,
                    "descriptors": _json_finite_descriptors(
                        self._cell_descriptors.get(cell, {})
                    ),
                    "selection_score": _json_finite_selection_score(program),
                }
                for cell, program in sorted(
                    self._grid.items(),
                    key=lambda item: (item[0], item[1].id),
                )
            ],
            "elite_program_ids": [program.id for program in self._elite],
            "elite_descriptor_records": [
                {
                    "program_id": program.id,
                    "descriptors": _json_finite_descriptors(
                        self._program_descriptors.get(program.id, {})
                    ),
                }
                for program in self._elite
            ],
            "pareto_frontier_program_ids": [
                program.id for program in self._pareto_elite
            ],
            "pareto_frontier_descriptor_records": [
                {
                    "program_id": program.id,
                    "descriptors": _json_finite_descriptors(
                        self._program_descriptors.get(program.id, {})
                    ),
                }
                for program in self._pareto_elite
            ],
            "metric_cell_archives": [
                {
                    "metric": metric,
                    "cells": [
                        {
                            "cell": list(cell),
                            "program_id": program.id,
                            "metric_value": _json_finite_metric_value(
                                program,
                                metric,
                                self._metric_order,
                            ),
                            "descriptors": _json_finite_descriptors(
                                self._program_descriptors.get(program.id, {})
                            ),
                            "selection_score": _json_finite_selection_score(program),
                        }
                        for cell, program in sorted(
                            self._metric_cell_elites.get(metric, {}).items(),
                            key=lambda item: (item[0], item[1].id),
                        )
                    ],
                }
                for metric in self._metric_order
            ],
            "objective_archive_policy": {
                "schema": MAP_ELITES_OBJECTIVE_ARCHIVE_POLICY_SCHEMA,
                "status": "bounded_non_dominated_archive_retention",
                "metric_order": list(self._metric_order),
                "candidate_vector": "complete_normalized_declared_metrics_required",
                "dominance": "all_metrics_greater_or_equal_and_one_strictly_greater",
                "bound": self._elite_size,
                "trim_policy": "crowding_distance_then_selection_score_then_fitness",
                "sampling_policy": (
                    "eligible_for_metric_frontier_and_metric_cell_sampling_via_island_retained_pool"
                ),
                "cell_replacement_policy": (
                    "scalar_primary_cells_plus_metric_specific_cell_overlays"
                ),
                "readiness": map_elites_objective_archive_readiness(),
            },
            "descriptor_policy": {
                "schema": "libreevolve.map_elites_descriptor_policy.v1",
                "axes": list(self._descriptor_axes),
                "performance": "selection_score_normalized_by_fixed_perf_bounds",
                "complexity": "workspace_descriptor_chars_clamped_to_configured_bound",
                "diversity": "tfidf_char_ngram_distance_to_current_elite_archive",
                "metric": "normalized_metrics_axis_else_raw_metric_clamped_to_unit_interval",
                "evaluation_metadata": "numeric_evaluation_metadata_path_clamped_to_unit_interval",
                "candidate_metadata": "numeric_candidate_metadata_path_clamped_to_unit_interval",
                "diversity_reference_program_ids": [
                    program.id for program in self._elite
                ],
                "diversity_update_policy": (
                    "reference_updates_after_search_state_change"
                ),
                "rebin_policy": (
                    "no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots"
                ),
            },
            "descriptor_model": {
                "schema": "libreevolve.map_elites_descriptor_model.v1",
                "revision": self._descriptor_model_revision,
                "revision_policy": "increments_on_search_state_change",
                "axes": list(self._descriptor_axes),
                "performance_bounds": [self._perf_min, self._perf_max],
                "complexity_max_chars": self._complexity_max_chars,
                "diversity_reference_program_ids": [
                    program.id for program in self._elite
                ],
                "dynamic_diversity_reference": True,
                "rebin_policy": (
                    "no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots"
                ),
                "readiness": map_elites_descriptor_readiness(),
            },
        }

    def restore_state_snapshot(
        self,
        snapshot: dict,
        programs_by_id: dict[str, Program],
    ) -> dict:
        restored = _validate_map_elites_snapshot(snapshot, self)
        grid: dict[tuple[int, int, int], Program] = {}
        cell_descriptors: dict[tuple[int, int, int], dict[str, float]] = {}
        program_descriptors: dict[str, dict[str, float]] = {}
        for cell_record in restored["cells"]:
            program_id = cell_record["program_id"]
            if program_id not in programs_by_id:
                raise ValueError(
                    "MAP-Elites snapshot cell references missing program id "
                    f"{program_id!r}"
                )
            cell = tuple(cell_record["cell"])
            grid[cell] = programs_by_id[program_id]
            cell_descriptors[cell] = dict(cell_record["descriptors"])
            if cell_record["descriptors"]:
                program_descriptors[program_id] = dict(cell_record["descriptors"])
        elite: list[Program] = []
        for program_id in restored["elite_program_ids"]:
            if program_id not in programs_by_id:
                raise ValueError(
                    "MAP-Elites snapshot elite references missing program id "
                    f"{program_id!r}"
                )
            elite.append(programs_by_id[program_id])
            if descriptors := restored["elite_descriptor_records"].get(program_id):
                program_descriptors[program_id] = dict(descriptors)
        pareto_elite: list[Program] = []
        for program_id in restored["pareto_frontier_program_ids"]:
            if program_id not in programs_by_id:
                raise ValueError(
                    "MAP-Elites snapshot Pareto frontier references missing program id "
                    f"{program_id!r}"
                )
            pareto_elite.append(programs_by_id[program_id])
            if descriptors := restored["pareto_frontier_descriptor_records"].get(
                program_id
            ):
                program_descriptors[program_id] = dict(descriptors)
        metric_cell_elites: dict[str, dict[tuple[int, int, int], Program]] = {
            metric: {} for metric in self._metric_order
        }
        for archive_record in restored["metric_cell_archives"]:
            metric = archive_record["metric"]
            for cell_record in archive_record["cells"]:
                program_id = cell_record["program_id"]
                if program_id not in programs_by_id:
                    raise ValueError(
                        "MAP-Elites snapshot metric cell references missing program id "
                        f"{program_id!r}"
                )
                cell = tuple(cell_record["cell"])
                metric_cell_elites[metric][cell] = programs_by_id[program_id]
                if cell_record["descriptors"]:
                    program_descriptors[program_id] = dict(cell_record["descriptors"])
        self._grid = grid
        self._cell_descriptors = cell_descriptors
        self._program_descriptors = program_descriptors
        self._elite = elite
        self._pareto_elite = pareto_elite
        self._metric_cell_elites = metric_cell_elites
        self._descriptor_model_revision = restored["descriptor_model"]["revision"]
        return {
            "status": "map_elites_state_restored",
            "occupied_cell_count": len(self._grid),
            "elite_count": len(self._elite),
            "pareto_frontier_count": len(self._pareto_elite),
            "metric_cell_archive_count": sum(
                len(cells) for cells in self._metric_cell_elites.values()
            ),
        }


def _selection_score(program: Program) -> float:
    raw = program.metadata.get("selection_score")
    if _is_finite_real(raw):
        return float(raw)
    if _is_finite_real(program.fitness):
        return float(program.fitness)
    return float("-inf")


def _selection_key(program: Program) -> tuple[float, float]:
    fitness = float(program.fitness) if _is_finite_real(program.fitness) else float("-inf")
    return (_selection_score(program), fitness)


def _json_finite_selection_score(program: Program) -> float | None:
    value = _selection_score(program)
    return value if math.isfinite(value) else None


def _json_finite_metric_value(
    program: Program,
    metric: str,
    metric_order: tuple[str, ...],
) -> float | None:
    vector = _objective_vector(program, metric_order)
    if not isinstance(vector, dict):
        return None
    value = vector.get(metric)
    return float(value) if _is_finite_real(value) else None


def _json_finite_descriptors(descriptors: dict[str, float]) -> dict[str, float]:
    return {
        name: float(value)
        for name, value in sorted(descriptors.items())
        if _is_finite_real(value)
    }


def _is_finite_real(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _validate_perf_bounds(bounds: object) -> tuple[float, float]:
    if not isinstance(bounds, (tuple, list)) or len(bounds) != 2:
        raise ValueError("MAP-Elites perf_bounds must be numeric [lo, hi]")
    lo_raw, hi_raw = bounds
    if not _is_finite_real(lo_raw) or not _is_finite_real(hi_raw):
        raise ValueError("MAP-Elites perf_bounds must be finite numeric [lo, hi]")
    lo = float(lo_raw)
    hi = float(hi_raw)
    if not lo < hi:
        raise ValueError("MAP-Elites perf_bounds must satisfy lo < hi")
    return (lo, hi)


def _validate_complexity_max_chars(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("MAP-Elites complexity_max_chars must be a positive integer")
    return value


def _validate_descriptor_axes(
    value: list[str] | tuple[str, ...] | None,
) -> tuple[str, str, str]:
    if value is None:
        value = ("performance", "complexity", "diversity")
    if not isinstance(value, (list, tuple)) or len(value) != 3:
        raise ValueError("MAP-Elites descriptor_axes must contain exactly three axes")
    normalized: list[str] = []
    seen: set[str] = set()
    for index, axis in enumerate(value):
        if not isinstance(axis, str) or not axis:
            raise ValueError(
                f"MAP-Elites descriptor_axes[{index}] must be a descriptor axis string"
            )
        if not _is_supported_descriptor_axis(axis):
            raise ValueError(
                f"MAP-Elites descriptor_axes[{index}] is unsupported: {axis!r}"
            )
        if axis in seen:
            raise ValueError("MAP-Elites descriptor_axes must not contain duplicates")
        seen.add(axis)
        normalized.append(axis)
    return (normalized[0], normalized[1], normalized[2])


def _validate_metric_order(value: list[str] | tuple[str, ...] | None) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)):
        raise ValueError("MAP-Elites metric_order must be a list of metric names")
    normalized: list[str] = []
    seen: set[str] = set()
    for index, name in enumerate(value):
        if not isinstance(name, str) or not name:
            raise ValueError(
                f"MAP-Elites metric_order[{index}] must be a metric name string"
            )
        try:
            validate_program_metrics({name: 0.0})
        except ValueError as exc:
            raise ValueError(
                f"MAP-Elites metric_order[{index}] is unsupported: {name!r}"
            ) from exc
        if name in seen:
            raise ValueError("MAP-Elites metric_order must not contain duplicates")
        seen.add(name)
        normalized.append(name)
    return tuple(normalized)


def _is_supported_descriptor_axis(axis: str) -> bool:
    if axis in {"performance", "complexity", "diversity"}:
        return True
    if axis.startswith("metric:"):
        return _safe_metric_or_path(axis.split(":", 1)[1])
    if axis.startswith("evaluation_metadata:"):
        return _safe_metric_or_path(axis.split(":", 1)[1])
    if axis.startswith("candidate_metadata:"):
        return _safe_metric_or_path(axis.split(":", 1)[1])
    return False


def _safe_metric_or_path(value: str) -> bool:
    if not value:
        return False
    try:
        for part in value.split("."):
            validate_program_metrics({part: 0.0})
    except ValueError:
        return False
    return True


def _descriptor_axis_value(
    axis: str,
    program: Program,
    base_descriptors: dict[str, float],
) -> float:
    if axis in base_descriptors:
        return base_descriptors[axis]
    if axis.startswith("metric:"):
        metric = axis.split(":", 1)[1]
        normalized = program.metadata.get("normalized_metrics")
        if isinstance(normalized, dict) and _is_finite_real(normalized.get(metric)):
            return _unit_interval(float(normalized[metric]))
        if _is_finite_real(program.metrics.get(metric)):
            return _unit_interval(float(program.metrics[metric]))
        return 0.0
    if axis.startswith("evaluation_metadata:"):
        value = _nested_numeric(
            program.evaluation.get("metadata"),
            axis.split(":", 1)[1],
        )
        return _unit_interval(value) if value is not None else 0.0
    if axis.startswith("candidate_metadata:"):
        value = _nested_numeric(program.metadata, axis.split(":", 1)[1])
        return _unit_interval(value) if value is not None else 0.0
    return 0.0


def _nested_numeric(root: object, path: str) -> float | None:
    current = root
    for part in path.split("."):
        if not isinstance(current, dict):
            return None
        current = current.get(part)
    if _is_finite_real(current):
        return float(current)
    return None


def _unit_interval(value: float) -> float:
    return max(0.0, min(1.0, value))


def _objective_vector(
    program: Program,
    metric_order: tuple[str, ...],
) -> dict[str, float] | None:
    if not metric_order:
        return None
    raw = program.metadata.get("normalized_metrics")
    if not isinstance(raw, dict):
        return None
    vector: dict[str, float] = {}
    for name in metric_order:
        value = raw.get(name)
        if not _is_finite_real(value):
            return None
        numeric = float(value)
        if numeric < 0.0 or numeric > 1.0:
            return None
        vector[name] = numeric
    return vector


def _objective_vector_dominates(
    left: dict[str, float],
    right: dict[str, float],
    metric_order: tuple[str, ...],
) -> bool:
    return all(left[name] >= right[name] for name in metric_order) and any(
        left[name] > right[name] for name in metric_order
    )


def _trim_pareto_frontier(
    candidates: list[Program],
    metric_order: tuple[str, ...],
    limit: int,
) -> list[Program]:
    if len(candidates) <= limit:
        return sorted(candidates, key=_selection_key, reverse=True)
    crowding = _crowding_distances(candidates, metric_order)
    return sorted(
        candidates,
        key=lambda program: (
            crowding.get(program.id, 0.0),
            *_selection_key(program),
        ),
        reverse=True,
    )[:limit]


def _crowding_distances(
    candidates: list[Program],
    metric_order: tuple[str, ...],
) -> dict[str, float]:
    distances = {program.id: 0.0 for program in candidates}
    vectors = {
        program.id: _objective_vector(program, metric_order) for program in candidates
    }
    for metric in metric_order:
        ordered = sorted(
            [
                program
                for program in candidates
                if vectors.get(program.id) is not None
            ],
            key=lambda program: vectors[program.id][metric],  # type: ignore[index]
        )
        if not ordered:
            continue
        distances[ordered[0].id] = float("inf")
        distances[ordered[-1].id] = float("inf")
        if len(ordered) <= 2:
            continue
        lo = vectors[ordered[0].id][metric]  # type: ignore[index]
        hi = vectors[ordered[-1].id][metric]  # type: ignore[index]
        span = hi - lo
        if span <= 0:
            continue
        for index in range(1, len(ordered) - 1):
            previous_value = vectors[ordered[index - 1].id][metric]  # type: ignore[index]
            next_value = vectors[ordered[index + 1].id][metric]  # type: ignore[index]
            distances[ordered[index].id] += (next_value - previous_value) / span
    return distances


def _fitness_rejection_reason(value: object) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "invalid_fitness_type"
    return "non_finite_fitness"


def _descriptor_text(program: Program) -> str:
    """Stable text representation used by local archive descriptors."""
    files = program.files if program.files else {program.primary_file: program.code}
    parts = [
        "libreevolve.map_elites.workspace_descriptor.v1",
        f"primary_file={program.primary_file}",
        f"file_count={len(files)}",
    ]
    for path, content in sorted(files.items()):
        role = "primary" if path == program.primary_file else "support"
        parts.append(f"<<<FILE path={path!r} role={role} chars={len(content)}>>>")
        parts.append(content)
        parts.append("<<<END_FILE>>>")
    return "\n".join(parts)


def _char_ngram_size(corpus: list[str]) -> int | None:
    longest = max((len(text) for text in corpus), default=0)
    if longest <= 0:
        return None
    return max(1, min(4, longest))


def map_elites_descriptor_readiness() -> dict:
    return {
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


def _validate_map_elites_snapshot(snapshot: object, archive: MAPElites) -> dict:
    if not isinstance(snapshot, dict):
        raise ValueError("MAP-Elites snapshot must be an object")
    required = {
        "schema",
        "bins",
        "elite_archive_size",
        "perf_bounds",
        "complexity_max_chars",
        "descriptor_axes",
        "cells",
        "elite_program_ids",
        "descriptor_policy",
        "descriptor_model",
    }
    optional = {
        "elite_descriptor_records",
        "pareto_frontier_program_ids",
        "pareto_frontier_descriptor_records",
        "metric_cell_archives",
        "objective_archive_policy",
    }
    missing = required - set(snapshot)
    if missing:
        raise ValueError(f"MAP-Elites snapshot missing fields: {sorted(missing)}")
    unsupported = set(snapshot) - required - optional
    if unsupported:
        raise ValueError(f"MAP-Elites snapshot has unsupported fields: {sorted(unsupported)}")
    if snapshot["schema"] != "libreevolve.map_elites_state.v1":
        raise ValueError("MAP-Elites snapshot schema is unsupported")
    if snapshot["bins"] != archive.bins:
        raise ValueError("MAP-Elites snapshot bins must match archive")
    if snapshot["elite_archive_size"] != archive._elite_size:
        raise ValueError("MAP-Elites snapshot elite_archive_size must match archive")
    if _validate_perf_bounds(snapshot["perf_bounds"]) != (
        archive._perf_min,
        archive._perf_max,
    ):
        raise ValueError("MAP-Elites snapshot perf_bounds must match archive")
    if snapshot["complexity_max_chars"] != archive._complexity_max_chars:
        raise ValueError("MAP-Elites snapshot complexity_max_chars must match archive")
    descriptor_axes = _validate_descriptor_axes(snapshot["descriptor_axes"])
    if descriptor_axes != archive._descriptor_axes:
        raise ValueError("MAP-Elites snapshot descriptor_axes must match archive")
    descriptor_policy = snapshot["descriptor_policy"]
    if not isinstance(descriptor_policy, dict):
        raise ValueError("MAP-Elites snapshot descriptor_policy must be an object")
    if (
        descriptor_policy.get("schema")
        != "libreevolve.map_elites_descriptor_policy.v1"
    ):
        raise ValueError("MAP-Elites snapshot descriptor_policy schema is unsupported")
    policy_axes = _validate_descriptor_axes(descriptor_policy.get("axes"))
    if policy_axes != archive._descriptor_axes:
        raise ValueError("MAP-Elites snapshot descriptor_policy.axes must match archive")
    cells = _validate_map_elites_snapshot_cells(
        snapshot["cells"],
        archive.bins,
        archive._descriptor_axes,
    )
    elite_program_ids = _validate_snapshot_program_id_list(
        snapshot["elite_program_ids"],
        "elite_program_ids",
    )
    if len(elite_program_ids) > archive._elite_size:
        raise ValueError("MAP-Elites snapshot elite_program_ids exceeds configured size")
    elite_descriptor_records = _validate_descriptor_record_list(
        snapshot.get("elite_descriptor_records"),
        "elite_descriptor_records",
        elite_program_ids,
        archive._descriptor_axes,
    )
    pareto_frontier_program_ids = _validate_snapshot_program_id_list(
        snapshot.get("pareto_frontier_program_ids", []),
        "pareto_frontier_program_ids",
    )
    if len(pareto_frontier_program_ids) > archive._elite_size:
        raise ValueError(
            "MAP-Elites snapshot pareto_frontier_program_ids exceeds configured size"
        )
    pareto_frontier_descriptor_records = _validate_descriptor_record_list(
        snapshot.get("pareto_frontier_descriptor_records"),
        "pareto_frontier_descriptor_records",
        pareto_frontier_program_ids,
        archive._descriptor_axes,
    )
    _validate_objective_archive_policy(
        snapshot.get("objective_archive_policy"),
        archive,
        pareto_frontier_program_ids,
    )
    metric_cell_archives = _validate_metric_cell_archives(
        snapshot.get("metric_cell_archives", []),
        archive,
    )
    if not isinstance(
        descriptor_policy.get("diversity_reference_program_ids"),
        list,
    ):
        raise ValueError(
            "MAP-Elites snapshot descriptor_policy.diversity_reference_program_ids must be a list"
        )
    diversity_reference_ids = _validate_snapshot_program_id_list(
        descriptor_policy["diversity_reference_program_ids"],
        "descriptor_policy.diversity_reference_program_ids",
    )
    if diversity_reference_ids != elite_program_ids:
        raise ValueError(
            "MAP-Elites snapshot diversity_reference_program_ids must match elite_program_ids"
        )
    descriptor_model = _validate_map_elites_descriptor_model(
        snapshot["descriptor_model"],
        archive,
        elite_program_ids,
    )
    return {
        "cells": cells,
        "elite_program_ids": elite_program_ids,
        "elite_descriptor_records": elite_descriptor_records,
        "pareto_frontier_program_ids": pareto_frontier_program_ids,
        "pareto_frontier_descriptor_records": pareto_frontier_descriptor_records,
        "metric_cell_archives": metric_cell_archives,
        "descriptor_model": descriptor_model,
    }


def _validate_metric_cell_archives(value: object, archive: MAPElites) -> list[dict]:
    if value is None:
        value = []
    if not isinstance(value, list):
        raise ValueError("MAP-Elites snapshot metric_cell_archives must be a list")
    by_metric: dict[str, dict] = {}
    for index, record in enumerate(value):
        if not isinstance(record, dict):
            raise ValueError(
                f"MAP-Elites snapshot metric_cell_archives[{index}] must be an object"
            )
        required = {"metric", "cells"}
        missing = required - set(record)
        if missing:
            raise ValueError(
                "MAP-Elites snapshot metric_cell_archives record missing fields: "
                f"{sorted(missing)}"
            )
        unsupported = set(record) - required
        if unsupported:
            raise ValueError(
                "MAP-Elites snapshot metric_cell_archives record has unsupported fields: "
                f"{sorted(unsupported)}"
            )
        metric = record["metric"]
        if metric not in archive._metric_order:
            raise ValueError(
                "MAP-Elites snapshot metric_cell_archives metric must match archive"
            )
        if metric in by_metric:
            raise ValueError(
                "MAP-Elites snapshot metric_cell_archives must not duplicate metrics"
            )
        cells = _validate_metric_cell_archive_cells(
            record["cells"],
            archive.bins,
            f"metric_cell_archives[{index}].cells",
            archive._descriptor_axes,
        )
        if len(cells) > archive.bins ** 3:
            raise ValueError(
                "MAP-Elites snapshot metric_cell_archives exceeds possible cell count"
            )
        by_metric[metric] = {"metric": metric, "cells": cells}
    for metric in archive._metric_order:
        by_metric.setdefault(metric, {"metric": metric, "cells": []})
    if not archive._metric_order and by_metric:
        raise ValueError(
            "MAP-Elites snapshot metric_cell_archives requires configured metric_order"
        )
    return [by_metric[metric] for metric in archive._metric_order]


def _validate_metric_cell_archive_cells(
    value: object,
    bins: int,
    label: str,
    descriptor_axes: tuple[str, str, str],
) -> list[dict]:
    if not isinstance(value, list):
        raise ValueError(f"MAP-Elites snapshot {label} must be a list")
    cells = []
    seen: set[tuple[int, int, int]] = set()
    for index, record in enumerate(value):
        if not isinstance(record, dict):
            raise ValueError(f"MAP-Elites snapshot {label}[{index}] must be an object")
        required = {"cell", "program_id", "metric_value", "selection_score"}
        missing = required - set(record)
        if missing:
            raise ValueError(
                f"MAP-Elites snapshot {label}[{index}] missing fields: {sorted(missing)}"
            )
        unsupported = set(record) - required - {"descriptors"}
        if unsupported:
            raise ValueError(
                "MAP-Elites snapshot "
                f"{label}[{index}] has unsupported fields: {sorted(unsupported)}"
            )
        cell = _validate_map_elites_cell(record["cell"], bins, index)
        if tuple(cell) in seen:
            raise ValueError(f"MAP-Elites snapshot {label} has duplicate cells")
        seen.add(tuple(cell))
        program_id = record["program_id"]
        validate_program_identity(program_id)
        metric_value = record["metric_value"]
        if not _is_finite_real(metric_value) or not 0.0 <= float(metric_value) <= 1.0:
            raise ValueError(
                f"MAP-Elites snapshot {label}[{index}].metric_value must be in [0, 1]"
            )
        selection_score = record["selection_score"]
        if selection_score is not None and not _is_finite_real(selection_score):
            raise ValueError(
                f"MAP-Elites snapshot {label}[{index}].selection_score must be finite or null"
            )
        descriptors = _validate_map_elites_snapshot_descriptors(
            record.get("descriptors", {}),
            descriptor_axes,
            f"{label}[{index}].descriptors",
        )
        cells.append(
            {
                "cell": cell,
                "program_id": program_id,
                "metric_value": float(metric_value),
                "descriptors": descriptors,
                "selection_score": (
                    float(selection_score) if selection_score is not None else None
                ),
            }
        )
    return cells


def _validate_objective_archive_policy(
    value: object,
    archive: MAPElites,
    pareto_frontier_program_ids: list[str],
) -> None:
    if value is None:
        if pareto_frontier_program_ids:
            raise ValueError(
                "MAP-Elites snapshot objective_archive_policy is required with Pareto frontier ids"
            )
        return
    if not isinstance(value, dict):
        raise ValueError("MAP-Elites snapshot objective_archive_policy must be an object")
    required = {
        "schema",
        "status",
        "metric_order",
        "candidate_vector",
        "dominance",
        "bound",
        "trim_policy",
        "sampling_policy",
        "cell_replacement_policy",
    }
    missing = required - set(value)
    if missing:
        raise ValueError(
            f"MAP-Elites snapshot objective_archive_policy missing fields: {sorted(missing)}"
        )
    unsupported = set(value) - required - _OBJECTIVE_ARCHIVE_POLICY_OPTIONAL_FIELDS
    if unsupported:
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy has unsupported fields: "
            f"{sorted(unsupported)}"
        )
    if value["schema"] != MAP_ELITES_OBJECTIVE_ARCHIVE_POLICY_SCHEMA:
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy schema is unsupported"
        )
    if value["status"] != "bounded_non_dominated_archive_retention":
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy.status is unsupported"
        )
    if _validate_metric_order(value["metric_order"]) != archive._metric_order:
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy.metric_order must match archive"
        )
    if value["candidate_vector"] != "complete_normalized_declared_metrics_required":
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy.candidate_vector is unsupported"
        )
    if (
        value["dominance"]
        != "all_metrics_greater_or_equal_and_one_strictly_greater"
    ):
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy.dominance is unsupported"
        )
    if value["bound"] != archive._elite_size:
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy.bound must match archive"
        )
    if value["trim_policy"] != "crowding_distance_then_selection_score_then_fitness":
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy.trim_policy is unsupported"
        )
    if value["sampling_policy"] not in _OBJECTIVE_ARCHIVE_SAMPLING_POLICIES:
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy.sampling_policy is unsupported"
        )
    if value["cell_replacement_policy"] not in _OBJECTIVE_ARCHIVE_CELL_REPLACEMENT_POLICIES:
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy.cell_replacement_policy is unsupported"
        )
    readiness_issues = _objective_archive_readiness_issues(
        value.get("readiness"),
        issue_type=ObjectiveArchivePolicyIssue,
    )
    if readiness_issues:
        raise ValueError(
            "MAP-Elites snapshot objective_archive_policy.readiness "
            f"{readiness_issues[0].message}"
        )


def _validate_map_elites_descriptor_model(
    value: object,
    archive: MAPElites,
    elite_program_ids: list[str],
) -> dict:
    if not isinstance(value, dict):
        raise ValueError("MAP-Elites snapshot descriptor_model must be an object")
    required = {
        "schema",
        "revision",
        "revision_policy",
        "axes",
        "performance_bounds",
        "complexity_max_chars",
        "diversity_reference_program_ids",
        "dynamic_diversity_reference",
        "rebin_policy",
    }
    missing = required - set(value)
    if missing:
        raise ValueError(
            f"MAP-Elites snapshot descriptor_model missing fields: {sorted(missing)}"
        )
    unsupported = set(value) - required - {"readiness"}
    if unsupported:
        raise ValueError(
            "MAP-Elites snapshot descriptor_model has unsupported fields: "
            f"{sorted(unsupported)}"
        )
    if value["schema"] != "libreevolve.map_elites_descriptor_model.v1":
        raise ValueError("MAP-Elites snapshot descriptor_model schema is unsupported")
    revision = value["revision"]
    if isinstance(revision, bool) or not isinstance(revision, int) or revision < 0:
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.revision must be a non-negative integer"
        )
    if value["revision_policy"] != "increments_on_search_state_change":
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.revision_policy is unsupported"
        )
    model_axes = _validate_descriptor_axes(value["axes"])
    if model_axes != archive._descriptor_axes:
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.axes must match archive"
        )
    if _validate_perf_bounds(value["performance_bounds"]) != (
        archive._perf_min,
        archive._perf_max,
    ):
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.performance_bounds must match archive"
        )
    if value["complexity_max_chars"] != archive._complexity_max_chars:
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.complexity_max_chars must match archive"
        )
    reference_ids = _validate_snapshot_program_id_list(
        value["diversity_reference_program_ids"],
        "descriptor_model.diversity_reference_program_ids",
    )
    if reference_ids != elite_program_ids:
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.diversity_reference_program_ids must match elite_program_ids"
        )
    if value["dynamic_diversity_reference"] is not True:
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.dynamic_diversity_reference must be true"
        )
    rebin_policy = value["rebin_policy"]
    expected_rebin_policy = (
        "no_rebin_existing_cells_cell_coordinates_are_insertion_time_snapshots"
    )
    if rebin_policy != expected_rebin_policy:
        raise ValueError("MAP-Elites snapshot descriptor_model.rebin_policy is unsupported")
    return {
        "revision": revision,
        "diversity_reference_program_ids": reference_ids,
        "readiness": _validate_map_elites_descriptor_readiness(
            value.get("readiness")
        ),
    }


def _validate_map_elites_descriptor_readiness(value: object) -> dict:
    if value is None:
        return map_elites_descriptor_readiness()
    if not isinstance(value, dict):
        raise ValueError("MAP-Elites snapshot descriptor_model.readiness must be an object")
    expected = map_elites_descriptor_readiness()
    required = set(expected)
    missing = required - set(value)
    if missing:
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.readiness missing fields: "
            f"{sorted(missing)}"
        )
    unsupported = set(value) - required
    if unsupported:
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.readiness has unsupported fields: "
            f"{sorted(unsupported)}"
        )
    if value["schema"] != MAP_ELITES_DESCRIPTOR_READINESS_SCHEMA:
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.readiness schema is unsupported"
        )
    for field in (
        "stable_task_behavior_descriptor_contract",
        "learned_descriptor_model",
        "evaluator_provided_descriptor_model",
        "full_archive_rebin_engine",
        "partial_archive_rebin_engine",
        "descriptor_training_inputs_recorded",
        "restore_compatible_descriptor_revisioning",
    ):
        if value[field] is not False:
            raise ValueError(
                "MAP-Elites snapshot descriptor_model.readiness "
                f"must not claim {field}"
            )
    remaining_gap = value["remaining_gap"]
    if not isinstance(remaining_gap, list) or not remaining_gap:
        raise ValueError(
            "MAP-Elites snapshot descriptor_model.readiness remaining_gap must be a non-empty list"
        )
    for index, gap in enumerate(remaining_gap):
        if not isinstance(gap, str) or not gap.strip():
            raise ValueError(
                "MAP-Elites snapshot descriptor_model.readiness "
                f"remaining_gap[{index}] must be non-empty text"
            )
    return {
        "schema": value["schema"],
        "stable_task_behavior_descriptor_contract": value[
            "stable_task_behavior_descriptor_contract"
        ],
        "learned_descriptor_model": value["learned_descriptor_model"],
        "evaluator_provided_descriptor_model": value[
            "evaluator_provided_descriptor_model"
        ],
        "full_archive_rebin_engine": value["full_archive_rebin_engine"],
        "partial_archive_rebin_engine": value["partial_archive_rebin_engine"],
        "descriptor_training_inputs_recorded": value[
            "descriptor_training_inputs_recorded"
        ],
        "restore_compatible_descriptor_revisioning": value[
            "restore_compatible_descriptor_revisioning"
        ],
        "remaining_gap": list(remaining_gap),
    }


def _validate_map_elites_snapshot_cells(
    value: object,
    bins: int,
    descriptor_axes: tuple[str, str, str],
) -> list[dict]:
    if not isinstance(value, list):
        raise ValueError("MAP-Elites snapshot cells must be a list")
    restored: list[dict] = []
    seen_cells: set[tuple[int, int, int]] = set()
    seen_program_ids: set[str] = set()
    for index, record in enumerate(value):
        if not isinstance(record, dict):
            raise ValueError(f"MAP-Elites snapshot cells[{index}] must be an object")
        required = {"cell", "program_id", "selection_score"}
        missing = required - set(record)
        if missing:
            raise ValueError(
                f"MAP-Elites snapshot cells[{index}] missing fields: {sorted(missing)}"
            )
        unsupported = set(record) - required - {"descriptors"}
        if unsupported:
            raise ValueError(
                f"MAP-Elites snapshot cells[{index}] has unsupported fields: {sorted(unsupported)}"
            )
        cell = _validate_map_elites_cell(record["cell"], bins, index)
        if cell in seen_cells:
            raise ValueError("MAP-Elites snapshot cells must not repeat cell coordinates")
        seen_cells.add(cell)
        program_id = record["program_id"]
        validate_program_identity(program_id)
        if program_id in seen_program_ids:
            raise ValueError("MAP-Elites snapshot cells must not repeat program ids")
        seen_program_ids.add(program_id)
        selection_score = record["selection_score"]
        if selection_score is not None and not _is_finite_real(selection_score):
            raise ValueError(
                f"MAP-Elites snapshot cells[{index}].selection_score must be finite or null"
            )
        descriptors = _validate_map_elites_snapshot_descriptors(
            record.get("descriptors", {}),
            descriptor_axes,
            f"cells[{index}].descriptors",
        )
        restored.append(
            {
                "cell": list(cell),
                "program_id": program_id,
                "descriptors": descriptors,
                "selection_score": (
                    float(selection_score) if selection_score is not None else None
                ),
            }
        )
    return restored


def _validate_descriptor_record_list(
    value: object,
    field: str,
    expected_program_ids: list[str],
    descriptor_axes: tuple[str, str, str],
) -> dict[str, dict[str, float]]:
    if value is None:
        return {}
    if not isinstance(value, list):
        raise ValueError(f"MAP-Elites snapshot {field} must be a list")
    if len(value) != len(expected_program_ids):
        raise ValueError(
            f"MAP-Elites snapshot {field} must match its program id list length"
        )
    expected = list(expected_program_ids)
    restored: dict[str, dict[str, float]] = {}
    for index, record in enumerate(value):
        if not isinstance(record, dict):
            raise ValueError(f"MAP-Elites snapshot {field}[{index}] must be an object")
        required = {"program_id", "descriptors"}
        missing = required - set(record)
        if missing:
            raise ValueError(
                f"MAP-Elites snapshot {field}[{index}] missing fields: {sorted(missing)}"
            )
        unsupported = set(record) - required
        if unsupported:
            raise ValueError(
                f"MAP-Elites snapshot {field}[{index}] has unsupported fields: {sorted(unsupported)}"
            )
        program_id = record["program_id"]
        validate_program_identity(program_id)
        if program_id != expected[index]:
            raise ValueError(
                f"MAP-Elites snapshot {field}[{index}].program_id must match its program id list"
            )
        restored[program_id] = _validate_map_elites_snapshot_descriptors(
            record["descriptors"],
            descriptor_axes,
            f"{field}[{index}].descriptors",
        )
    return restored


def _validate_map_elites_snapshot_descriptors(
    value: object,
    descriptor_axes: tuple[str, str, str],
    label: str,
) -> dict[str, float]:
    if not isinstance(value, dict):
        raise ValueError(f"MAP-Elites snapshot {label} must be an object")
    if not value:
        return {}
    actual_axes = set(value)
    expected_axes = set(descriptor_axes)
    if actual_axes != expected_axes:
        raise ValueError(f"MAP-Elites snapshot {label} must match descriptor_axes")
    descriptors: dict[str, float] = {}
    for axis in descriptor_axes:
        raw = value[axis]
        if not _is_finite_real(raw) or not 0.0 <= float(raw) <= 1.0:
            raise ValueError(
                f"MAP-Elites snapshot {label}[{axis!r}] must be in [0, 1]"
            )
        descriptors[axis] = float(raw)
    return descriptors


def _validate_map_elites_cell(value: object, bins: int, index: int) -> tuple[int, int, int]:
    if not isinstance(value, list) or len(value) != 3:
        raise ValueError(f"MAP-Elites snapshot cells[{index}].cell must be a length-3 list")
    restored = []
    for axis, raw in enumerate(value):
        if isinstance(raw, bool) or not isinstance(raw, int):
            raise ValueError(
                f"MAP-Elites snapshot cells[{index}].cell[{axis}] must be an integer"
            )
        if raw < 0 or raw >= bins:
            raise ValueError(
                f"MAP-Elites snapshot cells[{index}].cell[{axis}] is out of range"
            )
        restored.append(raw)
    return (restored[0], restored[1], restored[2])


def _validate_snapshot_program_id_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list):
        raise ValueError(f"MAP-Elites snapshot {field} must be a list")
    restored: list[str] = []
    seen: set[str] = set()
    for index, program_id in enumerate(value):
        validate_program_identity(program_id)
        if program_id in seen:
            raise ValueError(f"MAP-Elites snapshot {field} must not contain duplicates")
        seen.add(program_id)
        restored.append(program_id)
    return restored
