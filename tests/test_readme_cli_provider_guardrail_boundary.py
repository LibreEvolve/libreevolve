from libreevolve.problems.benchmarks.readme_cli_provider_guardrail_boundary import (
    README_CLI_PROVIDER_GUARDRAIL_BOUNDARY_SCHEMA,
    readme_cli_provider_guardrail_boundary_record,
    render_readme_cli_provider_guardrail_boundary_summary,
    validate_readme_cli_provider_guardrail_boundary,
)


def test_readme_cli_provider_guardrail_boundary_accepts_current_markers():
    boundary = readme_cli_provider_guardrail_boundary_record()

    validation = validate_readme_cli_provider_guardrail_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "readme_codex_cli_lane_without_benchmark_ready_parity"
    )
    assert boundary["schema"] == README_CLI_PROVIDER_GUARDRAIL_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.marker_record_count == 15
    assert validation.missing_marker_count == 0
    assert validation.forbidden_claim_count == 0
    assert boundary["cli_provider_guardrail_status"] == (
        "readme_cli_provider_guardrail_present"
    )
    assert boundary["missing_marker_records"] == []
    assert boundary["forbidden_claim_records"] == []
    assert boundary["missing_evidence"] == {
        "benchmark_ready_cli_provider_contract": "not_recorded_locally",
        "cli_backend_manifest_report_integration": "not_recorded_locally",
        "credential_safe_cli_backend_smoke": "not_recorded_locally",
        "cli_model_availability_preflight": "not_recorded_locally",
        "provider_budget_accounting_for_cli_backend": "not_recorded_locally",
        "provider_diagnostics_for_cli_backend": "not_recorded_locally",
    }
    assert "subprocess/CLI backend contract TODO" in boundary["claim_boundary"]


def test_readme_cli_provider_guardrail_boundary_rejects_overclaim_and_drift():
    boundary = readme_cli_provider_guardrail_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "first_class_cli_backend_supported"
    boundary["marker_record_count"] = 0
    boundary["missing_marker_count"] = 1
    boundary["missing_marker_records"] = [boundary["marker_records"][0]]
    boundary["marker_records"][0]["marker_status"] = "marker_missing"
    boundary["forbidden_claim_count"] = 1
    boundary["forbidden_claim_records"] = [
        {
            "path": "README.md",
            "forbidden_phrase": "Codex CLI runs are benchmark-ready",
            "claim_status": "forbidden_supported_claim_present",
        }
    ]
    boundary["cli_provider_guardrail_status"] = "readme_cli_provider_guardrail_incomplete"
    boundary["missing_evidence"]["benchmark_ready_cli_provider_contract"] = "recorded"
    boundary["required_evidence_fields"] = ["readme_backend_feature_bullet"]

    validation = validate_readme_cli_provider_guardrail_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_marker_record_count" in codes
    assert "invalid_missing_marker_count" in codes
    assert "invalid_missing_marker_records" in codes
    assert "invalid_marker_records" in codes
    assert "invalid_forbidden_claim_count" in codes
    assert "invalid_forbidden_claim_records" in codes
    assert "invalid_cli_provider_guardrail_status" in codes
    assert "missing_cli_provider_guardrail_marker" in codes
    assert "forbidden_cli_provider_supported_claim" in codes
    assert "invalid_missing_evidence_benchmark_ready_cli_provider_contract" in codes
    assert "missing_required_evidence_field" in codes


def test_render_readme_cli_provider_guardrail_boundary_summary_reports_shape():
    summary = render_readme_cli_provider_guardrail_boundary_summary(
        readme_cli_provider_guardrail_boundary_record()
    )

    assert "README CLI-provider guardrail boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | readme_codex_cli_lane_without_benchmark_ready_parity |"
        in summary
    )
    assert "| marker_record_count | 15 |" in summary
    assert "| missing_marker_count | 0 |" in summary
    assert "| forbidden_claim_count | 0 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
