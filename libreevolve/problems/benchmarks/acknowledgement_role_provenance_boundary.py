from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ACKNOWLEDGEMENT_ROLE_PROVENANCE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_acknowledgement_role_provenance_boundary.v1"
)
ACKNOWLEDGEMENT_ROLE_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.acknowledgement_role_provenance_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "acknowledgement_role_claim_ready"
EXPECTED_FIXTURE_PATH = "libreevolve/problems/examples/matrix_multiplication/acknowledgements.yaml"
EXPECTED_REQUIRED_ROLE_CATEGORIES = (
    "white_paper_review",
    "early_exploration",
    "support_advice",
    "practical_application_management_advice",
    "application_review",
    "application_specific_advice",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "metadata_present",
    "all_acknowledgement_role_categories_recorded",
    "source_page_and_section_recorded",
    "privacy_redaction_policy_recorded",
    "paper_process_review_or_owner_signoff",
    "technical_validation_boundary_separated",
    "publication_author_boundary_separated",
    "alphaevolve_acknowledgement_role_parity",
    "reviewed_matrix_fixture_acknowledgement_records",
    "source_pages_21_22_recorded",
)
EXPECTED_EXCLUDED_CLAIMS = {
    "technical_validation_or_benchmark_success": "out_of_scope",
    "publication_author_metadata": "separate_runtime_report",
    "title_page_affiliation_metadata": "separate_runtime_report",
    "system_contribution_provenance": "separate_runtime_report",
    "local_author_affiliation_or_endorsement": "not_claimed",
    "deployment_evidence": "not_claimed",
}


@dataclass(frozen=True)
class AcknowledgementRoleProvenanceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AcknowledgementRoleProvenanceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    excluded_claim_count: int
    issues: list[AcknowledgementRoleProvenanceBoundaryIssue]


def acknowledgement_role_provenance_boundary_record() -> dict[str, Any]:
    """Return the paper-facing AlphaEvolve acknowledgement-role boundary."""

    return {
        "schema": ACKNOWLEDGEMENT_ROLE_PROVENANCE_BOUNDARY_SCHEMA,
        "runtime_report_schema": ACKNOWLEDGEMENT_ROLE_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve Acknowledgements pages 21-22 record white-paper review, "
            "early exploration, support/advice, practical-application management "
            "advice, application review, and application-specific advice roles"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "acknowledgement_role_provenance_report_available",
        "claim_ready": True,
        "claim_ready_fixture": EXPECTED_FIXTURE_PATH,
        "source_pages": [21, 22],
        "required_role_categories": list(EXPECTED_REQUIRED_ROLE_CATEGORIES),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "excluded_claims": dict(EXPECTED_EXCLUDED_CLAIMS),
        "claim_boundary": (
            "This boundary records that the matrix_multiplication fixture has "
            "reviewed acknowledgement-role metadata covering the AlphaEvolve "
            "Acknowledgements role categories and source locators needed for "
            "acknowledgement-role parity. It does not claim benchmark success, "
            "technical validation, publication-author metadata, title-page "
            "affiliation metadata, system-contribution provenance, local author "
            "or affiliation endorsement, or deployment evidence."
        ),
    }


def validate_acknowledgement_role_provenance_boundary(
    boundary: object | str | Path | None = None,
) -> AcknowledgementRoleProvenanceBoundaryValidation:
    data, read_issues = _load_boundary(
        acknowledgement_role_provenance_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AcknowledgementRoleProvenanceBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AcknowledgementRoleProvenanceBoundaryIssue] = []
    if data.get("schema") != ACKNOWLEDGEMENT_ROLE_PROVENANCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported acknowledgement role provenance boundary schema"))
    if data.get("runtime_report_schema") != ACKNOWLEDGEMENT_ROLE_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify acknowledgement role provenance reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "Acknowledgements pages 21-22" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve Acknowledgements pages 21-22"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "acknowledgement_role_provenance_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to acknowledgement role provenance reports"))
    if data.get("claim_ready") is not True:
        issues.append(_issue("claim_ready_underclaim", "acknowledgement role boundary should remain claim-ready for the reviewed fixture"))
    if data.get("claim_ready_fixture") != EXPECTED_FIXTURE_PATH:
        issues.append(_issue("invalid_claim_ready_fixture", f"claim_ready_fixture must be {EXPECTED_FIXTURE_PATH}"))
    if data.get("source_pages") != [21, 22]:
        issues.append(_issue("invalid_source_pages", "source_pages must identify AlphaEvolve pages 21 and 22"))
    _validate_role_categories(data.get("required_role_categories"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    excluded_count = _validate_excluded_claims(data.get("excluded_claims"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim benchmark success" not in boundary_text
        or "publication-author metadata" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate acknowledgement roles from technical and authorship claims"))
    return AcknowledgementRoleProvenanceBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        excluded_claim_count=excluded_count,
        issues=issues,
    )


def render_acknowledgement_role_provenance_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_acknowledgement_role_provenance_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve acknowledgement-role provenance boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| excluded_claim_count | {validation.excluded_claim_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AcknowledgementRoleProvenanceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "acknowledgement role provenance boundary must be a JSON object")]


def _validate_role_categories(
    value: object,
    issues: list[AcknowledgementRoleProvenanceBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_role_categories", "required_role_categories must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_ROLE_CATEGORIES)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_role_category", f"missing role categories: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_role_category", f"unknown role categories: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_role_category", "required role categories must be strings"))
    return len(seen)


def _validate_required_fields(
    value: object,
    issues: list[AcknowledgementRoleProvenanceBoundaryIssue],
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


def _validate_excluded_claims(
    value: object,
    issues: list[AcknowledgementRoleProvenanceBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_excluded_claims", "excluded_claims must be an object"))
        return 0
    expected_keys = set(EXPECTED_EXCLUDED_CLAIMS)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_excluded_claim_key", f"excluded_claims lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_excluded_claim_key", f"excluded_claims has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_EXCLUDED_CLAIMS.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_excluded_claim_{key}", f"excluded_claims.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> AcknowledgementRoleProvenanceBoundaryIssue:
    return AcknowledgementRoleProvenanceBoundaryIssue(code, message)
