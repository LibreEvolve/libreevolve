from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALPHAEVOLVE_2026_IMPACT_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_2026_impact_boundary.v1"
)
EXPECTED_IMPACT_BOUNDARY_FILE = "papers/alphaevolve_2026_impact_boundary.json"
EXPECTED_ARTICLE_URL = "https://deepmind.google/blog/alphaevolve-impact/"
EXPECTED_ARTICLE_TITLE = (
    "AlphaEvolve: How our Gemini-powered coding agent is scaling impact across fields"
)
EXPECTED_ARTICLE_DATE = "2026-05-07"
EXPECTED_ARTICLE_AUTHOR = "AlphaEvolve team"
EXPECTED_ARTICLE_SECTION = "Science"
EXPECTED_RETRIEVED_ON = "2026-06-12"
EXPECTED_HTML_BYTES = 156554
EXPECTED_HTML_SHA256 = (
    "2b56730407c01a316325222beda6c9c45727362505005c81a3bbc40bc5c4c97d"
)
EXPECTED_BOUNDARY_STATUS = (
    "official_2026_impact_article_without_local_deployment_benchmarks"
)
EXPECTED_COMPONENT_IDS = (
    "source_artifact_snapshot",
    "outbound_link_inventory",
    "impact_claim_registry",
    "domain_category_taxonomy",
    "value_unit_baseline_records",
    "customer_case_registry",
    "public_gallery_inventory",
    "ui_api_attribution_records",
    "linked_source_evidence_status",
    "local_fixture_support_status",
    "independent_verification_status",
    "readme_roadmap_claim_boundary",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "canonical_url",
    "publication_date",
    "article_title",
    "author_or_team",
    "source_section",
    "retrieval_timestamp",
    "retrieval_html_bytes",
    "retrieval_html_sha256",
    "outbound_link_inventory",
    "claim_ids",
    "domain_categories",
    "value_fields",
    "unit_fields",
    "baseline_fields",
    "linked_source_urls",
    "linked_source_status",
    "customer_case_names",
    "deployment_attribution_labels",
    "public_gallery_url",
    "ui_contributor_attribution",
    "api_cloud_contributor_attribution",
    "local_fixture_status",
    "local_benchmark_report_status",
    "unsupported_local_benchmark_flags",
    "independent_verification_status",
    "original_spec_separation",
    "libreevolve_feature_support_separation",
    "readme_claim_boundary",
    "roadmap_claim_boundary",
    "paper_index_claim_boundary",
)
EXPECTED_CLAIM_IDS = (
    "deepconsensus_variant_error_reduction",
    "ac_opf_feasibility_improvement",
    "earth_ai_disaster_risk_accuracy_gain",
    "willow_quantum_circuit_error_reduction",
    "erdos_public_gallery_examples",
    "traveling_salesman_lower_bound",
    "ramsey_numbers_lower_bound",
    "neuroscience_interpretable_models",
    "microeconomics_market_limits",
    "neural_network_building_blocks",
    "cryptography_user_privacy",
    "synthetic_data_generation",
    "frontier_ai_safety_mitigations",
    "next_generation_tpu_design",
    "cache_replacement_policy_effort",
    "spanner_write_amplification_reduction",
    "compiler_storage_footprint_reduction",
    "klarna_training_speed",
    "substrate_lithography_runtime",
    "fm_logistic_routing_efficiency",
    "wpp_accuracy_gain",
    "schrodinger_mlff_speedup",
)
EXPECTED_MISSING_EVIDENCE = {
    "deepconsensus_local_variant_detection_benchmark": "not_implemented_locally",
    "ac_opf_local_power_grid_fixture": "not_implemented_locally",
    "earth_ai_local_geospatial_fixture": "not_implemented_locally",
    "willow_quantum_circuit_fixture": "not_implemented_locally",
    "public_gallery_snapshot_hashes": "not_recorded_locally",
    "traveling_salesman_lower_bound_checker": "not_implemented_locally",
    "ramsey_number_graph_checker": "not_implemented_locally",
    "neuroscience_model_fixture": "not_implemented_locally",
    "microeconomics_market_limit_fixture": "not_implemented_locally",
    "neural_network_building_block_fixture": "not_implemented_locally",
    "cryptography_privacy_fixture": "not_implemented_locally",
    "synthetic_data_generation_fixture": "not_implemented_locally",
    "safety_mitigation_fixture": "not_implemented_locally",
    "tpu_design_deployment_evidence": "not_recorded_locally",
    "cache_policy_runtime_reproduction": "not_implemented_locally",
    "spanner_lsm_compaction_fixture": "not_implemented_locally",
    "compiler_storage_benchmark": "not_implemented_locally",
    "customer_case_source_snapshots": "not_recorded_locally",
    "ui_surface_artifact_inventory": "not_recorded_locally",
    "api_cloud_customer_artifact_inventory": "not_recorded_locally",
    "linked_source_independent_verification": "not_recorded_locally",
    "local_benchmark_reports": "not_implemented_locally",
    "claim_value_normalization_policy": "not_recorded_locally",
    "release_note_claim_gate": "not_implemented_locally",
}


