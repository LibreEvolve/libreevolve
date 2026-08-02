from __future__ import annotations

import hashlib
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_citation_use_inventory_boundary import (
    EXPECTED_ENTRYPOINT,
    EXPECTED_TEX_CLOSURE_FILES,
    _consume_group,
    _normalize_whitespace,
    _read_source_archive,
    _section_headings,
    _section_path_at,
    _skip_whitespace,
    _strip_tex_comments,
    _tex_dependency_closure,
)
from libreevolve.problems.benchmarks.paper_bibliography import (
    EXPECTED_SOURCE_PAPER_ID,
)


ALPHAEVOLVE_TEX_SOURCE_DETAIL_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_tex_source_detail_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "tex_equation_footnote_caption_constructs_dispositioned_without_"
    "proposition_level_exhaustiveness"
)
EXPECTED_CAPTION_COUNT = 22
EXPECTED_EQUATION_COUNT = 5
EXPECTED_FOOTNOTE_COUNT = 3
EXPECTED_EXCLUDED_FOOTNOTE_MACRO_TEMPLATE_COUNT = 1
EXPECTED_SOURCE_DETAIL_COUNT = 30
EXPECTED_MAPPED_BOUNDED_CLAIM_CONSTRUCT_COUNT = 24
EXPECTED_METADATA_BOUNDARY_CONSTRUCT_COUNT = 1
EXPECTED_NAMED_SPAN_LOCATOR_COUNT = 2
EXPECTED_DECORATIVE_MARKER_COUNT = 3
EXPECTED_MAPPED_CLAIM_REF_COUNT = 80

_SOURCE_INVENTORY_PATH = "papers/alphaevolve_source_inventory_boundary.json"
_CLAIM_INVENTORY_PATHS = {
    "system": "papers/alphaevolve_system_requirement_inventory_boundary.json",
    "matrix": "papers/alphaevolve_matrix_result_claim_inventory_boundary.json",
    "math": "papers/alphaevolve_math_result_claim_inventory_boundary.json",
    "scheduling": "papers/alphaevolve_scheduling_claim_inventory_boundary.json",
    "kernel": "papers/alphaevolve_kernel_claim_inventory_boundary.json",
    "ablation": "papers/alphaevolve_ablation_claim_inventory_boundary.json",
    "appendix_a": "papers/alphaevolve_appendix_a_claim_inventory_boundary.json",
    "appendix_b": "papers/alphaevolve_appendix_b_claim_inventory_boundary.json",
}
_TODO_SPECS = (
    {
        "todo_id": "whole_paper_semantics_code",
        "path": "docs/todo/code.md",
        "required_phrase": "Add exhaustive implementation-evidence mapping for AlphaEvolve",
    },
    {
        "todo_id": "whole_paper_semantics_paper",
        "path": "docs/todo/papers.md",
        "required_phrase": "Extend the bounded AlphaEvolve claim inventories to the whole paper.",
    },
    {
        "todo_id": "whole_paper_semantics_roadmap",
        "path": "docs/todo/roadmap.md",
        "required_phrase": "whole-paper requirement",
    },
)


def _claim_refs(inventory: str, *claim_ids: str) -> tuple[dict[str, str], ...]:
    path = _CLAIM_INVENTORY_PATHS[inventory]
    return tuple(
        {"inventory_path": path, "claim_id": claim_id}
        for claim_id in claim_ids
    )


def _caption_spec(
    construct_id: str,
    page: int,
    span_id: str,
    *,
    claims: tuple[dict[str, str], ...] = (),
    disposition: str = "bounded_claim_mapping",
    semantic_role: str = "claim_bearing_caption",
) -> dict[str, Any]:
    return {
        "construct_id": construct_id,
        "source_page": page,
        "source_span_id": span_id,
        "semantic_role": semantic_role,
        "disposition": disposition,
        "claim_refs": claims,
        "supporting_boundary_paths": (),
    }


