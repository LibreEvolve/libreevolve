from __future__ import annotations

from dataclasses import dataclass
from typing import Any


MATH_OUTCOME_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_math_outcome_boundary.v1"
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
EXPECTED_SOURCE_SUMMARY = {
    "source_paper_id": "2506.13131",
    "source_section_id": "3.2",
    "source_claim": "curated constructive-math problem set breadth and outcome rates",
    "minimum_problem_instances": 51,
    "problem_instance_text": "over 50 mathematical problems",
    "minimum_branch_count": 6,
    "branch_text": "more than five different branches of mathematics",
    "rediscovered_best_known_percent_approx": 75.0,
    "improved_sota_percent_approx": 20.0,
    "verification_claim": "In all these cases, results were verified according to their provided mathematical definitions.",
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
_MISSING_EVIDENCE_KEYS = tuple(EXPECTED_MATH_OUTCOME_BOUNDARY["missing_evidence"].keys())


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
