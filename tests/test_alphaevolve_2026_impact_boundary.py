from libreevolve.problems.benchmarks.alphaevolve_2026_impact_boundary import (
    ALPHAEVOLVE_2026_IMPACT_BOUNDARY_SCHEMA,
    alphaevolve_2026_impact_boundary_record,
    render_alphaevolve_2026_impact_boundary_summary,
    validate_alphaevolve_2026_impact_boundary,
)


def test_alphaevolve_2026_impact_boundary_accepts_builtin_record():
    boundary = alphaevolve_2026_impact_boundary_record()

    validation = validate_alphaevolve_2026_impact_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "official_2026_impact_article_without_local_deployment_benchmarks"
    )
    assert validation.component_count == 12
    assert validation.claim_count == 22
    assert validation.required_evidence_field_count == 30
    assert validation.missing_evidence_count == 24
    assert boundary["schema"] == ALPHAEVOLVE_2026_IMPACT_BOUNDARY_SCHEMA
    assert boundary["article"]["date"] == "2026-05-07"
    assert boundary["article"]["retrieval"]["html_bytes"] == 156554
    assert boundary["article"]["retrieval"]["html_sha256"] == (
        "2b56730407c01a316325222beda6c9c45727362505005c81a3bbc40bc5c4c97d"
    )
    assert boundary["claim_ready"] is False
    assert boundary["local_evidence"]["spanner_fixture_ready"] is False
    assert boundary["customer_cases"][0]["customer"] == "Klarna"
    assert boundary["customer_cases"][-1]["customer"] == "Schrodinger"


def test_alphaevolve_2026_impact_boundary_rejects_overclaims_and_metric_drift():
    boundary = alphaevolve_2026_impact_boundary_record()
    boundary["claim_ready"] = True
    boundary["article"]["retrieval"]["html_sha256"] = "0" * 64
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["claim_registry"][0]["value"] = 29
    boundary["claim_registry"][0]["local_benchmark_supported"] = True
    boundary["customer_cases"][0]["local_evidence"] = True
    boundary["attribution"]["local_role_artifact_links_ready"] = True
    boundary["local_evidence"]["spanner_fixture_ready"] = True
    boundary["missing_evidence"]["spanner_lsm_compaction_fixture"] = "implemented_locally"
    boundary["claim_boundary"] = "LibreEvolve implements these workflows."

    validation = validate_alphaevolve_2026_impact_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_article_retrieval_html_sha256" in codes
    assert "framework_component_overclaim" in codes
    assert "claim_value_mismatch_deepconsensus_variant_error_reduction" in codes
    assert "claim_local_benchmark_overclaim" in codes
    assert "customer_case_overclaim" in codes
    assert "attribution_artifact_overclaim" in codes
    assert "local_evidence_spanner_fixture_ready_overclaim" in codes
    assert "missing_evidence_mismatch" in codes
    assert "invalid_claim_boundary" in codes


def test_alphaevolve_2026_impact_boundary_rejects_claim_taxonomy_drift():
    boundary = alphaevolve_2026_impact_boundary_record()
    boundary["claim_registry"].pop()
    boundary["framework_components"].pop()
    boundary["outbound_links"][0]["status"] = "verified_supported_locally"

    validation = validate_alphaevolve_2026_impact_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_id_mismatch" in codes
    assert "component_id_mismatch" in codes
    assert "invalid_outbound_link_status" in codes


def test_render_alphaevolve_2026_impact_boundary_summary_reports_shape():
    summary = render_alphaevolve_2026_impact_boundary_summary(
        alphaevolve_2026_impact_boundary_record()
    )

    assert "AlphaEvolve 2026 impact boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | official_2026_impact_article_without_local_deployment_benchmarks |"
        in summary
    )
    assert "| claim_count | 22 |" in summary