_CAPTION_SPECS = {
    "tab:funsearch-vs-alphaevolve": _caption_spec(
        "caption_table_1",
        2,
        "table_1",
        disposition="named_span_locator",
        semantic_role="exhibit_locator_caption",
    ),
    "fig:high-level": _caption_spec(
        "caption_figure_1",
        3,
        "figure_1",
        disposition="named_span_locator",
        semantic_role="exhibit_locator_caption",
    ),
    "fig:method": _caption_spec(
        "caption_figure_2",
        4,
        "figure_2",
        claims=_claim_refs("system", "figure2_expanded_loop"),
    ),
    "fig:grounding-api": _caption_spec(
        "caption_figure_3_human_icon",
        6,
        "figure_3",
        disposition="decorative_marker",
        semantic_role="decorative_icon_subcaption",
    ),
    "fig:grounding-llm": _caption_spec(
        "caption_figure_3_llm_icon",
        6,
        "figure_3",
        disposition="decorative_marker",
        semantic_role="decorative_icon_subcaption",
    ),
    "fig:grounding-prompt": _caption_spec(
        "caption_figure_3_prompt_icon",
        6,
        "figure_3",
        disposition="decorative_marker",
        semantic_role="decorative_icon_subcaption",
    ),
    "fig:grounding": _caption_spec(
        "caption_figure_3",
        6,
        "figure_3",
        claims=_claim_refs("system", "figure3_supervised_pipeline_exhibit"),
    ),
    "tab:relaxed-opt-results": _caption_spec(
        "caption_table_2",
        9,
        "table_2",
        claims=_claim_refs(
            "matrix",
            "table2_best_known_reference_comparison",
            "table2_mnp_le_5_match_or_surpass_exact",
            "table2_complex_rows_exact_real_and_complex",
            "table2_decompositions_in_companion_colab",
        ),
    ),
    "fig:math_sota_examples": _caption_spec(
        "caption_figure_5",
        12,
        "figure_5",
        claims=_claim_refs(
            "math",
            "figure5_sota_breaking_constructions",
            "figure5_analysis_problem_scope",
            "figure5_geometry_problem_scope",
            "figure5_combinatorics_problem_scope",
        ),
    ),
    "fig:alphaevolve_heuristic": _caption_spec(
        "caption_figure_6",
        14,
        "figure_6",
        claims=_claim_refs(
            "scheduling",
            "figure6_tailored_google_workloads_and_capacity",
            "figure6_scoring_function_visualization",
            "figure6_yellow_regions_high_scores",
            "figure6_purple_regions_low_scores",
        ),
    ),
    "fig:tiling_heuristic": _caption_spec(
        "caption_figure_7",
        15,
        "figure_7",
        claims=_claim_refs(
            "kernel",
            "figure7_matrix_product_tiling_problem",
            "figure7_choose_m_n_p_tile_size",
            "figure7_tile_selection_for_all_input_shapes",
            "figure7_matrix_unit_optimal_shape_context",
            "figure7_accelerator_memory_capacity_context",
            "figure7_surrounding_operation_memory_context",
            "figure7_fused_operation_context",
            "figure7_compiler_intricacy_context",
        ),
    ),
    "fig:relaxed-opt-diff": _caption_spec(
        "caption_figure_4",
        11,
        "figure_4",
        claims=_claim_refs(
            "matrix",
            "figure4_full_diff_and_figure9_linkage",
            "figure4_optimizer_init_loss_sweep_changes",
            "figure4_fifteen_mutation_lineage",
        ),
    ),
    "fig:ablations_rewrite": _caption_spec(
        "caption_figure_8",
        18,
        "figure_8",
        claims=_claim_refs(
            "ablation",
            "figure8_left_matrix_panel",
            "figure8_right_kissing_panel",
            "figure8_curve_per_setting",
            "figure8_increasing_compute_budget",
            "figure8_average_over_targets",
            "figure8_higher_metric_is_better",
            "figure8_intra_target_standard_deviation",
            "figure8_three_independent_runs",
            "figure8_different_random_seeds",
        ),
    ),
    "tab:relaxed-opt-results-appendix": _caption_spec(
        "caption_table_3",
        34,
        "table_3",
        claims=_claim_refs(
            "appendix_a",
            "table3_full_table2_all_parameters",
            "table3_38_matches",
            "table3_14_surpasses",
            "table3_surpass_green_encoding",
            "table3_two_fall_behind",
            "table3_fall_behind_red_encoding",
            "table3_all_exact_algorithms",
            "table3_integer_or_half_integer_entries",
            "table3_three_complex_targets",
            "table3_complex_matrix_applicability",
            "table3_real_matrix_applicability",
            "table3_decompositions_in_colab",
        ),
    ),
    "fig:erdos": _caption_spec(
        "caption_figure_10",
        40,
        "figure_10",
        claims=_claim_refs(
            "appendix_b", "figure10_alphaevolve_minimum_overlap_construction"
        ),
    ),
    "fig:hexagons": _caption_spec(
        "caption_figure_11",
        41,
        "figure_11",
        claims=_claim_refs(
            "appendix_b",
            "figure11_two_packing_panels",
            "figure11_left_11_hexagons",
            "figure11_left_outer_side_3_931",
            "figure11_right_12_hexagons",
            "figure11_right_outer_side_3_942",
        ),
    ),
    "fig:distance_ratios": _caption_spec(
        "caption_figure_12",
        42,
        "figure_12",
        claims=_claim_refs(
            "appendix_b",
            "figure12_two_distance_panels",
            "figure12_left_16_points_2d",
            "figure12_left_ratio_12_889266112",
            "figure12_right_14_points_3d",
            "figure12_right_ratio_4_165849767",
            "b8_both_improve_best_known",
        ),
    ),
    "fig:heilbronn": _caption_spec(
        "caption_figure_13",
        43,
        "figure_13",
        claims=_claim_refs(
            "appendix_b",
            "figure13_three_heilbronn_panels",
            "figure13_left_11_points_area_0_0365",
            "figure13_middle_13_points_area_0_0309",
            "figure13_right_14_points_area_0_0278",
        ),
    ),
    "fig:circle_packing": _caption_spec(
        "caption_figure_14",
        44,
        "figure_14",
        claims=_claim_refs(
            "appendix_b",
            "figure14_three_circle_packing_panels",
            "figure14_left_26_circles_2_635",
            "figure14_middle_32_circles_2_937",
            "figure14_right_21_circles_2_365",
        ),
    ),
    "fig:relaxed-opt-diff-appendix-1": _caption_spec(
        "caption_figure_9a",
        35,
        "figure_9",
        claims=_claim_refs("appendix_a", "figure9a_caption_part_1_of_3"),
    ),
    "fig:relaxed-opt-diff-appendix-2": _caption_spec(
        "caption_figure_9b",
        36,
        "figure_9",
        claims=_claim_refs("appendix_a", "figure9b_caption_part_2_of_3"),
    ),
    "fig:relaxed-opt-diff-appendix-3": _caption_spec(
        "caption_figure_9c",
        37,
        "figure_9",
        claims=_claim_refs(
            "appendix_a",
            "figure9c_caption_part_3_of_3",
            "figure9_hyper_user_provided_library",
        ),
    ),
}

