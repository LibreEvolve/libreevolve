from libreevolve.problems.benchmarks.alphaevolve_raw_http_headers_boundary import (
    ALPHAEVOLVE_RAW_HTTP_HEADERS_BOUNDARY_SCHEMA,
    alphaevolve_raw_http_headers_boundary_record,
    render_alphaevolve_raw_http_headers_boundary_summary,
    validate_alphaevolve_raw_http_headers_boundary,
)


def test_alphaevolve_raw_http_headers_boundary_accepts_header_record():
    boundary = alphaevolve_raw_http_headers_boundary_record()

    validation = validate_alphaevolve_raw_http_headers_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "raw_http_headers_recorded_without_full_response_retention_or_refresh_gate"
    )
    assert validation.response_count == 6
    assert validation.required_evidence_field_count == 13
    assert validation.missing_evidence_count == 3
    assert boundary["schema"] == ALPHAEVOLVE_RAW_HTTP_HEADERS_BOUNDARY_SCHEMA
    assert (
        boundary["header_snapshots"]["floating_pdf"]["response_sha256"]
        == "f092c8cbd65da89951ee6496374da9a54963f9035758c25ac6e4625f506df9ad"
    )
    assert "content-type: application/pdf" in boundary["header_snapshots"]["floating_pdf"]["raw_header_lines"]


def test_alphaevolve_raw_http_headers_boundary_rejects_refresh_overclaim():
    boundary = alphaevolve_raw_http_headers_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "raw_http_headers_refresh_gate_ready"
    boundary["header_snapshots"]["datacite_api"]["raw_header_lines"] = []
    boundary["missing_evidence"]["automated_header_refresh_gate"] = "recorded"

    validation = validate_alphaevolve_raw_http_headers_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_datacite_api_raw_header_lines" in codes
    assert "invalid_missing_evidence_automated_header_refresh_gate" in codes


def test_render_alphaevolve_raw_http_headers_boundary_summary_reports_shape():
    summary = render_alphaevolve_raw_http_headers_boundary_summary(
        alphaevolve_raw_http_headers_boundary_record()
    )

    assert "AlphaEvolve raw HTTP headers boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | raw_http_headers_recorded_without_full_response_retention_or_refresh_gate |"
        in summary
    )
    assert "| response_count | 6 |" in summary
    assert "| missing_evidence_count | 3 |" in summary
