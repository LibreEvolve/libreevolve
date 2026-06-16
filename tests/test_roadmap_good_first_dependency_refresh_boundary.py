from libreevolve.problems.benchmarks.roadmap_good_first_dependency_refresh_boundary import (
    ROADMAP_GOOD_FIRST_DEPENDENCY_REFRESH_BOUNDARY_SCHEMA,
    render_roadmap_good_first_dependency_refresh_boundary_summary,
    roadmap_good_first_dependency_refresh_boundary_record,
    validate_roadmap_good_first_dependency_refresh_boundary,
)


def test_roadmap_good_first_dependency_refresh_accepts_current_dependencies():
    boundary = roadmap_good_first_dependency_refresh_boundary_record()

    validation = validate_roadmap_good_first_dependency_refresh_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "good_first_dependency_state_refresh_recorded_with_validation_artifact_report"
    )
    assert boundary["schema"] == ROADMAP_GOOD_FIRST_DEPENDENCY_REFRESH_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["source_priority_item_count"] == 4
    assert validation.dependency_record_count == 4
    assert validation.active_dependency_ref_count == 9
    assert validation.stale_dependency_ref_count == 0
    assert validation.missing_evidence_count == 1
    assert [record["item_id"] for record in boundary["dependency_records"]] == [
        "durable_query_indexes",
        "non_toy_benchmark_fixture",
        "workspace_resume_coverage",
        "feedback_calibration_reports",
    ]
    assert all(
        ref["dependency_ref_status"] == "live_active_dependency_ref"
        for record in boundary["dependency_records"]
        for ref in record["dependency_todo_refs"]
    )
    assert all(
        record["dependency_refresh_status"] == "dependency_state_refreshed"
        for record in boundary["dependency_records"]
    )
    assert boundary["missing_evidence"] == {
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "rejects stale or missing dependency refs" in boundary["claim_boundary"]


def test_roadmap_good_first_dependency_refresh_rejects_overclaim_and_stale_ref():
    boundary = roadmap_good_first_dependency_refresh_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "good_first_priority_freshness_ready"
    boundary["stale_dependency_ref_count"] = 1
    boundary["stale_dependency_ref_records"] = [
        {
            "item_id": "durable_query_indexes",
            "path": "docs/todo/code.md",
            "required_phrase": "missing",
            "required_phrase_present": False,
            "active_marker_present": False,
            "dependency_ref_status": "missing_or_completed_dependency_ref",
        }
    ]
    boundary["dependency_records"][0]["dependency_refresh_status"] = (
        "dependency_state_stale_or_incomplete"
    )
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["source_good_first_priority_items"]

    validation = validate_roadmap_good_first_dependency_refresh_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_stale_dependency_ref_count" in codes
    assert "invalid_stale_dependency_ref_records" in codes
    assert "invalid_dependency_records" in codes
    assert "stale_dependency_ref_detected" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_good_first_dependency_refresh_summary_reports_shape():
    summary = render_roadmap_good_first_dependency_refresh_boundary_summary(
        roadmap_good_first_dependency_refresh_boundary_record()
    )

    assert "ROADMAP Good First dependency refresh boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | good_first_dependency_state_refresh_recorded_with_validation_artifact_report |"
        in summary
    )
    assert "| dependency_record_count | 4 |" in summary
    assert "| active_dependency_ref_count | 9 |" in summary
    assert "| stale_dependency_ref_count | 0 |" in summary
    assert "| missing_evidence_count | 1 |" in summary
