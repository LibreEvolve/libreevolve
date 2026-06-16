from libreevolve.problems.benchmarks.readme_provider_example_matrix_boundary import (
    README_PROVIDER_EXAMPLE_MATRIX_BOUNDARY_SCHEMA,
    readme_provider_example_matrix_boundary_record,
    render_readme_provider_example_matrix_boundary_summary,
    validate_readme_provider_example_matrix_boundary,
)


def test_readme_provider_example_matrix_boundary_accepts_current_markers():
    boundary = readme_provider_example_matrix_boundary_record()

    validation = validate_readme_provider_example_matrix_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_provider_examples_static_matrix_without_live_provider_smoke"
    )
    assert boundary["schema"] == README_PROVIDER_EXAMPLE_MATRIX_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.provider_command_record_count == 3
    assert validation.missing_provider_command_record_count == 0
    assert validation.contract_marker_record_count == 15
    assert validation.missing_contract_marker_count == 0
    assert boundary["provider_example_matrix_status"] == (
        "readme_provider_example_static_contract_present"
    )
    assert [record["provider"] for record in boundary["provider_command_records"]] == [
        "openai",
        "anthropic",
        "ollama",
    ]
    assert boundary["missing_provider_command_records"] == []
    assert boundary["missing_contract_marker_records"] == []
    assert boundary["missing_evidence"] == {
        "live_openai_model_availability_probe": "not_recorded_locally",
        "live_anthropic_model_availability_probe": "not_recorded_locally",
        "live_ollama_inventory_probe": "not_recorded_locally",
        "credential_safe_provider_smoke_matrix": "not_recorded_locally",
        "account_specific_model_id_provenance": "not_recorded_locally",
        "ci_provider_matrix": "not_recorded_locally",
        "google_gemini_provider_parity": "not_recorded_locally",
    }
    assert "CLI type:model backend-shorthand construction" in boundary["claim_boundary"]


def test_readme_provider_example_matrix_boundary_rejects_overclaim_and_drift():
    boundary = readme_provider_example_matrix_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "readme_provider_examples_live_smoke_ready"
    boundary["provider_command_record_count"] = 2
    boundary["missing_provider_command_record_count"] = 1
    boundary["missing_provider_command_records"] = [
        boundary["provider_command_records"][0]
    ]
    boundary["provider_command_records"][0]["command_marker_status"] = (
        "command_marker_missing"
    )
    boundary["contract_marker_record_count"] = 0
    boundary["missing_contract_marker_count"] = 1
    boundary["missing_contract_marker_records"] = [boundary["contract_marker_records"][0]]
    boundary["contract_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["provider_example_matrix_status"] = (
        "readme_provider_example_static_contract_incomplete"
    )
    boundary["missing_evidence"]["ci_provider_matrix"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_provider_command_markers"]

    validation = validate_readme_provider_example_matrix_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_provider_command_record_count" in codes
    assert "invalid_missing_provider_command_record_count" in codes
    assert "invalid_missing_provider_command_records" in codes
    assert "invalid_provider_command_records" in codes
    assert "invalid_contract_marker_record_count" in codes
    assert "invalid_missing_contract_marker_count" in codes
    assert "invalid_missing_contract_marker_records" in codes
    assert "invalid_contract_marker_records" in codes
    assert "invalid_provider_example_matrix_status" in codes
    assert "missing_provider_command_marker" in codes
    assert "missing_provider_contract_marker" in codes
    assert "invalid_missing_evidence_ci_provider_matrix" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_provider_example_matrix_boundary_summary_reports_shape():
    summary = render_readme_provider_example_matrix_boundary_summary(
        readme_provider_example_matrix_boundary_record()
    )

    assert "README provider example matrix boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_provider_examples_static_matrix_without_live_provider_smoke |"
        in summary
    )
    assert "| provider_command_record_count | 3 |" in summary
    assert "| missing_provider_command_record_count | 0 |" in summary
    assert "| contract_marker_record_count | 15 |" in summary
    assert "| missing_contract_marker_count | 0 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
