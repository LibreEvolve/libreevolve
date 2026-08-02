from __future__ import annotations

import hashlib
import json
import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_citation_use_inventory_boundary import (
    EXPECTED_ENTRYPOINT,
    EXPECTED_TEX_CLOSURE_FILES,
    _read_source_archive,
    _section_headings,
    _section_path_at,
    _strip_tex_comments,
    _tex_dependency_closure,
)
from libreevolve.problems.benchmarks.paper_bibliography import (
    EXPECTED_SOURCE_PAPER_ID,
)


ALPHAEVOLVE_TEX_PROSE_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_tex_prose_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "retained_tex_paragraph_and_sentence_inventory_complete_without_"
    "semantic_clause_exhaustiveness"
)
EXPECTED_PARAGRAPH_COUNT = 128
EXPECTED_SENTENCE_COUNT = 402

_EXCLUDED_FILE_REASONS = {
    "authors.tex": "author_metadata_covered_by_manifest_and_pdf_identity",
    "preamble.tex": "typesetting_macros_without_paper_body_prose",
}
_EXCLUDED_ENVIRONMENTS = frozenset(
    {
        "equation",
        "equation*",
        "figure",
        "lstlisting",
        "minted",
        "table",
        "verbatim",
        "wrapfigure",
    }
)
_TRANSPARENT_ENVIRONMENTS = frozenset(
    {
        "abstract",
        "adjustbox",
        "center",
        "document",
        "itemize",
        "lemma",
        "minipage",
        "proof",
        "subfigure",
    }
)
_WHOLE_COMMANDS = frozenset(
    {
        "PassOptionsToPackage",
        "addtocounter",
        "affil",
        "author",
        "bibliography",
        "bibliographystyle",
        "caption",
        "correspondingauthor",
        "date",
        "documentclass",
        "email",
        "equalcontrib",
        "include",
        "includegraphics",
        "input",
        "label",
        "renewcommand",
        "section",
        "subsection",
        "subsubsection",
        "title",
        "usepackage",
        "vspace",
    }
)
_INLINE_MASK_COMMANDS = frozenset({"footnote", "href", "paragraph", "url"})
_STANDALONE_COMMANDS = frozenset(
    {
        "appendix",
        "centering",
        "clearpage",
        "item",
        "newpage",
        "noindent",
        "small",
    }
)
_CITATION_COMMAND_PATTERN = re.compile(
    r"\\(?:cite|citealp|citep|citet|authoryearcite|authoryearcitet|"
    r"Cref|cref|ref)\w*"
)
_ABBREVIATIONS = frozenset(
    {
        "dr.",
        "e.g.",
        "eq.",
        "et al.",
        "fig.",
        "figs.",
        "i.e.",
        "no.",
        "resp.",
        "sec.",
        "secs.",
        "vs.",
    }
)

_CLAIM_INVENTORY_PATHS = {
    "system": "papers/alphaevolve_system_requirement_inventory_boundary.json",
    "context": "papers/alphaevolve_context_claim_inventory_boundary.json",
    "matrix": "papers/alphaevolve_matrix_result_claim_inventory_boundary.json",
    "math": "papers/alphaevolve_math_result_claim_inventory_boundary.json",
    "scheduling": "papers/alphaevolve_scheduling_claim_inventory_boundary.json",
    "kernel": "papers/alphaevolve_kernel_claim_inventory_boundary.json",
    "hardware": "papers/alphaevolve_hardware_claim_inventory_boundary.json",
    "compiler": "papers/alphaevolve_compiler_claim_inventory_boundary.json",
    "ablation": "papers/alphaevolve_ablation_claim_inventory_boundary.json",
    "related": "papers/alphaevolve_related_work_claim_inventory_boundary.json",
    "appendix_a": "papers/alphaevolve_appendix_a_claim_inventory_boundary.json",
    "appendix_b": "papers/alphaevolve_appendix_b_claim_inventory_boundary.json",
}
_FILE_CLAIM_INVENTORIES = {
    "main.tex": ("context",),
    "introduction.tex": ("context",),
    "methods.tex": ("system",),
    "grounding_example.tex": ("system",),
    "results.tex": (
        "matrix",
        "math",
        "scheduling",
        "kernel",
        "hardware",
        "compiler",
    ),
    "ablations.tex": ("ablation",),
    "related_work.tex": ("related",),
    "discussion.tex": ("context",),
    "acknowledgement.tex": ("context",),
    "appendix.tex": ("appendix_a", "appendix_b"),
    "discovered_program.tex": ("appendix_a",),
    "discovered_program_appendix.tex": ("appendix_a",),
}

def _claim_refs(
    inventory_name: str,
    *claim_ids: str,
) -> tuple[tuple[str, str], ...]:
    path = _CLAIM_INVENTORY_PATHS[inventory_name]
    return tuple((path, claim_id) for claim_id in claim_ids)


