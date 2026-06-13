from libreevolve.problems.benchmarks.proposal_lifecycle_audit import (
    PROPOSAL_LIFECYCLE_AUDIT_BOUNDARY_SCHEMA,
    proposal_lifecycle_audit_boundary_record,
    render_proposal_lifecycle_audit_boundary_summary,
    validate_proposal_lifecycle_audit_boundary,
)


def test_proposal_lifecycle_audit_boundary_accepts_absence_record():
    boundary = proposal_lifecycle_audit_boundary_record()

    validation = validate_proposal_lifecycle_audit_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "not_independently_audited"
    assert validation.required_evidence_field_count == 18
    assert validation.missing_evidence_count == 11
    assert boundary["schema"] == PROPOSAL_LIFECYCLE_AUDIT_BOUNDARY_SCHEMA
    assert "does not claim independent rejudge" in boundary["claim_boundary"]
    assert "candidate_family_label" in boundary["required_evidence_fields"]
    assert "audit_denominator" in boundary["required_evidence_fields"]
    assert (
        boundary["missing_evidence"]["beyond_initial_pool_novelty_audit"]
        == "not_recorded_locally"
    )
    assert "candidate-family filter rates" in boundary["claim_boundary"]


def test_proposal_lifecycle_audit_boundary_rejects_premature_audit_claim():
    boundary = proposal_lifecycle_audit_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "independently_audited"
    boundary["missing_evidence"]["audited_false_acceptance_rate"] = "recorded"
    boundary["required_evidence_fields"] = ["proposal_id"]

    validation = validate_proposal_lifecycle_audit_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_audited_false_acceptance_rate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_proposal_lifecycle_audit_boundary_summary_reports_shape():
    summary = render_proposal_lifecycle_audit_boundary_summary(
        proposal_lifecycle_audit_boundary_record()
    )

    assert "AlphaEvolve proposal lifecycle audit boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | not_independently_audited |" in summary
    assert "| required_evidence_field_count | 18 |" in summary
    assert "| missing_evidence_count | 11 |" in summary
