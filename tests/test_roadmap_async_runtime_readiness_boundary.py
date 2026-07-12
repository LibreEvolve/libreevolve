from libreevolve.problems.benchmarks.roadmap_async_runtime_readiness_boundary import (
    ROADMAP_ASYNC_RUNTIME_READINESS_BOUNDARY_SCHEMA,
    render_roadmap_async_runtime_readiness_boundary_summary,
    roadmap_async_runtime_readiness_boundary_record,
    validate_roadmap_async_runtime_readiness_boundary,
)


def test_roadmap_async_runtime_readiness_accepts_bounded_matrix():
    boundary = roadmap_async_runtime_readiness_boundary_record()

    validation = validate_roadmap_async_runtime_readiness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_async_runtime_readiness_matrix_without_full_replay_gate"
    )
    assert boundary["schema"] == ROADMAP_ASYNC_RUNTIME_READINESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_async_boundary_input"]
        == "papers/roadmap_async_resumable_runtime_boundary.json"
    )
    assert boundary["source_criterion_count"] == 9
    assert boundary["source_active_todo_ref_count"] == 18
    assert boundary["source_sidecar_ref_count"] == 16
    assert boundary["readiness_criterion_count"] == 8
    assert boundary["sidecar_ref_count"] == 16
    assert boundary["active_todo_ref_count"] == 16
    assert [record["criterion_id"] for record in boundary["readiness_criteria"]] == [
        "async_state_inventory",
        "replay_resume_acceptance_checklist",
        "controller_sampler_task_checkpoints",
        "evaluator_pending_work_and_merge_order",
        "archive_migration_restore_engine",
        "provider_plugin_replay_policy",
        "async_budget_environment_replay",
        "stale_readiness_and_owner_signoff",
    ]
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
        "async_state_inventory": "not_recorded_locally",
        "replay_resume_acceptance_checklist": "not_recorded_locally",
        "controller_queue_checkpoint": "not_recorded_locally",
        "llm_sampler_task_state": "not_recorded_locally",
        "evaluator_pending_work_state": "not_recorded_locally",
        "deterministic_async_merge_admission_replay": "not_recorded_locally",
        "ordered_migration_restore_engine": "not_recorded_locally",
        "provider_output_replay": "not_recorded_locally",
        "plugin_rng_replay": "not_recorded_locally",
        "async_budget_accounting": "not_recorded_locally",
        "external_environment_replay": "not_recorded_locally",
        "end_to_end_resumed_trace_proof": "not_recorded_locally",
        "stale_readiness_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim an async-state inventory" in boundary["claim_boundary"]


def test_roadmap_async_runtime_readiness_rejects_overclaim_and_drift():
    boundary = roadmap_async_runtime_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_replay_ready"
    boundary["readiness_criterion_count"] = 0
    boundary["readiness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["missing_evidence"]["async_state_inventory"] = "recorded"
    boundary["required_evidence_fields"] = ["async_state_inventory"]

    validation = validate_roadmap_async_runtime_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readiness_criterion_count" in codes
    assert "invalid_readiness_criteria" in codes
    assert "invalid_missing_evidence_async_state_inventory" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_async_runtime_readiness_summary_reports_shape():
    summary = render_roadmap_async_runtime_readiness_boundary_summary(
        roadmap_async_runtime_readiness_boundary_record()
    )

    assert "ROADMAP async runtime readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_async_runtime_readiness_matrix_without_full_replay_gate |"
        in summary
    )
    assert "| readiness_criterion_count | 8 |" in summary
    assert "| sidecar_ref_count | 16 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 14 |" in summary
