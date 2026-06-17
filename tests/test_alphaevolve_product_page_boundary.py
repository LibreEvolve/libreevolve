from libreevolve.problems.benchmarks.alphaevolve_product_page_boundary import (
    ALPHAEVOLVE_PRODUCT_PAGE_BOUNDARY_SCHEMA,
    alphaevolve_product_page_boundary_record,
    render_alphaevolve_product_page_boundary_summary,
    validate_alphaevolve_product_page_boundary,
)


def test_alphaevolve_product_page_boundary_accepts_current_404_scope():
    boundary = alphaevolve_product_page_boundary_record()

    validation = validate_alphaevolve_product_page_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "outbound_deepmind_product_page_reference_currently_unavailable_without_snapshot"
    )
    assert validation.http_status == 404
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 10
    assert boundary["schema"] == ALPHAEVOLVE_PRODUCT_PAGE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["retrieval"]["url"] == "https://deepmind.google/science/alphaevolve/"
    assert "does not claim a reachable product-page HTML snapshot" in boundary["claim_boundary"]


def test_alphaevolve_product_page_boundary_rejects_availability_overclaim():
    boundary = alphaevolve_product_page_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "product_page_snapshot_ready"
    boundary["retrieval"]["http_status"] = 200
    boundary["retrieval"]["html_bytes"] = 123
    boundary["missing_evidence"]["reachable_product_page_snapshot"] = "recorded"
    boundary["required_evidence_fields"] = ["canonical_url"]

    validation = validate_alphaevolve_product_page_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_http_status" in codes
    assert "invalid_unavailable_html_fields" in codes
    assert "invalid_missing_evidence_reachable_product_page_snapshot" in codes
    assert "missing_required_evidence_field" in codes


def test_render_alphaevolve_product_page_boundary_summary_reports_shape():
    summary = render_alphaevolve_product_page_boundary_summary(
        alphaevolve_product_page_boundary_record()
    )

    assert "AlphaEvolve product page boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| http_status | 404 |" in summary
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 10 |" in summary
