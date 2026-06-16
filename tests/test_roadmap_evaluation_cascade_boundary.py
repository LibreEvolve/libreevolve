from libreevolve.problems.benchmarks.roadmap_evaluation_cascade_boundary import (
    ROADMAP_EVALUATION_CASCADE_BOUNDARY_SCHEMA,
    render_roadmap_evaluation_cascade_boundary_summary,
    roadmap_evaluation_cascade_boundary_record,
    validate_roadmap_evaluation_cascade_boundary,
)


def test_roadmap_evaluation_cascade_accepts_bounded_criteria_map():
    boundary = roadmap_evaluation_cascade_boundary_record()

    validation = validate_roadmap_evaluation_cascade_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_evaluation_cascade_matrix_without_alphaevolve_cascade_readiness"
    )
    assert boundary["schema"] == ROADMAP_EVALUATION_CASCADE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["roadmap_heading_present"] is True
    assert boundary["criterion_count"] == 10
    assert boundary["active_todo_ref_count"] == 20
    assert boundary["sidecar_ref_count"] == 16
    assert [record["criterion_id"] for record in boundary["criterion_records"]] == [
        "cascade_transition_artifacts",
        "artifact_schema_hash_coverage",
        "budget_ownership",
        "feedback_calibration",
        "statistical_promotion_policy",
        "oracle_independence",
        "workload_execution_contract",
        "automated_scope_programmatic_boundary",
        "validator_sandbox_dependency_boundary",
        "environment_release_reproducibility",
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
        "validator_authority_matrix": "not_recorded_locally",
        "complete_artifact_schema_hash_coverage": "not_recorded_locally",
        "accelerator_async_budget_ownership": "not_recorded_locally",
        "executed_feedback_calibration": "not_recorded_locally",
        "benchmark_calibrated_statistical_promotion": "not_recorded_locally",
        "independent_oracle_disagreement_records": "not_recorded_locally",
        "workload_specific_execution_contracts": "not_recorded_locally",
        "robust_automated_environment_fixtures": "not_recorded_locally",
        "os_container_resource_sandbox": "not_recorded_locally",
        "replayable_environment_release_bundle": "not_recorded_locally",
        "benchmark_sufficiency_signoff": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim a validator-authority matrix" in boundary["claim_boundary"]


def test_roadmap_evaluation_cascade_rejects_overclaim_and_drift():
    boundary = roadmap_evaluation_cascade_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_alphaevolve_cascade_ready"
    boundary["criterion_count"] = 9
    boundary["criterion_records"][0]["roadmap_phrase_present"] = False
    boundary["missing_evidence"]["benchmark_calibrated_statistical_promotion"] = "recorded"
    boundary["required_evidence_fields"] = ["criterion_records"]

    validation = validate_roadmap_evaluation_cascade_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_criterion_count" in codes
    assert "invalid_criterion_records" in codes
    assert "invalid_missing_evidence_benchmark_calibrated_statistical_promotion" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_evaluation_cascade_summary_reports_shape():
    summary = render_roadmap_evaluation_cascade_boundary_summary(
        roadmap_evaluation_cascade_boundary_record()
    )

    assert "ROADMAP evaluation cascade boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_evaluation_cascade_matrix_without_alphaevolve_cascade_readiness |"
        in summary
    )
    assert "| criterion_count | 10 |" in summary
    assert "| active_todo_ref_count | 20 |" in summary
    assert "| missing_evidence_count | 12 |" in summary
