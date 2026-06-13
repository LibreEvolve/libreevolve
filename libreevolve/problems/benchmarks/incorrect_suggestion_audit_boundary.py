from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


INCORRECT_SUGGESTION_AUDIT_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_incorrect_suggestion_audit_boundary.v1"
)
INCORRECT_SUGGESTION_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.incorrect_suggestion_audit_report.v1"
)
INCORRECT_SUGGESTION_REJUDGE_COVERAGE_SCHEMA = (
    "libreevolve.incorrect_suggestion_rejudge_coverage.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "local_execution_grounding_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "generated_candidate_count",
    "accepted_generated_count",
    "rejected_generated_count",
    "execution_filtered_count",
    "invalid_evaluation_count",
    "diff_or_parse_error_count",
    "archive_rejected_count",
    "accepted_invalid_count",
    "local_filter_rate",
    "accepted_invalid_rate",
    "rejection_reasons",
    "candidate_family_filter_rates",
    "initial_pool_distance_audit",
    "audit_sampling_policy",
    "audit_denominator",
    "audit_record_lifecycle_status",
    "independent_rejudge_coverage",
    "independent_rejudge_status",
    "false_acceptance_review",
    "false_rejection_review",
    "reference_or_statistical_oracle_sufficiency",
    "cross_run_proposal_lifecycle_table",
    "semantic_failed_proposal_retrieval",
    "audited_false_acceptance_rate",
    "audited_false_rejection_rate",
    "publication_strength_incorrect_suggestion_filtering",
)
EXPECTED_MISSING_EVIDENCE = {
    "independent_rejudge_of_accepted_candidates": (
        "zero_coverage_recorded_no_independent_rejudge"
    ),
    "independent_rejudge_of_rejected_candidates": (
        "zero_coverage_recorded_no_independent_rejudge"
    ),
    "reference_or_statistical_oracle_sufficiency": "not_recorded_locally",
    "sampled_audit_denominator_policy": "not_recorded_locally",
    "candidate_family_filter_rates": "not_recorded_locally",
    "beyond_initial_pool_novelty_audit": "not_recorded_locally",
    "cross_run_proposal_lifecycle_table": "not_recorded_locally",
    "semantic_failed_proposal_retrieval": "not_recorded_locally",
    "audited_false_acceptance_rate": "not_recorded_locally",
    "audited_false_rejection_rate": "not_recorded_locally",
}


@dataclass(frozen=True)
class IncorrectSuggestionAuditBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class IncorrectSuggestionAuditBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[IncorrectSuggestionAuditBoundaryIssue]


def incorrect_suggestion_audit_boundary_record() -> dict[str, Any]:
    """Return the current incorrect-suggestion audit boundary."""

    return {
        "schema": INCORRECT_SUGGESTION_AUDIT_BOUNDARY_SCHEMA,
        "runtime_report_schema": INCORRECT_SUGGESTION_RUNTIME_REPORT_SCHEMA,
        "rejudge_coverage_schema": INCORRECT_SUGGESTION_REJUDGE_COVERAGE_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve uses code execution and automatic evaluation to ground "
            "LLM-directed evolution, filter incorrect base-LLM suggestions, "
            "and move beyond the initial candidate pool"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "incorrect_suggestion_audit_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has local execution-grounding "
            "telemetry for generated, accepted, rejected, execution-filtered, "
            "invalid-evaluation, diff/parse-error, archive-rejected, and "
            "accepted-invalid candidates, plus explicit zero-coverage "
            "independent rejudge summaries, but does not claim independent rejudge "
            "coverage, reference/statistical-oracle sufficiency, sampled audit-"
            "denominator policy, candidate-family filter rates, beyond-initial-"
            "pool novelty audit, cross-run proposal lifecycle tables, semantic "
            "failed-proposal retrieval, audited false-acceptance or false-"
            "rejection rates, or publication-strength incorrect-suggestion "
            "filtering."
        ),
    }


def validate_incorrect_suggestion_audit_boundary(
    boundary: object | str | Path | None = None,
) -> IncorrectSuggestionAuditBoundaryValidation:
    data, read_issues = _load_boundary(
        incorrect_suggestion_audit_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return IncorrectSuggestionAuditBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[IncorrectSuggestionAuditBoundaryIssue] = []
    if data.get("schema") != INCORRECT_SUGGESTION_AUDIT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported incorrect-suggestion audit boundary schema"))
    if data.get("runtime_report_schema") != INCORRECT_SUGGESTION_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify incorrect-suggestion audit reports"))
    if data.get("rejudge_coverage_schema") != INCORRECT_SUGGESTION_REJUDGE_COVERAGE_SCHEMA:
        issues.append(_issue("invalid_rejudge_coverage_schema", "rejudge coverage schema must identify incorrect-suggestion rejudge coverage reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "filter incorrect" not in source_claim
        or "initial candidate pool" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify incorrect-suggestion filtering"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "incorrect_suggestion_audit_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to incorrect-suggestion audit reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "incorrect-suggestion audit boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim" not in boundary_text
        or "sampled audit-denominator policy" not in boundary_text
        or "candidate-family filter rates" not in boundary_text
        or "beyond-initial-pool novelty audit" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim independent audit evidence"))
    return IncorrectSuggestionAuditBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_incorrect_suggestion_audit_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_incorrect_suggestion_audit_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve incorrect-suggestion audit boundary",
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
) -> tuple[dict[str, Any] | None, list[IncorrectSuggestionAuditBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "incorrect-suggestion audit boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[IncorrectSuggestionAuditBoundaryIssue],
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
    issues: list[IncorrectSuggestionAuditBoundaryIssue],
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


def _issue(code: str, message: str) -> IncorrectSuggestionAuditBoundaryIssue:
    return IncorrectSuggestionAuditBoundaryIssue(code, message)
