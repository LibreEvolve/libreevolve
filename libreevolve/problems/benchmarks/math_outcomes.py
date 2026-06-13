from __future__ import annotations

from dataclasses import dataclass
from typing import Any


MATH_OUTCOME_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_math_outcome_boundary.v1"
MATH_STARTING_CONSTRUCTION_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_math_starting_construction_boundary.v1"
MATH_HEURISTIC_HANDOFF_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_math_heuristic_handoff_boundary.v1"
MATH_HEURISTIC_STAGE_SEQUENCE_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_math_heuristic_stage_sequence_boundary.v1"
EXPECTED_SOURCE_SECTION_IDS = ("3.2",)
EXPECTED_REQUIRED_INSTANCE_FIELDS = (
    "instance_id",
    "problem_family_id",
    "branch_label",
    "parameter_setting",
    "prior_best_reference",
    "prior_best_value",
    "alphaevolve_result_value",
    "outcome_status",
    "construction_artifact_path",
    "construction_artifact_sha256",
    "verifier_artifact_path",
    "verifier_artifact_sha256",
    "starting_construction_class",
)
EXPECTED_REQUIRED_AGGREGATE_FIELDS = (
    "total_problem_instances",
    "branch_count",
    "rediscovered_best_known_count",
    "improved_sota_count",
    "failed_or_unmatched_count",
    "rediscovered_best_known_percent",
    "improved_sota_percent",
    "percentage_rounding_policy",
    "verified_case_count",
)
EXPECTED_REQUIRED_STARTING_CONSTRUCTION_FIELDS = (
    "instance_id",
    "problem_family_id",
    "starting_construction_class",
    "starting_construction_artifact_path",
    "starting_construction_artifact_sha256",
    "generator_id",
    "random_seed",
    "baseline_metric_name",
    "baseline_metric_value",
    "prior_best_visibility_policy",
    "prior_best_seeding_policy",
)
EXPECTED_REQUIRED_HEURISTIC_HANDOFF_FIELDS = (
    "instance_id",
    "heuristic_program_id",
    "heuristic_program_artifact_path",
    "heuristic_program_artifact_sha256",
    "fixed_time_budget_seconds",
    "incumbent_construction_artifact_path",
    "incumbent_construction_artifact_sha256",
    "previous_best_heuristic_id",
    "produced_construction_artifact_path",
    "produced_construction_artifact_sha256",
    "before_metric_value",
    "after_metric_value",
    "improvement_delta",
    "evaluator_score",
    "verifier_artifact_path",
    "verifier_artifact_sha256",
)
EXPECTED_REQUIRED_HEURISTIC_STAGE_FIELDS = (
    "instance_id",
    "stage_index",
    "heuristic_program_id",
    "stage_role",
    "input_construction_artifact_path",
    "input_construction_artifact_sha256",
    "output_construction_artifact_path",
    "output_construction_artifact_sha256",
    "fixed_time_budget_seconds",
    "before_metric_value",
    "after_metric_value",
    "improvement_delta",
    "verifier_artifact_path",
    "verifier_artifact_sha256",
)
EXPECTED_SOURCE_SUMMARY = {
    "source_paper_id": "2506.13131",
    "source_section_id": "3.2",
    "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
    "source_claim": "curated constructive-math problem set breadth and outcome rates",
    "minimum_problem_instances": 51,
    "problem_instance_text": "over 50 mathematical problems",
    "minimum_branch_count": 6,
    "branch_text": "more than five different branches of mathematics",
    "rediscovered_best_known_percent_approx": 75.0,
    "improved_sota_percent_approx": 20.0,
    "verification_claim": "In all these cases, results were verified according to their provided mathematical definitions.",
}
EXPECTED_STARTING_CONSTRUCTION_SUMMARY = {
    "source_paper_id": "2506.13131",
    "source_section_id": "3.2",
    "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
    "source_claim": "constructive-math runs started from simple or random constructions",
    "starting_point_text": "the initial starting point was a simple or a random construction",
    "allowed_claimed_starting_classes": ["simple", "random"],
    "unsupported_without_explicit_label": ["human_seeded", "prior_art_seeded", "expert_seeded"],
}
EXPECTED_HEURISTIC_HANDOFF_SUMMARY = {
    "source_paper_id": "2506.13131",
    "source_section_id": "3.2",
    "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
    "source_claim": "constructive-math programs are search heuristics that produce constructions",
    "methodology_text": "evolve heuristic search algorithms rather than directly evolving the constructions themselves",
    "program_role": "program representing a search heuristic",
    "fixed_budget_text": "given a fixed time budget",
    "example_budget_seconds": 1000,
    "incumbent_input_text": "shown the best construction found by the previous best heuristic",
    "goal_text": "leverage this starting point and the allotted time to find an even better construction",
    "selection_target": "heuristics effective at improving already high-quality solutions",
}
EXPECTED_HEURISTIC_STAGE_SEQUENCE_SUMMARY = {
    "source_paper_id": "2506.13131",
    "source_section_id": "3.2",
    "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
    "source_claim": "final constructions often result from a sequence of specialized heuristics",
    "sequence_text": "The final constructions were often the result of a sequence of different, specialized heuristics discovered by AlphaEvolve",
    "early_stage_role": "early_large_gains_from_random_or_simple_initial_states",
    "early_stage_text": "early heuristics proficient at making large gains from random or simple initial states",
    "later_stage_role": "later_fine_tuning_near_optimal_configurations",
    "later_stage_text": "later heuristics adept at fine-tuning near-optimal configurations",
    "minimum_stage_roles": ["early_large_gains_from_random_or_simple_initial_states", "later_fine_tuning_near_optimal_configurations"],
}
EXPECTED_MATH_OUTCOME_BOUNDARY = {
    "schema": MATH_OUTCOME_BOUNDARY_SCHEMA,
    **EXPECTED_SOURCE_SUMMARY,
    "status": "not_recorded_locally",
    "scope_boundary": "This boundary records the paper's Section 3.2 aggregate claim, but does not claim local per-problem outcome rows, construction artifacts, verifier artifacts, or reproduced aggregate percentages.",
    "required_instance_fields": list(EXPECTED_REQUIRED_INSTANCE_FIELDS),
    "required_aggregate_fields": list(EXPECTED_REQUIRED_AGGREGATE_FIELDS),
    "missing_evidence": {
        "per_problem_instance_rows": "not_recorded_locally",
        "branch_taxonomy_rows": "not_recorded_locally",
        "prior_best_reference_rows": "not_recorded_locally",
        "construction_artifacts": "not_recorded_locally",
        "verifier_artifacts": "not_recorded_locally",
        "aggregate_counts": "not_recorded_locally",
        "aggregate_percentage_recomputation": "not_recorded_locally",
    },
}
EXPECTED_STARTING_CONSTRUCTION_BOUNDARY = {
    "schema": MATH_STARTING_CONSTRUCTION_BOUNDARY_SCHEMA,
    **EXPECTED_STARTING_CONSTRUCTION_SUMMARY,
    "status": "not_recorded_locally",
    "scope_boundary": "This boundary records the paper's Section 3.2 simple-or-random starting-point claim, but does not claim local per-instance starting construction artifacts, random seeds, baseline metrics, or prior-best seeding policy evidence.",
    "required_starting_construction_fields": list(EXPECTED_REQUIRED_STARTING_CONSTRUCTION_FIELDS),
    "missing_evidence": {
        "per_instance_starting_rows": "not_recorded_locally",
        "starting_construction_artifacts": "not_recorded_locally",
        "random_generator_and_seed_records": "not_recorded_locally",
        "baseline_metric_values": "not_recorded_locally",
        "prior_best_visibility_policy": "not_recorded_locally",
        "prior_best_seeding_policy": "not_recorded_locally",
    },
}
EXPECTED_HEURISTIC_HANDOFF_BOUNDARY = {
    "schema": MATH_HEURISTIC_HANDOFF_BOUNDARY_SCHEMA,
    **EXPECTED_HEURISTIC_HANDOFF_SUMMARY,
    "status": "not_recorded_locally",
    "scope_boundary": "This boundary records the paper's Section 3.2 heuristic-to-construction handoff, but does not claim local heuristic program artifacts, incumbent construction inputs, fixed-budget execution records, produced construction artifacts, scores, or verifier evidence.",
    "required_handoff_fields": list(EXPECTED_REQUIRED_HEURISTIC_HANDOFF_FIELDS),
    "missing_evidence": {
        "per_instance_handoff_rows": "not_recorded_locally",
        "heuristic_program_artifacts": "not_recorded_locally",
        "fixed_budget_execution_records": "not_recorded_locally",
        "incumbent_construction_artifacts": "not_recorded_locally",
        "produced_construction_artifacts": "not_recorded_locally",
        "before_after_metric_values": "not_recorded_locally",
        "evaluator_scores": "not_recorded_locally",
        "verifier_artifacts": "not_recorded_locally",
    },
}
EXPECTED_HEURISTIC_STAGE_SEQUENCE_BOUNDARY = {
    "schema": MATH_HEURISTIC_STAGE_SEQUENCE_BOUNDARY_SCHEMA,
    **EXPECTED_HEURISTIC_STAGE_SEQUENCE_SUMMARY,
    "status": "not_recorded_locally",
    "scope_boundary": "This boundary records the paper's Section 3.2 multi-stage heuristic sequence claim, but does not claim local per-stage heuristic artifacts, ordered construction transitions, stage roles, improvement deltas, or verifier evidence.",
    "required_stage_fields": list(EXPECTED_REQUIRED_HEURISTIC_STAGE_FIELDS),
    "missing_evidence": {
        "per_stage_rows": "not_recorded_locally",
        "stage_ordering_records": "not_recorded_locally",
        "heuristic_program_artifacts": "not_recorded_locally",
        "input_output_construction_artifacts": "not_recorded_locally",
        "stage_role_labels": "not_recorded_locally",
        "improvement_delta_records": "not_recorded_locally",
        "verifier_artifacts": "not_recorded_locally",
    },
}
_MISSING_EVIDENCE_KEYS = tuple(EXPECTED_MATH_OUTCOME_BOUNDARY["missing_evidence"].keys())
_STARTING_MISSING_EVIDENCE_KEYS = tuple(EXPECTED_STARTING_CONSTRUCTION_BOUNDARY["missing_evidence"].keys())
_HANDOFF_MISSING_EVIDENCE_KEYS = tuple(EXPECTED_HEURISTIC_HANDOFF_BOUNDARY["missing_evidence"].keys())
_STAGE_SEQUENCE_MISSING_EVIDENCE_KEYS = tuple(EXPECTED_HEURISTIC_STAGE_SEQUENCE_BOUNDARY["missing_evidence"].keys())


