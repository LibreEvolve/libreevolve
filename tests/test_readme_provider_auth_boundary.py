from libreevolve.problems.benchmarks.readme_provider_auth_boundary import (
    README_PROVIDER_AUTH_BOUNDARY_SCHEMA,
    readme_provider_auth_boundary_record,
    render_readme_provider_auth_boundary_summary,
    validate_readme_provider_auth_boundary,
)


def test_readme_provider_auth_boundary_accepts_current_markers():
    boundary = readme_provider_auth_boundary_record()

    validation = validate_readme_provider_auth_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_provider_auth_static_markers_without_live_provider_proof"
    )
    assert boundary["schema"] == README_PROVIDER_AUTH_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["expected_provider_variables"] == {
        "OPENAI_API_KEY": "sk-your-openai-key-here",
        "ANTHROPIC_API_KEY": "sk-ant-your-anthropic-key-here",
        "GEMINI_API_KEY": "your-gemini-key-here",
        "OLLAMA_HOST": "http://localhost:11434",
    }
    assert validation.env_variable_count == 4
    assert boundary["env_missing_records"] == []
    assert boundary["unsafe_placeholder_records"] == []
    assert validation.missing_marker_count == 0
    assert validation.unsafe_placeholder_count == 0
    assert boundary["provider_auth_marker_status"] == "provider_auth_static_markers_present"
    assert boundary["missing_evidence"] == {
        "backend_registry_auth_reflection": "not_recorded_locally",
        "live_provider_account_probe": "not_recorded_locally",
        "provider_auth_drift_ci_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert ".env.example provider variables" in boundary["claim_boundary"]


def test_readme_provider_auth_boundary_rejects_overclaim_and_marker_drift():
    boundary = readme_provider_auth_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "provider_auth_live_account_proof_ready"
    boundary["env_variable_count"] = 2
    boundary["env_missing_count"] = 1
    boundary["env_missing_records"] = [
        {
            "name": "OPENAI_API_KEY",
            "expected_value": "sk-your-openai-key-here",
            "record_status": "env_variable_missing",
        }
    ]
    boundary["placeholder_records"][0]["placeholder_status"] = "placeholder_unsafe"
    boundary["unsafe_placeholder_count"] = 1
    boundary["unsafe_placeholder_records"] = [boundary["placeholder_records"][0]]
    boundary["missing_marker_count"] = 1
    boundary["missing_marker_records"] = [boundary["marker_records"][0]]
    boundary["marker_records"][0]["marker_status"] = "marker_missing"
    boundary["provider_auth_marker_status"] = "provider_auth_static_markers_incomplete"
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["env_example_provider_variables"]

    validation = validate_readme_provider_auth_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_env_variable_count" in codes
    assert "invalid_env_missing_count" in codes
    assert "invalid_env_missing_records" in codes
    assert "invalid_placeholder_records" in codes
    assert "invalid_unsafe_placeholder_count" in codes
    assert "invalid_unsafe_placeholder_records" in codes
    assert "invalid_missing_marker_count" in codes
    assert "invalid_missing_marker_records" in codes
    assert "invalid_marker_records" in codes
    assert "invalid_provider_auth_marker_status" in codes
    assert "missing_env_variable" in codes
    assert "missing_provider_auth_marker" in codes
    assert "unsafe_provider_placeholder" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_provider_auth_boundary_summary_reports_shape():
    summary = render_readme_provider_auth_boundary_summary(
        readme_provider_auth_boundary_record()
    )

    assert "README provider-auth boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_provider_auth_static_markers_without_live_provider_proof |"
        in summary
    )
    assert "| env_variable_count | 4 |" in summary
    assert "| missing_marker_count | 0 |" in summary
    assert "| unsafe_placeholder_count | 0 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
