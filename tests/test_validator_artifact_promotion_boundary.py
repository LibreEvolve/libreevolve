from libreevolve.problems.benchmarks.validator_artifact_promotion_boundary import (
    VALIDATOR_ARTIFACT_PROMOTION_BOUNDARY_SCHEMA,
    render_validator_artifact_promotion_boundary_summary,
    validate_validator_artifact_promotion_boundary,
    validator_artifact_promotion_boundary_record,
)


def test_validator_artifact_promotion_boundary_accepts_cli_gate_record():
    boundary = validator_artifact_promotion_boundary_record()

    validation = validate_validator_artifact_promotion_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "cli_inspection_gate_without_promotion_time_enforcement"
    )
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == VALIDATOR_ARTIFACT_PROMOTION_BOUNDARY_SCHEMA
    assert "show_command_gate" in boundary["required_evidence_fields"]
    assert "does not claim run-finalization enforcement" in (
        boundary["claim_boundary"]
    )


def test_validator_artifact_promotion_boundary_rejects_promotion_overclaim():
    boundary = validator_artifact_promotion_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "release_artifact_promotion_gate_ready"
    boundary["missing_evidence"]["release_artifact_promotion_gate"] = "recorded"
    boundary["required_evidence_fields"] = [
        "run_artifact_validator_boundary_consistency_schema"
    ]

    validation = validate_validator_artifact_promotion_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_release_artifact_promotion_gate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_validator_artifact_promotion_boundary_summary_reports_shape():
    summary = render_validator_artifact_promotion_boundary_summary(
        validator_artifact_promotion_boundary_record()
    )

    assert "Validator artifact promotion boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | cli_inspection_gate_without_promotion_time_enforcement |"
        in summary
    )
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
