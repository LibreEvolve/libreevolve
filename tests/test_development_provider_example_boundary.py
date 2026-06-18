from libreevolve.problems.benchmarks.development_provider_example_boundary import (
    DEVELOPMENT_PROVIDER_EXAMPLE_BOUNDARY_SCHEMA,
    development_provider_example_boundary_record,
    render_development_provider_example_boundary_summary,
    validate_development_provider_example_boundary,
)


def test_development_provider_example_boundary_accepts_current_static_inventory():
    boundary = development_provider_example_boundary_record()

    validation = validate_development_provider_example_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "development_provider_examples_static_inventory_with_paired_show_commands"
    )
    assert boundary["schema"] == DEVELOPMENT_PROVIDER_EXAMPLE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.provider_example_count == 2
    assert validation.missing_command_count == 0
    assert validation.unpaired_show_count == 0
    assert validation.guidance_marker_count == 13
    assert validation.missing_guidance_marker_count == 0
    assert validation.missing_evidence_count == 6
    assert boundary["missing_command_records"] == []
    assert boundary["missing_guidance_marker_records"] == []
    assert [record["provider"] for record in boundary["provider_example_records"]] == [
        "openai",
        "anthropic",
    ]
    assert boundary["unpaired_show_records"] == []
    assert [record["expected_run_dir"] for record in boundary["provider_example_records"]] == [
        "runs/development_hello_world",
        "runs/development_circle_packing",
    ]
    assert boundary["development_provider_example_status"] == (
        "development_provider_examples_static_inventory_with_paired_show_commands"
    )
    assert boundary["missing_evidence"] == {
        "live_openai_model_availability_probe": "not_recorded_locally",
        "live_anthropic_model_availability_probe": "not_recorded_locally",
        "credential_safe_development_provider_smoke": "not_recorded_locally",
        "account_specific_model_id_provenance": "not_recorded_locally",
        "ci_development_provider_matrix": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "paired show commands for both provider examples" in boundary["claim_boundary"]


def test_development_provider_example_boundary_rejects_overclaim_and_drift():
    boundary = development_provider_example_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "development_provider_examples_live_smoke_ready"
    boundary["provider_example_count"] = 1
    boundary["missing_command_count"] = 1
    boundary["missing_command_records"] = [boundary["provider_example_records"][0]]
    boundary["provider_example_records"][0]["command_marker_status"] = (
        "command_marker_missing"
    )
    boundary["unpaired_show_count"] = 1
    boundary["unpaired_show_records"] = [boundary["provider_example_records"][1]]
    boundary["guidance_marker_count"] = 0
    boundary["missing_guidance_marker_count"] = 1
    boundary["missing_guidance_marker_records"] = [boundary["guidance_marker_records"][0]]
    boundary["guidance_marker_records"][0]["marker_status"] = "marker_missing"
    boundary["development_provider_example_status"] = (
        "development_provider_examples_static_inventory_incomplete"
    )
    boundary["missing_evidence"]["ci_development_provider_matrix"] = "recorded"
    boundary["required_evidence_fields"] = ["development_provider_command_markers"]

    validation = validate_development_provider_example_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_provider_example_count" in codes
    assert "invalid_missing_command_count" in codes
    assert "invalid_missing_command_records" in codes
    assert "invalid_provider_example_records" in codes
    assert "invalid_unpaired_show_count" in codes
    assert "invalid_unpaired_show_records" in codes
    assert "invalid_guidance_marker_count" in codes
    assert "invalid_missing_guidance_marker_count" in codes
    assert "invalid_missing_guidance_marker_records" in codes
    assert "invalid_guidance_marker_records" in codes
    assert "invalid_development_provider_example_status" in codes
    assert "missing_development_provider_command" in codes
    assert "invalid_missing_evidence_ci_development_provider_matrix" in codes
    assert "missing_required_evidence_field" in codes


def test_render_development_provider_example_boundary_summary_reports_shape():
    summary = render_development_provider_example_boundary_summary(
        development_provider_example_boundary_record()
    )

    assert "Development provider example boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | development_provider_examples_static_inventory_with_paired_show_commands |"
        in summary
    )
    assert "| provider_example_count | 2 |" in summary
    assert "| missing_command_count | 0 |" in summary
    assert "| unpaired_show_count | 0 |" in summary
    assert "| guidance_marker_count | 13 |" in summary
    assert "| missing_guidance_marker_count | 0 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
