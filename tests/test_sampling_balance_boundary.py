from libreevolve.problems.benchmarks.sampling_balance_boundary import (
    SAMPLING_BALANCE_BOUNDARY_SCHEMA,
    render_sampling_balance_boundary_summary,
    sampling_balance_boundary_record,
    validate_sampling_balance_boundary,
)


def test_sampling_balance_boundary_accepts_local_sampling_counts_boundary():
    boundary = sampling_balance_boundary_record()

    validation = validate_sampling_balance_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "local_sampling_counts_with_repetition_and_source_provenance"
    )
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 4
    assert boundary["schema"] == SAMPLING_BALANCE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        "does not claim calibrated exploration/exploitation balance"
        in boundary["claim_boundary"]
    )


def test_sampling_balance_boundary_rejects_calibrated_balance_overclaim():
    boundary = sampling_balance_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "calibrated_alphaevolve_sampling_balance"
    boundary["missing_evidence"]["equal_budget_strategy_comparisons"] = "recorded"
    boundary["required_evidence_fields"] = ["configured_explore_ratio"]

    validation = validate_sampling_balance_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_equal_budget_strategy_comparisons" in codes
    assert "missing_required_evidence_field" in codes


def test_render_sampling_balance_boundary_summary_reports_shape():
    summary = render_sampling_balance_boundary_summary(
        sampling_balance_boundary_record()
    )

    assert "Sampling balance boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | local_sampling_counts_with_repetition_and_source_provenance |"
        in summary
    )
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
