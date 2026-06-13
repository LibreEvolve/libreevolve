from libreevolve.problems.benchmarks.proposal_diversity_boundary import (
    PROPOSAL_DIVERSITY_BOUNDARY_SCHEMA,
    proposal_diversity_boundary_record,
    render_proposal_diversity_boundary_summary,
    validate_proposal_diversity_boundary,
)


def test_proposal_diversity_boundary_accepts_absence_record():
    boundary = proposal_diversity_boundary_record()

    validation = validate_proposal_diversity_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "exact_text_diversity_without_semantic_novelty"
    assert validation.required_evidence_field_count == 14
    assert validation.missing_evidence_count == 10
    assert boundary["schema"] == PROPOSAL_DIVERSITY_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.3", "4"]
    assert "exact_proposal_hashes" in boundary["current_evidence_fields"]
    assert "does not claim semantic proposal diversity" in boundary["claim_boundary"]


def test_proposal_diversity_boundary_rejects_premature_semantic_claim():
    boundary = proposal_diversity_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "semantic_proposal_diversity_ready"
    boundary["source_section_ids"] = ["2.3"]
    boundary["missing_evidence"]["near_duplicate_detection"] = "recorded"
    boundary["required_evidence_fields"] = ["runtime_report_schema"]

    validation = validate_proposal_diversity_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_near_duplicate_detection" in codes
    assert "missing_required_evidence_field" in codes


def test_render_proposal_diversity_boundary_summary_reports_shape():
    summary = render_proposal_diversity_boundary_summary(
        proposal_diversity_boundary_record()
    )

    assert "AlphaEvolve proposal-diversity boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | exact_text_diversity_without_semantic_novelty |" in summary
    assert "| required_evidence_field_count | 14 |" in summary
    assert "| missing_evidence_count | 10 |" in summary
