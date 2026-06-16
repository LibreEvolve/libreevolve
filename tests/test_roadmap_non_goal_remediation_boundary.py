from libreevolve.problems.benchmarks.roadmap_non_goal_remediation_boundary import (
    ROADMAP_NON_GOAL_REMEDIATION_BOUNDARY_SCHEMA,
    render_roadmap_non_goal_remediation_boundary_summary,
    roadmap_non_goal_remediation_boundary_record,
    validate_roadmap_non_goal_remediation_boundary,
)


def test_roadmap_non_goal_remediation_accepts_zero_unresolved_report():
    boundary = roadmap_non_goal_remediation_boundary_record()

    validation = validate_roadmap_non_goal_remediation_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "contradiction_remediation_report_recorded_without_scope_join_or_signoff"
    )
    assert boundary["schema"] == ROADMAP_NON_GOAL_REMEDIATION_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert validation.source_scan_count == 4
    assert validation.unresolved_contradiction_count == 0
    assert validation.remediation_route_count == 3
    assert validation.missing_evidence_count == 2
    assert all(
        record["contradiction_count"] == 0
        for record in boundary["source_scan_records"]
    )
    assert all(
        record["owner_todo_exists"] and record["owner_todo_required_phrase_present"]
        for record in boundary["remediation_route_records"]
    )
    assert boundary["missing_evidence"] == {
        "runtime_plugin_scope_join": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "requiring zero unresolved hits" in boundary["claim_boundary"]


def test_roadmap_non_goal_remediation_rejects_overclaim_and_unresolved_hits():
    boundary = roadmap_non_goal_remediation_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_non_goal_lifecycle_ready"
    boundary["unresolved_contradiction_count"] = 1
    boundary["source_scan_records"][0]["contradiction_count"] = 1
    boundary["source_scan_records"][0]["unresolved_record_count"] = 1
    boundary["remediation_route_records"][0]["owner_todo_required_phrase_present"] = False
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["bounded_contradiction_inventory"]

    validation = validate_roadmap_non_goal_remediation_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_scan_records" in codes
    assert "invalid_unresolved_contradiction_count" in codes
    assert "invalid_remediation_route_records" in codes
    assert "unresolved_contradiction_detected" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_non_goal_remediation_summary_reports_shape():
    summary = render_roadmap_non_goal_remediation_boundary_summary(
        roadmap_non_goal_remediation_boundary_record()
    )

    assert "ROADMAP non-goal remediation boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | contradiction_remediation_report_recorded_without_scope_join_or_signoff |"
        in summary
    )
    assert "| source_scan_count | 4 |" in summary
    assert "| unresolved_contradiction_count | 0 |" in summary
    assert "| remediation_route_count | 3 |" in summary
    assert "| missing_evidence_count | 2 |" in summary
