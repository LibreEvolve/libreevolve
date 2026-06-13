from libreevolve.problems.benchmarks.feedback_calibration_boundary import (
    FEEDBACK_CALIBRATION_BOUNDARY_SCHEMA,
    feedback_calibration_boundary_record,
    render_feedback_calibration_boundary_summary,
    validate_feedback_calibration_boundary,
)


def test_feedback_calibration_boundary_accepts_report_contract_boundary():
    boundary = feedback_calibration_boundary_record()

    validation = validate_feedback_calibration_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "report_contract_without_executed_calibration_fixtures"
    )
    assert validation.required_evidence_field_count == 12
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == FEEDBACK_CALIBRATION_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.4"]
    assert boundary["claim_ready"] is False
    assert "does not claim a runtime calibration runner" in boundary["claim_boundary"]


def test_feedback_calibration_boundary_rejects_executed_calibration_overclaim():
    boundary = feedback_calibration_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "executed_feedback_calibration_ready"
    boundary["source_section_ids"] = ["2.3"]
    boundary["missing_evidence"]["runtime_calibration_runner"] = "recorded"
    boundary["required_evidence_fields"] = ["feedback_calibration_report_schema"]

    validation = validate_feedback_calibration_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_runtime_calibration_runner" in codes
    assert "missing_required_evidence_field" in codes


def test_render_feedback_calibration_boundary_summary_reports_shape():
    summary = render_feedback_calibration_boundary_summary(
        feedback_calibration_boundary_record()
    )

    assert "Feedback calibration boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | report_contract_without_executed_calibration_fixtures |"
        in summary
    )
    assert "| required_evidence_field_count | 12 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
