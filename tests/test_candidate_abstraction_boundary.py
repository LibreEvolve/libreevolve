from libreevolve.problems.benchmarks.candidate_abstraction import (
    CANDIDATE_ABSTRACTION_BOUNDARY_SCHEMA,
    candidate_abstraction_boundary_record,
    render_candidate_abstraction_boundary_summary,
    validate_candidate_abstraction_boundary,
)


def test_candidate_abstraction_boundary_accepts_absence_record():
    boundary = candidate_abstraction_boundary_record()

    validation = validate_candidate_abstraction_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == "not_configured_as_problem_defined_abstractions"
    assert validation.selected_abstraction == "code_file_set"
    assert validation.abstraction_option_count == 4
    assert validation.required_evidence_field_count == 10
    assert validation.missing_evidence_count == 6
    assert boundary["schema"] == CANDIDATE_ABSTRACTION_BOUNDARY_SCHEMA
    assert boundary["source_section_ids"] == ["2.1", "Discussion"]
    assert "does not claim AlphaEvolve-style problem-defined candidate abstractions" in (
        boundary["claim_boundary"]
    )


def test_candidate_abstraction_boundary_rejects_premature_parity_claim():
    boundary = candidate_abstraction_boundary_record()
    boundary["claim_ready"] = True
    boundary["selected_abstraction"] = "constructor_function"
    boundary["source_section_ids"] = ["2.1"]
    boundary["abstraction_options"][1]["typed_abstraction_api"] = "configured"
    boundary["abstraction_options"][1]["bias_evidence"] = "recorded"
    boundary["missing_evidence"]["benchmark_bias_report"] = "recorded"

    validation = validate_candidate_abstraction_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_selected_abstraction" in codes
    assert "invalid_source_section_ids" in codes
    assert "typed_abstraction_api_overclaim" in codes
    assert "bias_evidence_overclaim" in codes
    assert "invalid_missing_evidence_benchmark_bias_report" in codes


def test_render_candidate_abstraction_boundary_summary_reports_shape():
    summary = render_candidate_abstraction_boundary_summary(
        candidate_abstraction_boundary_record()
    )

    assert "AlphaEvolve candidate-abstraction boundary" in summary
    assert "| schema_status | ok |" in summary
    assert "| boundary_status | not_configured_as_problem_defined_abstractions |" in summary
    assert "| selected_abstraction | code_file_set |" in summary
    assert "| abstraction_option_count | 4 |" in summary
