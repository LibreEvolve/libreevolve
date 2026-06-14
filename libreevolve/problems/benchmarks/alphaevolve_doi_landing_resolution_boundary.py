from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_DOI_LANDING_RESOLUTION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_doi_landing_resolution_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_DOI = "10.48550/arxiv.2506.13131"
EXPECTED_DOI_URL = "https://doi.org/10.48550/arxiv.2506.13131"
EXPECTED_RETRIEVED_AT_UTC = "2026-06-14T02:32:29Z"
EXPECTED_BOUNDARY_STATUS = "doi_redirect_headers_without_body_retention_or_refresh_gate"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "doi_url",
    "retrieved_at_utc",
    "doi_redirect_status",
    "doi_redirect_location",
    "doi_redirect_raw_header_lines",
    "doi_redirect_body_bytes",
    "final_landing_url",
    "final_landing_status",
    "final_landing_content_type",
    "final_landing_raw_header_lines",
    "final_landing_response_bytes",
    "final_landing_response_sha256",
    "full_doi_redirect_body_artifact",
    "automated_doi_resolution_refresh_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "full_doi_redirect_body_artifact": "not_recorded_locally",
    "automated_doi_resolution_refresh_gate": "not_recorded_locally",
}
EXPECTED_DOI_REDIRECT_HEADER_LINES = (
    "Date: Sun, 14 Jun 2026 02:32:27 GMT",
    "Content-Type: text/html;charset=utf-8",
    "Transfer-Encoding: chunked",
    "Connection: close",
    "location: https://arxiv.org/abs/2506.13131",
    "Server: cloudflare",
    "vary: Origin",
    "vary: Accept",
    "expires: Sun, 14 Jun 2026 03:02:17 GMT",
    "permissions-policy: interest-cohort=(),browsing-topics=()",
    "cf-cache-status: DYNAMIC",
    'Nel: {"report_to":"cf-nel","success_fraction":0.0,"max_age":604800}',
    "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
    'Report-To: {"group":"cf-nel","max_age":604800,"endpoints":[{"url":"https://a.nel.cloudflare.com/report/v4?s=BAtMPR7rKW9O2QlWTMUiAnJi50%2FCFOftLcifnFmUi5oQnSiOIB%2BPgGvEQXFbMxyaGZycV6L3ywUBzrotoHcSCLChVX68n0xT%2BvMnpKy7%2Fv6lBDVh%2F80%2B2Y4%3D"}]}',
    "CF-RAY: a0b5ecb518554a3e-CMH",
    'alt-svc: h3=":443"; ma=86400',
)
EXPECTED_FINAL_LANDING_HEADER_LINES = (
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
    "Age: 479589",
    "Date: Sun, 14 Jun 2026 02:32:27 GMT",
    "X-Served-By: cache-lga21947-LGA, cache-lga21962-LGA, cache-cmh1290123-CMH",
    "X-Cache: MISS, HIT, HIT",
    "X-Timer: S1781404348.935582,VS0,VE1",
)


@dataclass(frozen=True)
class AlphaEvolveDoiLandingResolutionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveDoiLandingResolutionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    redirect_status: int | None
    final_status: int | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveDoiLandingResolutionBoundaryIssue]


def alphaevolve_doi_landing_resolution_boundary_record() -> dict[str, Any]:
    """Return pinned DOI landing-resolution headers for AlphaEvolve."""

    return {
        "schema": ALPHAEVOLVE_DOI_LANDING_RESOLUTION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve source metadata should retain DOI landing-resolution "
            "evidence connecting the DOI URL to the arXiv abstract landing page."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "doi": EXPECTED_DOI,
        "retrieved_at_utc": EXPECTED_RETRIEVED_AT_UTC,
        "doi_redirect": {
            "url": EXPECTED_DOI_URL,
            "http_status": 302,
            "reason": "Found",
            "location": "https://arxiv.org/abs/2506.13131",
            "body_bytes": 149,
            "raw_header_lines": list(EXPECTED_DOI_REDIRECT_HEADER_LINES),
        },
        "final_landing": {
            "url": "https://arxiv.org/abs/2506.13131",
            "http_status": 200,
            "reason": "OK",
            "content_type": "text/html; charset=utf-8",
            "response_bytes": 49939,
            "response_sha256": "707d6aa982e50eca955e6cf7f4a86d2bce2ca6cea543827fea22537ef68d87bb",
            "raw_header_lines": list(EXPECTED_FINAL_LANDING_HEADER_LINES),
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records raw DOI resolver redirect headers and the "
            "final arXiv landing response headers for 10.48550/arxiv.2506.13131. "
            "It does not claim full DOI redirect body retention, an automated "
            "DOI resolution refresh gate. It is paired with the cached-PDF "
            "header consistency sidecar."
        ),
    }


