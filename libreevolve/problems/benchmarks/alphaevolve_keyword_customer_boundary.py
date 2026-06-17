from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_KEYWORD_CUSTOMER_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_keyword_customer_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "official_keyword_update_without_customer_availability_or_local_product_evidence"
)
EXPECTED_DOMAIN_CLAIMS = (
    "dna_sequencing_error_correction",
    "disaster_prediction_accuracy",
    "power_grid_stabilization_simulations",
    "molecular_simulations",
    "neuroscience_insights",
    "google_infrastructure_efficiency",
    "cloud_customer_ml_models",
    "cloud_customer_drug_discovery",
    "cloud_customer_supply_chains",
    "cloud_customer_warehouse_design",
)
EXPECTED_CUSTOMER_AVAILABILITY_ROWS = (
    "ml_model_improvement",
    "drug_discovery_acceleration",
    "supply_chain_improvement",
    "warehouse_design_optimization",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "keyword_article_url",
    "keyword_article_authors",
    "keyword_article_retrieval_html_sha256",
    "deepmind_impact_article_linkage",
    "google_cloud_private_preview_linkage",
    "research_to_real_world_claim",
    "domain_claim_table",
    "google_infrastructure_claim_separation",
    "customer_availability_rows",
    "customer_source_crosswalk",
    "named_customer_source_links",
    "cloud_account_access_evidence",
    "console_or_billing_artifact_inventory",
    "ui_or_api_artifact_inventory",
    "availability_geography_or_access_tier",
    "rollout_owner_metadata",
    "claim_value_normalization_policy",
    "independent_availability_assessment",
    "local_customer_case_fixture",
    "local_managed_service_support",
    "readme_roadmap_paper_index_boundary",
)
EXPECTED_MISSING_EVIDENCE = {
    "customer_source_crosswalk": "not_recorded_locally",
    "named_customer_source_links": "not_recorded_locally",
    "cloud_account_access_evidence": "not_recorded_locally",
    "console_or_billing_artifact_inventory": "not_recorded_locally",
    "ui_or_api_artifact_inventory": "not_recorded_locally",
    "availability_geography_or_access_tier": "not_recorded_locally",
    "rollout_owner_metadata": "not_recorded_locally",
    "claim_value_normalization_policy": "not_recorded_locally",
    "independent_availability_assessment": "not_recorded_locally",
    "local_customer_case_fixture": "not_implemented_locally",
    "local_managed_service_support": "not_implemented_locally",
}


@dataclass(frozen=True)
class AlphaEvolveKeywordCustomerBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveKeywordCustomerBoundaryValidation:
    ok: bool
    boundary_status: str | None
    domain_claim_count: int
    customer_availability_row_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveKeywordCustomerBoundaryIssue]


def alphaevolve_keyword_customer_boundary_record() -> dict[str, Any]:
    """Return the Google Keyword one-year customer-availability boundary."""

    return {
        "schema": ALPHAEVOLVE_KEYWORD_CUSTOMER_BOUNDARY_SCHEMA,
        "source_id": "google-keyword-alphaevolve-one-year-update",
        "source_family": "official_google_keyword_alphaevolve_customer_update",
        "source_relation": (
            "newer official customer-impact reporting, not local LibreEvolve "
            "customer availability, managed service support, or reproduced "
            "benchmark evidence"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "article": {
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
        },
        "source_linkage": {
            "deepmind_impact_article": (
                "https://deepmind.google/blog/alphaevolve-impact/"
            ),
            "cloud_private_preview_post": (
                "https://cloud.google.com/blog/products/ai-machine-learning/"
                "alphaevolve-on-google-cloud/"
            ),
            "relationship": (
                "Keyword update reports one-year impact and customer-facing "
                "domains; Cloud post separately describes private preview and "
                "Early Access path."
            ),
        },
        "domain_claims": [
            {
                "claim_id": "dna_sequencing_error_correction",
                "claim_group": "science",
                "source_status": "reported_without_local_fixture",
            },
            {
                "claim_id": "disaster_prediction_accuracy",
                "claim_group": "science",
                "source_status": "reported_without_local_fixture",
            },
            {
                "claim_id": "power_grid_stabilization_simulations",
                "claim_group": "science",
                "source_status": "reported_without_local_fixture",
            },
            {
                "claim_id": "molecular_simulations",
                "claim_group": "science",
                "source_status": "reported_without_local_fixture",
            },
            {
                "claim_id": "neuroscience_insights",
                "claim_group": "science",
                "source_status": "reported_without_local_fixture",
            },
            {
                "claim_id": "google_infrastructure_efficiency",
                "claim_group": "google_internal_infrastructure",
                "source_status": "separated_from_customer_availability",
            },
            {
                "claim_id": "cloud_customer_ml_models",
                "claim_group": "google_cloud_customer_impact",
                "source_status": "requires_customer_source_crosswalk",
            },
            {
                "claim_id": "cloud_customer_drug_discovery",
                "claim_group": "google_cloud_customer_impact",
                "source_status": "requires_customer_source_crosswalk",
            },
            {
                "claim_id": "cloud_customer_supply_chains",
                "claim_group": "google_cloud_customer_impact",
                "source_status": "requires_customer_source_crosswalk",
            },
            {
                "claim_id": "cloud_customer_warehouse_design",
                "claim_group": "google_cloud_customer_impact",
                "source_status": "requires_customer_source_crosswalk",
            },
        ],
        "customer_availability_rows": [
            {
                "row_id": "ml_model_improvement",
                "keyword_phrase": "improve their machine learning models",
                "availability_status": "source_reported_without_customer_matrix",
            },
            {
                "row_id": "drug_discovery_acceleration",
                "keyword_phrase": "accelerate drug discovery",
                "availability_status": "source_reported_without_customer_matrix",
            },
            {
                "row_id": "supply_chain_improvement",
                "keyword_phrase": "improve supply chains",
                "availability_status": "source_reported_without_customer_matrix",
            },
            {
                "row_id": "warehouse_design_optimization",
                "keyword_phrase": "optimize warehouse design",
                "availability_status": "source_reported_without_customer_matrix",
            },
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the official Google Keyword one-year "
            "AlphaEvolve article as source-reported science, Google "
            "infrastructure, and Google Cloud customer-impact context. It does "
            "not claim named-customer availability, customer source crosswalks, "
            "Cloud account access, UI/API/console/billing artifacts, rollout "
            "owner evidence, geographic or access-tier availability, independent "
            "availability assessment, local customer-case fixtures, or local "
            "managed AlphaEvolve service support in LibreEvolve."
        ),
    }


def validate_alphaevolve_keyword_customer_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveKeywordCustomerBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_keyword_customer_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AlphaEvolveKeywordCustomerBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveKeywordCustomerBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_KEYWORD_CUSTOMER_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Keyword customer boundary schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Keyword customer boundary must not claim customer availability"))
    _validate_article(data.get("article"), issues)
    _validate_source_linkage(data.get("source_linkage"), issues)
    domain_count = _validate_domain_claims(data.get("domain_claims"), issues)
    availability_count = _validate_customer_availability_rows(
        data.get("customer_availability_rows"), issues
    )
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim named-customer availability" not in boundary_text
        or "customer source crosswalks" not in boundary_text
        or "local managed AlphaEvolve service support" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must prevent customer availability overclaims"))
    return AlphaEvolveKeywordCustomerBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        domain_claim_count=domain_count,
        customer_availability_row_count=availability_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_keyword_customer_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_keyword_customer_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve Keyword customer boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| domain_claim_count | {validation.domain_claim_count} |",
        f"| customer_availability_row_count | {validation.customer_availability_row_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveKeywordCustomerBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Keyword customer boundary must be a JSON object")]


