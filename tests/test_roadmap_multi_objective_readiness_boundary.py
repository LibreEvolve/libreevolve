from libreevolve.problems.benchmarks.roadmap_multi_objective_readiness_boundary import (
    ROADMAP_MULTI_OBJECTIVE_READINESS_BOUNDARY_SCHEMA,
    render_roadmap_multi_objective_readiness_boundary_summary,
    roadmap_multi_objective_readiness_boundary_record,
    validate_roadmap_multi_objective_readiness_boundary,
)


def test_roadmap_multi_objective_readiness_accepts_bounded_matrix():
    boundary = roadmap_multi_objective_readiness_boundary_record()

    validation = validate_roadmap_multi_objective_readiness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_multi_objective_readiness_matrix_without_primary_archive_gate"
    )
    assert boundary["schema"] == ROADMAP_MULTI_OBJECTIVE_READINESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_multi_objective_boundary_input"]
        == "papers/roadmap_multi_objective_search_boundary.json"
    )
    assert boundary["source_criterion_count"] == 8
    assert boundary["source_active_todo_ref_count"] == 16
    assert boundary["source_sidecar_ref_count"] == 10
    assert boundary["readiness_criterion_count"] == 8
    assert boundary["sidecar_ref_count"] == 16
    assert boundary["active_todo_ref_count"] == 16
    assert [record["criterion_id"] for record in boundary["readiness_criteria"]] == [
        "primary_archive_policy_matrix",
        "durable_metric_storage_policy",
        "sampling_balance_and_metric_policy",
        "descriptor_authority_and_rebin_semantics",
        "duplicate_work_memory_semantics",
        "metric_drilldown_and_cli_policy",
        "equal_budget_benchmark_evidence",
        "stale_readiness_and_owner_signoff",
    ]
    assert boundary["multi_objective_claim_guard_count"] == 8
    assert [
        record["criterion_id"] for record in boundary["multi_objective_claim_guard"]
    ] == [
        "primary_archive_policy_matrix",
        "durable_metric_storage_policy",
        "sampling_balance_and_metric_policy",
        "descriptor_authority_and_rebin_semantics",
        "duplicate_work_memory_semantics",
        "metric_drilldown_and_cli_policy",
        "equal_budget_benchmark_evidence",
        "stale_readiness_and_owner_signoff",
    ]
    assert all(
        "missing_before_parity_claim" in record
        for record in boundary["multi_objective_claim_guard"]
    )
    assert all(
        sidecar["exists"]
        for record in boundary["readiness_criteria"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in boundary["readiness_criteria"]
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
        "stale_readiness_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert (
        "does not claim primary Pareto/frontier archive replacement"
        in boundary["claim_boundary"]
    )
    assert "claim guard for each search surface" in boundary["claim_boundary"]
    assert "equal-budget multi-objective benchmarks" in boundary["claim_boundary"]
    assert "stale-readiness detector" in boundary["claim_boundary"]


def test_roadmap_multi_objective_readiness_rejects_overclaim_and_drift():
    boundary = roadmap_multi_objective_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_multi_objective_readiness_ready"
    boundary["readiness_criterion_count"] = 7
    boundary["source_criterion_count"] = 7
    boundary["readiness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["multi_objective_claim_guard_count"] = 0
    boundary["readiness_criteria"][0]["active_todo_refs"][0][
        "required_phrase_present"
    ] = False
    boundary["missing_evidence"][
        "primary_pareto_frontier_archive_replacement"
    ] = "recorded"
    boundary["required_evidence_fields"] = ["readiness_criteria"]

    validation = validate_roadmap_multi_objective_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_criterion_count" in codes
    assert "invalid_readiness_criterion_count" in codes
    assert "invalid_readiness_criteria" in codes
    assert "invalid_multi_objective_claim_guard_count" in codes
    assert (
        "invalid_missing_evidence_primary_pareto_frontier_archive_replacement"
        in codes
    )
    assert "missing_required_evidence_field" in codes
    assert "invalid_required_evidence_field_count" in codes


def test_render_roadmap_multi_objective_readiness_summary_reports_shape():
    summary = render_roadmap_multi_objective_readiness_boundary_summary(
        roadmap_multi_objective_readiness_boundary_record()
    )

    assert "ROADMAP multi objective readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_multi_objective_readiness_matrix_without_primary_archive_gate |"
        in summary
    )
    assert "| readiness_criterion_count | 8 |" in summary
    assert "| sidecar_ref_count | 16 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 12 |" in summary
