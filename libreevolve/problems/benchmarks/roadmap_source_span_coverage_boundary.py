from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_source_span_disposition_boundary import (
    roadmap_source_span_disposition_boundary_record,
)


ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_source_span_coverage_boundary.v27"
)
EXPECTED_BOUNDARY_STATUS = (
    "named_structure_plus_846_bounded_claims_195_citation_uses_"
    "30_tex_source_details_240_table_cells_305_listing_lines_309_tex_math_"
    "constructs_402_tex_prose_sentences_and_812_propositions_across_244_"
    "abstract_through_section4_ablation_sentences_"
    "without_whole_paper_semantic_exhaustiveness"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "coverage_surface_records",
    "named_source_inventory_input",
    "named_source_span_disposition_input",
    "paper_status_row_count",
    "claim_level_requirement_inventory",
    "application_result_claim_matrix",
    "status_row_to_roadmap_disposition_map",
    "missing_partial_todo_proof",
    "non_goal_decision_map",
    "phase_priority_map",
    "ci_source_span_exhaustiveness_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "claim_level_requirement_inventory": "846_bounded_claims_cover_all_named_spans_195_citation_uses_have_lexical_linkage_30_tex_source_details_have_construct_dispositions_240_table_cells_have_row_cell_dispositions_305_listing_lines_have_line_dispositions_309_explicit_math_constructs_have_delimiter_dispositions_128_paragraphs_402_sentences_have_prose_dispositions_and_244_abstract_through_section4_ablation_sentences_have_812_proposition_dispositions_without_remaining_158_sentence_proposition_image_pixel_citation_semantic_implementation_semantic_mathematical_correctness_independent_review_or_reproduction_exhaustiveness",
    "application_result_claim_matrix": "section_3_3_claim_dispositions_recorded_without_reproduction_phase_priority_or_non_goal_proof",
    "status_row_to_roadmap_disposition_map": "not_recorded_locally",
    "missing_partial_todo_proof": "not_recorded_locally",
    "non_goal_decision_map": "not_recorded_locally",
    "phase_priority_map": "not_recorded_locally",
    "ci_source_span_exhaustiveness_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


COVERAGE_SURFACE_SPECS = (
    {
        "surface_id": "main_text_section_walk",
        "source_surface": "AlphaEvolve main-text sections and requirement claims",
        "current_scope": "PDF-verified named main-text sections plus 56 Table 1/Section 2 system requirements, 45 Abstract/Introduction/Discussion/collaborator claims, 44 Section 3.1/Table 2/Figure 4 matrix-result claims, 63 Section 3.2/Figure 5 constructive-math claims, 45 Section 3.3 opening/Section 3.3.1/Figure 6 scheduling claims, 59 Section 3.3.2/Figure 7 kernel-engineering claims, 35 Section 3.3.3 hardware-circuit-design claims, 44 Section 3.3.4 compiler-generated-code claims, 51 Section 4/Figure 8 ablation claims, 85 Section 5 Related Work claims, 131 Appendix A/Table 3/Figure 9 claims, and 188 Appendix B/Figures 10-14 claims with implementation, context-only, or TODO disposition; all 195 retained-TeX citation uses have lexical key linkage; all 30 retained-source captions, five equation-environment constructs, and semantic footnotes have construct-level dispositions; all 83 table rows and 240 cells have row/cell dispositions; all 8 retained TeX code listing environments and 305 physical source lines have environment/line dispositions; all 309 explicit TeX math constructs have delimiter-level dispositions; all 128 retained TeX prose paragraphs and 402 grammatical sentences have dispositions; and all 244 sentences from the Abstract through Section 4 ablations have 812 atomic-proposition dispositions",
        "missing_readiness": "proposition review for the remaining 158 prose sentences plus image-pixel, citation-semantic, implementation-semantic, mathematical-correctness, independent-review, and result-reproduction evidence",
        "sidecars": (
            "papers/roadmap_source_span_disposition_boundary.json",
            "papers/implementation_evidence_map_boundary.json",
            "papers/alphaevolve_system_requirement_inventory_boundary.json",
            "papers/alphaevolve_context_claim_inventory_boundary.json",
            "papers/alphaevolve_matrix_result_claim_inventory_boundary.json",
            "papers/alphaevolve_math_result_claim_inventory_boundary.json",
            "papers/alphaevolve_scheduling_claim_inventory_boundary.json",
            "papers/alphaevolve_kernel_claim_inventory_boundary.json",
            "papers/alphaevolve_hardware_claim_inventory_boundary.json",
            "papers/alphaevolve_compiler_claim_inventory_boundary.json",
            "papers/alphaevolve_ablation_claim_inventory_boundary.json",
            "papers/alphaevolve_related_work_claim_inventory_boundary.json",
            "papers/alphaevolve_appendix_a_claim_inventory_boundary.json",
            "papers/alphaevolve_appendix_b_claim_inventory_boundary.json",
            "papers/alphaevolve_citation_use_inventory_boundary.json",
            "papers/alphaevolve_tex_source_detail_inventory_boundary.json",
            "papers/alphaevolve_tex_code_listing_inventory_boundary.json",
            "papers/alphaevolve_tex_math_inventory_boundary.json",
            "papers/alphaevolve_tex_prose_inventory_boundary.json",
            "papers/alphaevolve_tex_proposition_inventory_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "named sections, figures, tables, and",
            },
        ),
        "validation_gate": "section-level source-span disposition matrix",
        "readiness_status": "846_bounded_claims_plus_195_lexical_citation_uses_30_dispositioned_tex_source_details_240_dispositioned_table_cells_305_dispositioned_listing_lines_309_dispositioned_tex_math_constructs_402_dispositioned_tex_prose_sentences_and_812_dispositioned_propositions_across_244_abstract_through_section4_ablation_sentences_without_remaining_158_sentence_proposition_semantic_exhaustiveness",
    },
    {
        "surface_id": "figure_exhibit_matrix",
        "source_surface": "AlphaEvolve figures and process/result exhibits",
        "current_scope": "all 14 numbered figure spans are page- and anchor-verified; Figures 1-3 have claim-level system requirements, Figure 4 has claim-level matrix dispositions, Figure 5 has claim-level constructive-math dispositions, Figure 6 has claim-level scheduling dispositions, Figure 7 has claim-level kernel-engineering dispositions, Figure 8 has claim-level ablation dispositions, Figure 9 has 48 panel-level code and caption dispositions, and Figures 10-14 have 27 caption and visual dispositions",
        "missing_readiness": "Figure 4-14 local result and rendered-exhibit reproduction evidence",
        "sidecars": (
            "papers/alphaevolve_system_requirement_inventory_boundary.json",
            "papers/process_exhibit_boundary.json",
            "papers/figure3_supervised_exhibit_boundary.json",
            "papers/figure6_scheduling_exhibit_boundary.json",
            "papers/figure7_pallas_tiling_exhibit_boundary.json",
            "papers/figure8_ablation_artifacts.json",
            "papers/alphaevolve_ablation_claim_inventory_boundary.json",
            "papers/figure4_matrix_discovery_artifacts.json",
            "papers/figure9_matrix_diff_artifacts.json",
            "papers/alphaevolve_math_result_claim_inventory_boundary.json",
            "papers/alphaevolve_scheduling_claim_inventory_boundary.json",
            "papers/alphaevolve_kernel_claim_inventory_boundary.json",
            "papers/alphaevolve_appendix_a_claim_inventory_boundary.json",
            "papers/alphaevolve_appendix_b_claim_inventory_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "figures",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "rendered diagram",
            },
        ),
        "validation_gate": "figure/table artifact disposition matrix",
        "readiness_status": "figures_1_14_bounded_claim_inventory_without_result_exhibit_reproduction",
    },
    {
        "surface_id": "table_capability_matrix",
        "source_surface": "AlphaEvolve tables and capability/result comparison claims",
        "current_scope": "all three numbered table spans are page- and anchor-verified; all 83 rows and 240 cells have source-pinned semantic dispositions; all eight Table 1 capability rows, all sixteen selected Table 2 rank rows, and all 54 Table 3 rows map to existing bounded claims",
        "missing_readiness": "Table 2 and Table 3 result reproduction with exact decomposition and certificate evidence",
        "sidecars": (
            "papers/alphaevolve_system_requirement_inventory_boundary.json",
            "papers/table1_capability_exhibit_boundary.json",
            "papers/matrix_rank_table_artifacts.json",
            "papers/matrix_suite_publication_artifacts.json",
            "papers/alphaevolve_appendix_a_claim_inventory_boundary.json",
            "papers/alphaevolve_tex_table_cell_inventory_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "tables",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Table 1",
            },
        ),
        "validation_gate": "table row to ROADMAP/TODO disposition matrix",
        "readiness_status": "tables_1_3_row_cell_dispositions_complete_without_tables_2_3_reproduction",
    },
    {
        "surface_id": "appendix_a_matrix_targets",
        "source_surface": "Appendix A matrix-target registry and related artifacts",
        "current_scope": "Appendix A, all 54 Table 3 rows, and 48 Figure 9 panel claims are PDF-anchored with implementation status and TODO ownership",
        "missing_readiness": "Appendix A result reproduction, exact decompositions, certificates, emitted Figure 9 artifacts, and local resource-frontier evidence",
        "sidecars": (
            "papers/appendix_a_matrix_curation.json",
            "papers/appendix_a_matrix_resource_frontier.json",
            "papers/appendix_a_matrix_row_note_artifacts.json",
            "papers/matrix_tensor_rank_runtime_boundary.json",
            "papers/matrix_cascade_run_runtime_boundary.json",
            "papers/alphaevolve_appendix_a_claim_inventory_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "appendix",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Appendix A",
            },
        ),
        "validation_gate": "Appendix A row-to-roadmap disposition matrix",
        "readiness_status": "named_appendix_a_complete_without_result_row_exhaustiveness",
    },
    {
        "surface_id": "appendix_b_constructive_math",
        "source_surface": "Appendix B constructive-math families and result claims",
        "current_scope": "Appendix B, all 13 named subsections, and Figures 10-14 have 188 PDF- and visual-anchored claim dispositions alongside the 63 Section 3.2/Figure 5 constructive-math dispositions",
        "missing_readiness": "Appendix B construction payloads, executable verification, result recomputation, rendered-exhibit reproduction, and explicit non-goal decisions",
        "sidecars": (
            "papers/math_outcome_boundary.json",
            "papers/math_starting_construction_boundary.json",
            "papers/math_heuristic_handoff_boundary.json",
            "papers/math_heuristic_stage_sequence_boundary.json",
            "papers/alphaevolve_math_result_claim_inventory_boundary.json",
            "papers/alphaevolve_appendix_b_claim_inventory_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "benchmark family",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Appendix B",
            },
        ),
        "validation_gate": "Appendix B family/result disposition matrix",
        "readiness_status": "appendix_b_claim_inventory_complete_without_result_reproduction",
    },
    {
        "surface_id": "application_result_claims",
        "source_surface": "AlphaEvolve application-result claims for systems, kernels, hardware, and compiler work",
        "current_scope": "all named Section 3.3 application subsections and Figures 6-7 are page- and anchor-verified; the Section 3.3 opening, Section 3.3.1, and Figure 6 have 45 scheduling claim dispositions, Section 3.3.2 and Figure 7 have 59 kernel-engineering claim dispositions, Section 3.3.3 has 35 hardware-circuit-design claim dispositions, and Section 3.3.4 has 44 compiler-generated-code claim dispositions alongside systems absence/readiness boundaries",
        "missing_readiness": "application-result reproduction artifacts, claim-level phase priority, and domain TODO/non-goal proof beyond the bounded Section 3.3 disposition matrix",
        "sidecars": (
            "papers/systems_result_readiness_boundary.json",
            "papers/alphaevolve_scheduling_claim_inventory_boundary.json",
            "papers/alphaevolve_kernel_claim_inventory_boundary.json",
            "papers/alphaevolve_hardware_claim_inventory_boundary.json",
            "papers/alphaevolve_compiler_claim_inventory_boundary.json",
            "papers/compiler_stack_context_boundary.json",
            "papers/compiler_adoption_path_boundary.json",
            "papers/hardware_rtl_eda_evidence_boundary.json",
            "papers/hardware_rewrite_artifact_boundary.json",
            "papers/magellan_boundary.json",
            "papers/archagent_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "application-result claim",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Keep named AlphaEvolve application-context rows background-only",
            },
        ),
        "validation_gate": "application-result claim to ROADMAP/TODO disposition matrix",
        "readiness_status": "section_3_3_claim_dispositions_complete_without_application_reproduction",
    },
    {
        "surface_id": "paper_status_row_dispositions",
        "source_surface": "paper-index status rows and source-specific sidecars",
        "current_scope": "paper-index rows and structural status-claim inventory without complete ROADMAP disposition",
        "missing_readiness": "all paper/status sidecar rows mapped to ROADMAP dispositions or explicit non-goals",
        "sidecars": (
            "papers/status_claim_inventory.json",
            "papers/roadmap_source_span_disposition_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "disposition every paper/status row",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "semantic evidence mapping for every paper-index status row",
            },
        ),
        "validation_gate": "paper-status row to ROADMAP disposition map",
        "readiness_status": "status_rows_not_exhaustively_roadmapped",
    },
    {
        "surface_id": "todo_non_goal_phase_proof",
        "source_surface": "missing/partial source spans, non-goals, and phase priority",
        "current_scope": "separate TODO, non-goal, and phase-sequence boundaries",
        "missing_readiness": "proof every missing/partial span has an active TODO, non-goal decision, and phase priority",
        "sidecars": (
            "papers/todo_canonical_gap_boundary.json",
            "papers/roadmap_non_goal_contradiction_boundary.json",
            "papers/roadmap_phase_sequence_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "domain-specific missing/partial TODO proof",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "phase-priority map",
            },
        ),
        "validation_gate": "missing/partial source-span TODO and phase proof",
        "readiness_status": "separate_boundaries_without_span_level_join",
    },
)


