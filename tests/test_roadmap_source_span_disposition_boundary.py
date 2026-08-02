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
        == "named_span_dispositions_plus_846_bounded_claims_195_citation_uses_30_tex_source_details_240_table_cells_305_listing_lines_309_tex_math_constructs_402_tex_prose_sentences_and_382_propositions_across_136_abstract_through_section3_2_math_methodology_sentences_without_whole_paper_semantic_exhaustiveness"
    )
    assert boundary["schema"] == ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_SCHEMA
    assert boundary["source_paper_id"] == "2506.13131"
    assert boundary["claim_ready"] is False
    assert boundary["disposition_record_count"] == 55
    assert boundary["disposition_source_ref_count"] == 55
    assert boundary["paper_status_row_count"] == 53
    assert boundary["paper_status_row_dispositioned_count"] == 1
    assert boundary["scheduling_claim_inventory_input"] == (
        "papers/alphaevolve_scheduling_claim_inventory_boundary.json"
    )
    assert boundary["kernel_claim_inventory_input"] == (
        "papers/alphaevolve_kernel_claim_inventory_boundary.json"
    )
    assert boundary["hardware_claim_inventory_input"] == (
        "papers/alphaevolve_hardware_claim_inventory_boundary.json"
    )
    assert boundary["compiler_claim_inventory_input"] == (
        "papers/alphaevolve_compiler_claim_inventory_boundary.json"
    )
    assert boundary["ablation_claim_inventory_input"] == (
        "papers/alphaevolve_ablation_claim_inventory_boundary.json"
    )
    assert boundary["related_work_claim_inventory_input"] == (
        "papers/alphaevolve_related_work_claim_inventory_boundary.json"
    )
    assert boundary["appendix_a_claim_inventory_input"] == (
        "papers/alphaevolve_appendix_a_claim_inventory_boundary.json"
    )
    assert boundary["appendix_b_claim_inventory_input"] == (
        "papers/alphaevolve_appendix_b_claim_inventory_boundary.json"
    )
    assert boundary["citation_use_inventory_input"] == (
        "papers/alphaevolve_citation_use_inventory_boundary.json"
    )
    assert boundary["tex_source_detail_inventory_input"] == (
        "papers/alphaevolve_tex_source_detail_inventory_boundary.json"
    )
    assert boundary["tex_table_cell_inventory_input"] == (
        "papers/alphaevolve_tex_table_cell_inventory_boundary.json"
    )
    assert boundary["tex_code_listing_inventory_input"] == (
        "papers/alphaevolve_tex_code_listing_inventory_boundary.json"
    )
    assert boundary["tex_math_inventory_input"] == (
        "papers/alphaevolve_tex_math_inventory_boundary.json"
    )
    assert boundary["tex_prose_inventory_input"] == (
        "papers/alphaevolve_tex_prose_inventory_boundary.json"
    )
    assert boundary["tex_proposition_inventory_input"] == (
        "papers/alphaevolve_tex_proposition_inventory_boundary.json"
    )
    assert boundary["completed_evidence"]["citation_uses"] == (
        "195_tex_source_anchored_uses_with_240_key_links_and_120_compiled_references_without_semantic_classification"
    )
    assert boundary["completed_evidence"]["tex_source_details"] == (
        "30_construct_level_dispositions_for_22_captions_5_equation_environment_constructs_and_3_semantic_footnotes"
    )
    assert boundary["completed_evidence"]["tex_table_cells"] == (
        "83_rows_240_cells_78_existing_claims_and_zero_unmapped_units"
    )
    assert boundary["completed_evidence"]["tex_code_listing_lines"] == (
        "8_environments_305_lines_60_existing_claims_and_zero_unmapped_lines"
    )
    assert boundary["completed_evidence"]["tex_math_constructs"] == (
        "309_explicit_math_constructs_291_inline_18_display_and_zero_unmapped_constructs"
    )
    assert boundary["completed_evidence"]["tex_prose_sentences"] == (
        "128_paragraphs_402_sentences_372_existing_claim_mappings_30_reviewed_nonclaims_and_zero_unmapped_or_unresolved_sentences"
    )
    assert boundary["completed_evidence"]["tex_propositions"] == (
        "136_abstract_through_section3_2_math_methodology_sentences_382_atomic_propositions_345_existing_claim_mappings_37_context_outlook_or_interpretation_and_zero_unmapped_or_unresolved_propositions"
    )
    assert (
        boundary["paper_status_row_disposition_status"]
        == "paper_index_rows_not_exhaustively_roadmapped"
    )
    first_record = boundary["disposition_records"][0]
    assert first_record == {
        "span_id": "abstract",
        "source_kind": "structure",
        "source_label": "Abstract",
        "source_refs": ["2506.13131:pages 1"],
        "source_ref_count": 1,
        "source_anchor_count": 1,
        "source_anchors_verified": True,
        "local_claim_status": "mixed_implemented_partial_missing_and_undemonstrated",
        "roadmap_section_id": "documentation_truthfulness",
        "roadmap_phase": "near_term",
        "coverage_scope": "named_structure_span",
        "sidecar_refs": [
            "papers/alphaevolve_context_claim_inventory_boundary.json"
        ],
        "todo_refs": [
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add exhaustive implementation-evidence mapping for AlphaEvolve",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "Add ROADMAP AlphaEvolve source-span disposition coverage.",
            },
        ],
        "disposition_status": "named_structure_disposition_only",
    }
    assert boundary["missing_evidence"] == {
        "claim_level_requirement_inventory": "846_bounded_claims_cover_all_named_spans_195_citation_uses_have_lexical_linkage_30_tex_source_details_have_construct_dispositions_240_table_cells_have_row_cell_dispositions_305_listing_lines_have_line_dispositions_309_explicit_math_constructs_have_delimiter_dispositions_128_paragraphs_402_sentences_have_prose_dispositions_and_136_abstract_through_section3_2_math_methodology_sentences_have_382_proposition_dispositions_without_remaining_266_sentence_proposition_image_pixel_citation_semantic_implementation_semantic_mathematical_correctness_independent_review_or_reproduction_exhaustiveness",
        "application_result_claim_matrix": "not_recorded_locally",
        "status_row_to_roadmap_disposition_map": "not_recorded_locally",
        "missing_partial_todo_proof": "not_recorded_locally",
        "ci_source_span_exhaustiveness_gate": "not_recorded_locally",
    }
    assert "all 55 PDF-verified named AlphaEvolve structural spans" in boundary["claim_boundary"]
    assert "remaining 266 prose sentences" in boundary["claim_boundary"]
    assert "all 83 rows and 240 cells" in boundary["claim_boundary"]
    assert "all 8 retained TeX code listing environments" in boundary["claim_boundary"]
    assert "all 128 retained TeX prose paragraphs" in boundary["claim_boundary"]


