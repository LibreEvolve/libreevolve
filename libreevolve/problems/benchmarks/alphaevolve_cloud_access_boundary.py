from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_CLOUD_ACCESS_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_cloud_access_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "official_google_cloud_sources_without_local_service_access_or_managed_agent_evidence"
)
EXPECTED_SOURCE_IDS = (
    "google-cloud-alphaevolve-private-preview",
    "gemini-enterprise-coscientist-alphaevolve-prega",
    "google-keyword-alphaevolve-one-year-update",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "cloud_blog_url",
    "cloud_blog_publication_date",
    "cloud_blog_authors",
    "cloud_blog_retrieval_html_sha256",
    "deepmind_impact_linkage",
    "private_preview_status",
    "service_api_access_model",
    "early_access_registration_path",
    "google_cloud_representative_requirement",
    "service_api_endpoint_schema_inventory",
    "service_api_auth_model",
    "console_artifact_inventory",
    "billing_artifact_inventory",
    "gemini_enterprise_docs_url",
    "gemini_enterprise_docs_last_updated",
    "gemini_enterprise_pre_ga_terms_status",
    "restricted_access_contact_path",
    "account_team_documentation_boundary",
    "managed_agent_workflow_semantics",
    "customer_availability_source_snapshot",
    "keyword_customer_claim_source_snapshot",
    "external_availability_assessment",
    "security_and_data_use_boundary",
    "libreevolve_provider_adapter_status",
)
EXPECTED_MISSING_EVIDENCE = {
    "service_api_endpoint_schema_inventory": "not_publicly_documented_locally",
    "service_api_auth_model": "not_recorded_locally",
    "console_artifact_inventory": "not_recorded_locally",
    "billing_artifact_inventory": "not_recorded_locally",
    "early_access_eligibility_evidence": "not_recorded_locally",
    "private_preview_terms_snapshot": "not_recorded_locally",
    "account_team_handoff_artifact": "not_recorded_locally",
    "managed_agent_execution_transcript": "not_recorded_locally",
    "customer_availability_matrix": "not_recorded_locally",
    "customer_source_crosswalk": "not_recorded_locally",
    "external_account_availability_check": "not_recorded_locally",
    "security_review_and_data_use_terms": "not_recorded_locally",
    "libreevolve_cloud_provider_adapter": "not_implemented_locally",
}


@dataclass(frozen=True)
class AlphaEvolveCloudAccessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveCloudAccessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    source_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveCloudAccessBoundaryIssue]


