from __future__ import annotations

import json
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from libreevolve.problems.benchmarks.alphaevolve_source_inventory_boundary import (
    EXPECTED_NAMED_SOURCE_SPAN_IDS,
    SOURCE_PAPER_ID,
    SOURCE_PDF_PATH,
    alphaevolve_source_inventory_boundary_record,
)
from libreevolve.problems.benchmarks.appendix_a_matrix_registry import (
    BASELINE_REFERENCE_IDS_BY_TARGET_ID,
    matrix_target_records,
)


ALPHAEVOLVE_APPENDIX_A_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_appendix_a_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "appendix_a_table_3_figure_9_claim_inventory_complete_without_result_"
    "reproduction"
)
EXPECTED_CLAIM_COUNT = 131
IMPLEMENTED_STATUS = "implemented_local"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)


_TODO_SPECS = {
    "baseline": (
        "docs/todo/code.md",
        "Record matrix baseline-component provenance for Section 3.1 starts.",
    ),
    "baseline_citations": (
        "docs/todo/code.md",
        "Wire Appendix A best-known-rank citation provenance into reports.",
    ),
    "curation": (
        "docs/todo/code.md",
        "Add Appendix A matrix target-suite curation provenance.",
    ),
    "figure9": (
        "docs/todo/code.md",
        "Add Appendix A Figure 9a-9c magnified matrix-diff exhibit provenance.",
    ),
    "near_integrality": (
        "docs/todo/code.md",
        "Add a matrix coefficient-domain prompt/evaluator contract for",
    ),
    "resource_frontier": (
        "docs/todo/code.md",
        "Add matrix scaling resource-frontier evidence for larger target claims.",
    ),
    "row_note": (
        "docs/todo/code.md",
        "Add Appendix A matrix row-note and concurrent-work provenance.",
    ),
    "scalar_field": (
        "docs/todo/code.md",
        "Add matrix scalar-field provenance for real, complex, and characteristic",
    ),
    "subset_scope": (
        "docs/todo/code.md",
        "Add matrix result subset-scope validation for main-text versus",
    ),
    "suite": (
        "docs/todo/code.md",
        "Generate suite matrix tensor artifacts and per-seed hit-rate reports.",
    ),
    "sweep": (
        "docs/todo/code.md",
        "Add matrix hyperparameter-sweep provenance for evolved search programs.",
    ),
    "table_export": (
        "docs/todo/code.md",
        "Wire Table 2/Table 3 matrix-rank table artifacts into report/export.",
    ),
}


def _claim(
    claim_id: str,
    source_span_id: str,
    source_page: int,
    source_anchor: str,
    claim: str,
    category: str,
    implementation_status: str,
    evidence_paths: tuple[str, ...],
    todo_ids: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "source_span_id": source_span_id,
        "source_page": source_page,
        "source_anchor": source_anchor,
        "claim": claim,
        "category": category,
        "implementation_status": implementation_status,
        "roadmap_section_id": "representative_benchmarks",
        "roadmap_phase": "longer_term",
        "evidence_paths": evidence_paths,
        "todo_ids": todo_ids,
    }


def _appendix_claim(
    claim_id: str,
    source_anchor: str,
    claim: str,
    category: str,
    implementation_status: str,
    evidence_paths: tuple[str, ...],
    todo_ids: tuple[str, ...],
) -> dict[str, Any]:
    return _claim(
        claim_id,
        "appendix_a",
        34,
        source_anchor,
        claim,
        category,
        implementation_status,
        evidence_paths,
        todo_ids,
    )


def _figure_claim(
    claim_id: str,
    source_page: int,
    source_anchor: str,
    claim: str,
    category: str,
    todo_ids: tuple[str, ...] = ("figure9",),
    implementation_status: str = "not_demonstrated",
    evidence_paths: tuple[str, ...] = (
        "papers/figure9_matrix_diff_artifacts.json",
    ),
) -> dict[str, Any]:
    return _claim(
        claim_id,
        "figure_9",
        source_page,
        source_anchor,
        claim,
        category,
        implementation_status,
        evidence_paths,
        todo_ids,
    )