# Stable source-line overrides are added only after a sentence has been reviewed.
_DIRECT_CLAIM_MAP: dict[
    tuple[str, int, int], tuple[tuple[str, str], ...]
] = {
    ("introduction.tex", 16, 0): _claim_refs(
        "related", "recent_llm_evolution_predecessors"
    ),
    ("introduction.tex", 17, 0): _claim_refs("related", "extends_funsearch"),
    ("introduction.tex", 18, 0): _claim_refs(
        "related",
        "llm_evolution_robot_policies",
        "llm_evolution_symbolic_regression",
        "llm_evolution_combinatorial_heuristics",
    ),
    ("introduction.tex", 19, 1): _claim_refs(
        "context", "introduction_large_code_evolution"
    ),
    ("main.tex", 34, 0): _claim_refs(
        "context",
        "abstract_complex_4x4_matrix_48_multiplications",
        "abstract_first_strassen_improvement_56_years",
    ),
    ("introduction.tex", 45, 0): _claim_refs(
        "context", "abstract_broad_applicability"
    ),
    ("introduction.tex", 47, 0): _claim_refs(
        "related", "alphatensor_limited_matrix_setting"
    ),
    ("introduction.tex", 48, 0): _claim_refs(
        "context",
        "introduction_fourteen_matrix_sota_improvements",
        "introduction_complex_4x4_matrix_48_multiplications",
    ),
    ("introduction.tex", 51, 0): _claim_refs(
        "context",
        "introduction_algorithmic_candidate_representation",
        "introduction_automatically_evaluable_problem_scope",
    ),
    ("introduction.tex", 52, 1): _claim_refs(
        "context", "introduction_twenty_percent_math_sota_uplift"
    ),
    ("introduction.tex", 52, 0): _claim_refs(
        "context",
        "introduction_over_fifty_math_problems_best_known",
        "introduction_seventy_five_percent_math_best_known",
    ),
    ("introduction.tex", 53, 0): _claim_refs(
        "context",
        "introduction_erdos_minimum_overlap_result",
        "introduction_kissing_number_d11_improvement",
    ),
    ("introduction.tex", 56, 0): _claim_refs(
        "context", "introduction_four_google_compute_stack_results"
    ),
    ("methods.tex", 32, 0): _claim_refs(
        "system", "task_scalar_metric_mapping"
    )
    + _claim_refs(
        "context", "introduction_automatically_evaluable_problem_scope"
    ),
    ("methods.tex", 37, 1): _claim_refs(
        "system", "task_evaluation_workload_range"
    ),
    ("methods.tex", 38, 0): _claim_refs(
        "system",
        "task_scalar_metric_mapping",
        "task_constructor_function_abstraction",
    ),
    ("methods.tex", 39, 0): _claim_refs(
        "system",
        "task_evaluation_workload_range",
        "task_bespoke_search_abstraction",
    ),
    ("methods.tex", 48, 0): _claim_refs(
        "system", "task_problem_specific_abstraction_choice"
    )
    + _claim_refs(
        "context", "introduction_algorithm_discovery_instrumental_goal"
    ),
    ("methods.tex", 76, 0): _claim_refs(
        "system",
        "prompt_prior_solutions_and_instructions",
        "generation_model_ensemble",
    ),
    ("methods.tex", 91, 0): _claim_refs(
        "system", "generation_search_replace_blocks"
    ),
    ("methods.tex", 91, 1): _claim_refs(
        "system", "generation_search_replace_blocks"
    ),
    ("methods.tex", 92, 0): _claim_refs(
        "system", "generation_search_replace_blocks"
    ),
    ("methods.tex", 98, 0): _claim_refs(
        "system", "generation_model_ensemble", "generation_fast_strong_model_mix"
    ),
    ("methods.tex", 99, 0): _claim_refs(
        "system", "generation_fast_strong_model_mix"
    ),
    ("methods.tex", 100, 0): _claim_refs(
        "system", "generation_fast_strong_model_mix"
    ),
    ("methods.tex", 101, 0): _claim_refs(
        "system", "generation_fast_strong_model_mix"
    ),
    ("methods.tex", 107, 0): _claim_refs(
        "system", "evaluation_every_proposal", "evolution_database_resurfacing"
    ),
    ("methods.tex", 108, 0): _claim_refs(
        "system", "evaluation_every_proposal", "task_scalar_metric_mapping"
    ),
    ("methods.tex", 113, 0): _claim_refs(
        "system", "evaluation_increasing_difficulty_cascade"
    ),
    ("methods.tex", 113, 1): _claim_refs(
        "system", "evaluation_increasing_difficulty_cascade"
    ),
    ("methods.tex", 115, 0): _claim_refs(
        "system", "evaluation_llm_generated_feedback"
    ),
    ("methods.tex", 118, 0): _claim_refs(
        "system",
        "evaluation_order_hundred_compute_hours_per_candidate",
        "evaluation_sample_efficiency_enables_expensive_evaluation",
    ),
    ("methods.tex", 119, 0): _claim_refs(
        "system",
        "evaluation_order_hundred_compute_hours_per_candidate",
        "evaluation_async_cluster_parallelism",
    ),
    ("methods.tex", 125, 0): _claim_refs(
        "system", "evaluation_multi_metric_single_target_uplift"
    ),
    ("results.tex", 43, 0): _claim_refs(
        "matrix", "section3_1_3x3_minimum_rank_unknown"
    ),
    ("results.tex", 45, 0): _claim_refs(
        "matrix",
        "section3_1_standard_gradient_baseline_components",
        "section3_1_sophisticated_algorithms_outperform_approaches",
    )
    + _claim_refs("system", "prompt_explicit_context"),
    ("results.tex", 46, 0): _claim_refs(
        "matrix", "section3_1_multi_seed_evaluation_cascade"
    )
    + _claim_refs("system", "evaluation_every_proposal"),
    ("results.tex", 47, 0): _claim_refs(
        "matrix", "section3_1_best_rank_and_seed_hit_fraction"
    )
    + _claim_refs("system", "section2_evolutionary_metric_improvement"),
    ("results.tex", 48, 0): _claim_refs(
        "matrix",
        "section3_1_integer_half_integer_rounding_exactness",
        "section3_1_natural_language_near_integrality_prompt",
    ),
    ("results.tex", 53, 0): _claim_refs(
        "matrix", "section3_1_recursive_strassen_rank49_any_field"
    ),
    ("results.tex", 54, 0): _claim_refs(
        "matrix", "section3_1_fawzi_rank47_field_two"
    ),
    ("results.tex", 57, 0): _claim_refs(
        "matrix", "section3_1_first_rank48_complex_4x4"
    ),
    ("results.tex", 60, 0): _claim_refs(
        "matrix",
        "section3_1_most_table2_simple_initial_program",
        "section3_1_researcher_ideas_boost_performance",
        "section3_1_scientific_collaboration_possibility",
    ),
    ("results.tex", 68, 1): _claim_refs(
        "math",
        "section3_2_seventy_five_percent_rediscovery",
        "section3_2_twenty_percent_sota_improvement",
    ),
    ("results.tex", 82, 1): _claim_refs(
        "math", "section3_2_full_list_and_details_in_appendix_b"
    ),
    ("results.tex", 103, 0): _claim_refs(
        "math",
        "section3_2_full_list_and_details_in_appendix_b",
        "section3_2_new_constructions_in_companion_colab",
    ),
    ("results.tex", 117, 2): _claim_refs(
        "scheduling", "section3_3_1_heuristic_required_and_free_inputs"
    ),
    ("results.tex", 119, 1): _claim_refs(
        "scheduling", "section3_3_1_historical_fleet_snapshot_simulator_feedback"
    ),
    ("results.tex", 150, 2): _claim_refs(
        "kernel", "section3_3_2_pallas_kernel_training_importance"
    ),
    ("results.tex", 168, 0): _claim_refs(
        "hardware",
        "already_highly_optimized_verilog_target",
        "key_tpu_arithmetic_circuit_target",
        "matrix_multiplication_unit_context",
    ),
    ("ablations.tex", 8, 3): _claim_refs(
        "ablation", "no_context_variant_name"
    ),
    ("ablations.tex", 9, 4): _claim_refs(
        "ablation", "no_meta_prompt_variant_name"
    ),
    ("ablations.tex", 10, 3): _claim_refs(
        "ablation", "no_full_file_variant_name"
    ),
    ("ablations.tex", 11, 3): _claim_refs(
        "ablation", "small_base_only_variant_name"
    ),
    ("ablations.tex", 29, 0): _claim_refs(
        "ablation", "figure8_reports_full_and_alternative_results"
    ),
    ("related_work.tex", 45, 0): _claim_refs(
        "related", "evolutionary_llm_approach_enables_harder_problems"
    ),
    ("discussion.tex", 12, 0): _claim_refs(
        "context", "discussion_distill_augmented_performance"
    ),
    ("discussion.tex", 19, 0): _claim_refs(
        "context", "discussion_automated_evaluator_limitation"
    ),
    ("appendix.tex", 3, 0): _claim_refs(
        "appendix_a", "appendix_a_best_ranks_in_table3"
    ),
    ("appendix.tex", 84, 0): _claim_refs(
        "appendix_a", "table3_concurrent_rank90_4x5x6"
    ),
    ("appendix.tex", 96, 0): _claim_refs(
        "appendix_b", "b1_autoconvolution_definition"
    ),
    ("appendix.tex", 97, 0): _claim_refs(
        "appendix_b", "b1_c1_largest_constant", "b1_equation_1_max_autoconvolution"
    ),
    ("appendix.tex", 101, 0): _claim_refs(
        "appendix_b", "b1_nonnegative_real_functions"
    ),
    ("appendix.tex", 101, 2): _claim_refs(
        "appendix_b",
        "b1_known_lower_bound_1_28",
        "b1_known_upper_bound_1_5098",
        "b1_lower_bound_source_17",
        "b1_upper_bound_source_70",
        "b1_prior_step_function_construction",
    ),
    ("appendix.tex", 104, 0): _claim_refs(
        "appendix_b",
        "b1_alphaevolve_600_intervals",
        "b1_alphaevolve_equal_spacing",
        "b1_alphaevolve_domain",
        "b1_alphaevolve_bound_1_5053",
    ),
    ("appendix.tex", 107, 0): _claim_refs(
        "appendix_b",
        "b2_c2_smallest_constant",
        "b2_norm_inequality",
        "b2_nonnegative_real_functions",
    ),
    ("appendix.tex", 110, 0): _claim_refs(
        "appendix_b",
        "b2_known_lower_bound_0_88922",
        "b2_known_upper_bound_1",
        "b2_lower_bound_step_source_70",
    ),
    ("appendix.tex", 113, 0): _claim_refs(
        "appendix_b",
        "b2_alphaevolve_50_intervals",
        "b2_alphaevolve_equal_spacing",
        "b2_alphaevolve_domain",
        "b2_alphaevolve_bound_0_8962",
    ),
    ("appendix.tex", 116, 0): _claim_refs(
        "appendix_b",
        "b3_c3_largest_constant",
        "b3_absolute_autoconvolution_inequality",
        "b3_signed_real_functions",
    ),
    ("appendix.tex", 118, 0): _claim_refs(
        "appendix_b", "b3_c3_at_most_c1", "b3_c3_c1_signed_reason"
    ),
    ("appendix.tex", 119, 0): _claim_refs(
        "appendix_b", "b3_prior_bound_1_45810", "b3_prior_source_104_page_75"
    ),
    ("appendix.tex", 120, 0): _claim_refs(
        "appendix_b",
        "b3_alphaevolve_400_intervals",
        "b3_alphaevolve_equal_spacing_and_domain",
        "b3_alphaevolve_bound_1_4557",
    ),
    ("appendix.tex", 125, 0): _claim_refs(
        "appendix_b", "b4_fourier_transform_definition", "b4_a_function_definition"
    ),
    ("appendix.tex", 127, 0): _claim_refs(
        "appendix_b",
        "b4_c4_largest_constant",
        "b4_uncertainty_product_inequality",
        "b4_even_function_condition",
        "b4_negative_origin_condition",
    ),
    ("appendix.tex", 129, 0): _claim_refs(
        "appendix_b",
        "b4_known_lower_bound_0_2025",
        "b4_known_upper_bound_0_3523",
        "b4_prior_source_33",
    ),
    ("appendix.tex", 132, 0): _claim_refs(
        "appendix_b",
        "b4_first_version_result_0_3521",
        "b4_similar_linear_combination",
        "b4_refined_constants_found_by_alphaevolve",
    ),
    ("appendix.tex", 134, 6): _claim_refs(
        "appendix_b", "b4_c4_at_most_a_squared"
    ),
    ("appendix.tex", 136, 2): _claim_refs(
        "appendix_b", "b4_rmax_root_of_quotient"
    ),
    ("appendix.tex", 136, 3): _claim_refs(
        "appendix_b", "b4_bound_rmax_squared_over_2pi"
    ),
    ("appendix.tex", 136, 1): _claim_refs(
        "appendix_b", "b4_p_zero_condition", "b4_x_squared_factor"
    ),
    ("appendix.tex", 138, 0): _claim_refs(
        "appendix_b",
        "b4_refined_constants_found_by_alphaevolve",
        "b4_reported_coefficients",
    ),
    ("appendix.tex", 138, 1): _claim_refs(
        "appendix_b", "b4_coefficients_yield_0_3521", "b4_first_version_result_0_3521"
    ),
    ("appendix.tex", 138, 2): _claim_refs(
        "appendix_b",
        "b4_qualitative_similarity_to_33",
        "b4_empirical_near_optimal_hypothesis",
    ),
    ("appendix.tex", 140, 2): _claim_refs(
        "appendix_b", "b4_revision_details_in_colab"
    ),
    ("appendix.tex", 144, 0): _claim_refs(
        "appendix_b",
        "b5_c5_largest_constant",
        "b5_original_overlap_integral",
        "b5_f_g_nonnegative_unit_range",
        "b5_f_plus_g_one",
        "b5_integral_f_one",
        "b5_zero_extension",
    ),
    ("appendix.tex", 146, 1): _claim_refs(
        "appendix_b",
        "b5_known_lower_bound_0_379005",
        "b5_known_upper_bound_0_380927",
        "b5_lower_bound_source_107",
    ),
    ("appendix.tex", 159, 0): _claim_refs(
        "appendix_b", "b5_prior_upper_step_construction_40"
    ),
    ("appendix.tex", 160, 0): _claim_refs(
        "appendix_b", "b5_figure10_slight_improvement", "b5_alphaevolve_bound_0_380924"
    ),
    ("appendix.tex", 173, 0): _claim_refs(
        "appendix_b",
        "b6_c6_largest_constant",
        "b6_arbitrarily_large_integer_sets",
        "b6_small_sumset_condition",
        "b6_large_difference_condition",
    ),
    ("appendix.tex", 174, 1): _claim_refs(
        "appendix_b", "b6_little_less_notation"
    ),
    ("appendix.tex", 174, 2): _claim_refs(
        "appendix_b", "b6_little_greater_notation"
    ),
    ("appendix.tex", 178, 0): _claim_refs(
        "appendix_b",
        "b6_upper_bound_source_39_corollary_3",
        "b6_lower_bound_source_39_theorem_1",
    ),
    ("appendix.tex", 184, 0): _claim_refs(
        "appendix_b",
        "b6_u1_size_2003",
        "b6_u1_bound_1_1479",
        "b6_u2_size_54265",
        "b6_u2_bound_1_1584",
    ),
    ("appendix.tex", 193, 0): _claim_refs(
        "appendix_b", "figure11_two_packing_panels"
    ),
    ("appendix.tex", 207, 0): _claim_refs(
        "appendix_b", "b8_two_new_constructions", "figure12_two_distance_panels"
    ),
    ("appendix.tex", 206, 1): _claim_refs(
        "appendix_b", "b8_two_new_constructions", "b8_both_improve_best_known"
    ),
    ("appendix.tex", 209, 0): _claim_refs(
        "appendix_b",
        "figure12_left_16_points_2d",
        "figure12_left_ratio_12_889266112",
        "b8_2d_prior_sqrt_12_890",
        "b8_both_improve_best_known",
    ),
    ("appendix.tex", 212, 0): _claim_refs(
        "appendix_b",
        "figure12_right_14_points_3d",
        "figure12_right_ratio_4_165849767",
        "b8_3d_prior_sqrt_4_168",
        "b8_both_improve_best_known",
    ),
    ("appendix.tex", 226, 0): _claim_refs(
        "appendix_b",
        "b9_triangle_unit_area_domain",
        "b9_maximize_smallest_triangle_area",
    ),
    ("appendix.tex", 229, 0): _claim_refs(
        "appendix_b",
        "b10_convex_unit_area_domain",
        "b10_maximize_smallest_triangle_area",
    ),
    ("appendix.tex", 256, 0): _claim_refs(
        "appendix_b", "b11_lemma_center_transformation"
    ),
    ("appendix.tex", 260, 0): _claim_refs(
        "appendix_b", "b11_proof_inner_product_equation_4"
    ),
    ("appendix.tex", 267, 1): _claim_refs(
        "appendix_b", "b11_nonoverlap_inner_product_equivalence"
    ),
    ("appendix.tex", 275, 0): _claim_refs(
        "appendix_b", "b11_proof_valid_configuration_conclusion"
    ),
    ("appendix.tex", 281, 0): _claim_refs(
        "appendix_b", "b12_unit_square_circle_problem", "b12_maximize_sum_of_radii"
    ),
    ("appendix.tex", 281, 1): _claim_refs(
        "appendix_b", "b12_two_new_constructions"
    ),
    ("appendix.tex", 287, 0): _claim_refs(
        "appendix_b",
        "b13_perimeter4_rectangle_problem",
        "b13_maximize_sum_of_radii",
    ),
}
_NONCLAIM_DISPOSITIONS: dict[tuple[str, int, int], tuple[str, str]] = {
    ("main.tex", 34, 1): (
        "author_outlook",
        "Forward-looking impact outlook is not a LibreEvolve implementation requirement.",
    ),
    ("introduction.tex", 5, 1): (
        "literature_motivation",
        "Field-interest motivation does not specify AlphaEvolve behavior to implement.",
    ),
    ("introduction.tex", 6, 0): (
        "literature_context",
        "LLM, test-time-compute, and agent background is source context.",
    ),
    ("introduction.tex", 6, 1): (
        "literature_context",
        "Benchmark and discovery-task background is not a platform requirement.",
    ),
    ("introduction.tex", 6, 2): (
        "problem_motivation",
        "General discovery difficulty motivates the work without specifying behavior.",
    ),
    ("methods.tex", 13, 0): (
        "figure_navigation",
        "Cross-reference navigation adds no requirement beyond the figure inventories.",
    ),
    ("methods.tex", 60, 0): (
        "list_introduction",
        "The sentence introduces an itemized list whose substantive items are mapped.",
    ),
    ("methods.tex", 109, 0): (
        "list_introduction",
        "The sentence introduces evaluator mechanisms dispositioned in following items.",
    ),
    ("results.tex", 39, 0): (
        "domain_motivation",
        "General matrix-multiplication importance is domain context, not a requirement.",
    ),
    ("results.tex", 82, 0): (
        "section_navigation",
        "The sentence introduces examples whose substantive claims are mapped separately.",
    ),
    ("results.tex", 85, 0): (
        "list_category_label",
        "Analysis is a category heading rather than an implementation claim.",
    ),
    ("results.tex", 87, 0): (
        "list_category_label",
        "Autocorrelation inequalities is a problem label, not a standalone requirement.",
    ),
    ("results.tex", 88, 0): (
        "list_category_label",
        "Uncertainty principles is a problem label, not a standalone requirement.",
    ),
    ("results.tex", 91, 0): (
        "list_category_label",
        "Combinatorics and number theory is a category heading.",
    ),
    ("results.tex", 93, 0): (
        "list_category_label",
        "The Erdos minimum-overlap text is a problem label covered by detailed claims.",
    ),
    ("results.tex", 96, 0): (
        "list_category_label",
        "Geometry and packing is a category heading.",
    ),
    ("results.tex", 98, 0): (
        "list_category_label",
        "Kissing number problem is a problem label covered by detailed claims.",
    ),
    ("results.tex", 99, 0): (
        "list_category_label",
        "Packing problems is a problem label covered by detailed claims.",
    ),
    ("ablations.tex", 7, 0): (
        "ablation_component_label",
        "Evolutionary approach labels an ablation component mapped in adjacent prose.",
    ),
    ("ablations.tex", 8, 0): (
        "ablation_component_label",
        "Context in prompts labels an ablation component mapped in adjacent prose.",
    ),
    ("ablations.tex", 9, 0): (
        "ablation_component_label",
        "Meta prompts labels an ablation component mapped in adjacent prose.",
    ),
    ("ablations.tex", 10, 0): (
        "ablation_component_label",
        "Full-file evolution labels an ablation component mapped in adjacent prose.",
    ),
    ("ablations.tex", 11, 0): (
        "ablation_component_label",
        "Powerful language models labels an ablation component mapped in adjacent prose.",
    ),
    ("related_work.tex", 24, 0): (
        "literature_transition",
        "The sentence transitions between prior-work groups without a new requirement.",
    ),
    ("acknowledgement.tex", 4, 1): (
        "contributor_credit_introduction",
        "The sentence introduces contributor credits rather than implementation behavior.",
    ),
    ("acknowledgement.tex", 6, 0): (
        "contributor_credit",
        "Mathematical-application contributor credit is retained source provenance.",
    ),
    ("acknowledgement.tex", 8, 0): (
        "contributor_credit",
        "Data-center-scheduling contributor credit is retained source provenance.",
    ),
    ("acknowledgement.tex", 10, 0): (
        "contributor_credit",
        "Gemini-kernel contributor credit is retained source provenance.",
    ),
    ("acknowledgement.tex", 12, 0): (
        "contributor_credit",
        "TPU-circuit contributor credit is retained source provenance.",
    ),
    ("acknowledgement.tex", 14, 0): (
        "contributor_credit",
        "XLA contributor credit is retained source provenance.",
    ),
}


