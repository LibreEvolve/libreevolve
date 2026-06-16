from libreevolve.problems.benchmarks.roadmap_source_span_coverage_boundary import (
    ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_SCHEMA,
    render_roadmap_source_span_coverage_boundary_summary,
    roadmap_source_span_coverage_boundary_record,
    validate_roadmap_source_span_coverage_boundary,
)


def test_roadmap_source_span_coverage_accepts_bounded_matrix():
    boundary = roadmap_source_span_coverage_boundary_record()

    validation = validate_roadmap_source_span_coverage_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "bounded_source_span_coverage_matrix_without_exhaustive_alphaevolve_walk"
    )
    assert boundary["schema"] == ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_SCHEMA
    assert boundary["source_paper_id"] == "2506.13131"
    assert boundary["claim_ready"] is False
    assert boundary["core_anchor_disposition_count"] == 6
    assert boundary["paper_status_row_count"] == 53
    assert boundary["paper_status_row_dispositioned_count"] == 1
    assert boundary["coverage_surface_count"] == 8
    assert boundary["active_todo_ref_count"] == 15
    assert boundary["sidecar_ref_count"] == 33
    assert [record["surface_id"] for record in boundary["coverage_surface_records"]] == [
        "main_text_section_walk",
        "figure_exhibit_matrix",
        "table_capability_matrix",
        "appendix_a_matrix_targets",
        "appendix_b_constructive_math",
        "application_result_claims",
        "paper_status_row_dispositions",
        "todo_non_goal_phase_proof",
    ]
    assert all(
        sidecar["exists"]
        for record in boundary["coverage_surface_records"]
        for sidecar in record["sidecar_refs"]
    )
    assert all(
        todo_ref["exists"] and todo_ref["required_phrase_present"]
        for record in boundary["coverage_surface_records"]
        for todo_ref in record["active_todo_refs"]
    )
    assert boundary["missing_evidence"] == {
        "exhaustive_pdf_section_walk": "not_recorded_locally",
        "figure_table_appendix_matrix": "not_recorded_locally",
        "application_result_claim_matrix": "not_recorded_locally",
        "status_row_to_roadmap_disposition_map": "not_recorded_locally",
        "missing_partial_todo_proof": "not_recorded_locally",
        "non_goal_decision_map": "not_recorded_locally",
        "phase_priority_map": "not_recorded_locally",
        "ci_source_span_exhaustiveness_gate": "not_recorded_locally",
        "owner_review_signoff": "not_recorded_locally",
    }
    assert "does not claim an exhaustive PDF section walk" in boundary["claim_boundary"]


def test_roadmap_source_span_coverage_rejects_overclaim_and_drift():
    boundary = roadmap_source_span_coverage_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "exhaustive_source_span_walk_ready"
    boundary["coverage_surface_count"] = 7
    boundary["coverage_surface_records"][0]["readiness_status"] = "ready"
    boundary["missing_evidence"]["exhaustive_pdf_section_walk"] = "recorded"
    boundary["required_evidence_fields"] = ["coverage_surface_records"]

    validation = validate_roadmap_source_span_coverage_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_coverage_surface_count" in codes
    assert "invalid_coverage_surface_records" in codes
    assert "invalid_missing_evidence_exhaustive_pdf_section_walk" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_source_span_coverage_summary_reports_shape():
    summary = render_roadmap_source_span_coverage_boundary_summary(
        roadmap_source_span_coverage_boundary_record()
    )

    assert "ROADMAP source-span coverage boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | bounded_source_span_coverage_matrix_without_exhaustive_alphaevolve_walk |"
        in summary
    )
    assert "| coverage_surface_count | 8 |" in summary
    assert "| active_todo_ref_count | 15 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
