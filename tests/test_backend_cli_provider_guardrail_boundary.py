from libreevolve.problems.benchmarks.backend_cli_provider_guardrail_boundary import (
    BACKEND_CLI_PROVIDER_GUARDRAIL_BOUNDARY_SCHEMA,
    backend_cli_provider_guardrail_boundary_record,
    render_backend_cli_provider_guardrail_boundary_summary,
    validate_backend_cli_provider_guardrail_boundary,
)


def test_backend_cli_provider_guardrail_boundary_accepts_current_markers():
    boundary = backend_cli_provider_guardrail_boundary_record()

    validation = validate_backend_cli_provider_guardrail_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "backend_docs_cli_provider_guardrail_without_first_class_cli_backend_contract"
    )
    assert boundary["schema"] == BACKEND_CLI_PROVIDER_GUARDRAIL_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.marker_record_count == 13
    assert validation.missing_marker_count == 0
    assert validation.forbidden_claim_count == 0
    assert boundary["backend_cli_provider_guardrail_status"] == (
        "backend_docs_cli_provider_guardrail_present"
    )
    assert boundary["missing_marker_records"] == []
    assert boundary["forbidden_claim_records"] == []
    assert boundary["missing_evidence"] == {
        "first_class_cli_backend_contract": "not_recorded_locally",
        "cli_backend_manifest_schema": "not_recorded_locally",
        "credential_safe_cli_backend_smoke": "not_recorded_locally",
        "cli_provider_attempt_accounting": "not_recorded_locally",
        "cli_provider_diagnostics": "not_recorded_locally",
    }
    assert "docs/backends.md provider-lane taxonomy" in boundary["claim_boundary"]


def test_backend_cli_provider_guardrail_boundary_rejects_overclaim_and_drift():
    boundary = backend_cli_provider_guardrail_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "first_class_cli_backend_supported"
    boundary["marker_record_count"] = 0
    boundary["missing_marker_count"] = 1
    boundary["missing_marker_records"] = [boundary["marker_records"][0]]
    boundary["marker_records"][0]["marker_status"] = "marker_missing"
    boundary["forbidden_claim_count"] = 1
    boundary["forbidden_claim_records"] = [
        {
            "path": "docs/backends.md",
            "forbidden_phrase": "Codex CLI backend is supported",
            "claim_status": "forbidden_supported_claim_present",
        }
    ]
    boundary["backend_cli_provider_guardrail_status"] = (
        "backend_docs_cli_provider_guardrail_incomplete"
    )
    boundary["missing_evidence"]["cli_backend_manifest_schema"] = "recorded"
    boundary["required_evidence_fields"] = ["backends_provider_lane_taxonomy"]

    validation = validate_backend_cli_provider_guardrail_boundary(boundary)
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
    assert "invalid_backend_cli_provider_guardrail_status" in codes
    assert "missing_backend_cli_provider_guardrail_marker" in codes
    assert "forbidden_cli_provider_supported_claim" in codes
    assert "invalid_missing_evidence_cli_backend_manifest_schema" in codes
    assert "missing_required_evidence_field" in codes


def test_render_backend_cli_provider_guardrail_boundary_summary_reports_shape():
    summary = render_backend_cli_provider_guardrail_boundary_summary(
        backend_cli_provider_guardrail_boundary_record()
    )

    assert "Backend CLI-provider guardrail boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | backend_docs_cli_provider_guardrail_without_first_class_cli_backend_contract |"
        in summary
    )
    assert "| marker_record_count | 13 |" in summary
    assert "| missing_marker_count | 0 |" in summary
    assert "| forbidden_claim_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