def alphaevolve_cloud_access_boundary_record() -> dict[str, Any]:
    """Return the Google Cloud AlphaEvolve product/access claim boundary."""

    return {
        "schema": ALPHAEVOLVE_CLOUD_ACCESS_BOUNDARY_SCHEMA,
        "source_family": "official_google_cloud_alphaevolve_product_surfaces",
        "source_relation": (
            "newer official product/access reporting, not local LibreEvolve "
            "provider support and not original AlphaEvolve paper parity"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "sources": [
            {
                "source_id": "google-cloud-alphaevolve-private-preview",
                "title": (
                    "AlphaEvolve on Google Cloud: AI for agentic discovery "
                    "and optimization"
                ),
                "url": (
                    "https://cloud.google.com/blog/products/ai-machine-learning/"
                    "alphaevolve-on-google-cloud/"
                ),
                "publication_date": "2025-12-09",
                "authors": [
                    "Vladimir Vuskovic",
                    "Anant Nawalgaria",
                ],
                "retrieved_on": "2026-06-17",
                "html_bytes": 232057,
                "html_sha256": (
                    "5573e49c92b71e1afaf77346ab0a0ea0a0d52b748701475fd"
                    "5474750cbbc2065"
                ),
                "source_status": (
                    "official_cloud_blog_private_preview_and_early_access_source"
                ),
            },
            {
                "source_id": "gemini-enterprise-coscientist-alphaevolve-prega",
                "title": "Accelerate R&D with Co-Scientist and AlphaEvolve agents",
                "url": (
                    "https://docs.cloud.google.com/gemini/enterprise/docs/"
                    "co-scientist-and-alphaevolve"
                ),
                "last_updated": "2026-06-15 UTC",
                "retrieved_on": "2026-06-17",
                "html_bytes": 121651,
                "html_sha256": (
                    "34facc6ea7522f3acfd51e55123f6e5a16e10bb4fa6dd04"
                    "b3bb2df5243a91261"
                ),
                "source_status": "official_cloud_docs_preview_restricted_access_source",
            },
            {
                "source_id": "google-keyword-alphaevolve-one-year-update",
                "title": "AlphaEvolve, 1 year later: Impact on science, technology",
                "url": (
                    "https://blog.google/innovation-and-ai/infrastructure-and-cloud/"
                    "google-cloud/alphaevolve-updates/"
                ),
                "authors": [
                    "Pushmeet Kohli",
                    "Amin Vahdat",
                ],
                "retrieved_on": "2026-06-17",
                "html_bytes": 394899,
                "html_sha256": (
                    "435c8244ef63c997a1a5bcdb657ca915703ac588d9533a3a90"
                    "e1f7784a79e428"
                ),
                "source_status": (
                    "official_keyword_customer_availability_context_source"
                ),
            },
        ],
        "source_claims": {
            "private_preview_status": (
                "Google Cloud blog says AlphaEvolve is being released to "
                "Google Cloud in private preview."
            ),
            "service_api_access_model": (
                "Google Cloud blog says the AlphaEvolve Service API is "
                "available through an Early Access Program with Google Cloud."
            ),
            "early_access_registration_path": (
                "Interested users are directed to reach out to their Google "
                "Cloud representative."
            ),
            "gemini_enterprise_pre_ga_terms_status": (
                "Gemini Enterprise docs mark Co-Scientist and AlphaEvolve "
                "agents as Preview/Pre-GA and subject to Pre-GA terms."
            ),
            "restricted_access_contact_path": (
                "Gemini Enterprise docs say access is restricted and users "
                "should contact their Google account team."
            ),
            "account_team_documentation_boundary": (
                "Gemini Enterprise docs say detailed product documentation is "
                "provided by account teams after access is granted."
            ),
            "keyword_customer_claim_source_snapshot": (
                "Google Keyword article reports Google Cloud customer impact "
                "areas, but does not provide local LibreEvolve access evidence."
            ),
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records official Google Cloud, Gemini Enterprise, "
            "and Google Keyword product/source snapshots for AlphaEvolve access "
            "claims. It does not claim LibreEvolve has Google Cloud "
            "AlphaEvolve private-preview access, AlphaEvolve Service API "
            "endpoint/schema documentation, console/API/billing artifacts, "
            "Gemini Enterprise managed-agent execution evidence, customer "
            "availability verification, security/data-use review, or a local "
            "Cloud AlphaEvolve provider adapter."
        ),
    }


def validate_alphaevolve_cloud_access_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveCloudAccessBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_cloud_access_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AlphaEvolveCloudAccessBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AlphaEvolveCloudAccessBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_CLOUD_ACCESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported cloud access boundary schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "cloud access boundary must not claim local service access"))
    source_count = _validate_sources(data.get("sources"), issues)
    _validate_source_claims(data.get("source_claims"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim LibreEvolve has Google Cloud AlphaEvolve" not in boundary_text
        or "AlphaEvolve Service API endpoint/schema documentation" not in boundary_text
        or "local Cloud AlphaEvolve provider adapter" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must prevent Cloud/API/Gemini overclaims"))
    return AlphaEvolveCloudAccessBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        source_count=source_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_cloud_access_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_alphaevolve_cloud_access_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve cloud access boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| source_count | {validation.source_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveCloudAccessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "cloud access boundary must be a JSON object")]


def _validate_sources(
    value: object,
    issues: list[AlphaEvolveCloudAccessBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_sources", "sources must be a list"))
        return 0
    source_ids = []
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_entry", "source entries must be objects"))
            continue
        source_id = item.get("source_id")
        if isinstance(source_id, str):
            source_ids.append(source_id)
        for key in ("title", "url", "retrieved_on", "html_sha256", "source_status"):
            if not isinstance(item.get(key), str) or not item.get(key):
                issues.append(_issue("invalid_source_entry", f"source entry must include {key}"))
                break
        html_bytes = item.get("html_bytes")
        if isinstance(html_bytes, bool) or not isinstance(html_bytes, int) or html_bytes <= 0:
            issues.append(_issue("invalid_source_bytes", "source html_bytes must be a positive integer"))
        sha = item.get("html_sha256")
        if isinstance(sha, str) and len(sha) != 64:
            issues.append(_issue("invalid_source_sha256", "source html_sha256 must be 64 hex characters"))
    if tuple(source_ids) != EXPECTED_SOURCE_IDS:
        issues.append(_issue("invalid_source_ids", "sources must preserve the expected official source ids"))
    return len(source_ids)


def _validate_source_claims(
    value: object,
    issues: list[AlphaEvolveCloudAccessBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_source_claims", "source_claims must be an object"))
        return
    required_snippets = {
        "private_preview_status": "private preview",
        "service_api_access_model": "Early Access Program",
        "early_access_registration_path": "Google Cloud representative",
        "gemini_enterprise_pre_ga_terms_status": "Pre-GA",
        "restricted_access_contact_path": "Google account team",
        "account_team_documentation_boundary": "after access is granted",
        "keyword_customer_claim_source_snapshot": "customer impact",
    }
    for key, snippet in required_snippets.items():
        text = value.get(key)
        if not isinstance(text, str) or snippet not in text:
            issues.append(_issue(f"invalid_source_claim_{key}", f"source_claims.{key} must mention {snippet}"))


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveCloudAccessBoundaryIssue],
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
    issues: list[AlphaEvolveCloudAccessBoundaryIssue],
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


def _issue(code: str, message: str) -> AlphaEvolveCloudAccessBoundaryIssue:
    return AlphaEvolveCloudAccessBoundaryIssue(code, message)
