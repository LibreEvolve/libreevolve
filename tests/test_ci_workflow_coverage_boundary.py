from libreevolve.problems.benchmarks.ci_workflow_coverage_boundary import (
    CI_WORKFLOW_COVERAGE_BOUNDARY_SCHEMA,
    ci_workflow_coverage_boundary_record,
    render_ci_workflow_coverage_boundary_summary,
    validate_ci_workflow_coverage_boundary,
)


def test_ci_workflow_coverage_boundary_accepts_path_scoped_boundary():
    boundary = ci_workflow_coverage_boundary_record()

    validation = validate_ci_workflow_coverage_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "path_scoped_ubuntu_workflow_only"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == CI_WORKFLOW_COVERAGE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "committed-manifest paper/docs job" in boundary["claim_boundary"]
    assert boundary["partial_evidence"]["wheel_sdist_ci_smoke"] == (
        "release_artifact_job_with_bundled_example_inventory"
    )
    assert (
        boundary["missing_evidence"]["paper_manifest_ci_job"]
        == "committed_manifest_only_no_local_pdf_cache"
    )


def test_ci_workflow_coverage_boundary_rejects_full_ci_overclaim():
    boundary = ci_workflow_coverage_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_alphaevolve_ci_ready"
    boundary["missing_evidence"]["cross_platform_ci_matrix"] = "recorded"
    boundary["required_evidence_fields"] = ["workflow_dispatch_trigger"]

    validation = validate_ci_workflow_coverage_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_cross_platform_ci_matrix" in codes
    assert "missing_required_evidence_field" in codes


def test_render_ci_workflow_coverage_boundary_summary_reports_shape():
    summary = render_ci_workflow_coverage_boundary_summary(
        ci_workflow_coverage_boundary_record()
    )

    assert "CI workflow coverage boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | path_scoped_ubuntu_workflow_only |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
