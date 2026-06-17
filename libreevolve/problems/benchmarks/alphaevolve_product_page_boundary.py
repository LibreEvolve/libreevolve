from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_PRODUCT_PAGE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_product_page_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "outbound_deepmind_product_page_reference_currently_unavailable_without_snapshot"
)
EXPECTED_PRODUCT_URL = "https://deepmind.google/science/alphaevolve/"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "canonical_url",
    "retrieval_date",
    "http_status",
    "page_title",
    "page_subtitle",
    "html_byte_count",
    "html_sha256",
    "science_navigation_placement",
    "outbound_link_inventory",
    "media_asset_inventory",
    "access_or_availability_statement",
    "product_page_to_whitepaper_relation",
    "product_page_to_announcement_relation",
    "product_page_to_impact_article_relation",
    "product_page_to_cloud_preview_relation",
    "local_libreevolve_support_boundary",
    "independent_availability_check",
    "product_page_snapshot_verifier",
)
EXPECTED_MISSING_EVIDENCE = {
    "reachable_product_page_snapshot": "http_404_not_found_on_2026_06_17",
    "page_title": "not_recorded_because_page_unavailable",
    "page_subtitle": "not_recorded_because_page_unavailable",
    "html_sha256": "not_recorded_because_page_unavailable",
    "science_navigation_placement": "not_recorded_locally",
    "outbound_link_inventory": "not_recorded_because_page_unavailable",
    "media_asset_inventory": "not_recorded_because_page_unavailable",
    "access_or_availability_statement": "not_recorded_because_page_unavailable",
    "product_page_snapshot_verifier": "not_implemented_locally",
    "managed_alphaevolve_compatibility_claim": "not_supported_locally",
}


@dataclass(frozen=True)
class AlphaEvolveProductPageBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveProductPageBoundaryValidation:
    ok: bool
    boundary_status: str | None
    http_status: int | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveProductPageBoundaryIssue]


def alphaevolve_product_page_boundary_record() -> dict[str, Any]:
    """Return the DeepMind AlphaEvolve product/science page boundary."""

    return {
        "schema": ALPHAEVOLVE_PRODUCT_PAGE_BOUNDARY_SCHEMA,
        "source_id": "deepmind-alphaevolve-product-page",
        "source_family": "official_google_deepmind_science_page_reference",
        "source_relation": (
            "outbound product/science context from the 2026 impact boundary, "
            "not original white-paper specification and not local implementation "
            "or managed-service evidence"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "retrieval": {
            "url": EXPECTED_PRODUCT_URL,
            "retrieved_on": "2026-06-17",
            "http_status": 404,
            "reason": "Not Found",
            "html_bytes": None,
            "html_sha256": None,
        },
        "recorded_product_context": {
            "source_in_alphaevolve_2026_impact_boundary": (
                "outbound link id alphaevolve_product_page, category product_context"
            ),
            "search_snippet_context": (
                "search snippets have positioned AlphaEvolve as a Gemini-built "
                "coding agent for designing advanced algorithms by combining "
                "large language model creativity with automated evaluators"
            ),
            "current_page_snapshot_status": "unavailable_http_404",
        },
        "relation_boundaries": {
            "white_paper": "separate AlphaEvolve specification source",
            "announcement_blog": "separate May 2025 official announcement source",
            "impact_article": "separate May 2026 official impact source",
            "google_cloud_private_preview": "separate Cloud access/product source",
            "libreevolve_support": "no local product-page implementation evidence",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that the DeepMind AlphaEvolve product/science "
            "page URL currently resolves as HTTP 404 from this repository audit. "
            "It does not claim a reachable product-page HTML snapshot, title, "
            "subtitle, navigation placement, outbound links, media assets, "
            "access statement, independent availability check, product-page "
            "snapshot verifier, local LibreEvolve support, or managed "
            "AlphaEvolve compatibility."
        ),
    }


def validate_alphaevolve_product_page_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveProductPageBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_product_page_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AlphaEvolveProductPageBoundaryValidation(
            False, None, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveProductPageBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_PRODUCT_PAGE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported product page boundary schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "product page boundary must not claim reachable implementation evidence"))
    http_status = _validate_retrieval(data.get("retrieval"), issues)
    _validate_recorded_context(data.get("recorded_product_context"), issues)
    _validate_relation_boundaries(data.get("relation_boundaries"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "HTTP 404" not in boundary_text
        or "does not claim a reachable product-page HTML snapshot" not in boundary_text
        or "managed AlphaEvolve compatibility" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must prevent product-page availability overclaims"))
    return AlphaEvolveProductPageBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        http_status=http_status,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_product_page_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_alphaevolve_product_page_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve product page boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| http_status | {validation.http_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveProductPageBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "product page boundary must be a JSON object")]


def _validate_retrieval(
    value: object,
    issues: list[AlphaEvolveProductPageBoundaryIssue],
) -> int | None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_retrieval", "retrieval must be an object"))
        return None
    if value.get("url") != EXPECTED_PRODUCT_URL:
        issues.append(_issue("invalid_product_url", f"retrieval.url must be {EXPECTED_PRODUCT_URL}"))
    if value.get("retrieved_on") != "2026-06-17":
        issues.append(_issue("invalid_retrieved_on", "retrieved_on must record the audit date"))
    status = value.get("http_status")
    if status != 404:
        issues.append(_issue("invalid_http_status", "product page retrieval must preserve current HTTP 404 status"))
    if value.get("reason") != "Not Found":
        issues.append(_issue("invalid_http_reason", "retrieval reason must be Not Found"))
    if value.get("html_bytes") is not None or value.get("html_sha256") is not None:
        issues.append(_issue("invalid_unavailable_html_fields", "unavailable page must not claim html bytes or sha256"))
    return status if isinstance(status, int) and not isinstance(status, bool) else None


def _validate_recorded_context(
    value: object,
    issues: list[AlphaEvolveProductPageBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_recorded_product_context", "recorded_product_context must be an object"))
        return
    impact = value.get("source_in_alphaevolve_2026_impact_boundary")
    snippet = value.get("search_snippet_context")
    snapshot = value.get("current_page_snapshot_status")
    if not isinstance(impact, str) or "alphaevolve_product_page" not in impact:
        issues.append(_issue("invalid_impact_boundary_context", "context must reference alphaevolve_product_page"))
    if not isinstance(snippet, str) or "Gemini-built" not in snippet or "automated evaluators" not in snippet:
        issues.append(_issue("invalid_search_snippet_context", "search snippet context must preserve product positioning"))
    if snapshot != "unavailable_http_404":
        issues.append(_issue("invalid_page_snapshot_status", "current page snapshot status must remain unavailable_http_404"))


def _validate_relation_boundaries(
    value: object,
    issues: list[AlphaEvolveProductPageBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_relation_boundaries", "relation_boundaries must be an object"))
        return
    expected_keys = {
        "white_paper",
        "announcement_blog",
        "impact_article",
        "google_cloud_private_preview",
        "libreevolve_support",
    }
    actual_keys = set(value)
    if actual_keys != expected_keys:
        issues.append(_issue("invalid_relation_boundary_keys", "relation boundary keys drifted"))
    for key in expected_keys:
        if not isinstance(value.get(key), str) or not value[key]:
            issues.append(_issue("invalid_relation_boundary_value", "relation boundary values must be non-empty text"))


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveProductPageBoundaryIssue],
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
    issues: list[AlphaEvolveProductPageBoundaryIssue],
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


def _issue(code: str, message: str) -> AlphaEvolveProductPageBoundaryIssue:
    return AlphaEvolveProductPageBoundaryIssue(code, message)
