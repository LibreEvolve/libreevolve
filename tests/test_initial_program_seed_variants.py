from libreevolve.problems.benchmarks.initial_program_seed_variants import (
    INITIAL_PROGRAM_SEED_VARIANT_MATRIX_SCHEMA,
    initial_program_seed_variant_matrix_record,
    render_initial_program_seed_variant_matrix_summary,
    validate_initial_program_seed_variant_matrix,
)


def test_initial_program_seed_variant_matrix_accepts_design_boundary():
    matrix = initial_program_seed_variant_matrix_record()

    validation = validate_initial_program_seed_variant_matrix(matrix)

    assert validation.ok is True
    assert validation.matrix_status == "design_matrix_without_equal_budget_seed_results"
    assert validation.variant_count == 5
    assert validation.comparison_field_count == 12
    assert validation.missing_evidence_count == 11
    assert matrix["schema"] == INITIAL_PROGRAM_SEED_VARIANT_MATRIX_SCHEMA
    assert matrix["claim_ready"] is False
    assert "rendered_prompt_digest" in matrix["comparison_fields"]
    ids = [item["seed_variant_id"] for item in matrix["seed_variants"]]
    assert ids == [
        "simple_initial_program",
        "random_initial_program",
        "researcher_idea_initial_program",
        "stochastic_evaluation_idea",
        "evolutionary_approach_idea",
    ]
    assert "does not claim prompt context linkage" in matrix["claim_boundary"]


def test_initial_program_seed_variant_matrix_rejects_benchmark_overclaim():
    matrix = initial_program_seed_variant_matrix_record()
    matrix["claim_ready"] = True
    matrix["matrix_status"] = "equal_budget_seed_results_ready"
    matrix["missing_evidence"]["equal_budget_seed_variant_results"] = "recorded"
    matrix["missing_evidence"]["replicate_budget_protocol"] = "recorded"

    validation = validate_initial_program_seed_variant_matrix(matrix)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_matrix_status" in codes
    assert "invalid_missing_evidence_equal_budget_seed_variant_results" in codes
    assert "invalid_missing_evidence_replicate_budget_protocol" in codes


def test_initial_program_seed_variant_matrix_rejects_variant_drift():
    matrix = initial_program_seed_variant_matrix_record()
    matrix["seed_variants"][2]["paper_role"] = "ready"

    validation = validate_initial_program_seed_variant_matrix(matrix)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_researcher_idea_initial_program_paper_role" in codes


def test_render_initial_program_seed_variant_matrix_summary_reports_shape():
    summary = render_initial_program_seed_variant_matrix_summary(
        initial_program_seed_variant_matrix_record()
    )

    assert "Initial-program seed-variant matrix" in summary
    assert "| schema_status | ok |" in summary
    assert "| matrix_status | design_matrix_without_equal_budget_seed_results |" in summary
    assert "| variant_count | 5 |" in summary
    assert "| comparison_field_count | 12 |" in summary
