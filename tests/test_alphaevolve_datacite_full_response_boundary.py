from libreevolve.problems.benchmarks.alphaevolve_datacite_full_response_boundary import (
    ALPHAEVOLVE_DATACITE_FULL_RESPONSE_BOUNDARY_SCHEMA,
    alphaevolve_datacite_full_response_boundary_record,
    render_alphaevolve_datacite_full_response_boundary_summary,
    validate_alphaevolve_datacite_full_response_boundary,
)


def test_alphaevolve_datacite_full_response_boundary_accepts_raw_body_record():
    boundary = alphaevolve_datacite_full_response_boundary_record()

    validation = validate_alphaevolve_datacite_full_response_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "full_datacite_response_body_retained_without_refresh_gate"
    )
    assert validation.response_bytes == 15905
    assert validation.required_evidence_field_count == 15
    assert validation.missing_evidence_count == 2
    assert boundary["schema"] == ALPHAEVOLVE_DATACITE_FULL_RESPONSE_BOUNDARY_SCHEMA
    assert boundary["parsed_response_summary"]["doi"] == "10.48550/arxiv.2506.13131"
    assert boundary["parsed_response_summary"]["creator_count"] == 18


def test_alphaevolve_datacite_full_response_boundary_rejects_refresh_overclaim():
    boundary = alphaevolve_datacite_full_response_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "datacite_refresh_gate_ready"
    boundary["raw_response_body"] = "{}"
    boundary["missing_evidence"]["automated_datacite_refresh_gate"] = "recorded"

    validation = validate_alphaevolve_datacite_full_response_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_raw_response_body_bytes" in codes
    assert "invalid_raw_response_body_sha256" in codes
    assert "invalid_raw_response_shape" in codes
    assert "invalid_missing_evidence_automated_datacite_refresh_gate" in codes


def test_render_alphaevolve_datacite_full_response_boundary_summary_reports_shape():
    summary = render_alphaevolve_datacite_full_response_boundary_summary(
        alphaevolve_datacite_full_response_boundary_record()
    )

    assert "AlphaEvolve DataCite full-response boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | full_datacite_response_body_retained_without_refresh_gate |"
        in summary
    )
    assert "| response_bytes | 15905 |" in summary
    assert "| missing_evidence_count | 2 |" in summary
