from libreevolve.problems.benchmarks.global_nlp_optimization_boundary import (
    GLOBAL_NLP_OPTIMIZATION_BOUNDARY_SCHEMA,
    global_nlp_optimization_boundary_record,
    render_global_nlp_optimization_boundary_summary,
    validate_global_nlp_optimization_boundary,
)


def test_global_nlp_optimization_boundary_accepts_absence_record():
    boundary = global_nlp_optimization_boundary_record()

    validation = validate_global_nlp_optimization_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == (
        "global_nlp_comparator_without_local_solver_harness"
    )
    assert validation.component_count == 14
    assert validation.required_evidence_field_count == 24
    assert validation.missing_evidence_count == 20
    assert boundary["schema"] == GLOBAL_NLP_OPTIMIZATION_BOUNDARY_SCHEMA
    assert boundary["source_version"] == "v2"
    assert boundary["source_last_revised_date"] == "2026-01-15"
    assert boundary["local_evidence"]["xpress_runner_ready"] is False
    assert len(boundary["reported_result"]["table1_rows"]) == 5
    assert len(boundary["reported_result"]["table2_rows"]) == 3
    assert len(boundary["reported_result"]["table3_rows"]) == 5
    assert "does not claim NLP formulation schemas" in boundary["claim_boundary"]


def test_global_nlp_optimization_boundary_rejects_premature_runtime_claims():
    boundary = global_nlp_optimization_boundary_record()
    boundary["claim_ready"] = True
    boundary["source_links"][6]["status"] = "verified_local_solver"
    boundary["framework_components"][7]["local_status"] = "implemented"
    boundary["local_evidence"]["xpress_runner_ready"] = True
    boundary["local_evidence"]["repository_runtime_verified"] = True
    boundary["reported_result"]["modeling_language"] = "AMPL"
    boundary["reported_result"]["table3_rows"].pop()
    boundary["missing_evidence"]["xpress_global_solver_runner"] = "implemented"

    validation = validate_global_nlp_optimization_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "source_link_status_overclaim" in codes
    assert "framework_component_overclaim" in codes
    assert "local_evidence_xpress_runner_ready_overclaim" in codes
    assert "local_evidence_repository_runtime_verified_overclaim" in codes
    assert "reported_result_modeling_language_mismatch" in codes
    assert "reported_result_table3_rows_mismatch" in codes
    assert "missing_evidence_mismatch" in codes


def test_render_global_nlp_optimization_boundary_summary_reports_shape():
    summary = render_global_nlp_optimization_boundary_summary(
        global_nlp_optimization_boundary_record()
    )

    assert "Global NLP Optimization boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | global_nlp_comparator_without_local_solver_harness |"
        in summary
    )
    assert "| component_count | 14 |" in summary
