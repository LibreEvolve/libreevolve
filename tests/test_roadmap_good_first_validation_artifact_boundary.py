from libreevolve.problems.benchmarks.roadmap_good_first_validation_artifact_boundary import (
    ROADMAP_GOOD_FIRST_VALIDATION_ARTIFACT_BOUNDARY_SCHEMA,
    render_roadmap_good_first_validation_artifact_boundary_summary,
    roadmap_good_first_validation_artifact_boundary_record,
    validate_roadmap_good_first_validation_artifact_boundary,
)


def test_roadmap_good_first_validation_artifact_accepts_report():
    boundary = roadmap_good_first_validation_artifact_boundary_record()

    validation = validate_roadmap_good_first_validation_artifact_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "good_first_validation_artifact_report_recorded_without_owner_signoff"
    )
    assert boundary["schema"] == ROADMAP_GOOD_FIRST_VALIDATION_ARTIFACT_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_good_first_boundary_input"]
        == "papers/roadmap_good_first_followups_boundary.json"
    )
    assert boundary["source_priority_item_count"] == 4
    assert boundary["source_validation_gate_count"] == 12
    assert (
        boundary["ci_priority_gate_boundary_input"]
        == "papers/roadmap_good_first_ci_priority_gate_boundary.json"
    )
    assert boundary["ci_priority_gate_status"] == (
        "good_first_priority_freshness_gate_present"
    )
    assert boundary["validation_artifact_record_count"] == 12
    assert boundary["stale_validation_artifact_record_count"] == 0
    assert boundary["stale_validation_artifact_records"] == []
    assert boundary["validation_artifact_report_status"] == (
        "validation_artifact_freshness_report_current"
    )
    assert [record["validation_gate"] for record in boundary["validation_artifact_records"]] == [
        "durable database/query index tests",
        "run-artifact query/report sidecar",
        "paper-manifest validation",
        "repeated-seed run reports",
        "target-hit-rate summaries",
        "benchmark hardening certification",
        "archive event replay restore tests",
        "pending-work resume tests",
        "workspace artifact integrity report",
        "runtime feedback-calibration fixture",
        "grader ablation outputs",
        "feedback-calibration artifact inventory",
    ]
    assert all(
        record["validation_gate_present"]
        for record in boundary["validation_artifact_records"]
    )
    assert all(
        sidecar["exists"]
        for record in boundary["validation_artifact_records"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        todo_ref["exists"] and todo_ref["required_phrase_present"]
        for record in boundary["validation_artifact_records"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "expected validation artifacts" in boundary["claim_boundary"]


def test_roadmap_good_first_validation_artifact_rejects_overclaim_and_drift():
    boundary = roadmap_good_first_validation_artifact_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "validation_artifact_refresh_ready"
    boundary["validation_artifact_record_count"] = 0
    boundary["validation_artifact_records"][0]["sidecar_refs"][0]["exists"] = False
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["source_good_first_priority_items"]

    validation = validate_roadmap_good_first_validation_artifact_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_validation_artifact_record_count" in codes
    assert "invalid_validation_artifact_records" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_good_first_validation_artifact_summary_reports_shape():
    summary = render_roadmap_good_first_validation_artifact_boundary_summary(
        roadmap_good_first_validation_artifact_boundary_record()
    )

    assert "ROADMAP Good First validation-artifact boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | good_first_validation_artifact_report_recorded_without_owner_signoff |"
        in summary
    )
    assert "| validation_artifact_record_count | 12 |" in summary
    assert "| stale_validation_artifact_record_count | 0 |" in summary
    assert "| missing_evidence_count | 1 |" in summary
