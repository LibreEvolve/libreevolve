from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TITLE_PAGE_AFFILIATION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_title_page_affiliation_boundary.v1"
)
TITLE_PAGE_AFFILIATION_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.title_page_affiliation_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("title_page",)
EXPECTED_BOUNDARY_STATUS = "title_page_affiliation_claim_ready"
EXPECTED_FIXTURE_PATH = "libreevolve/problems/examples/matrix_multiplication/title_page.yaml"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "metadata_present",
    "affiliation_organization_recorded",
    "affiliation_footnote_recorded",
    "equal_contribution_footnote_recorded",
    "author_to_marker_mapping_recorded",
    "source_rights_linked",
    "privacy_redaction_policy_recorded",
    "title_page_metadata_review_or_owner_signoff",
    "local_affiliation_boundary_separated",
    "publication_author_boundary_separated",
    "technical_system_boundary_separated",
    "alphaevolve_title_page_affiliation_parity",
    "reviewed_matrix_fixture_title_page_records",
    "source_page_1_recorded",
)
EXPECTED_EXCLUDED_CLAIMS = {
    "local_libreevolve_affiliation_or_endorsement": "not_claimed",
    "publication_author_metadata": "separate_runtime_report",
    "technical_capability_or_benchmark_success": "out_of_scope",
    "system_contribution_provenance": "separate_runtime_report",
    "license_or_rights_regrant": "not_claimed",
    "copied_contact_details": "not_recorded",
}


@dataclass(frozen=True)
class TitlePageAffiliationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class TitlePageAffiliationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    excluded_claim_count: int
    issues: list[TitlePageAffiliationBoundaryIssue]


def title_page_affiliation_boundary_record() -> dict[str, Any]:
    """Return the paper-facing AlphaEvolve title-page affiliation boundary."""

    return {
        "schema": TITLE_PAGE_AFFILIATION_BOUNDARY_SCHEMA,
        "runtime_report_schema": TITLE_PAGE_AFFILIATION_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve title page page 1 records the Google DeepMind "
            "affiliation footnote, equal-contribution footnote, and source "
            "rights linkage used as publication metadata"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "title_page_affiliation_report_available",
        "claim_ready": True,
        "claim_ready_fixture": EXPECTED_FIXTURE_PATH,
        "source_pages": [1],
        "affiliation_organization": "Google DeepMind",
        "required_marker_kinds": ["affiliation", "equal_contribution"],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "excluded_claims": dict(EXPECTED_EXCLUDED_CLAIMS),
        "claim_boundary": (
            "This boundary records that the matrix_multiplication fixture has "
            "reviewed title-page metadata for source-paper affiliation, "
            "affiliation and equal-contribution footnotes, author-marker "
            "mapping, source-rights linkage, privacy/redaction policy, and "
            "review status. It does not claim local LibreEvolve affiliation or "
            "endorsement, publication-author metadata, technical capability, "
            "benchmark success, system-contribution provenance, license or "
            "rights regrant, or copied contact details."
        ),
    }


def validate_title_page_affiliation_boundary(
    boundary: object | str | Path | None = None,
) -> TitlePageAffiliationBoundaryValidation:
    data, read_issues = _load_boundary(
        title_page_affiliation_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return TitlePageAffiliationBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[TitlePageAffiliationBoundaryIssue] = []
    if data.get("schema") != TITLE_PAGE_AFFILIATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported title-page affiliation boundary schema"))
    if data.get("runtime_report_schema") != TITLE_PAGE_AFFILIATION_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify title-page affiliation reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['title_page']"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "page 1" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve title page page 1"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "title_page_affiliation_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to title-page affiliation reports"))
    if data.get("claim_ready") is not True:
        issues.append(_issue("claim_ready_underclaim", "title-page affiliation boundary should remain claim-ready for the reviewed fixture"))
    if data.get("claim_ready_fixture") != EXPECTED_FIXTURE_PATH:
        issues.append(_issue("invalid_claim_ready_fixture", f"claim_ready_fixture must be {EXPECTED_FIXTURE_PATH}"))
    if data.get("source_pages") != [1]:
        issues.append(_issue("invalid_source_pages", "source_pages must identify AlphaEvolve page 1"))
    if data.get("affiliation_organization") != "Google DeepMind":
        issues.append(_issue("invalid_affiliation_organization", "affiliation_organization must match source-publication metadata"))
    marker_kinds = data.get("required_marker_kinds")
    if not isinstance(marker_kinds, list) or set(marker_kinds) != {"affiliation", "equal_contribution"}:
        issues.append(_issue("invalid_required_marker_kinds", "required_marker_kinds must contain affiliation and equal_contribution"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    excluded_count = _validate_excluded_claims(data.get("excluded_claims"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim local LibreEvolve affiliation" not in boundary_text
        or "license or rights regrant" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate source title-page facts from local affiliation and rights claims"))
    return TitlePageAffiliationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        excluded_claim_count=excluded_count,
        issues=issues,
    )


def render_title_page_affiliation_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_title_page_affiliation_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve title-page affiliation boundary",
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
) -> tuple[dict[str, Any] | None, list[TitlePageAffiliationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "title-page affiliation boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[TitlePageAffiliationBoundaryIssue],
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
    issues: list[TitlePageAffiliationBoundaryIssue],
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


def _issue(code: str, message: str) -> TitlePageAffiliationBoundaryIssue:
    return TitlePageAffiliationBoundaryIssue(code, message)
