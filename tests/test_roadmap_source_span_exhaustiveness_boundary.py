from libreevolve.problems.benchmarks.alphaevolve_tex_proposition_inventory_boundary import (
    EXPECTED_PROPOSITION_COUNT,
    EXPECTED_REVIEWED_SENTENCE_COUNT,
)
from libreevolve.problems.benchmarks.alphaevolve_tex_prose_inventory_boundary import (
    EXPECTED_SENTENCE_COUNT,
)
from libreevolve.problems.benchmarks.roadmap_source_span_exhaustiveness_boundary import (
    EXPECTED_BOUNDARY_STATUS,
    EXPECTED_MISSING_EVIDENCE,
    ROADMAP_SOURCE_SPAN_EXHAUSTIVENESS_BOUNDARY_SCHEMA,
    render_roadmap_source_span_exhaustiveness_boundary_summary,
    roadmap_source_span_exhaustiveness_boundary_record,
    validate_roadmap_source_span_exhaustiveness_boundary,
)


def test_roadmap_source_span_exhaustiveness_accepts_bounded_gate():
    boundary = roadmap_source_span_exhaustiveness_boundary_record()

    validation = validate_roadmap_source_span_exhaustiveness_boundary(boundary)

    assert validation.ok is True
    assert validation.boundary_status == EXPECTED_BOUNDARY_STATUS
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
    assert boundary["sidecar_ref_count"] == 46
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
    assert boundary["missing_evidence"] == EXPECTED_MISSING_EVIDENCE
    assert "complete named-structure gate for all 55" in boundary["claim_boundary"]
    assert "claim-level requirement exhaustiveness" in boundary["claim_boundary"]
    assert "CI source-span exhaustiveness gate" in boundary["claim_boundary"]
    assert "owner review signoff" in boundary["claim_boundary"]
    assert boundary["completed_evidence"]["citation_use_count"] == 195
    assert boundary["completed_evidence"]["citation_key_link_count"] == 240
    assert boundary["completed_evidence"]["unique_compiled_reference_count"] == 120
    assert boundary["completed_evidence"]["unused_bibtex_entry_count"] == 52
    assert boundary["completed_evidence"]["tex_source_detail_count"] == 30
    assert boundary["completed_evidence"]["tex_source_detail_mapped_claim_ref_count"] == 80
    assert boundary["completed_evidence"]["tex_table_row_count"] == 83
    assert boundary["completed_evidence"]["tex_table_cell_count"] == 240
    assert boundary["completed_evidence"]["tex_table_data_row_claim_count"] == 78
    assert boundary["completed_evidence"]["tex_code_listing_environment_count"] == 8
    assert boundary["completed_evidence"]["tex_code_listing_line_count"] == 305
    assert boundary["completed_evidence"]["tex_code_listing_existing_claim_count"] == 60
    assert boundary["completed_evidence"]["tex_math_construct_count"] == 309
    assert boundary["completed_evidence"]["tex_math_inline_construct_count"] == 291
    assert boundary["completed_evidence"]["tex_math_display_construct_count"] == 18
    assert boundary["completed_evidence"]["tex_prose_paragraph_count"] == 128
    assert boundary["completed_evidence"]["tex_prose_sentence_count"] == EXPECTED_SENTENCE_COUNT
    assert boundary["completed_evidence"]["tex_prose_claim_mapped_sentence_count"] == 373
    assert boundary["completed_evidence"]["tex_prose_reviewed_nonclaim_sentence_count"] == 30
    assert boundary["completed_evidence"]["tex_prose_unmapped_sentence_count"] == 0
    assert boundary["completed_evidence"]["tex_proposition_reviewed_sentence_count"] == EXPECTED_REVIEWED_SENTENCE_COUNT
    assert boundary["completed_evidence"]["tex_proposition_count"] == EXPECTED_PROPOSITION_COUNT
    assert boundary["completed_evidence"]["tex_proposition_claim_mapped_count"] == 919
    assert boundary["completed_evidence"]["tex_proposition_context_outlook_interpretation_count"] == 66
    assert boundary["completed_evidence"]["tex_proposition_remaining_sentence_count"] == 117
    assert "all 83 rows and 240 cells" in boundary["claim_boundary"]
    assert "all 8 retained TeX code listing environments" in boundary["claim_boundary"]
    assert "all 128 retained TeX prose paragraphs" in boundary["claim_boundary"]


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
    assert f"| boundary_status | {EXPECTED_BOUNDARY_STATUS} |" in summary
    assert "| exhaustiveness_criterion_count | 8 |" in summary
    assert "| sidecar_ref_count | 46 |" in summary
    assert "| active_todo_ref_count | 16 |" in summary
    assert "| missing_evidence_count | 9 |" in summary