_EQUATION_SPECS = {
    "maxf": {
        "construct_id": "equation_b1_max_autoconvolution",
        "source_page": 38,
        "source_span_id": "appendix_b_1",
        "semantic_role": "displayed_equation",
        "disposition": "bounded_claim_mapping",
        "claim_refs": _claim_refs("appendix_b", "b1_equation_1_max_autoconvolution"),
        "supporting_boundary_paths": (),
    },
    "cds": {
        "construct_id": "equation_b6_known_bounds",
        "source_page": 40,
        "source_span_id": "appendix_b_6",
        "semantic_role": "displayed_equation",
        "disposition": "bounded_claim_mapping",
        "claim_refs": _claim_refs("appendix_b", "b6_known_bounds_equation_2"),
        "supporting_boundary_paths": (),
    },
    "cds-lower": {
        "construct_id": "equation_b6_lower_bound",
        "source_page": 41,
        "source_span_id": "appendix_b_6",
        "semantic_role": "displayed_equation",
        "disposition": "bounded_claim_mapping",
        "claim_refs": _claim_refs("appendix_b", "b6_equation_3_formula"),
        "supporting_boundary_paths": (),
    },
    "appendix.tex:253": {
        "construct_id": "equation_b11_distance_norm_condition",
        "source_page": 43,
        "source_span_id": "appendix_b_11",
        "semantic_role": "displayed_equation",
        "disposition": "bounded_claim_mapping",
        "claim_refs": _claim_refs("appendix_b", "b11_lemma_distance_norm_condition"),
        "supporting_boundary_paths": (),
    },
    "eq:abi": {
        "construct_id": "equation_b11_inner_product",
        "source_page": 43,
        "source_span_id": "appendix_b_11",
        "semantic_role": "displayed_equation",
        "disposition": "bounded_claim_mapping",
        "claim_refs": _claim_refs("appendix_b", "b11_proof_inner_product_equation_4"),
        "supporting_boundary_paths": (),
    },
}