def _validate_article(
    value: object,
    issues: list[AlphaEvolveKeywordCustomerBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_article", "article must be an object"))
        return
    required_text = ("title", "url", "retrieved_on", "html_sha256")
    for key in required_text:
        if not isinstance(value.get(key), str) or not value.get(key):
            issues.append(_issue("invalid_article_field", f"article.{key} must be non-empty text"))
    if value.get("title") != "AlphaEvolve, 1 year later: Impact on science, technology":
        issues.append(_issue("invalid_article_title", "article title drifted"))
    authors = value.get("authors")
    if authors != ["Pushmeet Kohli", "Amin Vahdat"]:
        issues.append(_issue("invalid_article_authors", "article authors drifted"))
    html_bytes = value.get("html_bytes")
    if isinstance(html_bytes, bool) or not isinstance(html_bytes, int) or html_bytes <= 0:
        issues.append(_issue("invalid_article_bytes", "article html_bytes must be a positive integer"))
    sha = value.get("html_sha256")
    if isinstance(sha, str) and len(sha) != 64:
        issues.append(_issue("invalid_article_sha256", "article html_sha256 must be 64 hex characters"))


def _validate_source_linkage(
    value: object,
    issues: list[AlphaEvolveKeywordCustomerBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_source_linkage", "source_linkage must be an object"))
        return
    relationship = value.get("relationship")
    if (
        not isinstance(relationship, str)
        or "one-year impact" not in relationship
        or "private preview" not in relationship
        or "Early Access" not in relationship
    ):
        issues.append(_issue("invalid_source_linkage_relationship", "source linkage must separate Keyword and Cloud post scope"))


def _validate_domain_claims(
    value: object,
    issues: list[AlphaEvolveKeywordCustomerBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_domain_claims", "domain_claims must be a list"))
        return 0
    claim_ids = []
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_domain_claim_entry", "domain claim entries must be objects"))
            continue
        claim_id = item.get("claim_id")
        if isinstance(claim_id, str):
            claim_ids.append(claim_id)
        for key in ("claim_group", "source_status"):
            if not isinstance(item.get(key), str) or not item.get(key):
                issues.append(_issue("invalid_domain_claim_entry", f"domain claim entry must include {key}"))
                break
    if tuple(claim_ids) != EXPECTED_DOMAIN_CLAIMS:
        issues.append(_issue("invalid_domain_claim_ids", "domain claims must preserve expected Keyword claim ids"))
    return len(claim_ids)


def _validate_customer_availability_rows(
    value: object,
    issues: list[AlphaEvolveKeywordCustomerBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_customer_availability_rows", "customer_availability_rows must be a list"))
        return 0
    row_ids = []
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_customer_availability_entry", "customer availability entries must be objects"))
            continue
        row_id = item.get("row_id")
        if isinstance(row_id, str):
            row_ids.append(row_id)
        phrase = item.get("keyword_phrase")
        status = item.get("availability_status")
        if not isinstance(phrase, str) or not phrase:
            issues.append(_issue("invalid_customer_availability_phrase", "customer availability row must include keyword_phrase"))
        if status != "source_reported_without_customer_matrix":
            issues.append(_issue("invalid_customer_availability_status", "customer availability must remain source-reported only"))
    if tuple(row_ids) != EXPECTED_CUSTOMER_AVAILABILITY_ROWS:
        issues.append(_issue("invalid_customer_availability_row_ids", "customer availability rows drifted"))
    return len(row_ids)


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveKeywordCustomerBoundaryIssue],
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
    issues: list[AlphaEvolveKeywordCustomerBoundaryIssue],
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


def _issue(code: str, message: str) -> AlphaEvolveKeywordCustomerBoundaryIssue:
    return AlphaEvolveKeywordCustomerBoundaryIssue(code, message)
