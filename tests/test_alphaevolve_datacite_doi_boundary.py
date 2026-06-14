from libreevolve.problems.benchmarks.alphaevolve_datacite_doi_boundary import (
    ALPHAEVOLVE_DATACITE_DOI_BOUNDARY_SCHEMA,
    alphaevolve_datacite_doi_boundary_record,
    render_alphaevolve_datacite_doi_boundary_summary,
    validate_alphaevolve_datacite_doi_boundary,
)


def test_alphaevolve_datacite_doi_boundary_accepts_snapshot_record():
    boundary = alphaevolve_datacite_doi_boundary_record()

    validation = validate_alphaevolve_datacite_doi_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "datacite_api_snapshot_without_full_source_refresh_gate"
    )
    assert validation.required_evidence_field_count == 21
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == ALPHAEVOLVE_DATACITE_DOI_BOUNDARY_SCHEMA
    assert boundary["datacite_api_snapshot"]["doi"] == "10.48550/arxiv.2506.13131"
    assert boundary["datacite_api_snapshot"]["creator_count"] == 18


def test_alphaevolve_datacite_doi_boundary_rejects_refresh_overclaim():
    boundary = alphaevolve_datacite_doi_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_source_refresh_gate_ready"
    boundary["missing_evidence"]["datacite_refresh_gate"] = "recorded"
    boundary["datacite_api_snapshot"]["response_sha256"] = "0" * 64

    validation = validate_alphaevolve_datacite_doi_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_snapshot_response_sha256" in codes
    assert "invalid_missing_evidence_datacite_refresh_gate" in codes


def test_render_alphaevolve_datacite_doi_boundary_summary_reports_shape():
    summary = render_alphaevolve_datacite_doi_boundary_summary(
        alphaevolve_datacite_doi_boundary_record()
    )

    assert "AlphaEvolve DataCite DOI boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | datacite_api_snapshot_without_full_source_refresh_gate |"
        in summary
    )
    assert "| required_evidence_field_count | 21 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