@dataclass(frozen=True)
class MathOutcomeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MathOutcomeBoundaryValidation:
    ok: bool
    status: str | None
    minimum_problem_instances: int | None
    minimum_branch_count: int | None
    issues: list[MathOutcomeBoundaryIssue]


def alphaevolve_math_outcome_boundary() -> dict[str, Any]:
    """Return the Section 3.2 aggregate-claim absence boundary."""

    return {
        **EXPECTED_MATH_OUTCOME_BOUNDARY,
        "required_instance_fields": list(EXPECTED_REQUIRED_INSTANCE_FIELDS),
        "required_aggregate_fields": list(EXPECTED_REQUIRED_AGGREGATE_FIELDS),
        "missing_evidence": dict(EXPECTED_MATH_OUTCOME_BOUNDARY["missing_evidence"]),
    }


def alphaevolve_math_starting_construction_boundary() -> dict[str, Any]:
    """Return the Section 3.2 starting-construction absence boundary."""

    return {
        **EXPECTED_STARTING_CONSTRUCTION_BOUNDARY,
        "allowed_claimed_starting_classes": list(EXPECTED_STARTING_CONSTRUCTION_SUMMARY["allowed_claimed_starting_classes"]),
        "unsupported_without_explicit_label": list(EXPECTED_STARTING_CONSTRUCTION_SUMMARY["unsupported_without_explicit_label"]),
        "required_starting_construction_fields": list(EXPECTED_REQUIRED_STARTING_CONSTRUCTION_FIELDS),
        "missing_evidence": dict(EXPECTED_STARTING_CONSTRUCTION_BOUNDARY["missing_evidence"]),
    }


