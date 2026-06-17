from libreevolve.problems.benchmarks.alphaevolve_impact_verification_matrix_boundary import (
    ALPHAEVOLVE_IMPACT_VERIFICATION_MATRIX_BOUNDARY_SCHEMA,
    alphaevolve_impact_verification_matrix_boundary_record,
    render_alphaevolve_impact_verification_matrix_boundary_summary,
    validate_alphaevolve_impact_verification_matrix_boundary,
)


def test_alphaevolve_impact_verification_matrix_accepts_absence_rows():
    boundary = alphaevolve_impact_verification_matrix_boundary_record()

    validation = validate_alphaevolve_impact_verification_matrix_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "impact_claim_and_source_matrix_without_local_benchmark_or_independent_verification"
    )
    assert validation.claim_row_count == 22
    assert validation.source_row_count == 12
    assert validation.release_note_eligible_count == 0
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == ALPHAEVOLVE_IMPACT_VERIFICATION_MATRIX_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["claim_rows"][0]["row_id"] == "claim:deepconsensus_variant_error_reduction"
    assert boundary["outbound_source_rows"][0]["row_id"] == "source:alphaevolve_product_page"


def test_alphaevolve_impact_verification_matrix_rejects_reproduction_overclaim():
    boundary = alphaevolve_impact_verification_matrix_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "impact_claims_verified"
    row = boundary["claim_rows"][0]
    row["local_benchmark_status"] = "implemented"
    row["fixture_path"] = "libreevolve/problems/examples/deepconsensus"
    row["benchmark_report_path"] = "runs/deepconsensus/report.json"
    row["benchmark_report_hash"] = "a" * 64
    row["independent_verifier"] = "external"
    row["verification_date"] = "2026-06-17"
    row["verification_outcome"] = "verified"
    row["unsupported_local_benchmark_flag"] = False
    row["release_note_eligible"] = True
    boundary["required_evidence_fields"] = ["row_id"]
    boundary["missing_evidence"]["local_benchmark_reports"] = "implemented"

    validation = validate_alphaevolve_impact_verification_matrix_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "local_benchmark_status_overclaim" in codes
    assert "fixture_path_overclaim" in codes
    assert "benchmark_report_overclaim" in codes
    assert "independent_verifier_overclaim" in codes
    assert "verification_date_overclaim" in codes
    assert "verification_outcome_overclaim" in codes
    assert "missing_unsupported_local_benchmark_flag" in codes
    assert "release_note_eligibility_overclaim" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_missing_evidence_local_benchmark_reports" in codes


def test_render_alphaevolve_impact_verification_matrix_summary_reports_shape():
    summary = render_alphaevolve_impact_verification_matrix_boundary_summary(
        alphaevolve_impact_verification_matrix_boundary_record()
    )

    assert "AlphaEvolve impact verification matrix boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| claim_row_count | 22 |" in summary
    assert "| source_row_count | 12 |" in summary
    assert "| release_note_eligible_count | 0 |" in summary
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
