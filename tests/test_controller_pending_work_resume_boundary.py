from libreevolve.problems.benchmarks.controller_pending_work_resume_boundary import (
    CONTROLLER_PENDING_WORK_RESUME_BOUNDARY_SCHEMA,
    controller_pending_work_resume_boundary_record,
    render_controller_pending_work_resume_boundary_summary,
    validate_controller_pending_work_resume_boundary,
)


def test_controller_pending_work_resume_boundary_accepts_terminal_snapshot_record():
    boundary = controller_pending_work_resume_boundary_record()

    validation = validate_controller_pending_work_resume_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "terminal_controller_snapshot_without_pending_work_resume"
    )
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 9
    assert boundary["schema"] == CONTROLLER_PENDING_WORK_RESUME_BOUNDARY_SCHEMA
    assert "terminal_drained_controller_state" in boundary["required_evidence_fields"]
    assert "does not claim controller queue checkpoint schema support" in (
        boundary["claim_boundary"]
    )


def test_controller_pending_work_resume_boundary_rejects_resume_overclaim():
    boundary = controller_pending_work_resume_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "pending_work_resume_ready"
    boundary["missing_evidence"]["controller_queue_checkpoint_schema"] = "recorded"
    boundary["required_evidence_fields"] = ["controller_state_schema"]

    validation = validate_controller_pending_work_resume_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_controller_queue_checkpoint_schema"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_controller_pending_work_resume_boundary_summary_reports_shape():
    summary = render_controller_pending_work_resume_boundary_summary(
        controller_pending_work_resume_boundary_record()
    )

    assert "Controller pending-work resume boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | terminal_controller_snapshot_without_pending_work_resume |"
        in summary
    )
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
