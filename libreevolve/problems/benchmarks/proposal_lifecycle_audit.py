from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROPOSAL_LIFECYCLE_AUDIT_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_proposal_lifecycle_audit_boundary.v1"
)
PROPOSAL_LIFECYCLE_RUNTIME_REPORT_SCHEMA = "libreevolve.proposal_lifecycle_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "not_independently_audited"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "proposal_id",
    "candidate_id",
    "llm_call_id",
    "mutation_hash",
    "execution_validity",
    "archive_admission_status",
    "primary_evaluator_score",
    "candidate_family_label",
    "initial_pool_distance_ref",
    "audit_sampling_policy",
    "audit_denominator",
    "independent_rejudge_status",
    "reference_or_statistical_oracle_id",
    "benchmark_oracle_sufficiency_label",
    "false_acceptance_review_status",
    "false_rejection_review_status",
    "cross_run_proposal_table_ref",
    "semantic_failed_proposal_retrieval_ref",
)
EXPECTED_MISSING_EVIDENCE = {
    "accepted_proposal_rejudge_rows": "not_recorded_locally",
    "rejected_proposal_rejudge_rows": "not_recorded_locally",
    "reference_or_statistical_oracle_records": "not_recorded_locally",
    "benchmark_oracle_sufficiency_labels": "not_recorded_locally",
    "sampled_audit_denominator_policy": "not_recorded_locally",
    "candidate_family_filter_rates": "not_recorded_locally",
    "beyond_initial_pool_novelty_audit": "not_recorded_locally",
    "cross_run_proposal_lifecycle_table": "not_recorded_locally",
    "semantic_failed_proposal_retrieval": "not_recorded_locally",
    "audited_false_acceptance_rate": "not_recorded_locally",
    "audited_false_rejection_rate": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProposalLifecycleAuditBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProposalLifecycleAuditBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ProposalLifecycleAuditBoundaryIssue]


def proposal_lifecycle_audit_boundary_record() -> dict[str, Any]:
    """Return the current independent-audit absence boundary for proposal lifecycle evidence."""

    return {
        "schema": PROPOSAL_LIFECYCLE_AUDIT_BOUNDARY_SCHEMA,
        "runtime_report_schema": PROPOSAL_LIFECYCLE_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "execution and automatic evaluation ground LLM-directed evolution "
            "and filter incorrect base-LLM suggestions while enabling accepted "
            "candidates to move beyond the initial candidate pool"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "proposal_lifecycle_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has local proposal lifecycle "
            "execution-grounding evidence, but does not claim independent rejudge "
            "or reference/statistical-oracle audit evidence for accepted and "
            "rejected proposals, sampled audit-denominator policy, candidate-"
            "family filter rates, beyond-initial-pool novelty audit, cross-run "
            "proposal lifecycle tables, semantic failed-proposal retrieval, "
            "benchmark-specific oracle sufficiency, or audited false-acceptance "
            "and false-rejection rates."
        ),
    }


def validate_proposal_lifecycle_audit_boundary(
    boundary: object | str | Path | None = None,
) -> ProposalLifecycleAuditBoundaryValidation:
    data, read_issues = _load_boundary(
        proposal_lifecycle_audit_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ProposalLifecycleAuditBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ProposalLifecycleAuditBoundaryIssue] = []
    if data.get("schema") != PROPOSAL_LIFECYCLE_AUDIT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported proposal lifecycle audit boundary schema"))
    if data.get("runtime_report_schema") != PROPOSAL_LIFECYCLE_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify proposal lifecycle reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if (
        not isinstance(data.get("source_claim"), str)
        or "filter incorrect" not in data["source_claim"]
        or "initial candidate pool" not in data["source_claim"]
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify incorrect-suggestion filtering"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "proposal_lifecycle_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to proposal lifecycle reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "proposal lifecycle audit boundary must not claim paper readiness"))
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
    return ProposalLifecycleAuditBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_proposal_lifecycle_audit_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_proposal_lifecycle_audit_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve proposal lifecycle audit boundary",
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
) -> tuple[dict[str, Any] | None, list[ProposalLifecycleAuditBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "proposal lifecycle audit boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ProposalLifecycleAuditBoundaryIssue],
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
    issues: list[ProposalLifecycleAuditBoundaryIssue],
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


def _issue(code: str, message: str) -> ProposalLifecycleAuditBoundaryIssue:
    return ProposalLifecycleAuditBoundaryIssue(code, message)