def alphaevolve_math_heuristic_handoff_boundary() -> dict[str, Any]:
    """Return the Section 3.2 heuristic-to-construction handoff absence boundary."""

    return {
        **EXPECTED_HEURISTIC_HANDOFF_BOUNDARY,
        "required_handoff_fields": list(EXPECTED_REQUIRED_HEURISTIC_HANDOFF_FIELDS),
        "missing_evidence": dict(EXPECTED_HEURISTIC_HANDOFF_BOUNDARY["missing_evidence"]),
    }


def alphaevolve_math_heuristic_stage_sequence_boundary() -> dict[str, Any]:
    """Return the Section 3.2 multi-stage heuristic sequence absence boundary."""

    return {
        **EXPECTED_HEURISTIC_STAGE_SEQUENCE_BOUNDARY,
        "minimum_stage_roles": list(EXPECTED_HEURISTIC_STAGE_SEQUENCE_SUMMARY["minimum_stage_roles"]),
        "required_stage_fields": list(EXPECTED_REQUIRED_HEURISTIC_STAGE_FIELDS),
        "missing_evidence": dict(EXPECTED_HEURISTIC_STAGE_SEQUENCE_BOUNDARY["missing_evidence"]),
    }


def validate_math_outcome_boundary(boundary: object | None = None) -> MathOutcomeBoundaryValidation:
    """Validate Section 3.2 aggregate constructive-math claim metadata."""

    data = alphaevolve_math_outcome_boundary() if boundary is None else boundary
    if not isinstance(data, dict):
        return MathOutcomeBoundaryValidation(False, None, None, None, [MathOutcomeBoundaryIssue("invalid_boundary", "boundary must be an object")])
    issues: list[MathOutcomeBoundaryIssue] = []
    for field, expected_value in EXPECTED_MATH_OUTCOME_BOUNDARY.items():
        if field in {"required_instance_fields", "required_aggregate_fields", "missing_evidence"}:
            continue
        actual = data.get(field)
        if isinstance(expected_value, float):
            if isinstance(actual, bool) or not isinstance(actual, (int, float)) or float(actual) != expected_value:
                issues.append(MathOutcomeBoundaryIssue(f"invalid_{field}", f"{field} must match the AlphaEvolve Section 3.2 aggregate claim"))
        elif actual != expected_value:
            issues.append(MathOutcomeBoundaryIssue(f"invalid_{field}", f"{field} must match the AlphaEvolve Section 3.2 aggregate claim"))
    status = data.get("status")
    if status != "not_recorded_locally":
        issues.append(MathOutcomeBoundaryIssue("invalid_status", "aggregate math outcome boundary must remain not_recorded_locally until per-instance rows and artifacts exist"))
    if data.get("required_instance_fields") != list(EXPECTED_REQUIRED_INSTANCE_FIELDS):
        issues.append(MathOutcomeBoundaryIssue("invalid_required_instance_fields", "required_instance_fields must enumerate future per-problem outcome rows"))
    if data.get("required_aggregate_fields") != list(EXPECTED_REQUIRED_AGGREGATE_FIELDS):
        issues.append(MathOutcomeBoundaryIssue("invalid_required_aggregate_fields", "required_aggregate_fields must enumerate future aggregate count and percentage fields"))
    missing = data.get("missing_evidence")
    if not isinstance(missing, dict):
        issues.append(MathOutcomeBoundaryIssue("invalid_missing_evidence", "missing_evidence must be an object"))
    else:
        for key in _MISSING_EVIDENCE_KEYS:
            if missing.get(key) != "not_recorded_locally":
                issues.append(MathOutcomeBoundaryIssue(f"invalid_missing_{key}", f"{key} must remain not_recorded_locally until evidence artifacts exist"))
        extra = set(missing) - set(_MISSING_EVIDENCE_KEYS)
        if extra:
            issues.append(MathOutcomeBoundaryIssue("extra_missing_evidence", "missing_evidence contains unknown keys"))
    min_instances = data.get("minimum_problem_instances")
    min_branches = data.get("minimum_branch_count")
    if isinstance(min_instances, bool) or not isinstance(min_instances, int) or min_instances <= 50:
        issues.append(MathOutcomeBoundaryIssue("invalid_minimum_problem_instances", "over 50 problem instances requires a minimum integer count above 50"))
        min_instances = None
    if isinstance(min_branches, bool) or not isinstance(min_branches, int) or min_branches <= 5:
        issues.append(MathOutcomeBoundaryIssue("invalid_minimum_branch_count", "more than five branches requires a minimum integer count above 5"))
        min_branches = None
    rediscovered = data.get("rediscovered_best_known_percent_approx")
    improved = data.get("improved_sota_percent_approx")
    if (
        isinstance(rediscovered, (int, float))
        and not isinstance(rediscovered, bool)
        and isinstance(improved, (int, float))
        and not isinstance(improved, bool)
        and float(rediscovered) + float(improved) > 100.0
    ):
        issues.append(MathOutcomeBoundaryIssue("invalid_aggregate_percent_sum", "rediscovered and improved approximate percentages cannot exceed 100"))
    scope_boundary = data.get("scope_boundary")
    if not isinstance(scope_boundary, str) or "does not claim" not in scope_boundary:
        issues.append(MathOutcomeBoundaryIssue("missing_scope_boundary", "scope_boundary must state that local aggregate evidence is not claimed"))
    return MathOutcomeBoundaryValidation(
        ok=not issues,
        status=status if isinstance(status, str) else None,
        minimum_problem_instances=min_instances,
        minimum_branch_count=min_branches,
        issues=issues,
    )


