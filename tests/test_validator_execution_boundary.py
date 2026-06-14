from libreevolve.problems.benchmarks.validator_execution_boundary import (
    VALIDATOR_EXECUTION_BOUNDARY_SCHEMA,
    render_validator_execution_boundary_summary,
    validate_validator_execution_boundary,
    validator_execution_boundary_record,
)


def test_validator_execution_boundary_accepts_local_policy_record():
    boundary = validator_execution_boundary_record()

    validation = validate_validator_execution_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "local_subprocess_validator_policy_without_os_container_sandbox"
    )
    assert validation.required_evidence_field_count == 20
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == VALIDATOR_EXECUTION_BOUNDARY_SCHEMA
    assert "filesystem_capabilities_record" in boundary["required_evidence_fields"]
    assert "does not claim OS/container sandbox enforcement" in (
        boundary["claim_boundary"]
    )


def test_validator_execution_boundary_rejects_sandbox_overclaim():
    boundary = validator_execution_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "os_container_sandbox_ready"
    boundary["missing_evidence"]["os_container_sandbox_enforcement"] = "recorded"
    boundary["required_evidence_fields"] = ["startup_validator_execution_policy_schema"]

    validation = validate_validator_execution_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_os_container_sandbox_enforcement" in codes
    assert "missing_required_evidence_field" in codes


def test_render_validator_execution_boundary_summary_reports_shape():
    summary = render_validator_execution_boundary_summary(
        validator_execution_boundary_record()
    )

    assert "Validator execution boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | local_subprocess_validator_policy_without_os_container_sandbox |"
        in summary
    )
    assert "| required_evidence_field_count | 20 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
