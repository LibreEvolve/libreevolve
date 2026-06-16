from libreevolve.problems.benchmarks.roadmap_good_first_stale_priority_boundary import (
    ROADMAP_GOOD_FIRST_STALE_PRIORITY_BOUNDARY_SCHEMA,
    render_roadmap_good_first_stale_priority_boundary_summary,
    roadmap_good_first_stale_priority_boundary_record,
    validate_roadmap_good_first_stale_priority_boundary,
)


def test_roadmap_good_first_stale_priority_accepts_current_priority_order():
    boundary = roadmap_good_first_stale_priority_boundary_record()

    validation = validate_roadmap_good_first_stale_priority_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "good_first_stale_priority_detector_recorded_with_separate_score_model"
    )
    assert boundary["schema"] == ROADMAP_GOOD_FIRST_STALE_PRIORITY_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_good_first_boundary_input"]
        == "papers/roadmap_good_first_followups_boundary.json"
    )
    assert (
        boundary["dependency_refresh_boundary_input"]
        == "papers/roadmap_good_first_dependency_refresh_boundary.json"
    )
    assert boundary["source_priority_item_count"] == 4
    assert boundary["dependency_refresh_record_count"] == 4
    assert boundary["ordinal_sequence_check"] == {
        "expected_ordinals": [1, 2, 3, 4],
        "observed_ordinals": [1, 2, 3, 4],
        "status": "ordinal_sequence_current",
    }
    assert boundary["priority_detector_status"] == (
        "no_stale_good_first_priorities_detected"
    )
    assert validation.priority_item_count == 4
    assert validation.stale_priority_count == 0
    assert validation.missing_evidence_count == 3
    assert boundary["stale_priority_records"] == []
    assert all(
        record["priority_detector_status"] == "priority_current"
        for record in boundary["detector_records"]
    )
    assert boundary["missing_evidence"] == {
        "ci_priority_freshness_gate": "not_recorded_locally",
        "validation_artifact_refresh": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "priority score model is recorded separately" in boundary["detector_scope"]
    assert "rejects stale priority records" in boundary["claim_boundary"]


def test_roadmap_good_first_stale_priority_rejects_overclaim_and_stale_record():
    boundary = roadmap_good_first_stale_priority_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "good_first_priority_score_ready"
    boundary["priority_detector_status"] = "stale_good_first_priorities_detected"
    boundary["stale_priority_count"] = 1
    boundary["stale_priority_records"] = [
        {
            "item_id": "durable_query_indexes",
            "ordinal": 1,
            "source_spec_ordinal": 1,
            "dependency_refresh_status": "dependency_state_stale_or_incomplete",
            "stale_dependency_ref_count": 1,
            "roadmap_phrase_present": True,
            "current_blocker_label": "durable_tables",
            "priority_detector_status": "stale_priority_detected",
            "stale_reasons": ["stale_dependency_ref"],
        }
    ]
    boundary["detector_records"][0]["priority_detector_status"] = (
        "stale_priority_detected"
    )
    boundary["missing_evidence"]["ci_priority_freshness_gate"] = "recorded"
    boundary["required_evidence_fields"] = ["source_good_first_priority_items"]

    validation = validate_roadmap_good_first_stale_priority_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_priority_detector_status" in codes
    assert "invalid_stale_priority_count" in codes
    assert "invalid_stale_priority_records" in codes
    assert "invalid_detector_records" in codes
    assert "stale_priority_detected" in codes
    assert "invalid_missing_evidence_ci_priority_freshness_gate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_good_first_stale_priority_summary_reports_shape():
    summary = render_roadmap_good_first_stale_priority_boundary_summary(
        roadmap_good_first_stale_priority_boundary_record()
    )

    assert "ROADMAP Good First stale-priority boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | good_first_stale_priority_detector_recorded_with_separate_score_model |"
        in summary
    )
    assert "| priority_item_count | 4 |" in summary
    assert "| stale_priority_count | 0 |" in summary
    assert "| missing_evidence_count | 3 |" in summary
