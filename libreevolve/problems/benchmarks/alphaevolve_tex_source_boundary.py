from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_TEX_SOURCE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_tex_source_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_ARXIV_VERSIONED_ID = "2506.13131v1"
EXPECTED_EPRINT_URL = "https://arxiv.org/e-print/2506.13131"
EXPECTED_RETRIEVED_ON = "2026-06-14"
EXPECTED_HTTP_STATUS = 200
EXPECTED_CONTENT_TYPE = "application/gzip"
EXPECTED_CONTENT_DISPOSITION = 'attachment; filename="arXiv-2506.13131v1.tar.gz"'
EXPECTED_RESPONSE_BYTES = 2635462
EXPECTED_RESPONSE_SHA256 = (
    "a3ea37c5b6fe967fba459f0daca8548a78e2a1eac45e5c2aac83051ef113f21d"
)
EXPECTED_BOUNDARY_STATUS = (
    "tex_eprint_digest_without_archive_retention_or_refresh_gate"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "eprint_url",
    "retrieved_on",
    "http_status",
    "content_type",
    "content_disposition",
    "response_bytes",
    "response_sha256",
    "arxiv_versioned_id",
    "full_raw_archive_artifact",
    "raw_http_headers",
    "archive_member_inventory",
    "extraction_script_artifact",
    "tex_source_refresh_gate",
    "cached_pdf_header_consistency",
)
EXPECTED_MISSING_EVIDENCE = {
    "full_raw_archive_artifact": "not_recorded_locally",
    "raw_http_headers": "not_recorded_locally",
    "archive_member_inventory": "not_recorded_locally",
    "extraction_script_artifact": "not_recorded_locally",
    "tex_source_refresh_gate": "not_recorded_locally",
    "cached_pdf_header_consistency": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveTexSourceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveTexSourceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveTexSourceBoundaryIssue]


def alphaevolve_tex_source_boundary_record() -> dict[str, Any]:
    """Return the TeX/e-print source-evidence boundary for AlphaEvolve."""

    return {
        "schema": ALPHAEVOLVE_TEX_SOURCE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve source metadata should include bounded evidence for "
            "the arXiv TeX/e-print archive in addition to PDF, abstract-page, "
            "and DOI/DataCite evidence."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "tex_eprint_snapshot": {
            "eprint_url": EXPECTED_EPRINT_URL,
            "retrieved_on": EXPECTED_RETRIEVED_ON,
            "http_status": EXPECTED_HTTP_STATUS,
            "content_type": EXPECTED_CONTENT_TYPE,
            "content_disposition": EXPECTED_CONTENT_DISPOSITION,
            "response_bytes": EXPECTED_RESPONSE_BYTES,
            "response_sha256": EXPECTED_RESPONSE_SHA256,
            "arxiv_versioned_id": EXPECTED_ARXIV_VERSIONED_ID,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the arXiv e-print endpoint, HTTP status, "
            "gzip content type, content-disposition filename, byte count, and "
            "SHA-256 digest for the AlphaEvolve source archive. It does not "
            "claim full raw archive retention, raw HTTP header retention, "
            "archive member inventory, extraction-script artifacts, TeX-source "
            "refresh gates, or cached-PDF header consistency."
        ),
    }


def validate_alphaevolve_tex_source_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveTexSourceBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_tex_source_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AlphaEvolveTexSourceBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveTexSourceBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_TEX_SOURCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TeX source boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "arXiv TeX/e-print archive" not in source_claim
        or "DOI/DataCite evidence" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must link TeX/e-print evidence to source metadata"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "TeX source boundary must not claim full archive-refresh readiness"))
    _validate_snapshot(data.get("tex_eprint_snapshot"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim full raw archive retention" not in boundary_text
        or "TeX-source refresh gates" not in boundary_text
        or "cached-PDF header consistency" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate the e-print digest from full archive/refresh evidence"))
    return AlphaEvolveTexSourceBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_tex_source_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_tex_source_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve TeX source boundary",
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
    issues: list[AlphaEvolveTexSourceBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_tex_eprint_snapshot", "tex_eprint_snapshot must be an object"))
        return
    expected = {
        "eprint_url": EXPECTED_EPRINT_URL,
        "retrieved_on": EXPECTED_RETRIEVED_ON,
        "http_status": EXPECTED_HTTP_STATUS,
        "content_type": EXPECTED_CONTENT_TYPE,
        "content_disposition": EXPECTED_CONTENT_DISPOSITION,
        "response_bytes": EXPECTED_RESPONSE_BYTES,
        "response_sha256": EXPECTED_RESPONSE_SHA256,
        "arxiv_versioned_id": EXPECTED_ARXIV_VERSIONED_ID,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_snapshot_{key}", f"tex_eprint_snapshot.{key} must be {expected_value}"))


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveTexSourceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "TeX source boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveTexSourceBoundaryIssue],
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
    issues: list[AlphaEvolveTexSourceBoundaryIssue],
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
) -> AlphaEvolveTexSourceBoundaryIssue:
    return AlphaEvolveTexSourceBoundaryIssue(code, message)
