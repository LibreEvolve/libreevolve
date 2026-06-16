from libreevolve.problems.benchmarks.roadmap_non_goal_drift_boundary import (
    ROADMAP_NON_GOAL_DRIFT_BOUNDARY_SCHEMA,
    render_roadmap_non_goal_drift_boundary_summary,
    roadmap_non_goal_drift_boundary_record,
    validate_roadmap_non_goal_drift_boundary,
)


def test_roadmap_non_goal_drift_accepts_bounded_readiness_matrix():
    boundary = roadmap_non_goal_drift_boundary_record()

    validation = validate_roadmap_non_goal_drift_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_non_goal_drift_matrix_without_full_promotion_gate"
    )
    assert boundary["schema"] == ROADMAP_NON_GOAL_DRIFT_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_non_goal_boundary_input"]
        == "papers/roadmap_non_goal_contradiction_boundary.json"
    )
    assert boundary["source_non_goal_count"] == 3
    assert boundary["source_constrained_surface_count"] == 9
    assert boundary["source_contradiction_count"] == 0
    assert boundary["criterion_count"] == 7
    assert boundary["sidecar_ref_count"] == 16
    assert boundary["active_todo_ref_count"] == 14
    assert [record["criterion_id"] for record in boundary["readiness_criteria"]] == [
        "runtime_metadata_scan",
        "plugin_docstring_scan",
        "full_markdown_corpus_scan",
        "ci_non_goal_promotion_gate",
        "intentional_promotion_workflow",
        "claim_surface_remediation",
        "runtime_plugin_scope_join",
    ]
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
        "runtime_metadata_scan": "not_recorded_locally",
        "ci_non_goal_promotion_gate": "not_recorded_locally",
        "intentional_promotion_workflow": "not_recorded_locally",
        "claim_surface_remediation": "not_recorded_locally",
        "runtime_plugin_scope_join": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert (
        "Markdown corpus and plugin docstring scans are recorded separately"
        in boundary["claim_boundary"]
    )


def test_roadmap_non_goal_drift_rejects_overclaim_and_drift():
    boundary = roadmap_non_goal_drift_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_non_goal_promotion_gate_ready"
    boundary["criterion_count"] = 0
    boundary["readiness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["missing_evidence"]["ci_non_goal_promotion_gate"] = "recorded"
    boundary["required_evidence_fields"] = ["runtime_metadata_scan"]

    validation = validate_roadmap_non_goal_drift_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_criterion_count" in codes
    assert "invalid_readiness_criteria" in codes
    assert "invalid_missing_evidence_ci_non_goal_promotion_gate" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_non_goal_drift_summary_reports_shape():
    summary = render_roadmap_non_goal_drift_boundary_summary(
        roadmap_non_goal_drift_boundary_record()
    )

    assert "ROADMAP non-goal drift boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_non_goal_drift_matrix_without_full_promotion_gate |"
        in summary
    )
    assert "| criterion_count | 7 |" in summary
    assert "| sidecar_ref_count | 16 |" in summary
    assert "| active_todo_ref_count | 14 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
