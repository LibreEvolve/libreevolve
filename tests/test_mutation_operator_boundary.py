from libreevolve.problems.benchmarks.mutation_operator_boundary import (
    MUTATION_OPERATOR_BOUNDARY_SCHEMA,
    mutation_operator_boundary_record,
    render_mutation_operator_boundary_summary,
    validate_mutation_operator_boundary,
)


def test_mutation_operator_boundary_accepts_absence_record():
    boundary = mutation_operator_boundary_record()

    validation = validate_mutation_operator_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "fixed_edit_payload_grammar_without_operator_family_evidence"
    )
    assert validation.required_evidence_field_count == 12
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == MUTATION_OPERATOR_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.3", "5"]
    assert "search_replace_diff" in boundary["fixed_local_parser_surfaces"]
    assert "does not claim proposal-level operator-family provenance" in (
        boundary["claim_boundary"]
    )


def test_mutation_operator_boundary_rejects_premature_operator_claim():
    boundary = mutation_operator_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "operator_family_evidence_ready"
    boundary["source_section_ids"] = ["2.3"]
    boundary["missing_evidence"]["operator_family_scoring"] = "recorded"
    boundary["required_evidence_fields"] = ["runtime_report_schema"]

    validation = validate_mutation_operator_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_section_ids" in codes
    assert "invalid_missing_evidence_operator_family_scoring" in codes
    assert "missing_required_evidence_field" in codes


def test_render_mutation_operator_boundary_summary_reports_shape():
    summary = render_mutation_operator_boundary_summary(mutation_operator_boundary_record())

    assert "AlphaEvolve mutation-operator boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | fixed_edit_payload_grammar_without_operator_family_evidence |"
        in summary
    )
    assert "| required_evidence_field_count | 12 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
