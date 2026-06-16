from libreevolve.problems.benchmarks.readme_install_smoke_boundary import (
    README_INSTALL_SMOKE_BOUNDARY_SCHEMA,
    readme_install_smoke_boundary_record,
    render_readme_install_smoke_boundary_summary,
    validate_readme_install_smoke_boundary,
)


def test_readme_install_smoke_boundary_accepts_current_markers():
    boundary = readme_install_smoke_boundary_record()

    validation = validate_readme_install_smoke_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_editable_install_ci_markers_without_clean_transcript"
    )
    assert boundary["schema"] == README_INSTALL_SMOKE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_install_command"] == 'py -3.12 -m pip install -e ".[dev]"'
    assert boundary["ci_install_command"] == 'python -m pip install -e ".[dev]"'
    assert validation.ci_install_marker_count >= 1
    assert validation.missing_marker_count == 0
    assert boundary["missing_marker_records"] == []
    assert boundary["install_marker_status"] == "readme_install_markers_present"
    assert boundary["missing_evidence"] == {
        "clean_environment_install_transcript": "not_recorded_locally",
        "python_pip_version_record": "not_recorded_locally",
        "dev_dependency_import_smoke": "not_recorded_locally",
        "install_failure_classification": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "README editable-install command" in boundary["claim_boundary"]


def test_readme_install_smoke_boundary_rejects_overclaim_and_missing_marker():
    boundary = readme_install_smoke_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_clean_install_transcript_ready"
    boundary["ci_install_marker_count"] = 0
    boundary["missing_marker_count"] = 1
    boundary["missing_marker_records"] = [boundary["marker_records"][0]]
    boundary["marker_records"][0]["marker_status"] = "marker_missing"
    boundary["install_marker_status"] = "readme_install_markers_incomplete"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_editable_install_command"]

    validation = validate_readme_install_smoke_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_ci_install_marker_count" in codes
    assert "invalid_missing_marker_count" in codes
    assert "invalid_missing_marker_records" in codes
    assert "invalid_marker_records" in codes
    assert "missing_ci_install_marker" in codes
    assert "missing_install_marker" in codes
    assert "invalid_install_marker_status" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_install_smoke_boundary_summary_reports_shape():
    summary = render_readme_install_smoke_boundary_summary(
        readme_install_smoke_boundary_record()
    )

    assert "README install smoke boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_editable_install_ci_markers_without_clean_transcript |"
        in summary
    )
    assert "| missing_marker_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
