from libreevolve.problems.benchmarks.evaluator_oracle_boundary import (
    EVALUATOR_ORACLE_BOUNDARY_SCHEMA,
    evaluator_oracle_boundary_record,
    render_evaluator_oracle_boundary_summary,
    validate_evaluator_oracle_boundary,
)


def test_evaluator_oracle_boundary_accepts_absence_record():
    boundary = evaluator_oracle_boundary_record()

    validation = validate_evaluator_oracle_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "local_arbitration_without_independent_oracle_evidence"
    assert validation.required_evidence_field_count == 21
    assert validation.missing_evidence_count == 10
    assert boundary["schema"] == EVALUATOR_ORACLE_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.4"]
    assert "does not claim AlphaEvolve-style candidate-level oracle lineage" in (
        boundary["claim_boundary"]
    )
    assert "candidate_generation_ref" in boundary["required_evidence_fields"]
    assert "llm_feedback_separation_policy" in boundary["required_evidence_fields"]
    assert (
        boundary["missing_evidence"]["per_generation_feedback_trace"]
        == "not_recorded_as_independent_oracle_evidence"
    )
    assert "primary evaluator contract proof" in boundary["claim_boundary"]


def test_evaluator_oracle_boundary_rejects_premature_independence_claim():
    boundary = evaluator_oracle_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "independent_oracle_evidence_recorded"
    boundary["source_section_ids"] = ["2.3"]
    boundary["missing_evidence"]["independent_reference_oracle_records"] = "recorded"
    boundary["required_evidence_fields"] = ["evaluator_id"]

    validation = validate_evaluator_oracle_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_independent_reference_oracle_records" in codes
    assert "missing_required_evidence_field" in codes


def test_render_evaluator_oracle_boundary_summary_reports_shape():
    summary = render_evaluator_oracle_boundary_summary(
        evaluator_oracle_boundary_record()
    )

    assert "AlphaEvolve evaluator-oracle boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | local_arbitration_without_independent_oracle_evidence |" in summary
    assert "| required_evidence_field_count | 21 |" in summary
    assert "| missing_evidence_count | 10 |" in summary
