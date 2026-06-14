from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_DATACITE_DOI_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_datacite_doi_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_DOI = "10.48550/arxiv.2506.13131"
EXPECTED_API_URL = "https://api.datacite.org/dois/10.48550%2Farxiv.2506.13131"
EXPECTED_LANDING_URL = "https://arxiv.org/abs/2506.13131"
EXPECTED_TITLE = "AlphaEvolve: A coding agent for scientific and algorithmic discovery"
EXPECTED_CREATOR_COUNT = 18
EXPECTED_PUBLICATION_YEAR = 2025
EXPECTED_PUBLISHER = "arXiv"
EXPECTED_RESOURCE_TYPE_GENERAL = "Preprint"
EXPECTED_SCHEMA_VERSION = "http://datacite.org/schema/kernel-4"
EXPECTED_REGISTERED = "2025-06-17T02:53:57Z"
EXPECTED_VERSION = "1"
EXPECTED_RETRIEVED_ON = "2026-06-14"
EXPECTED_RESPONSE_BYTES = 15905
EXPECTED_RESPONSE_SHA256 = (
    "90c017a039e22f04fb6a5bc108ab8edf1614bc446aea83997537a01d2ef38af9"
)
EXPECTED_BOUNDARY_STATUS = (
    "datacite_api_snapshot_without_full_source_refresh_gate"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "datacite_api_url",
    "retrieved_on",
    "http_status",
    "response_bytes",
    "response_sha256",
    "doi",
    "landing_url",
    "title",
    "creator_count",
    "publisher",
    "publication_year",
    "resource_type_general",
    "schema_version",
    "registered_timestamp",
    "version",
    "raw_http_headers",
    "full_raw_response_artifact",
    "datacite_refresh_gate",
    "doi_landing_resolution_headers",
    "cached_pdf_header_consistency",
)
EXPECTED_MISSING_EVIDENCE = {
    "datacite_refresh_gate": "not_recorded_locally",
    "cached_pdf_header_consistency": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveDataCiteDoiBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveDataCiteDoiBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveDataCiteDoiBoundaryIssue]


def alphaevolve_datacite_doi_boundary_record() -> dict[str, Any]:
    """Return the DataCite DOI source-evidence boundary for AlphaEvolve."""

    return {
        "schema": ALPHAEVOLVE_DATACITE_DOI_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve source metadata should be backed by DOI/DataCite "
            "resolution evidence in addition to the cached PDF and arXiv "
            "abstract-page snapshot."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "datacite_api_snapshot": {
            "api_url": EXPECTED_API_URL,
            "retrieved_on": EXPECTED_RETRIEVED_ON,
            "http_status": 200,
            "response_bytes": EXPECTED_RESPONSE_BYTES,
            "response_sha256": EXPECTED_RESPONSE_SHA256,
            "doi": EXPECTED_DOI,
            "landing_url": EXPECTED_LANDING_URL,
            "title": EXPECTED_TITLE,
            "creator_count": EXPECTED_CREATOR_COUNT,
            "publisher": EXPECTED_PUBLISHER,
            "publication_year": EXPECTED_PUBLICATION_YEAR,
            "resource_type_general": EXPECTED_RESOURCE_TYPE_GENERAL,
            "schema_version": EXPECTED_SCHEMA_VERSION,
            "registered_timestamp": EXPECTED_REGISTERED,
            "version": EXPECTED_VERSION,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a bounded DataCite API response summary and "
            "content hash for DOI 10.48550/arxiv.2506.13131 and is paired "
            "with the raw HTTP headers, full raw response, and DOI "
            "landing-resolution sidecars. It does not claim automated DataCite "
            "refresh gates or cached-PDF header consistency."
        ),
    }


def validate_alphaevolve_datacite_doi_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveDataCiteDoiBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_datacite_doi_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveDataCiteDoiBoundaryValidation(
            False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveDataCiteDoiBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_DATACITE_DOI_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported DataCite DOI boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "DOI/DataCite resolution evidence" not in source_claim
        or "cached PDF" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must link DOI/DataCite evidence to source metadata"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "DataCite DOI boundary must not claim full source-refresh readiness"))
    _validate_snapshot(data.get("datacite_api_snapshot"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "raw HTTP headers" not in boundary_text
        or "full raw response" not in boundary_text
        or "DOI landing-resolution sidecars" not in boundary_text
        or "automated DataCite refresh gates" not in boundary_text
        or "cached-PDF header consistency" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate the DOI snapshot from full refresh evidence"))
    return AlphaEvolveDataCiteDoiBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_datacite_doi_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_datacite_doi_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve DataCite DOI boundary",
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
    issues: list[AlphaEvolveDataCiteDoiBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_datacite_api_snapshot", "datacite_api_snapshot must be an object"))
        return
    expected = {
        "api_url": EXPECTED_API_URL,
        "retrieved_on": EXPECTED_RETRIEVED_ON,
        "http_status": 200,
        "response_bytes": EXPECTED_RESPONSE_BYTES,
        "response_sha256": EXPECTED_RESPONSE_SHA256,
        "doi": EXPECTED_DOI,
        "landing_url": EXPECTED_LANDING_URL,
        "title": EXPECTED_TITLE,
        "creator_count": EXPECTED_CREATOR_COUNT,
        "publisher": EXPECTED_PUBLISHER,
        "publication_year": EXPECTED_PUBLICATION_YEAR,
        "resource_type_general": EXPECTED_RESOURCE_TYPE_GENERAL,
        "schema_version": EXPECTED_SCHEMA_VERSION,
        "registered_timestamp": EXPECTED_REGISTERED,
        "version": EXPECTED_VERSION,
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_snapshot_{key}", f"datacite_api_snapshot.{key} must be {expected_value}"))


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveDataCiteDoiBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "DataCite DOI boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveDataCiteDoiBoundaryIssue],
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
    issues: list[AlphaEvolveDataCiteDoiBoundaryIssue],
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
) -> AlphaEvolveDataCiteDoiBoundaryIssue:
    return AlphaEvolveDataCiteDoiBoundaryIssue(code, message)
