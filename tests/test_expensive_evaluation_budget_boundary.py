from libreevolve.problems.benchmarks.expensive_evaluation_budget_boundary import (
    EXPENSIVE_EVALUATION_BUDGET_BOUNDARY_SCHEMA,
    expensive_evaluation_budget_boundary_record,
    render_expensive_evaluation_budget_boundary_summary,
    validate_expensive_evaluation_budget_boundary,
)


def test_expensive_evaluation_budget_boundary_accepts_local_budget_boundary():
    boundary = expensive_evaluation_budget_boundary_record()

    validation = validate_expensive_evaluation_budget_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "local_cooperative_budgets_without_compute_hour_runtime"
    )
    assert validation.required_evidence_field_count == 22
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == EXPENSIVE_EVALUATION_BUDGET_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim per-candidate compute-hour accounting" in boundary["claim_boundary"]


def test_expensive_evaluation_budget_boundary_rejects_compute_hour_overclaim():
    boundary = expensive_evaluation_budget_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "compute_hour_accelerator_budget_ready"
    boundary["missing_evidence"]["per_candidate_compute_hour_accounting"] = "recorded"
    boundary["required_evidence_fields"] = ["max_evaluations_limit"]

    validation = validate_expensive_evaluation_budget_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_per_candidate_compute_hour_accounting" in codes
    assert "missing_required_evidence_field" in codes


def test_render_expensive_evaluation_budget_boundary_summary_reports_shape():
    summary = render_expensive_evaluation_budget_boundary_summary(
        expensive_evaluation_budget_boundary_record()
    )

    assert "Expensive evaluation budget boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | local_cooperative_budgets_without_compute_hour_runtime |"
        in summary
    )
    assert "| required_evidence_field_count | 22 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
