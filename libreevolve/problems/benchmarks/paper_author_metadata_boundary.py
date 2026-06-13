from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PAPER_AUTHOR_METADATA_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_paper_author_metadata_boundary.v1"
)
PAPER_AUTHOR_RUNTIME_REPORT_SCHEMA = "libreevolve.paper_author_metadata_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("Author information", "Contributions")
EXPECTED_BOUNDARY_STATUS = "paper_author_metadata_claim_ready"
EXPECTED_FIXTURE_PATH = "libreevolve/problems/examples/matrix_multiplication/paper_authors.yaml"
EXPECTED_REQUIRED_ROLE_CATEGORIES = (
    "equal_contributor",
    "manuscript_writer",
    "paper_input",
    "corresponding_author",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "metadata_present",
    "all_publication_author_roles_recorded",
    "source_page_and_section_recorded",
    "title_page_equal_contribution_marker_linked",
    "contact_privacy_policy_recorded",
    "publication_metadata_review_or_owner_signoff",
    "technical_implementation_boundary_separated",
    "acknowledgement_boundary_separated",
    "title_page_affiliation_boundary_separated",
    "alphaevolve_publication_author_metadata_parity",
    "reviewed_matrix_fixture_paper_author_records",
    "source_pages_22_23_recorded",
)
EXPECTED_EXCLUDED_CLAIMS = {
    "technical_implementation_or_benchmark_success": "out_of_scope",
    "acknowledgement_role_provenance": "separate_runtime_report",
    "title_page_affiliation_metadata": "separate_runtime_report",
    "system_contribution_provenance": "separate_runtime_report",
    "local_libreevolve_authorship_or_affiliation": "not_claimed",
    "copied_public_contact_details": "not_recorded",
}


@dataclass(frozen=True)
class PaperAuthorMetadataBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class PaperAuthorMetadataBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    excluded_claim_count: int
    issues: list[PaperAuthorMetadataBoundaryIssue]


def paper_author_metadata_boundary_record() -> dict[str, Any]:
    """Return the paper-facing AlphaEvolve publication-author boundary."""

    return {
        "schema": PAPER_AUTHOR_METADATA_BOUNDARY_SCHEMA,
        "runtime_report_schema": PAPER_AUTHOR_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve author information and Contributions pages 22-23 "
            "record equal contributors, manuscript writers, paper-input "
            "contributors, and corresponding authors, with the equal-"
            "contribution title-page marker linked separately"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "paper_author_metadata_report_available",
        "claim_ready": True,
        "claim_ready_fixture": EXPECTED_FIXTURE_PATH,
        "source_pages": [22, 23],
        "title_page_marker_linkage": "star",
        "required_role_categories": list(EXPECTED_REQUIRED_ROLE_CATEGORIES),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "excluded_claims": dict(EXPECTED_EXCLUDED_CLAIMS),
        "claim_boundary": (
            "This boundary records that the matrix_multiplication fixture has "
            "reviewed publication-author metadata covering AlphaEvolve equal "
            "contributors, manuscript writers, paper-input contributors, "
            "corresponding authors, source locators, title-page marker linkage, "
            "and contact/privacy policy. It does not claim technical "
            "implementation evidence, benchmark success, acknowledgement-role "
            "provenance, title-page affiliation metadata, system-contribution "
            "provenance, local LibreEvolve authorship or affiliation, or copied "
            "public contact details."
        ),
    }


def validate_paper_author_metadata_boundary(
    boundary: object | str | Path | None = None,
) -> PaperAuthorMetadataBoundaryValidation:
    data, read_issues = _load_boundary(
        paper_author_metadata_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return PaperAuthorMetadataBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[PaperAuthorMetadataBoundaryIssue] = []
    if data.get("schema") != PAPER_AUTHOR_METADATA_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported paper author metadata boundary schema"))
    if data.get("runtime_report_schema") != PAPER_AUTHOR_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify paper author metadata reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['Author information', 'Contributions']"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "pages 22-23" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve author pages 22-23"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "paper_author_metadata_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to paper author metadata reports"))
    if data.get("claim_ready") is not True:
        issues.append(_issue("claim_ready_underclaim", "paper author metadata boundary should remain claim-ready for the reviewed fixture"))
    if data.get("claim_ready_fixture") != EXPECTED_FIXTURE_PATH:
        issues.append(_issue("invalid_claim_ready_fixture", f"claim_ready_fixture must be {EXPECTED_FIXTURE_PATH}"))
    if data.get("source_pages") != [22, 23]:
        issues.append(_issue("invalid_source_pages", "source_pages must identify AlphaEvolve pages 22 and 23"))
    if data.get("title_page_marker_linkage") != "star":
        issues.append(_issue("invalid_title_page_marker_linkage", "title_page_marker_linkage must preserve the equal-contribution star marker"))
    _validate_role_categories(data.get("required_role_categories"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    excluded_count = _validate_excluded_claims(data.get("excluded_claims"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim technical implementation evidence" not in boundary_text
        or "copied public contact details" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate publication-author metadata from adjacent claims"))
    return PaperAuthorMetadataBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        excluded_claim_count=excluded_count,
        issues=issues,
    )


def render_paper_author_metadata_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_paper_author_metadata_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve paper-author metadata boundary",
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
) -> tuple[dict[str, Any] | None, list[PaperAuthorMetadataBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "paper author metadata boundary must be a JSON object")]


def _validate_role_categories(
    value: object,
    issues: list[PaperAuthorMetadataBoundaryIssue],
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
    issues: list[PaperAuthorMetadataBoundaryIssue],
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
    issues: list[PaperAuthorMetadataBoundaryIssue],
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


def _issue(code: str, message: str) -> PaperAuthorMetadataBoundaryIssue:
    return PaperAuthorMetadataBoundaryIssue(code, message)
