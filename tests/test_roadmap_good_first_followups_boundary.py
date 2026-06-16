from libreevolve.problems.benchmarks.roadmap_good_first_followups_boundary import (
    ROADMAP_GOOD_FIRST_FOLLOWUPS_BOUNDARY_SCHEMA,
    render_roadmap_good_first_followups_boundary_summary,
    roadmap_good_first_followups_boundary_record,
    validate_roadmap_good_first_followups_boundary,
)


def test_roadmap_good_first_followups_accepts_bounded_priority_map():
    boundary = roadmap_good_first_followups_boundary_record()

    validation = validate_roadmap_good_first_followups_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_good_first_followups_priority_map_without_freshness_gate"
    )
    assert boundary["schema"] == ROADMAP_GOOD_FIRST_FOLLOWUPS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["roadmap_section_present"] is True
    assert boundary["priority_item_count"] == 4
    assert boundary["active_todo_ref_count"] == 9
    assert [record["item_id"] for record in boundary["priority_records"]] == [
        "durable_query_indexes",
        "non_toy_benchmark_fixture",
        "workspace_resume_coverage",
        "feedback_calibration_reports",
    ]
    assert all(record["roadmap_phrase_present"] for record in boundary["priority_records"])
    assert all(
        todo_ref["required_phrase_present"]
        for record in boundary["priority_records"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "priority_score_model": "not_recorded_locally",
        "ci_priority_freshness_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert (
        "Dependency-state refresh and stale-priority detection are recorded separately"
        in boundary["claim_boundary"]
    )


def test_roadmap_good_first_followups_rejects_overclaim_and_drift():
    boundary = roadmap_good_first_followups_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "priority_freshness_gate_ready"
    boundary["priority_item_count"] = 3
    boundary["priority_records"][0]["roadmap_phrase_present"] = False
    boundary["missing_evidence"]["priority_score_model"] = "recorded"
    boundary["required_evidence_fields"] = ["roadmap_priority_items"]

    validation = validate_roadmap_good_first_followups_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_priority_item_count" in codes
    assert "invalid_priority_records" in codes
    assert "invalid_missing_evidence_priority_score_model" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_good_first_followups_summary_reports_shape():
    summary = render_roadmap_good_first_followups_boundary_summary(
        roadmap_good_first_followups_boundary_record()
    )

    assert "ROADMAP Good First Follow-Ups boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_good_first_followups_priority_map_without_freshness_gate |"
        in summary
    )
    assert "| priority_item_count | 4 |" in summary
    assert "| active_todo_ref_count | 9 |" in summary
    assert "| missing_evidence_count | 3 |" in summary