_FOOTNOTE_SPECS = {
    "main.tex:26": {
        "construct_id": "footnote_title_equal_contribution",
        "source_page": 1,
        "source_span_id": "title_page",
        "semantic_role": "publication_metadata_footnote",
        "disposition": "publication_metadata_boundary",
        "claim_refs": (),
        "supporting_boundary_paths": (
            "papers/title_page_affiliation_boundary.json",
            "papers/paper_author_metadata_boundary.json",
        ),
    },
    "introduction.tex:49": {
        "construct_id": "footnote_companion_colab_artifacts",
        "source_page": 2,
        "source_span_id": "introduction",
        "semantic_role": "artifact_availability_footnote",
        "disposition": "bounded_claim_mapping",
        "claim_refs": (
            *_claim_refs("matrix", "table2_decompositions_in_companion_colab"),
            *_claim_refs("math", "section3_2_new_constructions_in_companion_colab"),
            *_claim_refs("appendix_a", "table3_decompositions_in_colab"),
            *_claim_refs("appendix_b", "appendix_b_colab_data_and_verification_code"),
        ),
        "supporting_boundary_paths": (),
    },
    "results.tex:56": {
        "construct_id": "footnote_matrix_non_tensor_nonrecursive_caveat",
        "source_page": 10,
        "source_span_id": "section_3_1",
        "semantic_role": "technical_caveat_footnote",
        "disposition": "bounded_claim_mapping",
        "claim_refs": _claim_refs(
            "matrix", "section3_1_footnote_non_tensor_nonrecursive_caveat"
        ),
        "supporting_boundary_paths": (),
    },
}

_CAPTION_RE = re.compile(r"\\caption(?:\*)?(?![A-Za-z@])")
_LABEL_RE = re.compile(r"\\label\b\s*\{")
_FOOTNOTE_RE = re.compile(r"\\footnote\b")
_EQUATION_BEGIN_RE = re.compile(r"\\begin\s*\{(equation\*?)\}")


@dataclass(frozen=True)
class AlphaEvolveTexSourceDetailInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveTexSourceDetailInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    source_detail_count: int
    caption_count: int
    equation_count: int
    footnote_count: int
    unmapped_construct_count: int
    unresolved_reference_count: int
    issues: list[AlphaEvolveTexSourceDetailInventoryBoundaryIssue]


