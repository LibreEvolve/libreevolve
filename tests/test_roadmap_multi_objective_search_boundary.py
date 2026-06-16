from libreevolve.problems.benchmarks.roadmap_multi_objective_search_boundary import (
    ROADMAP_MULTI_OBJECTIVE_SEARCH_BOUNDARY_SCHEMA,
    render_roadmap_multi_objective_search_boundary_summary,
    roadmap_multi_objective_search_boundary_record,
    validate_roadmap_multi_objective_search_boundary,
)


def test_roadmap_multi_objective_search_accepts_bounded_criteria_map():
    boundary = roadmap_multi_objective_search_boundary_record()

    validation = validate_roadmap_multi_objective_search_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_multi_objective_search_matrix_without_primary_archive_readiness"
    )
    assert boundary["schema"] == ROADMAP_MULTI_OBJECTIVE_SEARCH_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["roadmap_heading_present"] is True
    assert boundary["criterion_count"] == 8
    assert boundary["active_todo_ref_count"] == 16
    assert boundary["sidecar_ref_count"] == 10
    assert [record["criterion_id"] for record in boundary["criterion_records"]] == [
        "paper_metric_bundles",
        "objective_archive_policy",
        "metric_diverse_sampling_balance",
        "duplicate_work_memory",
        "descriptor_authority",
        "map_elites_illumination",
        "metric_specific_drilldowns",
        "benchmark_comparison_evidence",
    ]
    assert all(record["roadmap_phrase_present"] for record in boundary["criterion_records"])
    assert all(
        sidecar["exists"]
        for record in boundary["criterion_records"]
        for sidecar in record["current_sidecar_refs"]
    )
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in boundary["criterion_records"]
        for ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "primary_pareto_frontier_archive_replacement": "not_recorded_locally",
        "durable_cross_run_metric_database": "not_recorded_locally",
        "calibrated_parent_inspiration_balance": "not_recorded_locally",
        "stable_behavior_descriptor_contracts": "not_recorded_locally",
        "learned_or_evaluator_descriptor_models": "not_recorded_locally",
        "tested_archive_rebin_semantics": "not_recorded_locally",
        "durable_duplicate_work_memory": "not_recorded_locally",
        "semantic_near_duplicate_detection": "not_recorded_locally",
        "metric_specific_cli_drilldowns": "not_recorded_locally",
        "equal_budget_multi_objective_benchmarks": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim primary Pareto/frontier archive replacement" in boundary["claim_boundary"]


def test_roadmap_multi_objective_search_rejects_overclaim_and_drift():
    boundary = roadmap_multi_objective_search_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_multi_objective_search_ready"
    boundary["criterion_count"] = 7
    boundary["criterion_records"][0]["roadmap_phrase_present"] = False
    boundary["missing_evidence"]["primary_pareto_frontier_archive_replacement"] = "recorded"
    boundary["required_evidence_fields"] = ["criterion_records"]

    validation = validate_roadmap_multi_objective_search_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_criterion_count" in codes
    assert "invalid_criterion_records" in codes
    assert "invalid_missing_evidence_primary_pareto_frontier_archive_replacement" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_multi_objective_search_summary_reports_shape():
    summary = render_roadmap_multi_objective_search_boundary_summary(
        roadmap_multi_objective_search_boundary_record()
    )

    assert "ROADMAP multi objective search boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_multi_objective_search_matrix_without_primary_archive_readiness |"
        in summary
    )
    assert "| criterion_count | 8 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 11 |" in summary
