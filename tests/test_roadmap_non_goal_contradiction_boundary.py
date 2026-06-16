from libreevolve.problems.benchmarks.roadmap_non_goal_contradiction_boundary import (
    ROADMAP_NON_GOAL_CONTRADICTION_BOUNDARY_SCHEMA,
    render_roadmap_non_goal_contradiction_boundary_summary,
    roadmap_non_goal_contradiction_boundary_record,
    validate_roadmap_non_goal_contradiction_boundary,
)


def test_roadmap_non_goal_contradiction_accepts_bounded_inventory():
    boundary = roadmap_non_goal_contradiction_boundary_record()

    validation = validate_roadmap_non_goal_contradiction_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_non_goal_inventory_without_full_contradiction_gate"
    )
    assert boundary["schema"] == ROADMAP_NON_GOAL_CONTRADICTION_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["non_goal_count"] == 3
    assert boundary["constrained_surface_count"] == 9
    assert boundary["contradiction_count"] == 0
    assert [record["non_goal_id"] for record in boundary["non_goal_records"]] == [
        "normal_local_use_no_service_database_required",
        "no_arbitrary_language_codebase_support_before_runners",
        "paper_inspired_plugins_not_faithful_implementations",
    ]
    assert all(
        surface["required_safe_phrase_present"]
        for record in boundary["non_goal_records"]
        for surface in record["constrained_surfaces"]
    )
    assert boundary["missing_evidence"] == {
        "runtime_metadata_scan": "not_recorded_locally",
        "plugin_docstring_scan": "not_recorded_locally",
        "full_markdown_corpus_scan": "not_recorded_locally",
        "ci_non_goal_promotion_gate": "not_recorded_locally",
        "intentional_promotion_workflow": "not_recorded_locally",
    }
    assert "does not claim a full runtime metadata scan" in boundary["claim_boundary"]


def test_roadmap_non_goal_contradiction_rejects_overclaim_and_drift():
    boundary = roadmap_non_goal_contradiction_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_non_goal_contradiction_gate_ready"
    boundary["contradiction_count"] = 1
    boundary["non_goal_records"][1]["constrained_surfaces"][1][
        "detected_forbidden_claims"
    ] = ["supports arbitrary-language runners"]
    boundary["missing_evidence"]["runtime_metadata_scan"] = "recorded"
    boundary["required_evidence_fields"] = ["stable_non_goal_ids"]

    validation = validate_roadmap_non_goal_contradiction_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_contradiction_count" in codes
    assert "invalid_non_goal_records" in codes
    assert "contradiction_detected" in codes
    assert "invalid_missing_evidence_runtime_metadata_scan" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_non_goal_contradiction_summary_reports_shape():
    summary = render_roadmap_non_goal_contradiction_boundary_summary(
        roadmap_non_goal_contradiction_boundary_record()
    )

    assert "ROADMAP non-goal contradiction boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_non_goal_inventory_without_full_contradiction_gate |"
        in summary
    )
    assert "| non_goal_count | 3 |" in summary
    assert "| contradiction_count | 0 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