@dataclass(frozen=True)
class RoadmapSourceSpanCoverageBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapSourceSpanCoverageBoundaryValidation:
    ok: bool
    boundary_status: str | None
    coverage_surface_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapSourceSpanCoverageBoundaryIssue]


def roadmap_source_span_coverage_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP AlphaEvolve source-span coverage matrix."""

    root_path = Path(root)
    disposition = roadmap_source_span_disposition_boundary_record(root_path)
    records = [_coverage_surface_record(root_path, spec) for spec in COVERAGE_SURFACE_SPECS]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    return {
        "schema": ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "named_source_inventory_input": "papers/alphaevolve_source_inventory_boundary.json",
        "named_source_span_disposition_input": "papers/roadmap_source_span_disposition_boundary.json",
        "named_source_span_disposition_count": disposition["disposition_record_count"],
        "paper_status_row_count": disposition["paper_status_row_count"],
        "paper_status_row_dispositioned_count": disposition[
            "paper_status_row_dispositioned_count"
        ],
        "coverage_surface_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "coverage_surface_records": records,
        "completed_evidence": {
            "named_structure_span_count": disposition["disposition_record_count"],
            "named_structure_source_ref_count": disposition["disposition_source_ref_count"],
            "named_structure_scope": "38_structure_14_figure_3_table_spans",
            "section_2_system_requirement_count": 56,
            "section_2_system_requirement_scope": "table_1_sections_2_1_through_2_6_figures_1_through_3",
            "context_claim_count": 45,
            "context_claim_scope": "abstract_introduction_discussion_and_collaborator_context",
            "matrix_result_claim_count": 44,
            "matrix_result_claim_scope": "section_3_1_table_2_figure_4_and_footnote_3",
            "math_result_claim_count": 63,
            "math_result_claim_scope": "section_3_2_and_figure_5",
            "scheduling_claim_count": 45,
            "scheduling_claim_scope": "section_3_3_opening_section_3_3_1_and_figure_6",
            "kernel_claim_count": 59,
            "kernel_claim_scope": "section_3_3_2_and_figure_7",
            "hardware_claim_count": 35,
            "hardware_claim_scope": "section_3_3_3",
            "compiler_claim_count": 44,
            "compiler_claim_scope": "section_3_3_4",
            "ablation_claim_count": 51,
            "ablation_claim_scope": "section_4_and_figure_8",
            "related_work_claim_count": 85,
            "related_work_claim_scope": "section_5_related_work",
            "related_work_source_context_only_count": 59,
            "related_work_implementation_relevant_count": 26,
            "appendix_a_claim_count": 131,
            "appendix_a_claim_scope": "appendix_a_table_3_and_figure_9",
            "appendix_a_table_3_row_claim_count": 54,
            "appendix_a_figure_9_claim_count": 48,
            "appendix_b_claim_count": 188,
            "appendix_b_subsection_count": 13,
            "appendix_b_figures_10_14_claim_count": 27,
            "citation_use_count": 195,
            "citation_key_link_count": 240,
            "unique_compiled_reference_count": 120,
            "unused_bibtex_entry_count": 52,
            "citation_use_inventory": "tex_source_line_and_bibliography_key_linkage_verified_without_semantic_classification",
            "tex_source_detail_count": 30,
            "tex_source_detail_caption_count": 22,
            "tex_source_detail_equation_count": 5,
            "tex_source_detail_footnote_count": 3,
            "tex_source_detail_mapped_claim_ref_count": 80,
            "tex_source_detail_inventory": "construct_level_disposition_verified_without_proposition_level_semantic_exhaustiveness",
            "tex_table_row_count": 83,
            "tex_table_cell_count": 240,
            "tex_table_data_row_claim_count": 78,
            "tex_table_bounded_claim_component_cell_count": 218,
            "tex_table_cell_inventory": "row_cell_disposition_verified_without_citation_semantics_or_result_reproduction",
            "tex_code_listing_environment_count": 8,
            "tex_code_listing_line_count": 305,
            "tex_code_listing_bounded_claim_component_line_count": 214,
            "tex_code_listing_existing_claim_count": 60,
            "tex_code_listing_inventory": "environment_line_disposition_verified_without_listing_execution_or_result_reproduction",
            "tex_math_construct_count": 309,
            "tex_math_inline_construct_count": 291,
            "tex_math_display_construct_count": 18,
            "tex_math_inventory": "explicit_delimiter_disposition_verified_without_mathematical_correctness_or_result_reproduction",
            "tex_prose_paragraph_count": 128,
            "tex_prose_sentence_count": 402,
            "tex_prose_claim_mapped_sentence_count": 372,
            "tex_prose_reviewed_nonclaim_sentence_count": 30,
            "tex_prose_unmapped_sentence_count": 0,
            "tex_prose_inventory": "paragraph_and_sentence_disposition_verified_without_sentence_internal_clause_or_proposition_exhaustiveness",
            "tex_proposition_reviewed_sentence_count": 244,
            "tex_proposition_count": 812,
            "tex_proposition_claim_mapped_count": 753,
            "tex_proposition_context_outlook_interpretation_count": 59,
            "tex_proposition_remaining_sentence_count": 158,
            "tex_proposition_inventory": "abstract_through_section4_ablation_atomic_proposition_disposition_verified_without_remaining_paper_or_independent_semantic_exhaustiveness",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a ROADMAP-level AlphaEvolve source-span "
            "coverage matrix for all 55 PDF-verified named main-text sections, "
            "figures, tables, Appendix A/B spans, and named application sections, "
            "plus 846 bounded claim-level records across Table 1, Section 2, "
            "the Abstract, Introduction, Discussion, collaborator context, "
            "Section 3.1, Table 2, Figure 4, footnote 3, Section 3.2, Figure 5, "
            "the Section 3.3 opening, Section 3.3.1, Figure 6, Section 3.3.2, "
            "Figure 7, Section 3.3.3, Section 3.3.4, Section 4, Figure 8, and "
            "Section 5 Related Work, Appendix A, Table 3, and Figure 9. The "
            "Section 5 inventory separates 59 source-context-only literature "
            "claims from 26 implementation-relevant claims. The Appendix A "
            "inventory records 29 prose/caption claims, all 54 Table 3 rows, "
            "and 48 Figure 9 claims. The Appendix B inventory records 188 "
            "claims across all 13 subsections and Figures 10-14. It also "
            "records lexical source and bibliography linkage for all 195 TeX "
            "citation uses, 240 key links, and 120 compiled references without "
            "classifying supported propositions, source sufficiency, or "
            "implementation relevance. It also records construct-level "
            "dispositions for all 30 retained-source captions, displayed "
            "equations, and semantic footnotes, plus row- and cell-level "
            "dispositions for all 83 rows and 240 cells in Tables 1-3, plus "
            "environment- and line-level dispositions for all 8 retained TeX "
            "code listing environments and all 305 physical source lines, plus "
            "delimiter-level dispositions for all 309 explicit TeX math constructs, "
            "split into 291 inline and 18 display constructs, without claiming "
            "mathematical correctness or result reproduction, plus paragraph- "
            "and sentence-level dispositions for all 128 retained TeX prose "
            "paragraphs and all 402 grammatical sentences, with 372 mapped to "
            "existing bounded claims, 30 reviewed as nonclaims, and zero unmapped "
            "or unresolved sentences, plus 812 atomic propositions across all 244 "
            "sentences from the Abstract through Section 4 ablations, "
            "with 753 mapped to bounded claims and 59 "
            "dispositioned as context, "
            "outlook, or interpretation. It does not claim proposition coverage "
            "for the remaining 158 prose "
            "sentences or independent semantic exhaustiveness, image-pixel coverage, "
            "citation-level proposition exhaustiveness, or independent semantic "
            "review. It also records "
            "paper-status rows, and TODO/non-goal/phase proof. It does not "
            "claim whole-paper claim-level requirement exhaustiveness, a complete application-result claim matrix, "
            "status-row to ROADMAP disposition map, missing/partial TODO "
            "proof, non-goal decision map, phase-priority map, CI source-span "
            "exhaustiveness gate, or owner review signoff."
        ),
    }


def validate_roadmap_source_span_coverage_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapSourceSpanCoverageBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_source_span_coverage_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapSourceSpanCoverageBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = roadmap_source_span_coverage_boundary_record(root)
    issues: list[RoadmapSourceSpanCoverageBoundaryIssue] = []
    if data.get("schema") != ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP source-span coverage boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP source-span coverage boundary must not claim exhaustive readiness"))
    for key in (
        "named_source_inventory_input",
        "named_source_span_disposition_input",
        "named_source_span_disposition_count",
        "paper_status_row_count",
        "paper_status_row_dispositioned_count",
        "coverage_surface_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "coverage_surface_records",
        "completed_evidence",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current source-span coverage inputs"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "all 55 PDF-verified named" not in boundary_text
        or "all 30 retained-source captions" not in boundary_text
        or "all 83 rows and 240 cells" not in boundary_text
        or "all 8 retained TeX code listing environments and all 305 physical source lines" not in boundary_text
        or "all 309 explicit TeX math constructs" not in boundary_text
        or "all 128 retained TeX prose paragraphs and all 402 grammatical sentences" not in boundary_text
        or "remaining 158 prose sentences" not in boundary_text
        or "citation-level proposition exhaustiveness" not in boundary_text
        or "claim-level requirement exhaustiveness" not in boundary_text
        or "complete application-result claim matrix" not in boundary_text
        or "CI source-span exhaustiveness gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded coverage mapping from exhaustive source-span proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapSourceSpanCoverageBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        coverage_surface_count=data.get("coverage_surface_count") if isinstance(data.get("coverage_surface_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_source_span_coverage_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_source_span_coverage_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP source-span coverage boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| coverage_surface_count | {validation.coverage_surface_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _coverage_surface_record(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "surface_id": spec["surface_id"],
        "source_surface": spec["source_surface"],
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "sidecar_refs": [
            {"path": path, "exists": (root / path).exists()}
            for path in spec["sidecars"]
        ],
        "active_todo_refs": [_local_ref_record(root, todo_ref) for todo_ref in spec["active_todos"]],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _local_ref_record(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": spec["required_phrase"],
        "required_phrase_present": _contains_phrase(text, spec["required_phrase"]),
        "exists": (root / path).exists(),
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized_text = " ".join(text.casefold().split())
    normalized_phrase = " ".join(phrase.casefold().split())
    return normalized_phrase in normalized_text


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapSourceSpanCoverageBoundaryIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(boundary).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "ROADMAP source-span coverage boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapSourceSpanCoverageBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_evidence_field", f"missing required evidence fields: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_evidence_field", f"unknown required evidence fields: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[RoadmapSourceSpanCoverageBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> RoadmapSourceSpanCoverageBoundaryIssue:
    return RoadmapSourceSpanCoverageBoundaryIssue(code=code, message=message)
