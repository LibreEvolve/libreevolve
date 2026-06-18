from libreevolve.problems.benchmarks.roadmap_backend_scheduling_critique_boundary import (
    ROADMAP_BACKEND_SCHEDULING_CRITIQUE_BOUNDARY_SCHEMA,
    render_roadmap_backend_scheduling_critique_boundary_summary,
    roadmap_backend_scheduling_critique_boundary_record,
    validate_roadmap_backend_scheduling_critique_boundary,
)


def test_roadmap_backend_scheduling_critique_accepts_bounded_matrix():
    boundary = roadmap_backend_scheduling_critique_boundary_record()

    validation = validate_roadmap_backend_scheduling_critique_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_backend_scheduling_critique_matrix_with_role_capability_inventory"
    )
    assert boundary["schema"] == ROADMAP_BACKEND_SCHEDULING_CRITIQUE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["roadmap_heading_present"] is True
    assert boundary["track_count"] == 9
    assert boundary["active_todo_ref_count"] == 18
    assert boundary["sidecar_ref_count"] == 13
    assert [record["track_id"] for record in boundary["track_records"]] == [
        "heuristic_ucb_rewards",
        "role_scoped_routing",
        "provider_diagnostics_pricing",
        "provider_cancellation_quarantine",
        "fast_strong_model_mix",
        "sample_efficiency",
        "repeated_sampling_baseline",
        "gemini_provider_parity",
        "critique_reviewer_pool",
    ]
    assert boundary["backend_role_capability_matrix_count"] == 9
    assert [
        record["track_id"] for record in boundary["backend_role_capability_matrix"]
    ] == [
        "heuristic_ucb_rewards",
        "role_scoped_routing",
        "provider_diagnostics_pricing",
        "provider_cancellation_quarantine",
        "fast_strong_model_mix",
        "sample_efficiency",
        "repeated_sampling_baseline",
        "gemini_provider_parity",
        "critique_reviewer_pool",
    ]
    assert boundary["critique_control_checklist_count"] == 8
    assert [
        check["check_id"] for check in boundary["critique_control_checklist"]
    ] == [
        "reviewer_pool_selection_policy",
        "reviewer_reward_policy",
        "reviewer_budget_quota_policy",
        "reviewer_diagnostics_replay",
        "reviewer_cancellation_timeout",
        "reviewer_resume_semantics",
        "no_reviewer_comparator",
        "reviewer_isolation",
    ]
    assert all(record["roadmap_phrase_present"] for record in boundary["track_records"])
    assert all(
        sidecar["exists"]
        for record in boundary["track_records"]
        for sidecar in record["current_sidecar_refs"]
    )
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in boundary["track_records"]
        for ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "calibrated_reward_policy": "not_recorded_locally",
        "role_quota_ownership": "not_recorded_locally",
        "live_provider_pricing_defaults": "not_recorded_locally",
        "raw_provider_replay": "not_recorded_locally",
        "live_hard_cancellation": "not_recorded_locally",
        "equal_budget_scheduler_comparators": "not_recorded_locally",
        "first_class_gemini_lanes": "not_recorded_locally",
        "async_reviewer_isolation": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert boundary["resolved_evidence"] == {
        "backend_role_capability_matrix": (
            "recorded_from_roadmap_backend_scheduling_track_records"
        ),
        "critique_control_checklist": (
            "recorded_from_critique_reviewer_pool_track_boundary"
        ),
    }
    assert "backend-role capability inventory" in boundary["claim_boundary"]
    assert "critique-control checklist" in boundary["claim_boundary"]


def test_roadmap_backend_scheduling_critique_rejects_overclaim_and_drift():
    boundary = roadmap_backend_scheduling_critique_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "backend_control_plane_ready"
    boundary["track_count"] = 8
    boundary["track_records"][0]["roadmap_phrase_present"] = False
    boundary["resolved_evidence"]["backend_role_capability_matrix"] = "missing"
    boundary["required_evidence_fields"] = ["track_records"]

    validation = validate_roadmap_backend_scheduling_critique_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_track_count" in codes
    assert "invalid_track_records" in codes
    assert "invalid_resolved_evidence_backend_role_capability_matrix" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_backend_scheduling_critique_summary_reports_shape():
    summary = render_roadmap_backend_scheduling_critique_boundary_summary(
        roadmap_backend_scheduling_critique_boundary_record()
    )

    assert "ROADMAP backend scheduling and critique boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_backend_scheduling_critique_matrix_with_role_capability_inventory |"
        in summary
    )
    assert "| track_count | 9 |" in summary
    assert "| active_todo_ref_count | 18 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
