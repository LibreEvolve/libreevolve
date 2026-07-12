from libreevolve.problems.benchmarks.evaluation_cascade_boundary import (
    EVALUATION_CASCADE_BOUNDARY_SCHEMA,
    evaluation_cascade_boundary_record,
    render_evaluation_cascade_boundary_summary,
    validate_evaluation_cascade_boundary,
)


def test_evaluation_cascade_boundary_accepts_absence_record():
    boundary = evaluation_cascade_boundary_record()

    validation = validate_evaluation_cascade_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "runtime_attrition_with_transition_linkage_without_benchmark_efficiency_evidence"
    )
    assert validation.required_evidence_field_count == 19
    assert boundary["stage_evidence_summary_schema"] == (
        "libreevolve.evaluation_cascade_stage_evidence_summary.v1"
    )
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == EVALUATION_CASCADE_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.4"]
    assert "does not claim AlphaEvolve-style cascade-efficiency evidence" in (
        boundary["claim_boundary"]
    )
    assert "candidate_stage_transition_id" in boundary["required_evidence_fields"]
    assert "transition_denominator_policy" in boundary["required_evidence_fields"]
    assert boundary["transition_matrix_schema"] == (
        "libreevolve.evaluation_cascade_transition_matrix.v1"
    )
    assert "runtime transition matrix" in boundary["claim_boundary"]
    assert "promotion-decision attribution" in boundary["claim_boundary"]


def test_evaluation_cascade_boundary_rejects_premature_efficiency_claim():
    boundary = evaluation_cascade_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "benchmark_efficiency_evidence_recorded"
    boundary["source_section_ids"] = ["2.3"]
    boundary["missing_evidence"]["wall_clock_cost_savings"] = "recorded"
    boundary["required_evidence_fields"] = ["stage_id"]

    validation = validate_evaluation_cascade_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_wall_clock_cost_savings" in codes
    assert "missing_required_evidence_field" in codes


def test_render_evaluation_cascade_boundary_summary_reports_shape():
    summary = render_evaluation_cascade_boundary_summary(
        evaluation_cascade_boundary_record()
    )

    assert "AlphaEvolve evaluation cascade boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | runtime_attrition_with_transition_linkage_without_benchmark_efficiency_evidence |"
        in summary
    )
    assert "| required_evidence_field_count | 19 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
