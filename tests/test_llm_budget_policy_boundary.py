from libreevolve.problems.benchmarks.llm_budget_policy_boundary import (
    LLM_BUDGET_POLICY_BOUNDARY_SCHEMA,
    llm_budget_policy_boundary_record,
    render_llm_budget_policy_boundary_summary,
    validate_llm_budget_policy_boundary,
)


def test_llm_budget_policy_boundary_accepts_cooperative_budget_boundary():
    boundary = llm_budget_policy_boundary_record()

    validation = validate_llm_budget_policy_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "cooperative_llm_budget_snapshots_without_async_pending_work_accounting"
    )
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == LLM_BUDGET_POLICY_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.2", "2.4", "2.6", "4"]
    assert boundary["claim_ready"] is False
    assert "does not claim async role work queue budget accounting" in boundary["claim_boundary"]


def test_llm_budget_policy_boundary_rejects_async_budget_overclaim():
    boundary = llm_budget_policy_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "async_pending_work_budget_accounting_ready"
    boundary["missing_evidence"]["queued_running_pending_work_budget_state"] = "recorded"
    boundary["required_evidence_fields"] = [
        "llm_budget_report_schema",
    ]

    validation = validate_llm_budget_policy_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_queued_running_pending_work_budget_state" in codes
    assert "missing_required_evidence_field" in codes


def test_render_llm_budget_policy_boundary_summary_reports_shape():
    summary = render_llm_budget_policy_boundary_summary(
        llm_budget_policy_boundary_record()
    )

    assert "LLM budget policy boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | cooperative_llm_budget_snapshots_without_async_pending_work_accounting |"
        in summary
    )
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