def test_roadmap_source_span_disposition_rejects_exhaustive_overclaim():
    boundary = roadmap_source_span_disposition_boundary_record()
    boundary["claim_ready"] = True
    boundary["boundary_status"] = "exhaustive_source_span_matrix_ready"
    boundary["paper_status_row_disposition_status"] = "all_rows_dispositioned"
    boundary["disposition_records"][0]["coverage_scope"] = "exhaustive"
    boundary["missing_evidence"]["claim_level_requirement_inventory"] = "recorded"
    boundary["required_evidence_fields"] = ["core_requirement_anchor_dispositions"]

    validation = validate_roadmap_source_span_disposition_boundary(boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "claim_ready_overclaim" in codes
    assert "invalid_boundary_status" in codes
    assert "invalid_paper_status_row_disposition_status" in codes
    assert "invalid_disposition_records" in codes
    assert "invalid_missing_evidence_claim_level_requirement_inventory" in codes
    assert "missing_required_evidence_field" in codes


def test_render_roadmap_source_span_disposition_summary_reports_shape():
    summary = render_roadmap_source_span_disposition_boundary_summary(
        roadmap_source_span_disposition_boundary_record()
    )

    assert "ROADMAP source-span disposition boundary" in summary
    assert "| schema_status | ok |" in summary
    assert (
        "| boundary_status | named_span_dispositions_plus_846_bounded_claims_195_citation_uses_30_tex_source_details_240_table_cells_305_listing_lines_309_tex_math_constructs_402_tex_prose_sentences_and_382_propositions_across_136_abstract_through_section3_2_math_methodology_sentences_without_whole_paper_semantic_exhaustiveness |"
        in summary
    )
    assert "| disposition_record_count | 55 |" in summary
    assert "| missing_evidence_count | 5 |" in summary
