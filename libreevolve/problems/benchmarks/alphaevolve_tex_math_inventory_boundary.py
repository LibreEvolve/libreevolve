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
    _normalize_whitespace,
    _read_source_archive,
    _section_headings,
    _section_path_at,
    _strip_tex_comments,
    _tex_dependency_closure,
)
from libreevolve.problems.benchmarks.paper_bibliography import (
    EXPECTED_SOURCE_PAPER_ID,
)


ALPHAEVOLVE_TEX_MATH_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_tex_math_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "all_explicit_tex_math_constructs_dispositioned_without_"
    "mathematical_correctness_or_result_reproduction"
)
EXPECTED_MATH_CONSTRUCT_COUNT = 309
EXPECTED_INLINE_CONSTRUCT_COUNT = 291
EXPECTED_DISPLAY_CONSTRUCT_COUNT = 18
EXPECTED_SOURCE_DETAIL_OVERLAP_COUNT = 34
EXPECTED_TABLE_CELL_OVERLAP_COUNT = 75
EXPECTED_DIRECT_CLAIM_MAPPING_COUNT = 200
EXPECTED_DELIMITER_KIND_COUNTS = {
    "bracket": 1,
    "double_dollar": 11,
    "environment": 5,
    "paren": 1,
    "single_dollar": 291,
}

