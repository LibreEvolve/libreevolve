from libreevolve.problems.benchmarks.provider_cancellation_boundary import (
    PROVIDER_CANCELLATION_BOUNDARY_SCHEMA,
    provider_cancellation_boundary_record,
    render_provider_cancellation_boundary_summary,
    validate_provider_cancellation_boundary,
)


def test_provider_cancellation_boundary_accepts_policy_audit_boundary():
    boundary = provider_cancellation_boundary_record()

    validation = validate_provider_cancellation_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "policy_and_audit_without_live_hard_cancellation"
    )
    assert validation.required_evidence_field_count == 20
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == PROVIDER_CANCELLATION_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim live provider SDK cancellation" in boundary["claim_boundary"]


def test_provider_cancellation_boundary_rejects_live_cancellation_overclaim():
    boundary = provider_cancellation_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "live_hard_provider_cancellation_ready"
    boundary["missing_evidence"]["live_provider_sdk_cancellation"] = "recorded"
    boundary["required_evidence_fields"] = ["provider_request_timeout_rules"]

    validation = validate_provider_cancellation_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_live_provider_sdk_cancellation" in codes
    assert "missing_required_evidence_field" in codes


def test_render_provider_cancellation_boundary_summary_reports_shape():
    summary = render_provider_cancellation_boundary_summary(
        provider_cancellation_boundary_record()
    )

    assert "Provider cancellation boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | policy_and_audit_without_live_hard_cancellation |"
        in summary
    )
    assert "| required_evidence_field_count | 20 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
