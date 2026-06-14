from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_RAW_HTTP_HEADERS_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_raw_http_headers_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RETRIEVED_AT_UTC = "2026-06-14T02:21:37Z"
EXPECTED_BOUNDARY_STATUS = (
    "raw_http_headers_recorded_without_full_response_retention_or_refresh_gate"
)
EXPECTED_RESPONSE_KEYS = (
    "versioned_abstract",
    "current_abstract",
    "floating_pdf",
    "datacite_api",
    "eprint_archive",
    "license_page",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "versioned_abstract_headers",
    "current_abstract_headers",
    "floating_pdf_headers",
    "datacite_api_headers",
    "eprint_archive_headers",
    "license_page_headers",
    "status_codes",
    "content_types",
    "content_lengths_or_transfer_encoding",
    "response_sha256_linkage",
    "full_raw_response_artifacts",
    "automated_header_refresh_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "full_raw_response_artifacts": "not_recorded_locally",
    "automated_header_refresh_gate": "not_recorded_locally",
}
EXPECTED_HEADERS: dict[str, dict[str, Any]] = {
    "versioned_abstract": {
        "url": "https://arxiv.org/abs/2506.13131v1",
        "final_url": "https://arxiv.org/abs/2506.13131v1",
        "http_status": 200,
        "reason": "OK",
        "response_bytes": 50098,
        "response_sha256": "ab39ec118afe0874f34179b5a06c42a57799b1103f027942a1ecd54dc3d95471",
        "raw_header_lines": (
            "Connection: close",
            "Content-Length: 50098",
            "content-type: text/html; charset=utf-8",
            "x-cloud-trace-context: 4a5adddf6728a630045bd2c1bf43ddd6",
            "last-modified: Tue, 17 Jun 2025 01:05:15 GMT",
            "via: 1.1 google, 1.1 varnish, 1.1 varnish, 1.1 varnish",
            "cache-control: max-age=3600",
            "content-security-policy: frame-ancestors 'none'",
            "x-frame-options: SAMEORIGIN",
            "server: Google Frontend",
            "Accept-Ranges: bytes",
            "Age: 271772",
            "Date: Sun, 14 Jun 2026 02:21:36 GMT",
            "X-Served-By: cache-lga21990-LGA, cache-lga21971-LGA, cache-cmh1290110-CMH",
            "X-Cache: MISS, HIT, HIT",
            "X-Timer: S1781403696.101439,VS0,VE2",
        ),
    },
    "current_abstract": {
        "url": "https://arxiv.org/abs/2506.13131",
        "final_url": "https://arxiv.org/abs/2506.13131",
        "http_status": 200,
        "reason": "OK",
        "response_bytes": 49939,
        "response_sha256": "707d6aa982e50eca955e6cf7f4a86d2bce2ca6cea543827fea22537ef68d87bb",
        "raw_header_lines": (
            "Connection: close",
            "Content-Length: 49939",
            "cache-control: max-age=3600",
            "x-cloud-trace-context: c7cc521b4a3d0fff5e24aab4e096e3cc",
            "last-modified: Tue, 17 Jun 2025 01:05:15 GMT",
            "content-type: text/html; charset=utf-8",
            "content-security-policy: frame-ancestors 'none'",
            "x-frame-options: SAMEORIGIN",
            "via: 1.1 google, 1.1 varnish, 1.1 varnish, 1.1 varnish",
            "server: Google Frontend",
            "Accept-Ranges: bytes",
            "Age: 478937",
            "Date: Sun, 14 Jun 2026 02:21:36 GMT",
            "X-Served-By: cache-lga21947-LGA, cache-lga21962-LGA, cache-cmh1290122-CMH",
            "X-Cache: MISS, HIT, HIT",
            "X-Timer: S1781403696.195162,VS0,VE1",
        ),
    },
    "floating_pdf": {
        "url": "https://arxiv.org/pdf/2506.13131.pdf",
        "final_url": "https://arxiv.org/pdf/2506.13131",
        "http_status": 200,
        "reason": "OK",
        "response_bytes": 3525764,
        "response_sha256": "f092c8cbd65da89951ee6496374da9a54963f9035758c25ac6e4625f506df9ad",
        "raw_header_lines": (
            "Connection: close",
            "Content-Length: 3525764",
            "server: Google Frontend",
            'content-disposition: inline; filename="2506.13131v1.pdf"',
            "link: <https://arxiv.org/pdf/2506.13131>; rel='canonical'",
            "x-cloud-trace-context: e522e965c7d209a62c6ce9b5d0f7cccc",
            "last-modified: Tue, 17 Jun 2025 01:33:09 GMT",
            'etag: "sha256:183370228c6b7cfb6195c50750c702a4ab8d3ef90226ea5031fc06e6c22f0682"',
            "access-control-allow-origin: *",
            "via: 1.1 google, 1.1 varnish, 1.1 varnish, 1.1 varnish",
            "content-type: application/pdf",
            "Accept-Ranges: bytes",
            "Age: 645248",
            "Date: Sun, 14 Jun 2026 02:21:36 GMT",
            "X-Served-By: cache-lga21952-LGA, cache-lga21952-LGA, cache-lga21936-LGA, cache-cmh1290059-CMH",
            "X-Cache: MISS, HIT, HIT",
            "X-Timer: S1781403696.338644,VS0,VE2",
        ),
    },
    "datacite_api": {
        "url": "https://api.datacite.org/dois/10.48550%2Farxiv.2506.13131",
        "final_url": "https://api.datacite.org/dois/10.48550%2Farxiv.2506.13131",
        "http_status": 200,
        "reason": "OK",
        "response_bytes": 15905,
        "response_sha256": "90c017a039e22f04fb6a5bc108ab8edf1614bc446aea83997537a01d2ef38af9",
        "raw_header_lines": (
            "Date: Sun, 14 Jun 2026 02:21:37 GMT",
            "Content-Type: application/json; charset=utf-8",
            "Transfer-Encoding: chunked",
            "Connection: close",
            "Status: 200 OK",
            "x-anonymous-consumer: true",
            "cache-control: max-age=0, private, must-revalidate",
            "vary: Accept-Encoding",
            "referrer-policy: strict-origin-when-cross-origin",
            "x-permitted-cross-domain-policies: none",
            "x-xss-protection: 0",
            "x-request-id: 67efe53d-dbe8-4549-bd2b-eb32407a7d39",
            'etag: W/"90c017a039e22f04fb6a5bc108ab8edf"',
            "x-frame-options: SAMEORIGIN",
            "x-runtime: 0.019617",
            "x-content-type-options: nosniff",
            "X-Powered-By: Phusion Passenger(R) 6.1.2",
            "Server: nginx/1.24.0 + Phusion Passenger(R) 6.1.2",
            "Access-Control-Allow-Credentials: true",
            "Access-Control-Allow-Methods: GET, POST, PUT, PATCH, DELETE, OPTIONS",
            "Access-Control-Allow-Headers: Accept,Access-Control-Allow-Origin,Access-Control-Expose-Headers,Access-Control-Allow-Methods,Access-Control-Allow-Headers,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Mx-ReqToken,X-Requested-With",
            "Access-Control-Expose-Headers: Authorization",
        ),
    },
    "eprint_archive": {
        "url": "https://arxiv.org/e-print/2506.13131",
        "final_url": "https://arxiv.org/e-print/2506.13131",
        "http_status": 200,
        "reason": "OK",
        "response_bytes": 2635462,
        "response_sha256": "a3ea37c5b6fe967fba459f0daca8548a78e2a1eac45e5c2aac83051ef113f21d",
        "raw_header_lines": (
            "Connection: close",
            "Content-Length: 2635462",
            'content-disposition: attachment; filename="arXiv-2506.13131v1.tar.gz"',
            "server: Google Frontend",
            "via: 1.1 google, 1.1 varnish, 1.1 varnish, 1.1 varnish",
            "last-modified: Tue, 17 Jun 2025 01:17:38 GMT",
            "content-type: application/gzip",
            "access-control-allow-origin: *",
            'etag: "sha256:4b5b5d94f2c08e7cb04855a64a4e662851a84d7717b17c863a124273e1677c47"',
            "x-cloud-trace-context: 20f2c0e41cf63bf1aacd9b43a67f8148",
            "Accept-Ranges: bytes",
            "Age: 209841",
            "Date: Sun, 14 Jun 2026 02:21:37 GMT",
            "X-Served-By: cache-lga21952-LGA, cache-lga21952-LGA, cache-lga21980-LGA, cache-cmh1290026-CMH",
            "X-Cache: MISS, HIT, HIT",
            "X-Timer: S1781403697.240002,VS0,VE1",
        ),
    },
    "license_page": {
        "url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "final_url": "https://creativecommons.org/licenses/by-nc-nd/4.0/",
        "http_status": 200,
        "reason": "OK",
        "response_bytes": 36988,
        "response_sha256": "7d6f32e34442a8e08c86a77ace49166f7193af0857816b739354493e2c812939",
        "raw_header_lines": (
            "Date: Sun, 14 Jun 2026 02:21:37 GMT",
            "Content-Type: text/html",
            "Transfer-Encoding: chunked",
            "Connection: close",
            "Server: cloudflare",
            "Last-Modified: Tue, 09 Jun 2026 14:26:09 GMT",
            "Age: 678",
            "Vary: Accept-Encoding",
            "cf-cache-status: HIT",
            "Access-Control-Allow-Origin: *",
            "CF-RAY: a0b5dcd52d122a9c-CMH",
        ),
    },
}