_APPENDIX_PROSE_CLAIMS = (
    _appendix_claim(
        "appendix_a_best_ranks_in_table3",
        "We provide the best ranks obtained by AlphaEvolve in Table 3",
        "Appendix A provides AlphaEvolve's best matrix ranks in Table 3.",
        "table_3_structure",
        "partially_implemented",
        ("papers/matrix_rank_table_artifacts.json",),
        ("table_export", "baseline_citations"),
    ),
    _appendix_claim(
        "appendix_a_54_sizes_considered",
        "we considered 54 matrix multiplication sizes",
        "The AlphaEvolve experiments considered 54 matrix-multiplication sizes.",
        "target_suite_curation",
        "partially_implemented",
        ("papers/appendix_a_matrix_curation.json",),
        ("curation", "suite"),
    ),
    _appendix_claim(
        "appendix_a_rough_m_n_range",
        "2 <= m,n <= 5",
        "The sizes were chosen roughly with 2 <= m,n <= 5.",
        "target_suite_curation",
        "partially_implemented",
        ("papers/appendix_a_matrix_curation.json",),
        ("curation",),
    ),
    _appendix_claim(
        "appendix_a_reasonable_p_cutoff",
        "with some reasonable cutoff for p",
        "The source uses a reasonable but numerically unspecified cutoff for p.",
        "target_suite_curation",
        "partially_implemented",
        ("papers/appendix_a_matrix_curation.json",),
        ("curation",),
    ),
    _appendix_claim(
        "appendix_a_axis_permutation_symmetry",
        "equivalent algorithms for any permutations of the three axes",
        "Matrix-tensor symmetry makes axis permutations algorithmically equivalent.",
        "target_suite_curation",
        "partially_implemented",
        ("papers/appendix_a_matrix_curation.json",),
        ("curation",),
    ),
    _appendix_claim(
        "appendix_a_sorted_dimensions",
        "we focus on sorted sizes m <= n <= p",
        "The reported suite uses canonical sorted dimensions m <= n <= p.",
        "target_suite_curation",
        "partially_implemented",
        ("papers/appendix_a_matrix_curation.json",),
        ("curation",),
    ),
    _appendix_claim(
        "appendix_a_all_but_two_match_or_surpass",
        "In all but two considered sizes",
        "AlphaEvolve matched or surpassed the best-known rank for all but two sizes.",
        "aggregate_result",
        "not_demonstrated",
        ("papers/matrix_suite_publication_artifacts.json",),
        ("suite", "table_export"),
    ),
    _appendix_claim(
        "appendix_a_increasing_size_difficulty",
        "difficulty when increasing the problem size",
        "The AlphaEvolve authors encountered difficulty as matrix size increased.",
        "resource_frontier",
        "not_demonstrated",
        ("papers/appendix_a_matrix_local_resource_frontier.json",),
        ("resource_frontier",),
    ),
    _appendix_claim(
        "appendix_a_beyond_5x5x5_attempts",
        "sizes beyond 5, 5, 5",
        "The reported resource-frontier experiments ran discovered programs beyond <5,5,5>.",
        "resource_frontier",
        "not_demonstrated",
        ("papers/appendix_a_matrix_local_resource_frontier.json",),
        ("resource_frontier",),
    ),
    _appendix_claim(
        "appendix_a_1000_random_seeds",
        "on 1000 random seeds",
        "The larger-size resource experiments used 1000 random seeds.",
        "resource_frontier",
        "not_demonstrated",
        ("papers/appendix_a_matrix_local_resource_frontier.json",),
        ("resource_frontier",),
    ),
    _appendix_claim(
        "appendix_a_single_gpu_evaluators",
        "evaluators with a single GPU accelerator",
        "The larger-size evaluators used one GPU accelerator.",
        "resource_frontier",
        "not_demonstrated",
        ("papers/appendix_a_matrix_local_resource_frontier.json",),
        ("resource_frontier",),
    ),
    _appendix_claim(
        "appendix_a_frequent_oom",
        "we often run out of memory",
        "The larger-size experiments frequently ran out of memory.",
        "resource_frontier",
        "not_demonstrated",
        ("papers/appendix_a_matrix_local_resource_frontier.json",),
        ("resource_frontier",),
    ),
    _appendix_claim(
        "appendix_a_larger_sizes_need_optimization",
        "requires further optimization",
        "Extending the setup to larger matrix sizes requires further optimization.",
        "resource_frontier",
        "not_demonstrated",
        ("papers/appendix_a_matrix_local_resource_frontier.json",),
        ("resource_frontier",),
    ),
    _appendix_claim(
        "table3_full_table2_all_parameters",
        "Full version of Table 2",
        "Table 3 is the full Table 2 result set for all considered parameters.",
        "table_3_structure",
        "partially_implemented",
        ("papers/matrix_rank_table_artifacts.json",),
        ("table_export", "subset_scope"),
    ),
    _appendix_claim(
        "table3_38_matches",
        "matches the state of the art in 38 cases",
        "Table 3 reports 38 matched targets.",
        "aggregate_result",
        "not_demonstrated",
        ("papers/matrix_suite_publication_artifacts.json",),
        ("suite", "table_export"),
    ),
    _appendix_claim(
        "table3_14_surpasses",
        "surpasses it in 14 cases",
        "Table 3 reports 14 surpassed targets.",
        "aggregate_result",
        "not_demonstrated",
        ("papers/matrix_suite_publication_artifacts.json",),
        ("suite", "table_export"),
    ),
    _appendix_claim(
        "table3_surpass_green_encoding",
        "14 cases (green)",
        "Table 3 encodes surpassed targets in green.",
        "table_3_structure",
        "partially_implemented",
        ("papers/matrix_rank_table_artifacts.json",),
        ("table_export",),
    ),
    _appendix_claim(
        "table3_two_fall_behind",
        "falls behind in 2 cases",
        "Table 3 reports two targets where AlphaEvolve fell behind.",
        "aggregate_result",
        "not_demonstrated",
        ("papers/matrix_suite_publication_artifacts.json",),
        ("suite", "table_export"),
    ),
    _appendix_claim(
        "table3_fall_behind_red_encoding",
        "2 cases (red)",
        "Table 3 encodes fell-behind targets in red.",
        "table_3_structure",
        "partially_implemented",
        ("papers/matrix_rank_table_artifacts.json",),
        ("table_export",),
    ),
    _appendix_claim(
        "table3_all_exact_algorithms",
        "In all cases, AlphaEvolve provides exact algorithms",
        "Every Table 3 result is reported as an exact algorithm.",
        "exactness_result",
        "not_demonstrated",
        ("papers/matrix_suite_publication_artifacts.json",),
        ("suite", "near_integrality"),
    ),
    _appendix_claim(
        "table3_integer_or_half_integer_entries",
        "using integer or half-integer entries",
        "Every reported decomposition uses integer or half-integer entries.",
        "exactness_result",
        "not_demonstrated",
        ("papers/matrix_near_integrality_runtime_boundary.json",),
        ("suite", "near_integrality"),
    ),
    _appendix_claim(
        "table3_three_complex_targets",
        "For 3, 4, 7, 4, 4, 4, and 4, 4, 8",
        "The 3x4x7, 4x4x4, and 4x4x8 results use complex-valued multiplications.",
        "scalar_field_result",
        "not_demonstrated",
        ("papers/matrix_scalar_field_runtime_boundary.json",),
        ("suite", "scalar_field"),
    ),
    _appendix_claim(
        "table3_complex_matrix_applicability",
        "exact multiplication of complex",
        "The three complex-valued algorithms apply to exact complex matrix multiplication.",
        "scalar_field_result",
        "not_demonstrated",
        ("papers/matrix_scalar_field_runtime_boundary.json",),
        ("suite", "scalar_field"),
    ),
    _appendix_claim(
        "table3_real_matrix_applicability",
        "or real-valued matrices",
        "The three complex-valued algorithms also apply to exact real matrix multiplication.",
        "scalar_field_result",
        "not_demonstrated",
        ("papers/matrix_scalar_field_runtime_boundary.json",),
        ("suite", "scalar_field"),
    ),
    _appendix_claim(
        "table3_decompositions_in_colab",
        "found in the accompanying Google Colab",
        "The Table 3 decompositions are available in an accompanying Google Colab.",
        "publication_artifact_result",
        "not_demonstrated",
        ("papers/matrix_suite_publication_artifacts.json",),
        ("suite", "table_export"),
    ),
    _appendix_claim(
        "table3_concurrent_rank90_4x5x6",
        "Concurrent work [49] has also found a rank-90 algorithm",
        "Concurrent work cited as reference 49 also reports rank 90 for 4x5x6.",
        "concurrent_work_result",
        "not_demonstrated",
        ("papers/appendix_a_matrix_row_note_artifacts.json",),
        ("row_note",),
    ),
    _appendix_claim(
        "appendix_a_figure9_magnifies_figure4_left",
        "Figures 9a to 9c, we show a magnified version of Figure 4 (left)",
        "Figures 9a through 9c magnify the left side of Figure 4.",
        "figure_9_structure",
        "partially_implemented",
        ("papers/figure9_matrix_diff_artifacts.json",),
        ("figure9",),
    ),
    _appendix_claim(
        "appendix_a_figure9_rank48_decomposition",
        "discovers a decomposition of rank 48",
        "The Figure 9 program discovers a rank-48 decomposition.",
        "figure_9_result",
        "not_demonstrated",
        ("papers/figure9_matrix_diff_artifacts.json",),
        ("figure9", "suite"),
    ),
    _appendix_claim(
        "appendix_a_figure9_4x4_tensor_target",
        "multiplying two 4 4 matrices",
        "The Figure 9 rank-48 tensor represents multiplication of two 4x4 matrices.",
        "figure_9_result",
        "not_demonstrated",
        ("papers/figure9_matrix_diff_artifacts.json",),
        ("figure9", "suite", "scalar_field"),
    ),
)