@dataclass(frozen=True)
class AlphaEvolveTexProseInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveTexProseInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    paragraph_count: int
    sentence_count: int
    unmapped_sentence_count: int
    unresolved_reference_count: int
    issues: list[AlphaEvolveTexProseInventoryBoundaryIssue]


def alphaevolve_tex_prose_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Inventory retained TeX body paragraphs and grammatical sentences."""

    root_path = Path(root)
    source_artifact, archive_texts, source_errors = _read_source_archive(root_path)
    tex_texts = {
        name: text
        for name, text in archive_texts.items()
        if name.casefold().endswith(".tex")
    }
    closure = _tex_dependency_closure(tex_texts, EXPECTED_ENTRYPOINT)
    paragraphs, sentences, exclusions, parse_errors = _parse_prose_units(
        tex_texts,
        closure,
    )
    claim_catalog, catalog_errors = _claim_catalog(root_path)
    sentence_records, disposition_errors = _disposition_records(
        sentences,
        claim_catalog,
    )
    paragraph_records = _paragraph_records(paragraphs, sentence_records)
    source_errors = sorted(set([*source_errors, *catalog_errors]))
    parse_errors = sorted(set([*parse_errors, *disposition_errors]))
    disposition_counts = Counter(
        record["disposition"] for record in sentence_records
    )
    unmapped_sentence_count = disposition_counts["unmapped"]
    unresolved_reference_count = sum(
        not ref["resolved"]
        for record in sentence_records
        for ref in record["claim_refs"]
    )
    inventory_ready = (
        source_artifact["identity_ok"]
        and not source_errors
        and tuple(closure) == EXPECTED_TEX_CLOSURE_FILES
        and len(paragraph_records) == EXPECTED_PARAGRAPH_COUNT
        and len(sentence_records) == EXPECTED_SENTENCE_COUNT
    )
    disposition_ready = (
        inventory_ready
        and not parse_errors
        and unmapped_sentence_count == 0
        and unresolved_reference_count == 0
    )
    return {
        "schema": ALPHAEVOLVE_TEX_PROSE_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "prose_inventory_ready": inventory_ready,
        "prose_disposition_ready": disposition_ready,
        "whole_paper_semantic_exhaustiveness_claim_ready": False,
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
        "excluded_file_records": [
            {"source_file": path, "reason": reason}
            for path, reason in sorted(_EXCLUDED_FILE_REASONS.items())
        ],
        "excluded_range_count": len(exclusions),
        "excluded_range_records": exclusions,
        "paragraph_count": len(paragraph_records),
        "sentence_count": len(sentence_records),
        "paragraph_counts_by_file": dict(
            sorted(Counter(row["source_file"] for row in paragraph_records).items())
        ),
        "sentence_counts_by_file": dict(
            sorted(Counter(row["source_file"] for row in sentence_records).items())
        ),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "unmapped_sentence_count": unmapped_sentence_count,
        "unresolved_reference_count": unresolved_reference_count,
        "paragraph_records": paragraph_records,
        "sentence_records": sentence_records,
        "inventory_scope": {
            "included": [
                (
                    "all grammatical sentences and residual prose statements "
                    "in body paragraphs of the recursive main.tex closure"
                ),
                (
                    "abstract, introduction, methods, results, ablations, "
                    "related work, discussion, acknowledgements, and appendix prose"
                ),
                "source offsets, lines, columns, section paths, and text hashes",
            ],
            "excluded": [
                "preamble and author-metadata files",
                (
                    "table, figure, wrapfigure, equation, and code-listing "
                    "environments covered by separate retained-TeX inventories"
                ),
                "semantic footnote bodies covered by the source-detail inventory",
                "sentence-internal proposition or clause decomposition",
                "mathematical correctness, proof checking, or result reproduction",
                "independent reviewer proof of semantic exhaustiveness",
                "AlphaEvolve system parity",
            ],
        },
        "claim_boundary": (
            "This boundary inventories retained TeX body paragraphs and their "
            "grammatical sentences while masking source surfaces covered by "
            "separate table, figure, equation, listing, and footnote inventories. "
            "A complete mechanical disposition does not prove sentence-internal "
            "proposition exhaustiveness, mathematical correctness, result "
            "reproduction, independent semantic review, or AlphaEvolve parity."
        ),
    }


def validate_alphaevolve_tex_prose_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveTexProseInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_tex_prose_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveTexProseInventoryBoundaryValidation(
            False,
            None,
            0,
            0,
            0,
            0,
            read_issues,
        )
    assert isinstance(data, dict)
    expected = alphaevolve_tex_prose_inventory_boundary_record(root)
    issues: list[AlphaEvolveTexProseInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_TEX_PROSE_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TeX prose schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(
            _issue("invalid_source_paper_id", "source_paper_id must be 2506.13131")
        )
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    for key in (
        "whole_paper_semantic_exhaustiveness_claim_ready",
        "mathematical_correctness_claim_ready",
        "result_reproduction_claim_ready",
        "alphaevolve_parity_claim_ready",
    ):
        if data.get(key) is not False:
            issues.append(_issue(f"{key}_overclaim", f"{key} must remain false"))
    for key in (
        "source_artifact",
        "source_errors",
        "parse_errors",
        "source_closure",
        "excluded_file_records",
        "excluded_range_count",
        "excluded_range_records",
        "paragraph_count",
        "sentence_count",
        "paragraph_counts_by_file",
        "sentence_counts_by_file",
        "disposition_counts",
        "unmapped_sentence_count",
        "unresolved_reference_count",
        "paragraph_records",
        "sentence_records",
        "inventory_scope",
    ):
        if data.get(key) != expected[key]:
            issues.append(
                _issue(f"invalid_{key}", f"{key} drifted from retained TeX prose")
            )
    for key in ("prose_inventory_ready", "prose_disposition_ready"):
        if data.get(key) is not expected[key]:
            issues.append(
                _issue(f"invalid_{key}", f"{key} does not match current evidence")
            )
    if not expected["source_artifact"]["identity_ok"]:
        issues.append(
            _issue(
                "source_archive_identity_mismatch",
                "retained AlphaEvolve TeX archive identity does not match the pin",
            )
        )
    if expected["source_errors"]:
        issues.append(_issue("source_inventory_incomplete", "prose inputs are incomplete"))
    if expected["parse_errors"]:
        issues.append(_issue("prose_parse_incomplete", "prose parsing is incomplete"))
    if expected["unmapped_sentence_count"]:
        issues.append(
            _issue(
                "unmapped_prose_sentence",
                "one or more retained prose sentences lack a disposition",
            )
        )
    if expected["unresolved_reference_count"]:
        issues.append(
            _issue(
                "unresolved_prose_reference",
                "one or more prose claim references are unresolved",
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "grammatical sentences" not in claim_boundary
        or "sentence-internal proposition exhaustiveness" not in claim_boundary
        or "mathematical correctness" not in claim_boundary
        or "AlphaEvolve parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must preserve the semantic and parity limits",
            )
        )
    return AlphaEvolveTexProseInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=(
            data.get("boundary_status")
            if isinstance(data.get("boundary_status"), str)
            else None
        ),
        paragraph_count=(
            data.get("paragraph_count")
            if isinstance(data.get("paragraph_count"), int)
            else 0
        ),
        sentence_count=(
            data.get("sentence_count")
            if isinstance(data.get("sentence_count"), int)
            else 0
        ),
        unmapped_sentence_count=(
            data.get("unmapped_sentence_count")
            if isinstance(data.get("unmapped_sentence_count"), int)
            else 0
        ),
        unresolved_reference_count=(
            data.get("unresolved_reference_count")
            if isinstance(data.get("unresolved_reference_count"), int)
            else 0
        ),
        issues=issues,
    )


def render_alphaevolve_tex_prose_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_tex_prose_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve TeX prose inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| paragraph_count | {validation.paragraph_count} |",
        f"| sentence_count | {validation.sentence_count} |",
        f"| unmapped_sentence_count | {validation.unmapped_sentence_count} |",
        f"| unresolved_reference_count | {validation.unresolved_reference_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _parse_prose_units(
    tex_texts: dict[str, str],
    closure: list[str],
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[str],
]:
    paragraphs: list[dict[str, Any]] = []
    sentences: list[dict[str, Any]] = []
    exclusions: list[dict[str, Any]] = []
    errors: list[str] = []
    for file_index, source_file in enumerate(closure):
        if source_file in _EXCLUDED_FILE_REASONS:
            continue
        text = _strip_tex_comments(tex_texts.get(source_file, ""))
        work, file_exclusions, file_errors = _prose_work_text(source_file, text)
        exclusions.extend(file_exclusions)
        errors.extend(file_errors)
        boundary_text = _sentence_boundary_text(work)
        headings = _section_headings(text)
        line_ordinals: Counter[int] = Counter()
        for paragraph_start, paragraph_end in _paragraph_ranges(text, work):
            paragraph_id = f"tex_prose_paragraph_{len(paragraphs) + 1:04d}"
            sentence_ids: list[str] = []
            sentence_ranges = _sentence_ranges(
                boundary_text,
                paragraph_start,
                paragraph_end,
            )
            for sentence_start, sentence_end in sentence_ranges:
                rendered_text = _render_tex_prose(text[sentence_start:sentence_end])
                if not rendered_text:
                    continue
                source_line = _line_number(text, sentence_start)
                line_ordinal = line_ordinals[source_line]
                line_ordinals[source_line] += 1
                sentence_id = f"tex_prose_sentence_{len(sentences) + 1:04d}"
                sentence_ids.append(sentence_id)
                sentences.append(
                    {
                        "sentence_id": sentence_id,
                        "paragraph_id": paragraph_id,
                        "source_file": source_file,
                        "source_line": source_line,
                        "source_column": _column_number(text, sentence_start),
                        "source_end_line": _line_number(text, sentence_end - 1),
                        "source_end_column": _column_number(text, sentence_end - 1),
                        "line_ordinal": line_ordinal,
                        "section_path": _section_path_at(headings, sentence_start),
                        "source_text": text[sentence_start:sentence_end],
                        "rendered_text": rendered_text,
                        "source_text_sha256": hashlib.sha256(
                            text[sentence_start:sentence_end].encode("utf-8")
                        ).hexdigest(),
                        "_file_index": file_index,
                        "_start": sentence_start,
                        "_end": sentence_end,
                    }
                )
            if not sentence_ids:
                continue
            paragraphs.append(
                {
                    "paragraph_id": paragraph_id,
                    "source_file": source_file,
                    "source_line": _line_number(text, paragraph_start),
                    "source_column": _column_number(text, paragraph_start),
                    "source_end_line": _line_number(text, paragraph_end - 1),
                    "source_end_column": _column_number(text, paragraph_end - 1),
                    "section_path": _section_path_at(headings, paragraph_start),
                    "source_text": text[paragraph_start:paragraph_end],
                    "rendered_text": _render_tex_prose(
                        text[paragraph_start:paragraph_end]
                    ),
                    "source_text_sha256": hashlib.sha256(
                        text[paragraph_start:paragraph_end].encode("utf-8")
                    ).hexdigest(),
                    "sentence_ids": sentence_ids,
                }
            )
    return paragraphs, sentences, exclusions, errors


def _prose_work_text(
    source_file: str,
    text: str,
) -> tuple[str, list[dict[str, Any]], list[str]]:
    characters = list(text)
    exclusions: list[dict[str, Any]] = []
    errors: list[str] = []
    if source_file == "main.tex":
        begin = re.search(r"\\begin\{abstract\}", text)
        end = re.search(r"\\end\{abstract\}", text)
        if begin is None or end is None or begin.end() > end.start():
            errors.append("main_abstract_range_missing")
        else:
            _mask_range(characters, 0, begin.end())
            _mask_range(characters, end.start(), len(characters))
            exclusions.extend(
                [
                    _excluded_range_record(
                        source_file,
                        text,
                        0,
                        begin.end(),
                        "front_matter_before_abstract",
                    ),
                    _excluded_range_record(
                        source_file,
                        text,
                        end.start(),
                        len(text),
                        "document_body_after_abstract_loaded_via_inputs",
                    ),
                ]
            )
    for environment in sorted(_EXCLUDED_ENVIRONMENTS):
        pattern = re.compile(
            rf"\\begin\{{{re.escape(environment)}\}}.*?"
            rf"\\end\{{{re.escape(environment)}\}}",
            re.DOTALL,
        )
        for match in pattern.finditer(text):
            _mask_range(characters, match.start(), match.end())
            exclusions.append(
                _excluded_range_record(
                    source_file,
                    text,
                    match.start(),
                    match.end(),
                    f"separate_{environment}_inventory_surface",
                )
            )
        begin_count = len(
            re.findall(rf"\\begin\{{{re.escape(environment)}\}}", text)
        )
        end_count = len(re.findall(rf"\\end\{{{re.escape(environment)}\}}", text))
        if begin_count != end_count:
            errors.append(
                f"unbalanced_environment:{source_file}:{environment}:"
                f"{begin_count}:{end_count}"
            )
    command_pattern = re.compile(r"\\([A-Za-z@]+)\*?")
    for match in command_pattern.finditer(text):
        command = match.group(1)
        if command not in _WHOLE_COMMANDS | _INLINE_MASK_COMMANDS:
            continue
        end = _command_end(text, match.start())
        if command in _WHOLE_COMMANDS:
            line_start = text.rfind("\n", 0, match.start()) + 1
            line_end = text.find("\n", end)
            if line_end < 0:
                line_end = len(text)
            before = text[line_start : match.start()].strip()
            after = text[end:line_end].strip()
            start = line_start if not before and not after else match.start()
            finish = line_end if not before and not after else end
        else:
            start = match.start()
            finish = end
        _mask_range(characters, start, finish)
        if command == "footnote":
            exclusions.append(
                _excluded_range_record(
                    source_file,
                    text,
                    start,
                    finish,
                    "separate_semantic_footnote_inventory_surface",
                )
            )
    transparent_names = "|".join(
        re.escape(name) for name in sorted(_TRANSPARENT_ENVIRONMENTS)
    )
    for match in re.finditer(
        rf"\\(?:begin|end)\{{(?:{transparent_names})\}}",
        text,
    ):
        _mask_range(characters, match.start(), match.end())
    standalone_names = "|".join(
        re.escape(name) for name in sorted(_STANDALONE_COMMANDS)
    )
    for match in re.finditer(rf"\\(?:{standalone_names})\b", text):
        _mask_range(characters, match.start(), match.end())
    return "".join(characters), exclusions, errors


def _sentence_boundary_text(work: str) -> str:
    characters = list(work)
    for start, end in _math_ranges(work):
        terminal_punctuation: int | None = None
        for offset in range(end - 1, start - 1, -1):
            if work[offset] in ".?!":
                terminal_punctuation = offset
                break
            if (
                not work[offset].isspace()
                and work[offset] not in "$\\[](){}"
            ):
                break
        _mask_range(characters, start, end)
        characters[start] = "M"
        if terminal_punctuation is not None:
            characters[terminal_punctuation] = work[terminal_punctuation]
    for match in _CITATION_COMMAND_PATTERN.finditer(work):
        _mask_range(characters, match.start(), _command_end(work, match.start()))
    return "".join(characters)


def _paragraph_ranges(text: str, work: str) -> list[tuple[int, int]]:
    boundaries = {0, len(work)}
    for match in re.finditer(r"\n[ \t\r]*\n+", work):
        boundaries.update((match.start() + 1, match.end()))
    for match in re.finditer(r"(?m)^[ \t]*\\item\b", text):
        boundaries.add(match.start())
    result: list[tuple[int, int]] = []
    points = sorted(boundaries)
    for start, end in zip(points, points[1:]):
        while start < end and work[start].isspace():
            start += 1
        while end > start and work[end - 1].isspace():
            end -= 1
        if start < end and re.search(r"[A-Za-z]", work[start:end]):
            result.append((start, end))
    return result


def _sentence_ranges(
    boundary_text: str,
    paragraph_start: int,
    paragraph_end: int,
) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = []
    sentence_start = paragraph_start
    offset = paragraph_start
    while offset < paragraph_end:
        if boundary_text[offset] not in ".?!":
            offset += 1
            continue
        if (
            boundary_text[offset] == "."
            and offset > paragraph_start
            and offset + 1 < paragraph_end
            and boundary_text[offset - 1].isdigit()
            and boundary_text[offset + 1].isdigit()
        ):
            offset += 1
            continue
        left_context = boundary_text[max(sentence_start, offset - 12) : offset + 1]
        if any(
            left_context.casefold().endswith(abbreviation)
            for abbreviation in _ABBREVIATIONS
        ):
            offset += 1
            continue
        sentence_end = offset + 1
        while (
            sentence_end < paragraph_end
            and boundary_text[sentence_end] in "}])\"'"
        ):
            sentence_end += 1
        next_offset = sentence_end
        while (
            next_offset < paragraph_end
            and boundary_text[next_offset].isspace()
        ):
            next_offset += 1
        terminal = (
            next_offset >= paragraph_end
            or boundary_text[next_offset].isupper()
            or boundary_text[next_offset] in "\\("
        )
        if terminal:
            start = sentence_start
            while start < sentence_end and boundary_text[start].isspace():
                start += 1
            if start < sentence_end and re.search(
                r"[A-Za-z]", boundary_text[start:sentence_end]
            ):
                result.append((start, sentence_end))
            sentence_start = sentence_end
        offset = sentence_end
    while (
        sentence_start < paragraph_end
        and boundary_text[sentence_start].isspace()
    ):
        sentence_start += 1
    if sentence_start < paragraph_end and re.search(
        r"[A-Za-z]", boundary_text[sentence_start:paragraph_end]
    ):
        result.append((sentence_start, paragraph_end))
    return result


def _math_ranges(text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    masked = list(text)
    for pattern in (
        re.compile(r"\$\$(.*?)\$\$", re.DOTALL),
        re.compile(r"\\\[(.*?)\\\]", re.DOTALL),
        re.compile(r"\\\((.*?)\\\)", re.DOTALL),
    ):
        for match in pattern.finditer("".join(masked)):
            ranges.append((match.start(), match.end()))
            _mask_range(masked, match.start(), match.end())
    work = "".join(masked)
    dollar_offsets = [
        offset
        for offset, character in enumerate(work)
        if character == "$" and not _is_escaped(work, offset)
    ]
    ranges.extend(
        (start, end + 1)
        for start, end in zip(dollar_offsets[::2], dollar_offsets[1::2])
    )
    return sorted(ranges)


def _render_tex_prose(source_text: str) -> str:
    value = re.sub(
        r"\\(?:cite|citealp|citep|citet|authoryearcite|authoryearcitet|"
        r"Cref|cref|ref)\w*(?:\[[^\]]*\])?\{[^{}]*\}",
        " [citation] ",
        source_text,
    )
    value = value.replace("\\methodFull", "AlphaEvolve")
    value = value.replace("\\method", "AlphaEvolve")
    for _ in range(3):
        value = re.sub(
            r"\\(?:emph|hbox|textbf|textit|textrm|texttt)\*?\{([^{}]*)\}",
            r"\1",
            value,
        )
    value = value.replace("\\times", " times ")
    value = value.replace("\\sim", " approximately ")
    value = value.replace("\\%", " percent ")
    value = re.sub(r"\\[A-Za-z@]+\*?(?:\[[^\]]*\])?", " ", value)
    value = value.translate(
        str.maketrans({"{": " ", "}": " ", "$": " ", "~": " ", "\\": " "})
    )
    return " ".join(value.split())


def _disposition_records(
    parsed: list[dict[str, Any]],
    claim_catalog: dict[tuple[str, str], dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    for parsed_record in parsed:
        key = (
            parsed_record["source_file"],
            parsed_record["source_line"],
            parsed_record["line_ordinal"],
        )
        targets = _DIRECT_CLAIM_MAP.get(key)
        match_kind = "manual_source_line_mapping"
        if targets is None:
            targets = _automatic_claim_targets(parsed_record, claim_catalog)
            match_kind = "normalized_anchor_mapping"
        claim_refs = [
            {
                "inventory_path": path,
                "claim_id": claim_id,
                "resolved": (path, claim_id) in claim_catalog,
                "match_kind": match_kind,
            }
            for path, claim_id in targets
        ]
        nonclaim = _NONCLAIM_DISPOSITIONS.get(key)
        if claim_refs:
            disposition = "existing_bounded_claim_mapping"
            nonclaim_record = None
        elif nonclaim is not None:
            disposition = "reviewed_nonclaim"
            nonclaim_record = {"category": nonclaim[0], "rationale": nonclaim[1]}
        else:
            disposition = "unmapped"
            nonclaim_record = None
            errors.append(
                f"unmapped_prose_sentence:{key[0]}:{key[1]}:{key[2]}"
            )
        record = dict(parsed_record)
        record.pop("_file_index")
        record.pop("_start")
        record.pop("_end")
        record.update(
            {
                "disposition": disposition,
                "claim_refs": claim_refs,
                "nonclaim_disposition": nonclaim_record,
            }
        )
        records.append(record)
    return records, errors


def _automatic_claim_targets(
    sentence: dict[str, Any],
    claim_catalog: dict[tuple[str, str], dict[str, Any]],
) -> tuple[tuple[str, str], ...]:
    inventory_names = _FILE_CLAIM_INVENTORIES.get(sentence["source_file"], ())
    inventory_paths = {
        _CLAIM_INVENTORY_PATHS[name] for name in inventory_names
    }
    sentence_tokens = _semantic_tokens(sentence["rendered_text"])
    targets: list[tuple[str, str]] = []
    for key, metadata in claim_catalog.items():
        if key[0] not in inventory_paths:
            continue
        anchor = metadata.get("source_anchor")
        if not isinstance(anchor, str):
            continue
        anchor_tokens = _semantic_tokens(anchor)
        if len(anchor_tokens) < 3:
            continue
        if _contains_token_sequence(sentence_tokens, anchor_tokens):
            targets.append(key)
    return tuple(sorted(set(targets)))


def _semantic_tokens(value: str) -> tuple[str, ...]:
    normalized = unicodedata.normalize("NFKD", value)
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    return tuple(re.findall(r"[a-z0-9]+", ascii_value.casefold()))


def _contains_token_sequence(
    values: tuple[str, ...],
    target: tuple[str, ...],
) -> bool:
    if len(target) > len(values):
        return False
    return any(
        values[offset : offset + len(target)] == target
        for offset in range(len(values) - len(target) + 1)
    )


def _paragraph_records(
    paragraphs: list[dict[str, Any]],
    sentences: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sentence_by_id = {record["sentence_id"]: record for record in sentences}
    result: list[dict[str, Any]] = []
    for paragraph in paragraphs:
        sentence_records = [
            sentence_by_id[sentence_id]
            for sentence_id in paragraph["sentence_ids"]
        ]
        record = dict(paragraph)
        record["sentence_count"] = len(sentence_records)
        record["all_sentences_dispositioned"] = all(
            sentence["disposition"] != "unmapped"
            for sentence in sentence_records
        )
        result.append(record)
    return result


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


def _excluded_range_record(
    source_file: str,
    text: str,
    start: int,
    end: int,
    reason: str,
) -> dict[str, Any]:
    return {
        "source_file": source_file,
        "source_line": _line_number(text, start),
        "source_end_line": _line_number(text, max(start, end - 1)),
        "reason": reason,
        "source_text_sha256": hashlib.sha256(
            text[start:end].encode("utf-8")
        ).hexdigest(),
    }


def _command_end(text: str, start: int) -> int:
    match = re.match(r"\\[A-Za-z@]+\*?", text[start:])
    if match is None:
        return min(len(text), start + 1)
    position = start + match.end()
    position = _skip_horizontal_whitespace(text, position)
    while position < len(text) and text[position] == "[":
        position = _group_end(text, position, "[", "]")
        position = _skip_horizontal_whitespace(text, position)
    while position < len(text) and text[position] == "{":
        position = _group_end(text, position, "{", "}")
        position = _skip_horizontal_whitespace(text, position)
    return position


def _group_end(
    text: str,
    start: int,
    opening: str,
    closing: str,
) -> int:
    if start >= len(text) or text[start] != opening:
        return start
    depth = 1
    offset = start + 1
    while offset < len(text):
        if text[offset] == opening and not _is_escaped(text, offset):
            depth += 1
        elif text[offset] == closing and not _is_escaped(text, offset):
            depth -= 1
            if depth == 0:
                return offset + 1
        offset += 1
    return len(text)


def _skip_horizontal_whitespace(text: str, position: int) -> int:
    while position < len(text) and text[position] in " \t":
        position += 1
    return position


def _mask_range(characters: list[str], start: int, end: int) -> None:
    for offset in range(max(0, start), min(len(characters), end)):
        if characters[offset] not in "\r\n":
            characters[offset] = " "


def _is_escaped(text: str, offset: int) -> bool:
    slash_count = 0
    cursor = offset - 1
    while cursor >= 0 and text[cursor] == "\\":
        slash_count += 1
        cursor -= 1
    return bool(slash_count % 2)


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


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[
    dict[str, Any] | None,
    list[AlphaEvolveTexProseInventoryBoundaryIssue],
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
            return None, [
                _issue("unreadable_boundary", f"boundary could not be loaded: {exc}")
            ]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "TeX prose inventory must be an object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveTexProseInventoryBoundaryIssue:
    return AlphaEvolveTexProseInventoryBoundaryIssue(code, message)