@dataclass(frozen=True)
class AlphaEvolveRawHttpHeadersBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveRawHttpHeadersBoundaryValidation:
    ok: bool
    boundary_status: str | None
    response_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveRawHttpHeadersBoundaryIssue]


def alphaevolve_raw_http_headers_boundary_record() -> dict[str, Any]:
    """Return pinned raw HTTP response headers for AlphaEvolve source URLs."""

    return {
        "schema": ALPHAEVOLVE_RAW_HTTP_HEADERS_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve source metadata should retain the raw HTTP response "
            "headers used to support the cached abstract, PDF, DOI/DataCite, "
            "TeX/e-print, and license-page source evidence."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "retrieved_at_utc": EXPECTED_RETRIEVED_AT_UTC,
        "header_snapshots": {
            key: _header_snapshot_record(key, value)
            for key, value in EXPECTED_HEADERS.items()
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records raw HTTP response header lines and links "
            "them to pinned response byte counts and SHA-256 digests for the "
            "AlphaEvolve source URLs. It does not claim full raw response body "
            "retention or an automated header refresh gate, and is paired "
            "with the cached PDF header text consistency sidecar."
        ),
    }


def validate_alphaevolve_raw_http_headers_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveRawHttpHeadersBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_raw_http_headers_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveRawHttpHeadersBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveRawHttpHeadersBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_RAW_HTTP_HEADERS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported raw HTTP headers boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "raw HTTP response headers" not in source_claim
        or "TeX/e-print" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must describe retained source response headers"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "raw HTTP headers boundary must not claim refresh readiness"))
    if data.get("retrieved_at_utc") != EXPECTED_RETRIEVED_AT_UTC:
        issues.append(_issue("invalid_retrieved_at_utc", f"retrieved_at_utc must be {EXPECTED_RETRIEVED_AT_UTC}"))
    response_count = _validate_header_snapshots(data.get("header_snapshots"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "raw HTTP response header lines" not in boundary_text
        or "does not claim full raw response body retention" not in boundary_text
        or "automated header refresh gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate header retention from refresh/body evidence"))
    return AlphaEvolveRawHttpHeadersBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        response_count=response_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_raw_http_headers_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_raw_http_headers_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve raw HTTP headers boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| response_count | {validation.response_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _header_snapshot_record(key: str, snapshot: dict[str, Any]) -> dict[str, Any]:
    return {
        "source": key,
        "url": snapshot["url"],
        "final_url": snapshot["final_url"],
        "http_status": snapshot["http_status"],
        "reason": snapshot["reason"],
        "response_bytes": snapshot["response_bytes"],
        "response_sha256": snapshot["response_sha256"],
        "raw_header_lines": list(snapshot["raw_header_lines"]),
    }


def _validate_header_snapshots(
    value: object,
    issues: list[AlphaEvolveRawHttpHeadersBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_header_snapshots", "header_snapshots must be an object"))
        return 0
    expected_keys = set(EXPECTED_RESPONSE_KEYS)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_header_snapshot", f"header_snapshots lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_header_snapshot", f"header_snapshots has unknown keys: {', '.join(extra)}"))
    for key in EXPECTED_RESPONSE_KEYS:
        _validate_single_header_snapshot(key, value.get(key), issues)
    return len(actual_keys)


def _validate_single_header_snapshot(
    key: str,
    value: object,
    issues: list[AlphaEvolveRawHttpHeadersBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue(f"invalid_header_snapshot_{key}", f"header_snapshots.{key} must be an object"))
        return
    expected = EXPECTED_HEADERS[key]
    for field in ("url", "final_url", "http_status", "reason", "response_bytes", "response_sha256"):
        if value.get(field) != expected[field]:
            issues.append(_issue(f"invalid_{key}_{field}", f"header_snapshots.{key}.{field} must be {expected[field]}"))
    if value.get("source") != key:
        issues.append(_issue(f"invalid_{key}_source", f"header_snapshots.{key}.source must be {key}"))
    raw_lines = value.get("raw_header_lines")
    expected_lines = list(expected["raw_header_lines"])
    if raw_lines != expected_lines:
        issues.append(_issue(f"invalid_{key}_raw_header_lines", f"header_snapshots.{key}.raw_header_lines must match the pinned response headers"))


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveRawHttpHeadersBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "raw HTTP headers boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveRawHttpHeadersBoundaryIssue],
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
    issues: list[AlphaEvolveRawHttpHeadersBoundaryIssue],
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
) -> AlphaEvolveRawHttpHeadersBoundaryIssue:
    return AlphaEvolveRawHttpHeadersBoundaryIssue(code, message)