_FIGURE9_CLAIMS = (
    _figure_claim(
        "figure9a_caption_part_1_of_3",
        35,
        "faster algorithm to multiply 4 4 matrices (1/3)",
        "Figure 9a is part 1 of 3 of the faster 4x4 matrix program.",
        "figure_9_caption",
        implementation_status="partially_implemented",
    ),
    _figure_claim(
        "figure9b_caption_part_2_of_3",
        36,
        "faster algorithm to multiply 4 4 matrices (2/3)",
        "Figure 9b is part 2 of 3 of the faster 4x4 matrix program.",
        "figure_9_caption",
        implementation_status="partially_implemented",
    ),
    _figure_claim(
        "figure9c_caption_part_3_of_3",
        37,
        "faster algorithm to multiply 4 4 matrices (3/3)",
        "Figure 9c is part 3 of 3 of the faster 4x4 matrix program.",
        "figure_9_caption",
        implementation_status="partially_implemented",
    ),
    _figure_claim(
        "figure9_adam_to_adamw",
        35,
        "return optax.adamw",
        "The evolved optimizer changes Adam to AdamW.",
        "figure_9_optimizer",
        ("figure9", "baseline"),
    ),
    _figure_claim(
        "figure9_adamw_weight_decay",
        35,
        "weight_decay = self.hypers.weight_decay",
        "AdamW receives a configurable weight-decay value.",
        "figure_9_optimizer",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_initialization_scale_factor",
        35,
        "scale * 0.2",
        "The evolved initializer scales the configured initialization scale by 0.2.",
        "figure_9_initialization",
        ("figure9", "baseline"),
    ),
    _figure_claim(
        "figure9_complex64_normal_initialization",
        35,
        "normal (0 + 1j * 0, scale * 0.2, jnp.complex64)",
        "The evolved initializer uses a complex64 normal distribution centered at zero.",
        "figure_9_initialization",
        ("figure9", "baseline", "scalar_field"),
    ),
    _figure_claim(
        "figure9_gradient_noise",
        35,
        "grad_noise_std * jax.random.normal",
        "The update adds configurable Gaussian gradient noise.",
        "figure_9_noise",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_decomposition_noise",
        35,
        "noise_std * jax.random.normal",
        "The update adds Gaussian noise directly to decomposition parameters.",
        "figure_9_noise",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_decomposition_noise_linear_decay",
        35,
        "start = self.hypers.noise_std, end = 0.0",
        "Decomposition noise is linearly scheduled from noise_std to zero.",
        "figure_9_noise",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_clip_cycle_2000_steps",
        35,
        "cycle_length = 2000",
        "The clipping schedule uses a 2000-step cycle.",
        "figure_9_clipping",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_cosine_clip_threshold",
        35,
        "clip_threshold_multiplier = (1 + jnp.cos",
        "A cosine multiplier cycles the clipping threshold between clip_min and clip_max.",
        "figure_9_clipping",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_soft_clip_real_component",
        35,
        "x_re_clipped = jnp.where",
        "Soft clipping is applied to the real component.",
        "figure_9_clipping",
    ),
    _figure_claim(
        "figure9_soft_clip_imaginary_component",
        36,
        "x_im_clipped = jnp.where",
        "Soft clipping is applied separately to the imaginary component.",
        "figure_9_clipping",
    ),
    _figure_claim(
        "figure9_soft_clip_excess_slope",
        35,
        "(x_re - threshold) * 0.1",
        "Values beyond the clipping threshold retain a 0.1 excess slope.",
        "figure_9_clipping",
    ),
    _figure_claim(
        "figure9_target_tensor_noise",
        36,
        "target_noise_std * jax.random.normal",
        "The loss adds configurable Gaussian noise to the target tensor.",
        "figure_9_noise",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_hallucination_probability",
        36,
        "bernoulli (hallucination_rng, p = hallucination_prob)",
        "Hallucination masks are sampled with a configurable Bernoulli probability.",
        "figure_9_loss",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_hallucination_replacement_scale",
        36,
        "hallucination_scale * jax.random.normal",
        "Hallucinated values are Gaussian replacements with configurable scale.",
        "figure_9_loss",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_hallucination_applied_to_factors",
        36,
        "lambda x : hallucinate",
        "Hallucination is mapped across decomposition factors.",
        "figure_9_loss",
    ),
    _figure_claim(
        "figure9_reconstruction_uses_noisy_target",
        36,
        "l2_loss_complex (noisy_target_tensor",
        "Reconstruction loss is evaluated against the noisy target tensor.",
        "figure_9_loss",
    ),
    _figure_claim(
        "figure9_real_half_integer_distance",
        36,
        "abs (x_re - jnp.round (x_re * 2) / 2)",
        "The discretization loss measures real-component distance to half-integers.",
        "figure_9_discretization",
        ("figure9", "near_integrality"),
    ),
    _figure_claim(
        "figure9_imaginary_half_integer_distance",
        36,
        "abs (x_im - jnp.round (x_im * 2) / 2)",
        "The discretization loss measures imaginary-component distance to half-integers.",
        "figure_9_discretization",
        ("figure9", "near_integrality"),
    ),
    _figure_claim(
        "figure9_min_real_imag_half_integer_distance",
        36,
        "return jnp.minimum",
        "The shown half-integer term takes the minimum of real and imaginary distances.",
        "figure_9_discretization",
        ("figure9", "near_integrality"),
    ),
    _figure_claim(
        "figure9_integer_distance",
        37,
        "abs (x - jnp.round (x))",
        "The discretization loss also measures distance to integers.",
        "figure_9_discretization",
        ("figure9", "near_integrality"),
    ),
    _figure_claim(
        "figure9_combined_half_integer_and_integer_loss",
        37,
        "mean (dist_to_half_ints (factor))",
        "Each factor contributes both half-integer and integer distance terms.",
        "figure_9_discretization",
        ("figure9", "near_integrality"),
    ),
    _figure_claim(
        "figure9_discretization_factor_average",
        37,
        "len (decomposition) * 2",
        "The discretization loss is averaged over factors and its two terms.",
        "figure_9_discretization",
        ("figure9", "near_integrality"),
    ),
    _figure_claim(
        "figure9_discretization_weight_linear_schedule",
        37,
        "start = 0.0, end = self.hypers.discretization_weight",
        "Discretization weight is linearly scheduled from zero to its configured value.",
        "figure_9_discretization",
        ("figure9", "near_integrality", "sweep"),
    ),
    _figure_claim(
        "figure9_half_integer_cycle_length",
        37,
        "training_steps // 4",
        "The half-integer cosine schedule uses one quarter of training steps per cycle.",
        "figure_9_discretization",
        ("figure9", "near_integrality"),
    ),
    _figure_claim(
        "figure9_half_integer_cosine_multiplier",
        37,
        "half_int_multiplier = (1 + jnp.cos",
        "A cosine multiplier anneals the half-integer loss.",
        "figure_9_discretization",
        ("figure9", "near_integrality"),
    ),
    _figure_claim(
        "figure9_half_integer_start_floor",
        37,
        "1 - self.hypers.half_int_start",
        "half_int_start controls the floor of the half-integer multiplier.",
        "figure_9_discretization",
        ("figure9", "near_integrality", "sweep"),
    ),
    _figure_claim(
        "figure9_total_loss_adds_discretization",
        37,
        "discretization_weight * discretization_loss",
        "Total loss adds weighted, scheduled discretization to reconstruction loss.",
        "figure_9_loss",
        ("figure9", "near_integrality"),
    ),
    _figure_claim(
        "figure9_quadratic_large_value_penalty",
        37,
        "mean (jnp.abs (factor) ** 2)",
        "A quadratic factor-magnitude term penalizes large decomposition values.",
        "figure_9_loss",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_large_value_penalty_weight",
        37,
        "large_value_penalty_weight * large_value_penalty",
        "The large-value penalty has a configurable weight.",
        "figure_9_loss",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_real_total_loss",
        37,
        "return jnp.real (total_loss)",
        "The evolved loss returns the real component of total loss.",
        "figure_9_loss",
        ("figure9", "scalar_field"),
    ),
    _figure_claim(
        "figure9_sweep_init_scale_range",
        37,
        "init_scale', hyper.interval (0.1, 1.0)",
        "The sweep changes init_scale to the interval [0.1, 1.0].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_learning_rate_range",
        37,
        "learning_rate', hyper.interval (0.01, 0.2)",
        "The sweep changes learning_rate to the interval [0.01, 0.2].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_discretization_weight",
        37,
        "discretization_weight', hyper.interval (0.0, 0.1)",
        "The sweep adds discretization_weight in [0.0, 0.1].",
        "figure_9_sweep",
        ("figure9", "sweep", "near_integrality"),
    ),
    _figure_claim(
        "figure9_sweep_hallucination_probability",
        37,
        "hallucination_prob', hyper.interval (0.0, 0.2)",
        "The sweep adds hallucination_prob in [0.0, 0.2].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_hallucination_scale",
        37,
        "hallucination_scale', hyper.interval (0.0, 0.2)",
        "The sweep adds hallucination_scale in [0.0, 0.2].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_decomposition_noise",
        37,
        "noise_std', hyper.interval (0.0, 0.01)",
        "The sweep adds decomposition noise_std in [0.0, 0.01].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_target_noise",
        37,
        "target_noise_std', hyper.interval (0.0, 0.01)",
        "The sweep adds target_noise_std in [0.0, 0.01].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_weight_decay",
        37,
        "weight_decay', hyper.interval (0.00001, 0.001)",
        "The sweep adds weight_decay in [0.00001, 0.001].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_clip_min",
        37,
        "clip_min', hyper.interval (0.0, 0.5)",
        "The sweep adds clip_min in [0.0, 0.5].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_clip_max",
        37,
        "clip_max', hyper.interval (1.0, 3.0)",
        "The sweep adds clip_max in [1.0, 3.0].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_large_value_penalty",
        37,
        "large_value_penalty_weight', hyper.interval (0.0, 0.01)",
        "The sweep adds large_value_penalty_weight in [0.0, 0.01].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_gradient_noise",
        37,
        "grad_noise_std', hyper.interval (0.0, 0.001)",
        "The sweep adds grad_noise_std in [0.0, 0.001].",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
    _figure_claim(
        "figure9_sweep_half_integer_start",
        37,
        "half_int_start', hyper.interval (0.0, 1.0)",
        "The sweep adds half_int_start in [0.0, 1.0].",
        "figure_9_sweep",
        ("figure9", "sweep", "near_integrality"),
    ),
    _figure_claim(
        "figure9_hyper_user_provided_library",
        37,
        "hyper is a user-provided library",
        "The shown hyper library is user-provided and generates hyperparameter sweeps.",
        "figure_9_sweep",
        ("figure9", "sweep"),
    ),
)


def _table3_claim_specs() -> tuple[dict[str, Any], ...]:
    records = []
    for target in matrix_target_records():
        target_id = target["id"]
        dimensions = target["dimensions"]
        dimension_text = ",".join(str(value) for value in dimensions)
        references = BASELINE_REFERENCE_IDS_BY_TARGET_ID[target_id]
        reference_text = ", ".join(references)
        records.append(
            _claim(
                f"table3_{target_id}_rank_result",
                "table_3",
                34,
                (
                    f"<{dimension_text}> {target['best_known_rank']} "
                    f"[{reference_text}] {target['alphaevolve_rank']}"
                ),
                (
                    f"Table 3 reports {dimension_text} with best-known rank "
                    f"{target['best_known_rank']} from reference(s) "
                    f"{reference_text}, AlphaEvolve rank "
                    f"{target['alphaevolve_rank']}, and outcome "
                    f"{target['outcome']}."
                ),
                "table_3_row_result",
                "not_demonstrated",
                (
                    "libreevolve/problems/benchmarks/alphaevolve_appendix_a_matrix.json",
                    "papers/matrix_suite_publication_artifacts.json",
                    "papers/appendix_a_matrix_baseline_citations.json",
                ),
                ("suite", "table_export", "baseline_citations"),
            )
        )
    return tuple(records)


APPENDIX_A_CLAIM_SPECS = (
    *_APPENDIX_PROSE_CLAIMS,
    *_table3_claim_specs(),
    *_FIGURE9_CLAIMS,
)
EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in APPENDIX_A_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveAppendixAClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveAppendixAClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveAppendixAClaimInventoryBoundaryIssue]


