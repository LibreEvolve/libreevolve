from libreevolve.problems.benchmarks.roadmap_non_goal_ci_promotion_gate_boundary import (
    ROADMAP_NON_GOAL_CI_PROMOTION_GATE_BOUNDARY_SCHEMA,
    render_roadmap_non_goal_ci_promotion_gate_boundary_summary,
    roadmap_non_goal_ci_promotion_gate_boundary_record,
    validate_roadmap_non_goal_ci_promotion_gate_boundary,
)


def test_roadmap_non_goal_ci_promotion_gate_accepts_current_workflow():
    boundary = roadmap_non_goal_ci_promotion_gate_boundary_record()

    validation = validate_roadmap_non_goal_ci_promotion_gate_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "ci_non_goal_promotion_gate_recorded_without_intentional_workflow"
    )
    assert boundary["schema"] == ROADMAP_NON_GOAL_CI_PROMOTION_GATE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["workflow_exists"] is True
    assert validation.workflow_phrase_count == 7
    assert validation.non_goal_test_count == 5
    assert validation.sidecar_ref_count == 5
    assert validation.missing_evidence_count == 4
    assert all(record["present"] for record in boundary["workflow_phrases"].values())
    assert all(record["exists"] for record in boundary["non_goal_tests"])
    assert all(record["exists"] for record in boundary["non_goal_sidecars"])
    assert boundary["missing_evidence"] == {
        "intentional_promotion_workflow": "not_recorded_locally",
        "claim_surface_remediation": "not_recorded_locally",
        "runtime_plugin_scope_join": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim an intentional promotion workflow" in boundary["claim_boundary"]


def test_roadmap_non_goal_ci_promotion_gate_rejects_overclaim_and_drift():
    boundary = roadmap_non_goal_ci_promotion_gate_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "full_non_goal_lifecycle_gate_ready"
    boundary["workflow_phrases"]["paper_manifest_command"]["present"] = False
    boundary["non_goal_tests"][0]["exists"] = False
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["paper_docs_job_runs_manifest"]

    validation = validate_roadmap_non_goal_ci_promotion_gate_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_workflow_phrase_paper_manifest_command" in codes
    assert "missing_non_goal_tests_path" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_non_goal_ci_promotion_gate_summary_reports_shape():
    summary = render_roadmap_non_goal_ci_promotion_gate_boundary_summary(
        roadmap_non_goal_ci_promotion_gate_boundary_record()
    )

    assert "ROADMAP non-goal CI promotion gate boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | ci_non_goal_promotion_gate_recorded_without_intentional_workflow |"
        in summary
    )
    assert "| workflow_phrase_count | 7 |" in summary
    assert "| non_goal_test_count | 5 |" in summary
    assert "| sidecar_ref_count | 5 |" in summary
    assert "| missing_evidence_count | 4 |" in summary
