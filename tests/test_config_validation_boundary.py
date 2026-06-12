from libreevolve.problems.benchmarks.config_validation_boundary import (
    CONFIG_VALIDATION_BOUNDARY_SCHEMA,
    config_validation_boundary_record,
    render_config_validation_boundary_summary,
    validate_config_validation_boundary,
)


def test_config_validation_boundary_accepts_local_effective_config_boundary():
    boundary = config_validation_boundary_record()

    validation = validate_config_validation_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "local_effective_config_validation_only"
    assert validation.required_evidence_field_count == 12
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == CONFIG_VALIDATION_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim live provider/model API compatibility" in boundary["claim_boundary"]


def test_config_validation_boundary_rejects_live_provider_overclaim():
    boundary = config_validation_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "live_provider_api_compatible"
    boundary["missing_evidence"]["live_provider_model_registry_validation"] = "recorded"
    boundary["required_evidence_fields"] = ["cli_overrides_applied_before_validation"]

    validation = validate_config_validation_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_live_provider_model_registry_validation" in codes
    assert "missing_required_evidence_field" in codes


def test_render_config_validation_boundary_summary_reports_shape():
    summary = render_config_validation_boundary_summary(
        config_validation_boundary_record()
    )

    assert "Config validation boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | local_effective_config_validation_only |" in summary
    assert "| required_evidence_field_count | 12 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
