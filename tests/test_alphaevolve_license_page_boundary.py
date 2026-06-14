from libreevolve.problems.benchmarks.alphaevolve_license_page_boundary import (
    ALPHAEVOLVE_LICENSE_PAGE_BOUNDARY_SCHEMA,
    alphaevolve_license_page_boundary_record,
    render_alphaevolve_license_page_boundary_summary,
    validate_alphaevolve_license_page_boundary,
)


def test_alphaevolve_license_page_boundary_accepts_digest_record():
    boundary = alphaevolve_license_page_boundary_record()

    validation = validate_alphaevolve_license_page_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "license_page_digest_with_retained_html_without_refresh_gate"
    )
    assert validation.required_evidence_field_count == 13
    assert validation.missing_evidence_count == 1
    assert boundary["schema"] == ALPHAEVOLVE_LICENSE_PAGE_BOUNDARY_SCHEMA
    assert boundary["license_page_snapshot"]["response_bytes"] == 36988
    assert boundary["license_page_snapshot"]["license_family"] == "CC BY-NC-ND"


def test_alphaevolve_license_page_boundary_rejects_license_overclaim():
    boundary = alphaevolve_license_page_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "license_page_full_refresh_gate_ready"
    boundary["license_page_snapshot"]["response_sha256"] = "0" * 64
    boundary["missing_evidence"]["license_page_refresh_gate"] = "recorded"

    validation = validate_alphaevolve_license_page_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_snapshot_response_sha256" in codes
    assert "invalid_missing_evidence_license_page_refresh_gate" in codes


def test_render_alphaevolve_license_page_boundary_summary_reports_shape():
    summary = render_alphaevolve_license_page_boundary_summary(
        alphaevolve_license_page_boundary_record()
    )

    assert "AlphaEvolve license page boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | license_page_digest_with_retained_html_without_refresh_gate |"
        in summary
    )
    assert "| required_evidence_field_count | 13 |" in summary
    assert "| missing_evidence_count | 1 |" in summary
