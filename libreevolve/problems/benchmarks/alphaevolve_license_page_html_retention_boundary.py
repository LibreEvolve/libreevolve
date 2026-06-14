from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_LICENSE_PAGE_HTML_RETENTION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_license_page_html_retention_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_LICENSE_URL = "https://creativecommons.org/licenses/by-nc-nd/4.0/"
EXPECTED_RETRIEVED_AT_UTC = "2026-06-14T03:01:27Z"
EXPECTED_RESPONSE_BYTES = 36988
EXPECTED_RESPONSE_SHA256 = (
    "7d6f32e34442a8e08c86a77ace49166f7193af0857816b739354493e2c812939"
)
EXPECTED_BOUNDARY_STATUS = "license_page_html_retained_without_refresh_gate"
EXPECTED_HTML_ARTIFACT_PATH = "papers/alphaevolve_license_page.html"
EXPECTED_TITLE = (
    "Deed - Attribution-NonCommercial-NoDerivatives 4.0 International - "
    "Creative Commons"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "license_url",
    "retrieved_at_utc",
    "http_status",
    "content_type",
    "response_bytes",
    "response_sha256",
    "html_artifact_path",
    "html_artifact_retained",
    "html_artifact_bytes",
    "html_artifact_sha256",
    "title",
    "license_family",
    "license_version",
    "normalized_license_url",
    "content_markers",
    "license_page_refresh_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "license_page_refresh_gate": "not_recorded_locally",
}
EXPECTED_CONTENT_MARKERS = {
    "has_doctype": True,
    "has_license_title": True,
    "has_creative_commons_name": True,
    "has_noncommercial_term": True,
    "has_no_derivatives_term": True,
}


@dataclass(frozen=True)
class AlphaEvolveLicensePageHtmlRetentionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveLicensePageHtmlRetentionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    html_artifact_retained: bool
    html_artifact_bytes: int | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveLicensePageHtmlRetentionBoundaryIssue]


def alphaevolve_license_page_html_retention_boundary_record() -> dict[str, Any]:
    """Return committed Creative Commons license-page HTML retention evidence."""

    return _load_committed_record()


def validate_alphaevolve_license_page_html_retention_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveLicensePageHtmlRetentionBoundaryValidation:
    data, read_issues, base_dir = _load_boundary(
        alphaevolve_license_page_html_retention_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveLicensePageHtmlRetentionBoundaryValidation(
            False, None, False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveLicensePageHtmlRetentionBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_LICENSE_PAGE_HTML_RETENTION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported license-page HTML retention boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "full Creative Commons source-license page HTML body" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must describe retained full license-page HTML evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "license-page HTML boundary must not claim refresh readiness"))
    html_retained, html_bytes = _validate_license_page_snapshot(data.get("license_page_snapshot"), issues)
    _validate_content_markers(data.get("html_content_markers"), issues)
    if base_dir is not None:
        _validate_retained_html_file(data, base_dir, issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "full Creative Commons license-page HTML artifact" not in boundary_text
        or "automated license-page refresh gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate retained HTML evidence from refresh evidence"))
    return AlphaEvolveLicensePageHtmlRetentionBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        html_artifact_retained=html_retained,
        html_artifact_bytes=html_bytes,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_license_page_html_retention_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_license_page_html_retention_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve license-page HTML retention boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| html_artifact_retained | {validation.html_artifact_retained} |",
        f"| html_artifact_bytes | {validation.html_artifact_bytes or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_committed_record() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[3] / "papers" / "alphaevolve_license_page_html_retention_boundary.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data
    raise ValueError("alphaevolve_license_page_html_retention_boundary.json must contain an object")


