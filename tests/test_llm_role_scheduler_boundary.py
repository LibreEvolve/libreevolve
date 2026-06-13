from libreevolve.problems.benchmarks.llm_role_scheduler_boundary import (
    LLM_ROLE_SCHEDULER_BOUNDARY_SCHEMA,
    llm_role_scheduler_boundary_record,
    render_llm_role_scheduler_boundary_summary,
    validate_llm_role_scheduler_boundary,
)


def test_llm_role_scheduler_boundary_accepts_local_role_scoped_boundary():
    boundary = llm_role_scheduler_boundary_record()

    validation = validate_llm_role_scheduler_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "role_scoped_local_ucb_without_calibrated_experiment_policy"
    )
    assert validation.required_evidence_field_count == 28
    assert validation.missing_evidence_count == 11
    assert boundary["schema"] == LLM_ROLE_SCHEDULER_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim role-specific backend-pool policy" in (
        boundary["claim_boundary"]
    )
    assert "role reward normalization reports" in boundary["claim_boundary"]
    assert (
        boundary["missing_evidence"]["role_specific_exploration_parameters"]
        == "global_ucb_coefficient_only"
    )


def test_llm_role_scheduler_boundary_rejects_alphaevolve_overclaim():
    boundary = llm_role_scheduler_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "calibrated_alphaevolve_role_scheduler_ready"
    boundary["missing_evidence"]["calibrated_role_reward_policy"] = "recorded"
    boundary["missing_evidence"]["async_role_work_queue_policy"] = "recorded"
    boundary["required_evidence_fields"] = ["configured_reward_accounted_roles"]

    validation = validate_llm_role_scheduler_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_calibrated_role_reward_policy" in codes
    assert "invalid_missing_evidence_async_role_work_queue_policy" in codes
    assert "missing_required_evidence_field" in codes


def test_render_llm_role_scheduler_boundary_summary_reports_shape():
    summary = render_llm_role_scheduler_boundary_summary(
        llm_role_scheduler_boundary_record()
    )

    assert "LLM role scheduler boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | role_scoped_local_ucb_without_calibrated_experiment_policy |"
        in summary
    )
    assert "| required_evidence_field_count | 28 |" in summary
    assert "| missing_evidence_count | 11 |" in summary
