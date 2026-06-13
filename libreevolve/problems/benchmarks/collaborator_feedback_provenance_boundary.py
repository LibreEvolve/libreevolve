from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


COLLABORATOR_FEEDBACK_PROVENANCE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_collaborator_feedback_provenance_boundary.v1"
)
COLLABORATOR_FEEDBACK_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.collaborator_feedback_provenance_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("Acknowledgements",)
EXPECTED_BOUNDARY_STATUS = "metadata_contract_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "metadata_present",
    "diverse_use_case_cohorts",
    "cohort_identity_or_safe_label_recorded",
    "minimum_cohort_coverage_policy",
    "feedback_event_ids_recorded",
    "feedback_event_source_artifacts",
    "affected_workflow_areas_recorded",
    "affected_workflow_taxonomy",
    "change_artifact_links_recorded",
    "code_or_docs_diff_links",
    "validation_outcomes_recorded",
    "validation_rerun_artifacts",
    "privacy_redaction_policy_recorded",
    "privacy_redaction_artifact_links",
    "collaborator_review_or_owner_signoff",
    "review_or_signoff_identity_recorded",
    "review_or_signoff_version_recorded",
    "longitudinal_feedback_followup",
    "robustness_or_versatility_claim_linked",
    "claim_to_feedback_traceability",
    "external_feedback_separated_from_llm_feedback",
    "alphaevolve_collaborator_feedback_parity",
    "representative_fixture_feedback_records",
    "paper_facing_certification_rows",
    "workflow_change_artifact_links",
    "reviewed_validation_outcomes",
)
EXPECTED_MISSING_EVIDENCE = {
    "representative_fixture_feedback_records": "not_recorded_locally",
    "multi_cohort_reviewed_feedback_records": "not_recorded_locally",
    "minimum_cohort_coverage_policy": "not_recorded_locally",
    "feedback_event_source_artifacts": "not_recorded_locally",
    "code_or_docs_diff_links": "not_recorded_locally",
    "validation_rerun_artifacts": "not_recorded_locally",
    "privacy_redaction_artifact_links": "not_recorded_locally",
    "review_or_signoff_identity_records": "not_recorded_locally",
    "review_or_signoff_version_records": "not_recorded_locally",
    "longitudinal_feedback_followup": "not_recorded_locally",
    "claim_to_feedback_traceability": "not_recorded_locally",
    "paper_facing_certification_rows": "not_recorded_locally",
    "workflow_change_artifact_links": "not_recorded_locally",
    "reviewed_validation_outcomes": "not_recorded_locally",
    "alphaevolve_collaborator_feedback_parity": "not_recorded_locally",
}


@dataclass(frozen=True)
class CollaboratorFeedbackProvenanceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CollaboratorFeedbackProvenanceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CollaboratorFeedbackProvenanceBoundaryIssue]


def collaborator_feedback_provenance_boundary_record() -> dict[str, Any]:
    """Return the current collaborator-feedback provenance boundary."""

    return {
        "schema": COLLABORATOR_FEEDBACK_PROVENANCE_BOUNDARY_SCHEMA,
        "runtime_report_schema": COLLABORATOR_FEEDBACK_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Acknowledgements say early users and collaborators "
            "contributed diverse use cases and insightful feedback that shaped "
            "the system into a more robust and versatile tool"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "collaborator_feedback_provenance_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has an optional collaborator "
            "feedback metadata contract and runtime provenance report for cohorts, "
            "feedback events, affected workflow areas, change-artifact links, "
            "validation outcomes, privacy/redaction policy, review/signoff state, "
            "and robustness/versatility claim links, but does not claim populated "
            "representative-fixture feedback records, multi-cohort reviewed "
            "feedback evidence, cohort-coverage policy, source feedback "
            "artifacts, code/docs diff links, validation rerun artifacts, "
            "privacy/redaction artifact links, review/signoff identity or "
            "version records, longitudinal follow-up, claim-to-feedback "
            "traceability, paper-facing certification rows, workflow change "
            "artifact links, reviewed validation outcomes, or AlphaEvolve "
            "collaborator-feedback parity."
        ),
    }


def validate_collaborator_feedback_provenance_boundary(
    boundary: object | str | Path | None = None,
) -> CollaboratorFeedbackProvenanceBoundaryValidation:
    data, read_issues = _load_boundary(
        collaborator_feedback_provenance_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return CollaboratorFeedbackProvenanceBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CollaboratorFeedbackProvenanceBoundaryIssue] = []
    if data.get("schema") != COLLABORATOR_FEEDBACK_PROVENANCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported collaborator feedback provenance boundary schema"))
    if data.get("runtime_report_schema") != COLLABORATOR_FEEDBACK_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify collaborator feedback provenance reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['Acknowledgements']"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "Acknowledgements" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve acknowledgement feedback evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "collaborator_feedback_provenance_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to collaborator feedback provenance reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "collaborator feedback boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim collaborator-feedback parity"))
    return CollaboratorFeedbackProvenanceBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_collaborator_feedback_provenance_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_collaborator_feedback_provenance_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve collaborator-feedback provenance boundary",
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
) -> tuple[dict[str, Any] | None, list[CollaboratorFeedbackProvenanceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "collaborator feedback provenance boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[CollaboratorFeedbackProvenanceBoundaryIssue],
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
    issues: list[CollaboratorFeedbackProvenanceBoundaryIssue],
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


def _issue(code: str, message: str) -> CollaboratorFeedbackProvenanceBoundaryIssue:
    return CollaboratorFeedbackProvenanceBoundaryIssue(code, message)