def alphaevolve_appendix_a_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [_claim_record(root_path, spec, page_texts) for spec in APPENDIX_A_CLAIM_SPECS]
    status_counts = Counter(record["implementation_status"] for record in records)
    category_counts = Counter(record["category"] for record in records)
    missing_anchor_count = sum(not record["source_anchor_present"] for record in records)
    missing_reference_count = sum(
        not ref["exists"]
        or ("required_phrase_present" in ref and not ref["required_phrase_present"])
        for record in records
        for ref in (*record["evidence_refs"], *record["active_todo_refs"])
    )
    implementation_gap_count = sum(
        record["implementation_status"] != IMPLEMENTED_STATUS for record in records
    )
    todo_owned_gap_count = sum(
        record["implementation_status"] != IMPLEMENTED_STATUS
        and record["active_todo_refs"]
        and all(
            ref["exists"] and ref["required_phrase_present"]
            for ref in record["active_todo_refs"]
        )
        for record in records
    )
    source_artifact = source_inventory["source_artifact"]
    inventory_ready = (
        source_artifact["identity_ok"]
        and source_inventory["named_structure_inventory_ready"]
        and len(records) == EXPECTED_CLAIM_COUNT
        and missing_anchor_count == 0
        and missing_reference_count == 0
        and todo_owned_gap_count == implementation_gap_count
    )
    return {
        "schema": ALPHAEVOLVE_APPENDIX_A_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "appendix_a_claim_inventory_ready": inventory_ready,
        "alphaevolve_result_reproduction_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": ["appendix_a", "table_3", "figure_9"],
        "inventory_scope": {
            "included": [
                "all Appendix A prose and captions on PDF page 34",
                "all 54 Table 3 target rows with dimensions, baseline references, ranks, and outcomes",
                "all concrete optimizer, initialization, noise, clipping, loss, discretization, and sweep changes shown in Figure 9a through Figure 9c",
                "exact PDF-page anchors and active TODO ownership for every gap",
            ],
            "excluded": [
                "independent verification of best-known-rank citations or concurrent work",
                "local generation of the 54 decompositions, exactness certificates, or companion notebook",
                "stochastic rediscovery of the rank results or Figure 9 program",
                "Appendices B and later figures",
                "AlphaEvolve production scale or system parity",
            ],
        },
        "claim_count": len(records),
        "expected_claim_count": EXPECTED_CLAIM_COUNT,
        "category_counts": dict(sorted(category_counts.items())),
        "implementation_status_counts": dict(sorted(status_counts.items())),
        "implemented_local_count": status_counts[IMPLEMENTED_STATUS],
        "implementation_gap_count": implementation_gap_count,
        "todo_owned_gap_count": todo_owned_gap_count,
        "missing_anchor_count": missing_anchor_count,
        "missing_reference_count": missing_reference_count,
        "claim_records": records,
        "claim_boundary": (
            "This sidecar certifies a bounded claim-level inventory of 131 "
            "AlphaEvolve Appendix A, Table 3, and Figure 9 claims. It records "
            "29 prose/caption claims, all 54 result rows, and 48 panel-level "
            "program claims while separating partial metadata support from "
            "undemonstrated published behavior. It does not claim independent "
            "baseline verification, generated decomposition artifacts, exactness "
            "certificate reproduction, stochastic rediscovery, AlphaEvolve result "
            "reproduction, or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_appendix_a_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveAppendixAClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_appendix_a_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveAppendixAClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_appendix_a_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveAppendixAClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_APPENDIX_A_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Appendix A claim inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("alphaevolve_result_reproduction_claim_ready") is not False:
        issues.append(_issue("result_reproduction_overclaim", "Appendix A inventory must not claim result reproduction"))
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(_issue("parity_overclaim", "Appendix A inventory must not claim AlphaEvolve parity"))
    for key in (
        "source_artifact",
        "source_inventory_schema",
        "source_inventory_span_count",
        "source_span_ids",
        "inventory_scope",
        "claim_count",
        "expected_claim_count",
        "category_counts",
        "implementation_status_counts",
        "implemented_local_count",
        "implementation_gap_count",
        "todo_owned_gap_count",
        "missing_anchor_count",
        "missing_reference_count",
        "claim_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from the bounded Appendix A claim inventory"))
    if len(EXPECTED_CLAIM_IDS) != EXPECTED_CLAIM_COUNT:
        issues.append(_issue("invalid_spec_count", "Appendix A claim count must remain 131"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "Appendix A claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in APPENDIX_A_CLAIM_SPECS
            if spec["source_span_id"] not in EXPECTED_NAMED_SOURCE_SPAN_IDS
        }
    )
    if unknown_spans:
        issues.append(_issue("unknown_source_span", f"unknown source spans: {', '.join(unknown_spans)}"))
    unsupported_statuses = sorted(
        {
            spec["implementation_status"]
            for spec in APPENDIX_A_CLAIM_SPECS
            if spec["implementation_status"] not in INCOMPLETE_STATUSES | {IMPLEMENTED_STATUS}
        }
    )
    if unsupported_statuses:
        issues.append(_issue("unsupported_implementation_status", f"unsupported statuses: {', '.join(unsupported_statuses)}"))
    unowned_gaps = sorted(
        record["claim_id"]
        for record in expected["claim_records"]
        if record["implementation_status"] != IMPLEMENTED_STATUS
        and not record["active_todo_refs"]
    )
    if unowned_gaps:
        issues.append(_issue("unowned_implementation_gap", f"claims lack active TODO ownership: {', '.join(unowned_gaps)}"))
    if not expected["source_artifact"]["identity_ok"]:
        issues.append(_issue("source_pdf_identity_mismatch", "retained AlphaEvolve PDF identity does not match the pinned source"))
    if expected["missing_anchor_count"]:
        issues.append(_issue("missing_source_anchor", f"{expected['missing_anchor_count']} Appendix A claim anchors were not found"))
    if expected["missing_reference_count"]:
        issues.append(_issue("missing_local_reference", f"{expected['missing_reference_count']} evidence or TODO references are stale"))
    expected_ready = (
        expected["source_artifact"]["identity_ok"]
        and expected["claim_count"] == EXPECTED_CLAIM_COUNT
        and expected["missing_anchor_count"] == 0
        and expected["missing_reference_count"] == 0
        and expected["todo_owned_gap_count"] == expected["implementation_gap_count"]
    )
    if data.get("appendix_a_claim_inventory_ready") is not expected_ready:
        issues.append(_issue("invalid_appendix_a_claim_inventory_ready", "Appendix A readiness does not match source, reference, and TODO ownership checks"))
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "131" not in claim_boundary
        or "54 result rows" not in claim_boundary
        or "AlphaEvolve result reproduction" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded Appendix A coverage from reproduction and parity proof"))
    return AlphaEvolveAppendixAClaimInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        claim_count=data.get("claim_count") if isinstance(data.get("claim_count"), int) else 0,
        implemented_local_count=data.get("implemented_local_count") if isinstance(data.get("implemented_local_count"), int) else 0,
        implementation_gap_count=data.get("implementation_gap_count") if isinstance(data.get("implementation_gap_count"), int) else 0,
        missing_anchor_count=expected["missing_anchor_count"],
        missing_reference_count=expected["missing_reference_count"],
        issues=issues,
    )