def alphaevolve_tex_source_detail_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Disposition retained TeX captions, equation environments, and footnotes."""

    root_path = Path(root)
    source_artifact, archive_texts, source_errors = _read_source_archive(root_path)
    tex_texts = {
        name: text
        for name, text in archive_texts.items()
        if name.casefold().endswith(".tex")
    }
    closure = _tex_dependency_closure(tex_texts, EXPECTED_ENTRYPOINT)
    parsed, excluded_footnotes, parse_errors = _parse_source_details(
        tex_texts, closure
    )
    claim_ids, named_span_ids, reference_errors = _reference_ids(root_path)
    records, disposition_errors = _disposition_records(
        root_path,
        parsed,
        claim_ids,
        named_span_ids,
    )
    source_errors = sorted(set([*source_errors, *reference_errors]))
    parse_errors = sorted(set([*parse_errors, *disposition_errors]))
    kind_counts = Counter(record["source_kind"] for record in records)
    disposition_counts = Counter(record["disposition"] for record in records)
    unresolved_reference_count = sum(
        1
        for record in records
        for ref in (
            record["claim_refs"]
            + record["named_span_refs"]
            + record["supporting_boundary_refs"]
        )
        if not ref["resolved"]
    )
    mapped_claim_ref_count = sum(
        len(record["claim_refs"]) for record in records
    )
    unmapped_construct_count = disposition_counts["unmapped"]
    todo_refs = [_todo_ref(root_path, spec) for spec in _TODO_SPECS]
    todo_ownership_ready = all(
        ref["exists"] and ref["required_phrase_present"] for ref in todo_refs
    )
    construct_inventory_ready = (
        source_artifact["identity_ok"]
        and not source_errors
        and not parse_errors
        and tuple(closure) == EXPECTED_TEX_CLOSURE_FILES
        and kind_counts["caption"] == EXPECTED_CAPTION_COUNT
        and kind_counts["equation"] == EXPECTED_EQUATION_COUNT
        and kind_counts["footnote"] == EXPECTED_FOOTNOTE_COUNT
        and len(excluded_footnotes)
        == EXPECTED_EXCLUDED_FOOTNOTE_MACRO_TEMPLATE_COUNT
        and len(records) == EXPECTED_SOURCE_DETAIL_COUNT
    )
    construct_disposition_ready = (
        construct_inventory_ready
        and disposition_counts["bounded_claim_mapping"]
        == EXPECTED_MAPPED_BOUNDED_CLAIM_CONSTRUCT_COUNT
        and disposition_counts["publication_metadata_boundary"]
        == EXPECTED_METADATA_BOUNDARY_CONSTRUCT_COUNT
        and disposition_counts["named_span_locator"]
        == EXPECTED_NAMED_SPAN_LOCATOR_COUNT
        and disposition_counts["decorative_marker"]
        == EXPECTED_DECORATIVE_MARKER_COUNT
        and unmapped_construct_count == 0
        and mapped_claim_ref_count == EXPECTED_MAPPED_CLAIM_REF_COUNT
        and unresolved_reference_count == 0
        and todo_ownership_ready
    )
    return {
        "schema": ALPHAEVOLVE_TEX_SOURCE_DETAIL_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "construct_inventory_ready": construct_inventory_ready,
        "construct_disposition_ready": construct_disposition_ready,
        "proposition_level_semantic_exhaustiveness_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_errors": source_errors,
        "parse_errors": parse_errors,
        "source_closure": {
            "entrypoint": EXPECTED_ENTRYPOINT,
            "file_count": len(closure),
            "files": [
                {
                    "path": name,
                    "sha256": hashlib.sha256(
                        archive_texts.get(name, "").encode("utf-8")
                    ).hexdigest(),
                }
                for name in closure
            ],
        },
        "caption_count": kind_counts["caption"],
        "equation_count": kind_counts["equation"],
        "footnote_count": kind_counts["footnote"],
        "excluded_footnote_macro_template_count": len(excluded_footnotes),
        "excluded_footnote_macro_templates": excluded_footnotes,
        "source_detail_count": len(records),
        "source_kind_counts": dict(sorted(kind_counts.items())),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "mapped_bounded_claim_construct_count": disposition_counts[
            "bounded_claim_mapping"
        ],
        "metadata_boundary_construct_count": disposition_counts[
            "publication_metadata_boundary"
        ],
        "named_span_locator_count": disposition_counts["named_span_locator"],
        "decorative_marker_count": disposition_counts["decorative_marker"],
        "unmapped_construct_count": unmapped_construct_count,
        "mapped_claim_ref_count": mapped_claim_ref_count,
        "unresolved_reference_count": unresolved_reference_count,
        "new_claim_count": 0,
        "source_detail_records": records,
        "active_todo_refs": todo_refs,
        "todo_ownership_ready": todo_ownership_ready,
        "inventory_scope": {
            "included": [
                "all 22 caption commands in the recursive main.tex closure",
                "all five equation and equation-star environments in the closure",
                "all three semantic footnote uses in the closure",
                "the excluded preamble footnote macro template as a non-use audit record",
                "construct-level mapping to existing bounded claim IDs, publication metadata boundaries, named spans, or decorative-marker disposition",
            ],
            "excluded": [
                "sentence- and paragraph-level proposition exhaustiveness",
                "inline-math proposition semantics",
                "table-cell text and code-listing semantics",
                "image-pixel and visual-encoding semantics",
                "citation proposition, sufficiency, relevance, or implementation semantics",
                "independent reviewer proof or published-result reproduction",
                "AlphaEvolve system parity",
            ],
        },
        "claim_boundary": (
            "This sidecar certifies construct-level disposition for all 30 "
            "retained-source captions, equation-environment constructs, and semantic "
            "footnotes: 24 map to existing bounded claim IDs, one maps to "
            "reviewed publication metadata, two are non-additive named-span "
            "locators, and three are decorative markers. It adds zero bounded "
            "claims and does not establish proposition-level semantic "
            "exhaustiveness, citation sufficiency, independent result "
            "reproduction, or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_tex_source_detail_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveTexSourceDetailInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_tex_source_detail_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveTexSourceDetailInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_tex_source_detail_inventory_boundary_record(root)
    issues: list[AlphaEvolveTexSourceDetailInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_TEX_SOURCE_DETAIL_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TeX source-detail inventory schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("proposition_level_semantic_exhaustiveness_ready") is not False:
        issues.append(_issue("semantic_exhaustiveness_overclaim", "construct disposition must not claim proposition-level semantic exhaustiveness"))
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(_issue("parity_overclaim", "construct disposition must not claim AlphaEvolve parity"))
    if data.get("new_claim_count") != 0:
        issues.append(_issue("new_claim_overclaim", "source-detail disposition must add zero bounded claims"))
    for key in (
        "source_artifact",
        "source_errors",
        "parse_errors",
        "source_closure",
        "caption_count",
        "equation_count",
        "footnote_count",
        "excluded_footnote_macro_template_count",
        "excluded_footnote_macro_templates",
        "source_detail_count",
        "source_kind_counts",
        "disposition_counts",
        "mapped_bounded_claim_construct_count",
        "metadata_boundary_construct_count",
        "named_span_locator_count",
        "decorative_marker_count",
        "unmapped_construct_count",
        "mapped_claim_ref_count",
        "unresolved_reference_count",
        "source_detail_records",
        "active_todo_refs",
        "todo_ownership_ready",
        "inventory_scope",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from the retained TeX source-detail inventory"))
    for key in ("construct_inventory_ready", "construct_disposition_ready"):
        if data.get(key) is not expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} does not match source, disposition, reference, and TODO checks"))
    if not expected["source_artifact"]["identity_ok"]:
        issues.append(_issue("source_archive_identity_mismatch", "retained AlphaEvolve TeX archive identity does not match the pinned source"))
    if expected["source_errors"]:
        issues.append(_issue("source_inventory_incomplete", "TeX source-detail inventory inputs are incomplete"))
    if expected["parse_errors"]:
        issues.append(_issue("source_detail_parse_incomplete", "one or more retained TeX source details lack a stable disposition"))
    if expected["unresolved_reference_count"]:
        issues.append(_issue("unresolved_source_detail_reference", "one or more claim, named-span, or metadata references are unresolved"))
    if not expected["todo_ownership_ready"]:
        issues.append(_issue("unowned_proposition_level_gap", "remaining proposition-level exhaustiveness gaps require active TODO ownership"))
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "all 30" not in claim_boundary
        or "24 map to existing bounded claim IDs" not in claim_boundary
        or "zero bounded claims" not in claim_boundary
        or "does not establish proposition-level semantic exhaustiveness" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate construct disposition from proposition-level exhaustiveness and parity"))
    return AlphaEvolveTexSourceDetailInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        source_detail_count=data.get("source_detail_count") if isinstance(data.get("source_detail_count"), int) else 0,
        caption_count=data.get("caption_count") if isinstance(data.get("caption_count"), int) else 0,
        equation_count=data.get("equation_count") if isinstance(data.get("equation_count"), int) else 0,
        footnote_count=data.get("footnote_count") if isinstance(data.get("footnote_count"), int) else 0,
        unmapped_construct_count=data.get("unmapped_construct_count") if isinstance(data.get("unmapped_construct_count"), int) else 0,
        unresolved_reference_count=data.get("unresolved_reference_count") if isinstance(data.get("unresolved_reference_count"), int) else 0,
        issues=issues,
    )


def render_alphaevolve_tex_source_detail_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_tex_source_detail_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve TeX source-detail inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| source_detail_count | {validation.source_detail_count} |",
        f"| caption_count | {validation.caption_count} |",
        f"| equation_count | {validation.equation_count} |",
        f"| footnote_count | {validation.footnote_count} |",
        f"| unmapped_construct_count | {validation.unmapped_construct_count} |",
        f"| unresolved_reference_count | {validation.unresolved_reference_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _parse_source_details(
    tex_texts: dict[str, str],
    closure: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    excluded_footnotes: list[dict[str, Any]] = []
    errors: list[str] = []
    for file_index, source_file in enumerate(closure):
        text = _strip_tex_comments(tex_texts.get(source_file, ""))
        headings = _section_headings(text)
        caption_matches = list(_CAPTION_RE.finditer(text))
        for index, match in enumerate(caption_matches):
            position = _skip_whitespace(text, match.end())
            if position < len(text) and text[position] == "[":
                _, position = _consume_group(text, position, "[", "]")
                position = _skip_whitespace(text, position)
            value, end = _consume_group(text, position, "{", "}")
            if value is None:
                errors.append(f"malformed_caption:{source_file}:{_line_number(text, match.start())}")
                continue
            next_caption = caption_matches[index + 1].start() if index + 1 < len(caption_matches) else len(text)
            label = _first_label(value, 0, len(value))
            if label is None:
                label = _first_label(text, end, next_caption)
            if label is None:
                errors.append(f"caption_without_label:{source_file}:{_line_number(text, match.start())}")
                label = f"{source_file}:{_line_number(text, match.start())}"
            records.append(
                _parsed_record(
                    text,
                    source_file,
                    file_index,
                    headings,
                    match.start(),
                    end,
                    "caption",
                    label,
                    value,
                    None,
                )
            )
        for match in _EQUATION_BEGIN_RE.finditer(text):
            environment = match.group(1)
            end_match = re.search(
                rf"\\end\s*\{{{re.escape(environment)}\}}",
                text[match.end() :],
            )
            if end_match is None:
                errors.append(f"unterminated_equation:{source_file}:{_line_number(text, match.start())}")
                continue
            end = match.end() + end_match.end()
            value = text[match.end() : match.end() + end_match.start()]
            label = _first_label(value, 0, len(value))
            lookup_key = label or f"{source_file}:{_line_number(text, match.start())}"
            records.append(
                _parsed_record(
                    text,
                    source_file,
                    file_index,
                    headings,
                    match.start(),
                    end,
                    "equation",
                    lookup_key,
                    value,
                    environment,
                    source_label=label,
                )
            )
        for match in _FOOTNOTE_RE.finditer(text):
            position = _skip_whitespace(text, match.end())
            value, end = _consume_group(text, position, "{", "}")
            if value is None:
                errors.append(f"malformed_footnote:{source_file}:{_line_number(text, match.start())}")
                continue
            line = _line_number(text, match.start())
            if source_file == "preamble.tex" and _normalize_whitespace(value) == "#1":
                excluded_footnotes.append(
                    {
                        "source_file": source_file,
                        "source_line": line,
                        "source_column": _column_number(text, match.start()),
                        "command_text": text[match.start() : end],
                        "reason": "blfootnote_macro_template_not_semantic_use",
                    }
                )
                continue
            records.append(
                _parsed_record(
                    text,
                    source_file,
                    file_index,
                    headings,
                    match.start(),
                    end,
                    "footnote",
                    f"{source_file}:{line}",
                    value,
                    None,
                )
            )
    records.sort(key=lambda row: (row["_file_index"], row["_offset"]))
    for record in records:
        record.pop("_file_index")
        record.pop("_offset")
    return records, excluded_footnotes, errors


def _parsed_record(
    text: str,
    source_file: str,
    file_index: int,
    headings: list[tuple[int, int, str]],
    start: int,
    end: int,
    source_kind: str,
    lookup_key: str,
    value: str,
    environment: str | None,
    *,
    source_label: str | None = None,
) -> dict[str, Any]:
    line_start = text.rfind("\n", 0, start) + 1
    line_end = text.find("\n", start)
    if line_end < 0:
        line_end = len(text)
    section_path = _section_path_at(headings, start)
    if source_file == "main.tex" and not section_path:
        section_path = ["Title page"]
    return {
        "_file_index": file_index,
        "_offset": start,
        "lookup_key": lookup_key,
        "source_kind": source_kind,
        "source_file": source_file,
        "source_line": _line_number(text, start),
        "source_column": _column_number(text, start),
        "section_path": section_path,
        "source_label": source_label if source_label is not None else (lookup_key if source_kind == "caption" else None),
        "tex_environment": environment,
        "command_text": text[start:end],
        "normalized_text": _normalize_whitespace(value),
        "command_sha256": hashlib.sha256(text[start:end].encode("utf-8")).hexdigest(),
        "source_line_sha256": hashlib.sha256(text[line_start:line_end].encode("utf-8")).hexdigest(),
    }


def _disposition_records(
    root: Path,
    parsed: list[dict[str, Any]],
    claim_ids: dict[str, set[str]],
    named_span_ids: set[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_specs: set[tuple[str, str]] = set()
    specs_by_kind = {
        "caption": _CAPTION_SPECS,
        "equation": _EQUATION_SPECS,
        "footnote": _FOOTNOTE_SPECS,
    }
    for parsed_record in parsed:
        kind = parsed_record["source_kind"]
        lookup_key = parsed_record["lookup_key"]
        spec = specs_by_kind[kind].get(lookup_key)
        if spec is None:
            errors.append(f"unmapped_source_detail:{kind}:{lookup_key}")
            spec = {
                "construct_id": f"unmapped_{kind}_{len(records) + 1}",
                "source_page": None,
                "source_span_id": None,
                "semantic_role": "unmapped",
                "disposition": "unmapped",
                "claim_refs": (),
                "supporting_boundary_paths": (),
            }
        else:
            seen_specs.add((kind, lookup_key))
        claim_refs = [
            {
                **claim_ref,
                "resolved": claim_ref["claim_id"]
                in claim_ids.get(claim_ref["inventory_path"], set()),
            }
            for claim_ref in spec["claim_refs"]
        ]
        span_id = spec["source_span_id"]
        named_span_refs = []
        if spec["disposition"] == "named_span_locator" and span_id:
            named_span_refs.append(
                {
                    "inventory_path": _SOURCE_INVENTORY_PATH,
                    "span_id": span_id,
                    "resolved": span_id in named_span_ids,
                }
            )
        supporting_boundary_refs = [
            {
                "path": path,
                "resolved": (root / path).is_file(),
            }
            for path in spec["supporting_boundary_paths"]
        ]
        record = dict(parsed_record)
        record.pop("lookup_key")
        record.update(
            {
                "construct_id": spec["construct_id"],
                "source_page": spec["source_page"],
                "source_span_id": span_id,
                "semantic_role": spec["semantic_role"],
                "disposition": spec["disposition"],
                "claim_refs": claim_refs,
                "named_span_refs": named_span_refs,
                "supporting_boundary_refs": supporting_boundary_refs,
            }
        )
        records.append(record)
    for kind, specs in specs_by_kind.items():
        for lookup_key in specs:
            if (kind, lookup_key) not in seen_specs:
                errors.append(f"missing_source_detail:{kind}:{lookup_key}")
    return records, errors


def _reference_ids(
    root: Path,
) -> tuple[dict[str, set[str]], set[str], list[str]]:
    claim_ids: dict[str, set[str]] = {}
    errors: list[str] = []
    for path in _CLAIM_INVENTORY_PATHS.values():
        data, error = _read_json_object(root / path)
        if error:
            errors.append(f"claim_inventory_{error}:{path}")
            claim_ids[path] = set()
            continue
        ids: set[str] = set()
        for collection in ("claim_records", "requirement_records"):
            rows = data.get(collection)
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                value = row.get("claim_id", row.get("requirement_id"))
                if isinstance(value, str):
                    ids.add(value)
        claim_ids[path] = ids
    source_data, source_error = _read_json_object(root / _SOURCE_INVENTORY_PATH)
    if source_error:
        errors.append(f"source_inventory_{source_error}:{_SOURCE_INVENTORY_PATH}")
        named_span_ids: set[str] = set()
    else:
        rows = source_data.get("span_records")
        named_span_ids = (
            {
                row["span_id"]
                for row in rows
                if isinstance(row, dict) and isinstance(row.get("span_id"), str)
            }
            if isinstance(rows, list)
            else set()
        )
    return claim_ids, named_span_ids, errors


def _read_json_object(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, f"read_error_{type(exc).__name__}"
    if not isinstance(data, dict):
        return {}, "invalid_shape"
    return data, None


def _first_label(text: str, start: int, end: int) -> str | None:
    match = _LABEL_RE.search(text, start, end)
    if match is None:
        return None
    value, _ = _consume_group(text, match.end() - 1, "{", "}")
    return value.strip() if value and value.strip() else None


def _todo_ref(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = root / spec["path"]
    try:
        text = path.read_text(encoding="utf-8")
        exists = path.is_file()
    except (OSError, UnicodeDecodeError):
        text = ""
        exists = False
    return {
        **spec,
        "exists": exists,
        "required_phrase_present": spec["required_phrase"] in text,
    }


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _column_number(text: str, offset: int) -> int:
    return offset - text.rfind("\n", 0, offset)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[
    dict[str, Any] | None,
    list[AlphaEvolveTexSourceDetailInventoryBoundaryIssue],
]:
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
    return None, [_issue("invalid_shape", "TeX source-detail inventory must be a JSON object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveTexSourceDetailInventoryBoundaryIssue:
    return AlphaEvolveTexSourceDetailInventoryBoundaryIssue(code, message)
