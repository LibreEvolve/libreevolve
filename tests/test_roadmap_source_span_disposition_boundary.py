from libreevolve.problems.benchmarks.roadmap_source_span_disposition_boundary import (
    ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_SCHEMA,
    render_roadmap_source_span_disposition_boundary_summary,
    roadmap_source_span_disposition_boundary_record,
    validate_roadmap_source_span_disposition_boundary,
)


def test_roadmap_source_span_disposition_accepts_core_anchor_boundary():
    boundary = roadmap_source_span_disposition_boundary_record()

    validation = validate_roadmap_source_span_disposition_boundary(boundary)

    assert validation.ok is True
    assert (
        validation.boundary_status
        == "core_anchor_dispositions_without_exhaustive_source_span_matrix"
    )
    assert boundary["schema"] == ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_SCHEMA
    assert boundary["source_paper_id"] == "2506.13131"
    assert boundary["claim_ready"] is False
    assert boundary["disposition_record_count"] == 6
    assert boundary["disposition_source_ref_count"] == 13
    assert boundary["paper_status_row_count"] == 53
    assert boundary["paper_status_row_dispositioned_count"] == 1
    assert (
        boundary["paper_status_row_disposition_status"]
        == "paper_index_rows_not_exhaustively_roadmapped"
    )
    first_record = boundary["disposition_records"][0]
    assert first_record == {
        "requirement_id": "alphaevolve_program_markers",
        "source_refs": ["2506.13131:Section 2.1", "2506.13131:Figure 3"],
        "source_ref_count": 2,
        "local_claim_status": "partially_implemented",
        "roadmap_section_id": "candidate_workspace_fidelity",
        "roadmap_phase": "near_term",
        "coverage_scope": "anchor_only",
        "sidecar_refs": [
            "papers/existing_codebase_integration_boundary.json",
            "papers/candidate_language_runner_boundary.json",
        ],
        "todo_refs": [
            "docs/todo/code.md#candidate-workspace-fidelity",
            "docs/todo/papers.md#candidate-language-build-and-runner-contracts",
        ],
        "disposition_status": "core_anchor_only_not_exhaustive_source_span",
    }
    assert boundary["missing_evidence"] == {
        "exhaustive_pdf_section_walk": "not_recorded_locally",
        "figure_table_appendix_matrix": "not_recorded_locally",
        "application_result_claim_matrix": "not_recorded_locally",
        "status_row_to_roadmap_disposition_map": "not_recorded_locally",
        "missing_partial_todo_proof": "not_recorded_locally",
        "ci_source_span_exhaustiveness_gate": "not_recorded_locally",
    }
    assert "does not claim an exhaustive retained-PDF section walk" in boundary["claim_boundary"]


def test_roadmap_source_span_disposition_rejects_exhaustive_overclaim():
    boundary = roadmap_source_span_disposition_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "exhaustive_source_span_matrix_ready"
    boundary["paper_status_row_disposition_status"] = "all_rows_dispositioned"
    boundary["disposition_records"][0]["coverage_scope"] = "exhaustive"
    boundary["missing_evidence"]["exhaustive_pdf_section_walk"] = "recorded"
    boundary["required_evidence_fields"] = ["core_requirement_anchor_dispositions"]

    validation = validate_roadmap_source_span_disposition_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_paper_status_row_disposition_status" in codes
    assert "invalid_disposition_records" in codes
    assert "invalid_missing_evidence_exhaustive_pdf_section_walk" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_source_span_disposition_summary_reports_shape():
    summary = render_roadmap_source_span_disposition_boundary_summary(
        roadmap_source_span_disposition_boundary_record()
    )

    assert "ROADMAP source-span disposition boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | core_anchor_dispositions_without_exhaustive_source_span_matrix |"
        in summary
    )
    assert "| disposition_record_count | 6 |" in summary
    assert "| missing_evidence_count | 6 |" in summary
