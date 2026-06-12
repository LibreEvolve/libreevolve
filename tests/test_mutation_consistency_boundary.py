from libreevolve.problems.benchmarks.mutation_consistency_boundary import (
    MUTATION_CONSISTENCY_BOUNDARY_SCHEMA,
    mutation_consistency_boundary_record,
    render_mutation_consistency_boundary_summary,
    validate_mutation_consistency_boundary,
)


def test_mutation_consistency_boundary_accepts_diagnostic_scan_boundary():
    boundary = mutation_consistency_boundary_record()

    validation = validate_mutation_consistency_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "diagnostic_multi_edit_consistency_scan_only"
    assert validation.required_evidence_field_count == 15
    assert validation.missing_evidence_count == 7
    assert boundary["schema"] == MUTATION_CONSISTENCY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        "does not claim language-aware scope resolution"
        in boundary["claim_boundary"]
    )


def test_mutation_consistency_boundary_rejects_semantic_proof_overclaim():
    boundary = mutation_consistency_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "semantic_multi_edit_consistency_proven"
    boundary["missing_evidence"]["required_companion_edit_inference"] = "recorded"
    boundary["required_evidence_fields"] = ["multi_edit_candidate_inventory"]

    validation = validate_mutation_consistency_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert (
        "invalid_missing_evidence_required_companion_edit_inference"
        in codes
    )
    assert "missing_required_evidence_field" in codes


def test_render_mutation_consistency_boundary_summary_reports_shape():
    summary = render_mutation_consistency_boundary_summary(
        mutation_consistency_boundary_record()
    )

    assert "Mutation consistency boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | diagnostic_multi_edit_consistency_scan_only |" in summary
    assert "| required_evidence_field_count | 15 |" in summary
    assert "| missing_evidence_count | 7 |" in summary