def validate_math_starting_construction_boundary(boundary: object | None = None) -> MathOutcomeBoundaryValidation:
    """Validate Section 3.2 simple-or-random starting-construction metadata."""

    data = alphaevolve_math_starting_construction_boundary() if boundary is None else boundary
    if not isinstance(data, dict):
        return MathOutcomeBoundaryValidation(False, None, None, None, [MathOutcomeBoundaryIssue("invalid_boundary", "boundary must be an object")])
    issues: list[MathOutcomeBoundaryIssue] = []
    for field, expected_value in EXPECTED_STARTING_CONSTRUCTION_BOUNDARY.items():
        if field in {"required_starting_construction_fields", "missing_evidence"}:
            continue
        actual = data.get(field)
        if actual != expected_value:
            issues.append(MathOutcomeBoundaryIssue(f"invalid_starting_{field}", f"{field} must match the AlphaEvolve Section 3.2 starting-construction claim"))
    status = data.get("status")
    if status != "not_recorded_locally":
        issues.append(MathOutcomeBoundaryIssue("invalid_starting_status", "starting-construction boundary must remain not_recorded_locally until per-instance seed artifacts exist"))
    if data.get("required_starting_construction_fields") != list(EXPECTED_REQUIRED_STARTING_CONSTRUCTION_FIELDS):
        issues.append(MathOutcomeBoundaryIssue("invalid_required_starting_construction_fields", "required_starting_construction_fields must enumerate future per-instance starting construction rows"))
    classes = data.get("allowed_claimed_starting_classes")
    if classes != ["simple", "random"]:
        issues.append(MathOutcomeBoundaryIssue("invalid_allowed_starting_classes", "Section 3.2 claimed starting classes must stay limited to simple and random"))
    unsupported = data.get("unsupported_without_explicit_label")
    if not isinstance(unsupported, list) or not {"human_seeded", "prior_art_seeded", "expert_seeded"}.issubset(set(unsupported)):
        issues.append(MathOutcomeBoundaryIssue("invalid_unsupported_starting_classes", "human/prior-art/expert seeded starts must be explicitly labeled outside the simple-or-random claim"))
    missing = data.get("missing_evidence")
    if not isinstance(missing, dict):
        issues.append(MathOutcomeBoundaryIssue("invalid_starting_missing_evidence", "missing_evidence must be an object"))
    else:
        for key in _STARTING_MISSING_EVIDENCE_KEYS:
            if missing.get(key) != "not_recorded_locally":
                issues.append(MathOutcomeBoundaryIssue(f"invalid_starting_missing_{key}", f"{key} must remain not_recorded_locally until starting-construction evidence artifacts exist"))
        extra = set(missing) - set(_STARTING_MISSING_EVIDENCE_KEYS)
        if extra:
            issues.append(MathOutcomeBoundaryIssue("extra_starting_missing_evidence", "starting missing_evidence contains unknown keys"))
    scope_boundary = data.get("scope_boundary")
    if not isinstance(scope_boundary, str) or "does not claim" not in scope_boundary:
        issues.append(MathOutcomeBoundaryIssue("missing_starting_scope_boundary", "scope_boundary must state that local starting-construction evidence is not claimed"))
    return MathOutcomeBoundaryValidation(
        ok=not issues,
        status=status if isinstance(status, str) else None,
        minimum_problem_instances=None,
        minimum_branch_count=None,
        issues=issues,
    )