@dataclass(frozen=True)
class AlphaEvolve2026ImpactBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolve2026ImpactBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    claim_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolve2026ImpactBoundaryIssue]


def alphaevolve_2026_impact_boundary_record() -> dict[str, Any]:
    """Return the source boundary for the official 2026 AlphaEvolve impact article."""

    return {
        "schema": ALPHAEVOLVE_2026_IMPACT_BOUNDARY_SCHEMA,
        "source_id": "google-deepmind-alphaevolve-impact-2026-05-07",
        "source_family": "official_google_deepmind_alphaevolve_impact_article",
        "source_relation": (
            "newer official impact reporting, not the original AlphaEvolve "
            "specification and not reproduced LibreEvolve benchmark evidence"
        ),
        "article": {
            "title": EXPECTED_ARTICLE_TITLE,
            "url": EXPECTED_ARTICLE_URL,
            "date": EXPECTED_ARTICLE_DATE,
            "author": EXPECTED_ARTICLE_AUTHOR,
            "section": EXPECTED_ARTICLE_SECTION,
            "retrieval": {
                "retrieved_on": EXPECTED_RETRIEVED_ON,
                "html_bytes": EXPECTED_HTML_BYTES,
                "html_sha256": EXPECTED_HTML_SHA256,
                "hash_algorithm": "sha256",
            },
        },
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "outbound_links": [
            {
                "link_id": "alphaevolve_product_page",
                "url": "https://deepmind.google/science/alphaevolve/",
                "category": "product_context",
                "status": "outbound_reference_only",
            },
            {
                "link_id": "deepconsensus_nature",
                "url": "https://www.nature.com/articles/s41587-022-01435-7",
                "category": "linked_scientific_source",
                "status": "requires_separate_source_record",
            },
            {
                "link_id": "ac_optimal_power_flow_arxiv",
                "url": "https://arxiv.org/abs/2406.07200",
                "category": "linked_scientific_source",
                "status": "requires_separate_source_record",
            },
            {
                "link_id": "earth_ai_accuracy_arxiv",
                "url": "https://arxiv.org/abs/2507.11095",
                "category": "linked_scientific_source",
                "status": "requires_separate_source_record",
            },
            {
                "link_id": "willow_quantum_arxiv",
                "url": "https://arxiv.org/abs/2506.20661",
                "category": "linked_scientific_source",
                "status": "requires_separate_source_record",
            },
            {
                "link_id": "alphaevolve_public_gallery",
                "url": "https://alphaevolve-examples.web.app/",
                "category": "public_gallery",
                "status": "requires_snapshot_inventory",
            },
            {
                "link_id": "cache_replacement_policy_arxiv",
                "url": "https://arxiv.org/abs/2604.19837",
                "category": "linked_scientific_source",
                "status": "requires_separate_source_record",
            },
            {
                "link_id": "compiler_storage_arxiv",
                "url": "https://arxiv.org/abs/2604.15285",
                "category": "linked_scientific_source",
                "status": "requires_separate_source_record",
            },
            {
                "link_id": "fm_logistic_case",
                "url": "https://cloud.google.com/customers/fm-logistic",
                "category": "customer_case",
                "status": "requires_customer_source_snapshot",
            },
        ],
        "framework_components": [
            {
                "component_id": component_id,
                "local_status": "boundary_only",
            }
            for component_id in EXPECTED_COMPONENT_IDS
        ],
        "claim_registry": _impact_claims(),
        "customer_cases": [
            {
                "customer": "Klarna",
                "domain": "financial_services",
                "reported_result": "doubling transformer-model training speed while improving quality",
                "local_evidence": False,
            },
            {
                "customer": "Substrate",
                "domain": "semiconductor_manufacturing",
                "reported_result": "multi-fold computational-lithography runtime speed increase",
                "local_evidence": False,
            },
            {
                "customer": "FM Logistic",
                "domain": "logistics",
                "reported_result": "10.4% routing-efficiency improvement and over 15000 km saved annually",
                "local_evidence": False,
            },
            {
                "customer": "WPP",
                "domain": "advertising_and_marketing",
                "reported_result": "10% accuracy gain over competitive manual optimizations",
                "local_evidence": False,
            },
            {
                "customer": "Schrodinger",
                "domain": "computational_material_and_life_sciences",
                "reported_result": "roughly 4x Machine Learned Force Fields training and inference speedup",
                "local_evidence": False,
            },
        ],
        "attribution": {
            "initial_development_team_recorded": True,
            "scaling_impact_contributors_recorded": True,
            "ui_contributors_recorded": True,
            "api_cloud_contributors_recorded": True,
            "collaborator_application_names_recorded": True,
            "local_role_artifact_links_ready": False,
        },
        "local_evidence": {
            "deepconsensus_fixture_ready": False,
            "ac_opf_fixture_ready": False,
            "earth_ai_fixture_ready": False,
            "willow_quantum_fixture_ready": False,
            "gallery_snapshot_ready": False,
            "tpu_design_fixture_ready": False,
            "cache_policy_fixture_ready": False,
            "spanner_fixture_ready": False,
            "compiler_storage_fixture_ready": False,
            "customer_case_snapshots_ready": False,
            "ui_api_artifact_inventory_ready": False,
            "independent_verification_ready": False,
            "repository_runtime_verified": False,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This record preserves the official 2026 DeepMind impact article as "
            "source evidence only. It does not claim LibreEvolve implements or "
            "reproduces the named DeepConsensus, AC OPF, Earth AI, Willow, TPU, "
            "cache-policy, Spanner, compiler-storage, public-gallery, customer, "
            "UI, or API workflows."
        ),
    }


