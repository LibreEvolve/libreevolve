from libreevolve.problems.benchmarks.roadmap_claim_evidence_boundary import (
    ROADMAP_CLAIM_EVIDENCE_BOUNDARY_SCHEMA,
    render_roadmap_claim_evidence_boundary_summary,
    roadmap_claim_evidence_boundary_record,
    validate_roadmap_claim_evidence_boundary,
)


def test_roadmap_claim_evidence_accepts_bounded_claim_map():
    boundary = roadmap_claim_evidence_boundary_record()

    validation = validate_roadmap_claim_evidence_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_roadmap_claim_evidence_map_without_semantic_freshness_verifier"
    )
    assert boundary["schema"] == ROADMAP_CLAIM_EVIDENCE_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert boundary["current_state_heading_present"] is True
    assert boundary["good_first_heading_present"] is True
    assert boundary["roadmap_current_state_bullet_count"] == 61
    assert boundary["roadmap_good_first_item_count"] == 4
    assert boundary["claim_surface_count"] == 6
    assert boundary["sidecar_ref_count"] == 12
    assert boundary["active_todo_ref_count"] == 12
    assert [record["surface_id"] for record in boundary["claim_surface_records"]] == [
        "roadmap_scope_preamble",
        "current_state_bullet_inventory",
        "implementation_evidence_links",
        "good_first_priority_claims",
        "cross_document_claim_sync",
        "alignment_report_publication",
    ]
    assert all(record["roadmap_phrase_present"] for record in boundary["claim_surface_records"])
    assert all(
        sidecar["exists"]
        for record in boundary["claim_surface_records"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        todo_ref["exists"] and todo_ref["required_phrase_present"]
        for record in boundary["claim_surface_records"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "complete_current_state_claim_inventory": "not_recorded_locally",
        "per_bullet_code_test_runtime_evidence_map": "not_recorded_locally",
        "semantic_evidence_sufficiency_verifier": "not_recorded_locally",
        "stale_current_state_detector": "not_recorded_locally",
        "stale_priority_detector": "not_recorded_locally",
        "cross_document_claim_freshness_report": "not_recorded_locally",
        "generated_alignment_report": "not_recorded_locally",
        "ci_semantic_claim_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim complete per-bullet claim ids" in boundary["claim_boundary"]


def test_roadmap_claim_evidence_rejects_overclaim_and_drift():
    boundary = roadmap_claim_evidence_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "semantic_roadmap_claim_verifier_ready"
    boundary["roadmap_current_state_bullet_count"] = 0
    boundary["claim_surface_records"][0]["roadmap_phrase_present"] = False
    boundary["missing_evidence"]["generated_alignment_report"] = "recorded"
    boundary["required_evidence_fields"] = ["claim_surface_records"]

    validation = validate_roadmap_claim_evidence_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_roadmap_current_state_bullet_count" in codes
    assert "invalid_claim_surface_records" in codes
    assert "invalid_missing_evidence_generated_alignment_report" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_claim_evidence_summary_reports_shape():
    summary = render_roadmap_claim_evidence_boundary_summary(
        roadmap_claim_evidence_boundary_record()
    )

    assert "ROADMAP claim evidence boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_roadmap_claim_evidence_map_without_semantic_freshness_verifier |"
        in summary
    )
    assert "| claim_surface_count | 6 |" in summary
    assert "| current_state_bullet_count | 61 |" in summary
    assert "| good_first_item_count | 4 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
