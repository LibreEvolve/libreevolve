from libreevolve.problems.benchmarks.roadmap_backend_control_plane_readiness_boundary import (
    ROADMAP_BACKEND_CONTROL_PLANE_READINESS_BOUNDARY_SCHEMA,
    render_roadmap_backend_control_plane_readiness_boundary_summary,
    roadmap_backend_control_plane_readiness_boundary_record,
    validate_roadmap_backend_control_plane_readiness_boundary,
)


def test_roadmap_backend_control_plane_readiness_accepts_bounded_matrix():
    boundary = roadmap_backend_control_plane_readiness_boundary_record()

    validation = validate_roadmap_backend_control_plane_readiness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_backend_control_plane_readiness_matrix_without_scheduler_parity_gate"
    )
    assert boundary["schema"] == ROADMAP_BACKEND_CONTROL_PLANE_READINESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_backend_boundary_input"]
        == "papers/roadmap_backend_scheduling_critique_boundary.json"
    )
    assert boundary["source_track_count"] == 9
    assert boundary["source_active_todo_ref_count"] == 18
    assert boundary["source_sidecar_ref_count"] == 13
    assert boundary["readiness_criterion_count"] == 8
    assert boundary["sidecar_ref_count"] == 16
    assert boundary["active_todo_ref_count"] == 16
    assert [record["criterion_id"] for record in boundary["readiness_criteria"]] == [
        "backend_role_capability_matrix",
        "calibrated_reward_quota_policy",
        "live_pricing_default_and_raw_replay",
        "hard_cancellation_and_resume",
        "equal_budget_scheduler_comparator",
        "gemini_lane_and_substitution",
        "critique_reviewer_isolation",
        "stale_readiness_and_owner_signoff",
    ]
    assert boundary["backend_control_plane_claim_guard_count"] == 8
    assert [
        record["criterion_id"]
        for record in boundary["backend_control_plane_claim_guard"]
    ] == [
        "backend_role_capability_matrix",
        "calibrated_reward_quota_policy",
        "live_pricing_default_and_raw_replay",
        "hard_cancellation_and_resume",
        "equal_budget_scheduler_comparator",
        "gemini_lane_and_substitution",
        "critique_reviewer_isolation",
        "stale_readiness_and_owner_signoff",
    ]
    assert all(
        "missing_before_scheduler_parity_claim" in record
        for record in boundary["backend_control_plane_claim_guard"]
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
        "calibrated_reward_policy": "not_recorded_locally",
        "role_quota_ownership": "not_recorded_locally",
        "live_provider_pricing_default_evidence": "not_recorded_locally",
        "raw_provider_replay": "not_recorded_locally",
        "live_hard_cancellation": "not_recorded_locally",
        "equal_budget_scheduler_comparator": "not_recorded_locally",
        "first_class_gemini_lane_evidence": "not_recorded_locally",
        "async_reviewer_isolation": "not_recorded_locally",
        "stale_readiness_detector": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert boundary["resolved_evidence"] == {
        "backend_role_capability_matrix": (
            "recorded_in_source_backend_scheduling_critique_boundary"
        ),
        "critique_control_checklist": (
            "recorded_in_source_backend_scheduling_critique_boundary"
        ),
    }
    assert "recorded backend-role capability matrix" in boundary["claim_boundary"]
    assert "recorded critique-control checklist" in boundary["claim_boundary"]
    assert "claim guard for each control-plane surface" in boundary["claim_boundary"]
    assert "full backend scheduler parity" in boundary["claim_boundary"]


def test_roadmap_backend_control_plane_readiness_rejects_overclaim_and_drift():
    boundary = roadmap_backend_control_plane_readiness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "backend_scheduler_parity_ready"
    boundary["readiness_criterion_count"] = 0
    boundary["readiness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["backend_control_plane_claim_guard_count"] = 0
    boundary["missing_evidence"]["calibrated_reward_policy"] = "recorded"
    boundary["required_evidence_fields"] = ["backend_role_capability_matrix"]

    validation = validate_roadmap_backend_control_plane_readiness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_readiness_criterion_count" in codes
    assert "invalid_readiness_criteria" in codes
    assert "invalid_backend_control_plane_claim_guard_count" in codes
    assert "invalid_missing_evidence_calibrated_reward_policy" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_backend_control_plane_readiness_summary_reports_shape():
    summary = render_roadmap_backend_control_plane_readiness_boundary_summary(
        roadmap_backend_control_plane_readiness_boundary_record()
    )

    assert "ROADMAP backend control-plane readiness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_backend_control_plane_readiness_matrix_without_scheduler_parity_gate |"
        in summary
    )
    assert "| readiness_criterion_count | 8 |" in summary
    assert "| sidecar_ref_count | 16 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 10 |" in summary