def render_alphaevolve_appendix_a_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_appendix_a_claim_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve Appendix A claim inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| claim_count | {validation.claim_count} |",
        f"| implemented_local_count | {validation.implemented_local_count} |",
        f"| implementation_gap_count | {validation.implementation_gap_count} |",
        f"| missing_anchor_count | {validation.missing_anchor_count} |",
        f"| missing_reference_count | {validation.missing_reference_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _claim_record(
    root: Path,
    spec: dict[str, Any],
    page_texts: tuple[str, ...],
) -> dict[str, Any]:
    page_number = spec["source_page"]
    page_text = page_texts[page_number - 1] if page_number <= len(page_texts) else ""
    evidence_refs = [_evidence_ref(root, path) for path in spec["evidence_paths"]]
    active_todo_refs = []
    for todo_id in spec["todo_ids"]:
        path_label, phrase = _TODO_SPECS[todo_id]
        path = root / path_label
        text = _read_text(path)
        active_todo_refs.append(
            {
                "todo_id": todo_id,
                "path": path_label,
                "required_phrase": phrase,
                "exists": _safe_is_file(path),
                "required_phrase_present": phrase in text,
            }
        )
    return {
        "claim_id": spec["claim_id"],
        "source_span_id": spec["source_span_id"],
        "source_page": page_number,
        "source_anchor": spec["source_anchor"],
        "source_anchor_present": _canonical(spec["source_anchor"]) in _canonical(page_text),
        "claim": spec["claim"],
        "category": spec["category"],
        "implementation_status": spec["implementation_status"],
        "roadmap_section_id": spec["roadmap_section_id"],
        "roadmap_phase": spec["roadmap_phase"],
        "evidence_refs": evidence_refs,
        "active_todo_refs": active_todo_refs,
    }


