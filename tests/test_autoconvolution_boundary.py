from libreevolve.problems.benchmarks.autoconvolution_boundary import (
    AUTOCONVOLUTION_BOUNDARY_SCHEMA,
    autoconvolution_boundary_record,
    render_autoconvolution_boundary_summary,
    validate_autoconvolution_boundary,
)


def test_autoconvolution_boundary_accepts_absence_record():
    boundary = autoconvolution_boundary_record()

    validation = validate_autoconvolution_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "post_alphaevolve_autoconvolution_context_without_local_witness_verifier"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == AUTOCONVOLUTION_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v2"
    assert boundary["source_last_revised_date"] == "2025-08-10"
    assert boundary["local_evidence"]["formula3_checker_ready"] is False
    assert boundary["reported_result"]["interval_count"] == 575
    assert boundary["reported_result"]["lower_bound_decimal"] == 0.901564
    assert "does not claim a 575-interval witness schema" in (
        boundary["claim_boundary"]
    )


def test_autoconvolution_boundary_rejects_premature_runtime_claims():
    boundary = autoconvolution_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][1]["status"] = "verified_local_snapshot"
    boundary["framework_components"][2]["local_status"] = "implemented"
    boundary["local_evidence"]["formula3_checker_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["reported_result"]["interval_count"] = 574
    boundary["reported_result"]["public_artifacts"].pop()
    boundary["missing_evidence"]["formula_3_checker"] = "implemented"

    validation = validate_autoconvolution_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_formula3_checker_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "reported_result_interval_count_mismatch" in codes
    assert "reported_result_public_artifacts_mismatch" in codes
    assert "missing_evidence_mismatch" in codes


def test_render_autoconvolution_boundary_summary_reports_shape():
    summary = render_autoconvolution_boundary_summary(autoconvolution_boundary_record())

    assert "Autoconvolution boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | post_alphaevolve_autoconvolution_context_without_local_witness_verifier |"
        in summary
    )
    assert "| component_count | 14 |" in summary