_SOURCE_DETAIL_PATH = "papers/alphaevolve_tex_source_detail_inventory_boundary.json"
_TABLE_CELL_PATH = "papers/alphaevolve_tex_table_cell_inventory_boundary.json"
_CLAIM_INVENTORY_PATHS = {
    "context": "papers/alphaevolve_context_claim_inventory_boundary.json",
    "system": "papers/alphaevolve_system_requirement_inventory_boundary.json",
    "matrix": "papers/alphaevolve_matrix_result_claim_inventory_boundary.json",
    "math": "papers/alphaevolve_math_result_claim_inventory_boundary.json",
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


def _targets(inventory: str, *claim_ids: str) -> tuple[tuple[str, str], ...]:
    return tuple((_CLAIM_INVENTORY_PATHS[inventory], claim_id) for claim_id in claim_ids)


def _ordinal_targets(
    *groups: tuple[tuple[int, ...], str, tuple[str, ...]],
) -> dict[int, tuple[tuple[str, str], ...]]:
    result: dict[int, tuple[tuple[str, str], ...]] = {}
    for ordinals, inventory, claim_ids in groups:
        refs = _targets(inventory, *claim_ids)
        for ordinal in ordinals:
            if ordinal in result:
                raise ValueError(f"duplicate math ordinal mapping: {ordinal}")
            result[ordinal] = refs
    return result


_DIRECT_CLAIM_MAP: dict[
    tuple[str, int],
    tuple[tuple[str, str], ...] | dict[int, tuple[tuple[str, str], ...]],
] = {
    ("main.tex", 34): _targets(
        "context", "abstract_complex_4x4_matrix_48_multiplications"
    ),
    ("introduction.tex", 48): _targets(
        "context", "introduction_complex_4x4_matrix_48_multiplications"
    ),
    ("introduction.tex", 52): _ordinal_targets(
        ((0,), "context", ("introduction_seventy_five_percent_math_best_known",)),
        ((1,), "context", ("introduction_twenty_percent_math_sota_uplift",)),
    ),
    ("introduction.tex", 53): _targets(
        "context", "introduction_kissing_number_d11_improvement"
    ),
    ("methods.tex", 33): _targets("system", "task_scalar_metric_mapping"),
    ("methods.tex", 35): _targets("system", "task_fixed_evaluate_signature"),
    ("methods.tex", 37): _targets("system", "task_evaluation_workload_range"),
    ("methods.tex", 38): _targets("system", "task_scalar_metric_mapping"),
    ("methods.tex", 39): _targets("system", "task_evaluation_workload_range"),
    ("methods.tex", 108): _targets("system", "evaluation_every_proposal"),
    ("methods.tex", 115): _targets(
        "system", "evaluation_llm_generated_feedback"
    ),
    ("results.tex", 43): _targets(
        "matrix", "section3_1_3x3_minimum_rank_unknown"
    ),
    ("results.tex", 53): _targets(
        "matrix", "section3_1_recursive_strassen_rank49_any_field"
    ),
    ("results.tex", 57): _targets(
        "matrix", "section3_1_first_rank48_complex_4x4"
    ),
    ("results.tex", 60): _targets(
        "matrix", "section3_1_most_table2_simple_initial_program"
    ),
    ("results.tex", 99): _targets(
        "math", "section3_2_n_point_max_min_distance_packing"
    ),
    ("appendix.tex", 3): _ordinal_targets(
        ((0,), "appendix_a", ("appendix_a_54_sizes_considered",)),
        ((1,), "appendix_a", ("appendix_a_rough_m_n_range",)),
        ((2,), "appendix_a", ("appendix_a_reasonable_p_cutoff",)),
        (
            (3,),
            "appendix_a",
            (
                "appendix_a_axis_permutation_symmetry",
                "appendix_a_sorted_dimensions",
            ),
        ),
    ),
    ("appendix.tex", 5): _targets(
        "appendix_a", "appendix_a_beyond_5x5x5_attempts"
    ),
    ("appendix.tex", 84): _targets(
        "appendix_a", "table3_concurrent_rank90_4x5x6"
    ),
    ("appendix.tex", 86): _targets(
        "appendix_a", "appendix_a_figure9_4x4_tensor_target"
    ),
    ("appendix.tex", 96): _targets("appendix_b", "b1_autoconvolution_definition"),
    ("appendix.tex", 97): _targets("appendix_b", "b1_c1_largest_constant"),
    ("appendix.tex", 101): _targets("appendix_b", "b1_nonnegative_real_functions"),
    ("appendix.tex", 102): _targets(
        "appendix_b", "b1_known_lower_bound_1_28", "b1_known_upper_bound_1_5098"
    ),
    ("appendix.tex", 104): _ordinal_targets(
        ((0,), "appendix_b", ("b1_alphaevolve_domain",)),
        ((1,), "appendix_b", ("b1_alphaevolve_bound_1_5053",)),
    ),
    ("appendix.tex", 107): _targets("appendix_b", "b2_c2_smallest_constant"),
    ("appendix.tex", 108): _targets("appendix_b", "b2_norm_inequality"),
    ("appendix.tex", 109): _targets("appendix_b", "b2_nonnegative_real_functions"),
    ("appendix.tex", 111): _targets(
        "appendix_b", "b2_known_lower_bound_0_88922", "b2_known_upper_bound_1"
    ),
    ("appendix.tex", 113): _ordinal_targets(
        ((0,), "appendix_b", ("b2_alphaevolve_domain",)),
        ((1,), "appendix_b", ("b2_alphaevolve_bound_0_8962",)),
    ),
    ("appendix.tex", 116): _targets("appendix_b", "b3_c3_largest_constant"),
    ("appendix.tex", 117): _targets(
        "appendix_b", "b3_absolute_autoconvolution_inequality"
    ),
    ("appendix.tex", 118): _ordinal_targets(
        ((0,), "appendix_b", ("b3_signed_real_functions",)),
        ((1,), "appendix_b", ("b3_c3_at_most_c1",)),
        ((2,), "appendix_b", ("b3_c3_c1_signed_reason",)),
    ),
    ("appendix.tex", 119): _targets("appendix_b", "b3_prior_bound_1_45810"),
    ("appendix.tex", 120): _ordinal_targets(
        ((0,), "appendix_b", ("b3_alphaevolve_equal_spacing_and_domain",)),
        ((1,), "appendix_b", ("b3_alphaevolve_bound_1_4557",)),
    ),
    ("appendix.tex", 125): _targets(
        "appendix_b", "b4_fourier_transform_definition"
    ),
    ("appendix.tex", 126): _targets("appendix_b", "b4_a_function_definition"),
    ("appendix.tex", 127): _targets("appendix_b", "b4_c4_largest_constant"),
    ("appendix.tex", 128): _targets(
        "appendix_b", "b4_uncertainty_product_inequality"
    ),
    ("appendix.tex", 129): _ordinal_targets(
        ((0,), "appendix_b", ("b4_even_function_condition",)),
        ((1,), "appendix_b", ("b4_negative_origin_condition",)),
    ),
    ("appendix.tex", 130): _targets(
        "appendix_b", "b4_known_lower_bound_0_2025", "b4_known_upper_bound_0_3523"
    ),
    ("appendix.tex", 131): _ordinal_targets(
        ((0,), "appendix_b", ("b4_paper_stated_0_353",)),
        ((1,), "appendix_b", ("b4_rounding_to_fourth_digit_0_3523",)),
    ),
    ("appendix.tex", 132): _targets(
        "appendix_b", "b4_first_version_result_0_3521"
    ),
    ("appendix.tex", 134): _ordinal_targets(
        (tuple(range(0, 4)), "appendix_b", ("b4_test_function_upper_bound_method",)),
        ((4, 5), "appendix_b", ("b4_test_function_polynomial_gaussian_form",)),
        ((6, 9), "appendix_b", ("b4_even_polynomial_hermite_basis",)),
        ((7, 8), "appendix_b", ("b4_hermite_fourier_eigenfunction",)),
        ((10, 11), "appendix_b", ("b4_fourier_invariant_p",)),
        ((12, 13, 14, 15, 18, 19, 20, 21), "appendix_b", ("b4_a_related_to_largest_root",)),
        ((16, 17), "appendix_b", ("b4_eventual_positive_root_condition",)),
        ((22,), "appendix_b", ("b4_a_f_equals_a_fhat",)),
        ((23,), "appendix_b", ("b4_c4_at_most_a_squared",)),
    ),
    ("appendix.tex", 136): _ordinal_targets(
        (tuple(range(0, 7)), "appendix_b", ("b4_coefficient_search_constraints",)),
        ((7,), "appendix_b", ("b4_p_zero_condition",)),
        ((8, 9), "appendix_b", ("b4_x_squared_factor",)),
        ((10, 11, 12), "appendix_b", ("b4_rmax_root_of_quotient",)),
        ((13, 14), "appendix_b", ("b4_bound_rmax_squared_over_2pi",)),
    ),
    ("appendix.tex", 138): _ordinal_targets(
        ((0, 1), "appendix_b", ("b4_reported_coefficients",)),
        (tuple(range(2, 7)), "appendix_b", ("b4_coefficients_yield_0_3521",)),
    ),
    ("appendix.tex", 144): _targets("appendix_b", "b5_c5_largest_constant"),
    ("appendix.tex", 145): _targets("appendix_b", "b5_original_overlap_integral"),
    ("appendix.tex", 146): _ordinal_targets(
        ((0,), "appendix_b", ("b5_f_g_nonnegative_unit_range",)),
        ((1, 2), "appendix_b", ("b5_f_plus_g_one",)),
        ((3,), "appendix_b", ("b5_integral_f_one",)),
        ((4, 5), "appendix_b", ("b5_zero_extension",)),
    ),
    ("appendix.tex", 147): _targets(
        "appendix_b", "b5_known_lower_bound_0_379005", "b5_known_upper_bound_0_380927"
    ),
    ("appendix.tex", 152): _ordinal_targets(
        ((0,), "appendix_b", ("b5_equivalent_step_function_infimum",)),
        ((1, 2), "appendix_b", ("b5_step_function_value_and_integral_constraints",)),
    ),
    ("appendix.tex", 153): _targets(
        "appendix_b", "b5_step_function_value_and_integral_constraints"
    ),
    ("appendix.tex", 157): _targets("appendix_b", "b5_shift_objective"),
    ("appendix.tex", 160): _targets("appendix_b", "b5_alphaevolve_bound_0_380924"),
    ("appendix.tex", 173): _ordinal_targets(
        ((0,), "appendix_b", ("b6_c6_largest_constant",)),
        ((1,), "appendix_b", ("b6_arbitrarily_large_integer_sets",)),
        ((2,), "appendix_b", ("b6_small_sumset_condition",)),
        ((3,), "appendix_b", ("b6_large_difference_condition",)),
    ),
    ("appendix.tex", 174): _ordinal_targets(
        ((0,), "appendix_b", ("b6_sumset_definition",)),
        ((1,), "appendix_b", ("b6_difference_set_definition",)),
        (tuple(range(2, 7)), "appendix_b", ("b6_little_less_notation",)),
        (tuple(range(7, 12)), "appendix_b", ("b6_little_greater_notation",)),
    ),
    ("appendix.tex", 183): _targets(
        "appendix_b", "b6_u_admissibility_conditions"
    ),
    ("appendix.tex", 184): _ordinal_targets(
        ((0,), "appendix_b", ("b6_u1_size_2003",)),
        ((1,), "appendix_b", ("b6_u1_bound_1_1479",)),
    ),
    ("appendix.tex", 185): _targets("appendix_b", "b6_u2_size_54265"),
    ("appendix.tex", 186): _targets("appendix_b", "b6_u2_bound_1_1584"),
    ("appendix.tex", 189): _targets(
        "appendix_b", "b7_problem_n_disjoint_unit_hexagons"
    ),
    ("appendix.tex", 190): _ordinal_targets(
        ((0, 2), "appendix_b", ("b7_prior_n11_3_943",)),
        ((1, 3), "appendix_b", ("b7_prior_n12_4_0",)),
    ),
    ("appendix.tex", 192): _ordinal_targets(
        ((0,), "appendix_b", ("b7_alphaevolve_n11_3_931",)),
        ((1,), "appendix_b", ("b7_alphaevolve_n12_3_942",)),
    ),
    ("appendix.tex", 206): _targets(
        "appendix_b", "b8_objective_n_points_d_dimensions"
    ),
    ("appendix.tex", 209): _ordinal_targets(
        ((0,), "appendix_b", ("b8_two_new_constructions",)),
        ((1,), "appendix_b", ("b8_2d_prior_sqrt_12_890",)),
    ),
    ("appendix.tex", 212): _ordinal_targets(
        ((0,), "appendix_b", ("b8_two_new_constructions",)),
        ((1,), "appendix_b", ("b8_3d_prior_sqrt_4_168",)),
    ),
    ("appendix.tex", 226): _ordinal_targets(
        (
            (0,),
            "appendix_b",
            ("b9_triangle_unit_area_domain", "b9_maximize_smallest_triangle_area"),
        ),
        ((1, 2), "appendix_b", ("b9_n11_prior_0_036",)),
        ((3,), "appendix_b", ("b9_n11_result_larger_0_0365",)),
    ),
    ("appendix.tex", 229): _targets(
        "appendix_b",
        "b10_convex_unit_area_domain",
        "b10_maximize_smallest_triangle_area",
    ),
    ("appendix.tex", 231): _ordinal_targets(
        ((0, 1), "appendix_b", ("b10_n13_prior_0_0306",)),
        ((2,), "appendix_b", ("b10_n13_result_0_0309",)),
    ),
    ("appendix.tex", 232): _ordinal_targets(
        ((0, 1), "appendix_b", ("b10_n14_prior_0_0277",)),
        ((2,), "appendix_b", ("b10_n14_result_0_0278",)),
    ),
    ("appendix.tex", 245): _targets(
        "appendix_b", "b11_d_dimensional_kissing_number"
    ),
    ("appendix.tex", 246): _targets(
        "appendix_b",
        "b11_prior_d11_lower_bound_592",
        "b11_alphaevolve_lower_bound_593",
    ),
    ("appendix.tex", 251): _targets(
        "appendix_b", "b11_lemma_nonzero_set_condition"
    ),
    ("appendix.tex", 252): _targets(
        "appendix_b", "b11_lemma_nonzero_set_condition"
    ),
    ("appendix.tex", 256): _ordinal_targets(
        ((0, 1, 2), "appendix_b", ("b11_lemma_center_transformation",)),
        ((3,), "appendix_b", ("b11_lemma_kissing_lower_bound_cardinality",)),
    ),
    ("appendix.tex", 260): _ordinal_targets(
        ((0,), "appendix_b", ("b11_lemma_distance_norm_condition",)),
        ((1,), "appendix_b", ("b11_proof_inner_product_equation_4",)),
    ),
    ("appendix.tex", 266): _targets(
        "appendix_b", "b11_transformed_centers_norm_two"
    ),
    ("appendix.tex", 267): _targets(
        "appendix_b", "b11_nonoverlap_distance_at_least_two"
    ),
    ("appendix.tex", 268): _targets(
        "appendix_b", "b11_nonoverlap_distance_at_least_two"
    ),
    ("appendix.tex", 272): _targets(
        "appendix_b", "b11_nonoverlap_inner_product_equivalence"
    ),
    ("appendix.tex", 275): _targets(
        "appendix_b", "b11_proof_valid_configuration_conclusion"
    ),
    ("appendix.tex", 281): _ordinal_targets(
        ((0,), "appendix_b", ("b12_unit_square_circle_problem",)),
        ((1,), "appendix_b", ("b12_maximize_sum_of_radii",)),
    ),
    ("appendix.tex", 283): _ordinal_targets(
        ((0, 1), "appendix_b", ("b12_n26_prior_2_634",)),
        ((2,), "appendix_b", ("b12_n26_result_2_635",)),
    ),
    ("appendix.tex", 284): _ordinal_targets(
        ((0, 1), "appendix_b", ("b12_n32_prior_2_936",)),
        ((2,), "appendix_b", ("b12_n32_result_2_937",)),
    ),
    ("appendix.tex", 287): _ordinal_targets(
        ((0,), "appendix_b", ("b13_perimeter4_rectangle_problem",)),
        ((1,), "appendix_b", ("b13_maximize_sum_of_radii",)),
    ),
    ("appendix.tex", 288): _ordinal_targets(
        ((0,), "appendix_b", ("b13_n21_new_construction",)),
        ((1,), "appendix_b", ("b13_n21_prior_2_364",)),
        ((2,), "appendix_b", ("b13_n21_result_2_3658",)),
    ),
}


@dataclass(frozen=True)
class AlphaEvolveTexMathInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveTexMathInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    math_construct_count: int
    inline_construct_count: int
    display_construct_count: int
    unmapped_construct_count: int
    unresolved_reference_count: int
    issues: list[AlphaEvolveTexMathInventoryBoundaryIssue]


def alphaevolve_tex_math_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Inventory every explicit math delimiter in the retained TeX closure."""

    root_path = Path(root)
    source_artifact, archive_texts, source_errors = _read_source_archive(root_path)
    tex_texts = {
        name: text
        for name, text in archive_texts.items()
        if name.casefold().endswith(".tex")
    }
    closure = _tex_dependency_closure(tex_texts, EXPECTED_ENTRYPOINT)
    parsed, parse_errors = _parse_math_constructs(tex_texts, closure)
    claim_catalog, catalog_errors = _claim_catalog(root_path)
    supports, support_errors = _support_ranges(root_path, tex_texts)
    records, disposition_errors = _disposition_records(
        parsed,
        claim_catalog,
        supports,
    )
    source_errors = sorted(set([*source_errors, *catalog_errors, *support_errors]))
    parse_errors = sorted(set([*parse_errors, *disposition_errors]))
    kind_counts = Counter(record["delimiter_kind"] for record in records)
    mode_counts = Counter(record["render_mode"] for record in records)
    disposition_counts = Counter(record["disposition"] for record in records)
    support_counts = Counter(
        ref["inventory_path"]
        for record in records
        for ref in record["supporting_unit_refs"]
    )
    unresolved_reference_count = sum(
        not ref["resolved"]
        for record in records
        for ref in [
            *record["claim_refs"],
            *record["named_span_refs"],
            *record["supporting_unit_refs"],
            *record["supporting_boundary_refs"],
        ]
    )
    direct_mapping_count = disposition_counts["direct_bounded_claim_mapping"]
    unmapped_construct_count = disposition_counts["unmapped"]
    todo_refs = [_todo_ref(root_path, spec) for spec in _TODO_SPECS]
    todo_ownership_ready = all(
        ref["exists"] and ref["required_phrase_present"] for ref in todo_refs
    )
    inventory_ready = (
        source_artifact["identity_ok"]
        and not source_errors
        and not parse_errors
        and tuple(closure) == EXPECTED_TEX_CLOSURE_FILES
        and len(records) == EXPECTED_MATH_CONSTRUCT_COUNT
        and mode_counts["inline"] == EXPECTED_INLINE_CONSTRUCT_COUNT
        and mode_counts["display"] == EXPECTED_DISPLAY_CONSTRUCT_COUNT
        and dict(sorted(kind_counts.items())) == EXPECTED_DELIMITER_KIND_COUNTS
    )
    disposition_ready = (
        inventory_ready
        and support_counts[_SOURCE_DETAIL_PATH]
        == EXPECTED_SOURCE_DETAIL_OVERLAP_COUNT
        and support_counts[_TABLE_CELL_PATH]
        == EXPECTED_TABLE_CELL_OVERLAP_COUNT
        and direct_mapping_count == EXPECTED_DIRECT_CLAIM_MAPPING_COUNT
        and unmapped_construct_count == 0
        and unresolved_reference_count == 0
        and todo_ownership_ready
    )
    return {
        "schema": ALPHAEVOLVE_TEX_MATH_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "math_construct_inventory_ready": inventory_ready,
        "math_construct_disposition_ready": disposition_ready,
        "mathematical_correctness_claim_ready": False,
        "result_reproduction_claim_ready": False,
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
        "math_construct_count": len(records),
        "inline_construct_count": mode_counts["inline"],
        "display_construct_count": mode_counts["display"],
        "delimiter_kind_counts": dict(sorted(kind_counts.items())),
        "render_mode_counts": dict(sorted(mode_counts.items())),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "source_detail_overlap_count": support_counts[_SOURCE_DETAIL_PATH],
        "table_cell_overlap_count": support_counts[_TABLE_CELL_PATH],
        "direct_claim_mapping_count": direct_mapping_count,
        "unmapped_construct_count": unmapped_construct_count,
        "unresolved_reference_count": unresolved_reference_count,
        "new_claim_count": 0,
        "math_construct_records": records,
        "active_todo_refs": todo_refs,
        "todo_ownership_ready": todo_ownership_ready,
        "inventory_scope": {
            "included": [
                (
                    "all explicit single-dollar, double-dollar, bracket, "
                    "parenthesis, equation, and equation-star math constructs "
                    "in the recursive main.tex closure"
                ),
                (
                    "comment stripping and code-listing masking that preserve "
                    "source offsets and line numbers"
                ),
                (
                    "construct-level inheritance from the retained source-detail "
                    "and table-cell inventories"
                ),
                (
                    "direct mapping of every remaining construct to existing "
                    "bounded claim IDs"
                ),
            ],
            "excluded": [
                "math rendered only inside bitmap, PDF, or other external assets",
                "macros that do not contain explicit math delimiters at their use site",
                "sentence- and paragraph-level proposition exhaustiveness",
                (
                    "proof checking, formula equivalence, numerical verification, "
                    "or mathematical correctness"
                ),
                "citation sufficiency or semantic relevance",
                "independent published-result reproduction",
                "AlphaEvolve system parity",
            ],
        },
        "claim_boundary": (
            "This sidecar inventories and dispositions all 309 explicit TeX math "
            "constructs in the retained main.tex closure: 291 render inline and "
            "18 render as displays. Every construct either inherits an existing "
            "source-detail or table-cell disposition or maps directly to an "
            "existing bounded claim. It adds zero bounded claims and does not "
            "establish formula correctness, proof validity, result reproduction, "
            "whole-paper proposition exhaustiveness, or AlphaEvolve parity."
        ),
    }


def validate_alphaevolve_tex_math_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveTexMathInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_tex_math_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveTexMathInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_tex_math_inventory_boundary_record(root)
    issues: list[AlphaEvolveTexMathInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_TEX_MATH_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TeX math inventory schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    for key in (
        "mathematical_correctness_claim_ready",
        "result_reproduction_claim_ready",
        "alphaevolve_parity_claim_ready",
    ):
        if data.get(key) is not False:
            issues.append(_issue(f"{key}_overclaim", f"{key} must remain false"))
    if data.get("new_claim_count") != 0:
        issues.append(
            _issue(
                "new_claim_overclaim",
                "math disposition must add zero bounded claims",
            )
        )
    for key in (
        "source_artifact",
        "source_errors",
        "parse_errors",
        "source_closure",
        "math_construct_count",
        "inline_construct_count",
        "display_construct_count",
        "delimiter_kind_counts",
        "render_mode_counts",
        "disposition_counts",
        "source_detail_overlap_count",
        "table_cell_overlap_count",
        "direct_claim_mapping_count",
        "unmapped_construct_count",
        "unresolved_reference_count",
        "math_construct_records",
        "active_todo_refs",
        "todo_ownership_ready",
        "inventory_scope",
    ):
        if data.get(key) != expected[key]:
            issues.append(
                _issue(
                    f"invalid_{key}",
                    f"{key} drifted from the retained TeX math inventory",
                )
            )
    for key in ("math_construct_inventory_ready", "math_construct_disposition_ready"):
        if data.get(key) is not expected[key]:
            issues.append(
                _issue(
                    f"invalid_{key}",
                    f"{key} does not match source and disposition checks",
                )
            )
    if not expected["source_artifact"]["identity_ok"]:
        issues.append(
            _issue(
                "source_archive_identity_mismatch",
                "retained AlphaEvolve TeX archive identity does not match the pin",
            )
        )
    if expected["source_errors"]:
        issues.append(
            _issue(
                "source_inventory_incomplete",
                "TeX math inventory inputs are incomplete",
            )
        )
    if expected["parse_errors"]:
        issues.append(
            _issue(
                "math_parse_incomplete",
                "one or more explicit math constructs lack a stable disposition",
            )
        )
    if expected["unmapped_construct_count"]:
        issues.append(
            _issue(
                "unmapped_math_construct",
                "one or more explicit math constructs are unmapped",
            )
        )
    if expected["unresolved_reference_count"]:
        issues.append(
            _issue(
                "unresolved_math_reference",
                "one or more math disposition references are unresolved",
            )
        )
    if not expected["todo_ownership_ready"]:
        issues.append(
            _issue(
                "unowned_semantic_gap",
                (
                    "remaining proposition and correctness gaps require active "
                    "TODO ownership"
                ),
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "all 309" not in claim_boundary
        or "291 render inline" not in claim_boundary
        or "18 render as displays" not in claim_boundary
        or "zero bounded claims" not in claim_boundary
        or "does not establish formula correctness" not in claim_boundary
        or "AlphaEvolve parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                (
                    "claim_boundary must separate delimiter disposition from "
                    "correctness, reproduction, and parity"
                ),
            )
        )
    return AlphaEvolveTexMathInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=(
            data.get("boundary_status")
            if isinstance(data.get("boundary_status"), str)
            else None
        ),
        math_construct_count=(
            data.get("math_construct_count")
            if isinstance(data.get("math_construct_count"), int)
            else 0
        ),
        inline_construct_count=(
            data.get("inline_construct_count")
            if isinstance(data.get("inline_construct_count"), int)
            else 0
        ),
        display_construct_count=(
            data.get("display_construct_count")
            if isinstance(data.get("display_construct_count"), int)
            else 0
        ),
        unmapped_construct_count=(
            data.get("unmapped_construct_count")
            if isinstance(data.get("unmapped_construct_count"), int)
            else 0
        ),
        unresolved_reference_count=(
            data.get("unresolved_reference_count")
            if isinstance(data.get("unresolved_reference_count"), int)
            else 0
        ),
        issues=issues,
    )


def render_alphaevolve_tex_math_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_tex_math_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve TeX math inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| math_construct_count | {validation.math_construct_count} |",
        f"| inline_construct_count | {validation.inline_construct_count} |",
        f"| display_construct_count | {validation.display_construct_count} |",
        f"| unmapped_construct_count | {validation.unmapped_construct_count} |",
        f"| unresolved_reference_count | {validation.unresolved_reference_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _parse_math_constructs(
    tex_texts: dict[str, str],
    closure: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for file_index, source_file in enumerate(closure):
        text = _strip_tex_comments(tex_texts.get(source_file, ""))
        headings = _section_headings(text)
        masked = list(text)
        _mask_listing_environments(source_file, text, masked, errors)
        work = "".join(masked)
        candidates: list[tuple[int, int, str, str, str | None]] = []
        equation_pattern = re.compile(
            r"\\begin\{(equation\*?)\}(.*?)\\end\{\1\}", re.DOTALL
        )
        for match in equation_pattern.finditer(work):
            candidates.append(
                (match.start(), match.end(), "environment", match.group(2), match.group(1))
            )
            _mask_range(masked, match.start(), match.end())
        work = "".join(masked)
        for pattern, kind, body_group in (
            (re.compile(r"\$\$(.*?)\$\$", re.DOTALL), "double_dollar", 1),
            (re.compile(r"\\\[(.*?)\\\]", re.DOTALL), "bracket", 1),
            (re.compile(r"\\\((.*?)\\\)", re.DOTALL), "paren", 1),
        ):
            for match in pattern.finditer(work):
                candidates.append(
                    (match.start(), match.end(), kind, match.group(body_group), None)
                )
                _mask_range(masked, match.start(), match.end())
            work = "".join(masked)
        dollar_offsets = [
            offset
            for offset, character in enumerate(work)
            if character == "$" and not _is_escaped(work, offset)
        ]
        if len(dollar_offsets) % 2:
            errors.append(f"unclosed_single_dollar:{source_file}:{len(dollar_offsets)}")
        for start, close in zip(dollar_offsets[::2], dollar_offsets[1::2]):
            candidates.append((start, close + 1, "single_dollar", text[start + 1 : close], None))
        candidates.sort(key=lambda row: row[0])
        line_ordinals: Counter[int] = Counter()
        for start, end, kind, body, environment_name in candidates:
            source_line = _line_number(text, start)
            ordinal = line_ordinals[source_line]
            line_ordinals[source_line] += 1
            line_start = text.rfind("\n", 0, start) + 1
            line_end = text.find("\n", start)
            if line_end < 0:
                line_end = len(text)
            end_offset = max(start, end - 1)
            section_path = _section_path_at(headings, start)
            if source_file == "main.tex" and not section_path:
                section_path = ["Abstract"]
            render_mode = (
                "inline"
                if kind == "paren" or (kind == "single_dollar" and "\n" not in body)
                else "display"
            )
            records.append(
                {
                    "math_construct_id": f"tex_math_{len(records) + 1:04d}",
                    "source_file": source_file,
                    "source_line": source_line,
                    "source_column": _column_number(text, start),
                    "source_end_line": _line_number(text, end_offset),
                    "source_end_column": _column_number(text, end_offset),
                    "line_ordinal": ordinal,
                    "section_path": section_path,
                    "delimiter_kind": kind,
                    "environment_name": environment_name,
                    "render_mode": render_mode,
                    "source_text": text[start:end],
                    "normalized_body": _normalize_whitespace(body),
                    "source_text_sha256": hashlib.sha256(
                        text[start:end].encode("utf-8")
                    ).hexdigest(),
                    "source_line_sha256": hashlib.sha256(
                        text[line_start:line_end].encode("utf-8")
                    ).hexdigest(),
                    "_file_index": file_index,
                    "_start": start,
                    "_end": end,
                }
            )
    return records, errors


def _mask_listing_environments(
    source_file: str,
    text: str,
    masked: list[str],
    errors: list[str],
) -> None:
    begin_pattern = re.compile(r"\\begin\{(minted|lstlisting|verbatim)\}")
    for match in begin_pattern.finditer(text):
        end_match = re.search(
            rf"\\end\{{{re.escape(match.group(1))}\}}",
            text[match.end() :],
        )
        if end_match is None:
            errors.append(
                (
                    f"unclosed_listing_environment:{source_file}:"
                    f"{_line_number(text, match.start())}:{match.group(1)}"
                )
            )
            continue
        end = match.end() + end_match.end()
        _mask_range(masked, match.start(), end)


def _mask_range(characters: list[str], start: int, end: int) -> None:
    for offset in range(start, end):
        if characters[offset] not in "\r\n":
            characters[offset] = " "


def _is_escaped(text: str, offset: int) -> bool:
    slash_count = 0
    cursor = offset - 1
    while cursor >= 0 and text[cursor] == "\\":
        slash_count += 1
        cursor -= 1
    return bool(slash_count % 2)


def _disposition_records(
    parsed: list[dict[str, Any]],
    claim_catalog: dict[tuple[str, str], dict[str, Any]],
    supports: dict[str, list[dict[str, Any]]],
) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    used_direct_keys: set[tuple[str, int, int]] = set()
    for parsed_record in parsed:
        source_file = parsed_record["source_file"]
        start = parsed_record["_start"]
        end = parsed_record["_end"]
        overlapping = [
            support
            for support in supports.get(source_file, [])
            if start >= support["start"] and end <= support["end"]
        ]
        claim_refs: list[dict[str, Any]] = []
        named_span_refs: list[dict[str, Any]] = []
        supporting_boundary_refs: list[dict[str, Any]] = []
        supporting_unit_refs: list[dict[str, Any]] = []
        source_pages: set[int] = set()
        source_span_ids: set[str] = set()
        if overlapping:
            disposition = "inherited_source_unit_disposition"
            for support in overlapping:
                supporting_unit_refs.append(
                    {
                        "inventory_path": support["inventory_path"],
                        "record_id": support["record_id"],
                        "resolved": True,
                    }
                )
                claim_refs.extend(support["claim_refs"])
                named_span_refs.extend(support["named_span_refs"])
                supporting_boundary_refs.extend(support["supporting_boundary_refs"])
                if isinstance(support.get("source_page"), int):
                    source_pages.add(support["source_page"])
                if isinstance(support.get("source_span_id"), str):
                    source_span_ids.add(support["source_span_id"])
        else:
            key = (source_file, parsed_record["source_line"])
            line_mapping = _DIRECT_CLAIM_MAP.get(key)
            targets = (
                line_mapping.get(parsed_record["line_ordinal"], ())
                if isinstance(line_mapping, dict)
                else line_mapping or ()
            )
            if not targets:
                disposition = "unmapped"
                errors.append(
                    (
                        f"unmapped_math_construct:{source_file}:"
                        f"{parsed_record['source_line']}:"
                        f"{parsed_record['line_ordinal']}"
                    )
                )
            else:
                disposition = "direct_bounded_claim_mapping"
                used_direct_keys.add(
                    (source_file, parsed_record["source_line"], parsed_record["line_ordinal"])
                )
                for target in targets:
                    metadata = claim_catalog.get(target)
                    claim_refs.append(
                        {
                            "inventory_path": target[0],
                            "claim_id": target[1],
                            "resolved": metadata is not None,
                        }
                    )
                    if metadata is not None:
                        if isinstance(metadata.get("source_page"), int):
                            source_pages.add(metadata["source_page"])
                        if isinstance(metadata.get("source_span_id"), str):
                            source_span_ids.add(metadata["source_span_id"])
        record = dict(parsed_record)
        record.pop("_file_index")
        record.pop("_start")
        record.pop("_end")
        record.update(
            {
                "source_pages": sorted(source_pages),
                "source_span_ids": sorted(source_span_ids),
                "disposition": disposition,
                "claim_refs": _dedupe_refs(claim_refs),
                "named_span_refs": _dedupe_refs(named_span_refs),
                "supporting_boundary_refs": _dedupe_refs(supporting_boundary_refs),
                "supporting_unit_refs": _dedupe_refs(supporting_unit_refs),
            }
        )
        records.append(record)
    expected_direct_keys = {
        (source_file, source_line, ordinal)
        for (source_file, source_line), mapping in _DIRECT_CLAIM_MAP.items()
        for ordinal in (
            mapping.keys()
            if isinstance(mapping, dict)
            else {
                record["line_ordinal"]
                for record in parsed
                if record["source_file"] == source_file
                and record["source_line"] == source_line
            }
        )
    }
    for missing in sorted(expected_direct_keys - used_direct_keys):
        errors.append(f"unused_direct_math_mapping:{missing[0]}:{missing[1]}:{missing[2]}")
    return records, errors


def _claim_catalog(
    root: Path,
) -> tuple[dict[tuple[str, str], dict[str, Any]], list[str]]:
    catalog: dict[tuple[str, str], dict[str, Any]] = {}
    errors: list[str] = []
    for path in _CLAIM_INVENTORY_PATHS.values():
        data, error = _read_json_object(root / path)
        if error:
            errors.append(f"claim_inventory_{error}:{path}")
            continue
        for collection in ("claim_records", "requirement_records"):
            rows = data.get(collection)
            if not isinstance(rows, list):
                continue
            for row in rows:
                if not isinstance(row, dict):
                    continue
                claim_id = row.get("claim_id", row.get("requirement_id"))
                if isinstance(claim_id, str):
                    catalog[(path, claim_id)] = row
    return catalog, errors


def _support_ranges(
    root: Path,
    tex_texts: dict[str, str],
) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    supports: dict[str, list[dict[str, Any]]] = {}
    errors: list[str] = []
    specs = (
        (_SOURCE_DETAIL_PATH, "source_detail_records", "construct_id", "command_text"),
        (_TABLE_CELL_PATH, "cell_records", "table_cell_id", "raw_text"),
    )
    for path, collection, id_key, text_key in specs:
        data, error = _read_json_object(root / path)
        if error:
            errors.append(f"support_inventory_{error}:{path}")
            continue
        rows = data.get(collection)
        if not isinstance(rows, list):
            errors.append(f"support_inventory_missing_collection:{path}:{collection}")
            continue
        for row in rows:
            if not isinstance(row, dict):
                continue
            source_file = row.get("source_file")
            source_line = row.get("source_line")
            source_column = row.get("source_column")
            source_text = row.get(text_key)
            record_id = row.get(id_key)
            if not (
                isinstance(source_file, str)
                and isinstance(source_line, int)
                and isinstance(source_column, int)
                and isinstance(source_text, str)
                and isinstance(record_id, str)
            ):
                errors.append(f"support_inventory_invalid_record:{path}")
                continue
            text = _strip_tex_comments(tex_texts.get(source_file, ""))
            start = _offset_at(text, source_line, source_column)
            end = start + len(source_text)
            if text[start:end] != source_text:
                errors.append(f"support_inventory_source_drift:{path}:{record_id}")
                continue
            supports.setdefault(source_file, []).append(
                {
                    "inventory_path": path,
                    "record_id": record_id,
                    "start": start,
                    "end": end,
                    "source_page": row.get("source_page"),
                    "source_span_id": row.get("source_span_id", row.get("table_id")),
                    "claim_refs": (
                        row.get("claim_refs", [])
                        if isinstance(row.get("claim_refs"), list)
                        else []
                    ),
                    "named_span_refs": (
                        row.get("named_span_refs", [])
                        if isinstance(row.get("named_span_refs"), list)
                        else []
                    ),
                    "supporting_boundary_refs": (
                        row.get("supporting_boundary_refs", [])
                        if isinstance(row.get("supporting_boundary_refs"), list)
                        else []
                    ),
                }
            )
    return supports, errors


def _dedupe_refs(refs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    for ref in refs:
        key = json.dumps(ref, sort_keys=True, ensure_ascii=False)
        if key not in seen:
            seen.add(key)
            result.append(ref)
    return result


def _offset_at(text: str, line: int, column: int) -> int:
    if line < 1 or column < 1:
        return len(text)
    offset = 0
    for _ in range(line - 1):
        newline = text.find("\n", offset)
        if newline < 0:
            return len(text)
        offset = newline + 1
    return offset + column - 1


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _column_number(text: str, offset: int) -> int:
    return offset - text.rfind("\n", 0, offset)


def _read_json_object(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {}, type(exc).__name__
    return (data, None) if isinstance(data, dict) else ({}, "invalid_shape")


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


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveTexMathInventoryBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "TeX math inventory must be a JSON object")]


def _issue(code: str, message: str) -> AlphaEvolveTexMathInventoryBoundaryIssue:
    return AlphaEvolveTexMathInventoryBoundaryIssue(code, message)