def _validate_license_page_snapshot(
    value: object,
    issues: list[AlphaEvolveLicensePageHtmlRetentionBoundaryIssue],
) -> tuple[bool, int | None]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_license_page_snapshot", "license_page_snapshot must be an object"))
        return False, None
    expected = {
        "license_url": EXPECTED_LICENSE_URL,
        "retrieved_at_utc": EXPECTED_RETRIEVED_AT_UTC,
        "http_status": 200,
        "content_type": "text/html",
        "response_bytes": EXPECTED_RESPONSE_BYTES,
        "response_sha256": EXPECTED_RESPONSE_SHA256,
        "html_artifact_path": EXPECTED_HTML_ARTIFACT_PATH,
        "html_artifact_retained": True,
        "html_artifact_bytes": EXPECTED_RESPONSE_BYTES,
        "html_artifact_sha256": EXPECTED_RESPONSE_SHA256,
        "title": EXPECTED_TITLE,
        "license_family": "CC BY-NC-ND",
        "license_version": "4.0",
        "normalized_license_url": EXPECTED_LICENSE_URL,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_license_page_snapshot_{key}", f"license_page_snapshot.{key} must be {expected_value}"))
    retained = value.get("html_artifact_retained") is True
    artifact_bytes = value.get("html_artifact_bytes")
    return retained, artifact_bytes if isinstance(artifact_bytes, int) else None


def _validate_content_markers(
    value: object,
    issues: list[AlphaEvolveLicensePageHtmlRetentionBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_html_content_markers", "html_content_markers must be an object"))
        return
    for key, expected_value in EXPECTED_CONTENT_MARKERS.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_html_content_marker_{key}", f"html_content_markers.{key} must be {expected_value}"))


def _validate_retained_html_file(
    data: dict[str, Any],
    base_dir: Path,
    issues: list[AlphaEvolveLicensePageHtmlRetentionBoundaryIssue],
) -> None:
    snapshot = data.get("license_page_snapshot")
    markers = data.get("html_content_markers")
    if not isinstance(snapshot, dict):
        return
    artifact_value = snapshot.get("html_artifact_path")
    if not isinstance(artifact_value, str):
        return
    artifact_path = base_dir / artifact_value
    try:
        html_bytes = artifact_path.read_bytes()
    except OSError as exc:
        issues.append(_issue("missing_html_artifact", f"HTML artifact could not be read: {exc}"))
        return
    if len(html_bytes) != EXPECTED_RESPONSE_BYTES:
        issues.append(_issue("invalid_html_artifact_bytes", f"HTML artifact must be {EXPECTED_RESPONSE_BYTES} bytes"))
    digest = hashlib.sha256(html_bytes).hexdigest()
    if digest != EXPECTED_RESPONSE_SHA256:
        issues.append(_issue("invalid_html_artifact_sha256", f"HTML artifact SHA-256 must be {EXPECTED_RESPONSE_SHA256}"))
    html_text = html_bytes.decode("utf-8", errors="replace")
    actual_markers = {
        "has_doctype": html_text.startswith("<!DOCTYPE html>"),
        "has_license_title": "Attribution-NonCommercial-NoDerivatives 4.0 International" in html_text,
        "has_creative_commons_name": "Creative Commons" in html_text,
        "has_noncommercial_term": "NonCommercial" in html_text,
        "has_no_derivatives_term": "NoDerivatives" in html_text,
    }
    if isinstance(markers, dict) and actual_markers != markers:
        issues.append(_issue("html_content_marker_drift", "HTML content markers must match the retained artifact"))


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveLicensePageHtmlRetentionBoundaryIssue], Path | None]:
    if isinstance(boundary, dict):
        return dict(boundary), [], None
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")], None
        if isinstance(data, dict):
            return data, [], None
        return None, [_issue("invalid_shape", "license-page HTML retention boundary must be a JSON object")], None
    path = Path(boundary)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")], None
    if isinstance(data, dict):
        return data, [], path.parent.parent
    return None, [_issue("invalid_shape", "license-page HTML retention boundary must be a JSON object")], None


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveLicensePageHtmlRetentionBoundaryIssue],
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
    issues: list[AlphaEvolveLicensePageHtmlRetentionBoundaryIssue],
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


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveLicensePageHtmlRetentionBoundaryIssue:
    return AlphaEvolveLicensePageHtmlRetentionBoundaryIssue(code, message)
