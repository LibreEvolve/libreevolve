from libreevolve.problems.benchmarks.candidate_abstraction_bias import (
    CANDIDATE_ABSTRACTION_BIAS_MATRIX_SCHEMA,
    candidate_abstraction_bias_matrix_record,
    render_candidate_abstraction_bias_matrix_summary,
    validate_candidate_abstraction_bias_matrix,
)


def test_candidate_abstraction_bias_matrix_accepts_design_boundary():
    matrix = candidate_abstraction_bias_matrix_record()

    validation = validate_candidate_abstraction_bias_matrix(matrix)

    assert validation.ok is True
    assert validation.matrix_status == "design_matrix_without_executed_bias_benchmarks"
    assert validation.abstraction_count == 4
    assert validation.comparison_field_count == 8
    assert validation.missing_evidence_count == 5
    assert matrix["schema"] == CANDIDATE_ABSTRACTION_BIAS_MATRIX_SCHEMA
    assert matrix["claim_ready"] is False
    ids = [item["abstraction_id"] for item in matrix["abstraction_families"]]
    assert ids == [
        "direct_solution",
        "constructor_function",
        "bespoke_search_algorithm",
        "coevolved_solution_and_search",
    ]
    assert "does not claim problem-defined abstraction hooks" in matrix["claim_boundary"]


def test_candidate_abstraction_bias_matrix_rejects_benchmark_overclaim():
    matrix = candidate_abstraction_bias_matrix_record()
    matrix["claim_ready"] = True
    matrix["matrix_status"] = "executed_bias_benchmarks_ready"
    matrix["missing_evidence"]["executed_equal_budget_bias_benchmarks"] = "recorded"

    validation = validate_candidate_abstraction_bias_matrix(matrix)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_matrix_status" in codes
    assert "invalid_missing_evidence_executed_equal_budget_bias_benchmarks" in codes


def test_candidate_abstraction_bias_matrix_rejects_family_drift():
    matrix = candidate_abstraction_bias_matrix_record()
    matrix["abstraction_families"][1]["symmetry_structure_assumption"] = "unknown"

    validation = validate_candidate_abstraction_bias_matrix(matrix)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_constructor_function_symmetry_structure_assumption" in codes


def test_render_candidate_abstraction_bias_matrix_summary_reports_shape():
    summary = render_candidate_abstraction_bias_matrix_summary(
        candidate_abstraction_bias_matrix_record()
    )

    assert "Candidate abstraction bias matrix" in summary
    assert "| schema_status | ok |" in summary
    assert "| matrix_status | design_matrix_without_executed_bias_benchmarks |" in summary
    assert "| abstraction_count | 4 |" in summary
    assert "| comparison_field_count | 8 |" in summary
