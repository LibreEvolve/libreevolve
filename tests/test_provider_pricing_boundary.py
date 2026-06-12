from libreevolve.problems.benchmarks.provider_pricing_boundary import (
    PROVIDER_PRICING_BOUNDARY_SCHEMA,
    provider_pricing_boundary_record,
    render_provider_pricing_boundary_summary,
    validate_provider_pricing_boundary,
)


def test_provider_pricing_boundary_accepts_configured_cost_boundary():
    boundary = provider_pricing_boundary_record()

    validation = validate_provider_pricing_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "configured_cost_estimates_without_live_provider_pricing"
    )
    assert validation.required_evidence_field_count == 17
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == PROVIDER_PRICING_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim live provider pricing" in boundary["claim_boundary"]


def test_provider_pricing_boundary_rejects_live_pricing_overclaim():
    boundary = provider_pricing_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "live_provider_pricing_ready"
    boundary["missing_evidence"]["live_provider_pricing"] = "recorded"
    boundary["required_evidence_fields"] = ["backend_cost_usd_per_million_tokens"]

    validation = validate_provider_pricing_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_live_provider_pricing" in codes
    assert "missing_required_evidence_field" in codes


def test_render_provider_pricing_boundary_summary_reports_shape():
    summary = render_provider_pricing_boundary_summary(
        provider_pricing_boundary_record()
    )

    assert "Provider pricing boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | configured_cost_estimates_without_live_provider_pricing |"
        in summary
    )
    assert "| required_evidence_field_count | 17 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
