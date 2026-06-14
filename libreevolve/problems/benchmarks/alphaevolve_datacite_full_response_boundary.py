from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_DATACITE_FULL_RESPONSE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_datacite_full_response_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_API_URL = "https://api.datacite.org/dois/10.48550%2Farxiv.2506.13131"
EXPECTED_RETRIEVED_AT_UTC = "2026-06-14T02:40:10Z"
EXPECTED_RESPONSE_BYTES = 15905
EXPECTED_RESPONSE_SHA256 = (
    "90c017a039e22f04fb6a5bc108ab8edf1614bc446aea83997537a01d2ef38af9"
)
EXPECTED_BOUNDARY_STATUS = "full_datacite_response_body_retained_without_refresh_gate"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "datacite_api_url",
    "retrieved_at_utc",
    "http_status",
    "content_type",
    "response_bytes",
    "response_sha256",
    "raw_response_body",
    "parsed_doi",
    "parsed_landing_url",
    "parsed_title",
    "parsed_creator_count",
    "parsed_registered_timestamp",
    "parsed_version",
    "automated_datacite_refresh_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "automated_datacite_refresh_gate": "not_recorded_locally",
}
EXPECTED_PARSED_RESPONSE_SUMMARY = {
    "top_level_type": "dois",
    "id": "10.48550/arxiv.2506.13131",
    "doi": "10.48550/arxiv.2506.13131",
    "url": "https://arxiv.org/abs/2506.13131",
    "title": "AlphaEvolve: A coding agent for scientific and algorithmic discovery",
    "creator_count": 18,
    "publisher": "arXiv",
    "publication_year": 2025,
    "resource_type_general": "Preprint",
    "schema_version": "http://datacite.org/schema/kernel-4",
    "registered_timestamp": "2025-06-17T02:53:57.000Z",
    "version": "1",
}


@dataclass(frozen=True)
class AlphaEvolveDataCiteFullResponseBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveDataCiteFullResponseBoundaryValidation:
    ok: bool
    boundary_status: str | None
    response_bytes: int | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveDataCiteFullResponseBoundaryIssue]


def alphaevolve_datacite_full_response_boundary_record() -> dict[str, Any]:
    """Return the committed full DataCite response body evidence."""

    return _load_committed_record()


def validate_alphaevolve_datacite_full_response_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveDataCiteFullResponseBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_datacite_full_response_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveDataCiteFullResponseBoundaryValidation(
            False, None, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveDataCiteFullResponseBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_DATACITE_FULL_RESPONSE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported DataCite full-response boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "full raw DataCite API response body" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must describe retained full DataCite response evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "DataCite full-response boundary must not claim refresh readiness"))
    _validate_top_level_response_fields(data, issues)
    response_bytes = _validate_raw_response_body(data.get("raw_response_body"), issues)
    _validate_parsed_summary(data.get("parsed_response_summary"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "complete DataCite API response body" not in boundary_text
        or "automated DataCite refresh gate" not in boundary_text
        or "cached-PDF header consistency" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate full response retention from refresh/header evidence"))
    return AlphaEvolveDataCiteFullResponseBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        response_bytes=response_bytes,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_datacite_full_response_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_datacite_full_response_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve DataCite full-response boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| response_bytes | {validation.response_bytes or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_committed_record() -> dict[str, Any]:
    path = Path(__file__).resolve().parents[3] / "papers" / "alphaevolve_datacite_full_response_boundary.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, dict):
        return data
    raise ValueError("alphaevolve_datacite_full_response_boundary.json must contain an object")


def _validate_top_level_response_fields(
    data: dict[str, Any],
    issues: list[AlphaEvolveDataCiteFullResponseBoundaryIssue],
) -> None:
    expected = {
        "datacite_api_url": EXPECTED_API_URL,
        "retrieved_at_utc": EXPECTED_RETRIEVED_AT_UTC,
        "http_status": 200,
        "content_type": "application/json; charset=utf-8",
        "response_bytes": EXPECTED_RESPONSE_BYTES,
        "response_sha256": EXPECTED_RESPONSE_SHA256,
    }
    for key, expected_value in expected.items():
        if data.get(key) != expected_value:
            issues.append(_issue(f"invalid_{key}", f"{key} must be {expected_value}"))


def _validate_raw_response_body(
    value: object,
    issues: list[AlphaEvolveDataCiteFullResponseBoundaryIssue],
) -> int | None:
    if not isinstance(value, str):
        issues.append(_issue("invalid_raw_response_body", "raw_response_body must be a string"))
        return None
    raw_bytes = value.encode("utf-8")
    if len(raw_bytes) != EXPECTED_RESPONSE_BYTES:
        issues.append(_issue("invalid_raw_response_body_bytes", f"raw_response_body must encode to {EXPECTED_RESPONSE_BYTES} bytes"))
    digest = hashlib.sha256(raw_bytes).hexdigest()
    if digest != EXPECTED_RESPONSE_SHA256:
        issues.append(_issue("invalid_raw_response_body_sha256", f"raw_response_body SHA-256 must be {EXPECTED_RESPONSE_SHA256}"))
    try:
        parsed = json.loads(value)
    except json.JSONDecodeError as exc:
        issues.append(_issue("invalid_raw_response_json", f"raw_response_body must parse as JSON: {exc}"))
        return len(raw_bytes)
    if not isinstance(parsed, dict) or not isinstance(parsed.get("data"), dict):
        issues.append(_issue("invalid_raw_response_shape", "raw_response_body must contain a DataCite data object"))
        return len(raw_bytes)
    attrs = parsed["data"].get("attributes")
    if not isinstance(attrs, dict):
        issues.append(_issue("invalid_raw_response_attributes", "raw_response_body must contain DataCite attributes"))
        return len(raw_bytes)
    if attrs.get("doi") != EXPECTED_PARSED_RESPONSE_SUMMARY["doi"]:
        issues.append(_issue("invalid_raw_response_doi", "raw_response_body attributes.doi must match AlphaEvolve DOI"))
    if attrs.get("url") != EXPECTED_PARSED_RESPONSE_SUMMARY["url"]:
        issues.append(_issue("invalid_raw_response_url", "raw_response_body attributes.url must match AlphaEvolve arXiv landing URL"))
    return len(raw_bytes)


def _validate_parsed_summary(
    value: object,
    issues: list[AlphaEvolveDataCiteFullResponseBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_parsed_response_summary", "parsed_response_summary must be an object"))
        return
    for key, expected_value in EXPECTED_PARSED_RESPONSE_SUMMARY.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_parsed_summary_{key}", f"parsed_response_summary.{key} must be {expected_value}"))


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveDataCiteFullResponseBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "DataCite full-response boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveDataCiteFullResponseBoundaryIssue],
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
    issues: list[AlphaEvolveDataCiteFullResponseBoundaryIssue],
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
) -> AlphaEvolveDataCiteFullResponseBoundaryIssue:
    return AlphaEvolveDataCiteFullResponseBoundaryIssue(code, message)
