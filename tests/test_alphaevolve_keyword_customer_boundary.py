from libreevolve.problems.benchmarks.alphaevolve_keyword_customer_boundary import (
    ALPHAEVOLVE_KEYWORD_CUSTOMER_BOUNDARY_SCHEMA,
    alphaevolve_keyword_customer_boundary_record,
    render_alphaevolve_keyword_customer_boundary_summary,
    validate_alphaevolve_keyword_customer_boundary,
)


def test_alphaevolve_keyword_customer_boundary_accepts_source_scope():
    boundary = alphaevolve_keyword_customer_boundary_record()

    validation = validate_alphaevolve_keyword_customer_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "official_keyword_update_without_customer_availability_or_local_product_evidence"
    )
    assert validation.domain_claim_count == 10
    assert validation.customer_availability_row_count == 4
    assert validation.required_evidence_field_count == 21
    assert validation.missing_evidence_count == 11
    assert boundary["schema"] == ALPHAEVOLVE_KEYWORD_CUSTOMER_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "customer source crosswalks" in boundary["claim_boundary"]
    assert "local managed AlphaEvolve service support" in boundary["claim_boundary"]


def test_alphaevolve_keyword_customer_boundary_rejects_availability_overclaim():
    boundary = alphaevolve_keyword_customer_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "customer_availability_verified"
    boundary["missing_evidence"]["customer_source_crosswalk"] = "recorded"
    boundary["required_evidence_fields"] = ["keyword_article_url"]
    boundary["domain_claims"][0]["claim_id"] = "untracked_claim"
    boundary["customer_availability_rows"][0]["availability_status"] = "verified"

    validation = validate_alphaevolve_keyword_customer_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_customer_source_crosswalk" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_domain_claim_ids" in codes
    assert "invalid_customer_availability_status" in codes


def test_render_alphaevolve_keyword_customer_boundary_summary_reports_shape():
    summary = render_alphaevolve_keyword_customer_boundary_summary(
        alphaevolve_keyword_customer_boundary_record()
    )

    assert "AlphaEvolve Keyword customer boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| domain_claim_count | 10 |" in summary
    assert "| customer_availability_row_count | 4 |" in summary
    assert "| required_evidence_field_count | 21 |" in summary
    assert "| missing_evidence_count | 11 |" in summary
