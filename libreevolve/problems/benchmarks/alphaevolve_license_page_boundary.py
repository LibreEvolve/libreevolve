from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_LICENSE_PAGE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_license_page_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_LICENSE_URL = "https://creativecommons.org/licenses/by-nc-nd/4.0/"
EXPECTED_RETRIEVED_ON = "2026-06-14"
EXPECTED_HTTP_STATUS = 200
EXPECTED_CONTENT_TYPE = "text/html"
EXPECTED_RESPONSE_BYTES = 36988
EXPECTED_RESPONSE_SHA256 = (
    "7d6f32e34442a8e08c86a77ace49166f7193af0857816b739354493e2c812939"
)
EXPECTED_TITLE = (
    "Deed - Attribution-NonCommercial-NoDerivatives 4.0 International - "
    "Creative Commons"
)
EXPECTED_LICENSE_FAMILY = "CC BY-NC-ND"
EXPECTED_LICENSE_VERSION = "4.0"
EXPECTED_BOUNDARY_STATUS = (
    "license_page_digest_with_retained_html_without_refresh_gate"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "license_url",
    "retrieved_on",
    "http_status",
    "content_type",
    "response_bytes",
    "response_sha256",
    "title",
    "license_family",
    "license_version",
    "normalized_license_url",
    "full_html_artifact",
    "raw_http_headers",
    "license_page_refresh_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "license_page_refresh_gate": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveLicensePageBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveLicensePageBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveLicensePageBoundaryIssue]


def alphaevolve_license_page_boundary_record() -> dict[str, Any]:
    """Return the source-license page evidence boundary for AlphaEvolve."""

    return {
        "schema": ALPHAEVOLVE_LICENSE_PAGE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve source metadata should preserve bounded evidence for "
            "the arXiv-adjacent Creative Commons source-license page."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "license_page_snapshot": {
            "license_url": EXPECTED_LICENSE_URL,
            "retrieved_on": EXPECTED_RETRIEVED_ON,
            "http_status": EXPECTED_HTTP_STATUS,
            "content_type": EXPECTED_CONTENT_TYPE,
            "response_bytes": EXPECTED_RESPONSE_BYTES,
            "response_sha256": EXPECTED_RESPONSE_SHA256,
            "title": EXPECTED_TITLE,
            "license_family": EXPECTED_LICENSE_FAMILY,
            "license_version": EXPECTED_LICENSE_VERSION,
            "normalized_license_url": EXPECTED_LICENSE_URL,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the Creative Commons license URL, status, "
            "content type, byte count, SHA-256 digest, title, family, and "
            "version for the AlphaEvolve source-license page and is paired "
            "with the raw HTTP headers and retained HTML sidecars. It does "
            "not claim an automated license-page refresh gate."
        ),
    }


def validate_alphaevolve_license_page_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveLicensePageBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_license_page_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AlphaEvolveLicensePageBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveLicensePageBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_LICENSE_PAGE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported license page boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "Creative Commons source-license page" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must link Creative Commons license-page evidence to source metadata"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "license page boundary must not claim full license refresh readiness"))
    _validate_snapshot(data.get("license_page_snapshot"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "retained HTML sidecars" not in boundary_text
        or "raw HTTP headers" not in boundary_text
        or "license-page refresh gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate the license digest from full retention/refresh evidence"))
    return AlphaEvolveLicensePageBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_license_page_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_license_page_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve license page boundary",
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


def _validate_snapshot(
    value: object,
    issues: list[AlphaEvolveLicensePageBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_license_page_snapshot", "license_page_snapshot must be an object"))
        return
    expected = {
        "license_url": EXPECTED_LICENSE_URL,
        "retrieved_on": EXPECTED_RETRIEVED_ON,
        "http_status": EXPECTED_HTTP_STATUS,
        "content_type": EXPECTED_CONTENT_TYPE,
        "response_bytes": EXPECTED_RESPONSE_BYTES,
        "response_sha256": EXPECTED_RESPONSE_SHA256,
        "title": EXPECTED_TITLE,
        "license_family": EXPECTED_LICENSE_FAMILY,
        "license_version": EXPECTED_LICENSE_VERSION,
        "normalized_license_url": EXPECTED_LICENSE_URL,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_snapshot_{key}", f"license_page_snapshot.{key} must be {expected_value}"))


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveLicensePageBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "license page boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveLicensePageBoundaryIssue],
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
    issues: list[AlphaEvolveLicensePageBoundaryIssue],
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
) -> AlphaEvolveLicensePageBoundaryIssue:
    return AlphaEvolveLicensePageBoundaryIssue(code, message)