def validate_alphaevolve_2026_impact_boundary(
    recordset: object | str | Path | None = None,
) -> AlphaEvolve2026ImpactBoundaryValidation:
    data, read_issues = _load_recordset(recordset)
    if read_issues:
        return AlphaEvolve2026ImpactBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolve2026ImpactBoundaryIssue] = []

    _validate_scalar(data, "schema", ALPHAEVOLVE_2026_IMPACT_BOUNDARY_SCHEMA, issues)
    _validate_scalar(data, "source_id", "google-deepmind-alphaevolve-impact-2026-05-07", issues)
    _validate_scalar(data, "source_family", "official_google_deepmind_alphaevolve_impact_article", issues)
    _validate_article(data.get("article"), issues)
    _validate_scalar(data, "boundary_status", EXPECTED_BOUNDARY_STATUS, issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "claim_ready must remain false until local benchmark evidence exists"))

    _validate_outbound_links(data.get("outbound_links"), issues)
    component_count = _validate_components(data.get("framework_components"), issues)
    claim_count = _validate_claim_registry(data.get("claim_registry"), issues)
    _validate_customer_cases(data.get("customer_cases"), issues)
    _validate_attribution(data.get("attribution"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    required_count = _validate_required_evidence(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary = data.get("claim_boundary")
    if not isinstance(boundary, str) or "does not claim LibreEvolve implements" not in boundary:
        issues.append(_issue("invalid_claim_boundary", "claim_boundary must deny local implementation/reproduction claims"))

    return AlphaEvolve2026ImpactBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        component_count=component_count,
        claim_count=claim_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_2026_impact_boundary_summary(
    recordset: object | str | Path | None = None,
) -> str:
    validation = validate_alphaevolve_2026_impact_boundary(recordset)
    rows = [
        ("schema_status", "ok" if validation.ok else "invalid"),
        ("boundary_status", validation.boundary_status or "<missing>"),
        ("component_count", str(validation.component_count)),
        ("claim_count", str(validation.claim_count)),
        ("required_evidence_field_count", str(validation.required_evidence_field_count)),
        ("missing_evidence_count", str(validation.missing_evidence_count)),
    ]
    lines = ["# AlphaEvolve 2026 impact boundary", "", "| field | value |", "| --- | --- |"]
    lines.extend(f"| {field} | {value} |" for field, value in rows)
    return "\n".join(lines) + "\n"


def _impact_claims() -> list[dict[str, Any]]:
    return [
        _claim("deepconsensus_variant_error_reduction", "genomics", 30, "percent_error_reduction", "variant detection errors", "external_claim_requires_reproduction"),
        _claim("ac_opf_feasibility_improvement", "power_grid_optimization", "14_to_over_88", "percent_feasible_solutions", "trained GNN model feasibility", "external_claim_requires_reproduction"),
        _claim("earth_ai_disaster_risk_accuracy_gain", "earth_sciences", 5, "percent_accuracy_gain", "20-category disaster-risk prediction accuracy", "external_claim_requires_reproduction"),
        _claim("willow_quantum_circuit_error_reduction", "quantum_physics", 10, "x_lower_error", "previous conventional optimization baselines", "external_claim_requires_reproduction"),
        _claim("erdos_public_gallery_examples", "mathematics", "public_gallery_examples", "description", "public AlphaEvolve examples", "gallery_snapshot_required"),
        _claim("traveling_salesman_lower_bound", "mathematics", "improved_lower_bounds", "description", "classic TSP challenge", "linked_source_required"),
        _claim("ramsey_numbers_lower_bound", "mathematics", "improved_lower_bounds", "description", "Ramsey number challenge", "linked_source_required"),
        _claim("neuroscience_interpretable_models", "neuroscience", "discovering_interpretable_models", "description", "linked bioRxiv source", "linked_source_required"),
        _claim("microeconomics_market_limits", "microeconomics", "new_market_limits", "description", "linked arXiv source", "linked_source_required"),
        _claim("neural_network_building_blocks", "ai_research", "advancing_neural_network_building_blocks", "description", "linked arXiv source", "linked_source_required"),
        _claim("cryptography_user_privacy", "cryptography", "cryptography_for_user_privacy", "description", "linked arXiv source", "linked_source_required"),
        _claim("synthetic_data_generation", "ai_research", "synthetic_data_generation", "description", "linked arXiv source", "linked_source_required"),
        _claim("frontier_ai_safety_mitigations", "ai_safety", "critical_safety_mitigations", "description", "linked arXiv source", "linked_source_required"),
        _claim("next_generation_tpu_design", "ai_infrastructure", "regular_tool_for_next_generation_tpu_design", "description", "Google infrastructure deployment", "deployment_evidence_required"),
        _claim("cache_replacement_policy_effort", "ai_infrastructure", "two_days_vs_months", "time_to_result", "human-intensive months", "linked_source_required"),
        _claim("spanner_write_amplification_reduction", "database_infrastructure", 20, "percent_write_amplification_reduction", "Spanner LSM compaction heuristics", "external_claim_requires_reproduction"),
        _claim("compiler_storage_footprint_reduction", "compiler_optimization", 9, "nearly_percent_storage_footprint_reduction", "software storage footprint", "external_claim_requires_reproduction"),
        _claim("klarna_training_speed", "commercial_financial_services", 2, "x_training_speed", "large transformer model", "customer_source_required"),
        _claim("substrate_lithography_runtime", "commercial_semiconductors", "multi_fold", "runtime_speed_increase", "computational lithography framework", "customer_source_required"),
        _claim("fm_logistic_routing_efficiency", "commercial_logistics", 10.4, "percent_routing_efficiency_improvement", "previous heavily optimized solutions", "customer_source_required"),
        _claim("wpp_accuracy_gain", "commercial_advertising", 10, "percent_accuracy_gain", "competitive manual model optimizations", "customer_source_required"),
        _claim("schrodinger_mlff_speedup", "commercial_life_sciences", 4, "roughly_x_training_and_inference_speedup", "MLFF training and inference", "customer_source_required"),
    ]


def _claim(
    claim_id: str,
    domain: str,
    value: object,
    unit: str,
    baseline: str,
    evidence_status: str,
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "domain": domain,
        "value": value,
        "unit": unit,
        "baseline": baseline,
        "source": "official_2026_impact_article",
        "evidence_status": evidence_status,
        "local_benchmark_supported": False,
    }


def _load_recordset(
    recordset: object | str | Path | None,
) -> tuple[dict[str, Any] | None, list[AlphaEvolve2026ImpactBoundaryIssue]]:
    if recordset is None:
        return alphaevolve_2026_impact_boundary_record(), []
    if isinstance(recordset, dict):
        return recordset, []
    if isinstance(recordset, (str, Path)):
        try:
            data = json.loads(Path(recordset).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_recordset", f"could not read impact boundary: {exc}")]
        if not isinstance(data, dict):
            return None, [_issue("invalid_recordset", "impact boundary must be a JSON object")]
        return data, []
    return None, [_issue("invalid_recordset", "impact boundary must be an object or path")]


def _validate_scalar(
    data: dict[str, Any],
    field: str,
    expected: object,
    issues: list[AlphaEvolve2026ImpactBoundaryIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(_issue(f"invalid_{field}", f"{field} must match the official 2026 impact source boundary"))


def _validate_article(
    article: object,
    issues: list[AlphaEvolve2026ImpactBoundaryIssue],
) -> None:
    if not isinstance(article, dict):
        issues.append(_issue("invalid_article", "article must be an object"))
        return
    expected = {
        "title": EXPECTED_ARTICLE_TITLE,
        "url": EXPECTED_ARTICLE_URL,
        "date": EXPECTED_ARTICLE_DATE,
        "author": EXPECTED_ARTICLE_AUTHOR,
        "section": EXPECTED_ARTICLE_SECTION,
    }
    for field, expected_value in expected.items():
        if article.get(field) != expected_value:
            issues.append(_issue(f"invalid_article_{field}", f"article.{field} must match the official impact article"))
    retrieval = article.get("retrieval")
    if not isinstance(retrieval, dict):
        issues.append(_issue("invalid_article_retrieval", "article.retrieval must be an object"))
        return
    expected_retrieval = {
        "retrieved_on": EXPECTED_RETRIEVED_ON,
        "html_bytes": EXPECTED_HTML_BYTES,
        "html_sha256": EXPECTED_HTML_SHA256,
        "hash_algorithm": "sha256",
    }
    for field, expected_value in expected_retrieval.items():
        if retrieval.get(field) != expected_value:
            issues.append(_issue(f"invalid_article_retrieval_{field}", f"article.retrieval.{field} must match the retrieved source snapshot"))


def _validate_outbound_links(
    value: object,
    issues: list[AlphaEvolve2026ImpactBoundaryIssue],
) -> None:
    if not isinstance(value, list) or len(value) < 9:
        issues.append(_issue("invalid_outbound_links", "outbound_links must preserve the official article link inventory subset"))
        return
    for link in value:
        if not isinstance(link, dict):
            issues.append(_issue("invalid_outbound_link", "each outbound link must be an object"))
            continue
        for field in ("link_id", "url", "category", "status"):
            if not isinstance(link.get(field), str) or not link[field]:
                issues.append(_issue(f"invalid_outbound_link_{field}", f"outbound link {field} must be a non-empty string"))
        if link.get("status") not in {
            "outbound_reference_only",
            "requires_separate_source_record",
            "requires_snapshot_inventory",
            "requires_customer_source_snapshot",
        }:
            issues.append(_issue("invalid_outbound_link_status", "outbound links must remain source-boundary references"))


def _validate_components(
    value: object,
    issues: list[AlphaEvolve2026ImpactBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = tuple(item.get("component_id") for item in value if isinstance(item, dict))
    if ids != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("component_id_mismatch", "framework_components must preserve the impact-source boundary taxonomy"))
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component must be an object"))
        elif item.get("local_status") not in {"boundary_only", "not_recorded", "not_implemented"}:
            issues.append(_issue("framework_component_overclaim", "framework components must not claim local implementation"))
    return len(value)


def _validate_claim_registry(
    value: object,
    issues: list[AlphaEvolve2026ImpactBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_claim_registry", "claim_registry must be a list"))
        return 0
    ids = tuple(item.get("claim_id") for item in value if isinstance(item, dict))
    if ids != EXPECTED_CLAIM_IDS:
        issues.append(_issue("claim_id_mismatch", "claim_registry must preserve the official impact claim taxonomy"))
    expected_values = {
        "deepconsensus_variant_error_reduction": (30, "percent_error_reduction"),
        "ac_opf_feasibility_improvement": ("14_to_over_88", "percent_feasible_solutions"),
        "earth_ai_disaster_risk_accuracy_gain": (5, "percent_accuracy_gain"),
        "willow_quantum_circuit_error_reduction": (10, "x_lower_error"),
        "spanner_write_amplification_reduction": (20, "percent_write_amplification_reduction"),
        "compiler_storage_footprint_reduction": (9, "nearly_percent_storage_footprint_reduction"),
        "fm_logistic_routing_efficiency": (10.4, "percent_routing_efficiency_improvement"),
        "wpp_accuracy_gain": (10, "percent_accuracy_gain"),
        "schrodinger_mlff_speedup": (4, "roughly_x_training_and_inference_speedup"),
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_claim", "each impact claim must be an object"))
            continue
        claim_id = item.get("claim_id")
        if item.get("local_benchmark_supported") is not False:
            issues.append(_issue("claim_local_benchmark_overclaim", "impact claims must not claim local benchmark support"))
        if claim_id in expected_values:
            expected_value, expected_unit = expected_values[claim_id]
            if item.get("value") != expected_value:
                issues.append(_issue(f"claim_value_mismatch_{claim_id}", "impact claim value drifted from the official article boundary"))
            if item.get("unit") != expected_unit:
                issues.append(_issue(f"claim_unit_mismatch_{claim_id}", "impact claim unit drifted from the official article boundary"))
    return len(value)


def _validate_customer_cases(
    value: object,
    issues: list[AlphaEvolve2026ImpactBoundaryIssue],
) -> None:
    expected = ("Klarna", "Substrate", "FM Logistic", "WPP", "Schrodinger")
    if not isinstance(value, list):
        issues.append(_issue("invalid_customer_cases", "customer_cases must be a list"))
        return
    customers = tuple(item.get("customer") for item in value if isinstance(item, dict))
    if customers != expected:
        issues.append(_issue("customer_case_mismatch", "customer_cases must preserve the article customer list"))
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_customer_case", "customer cases must be objects"))
        elif item.get("local_evidence") is not False:
            issues.append(_issue("customer_case_overclaim", "customer cases must remain unsupported by local evidence"))


def _validate_attribution(
    value: object,
    issues: list[AlphaEvolve2026ImpactBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_attribution", "attribution must be an object"))
        return
    for field in (
        "initial_development_team_recorded",
        "scaling_impact_contributors_recorded",
        "ui_contributors_recorded",
        "api_cloud_contributors_recorded",
        "collaborator_application_names_recorded",
    ):
        if value.get(field) is not True:
            issues.append(_issue(f"invalid_attribution_{field}", f"attribution.{field} must be true"))
    if value.get("local_role_artifact_links_ready") is not False:
        issues.append(_issue("attribution_artifact_overclaim", "local attribution artifact links are not ready"))


def _validate_local_evidence(
    value: object,
    issues: list[AlphaEvolve2026ImpactBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    for field, field_value in value.items():
        if field_value is not False:
            issues.append(_issue(f"local_evidence_{field}_overclaim", f"local_evidence.{field} must remain false"))


def _validate_required_evidence(
    value: object,
    issues: list[AlphaEvolve2026ImpactBoundaryIssue],
) -> int:
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list of strings"))
        return 0
    if tuple(value) != EXPECTED_REQUIRED_EVIDENCE_FIELDS:
        issues.append(_issue("required_evidence_fields_mismatch", "required_evidence_fields must preserve the impact-source evidence contract"))
    return len(value)


def _validate_missing_evidence(
    value: object,
    issues: list[AlphaEvolve2026ImpactBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if value != EXPECTED_MISSING_EVIDENCE:
        issues.append(_issue("missing_evidence_mismatch", "missing_evidence must preserve unsupported local benchmark flags"))
    return len(value)


def _issue(code: str, message: str) -> AlphaEvolve2026ImpactBoundaryIssue:
    return AlphaEvolve2026ImpactBoundaryIssue(code, message)
