from libreevolve.problems.benchmarks.repeated_sampling_baseline_boundary import (
    REPEATED_SAMPLING_BASELINE_BOUNDARY_SCHEMA,
    repeated_sampling_baseline_boundary_record,
    render_repeated_sampling_baseline_boundary_summary,
    validate_repeated_sampling_baseline_boundary,
)


def test_repeated_sampling_baseline_boundary_accepts_absence_record():
    boundary = repeated_sampling_baseline_boundary_record()

    validation = validate_repeated_sampling_baseline_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "runtime_absence_boundary_only"
    assert validation.required_control_count == 11
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == REPEATED_SAMPLING_BASELINE_BOUNDARY_SCHEMA
    assert "does not claim an executable controlled repeated-sampling runner" in boundary["claim_boundary"]


def test_repeated_sampling_baseline_boundary_rejects_premature_comparator_claim():
    boundary = repeated_sampling_baseline_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "controlled_comparator_ready"
    boundary["missing_evidence"]["budget_parity_validation"] = "recorded"
    boundary["required_comparator_controls"] = ["fixed_model_and_backend"]

    validation = validate_repeated_sampling_baseline_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_budget_parity_validation" in codes
    assert "missing_required_comparator_control" in codes


def test_render_repeated_sampling_baseline_boundary_summary_reports_shape():
    summary = render_repeated_sampling_baseline_boundary_summary(
        repeated_sampling_baseline_boundary_record()
    )

    assert "AlphaEvolve repeated-sampling baseline boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | runtime_absence_boundary_only |" in summary
    assert "| required_control_count | 11 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
