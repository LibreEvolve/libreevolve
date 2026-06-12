from libreevolve.problems.benchmarks.incorrect_suggestion_audit_boundary import (
    INCORRECT_SUGGESTION_AUDIT_BOUNDARY_SCHEMA,
    incorrect_suggestion_audit_boundary_record,
    render_incorrect_suggestion_audit_boundary_summary,
    validate_incorrect_suggestion_audit_boundary,
)


def test_incorrect_suggestion_audit_boundary_accepts_absence_record():
    boundary = incorrect_suggestion_audit_boundary_record()

    validation = validate_incorrect_suggestion_audit_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "local_execution_grounding_only"
    assert validation.required_evidence_field_count == 21
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == INCORRECT_SUGGESTION_AUDIT_BOUNDARY_SCHEMA
    assert "does not claim independent rejudge coverage" in boundary["claim_boundary"]


def test_incorrect_suggestion_audit_boundary_rejects_premature_publication_claim():
    boundary = incorrect_suggestion_audit_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "publication_strength_ready"
    boundary["missing_evidence"]["audited_false_acceptance_rate"] = "recorded"
    boundary["required_evidence_fields"] = ["generated_candidate_count"]

    validation = validate_incorrect_suggestion_audit_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_audited_false_acceptance_rate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_incorrect_suggestion_audit_boundary_summary_reports_shape():
    summary = render_incorrect_suggestion_audit_boundary_summary(
        incorrect_suggestion_audit_boundary_record()
    )

    assert "AlphaEvolve incorrect-suggestion audit boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | local_execution_grounding_only |" in summary
    assert "| required_evidence_field_count | 21 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
