from libreevolve.problems.benchmarks.program_output_boundary import (
    PROGRAM_OUTPUT_BOUNDARY_SCHEMA,
    program_output_boundary_record,
    render_program_output_boundary_summary,
    validate_program_output_boundary,
)


def test_program_output_boundary_accepts_exact_current_run_lookup_boundary():
    boundary = program_output_boundary_record()

    validation = validate_program_output_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "exact_current_run_output_lookup_not_semantic_retrieval"
    assert validation.required_evidence_field_count == 16
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == PROGRAM_OUTPUT_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert "does not claim durable output query tables" in boundary["claim_boundary"]


def test_program_output_boundary_rejects_semantic_output_overclaim():
    boundary = program_output_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "semantic_output_retrieval_ready"
    boundary["missing_evidence"]["semantic_output_similarity_search"] = "recorded"
    boundary["required_evidence_fields"] = ["runtime_program_output_index"]

    validation = validate_program_output_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_missing_evidence_semantic_output_similarity_search" in codes
    assert "missing_required_evidence_field" in codes


def test_render_program_output_boundary_summary_reports_shape():
    summary = render_program_output_boundary_summary(
        program_output_boundary_record()
    )

    assert "Program output boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | exact_current_run_output_lookup_not_semantic_retrieval |" in summary
    assert "| required_evidence_field_count | 16 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
