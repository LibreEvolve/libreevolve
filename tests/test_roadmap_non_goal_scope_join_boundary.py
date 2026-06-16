from libreevolve.problems.benchmarks.roadmap_non_goal_scope_join_boundary import (
    ROADMAP_NON_GOAL_SCOPE_JOIN_BOUNDARY_SCHEMA,
    render_roadmap_non_goal_scope_join_boundary_summary,
    roadmap_non_goal_scope_join_boundary_record,
    validate_roadmap_non_goal_scope_join_boundary,
)


def test_roadmap_non_goal_scope_join_accepts_current_joined_map():
    boundary = roadmap_non_goal_scope_join_boundary_record()

    validation = validate_roadmap_non_goal_scope_join_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "runtime_plugin_docs_paper_scope_join_without_owner_signoff"
    )
    assert boundary["schema"] == ROADMAP_NON_GOAL_SCOPE_JOIN_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.non_goal_join_count == 3
    assert validation.joined_scope_count == 21
    assert validation.missing_join_count == 0
    assert validation.contradiction_count == 0
    assert validation.missing_evidence_count == 1
    assert all(record["exists"] for record in boundary["source_sidecar_records"])
    assert [
        record["non_goal_id"] for record in boundary["non_goal_join_records"]
    ] == [
        "normal_local_use_no_service_database_required",
        "no_arbitrary_language_codebase_support_before_runners",
        "paper_inspired_plugins_not_faithful_implementations",
    ]
    assert all(
        record["join_status"] == "joined_without_owner_signoff"
        for record in boundary["non_goal_join_records"]
    )
    assert boundary["missing_evidence"] == {
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "zero unresolved contradictions" in boundary["claim_boundary"]


def test_roadmap_non_goal_scope_join_rejects_overclaim_and_drift():
    boundary = roadmap_non_goal_scope_join_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_non_goal_lifecycle_ready"
    boundary["non_goal_join_count"] = 0
    boundary["missing_join_count"] = 1
    boundary["missing_join_records"] = [
        {
            "non_goal_id": "normal_local_use_no_service_database_required",
            "scope": "runtime_metadata",
            "status": "missing_runtime_scope",
        }
    ]
    boundary["contradiction_count"] = 1
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["stable_non_goal_ids"]

    validation = validate_roadmap_non_goal_scope_join_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_non_goal_join_count" in codes
    assert "invalid_missing_join_count" in codes
    assert "invalid_missing_join_records" in codes
    assert "invalid_contradiction_count" in codes
    assert "missing_scope_join" in codes
    assert "joined_contradiction_detected" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_non_goal_scope_join_summary_reports_shape():
    summary = render_roadmap_non_goal_scope_join_boundary_summary(
        roadmap_non_goal_scope_join_boundary_record()
    )

    assert "ROADMAP non-goal scope join boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | runtime_plugin_docs_paper_scope_join_without_owner_signoff |"
        in summary
    )
    assert "| non_goal_join_count | 3 |" in summary
    assert "| joined_scope_count | 21 |" in summary
    assert "| missing_join_count | 0 |" in summary
    assert "| contradiction_count | 0 |" in summary
    assert "| missing_evidence_count | 1 |" in summary
