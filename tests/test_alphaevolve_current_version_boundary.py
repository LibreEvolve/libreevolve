from libreevolve.problems.benchmarks.alphaevolve_current_version_boundary import (
    ALPHAEVOLVE_CURRENT_VERSION_BOUNDARY_SCHEMA,
    alphaevolve_current_version_boundary_record,
    render_alphaevolve_current_version_boundary_summary,
    validate_alphaevolve_current_version_boundary,
)


def test_alphaevolve_current_version_boundary_accepts_digest_record():
    boundary = alphaevolve_current_version_boundary_record()

    validation = validate_alphaevolve_current_version_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "current_v1_and_floating_pdf_digest_without_refresh_gate"
    )
    assert validation.required_evidence_field_count == 22
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == ALPHAEVOLVE_CURRENT_VERSION_BOUNDARY_SCHEMA
    assert boundary["current_abs_snapshot"]["resolved_current_version"] == 1
    assert boundary["floating_pdf_snapshot"]["floating_pdf_matches_cached_pdf"] is True


def test_alphaevolve_current_version_boundary_rejects_refresh_overclaim():
    boundary = alphaevolve_current_version_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "current_version_refresh_gate_ready"
    boundary["current_abs_snapshot"]["resolved_current_version"] = 2
    boundary["floating_pdf_snapshot"]["floating_pdf_matches_cached_pdf"] = False
    boundary["missing_evidence"]["automated_current_version_refresh_gate"] = "recorded"

    validation = validate_alphaevolve_current_version_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_current_abs_resolved_current_version" in codes
    assert "invalid_floating_pdf_floating_pdf_matches_cached_pdf" in codes
    assert "invalid_missing_evidence_automated_current_version_refresh_gate" in codes


def test_render_alphaevolve_current_version_boundary_summary_reports_shape():
    summary = render_alphaevolve_current_version_boundary_summary(
        alphaevolve_current_version_boundary_record()
    )

    assert "AlphaEvolve current-version boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | current_v1_and_floating_pdf_digest_without_refresh_gate |"
        in summary
    )
    assert "| required_evidence_field_count | 22 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
