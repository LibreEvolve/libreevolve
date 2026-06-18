from libreevolve.problems.benchmarks.roadmap_evaluation_cascade_readiness_boundary import (
    ROADMAP_EVALUATION_CASCADE_READINESS_BOUNDARY_SCHEMA,
    render_roadmap_evaluation_cascade_readiness_boundary_summary,
    roadmap_evaluation_cascade_readiness_boundary_record,
    validate_roadmap_evaluation_cascade_readiness_boundary,
)


def test_roadmap_evaluation_cascade_readiness_accepts_bounded_matrix():
    boundary = roadmap_evaluation_cascade_readiness_boundary_record()

    validation = validate_roadmap_evaluation_cascade_readiness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_evaluation_cascade_readiness_matrix_without_alphaevolve_cascade_gate"
    )
    assert boundary["schema"] == ROADMAP_EVALUATION_CASCADE_READINESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_cascade_boundary_input"]
        == "papers/roadmap_evaluation_cascade_boundary.json"
    )
    assert boundary["source_criterion_count"] == 10
    assert boundary["source_active_todo_ref_count"] == 20
    assert boundary["source_sidecar_ref_count"] == 16
    assert boundary["readiness_criterion_count"] == 8
    assert boundary["sidecar_ref_count"] == 16
    assert boundary["active_todo_ref_count"] == 16
    assert [record["criterion_id"] for record in boundary["readiness_criteria"]] == [
        "validator_authority_matrix",
        "artifact_and_budget_sufficiency",
        "feedback_and_statistical_promotion",
        "oracle_and_workload_contracts",
        "automated_environment_and_sandbox",
        "release_environment_reproducibility",
        "benchmark_sufficiency_signoff",
        "stale_readiness_and_owner_signoff",
    ]
    assert boundary["evaluation_cascade_claim_guard_count"] == 8
    assert [
        record["criterion_id"] for record in boundary["evaluation_cascade_claim_guard"]
    ] == [
        "validator_authority_matrix",
        "artifact_and_budget_sufficiency",
        "feedback_and_statistical_promotion",
        "oracle_and_workload_contracts",
        "automated_environment_and_sandbox",
        "release_environment_reproducibility",
        "benchmark_sufficiency_signoff",
        "stale_readiness_and_owner_signoff",
    ]
    assert all(
        "missing_before_parity_claim" in record
        for record in boundary["evaluation_cascade_claim_guard"]
    )
    assert all(
        sidecar["exists"]
        for record in boundary["readiness_criteria"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        todo_ref["exists"] and todo_ref["required_phrase_present"]
        for record in boundary["readiness_criteria"]
        for todo_ref in record["active_todo_refs"]
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
        "stale_readiness_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim a validator-authority matrix" in boundary["claim_boundary"]
    assert "claim guard for each cascade surface" in boundary["claim_boundary"]


def test_roadmap_evaluation_cascade_readiness_rejects_overclaim_and_drift():
    boundary = roadmap_evaluation_cascade_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "alphaevolve_cascade_ready"
    boundary["readiness_criterion_count"] = 0
    boundary["readiness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["evaluation_cascade_claim_guard_count"] = 0
    boundary["missing_evidence"]["benchmark_calibrated_statistical_promotion"] = "recorded"
    boundary["required_evidence_fields"] = ["validator_authority_matrix"]

    validation = validate_roadmap_evaluation_cascade_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readiness_criterion_count" in codes
    assert "invalid_readiness_criteria" in codes
    assert "invalid_evaluation_cascade_claim_guard_count" in codes
    assert "invalid_missing_evidence_benchmark_calibrated_statistical_promotion" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_evaluation_cascade_readiness_summary_reports_shape():
    summary = render_roadmap_evaluation_cascade_readiness_boundary_summary(
        roadmap_evaluation_cascade_readiness_boundary_record()
    )

    assert "ROADMAP evaluation cascade readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_evaluation_cascade_readiness_matrix_without_alphaevolve_cascade_gate |"
        in summary
    )
    assert "| readiness_criterion_count | 8 |" in summary
    assert "| sidecar_ref_count | 16 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 13 |" in summary
