from libreevolve.problems.benchmarks.roadmap_good_first_priority_score_boundary import (
    ROADMAP_GOOD_FIRST_PRIORITY_SCORE_BOUNDARY_SCHEMA,
    render_roadmap_good_first_priority_score_boundary_summary,
    roadmap_good_first_priority_score_boundary_record,
    validate_roadmap_good_first_priority_score_boundary,
)


def test_roadmap_good_first_priority_score_accepts_current_rank_order():
    boundary = roadmap_good_first_priority_score_boundary_record()

    validation = validate_roadmap_good_first_priority_score_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "good_first_priority_score_model_recorded_with_ci_priority_gate"
    )
    assert boundary["schema"] == ROADMAP_GOOD_FIRST_PRIORITY_SCORE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_good_first_boundary_input"]
        == "papers/roadmap_good_first_followups_boundary.json"
    )
    assert (
        boundary["dependency_refresh_boundary_input"]
        == "papers/roadmap_good_first_dependency_refresh_boundary.json"
    )
    assert (
        boundary["stale_priority_boundary_input"]
        == "papers/roadmap_good_first_stale_priority_boundary.json"
    )
    assert boundary["source_priority_item_count"] == 4
    assert boundary["dependency_refresh_record_count"] == 4
    assert boundary["stale_priority_count"] == 0
    assert boundary["score_feature_weights"] == {
        "alphaevolve_impact_score": 10,
        "dependency_readiness_score": 5,
        "live_dependency_refresh_score": 3,
        "validation_gate_count": 1,
        "stale_priority_penalty": -100,
    }
    assert boundary["priority_item_count"] == 4
    assert boundary["ranked_item_ids"] == [
        "durable_query_indexes",
        "non_toy_benchmark_fixture",
        "workspace_resume_coverage",
        "feedback_calibration_reports",
    ]
    assert boundary["roadmap_priority_item_ids"] == boundary["ranked_item_ids"]
    assert boundary["priority_order_match"] is True
    assert validation.rank_mismatch_count == 0
    assert boundary["rank_mismatch_records"] == []
    assert [record["priority_score"] for record in boundary["score_records"]] == [
        81,
        66,
        51,
        36,
    ]
    assert boundary["missing_evidence"] == {
        "validation_artifact_refresh": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "bounded deterministic priority score model" in boundary["claim_boundary"]


def test_roadmap_good_first_priority_score_rejects_overclaim_and_rank_drift():
    boundary = roadmap_good_first_priority_score_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "good_first_ci_priority_gate_ready"
    boundary["priority_order_match"] = False
    boundary["rank_mismatch_count"] = 1
    boundary["rank_mismatch_records"] = [
        {
            "expected_rank": 1,
            "roadmap_item_id": "durable_query_indexes",
            "score_model_item_id": "non_toy_benchmark_fixture",
        }
    ]
    boundary["ranked_item_ids"] = [
        "non_toy_benchmark_fixture",
        "durable_query_indexes",
        "workspace_resume_coverage",
        "feedback_calibration_reports",
    ]
    boundary["missing_evidence"]["validation_artifact_refresh"] = "recorded"
    boundary["required_evidence_fields"] = ["source_good_first_priority_items"]

    validation = validate_roadmap_good_first_priority_score_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_priority_order_match" in codes
    assert "invalid_rank_mismatch_count" in codes
    assert "invalid_rank_mismatch_records" in codes
    assert "invalid_ranked_item_ids" in codes
    assert "priority_order_mismatch" in codes
    assert "rank_mismatch_detected" in codes
    assert "invalid_missing_evidence_validation_artifact_refresh" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_good_first_priority_score_summary_reports_shape():
    summary = render_roadmap_good_first_priority_score_boundary_summary(
        roadmap_good_first_priority_score_boundary_record()
    )

    assert "ROADMAP Good First priority score boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | good_first_priority_score_model_recorded_with_ci_priority_gate |"
        in summary
    )
    assert "| priority_item_count | 4 |" in summary
    assert "| rank_mismatch_count | 0 |" in summary
    assert "| missing_evidence_count | 2 |" in summary
