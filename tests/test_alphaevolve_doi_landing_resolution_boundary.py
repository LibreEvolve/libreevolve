from libreevolve.problems.benchmarks.alphaevolve_doi_landing_resolution_boundary import (
    ALPHAEVOLVE_DOI_LANDING_RESOLUTION_BOUNDARY_SCHEMA,
    alphaevolve_doi_landing_resolution_boundary_record,
    render_alphaevolve_doi_landing_resolution_boundary_summary,
    validate_alphaevolve_doi_landing_resolution_boundary,
)


def test_alphaevolve_doi_landing_resolution_boundary_accepts_redirect_record():
    boundary = alphaevolve_doi_landing_resolution_boundary_record()

    validation = validate_alphaevolve_doi_landing_resolution_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "doi_redirect_headers_without_body_retention_or_refresh_gate"
    )
    assert validation.redirect_status == 302
    assert validation.final_status == 200
    assert validation.required_evidence_field_count == 15
    assert validation.missing_evidence_count == 3
    assert boundary["schema"] == ALPHAEVOLVE_DOI_LANDING_RESOLUTION_BOUNDARY_SCHEMA
    assert boundary["doi_redirect"]["location"] == "https://arxiv.org/abs/2506.13131"
    assert boundary["final_landing"]["response_bytes"] == 49939


def test_alphaevolve_doi_landing_resolution_boundary_rejects_refresh_overclaim():
    boundary = alphaevolve_doi_landing_resolution_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "doi_resolution_refresh_gate_ready"
    boundary["doi_redirect"]["location"] = "https://example.invalid/"
    boundary["missing_evidence"]["automated_doi_resolution_refresh_gate"] = "recorded"

    validation = validate_alphaevolve_doi_landing_resolution_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_doi_redirect_location" in codes
    assert "invalid_missing_evidence_automated_doi_resolution_refresh_gate" in codes


def test_render_alphaevolve_doi_landing_resolution_boundary_summary_reports_shape():
    summary = render_alphaevolve_doi_landing_resolution_boundary_summary(
        alphaevolve_doi_landing_resolution_boundary_record()
    )

    assert "AlphaEvolve DOI landing-resolution boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | doi_redirect_headers_without_body_retention_or_refresh_gate |"
        in summary
    )
    assert "| redirect_status | 302 |" in summary
    assert "| final_status | 200 |" in summary
