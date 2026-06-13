from libreevolve.problems.benchmarks.qualitative_feedback_boundary import (
    QUALITATIVE_FEEDBACK_BOUNDARY_SCHEMA,
    qualitative_feedback_boundary_record,
    render_qualitative_feedback_boundary_summary,
    validate_qualitative_feedback_boundary,
)


def test_qualitative_feedback_boundary_accepts_declared_policy_boundary():
    boundary = qualitative_feedback_boundary_record()

    validation = validate_qualitative_feedback_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "declared_qualitative_policy_without_executed_calibration"
    )
    assert validation.required_evidence_field_count == 15
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == QUALITATIVE_FEEDBACK_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.4"]
    assert boundary["claim_ready"] is False
    assert "does not claim executed calibration task suites" in boundary["claim_boundary"]


def test_qualitative_feedback_boundary_rejects_calibration_overclaim():
    boundary = qualitative_feedback_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "executed_qualitative_feedback_calibration_ready"
    boundary["source_section_ids"] = ["2.3"]
    boundary["missing_evidence"]["executed_calibration_task_suite"] = "recorded"
    boundary["required_evidence_fields"] = ["qualitative_criterion_metadata"]

    validation = validate_qualitative_feedback_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_executed_calibration_task_suite" in codes
    assert "missing_required_evidence_field" in codes


def test_render_qualitative_feedback_boundary_summary_reports_shape():
    summary = render_qualitative_feedback_boundary_summary(
        qualitative_feedback_boundary_record()
    )

    assert "Qualitative feedback boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | declared_qualitative_policy_without_executed_calibration |"
        in summary
    )
    assert "| required_evidence_field_count | 15 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
