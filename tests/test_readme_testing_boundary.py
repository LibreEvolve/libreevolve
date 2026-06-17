from libreevolve.problems.benchmarks.readme_testing_boundary import (
    README_TESTING_BOUNDARY_SCHEMA,
    readme_testing_boundary_record,
    render_readme_testing_boundary_summary,
    validate_readme_testing_boundary,
)


def test_readme_testing_boundary_accepts_current_command_map():
    boundary = readme_testing_boundary_record()

    validation = validate_readme_testing_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_testing_commands_structural_map_without_selection_transcript"
    )
    assert boundary["schema"] == README_TESTING_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["readme_path"] == "README.md"
    assert boundary["pytest_config_path"] == "pyproject.toml"
    assert boundary["workflow_path"] == ".github/workflows/tests.yml"
    assert boundary["integration_test_path"] == "tests/integration/test_hello_world.py"
    assert validation.readme_marker_count == 5
    assert validation.missing_readme_marker_count == 0
    assert boundary["missing_readme_marker_records"] == []
    assert boundary["command_record_count"] == 4
    assert {
        record["command_id"]: record["command_status"]
        for record in boundary["command_records"]
    } == {
        "readme_non_integration": "command_present",
        "readme_integration": "command_present",
        "ci_non_integration": "command_present",
        "ci_integration": "command_present",
    }
    assert boundary["pytest_config_record"] == {
        "path": "pyproject.toml",
        "testpaths": ["tests"],
        "markers": ["integration: marks tests requiring API keys"],
        "integration_marker_registered": True,
        "config_status": "pytest_config_recorded",
    }
    assert validation.pytest_marker_count == 1
    assert validation.integration_test_marker_count == 2
    assert validation.credential_skip_marker_count == 2
    assert validation.evidence_anchor_count == 11
    assert validation.missing_evidence_anchor_count == 0
    assert boundary["missing_evidence_anchor_records"] == []
    assert (
        boundary["readme_testing_map_status"]
        == "readme_testing_structural_map_present"
    )
    assert boundary["missing_evidence"] == {
        "python_pytest_version_transcript": "not_recorded_locally",
        "selected_non_integration_test_count": "not_recorded_locally",
        "selected_integration_test_count": "not_recorded_locally",
        "credential_skip_transcript": "not_recorded_locally",
        "failure_attribution_matrix": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "README Testing command markers" in boundary["claim_boundary"]
    assert "does not claim Python/pytest version transcripts" in boundary["claim_boundary"]
    assert "credential-skip transcript proof" in boundary["claim_boundary"]


def test_readme_testing_boundary_rejects_overclaim_and_drift():
    boundary = readme_testing_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_testing_command_transcripts_ready"
    boundary["readme_marker_count"] = 0
    boundary["missing_readme_marker_count"] = 1
    boundary["missing_readme_marker_records"] = [boundary["readme_marker_records"][0]]
    boundary["readme_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["command_record_count"] = 0
    boundary["command_records"][0]["command_status"] = "command_missing"
    boundary["pytest_marker_count"] = 0
    boundary["pytest_config_record"]["testpaths"] = []
    boundary["integration_test_marker_count"] = 0
    boundary["credential_skip_marker_count"] = 0
    boundary["evidence_anchor_count"] = 0
    boundary["missing_evidence_anchor_count"] = 1
    boundary["missing_evidence_anchor_records"] = [
        boundary["evidence_anchor_records"][0]
    ]
    boundary["evidence_anchor_records"][0]["marker_status"] = "marker_missing"
    boundary["readme_testing_map_status"] = "readme_testing_structural_map_incomplete"
    boundary["missing_evidence"]["credential_skip_transcript"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_testing_command_markers"]

    validation = validate_readme_testing_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_count" in codes
    assert "invalid_missing_readme_marker_records" in codes
    assert "invalid_readme_marker_records" in codes
    assert "missing_readme_testing_marker" in codes
    assert "invalid_command_record_count" in codes
    assert "invalid_command_records" in codes
    assert "invalid_pytest_marker_count" in codes
    assert "invalid_pytest_config_record" in codes
    assert "invalid_integration_test_marker_count" in codes
    assert "invalid_credential_skip_marker_count" in codes
    assert "invalid_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_count" in codes
    assert "invalid_missing_evidence_anchor_records" in codes
    assert "invalid_evidence_anchor_records" in codes
    assert "missing_readme_testing_evidence_anchor" in codes
    assert "invalid_readme_testing_map_status" in codes
    assert "invalid_missing_evidence_credential_skip_transcript" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_testing_boundary_summary_reports_shape():
    summary = render_readme_testing_boundary_summary(readme_testing_boundary_record())

    assert "README testing boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_testing_commands_structural_map_without_selection_transcript |"
        in summary
    )
    assert "| readme_marker_count | 5 |" in summary
    assert "| missing_readme_marker_count | 0 |" in summary
    assert "| evidence_anchor_count | 11 |" in summary
    assert "| missing_evidence_anchor_count | 0 |" in summary
    assert "| pytest_marker_count | 1 |" in summary
    assert "| integration_test_marker_count | 2 |" in summary
    assert "| credential_skip_marker_count | 2 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
