from libreevolve.problems.benchmarks.roadmap_async_resumable_runtime_boundary import (
    ROADMAP_ASYNC_RESUMABLE_RUNTIME_BOUNDARY_SCHEMA,
    render_roadmap_async_resumable_runtime_boundary_summary,
    roadmap_async_resumable_runtime_boundary_record,
    validate_roadmap_async_resumable_runtime_boundary,
)


def test_roadmap_async_resumable_runtime_accepts_bounded_criteria_map():
    boundary = roadmap_async_resumable_runtime_boundary_record()

    validation = validate_roadmap_async_resumable_runtime_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_async_resumable_runtime_matrix_without_full_replay_readiness"
    )
    assert boundary["schema"] == ROADMAP_ASYNC_RESUMABLE_RUNTIME_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["roadmap_heading_present"] is True
    assert boundary["criterion_count"] == 9
    assert boundary["active_todo_ref_count"] == 18
    assert boundary["sidecar_ref_count"] == 16
    assert [record["criterion_id"] for record in boundary["criterion_records"]] == [
        "distributed_pipeline_topology",
        "parallel_evaluation_throughput",
        "controller_pending_work_resume",
        "archive_event_replay",
        "rng_lineage_replay",
        "provider_plugin_nondeterminism",
        "budget_resume_accounting",
        "environment_replay",
        "resumed_trace_proof",
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
        "async_state_inventory": "not_recorded_locally",
        "replay_resume_acceptance_checklist": "not_recorded_locally",
        "controller_queue_checkpoints": "not_recorded_locally",
        "llm_sampler_task_state": "not_recorded_locally",
        "evaluator_worker_pending_state": "not_recorded_locally",
        "deterministic_async_merge_admission_replay": "not_recorded_locally",
        "ordered_migration_restore_engine": "not_recorded_locally",
        "provider_output_replay": "not_recorded_locally",
        "plugin_rng_replay": "not_recorded_locally",
        "async_budget_accounting": "not_recorded_locally",
        "external_environment_replay": "not_recorded_locally",
        "end_to_end_resumed_trace_proof": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim an async-state inventory" in boundary["claim_boundary"]


def test_roadmap_async_resumable_runtime_rejects_overclaim_and_drift():
    boundary = roadmap_async_resumable_runtime_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_async_replay_ready"
    boundary["criterion_count"] = 8
    boundary["criterion_records"][0]["roadmap_phrase_present"] = False
    boundary["missing_evidence"]["async_state_inventory"] = "recorded"
    boundary["required_evidence_fields"] = ["criterion_records"]

    validation = validate_roadmap_async_resumable_runtime_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_criterion_count" in codes
    assert "invalid_criterion_records" in codes
    assert "invalid_missing_evidence_async_state_inventory" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_async_resumable_runtime_summary_reports_shape():
    summary = render_roadmap_async_resumable_runtime_boundary_summary(
        roadmap_async_resumable_runtime_boundary_record()
    )

    assert "ROADMAP async resumable runtime boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_async_resumable_runtime_matrix_without_full_replay_readiness |"
        in summary
    )
    assert "| criterion_count | 9 |" in summary
    assert "| active_todo_ref_count | 18 |" in summary
    assert "| missing_evidence_count | 13 |" in summary