def validate_math_heuristic_handoff_boundary(boundary: object | None = None) -> MathOutcomeBoundaryValidation:
    """Validate Section 3.2 heuristic program handoff metadata."""

    data = alphaevolve_math_heuristic_handoff_boundary() if boundary is None else boundary
    if not isinstance(data, dict):
        return MathOutcomeBoundaryValidation(False, None, None, None, [MathOutcomeBoundaryIssue("invalid_boundary", "boundary must be an object")])
    issues: list[MathOutcomeBoundaryIssue] = []
    for field, expected_value in EXPECTED_HEURISTIC_HANDOFF_BOUNDARY.items():
        if field in {"required_handoff_fields", "missing_evidence"}:
            continue
        actual = data.get(field)
        if actual != expected_value:
            issues.append(MathOutcomeBoundaryIssue(f"invalid_handoff_{field}", f"{field} must match the AlphaEvolve Section 3.2 heuristic-handoff claim"))
    status = data.get("status")
    if status != "not_recorded_locally":
        issues.append(MathOutcomeBoundaryIssue("invalid_handoff_status", "heuristic handoff boundary must remain not_recorded_locally until per-instance handoff artifacts exist"))
    if data.get("required_handoff_fields") != list(EXPECTED_REQUIRED_HEURISTIC_HANDOFF_FIELDS):
        issues.append(MathOutcomeBoundaryIssue("invalid_required_handoff_fields", "required_handoff_fields must enumerate future heuristic program, incumbent, produced construction, score, and verifier fields"))
    budget = data.get("example_budget_seconds")
    if isinstance(budget, bool) or not isinstance(budget, int) or budget <= 0:
        issues.append(MathOutcomeBoundaryIssue("invalid_handoff_example_budget_seconds", "example fixed budget must be a positive integer number of seconds"))
    missing = data.get("missing_evidence")
    if not isinstance(missing, dict):
        issues.append(MathOutcomeBoundaryIssue("invalid_handoff_missing_evidence", "missing_evidence must be an object"))
    else:
        for key in _HANDOFF_MISSING_EVIDENCE_KEYS:
            if missing.get(key) != "not_recorded_locally":
                issues.append(MathOutcomeBoundaryIssue(f"invalid_handoff_missing_{key}", f"{key} must remain not_recorded_locally until heuristic-handoff evidence artifacts exist"))
        extra = set(missing) - set(_HANDOFF_MISSING_EVIDENCE_KEYS)
        if extra:
            issues.append(MathOutcomeBoundaryIssue("extra_handoff_missing_evidence", "handoff missing_evidence contains unknown keys"))
    scope_boundary = data.get("scope_boundary")
    if not isinstance(scope_boundary, str) or "does not claim" not in scope_boundary:
        issues.append(MathOutcomeBoundaryIssue("missing_handoff_scope_boundary", "scope_boundary must state that local heuristic-handoff evidence is not claimed"))
    return MathOutcomeBoundaryValidation(
        ok=not issues,
        status=status if isinstance(status, str) else None,
        minimum_problem_instances=None,
        minimum_branch_count=None,
        issues=issues,
    )


