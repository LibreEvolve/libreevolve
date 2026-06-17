from libreevolve.problems.benchmarks.alphaevolve_cloud_access_boundary import (
    ALPHAEVOLVE_CLOUD_ACCESS_BOUNDARY_SCHEMA,
    alphaevolve_cloud_access_boundary_record,
    render_alphaevolve_cloud_access_boundary_summary,
    validate_alphaevolve_cloud_access_boundary,
)


def test_alphaevolve_cloud_access_boundary_accepts_official_source_boundary():
    boundary = alphaevolve_cloud_access_boundary_record()

    validation = validate_alphaevolve_cloud_access_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "official_google_cloud_sources_without_local_service_access_or_managed_agent_evidence"
    )
    assert validation.source_count == 3
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 13
    assert boundary["schema"] == ALPHAEVOLVE_CLOUD_ACCESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "AlphaEvolve Service API" in boundary["claim_boundary"]
    assert "local Cloud AlphaEvolve provider adapter" in boundary["claim_boundary"]


def test_alphaevolve_cloud_access_boundary_rejects_service_access_overclaim():
    boundary = alphaevolve_cloud_access_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "cloud_service_access_ready"
    boundary["missing_evidence"]["libreevolve_cloud_provider_adapter"] = "implemented"
    boundary["required_evidence_fields"] = ["cloud_blog_url"]
    del boundary["source_claims"]["service_api_access_model"]
    boundary["sources"][0]["source_id"] = "untracked-source"

    validation = validate_alphaevolve_cloud_access_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_libreevolve_cloud_provider_adapter" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_source_claim_service_api_access_model" in codes
    assert "invalid_source_ids" in codes


def test_render_alphaevolve_cloud_access_boundary_summary_reports_shape():
    summary = render_alphaevolve_cloud_access_boundary_summary(
        alphaevolve_cloud_access_boundary_record()
    )

    assert "AlphaEvolve cloud access boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| source_count | 3 |" in summary
    assert "| required_evidence_field_count | 24 |" in summary
    assert "| missing_evidence_count | 13 |" in summary
