from libreevolve.problems.benchmarks.cascade_hypothesis_test_boundary import (
    CASCADE_HYPOTHESIS_TEST_BOUNDARY_SCHEMA,
    cascade_hypothesis_test_boundary_record,
    render_cascade_hypothesis_test_boundary_summary,
    validate_cascade_hypothesis_test_boundary,
)


def test_cascade_hypothesis_test_boundary_accepts_runtime_policy_boundary():
    boundary = cascade_hypothesis_test_boundary_record()

    validation = validate_cascade_hypothesis_test_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "runtime_policy_gates_without_benchmark_calibrated_fixtures"
    )
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 5
    assert boundary["schema"] == CASCADE_HYPOTHESIS_TEST_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim benchmark-calibrated thresholds" in boundary["claim_boundary"]


def test_cascade_hypothesis_test_boundary_rejects_benchmark_ready_overclaim():
    boundary = cascade_hypothesis_test_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "benchmark_calibrated_hypothesis_cascade_ready"
    boundary["missing_evidence"]["benchmark_calibrated_thresholds"] = "recorded"
    boundary["required_evidence_fields"] = ["confidence_bound_evidence"]

    validation = validate_cascade_hypothesis_test_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_benchmark_calibrated_thresholds" in codes
    assert "missing_required_evidence_field" in codes


def test_render_cascade_hypothesis_test_boundary_summary_reports_shape():
    summary = render_cascade_hypothesis_test_boundary_summary(
        cascade_hypothesis_test_boundary_record()
    )

    assert "Cascade hypothesis-test boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | runtime_policy_gates_without_benchmark_calibrated_fixtures |"
        in summary
    )
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
