from libreevolve.problems.benchmarks.sums_differences_sequence_boundary import (
    SUMS_DIFFERENCES_SEQUENCE_BOUNDARY_SCHEMA,
    render_sums_differences_sequence_boundary_summary,
    sums_differences_sequence_boundary_record,
    validate_sums_differences_sequence_boundary,
)


def test_sums_differences_sequence_boundary_accepts_absence_record():
    boundary = sums_differences_sequence_boundary_record()

    validation = validate_sums_differences_sequence_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "post_alphaevolve_sums_differences_sequence_without_local_asymptotic_verifier"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == SUMS_DIFFERENCES_SEQUENCE_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v1"
    assert boundary["source_license"] == "CC BY 4.0"
    assert boundary["source_pdf_date"] == "2025-06-11"
    assert boundary["local_evidence"]["theta0_recomputation_ready"] is False
    assert boundary["reported_result"]["paper_bound"] == 1.173077
    assert boundary["reported_result"]["winning_b"] == 5
    assert (
        boundary["reported_result"]["winning_theta_minus_one"][
            "epsilon_1e_minus_10"
        ]
        == 0.173077279785136
    )
    assert "does not claim a sequence-of-U construction schema" in (
        boundary["claim_boundary"]
    )


def test_sums_differences_sequence_boundary_rejects_premature_runtime_claims():
    boundary = sums_differences_sequence_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][0]["status"] = "verified_local_snapshot"
    boundary["framework_components"][0]["local_status"] = "implemented"
    boundary["local_evidence"]["theta0_recomputation_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["reported_result"]["paper_bound"] = 1.18
    boundary["reported_result"]["restricted_b_values"] = [5]
    boundary["missing_evidence"]["theta0_recomputation"] = "implemented"

    validation = validate_sums_differences_sequence_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_theta0_recomputation_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "reported_result_paper_bound_mismatch" in codes
    assert "reported_result_restricted_b_values_mismatch" in codes
    assert "missing_evidence_mismatch" in codes


def test_render_sums_differences_sequence_boundary_summary_reports_shape():
    summary = render_sums_differences_sequence_boundary_summary(
        sums_differences_sequence_boundary_record()
    )

    assert "Sums and Differences II boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | post_alphaevolve_sums_differences_sequence_without_local_asymptotic_verifier |"
        in summary
    )
    assert "| component_count | 14 |" in summary