def validate_math_heuristic_stage_sequence_boundary(boundary: object | None = None) -> MathOutcomeBoundaryValidation:
    """Validate Section 3.2 staged heuristic sequence metadata."""

    data = alphaevolve_math_heuristic_stage_sequence_boundary() if boundary is None else boundary
    if not isinstance(data, dict):
        return MathOutcomeBoundaryValidation(False, None, None, None, [MathOutcomeBoundaryIssue("invalid_boundary", "boundary must be an object")])
    issues: list[MathOutcomeBoundaryIssue] = []
    for field, expected_value in EXPECTED_HEURISTIC_STAGE_SEQUENCE_BOUNDARY.items():
        if field in {"required_stage_fields", "missing_evidence"}:
            continue
        actual = data.get(field)
        if actual != expected_value:
            issues.append(MathOutcomeBoundaryIssue(f"invalid_stage_sequence_{field}", f"{field} must match the AlphaEvolve Section 3.2 stage-sequence claim"))
    status = data.get("status")
    if status != "not_recorded_locally":
        issues.append(MathOutcomeBoundaryIssue("invalid_stage_sequence_status", "stage-sequence boundary must remain not_recorded_locally until per-stage artifacts exist"))
    if data.get("required_stage_fields") != list(EXPECTED_REQUIRED_HEURISTIC_STAGE_FIELDS):
        issues.append(MathOutcomeBoundaryIssue("invalid_required_stage_fields", "required_stage_fields must enumerate future stage, construction transition, metric, and verifier fields"))
    roles = data.get("minimum_stage_roles")
    if roles != list(EXPECTED_HEURISTIC_STAGE_SEQUENCE_SUMMARY["minimum_stage_roles"]):
        issues.append(MathOutcomeBoundaryIssue("invalid_stage_sequence_roles", "stage-sequence boundary must preserve early broad-gain and later fine-tuning roles"))
    missing = data.get("missing_evidence")
    if not isinstance(missing, dict):
        issues.append(MathOutcomeBoundaryIssue("invalid_stage_sequence_missing_evidence", "missing_evidence must be an object"))
    else:
        for key in _STAGE_SEQUENCE_MISSING_EVIDENCE_KEYS:
            if missing.get(key) != "not_recorded_locally":
                issues.append(MathOutcomeBoundaryIssue(f"invalid_stage_sequence_missing_{key}", f"{key} must remain not_recorded_locally until stage-sequence evidence artifacts exist"))
        extra = set(missing) - set(_STAGE_SEQUENCE_MISSING_EVIDENCE_KEYS)
        if extra:
            issues.append(MathOutcomeBoundaryIssue("extra_stage_sequence_missing_evidence", "stage-sequence missing_evidence contains unknown keys"))
    scope_boundary = data.get("scope_boundary")
    if not isinstance(scope_boundary, str) or "does not claim" not in scope_boundary:
        issues.append(MathOutcomeBoundaryIssue("missing_stage_sequence_scope_boundary", "scope_boundary must state that local stage-sequence evidence is not claimed"))
    return MathOutcomeBoundaryValidation(
        ok=not issues,
        status=status if isinstance(status, str) else None,
        minimum_problem_instances=None,
        minimum_branch_count=None,
        issues=issues,
    )
