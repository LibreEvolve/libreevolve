from libreevolve.problems.benchmarks.roadmap_good_first_freshness_boundary import (
    ROADMAP_GOOD_FIRST_FRESHNESS_BOUNDARY_SCHEMA,
    render_roadmap_good_first_freshness_boundary_summary,
    roadmap_good_first_freshness_boundary_record,
    validate_roadmap_good_first_freshness_boundary,
)


def test_roadmap_good_first_freshness_accepts_bounded_matrix():
    boundary = roadmap_good_first_freshness_boundary_record()

    validation = validate_roadmap_good_first_freshness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_good_first_freshness_matrix_with_stale_priority_detector_without_score_model"
    )
    assert boundary["schema"] == ROADMAP_GOOD_FIRST_FRESHNESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_good_first_boundary_input"]
        == "papers/roadmap_good_first_followups_boundary.json"
    )
    assert boundary["source_priority_item_count"] == 4
    assert boundary["source_active_todo_ref_count"] == 9
    assert (
        boundary["dependency_refresh_boundary_input"]
        == "papers/roadmap_good_first_dependency_refresh_boundary.json"
    )
    assert boundary["dependency_refresh_record_count"] == 4
    assert boundary["dependency_refresh_stale_ref_count"] == 0
    assert (
        boundary["stale_priority_boundary_input"]
        == "papers/roadmap_good_first_stale_priority_boundary.json"
    )
    assert boundary["stale_priority_count"] == 0
    assert boundary["priority_detector_status"] == (
        "no_stale_good_first_priorities_detected"
    )
    assert boundary["freshness_criterion_count"] == 6
    assert boundary["sidecar_ref_count"] == 14
    assert boundary["active_todo_ref_count"] == 12
    assert [record["criterion_id"] for record in boundary["freshness_criteria"]] == [
        "dependency_state_refresh",
        "stale_priority_detector",
        "calibrated_priority_score_model",
        "ci_priority_freshness_gate",
        "validation_artifact_refresh",
        "owner_review_signoff",
    ]
    assert all(
        sidecar["exists"]
        for record in boundary["freshness_criteria"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        todo_ref["exists"] and todo_ref["required_phrase_present"]
        for record in boundary["freshness_criteria"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "calibrated_priority_score_model": "not_recorded_locally",
        "ci_priority_freshness_gate": "not_recorded_locally",
        "validation_artifact_refresh": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert (
        "recorded dependency-state refresh and stale-priority detector boundaries"
        in boundary["claim_boundary"]
    )


def test_roadmap_good_first_freshness_rejects_overclaim_and_drift():
    boundary = roadmap_good_first_freshness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "good_first_freshness_gate_ready"
    boundary["freshness_criterion_count"] = 0
    boundary["freshness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["missing_evidence"]["calibrated_priority_score_model"] = "recorded"
    boundary["required_evidence_fields"] = ["dependency_state_refresh"]

    validation = validate_roadmap_good_first_freshness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_freshness_criterion_count" in codes
    assert "invalid_freshness_criteria" in codes
    assert "invalid_missing_evidence_calibrated_priority_score_model" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_good_first_freshness_summary_reports_shape():
    summary = render_roadmap_good_first_freshness_boundary_summary(
        roadmap_good_first_freshness_boundary_record()
    )

    assert "ROADMAP Good First Follow-Ups freshness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_good_first_freshness_matrix_with_stale_priority_detector_without_score_model |"
        in summary
    )
    assert "| freshness_criterion_count | 6 |" in summary
    assert "| sidecar_ref_count | 14 |" in summary
    assert "| active_todo_ref_count | 12 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