def validate_alphaevolve_doi_landing_resolution_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveDoiLandingResolutionBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_doi_landing_resolution_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveDoiLandingResolutionBoundaryValidation(False, None, None, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveDoiLandingResolutionBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_DOI_LANDING_RESOLUTION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported DOI landing-resolution boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("doi") != EXPECTED_DOI:
        issues.append(_issue("invalid_doi", f"doi must be {EXPECTED_DOI}"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "DOI landing-resolution evidence" not in source_claim
        or "arXiv abstract landing page" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must connect DOI resolution to the arXiv landing page"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "DOI landing-resolution boundary must not claim refresh readiness"))
    if data.get("retrieved_at_utc") != EXPECTED_RETRIEVED_AT_UTC:
        issues.append(_issue("invalid_retrieved_at_utc", f"retrieved_at_utc must be {EXPECTED_RETRIEVED_AT_UTC}"))
    redirect_status = _validate_doi_redirect(data.get("doi_redirect"), issues)
    final_status = _validate_final_landing(data.get("final_landing"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "raw DOI resolver redirect headers" not in boundary_text
        or "does not claim full DOI redirect body retention" not in boundary_text
        or "automated DOI resolution refresh gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate DOI resolution headers from body/refresh evidence"))
    return AlphaEvolveDoiLandingResolutionBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        redirect_status=redirect_status,
        final_status=final_status,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_doi_landing_resolution_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_doi_landing_resolution_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve DOI landing-resolution boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| redirect_status | {validation.redirect_status or '<unknown>'} |",
        f"| final_status | {validation.final_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _validate_doi_redirect(
    value: object,
    issues: list[AlphaEvolveDoiLandingResolutionBoundaryIssue],
) -> int | None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_doi_redirect", "doi_redirect must be an object"))
        return None
    expected = {
        "url": EXPECTED_DOI_URL,
        "http_status": 302,
        "reason": "Found",
        "location": "https://arxiv.org/abs/2506.13131",
        "body_bytes": 149,
        "raw_header_lines": list(EXPECTED_DOI_REDIRECT_HEADER_LINES),
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_doi_redirect_{key}", f"doi_redirect.{key} must match pinned DOI resolver evidence"))
    status = value.get("http_status")
    return status if isinstance(status, int) else None


def _validate_final_landing(
    value: object,
    issues: list[AlphaEvolveDoiLandingResolutionBoundaryIssue],
) -> int | None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_final_landing", "final_landing must be an object"))
        return None
    expected = {
        "url": "https://arxiv.org/abs/2506.13131",
        "http_status": 200,
        "reason": "OK",
        "content_type": "text/html; charset=utf-8",
        "response_bytes": 49939,
        "response_sha256": "707d6aa982e50eca955e6cf7f4a86d2bce2ca6cea543827fea22537ef68d87bb",
        "raw_header_lines": list(EXPECTED_FINAL_LANDING_HEADER_LINES),
    }
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_final_landing_{key}", f"final_landing.{key} must match pinned arXiv landing evidence"))
    status = value.get("http_status")
    return status if isinstance(status, int) else None


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveDoiLandingResolutionBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "DOI landing-resolution boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveDoiLandingResolutionBoundaryIssue],
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
    issues: list[AlphaEvolveDoiLandingResolutionBoundaryIssue],
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
) -> AlphaEvolveDoiLandingResolutionBoundaryIssue:
    return AlphaEvolveDoiLandingResolutionBoundaryIssue(code, message)
