from libreevolve.problems.benchmarks.proposal_score_boundary import (
    PROPOSAL_SCORE_BOUNDARY_SCHEMA,
    proposal_score_boundary_record,
    render_proposal_score_boundary_summary,
    validate_proposal_score_boundary,
)


def test_proposal_score_boundary_accepts_current_run_score_boundary():
    boundary = proposal_score_boundary_record()

    validation = validate_proposal_score_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_current_run_scores_and_lexical_families_not_semantic_idea_memory"
    )
    assert validation.required_evidence_field_count == 17
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == PROPOSAL_SCORE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        "does not claim semantic or embedding-backed proposal retrieval"
        in boundary["claim_boundary"]
    )


def test_proposal_score_boundary_rejects_semantic_memory_overclaim():
    boundary = proposal_score_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "semantic_idea_memory_ready"
    boundary["missing_evidence"]["semantic_embedding_proposal_index"] = "recorded"
    boundary["required_evidence_fields"] = ["versioned_proposal_score_records"]

    validation = validate_proposal_score_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_semantic_embedding_proposal_index" in codes
    assert "missing_required_evidence_field" in codes


def test_render_proposal_score_boundary_summary_reports_shape():
    summary = render_proposal_score_boundary_summary(proposal_score_boundary_record())

    assert "Proposal score boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_current_run_scores_and_lexical_families_not_semantic_idea_memory |"
        in summary
    )
    assert "| required_evidence_field_count | 17 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