def _evidence_ref(root: Path, path_label: str) -> dict[str, Any]:
    path = root / path_label
    record: dict[str, Any] = {"path": path_label, "exists": _safe_is_file(path)}
    if path.suffix.casefold() == ".json" and record["exists"]:
        payload = _read_json(path)
        if isinstance(payload, dict):
            for key in (
                "schema",
                "boundary_status",
                "artifact_status",
                "runtime_emission_status",
                "claim_ready",
            ):
                value = payload.get(key)
                if isinstance(value, (str, bool)):
                    record[key] = value
    return record


def _source_page_texts(root: Path) -> tuple[str, ...]:
    path = root / SOURCE_PDF_PATH
    try:
        stat = path.stat()
    except OSError:
        return ()
    return _cached_source_page_texts(str(path.resolve()), stat.st_mtime_ns, stat.st_size)


@lru_cache(maxsize=8)
def _cached_source_page_texts(
    resolved_path: str,
    _mtime_ns: int,
    _size: int,
) -> tuple[str, ...]:
    try:
        reader = PdfReader(Path(resolved_path), strict=True)
        return tuple(page.extract_text() or "" for page in reader.pages)
    except Exception:  # pragma: no cover - exact pypdf errors vary.
        return ()


def _canonical(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _read_json(path: Path) -> object:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return None


def _safe_is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[
    dict[str, Any] | None,
    list[AlphaEvolveAppendixAClaimInventoryBoundaryIssue],
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
    return None, [_issue("invalid_shape", "Appendix A claim inventory must be an object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveAppendixAClaimInventoryBoundaryIssue:
    return AlphaEvolveAppendixAClaimInventoryBoundaryIssue(code=code, message=message)
