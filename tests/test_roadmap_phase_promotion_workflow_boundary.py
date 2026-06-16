from libreevolve.problems.benchmarks.roadmap_phase_promotion_workflow_boundary import (
    ROADMAP_PHASE_PROMOTION_WORKFLOW_BOUNDARY_SCHEMA,
    render_roadmap_phase_promotion_workflow_boundary_summary,
    roadmap_phase_promotion_workflow_boundary_record,
    validate_roadmap_phase_promotion_workflow_boundary,
)


def test_roadmap_phase_promotion_workflow_accepts_current_doc():
    boundary = roadmap_phase_promotion_workflow_boundary_record()

    validation = validate_roadmap_phase_promotion_workflow_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "phase_promotion_demotion_workflow_recorded_without_ci_or_signoff"
    )
    assert boundary["schema"] == ROADMAP_PHASE_PROMOTION_WORKFLOW_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["workflow_doc"] == "docs/roadmap-phase-promotion-workflow.md"
    assert boundary["workflow_doc_exists"] is True
    assert validation.workflow_phrase_count == 9
    assert validation.claim_surface_count == 6
    assert validation.sidecar_ref_count == 7
    assert validation.missing_evidence_count == 3
    assert all(record["present"] for record in boundary["workflow_phrases"].values())
    assert all(
        record["exists"] and record["listed_in_workflow"]
        for record in boundary["claim_surfaces"]
    )
    assert all(
        record["exists"] and record["listed_in_workflow"]
        for record in boundary["sidecar_refs"]
    )
    assert boundary["missing_evidence"] == {
        "ci_phase_freshness_gate": "not_recorded_locally",
        "evidence_status_refresh": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "paper manifest gate" in boundary["claim_boundary"]


def test_roadmap_phase_promotion_workflow_rejects_overclaim_and_drift():
    boundary = roadmap_phase_promotion_workflow_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "phase_lifecycle_ready"
    boundary["workflow_phrases"]["stable_phase_section_id"]["present"] = False
    boundary["claim_surfaces"][0]["listed_in_workflow"] = False
    boundary["sidecar_refs"][0]["exists"] = False
    boundary["missing_evidence"]["owner_review_signoff"] = "recorded"
    boundary["required_evidence_fields"] = ["workflow_doc"]

    validation = validate_roadmap_phase_promotion_workflow_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_workflow_phrase_stable_phase_section_id" in codes
    assert "invalid_claim_surfaces_path" in codes
    assert "invalid_sidecar_refs_path" in codes
    assert "invalid_missing_evidence_owner_review_signoff" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_phase_promotion_workflow_summary_reports_shape():
    summary = render_roadmap_phase_promotion_workflow_boundary_summary(
        roadmap_phase_promotion_workflow_boundary_record()
    )

    assert "ROADMAP phase promotion workflow boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | phase_promotion_demotion_workflow_recorded_without_ci_or_signoff |"
        in summary
    )
    assert "| workflow_phrase_count | 9 |" in summary
    assert "| claim_surface_count | 6 |" in summary
    assert "| sidecar_ref_count | 7 |" in summary
    assert "| missing_evidence_count | 3 |" in summary
