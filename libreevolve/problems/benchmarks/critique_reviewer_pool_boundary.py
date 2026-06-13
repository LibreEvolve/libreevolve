from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CRITIQUE_REVIEWER_POOL_BOUNDARY_SCHEMA = (
    "libreevolve.critique_reviewer_pool_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("front_matter_overview", "2.4", "2.6")
EXPECTED_BOUNDARY_STATUS = "synchronous_first_last_valid_without_calibrated_reviewers"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "configured_reviewer_specs",
    "manifest_safe_reviewer_names",
    "optional_reviewer_prompts",
    "reviewer_role_labels",
    "role_backend_routing_compatibility",
    "role_budget_accounting_compatibility",
    "bounded_synchronous_pool",
    "first_valid_aggregation",
    "last_valid_aggregation",
    "reviewer_parser_status",
    "valid_revision_counts",
    "selected_reviewer_provenance",
    "reviewer_elapsed_seconds",
    "reviewer_outcome_status",
    "inline_runtime_artifact_policy",
    "independent_reviewer_task_definition",
    "reviewer_generator_role_separation",
    "critique_to_revision_attribution",
    "reviewer_score_to_selection_policy",
    "reviewer_budget_quota_policy",
    "reviewer_failure_isolation_report",
    "equal_budget_no_reviewer_comparison",
    "async_reviewer_overlap",
    "calibrated_reviewer_score_report",
    "reviewer_reliability_ablation",
    "per_reviewer_provider_isolation",
    "external_reviewer_timeout_artifacts",
)
EXPECTED_MISSING_EVIDENCE = {
    "independent_reviewer_task_definition": "not_recorded_locally",
    "reviewer_generator_role_separation": "not_recorded_locally",
    "critique_to_revision_attribution": "not_recorded_locally",
    "reviewer_score_to_selection_policy": "not_recorded_locally",
    "reviewer_budget_quota_policy": "not_recorded_locally",
    "reviewer_failure_isolation_report": "not_recorded_locally",
    "equal_budget_no_reviewer_comparison": "not_recorded_locally",
    "async_reviewer_overlap": "not_recorded_locally",
    "calibrated_reviewer_score_report": "not_recorded_locally",
    "reviewer_reliability_ablation": "not_recorded_locally",
    "per_reviewer_provider_isolation": "not_recorded_locally",
    "external_reviewer_timeout_artifacts": "not_recorded_locally",
}


@dataclass(frozen=True)
class CritiqueReviewerPoolBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CritiqueReviewerPoolBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CritiqueReviewerPoolBoundaryIssue]


def critique_reviewer_pool_boundary_record() -> dict[str, Any]:
    """Return the synchronous reviewer pool versus calibrated reviewer boundary."""

    return {
        "schema": CRITIQUE_REVIEWER_POOL_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve-style critique and feedback channels should provide "
            "attributable model-review signal under explicit budget policy; "
            "the paper names critique in the front overview, while detailed "
            "LLM-feedback and budget/orchestration evidence is in Sections "
            "2.4 and 2.6"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_pool_schema": "libreevolve.critique_reviewer_pool.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has configured reviewer "
            "specs, manifest-safe reviewer names, optional reviewer prompts, "
            "reviewer role labels, role backend routing compatibility, role "
            "budget accounting compatibility, a bounded synchronous reviewer "
            "pool, first-valid and last-valid aggregation, reviewer parser "
            "status, valid revision counts, selected reviewer provenance, "
            "reviewer elapsed seconds, reviewer outcome status, and inline "
            "runtime artifact policy. It does not claim async reviewer overlap, "
            "independent reviewer task definitions, reviewer/generator role "
            "separation proof, critique-to-revision attribution, reviewer "
            "score-to-selection policy, reviewer budget quota policy, reviewer "
            "failure-isolation reports, equal-budget no-reviewer comparisons, "
            "calibrated reviewer-score reports, reviewer reliability ablations, "
            "per-reviewer provider isolation, or external reviewer timeout "
            "artifacts."
        ),
    }


def validate_critique_reviewer_pool_boundary(
    boundary: object | str | Path | None = None,
) -> CritiqueReviewerPoolBoundaryValidation:
    data, read_issues = _load_boundary(
        critique_reviewer_pool_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CritiqueReviewerPoolBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CritiqueReviewerPoolBoundaryIssue] = []
    if data.get("schema") != CRITIQUE_REVIEWER_POOL_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported critique reviewer pool boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be front_matter_overview, 2.4, and 2.6"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "critique" not in source_claim
        or "model-review signal" not in source_claim
        or "budget policy" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify critique/reviewer signal under budget policy"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_pool_schema") != "libreevolve.critique_reviewer_pool.v1":
        issues.append(_issue("invalid_runtime_pool_schema", "runtime_pool_schema must be libreevolve.critique_reviewer_pool.v1"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "critique reviewer pool boundary must not claim calibrated reviewer readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim async reviewer overlap" not in boundary_text
        or "independent reviewer task definitions" not in boundary_text
        or "reviewer/generator role separation proof" not in boundary_text
        or "critique-to-revision attribution" not in boundary_text
        or "reviewer score-to-selection policy" not in boundary_text
        or "equal-budget no-reviewer comparisons" not in boundary_text
        or "calibrated reviewer-score reports" not in boundary_text
        or "per-reviewer provider isolation" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate synchronous reviewer telemetry from calibrated reviewer orchestration"))
    return CritiqueReviewerPoolBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_critique_reviewer_pool_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_critique_reviewer_pool_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Critique reviewer pool boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[CritiqueReviewerPoolBoundaryIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(boundary).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "critique reviewer pool boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[CritiqueReviewerPoolBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_evidence_field", f"missing required evidence fields: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_evidence_field", f"unknown required evidence fields: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[CritiqueReviewerPoolBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> CritiqueReviewerPoolBoundaryIssue:
    return CritiqueReviewerPoolBoundaryIssue(code, message)
