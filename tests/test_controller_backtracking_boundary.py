from libreevolve.problems.benchmarks.controller_backtracking_boundary import (
    CONTROLLER_BACKTRACKING_BOUNDARY_SCHEMA,
    controller_backtracking_boundary_record,
    render_controller_backtracking_boundary_summary,
    validate_controller_backtracking_boundary,
)


def test_controller_backtracking_boundary_accepts_absence_record():
    boundary = controller_backtracking_boundary_record()

    validation = validate_controller_backtracking_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "observed_redirects_without_controller_policy"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 10
    assert boundary["schema"] == CONTROLLER_BACKTRACKING_BOUNDARY_SCHEMA
    assert "does not claim AlphaEvolve-style controller-owned backtracking" in (
        boundary["claim_boundary"]
    )
    assert "unpromising_decision_rule" in boundary["required_evidence_fields"]
    assert "prompt_sampling_suppression_effect" in (
        boundary["required_evidence_fields"]
    )
    assert (
        boundary["missing_evidence"]["controller_branch_state_machine"]
        == "not_recorded_locally"
    )
    assert "unpromising-decision rules and thresholds" in boundary["claim_boundary"]


def test_controller_backtracking_boundary_rejects_premature_policy_claim():
    boundary = controller_backtracking_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "controller_policy_recorded"
    boundary["missing_evidence"]["controller_owned_suppression_policy"] = "configured"
    boundary["required_evidence_fields"] = ["branch_id"]

    validation = validate_controller_backtracking_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_controller_owned_suppression_policy" in codes
    assert "missing_required_evidence_field" in codes


def test_render_controller_backtracking_boundary_summary_reports_shape():
    summary = render_controller_backtracking_boundary_summary(
        controller_backtracking_boundary_record()
    )

    assert "AlphaEvolve controller backtracking boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | observed_redirects_without_controller_policy |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 10 |" in summary
