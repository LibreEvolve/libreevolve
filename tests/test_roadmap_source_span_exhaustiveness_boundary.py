from libreevolve.problems.benchmarks.roadmap_source_span_exhaustiveness_boundary import (
    ROADMAP_SOURCE_SPAN_EXHAUSTIVENESS_BOUNDARY_SCHEMA,
    render_roadmap_source_span_exhaustiveness_boundary_summary,
    roadmap_source_span_exhaustiveness_boundary_record,
    validate_roadmap_source_span_exhaustiveness_boundary,
)


def test_roadmap_source_span_exhaustiveness_accepts_bounded_gate():
    boundary = roadmap_source_span_exhaustiveness_boundary_record()

    validation = validate_roadmap_source_span_exhaustiveness_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "named_structure_plus_833_bounded_claims_without_whole_paper_claim_walk"
    )
    assert boundary["schema"] == ROADMAP_SOURCE_SPAN_EXHAUSTIVENESS_BOUNDARY_SCHEMA
    assert boundary["claim_ready"] is False
    assert (
        boundary["source_coverage_boundary_input"]
        == "papers/roadmap_source_span_coverage_boundary.json"
    )
    assert boundary["source_coverage_surface_count"] == 8
    assert boundary["source_named_span_disposition_count"] == 55
    assert boundary["source_paper_status_row_count"] == 53
    assert boundary["source_paper_status_row_dispositioned_count"] == 1
    assert boundary["source_missing_evidence_count"] == 8
    assert boundary["exhaustiveness_criterion_count"] == 8
    assert boundary["sidecar_ref_count"] == 39
    assert boundary["active_todo_ref_count"] == 16
    assert [record["criterion_id"] for record in boundary["exhaustiveness_criteria"]] == [
        "pdf_section_walk",
        "figure_table_appendix_matrix",
        "application_claim_matrix",
        "status_row_disposition_map",
        "span_status_classification",
        "missing_partial_todo_proof",
        "phase_priority_map",
        "ci_exhaustiveness_and_owner_signoff",
    ]
    assert all(
        sidecar["exists"]
        for record in boundary["exhaustiveness_criteria"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        ref["exists"] and ref["required_phrase_present"]
        for record in boundary["exhaustiveness_criteria"]
        for ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "claim_level_requirement_inventory": "833_bounded_claims_cover_all_named_spans_without_whole_paper_source_detail_semantic_or_reproduction_exhaustiveness",
        "claim_level_figure_table_appendix_matrix": "bounded_named_matrix_recorded_without_result_reproduction_or_whole_paper_semantic_exhaustiveness",
        "application_result_claim_matrix": "section_3_3_claim_dispositions_recorded_without_reproduction_phase_priority_or_non_goal_proof",
        "status_row_to_roadmap_disposition_map": "not_recorded_locally",
        "missing_partial_domain_todo_proof": "not_recorded_locally",
        "non_goal_decision_map": "not_recorded_locally",
        "claim_level_phase_priority_map": "not_recorded_locally",
        "ci_source_span_exhaustiveness_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "complete named-structure gate for all 55" in boundary["claim_boundary"]
    assert "claim-level requirement exhaustiveness" in boundary["claim_boundary"]
    assert "CI source-span exhaustiveness gate" in boundary["claim_boundary"]
    assert "owner review signoff" in boundary["claim_boundary"]


def test_roadmap_source_span_exhaustiveness_rejects_overclaim_and_drift():
    boundary = roadmap_source_span_exhaustiveness_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "source_span_exhaustiveness_ready"
    boundary["exhaustiveness_criterion_count"] = 7
    boundary["source_paper_status_row_dispositioned_count"] = 53
    boundary["exhaustiveness_criteria"][0]["sidecar_refs"][0]["exists"] = False
    boundary["exhaustiveness_criteria"][0]["active_todo_refs"][0][
        "required_phrase_present"
    ] = False
    boundary["missing_evidence"]["claim_level_requirement_inventory"] = "recorded"
    boundary["required_evidence_fields"] = ["exhaustiveness_criteria"]

    validation = validate_roadmap_source_span_exhaustiveness_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_source_paper_status_row_dispositioned_count" in codes
    assert "invalid_exhaustiveness_criterion_count" in codes
    assert "invalid_exhaustiveness_criteria" in codes
    assert "invalid_missing_evidence_claim_level_requirement_inventory" in codes
    assert "missing_required_evidence_field" in codes
    assert "invalid_required_evidence_field_count" in codes


def test_render_roadmap_source_span_exhaustiveness_summary_reports_shape():
    summary = render_roadmap_source_span_exhaustiveness_boundary_summary(
        roadmap_source_span_exhaustiveness_boundary_record()
    )

    assert "ROADMAP source-span exhaustiveness boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | named_structure_plus_833_bounded_claims_without_whole_paper_claim_walk |"
        in summary
    )
    assert "| exhaustiveness_criterion_count | 8 |" in summary
    assert "| sidecar_ref_count | 39 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
