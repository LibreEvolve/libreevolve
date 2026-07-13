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


ALPHAEVOLVE_KERNEL_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_kernel_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "section_3_3_2_figure_7_claim_inventory_complete_without_"
    "pallas_fixture_or_result_reproduction"
)
EXPECTED_CLAIM_COUNT = 59
IMPLEMENTED_STATUS = "implemented_local"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)


_TODO_SPECS = {
    "application": (
        "docs/todo/code.md",
        "Populate application-owner and domain-review provenance for practical",
    ),
    "calibration": (
        "docs/todo/code.md",
        "Populate Section 3.3 result-claim calibration fields for systems reports.",
    ),
    "figure7": (
        "docs/todo/code.md",
        "Add Figure 7 Pallas tiling-problem exhibit provenance and diagram",
    ),
    "pallas_fixture": (
        "docs/todo/code.md",
        "Add an executable JAX/Pallas matrix-tiling benchmark contract.",
    ),
    "self_training": (
        "docs/todo/code.md",
        "Add Gemini self-training optimization loop provenance for Pallas",
    ),
    "shape_corpus": (
        "docs/todo/code.md",
        "Add kernel-tiling train/eval shape provenance for Pallas-style heuristics.",
    ),
    "systems_fixtures": (
        "docs/todo/code.md",
        "Connect real systems fixtures to held-out and reference-correctness",
    ),
    "workflow": (
        "docs/todo/code.md",
        "Add Pallas autotuning/manual-heuristic baseline workflow provenance.",
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
    roadmap_section_id: str = "representative_benchmarks",
    roadmap_phase: str = "longer_term",
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "source_span_id": source_span_id,
        "source_page": source_page,
        "source_anchor": source_anchor,
        "claim": claim,
        "category": category,
        "implementation_status": implementation_status,
        "roadmap_section_id": roadmap_section_id,
        "roadmap_phase": roadmap_phase,
        "evidence_paths": evidence_paths,
        "todo_ids": todo_ids,
    }


_SYSTEMS_EVIDENCE = (
    "libreevolve/problems/benchmarks/systems_results.py",
    "papers/systems_result_readiness_boundary.json",
)
_FIGURE7_EVIDENCE = (
    "papers/figure7_pallas_tiling_exhibit_boundary.json",
    "papers/systems_result_readiness_boundary.json",
)
_SHAPE_EVIDENCE = (
    "papers/kernel_tiling_shape_corpus_boundary.json",
    "libreevolve/problems/benchmarks/systems_results.py",
)
_WORKFLOW_EVIDENCE = (
    "papers/pallas_workflow_baseline_boundary.json",
    "papers/kernel_tiling_shape_corpus_boundary.json",
)
_SELF_TRAINING_EVIDENCE = (
    "papers/gemini_self_training_loop_boundary.json",
    "papers/systems_result_readiness_boundary.json",
)


KERNEL_CLAIM_SPECS = (
    _claim(
        "figure7_matrix_product_tiling_problem",
        "figure_7",
        15,
        "Visualization of the tiling heuristic problem for a matrix product A B = C",
        "Reproduce Figure 7 as a matrix-product tiling problem for A B = C.",
        "figure_7_exhibit",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("figure7", "pallas_fixture"),
    ),
    _claim(
        "figure7_choose_m_n_p_tile_size",
        "figure_7",
        15,
        "automatically chooses the right tile size (M, N, P)",
        "Define the heuristic output as the M, N, and P tile-size tuple.",
        "figure_7_exhibit",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("figure7", "pallas_fixture"),
    ),
    _claim(
        "figure7_tile_selection_for_all_input_shapes",
        "figure_7",
        15,
        "for all input shapes is difficult",
        "Evaluate one tiling heuristic across the declared input-shape domain.",
        "figure_7_exhibit",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("figure7", "shape_corpus", "pallas_fixture"),
    ),
    _claim(
        "figure7_matrix_unit_optimal_shape_context",
        "figure_7",
        15,
        "matrix multiplication unit's optimal shapes",
        "Record matrix-multiplication-unit optimal-shape context for tile selection.",
        "figure_7_exhibit",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("figure7", "pallas_fixture"),
    ),
    _claim(
        "figure7_accelerator_memory_capacity_context",
        "figure_7",
        15,
        "optimal shapes and memory capacity",
        "Record accelerator memory-capacity constraints for tile selection.",
        "figure_7_exhibit",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("figure7", "pallas_fixture"),
    ),
    _claim(
        "figure7_surrounding_operation_memory_context",
        "figure_7",
        15,
        "memory requirements of surrounding operations",
        "Record surrounding-operation memory requirements in the tiling context.",
        "figure_7_exhibit",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("figure7", "pallas_fixture"),
    ),
    _claim(
        "figure7_fused_operation_context",
        "figure_7",
        15,
        "extra operations that are fused into the kernel",
        "Record fused-operation context affecting tile selection.",
        "figure_7_exhibit",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("figure7", "pallas_fixture"),
    ),
    _claim(
        "figure7_compiler_intricacy_context",
        "figure_7",
        15,
        "low-level compiler intricacies",
        "Record low-level compiler constraints affecting tile selection.",
        "figure_7_exhibit",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("figure7", "pallas_fixture"),
    ),
    _claim(
        "section3_3_2_gemini_training_compute_demand",
        "section_3_3_2",
        15,
        "Training large models like Gemini requires substantial computational resources",
        "Demonstrate the computational-resource context for the target training workload.",
        "gemini_pallas_context",
        "not_demonstrated",
        _SELF_TRAINING_EVIDENCE,
        ("application", "self_training"),
    ),
    _claim(
        "section3_3_2_gemini_built_on_jax",
        "section_3_3_2",
        15,
        "Gemini is built on JAX",
        "Preserve the source claim that the optimized Gemini training stack is based on JAX.",
        "gemini_pallas_context",
        "not_demonstrated",
        _SELF_TRAINING_EVIDENCE,
        ("pallas_fixture", "self_training"),
    ),
    _claim(
        "section3_3_2_pallas_extends_jax",
        "section_3_3_2",
        15,
        "Pallas is an extension to JAX",
        "Provide an executable JAX/Pallas task surface rather than metadata-only attribution.",
        "gemini_pallas_context",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("pallas_fixture",),
    ),
    _claim(
        "section3_3_2_custom_specialized_kernel_programs",
        "section_3_3_2",
        15,
        "writing custom, highly specialized programs (kernels)",
        "Evolve custom specialized kernel code through a task-owned candidate surface.",
        "gemini_pallas_context",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture",),
    ),
    _claim(
        "section3_3_2_optimal_accelerator_execution",
        "section_3_3_2",
        15,
        "tailored for optimal execution on hardware accelerators",
        "Execute and evaluate the specialized kernel on a declared accelerator target.",
        "gemini_pallas_context",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_pallas_kernel_training_importance",
        "section_3_3_2",
        15,
        "efficient Pallas kernels are crucial for optimizing Gemini's training performance",
        "Demonstrate how the target Pallas kernel affects Gemini training performance.",
        "gemini_pallas_context",
        "not_demonstrated",
        _SELF_TRAINING_EVIDENCE,
        ("application", "self_training"),
    ),
    _claim(
        "section3_3_2_matmul_tiling_is_critical_optimization",
        "section_3_3_2",
        15,
        "critical aspect of kernel optimization is tuning the tiling strategy",
        "Implement matrix-multiplication tiling as the benchmark's optimization surface.",
        "tiling_problem_formulation",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("pallas_fixture", "figure7"),
    ),
    _claim(
        "section3_3_2_tiling_divides_large_matmul",
        "section_3_3_2",
        15,
        "dividing a large matrix multiplication computation into smaller subproblems",
        "Define tiling as decomposition of a large matrix multiplication into smaller subproblems.",
        "tiling_problem_formulation",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("pallas_fixture", "figure7"),
    ),
    _claim(
        "section3_3_2_balance_compute_and_data_movement",
        "section_3_3_2",
        15,
        "balance computation with data movement",
        "Represent the computation-versus-data-movement tradeoff in tiling evidence.",
        "tiling_problem_formulation",
        "not_implemented",
        _FIGURE7_EVIDENCE,
        ("pallas_fixture", "figure7"),
    ),
    _claim(
        "section3_3_2_tiling_accelerates_overall_computation",
        "section_3_3_2",
        15,
        "key to accelerating the overall computation",
        "Measure whether the selected tiling strategy accelerates the full computation.",
        "tiling_problem_formulation",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_search_based_autotuning_baseline",
        "section_3_3_2",
        15,
        "search-based autotuning",
        "Provide a search-based autotuning baseline for the tiling task.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow", "pallas_fixture"),
    ),
    _claim(
        "section3_3_2_manual_heuristic_baseline",
        "section_3_3_2",
        15,
        "manually crafted heuristics",
        "Provide a manually crafted expert heuristic baseline for the tiling task.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow", "pallas_fixture"),
    ),
    _claim(
        "section3_3_2_near_optimal_configs_varied_shapes",
        "section_3_3_2",
        15,
        "near-optimal tiling configurations for various input shapes",
        "Compare tiling configurations across varied input shapes against declared baselines.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow", "shape_corpus", "pallas_fixture"),
    ),
    _claim(
        "section3_3_2_autotuning_interrupts_workflow",
        "section_3_3_2",
        15,
        "Search-based tuning interrupts the research workflow",
        "Record workflow interruption caused by search-based autotuning.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow",),
    ),
    _claim(
        "section3_3_2_retune_every_shape_change",
        "section_3_3_2",
        15,
        "retuning for every input shape change",
        "Record the autotuning retuning policy and burden for input-shape changes.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow",),
    ),
    _claim(
        "section3_3_2_manual_heuristic_bottleneck",
        "section_3_3_2",
        15,
        "manually crafting effective tiling heuristics is a major engineering bottleneck",
        "Measure the manual-authoring bottleneck for effective tiling heuristics.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow",),
    ),
    _claim(
        "section3_3_2_deep_kernel_functionality_expertise",
        "section_3_3_2",
        15,
        "deep understanding of both kernel functionality",
        "Record kernel-functionality expertise assumptions for manual heuristic design.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow",),
    ),
    _claim(
        "section3_3_2_deep_hardware_expertise",
        "section_3_3_2",
        15,
        "and hardware intricacies",
        "Record hardware-expertise assumptions for manual heuristic design.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow",),
    ),
    _claim(
        "section3_3_2_high_performance_arbitrary_shapes",
        "section_3_3_2",
        15,
        "deliver high performance across arbitrary input shapes",
        "Evaluate whether one heuristic maintains high performance across arbitrary declared shapes.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_expedite_emerging_hardware_kernels",
        "section_3_3_2",
        15,
        "expedite the design of performant kernels for emerging hardware",
        "Measure whether generated heuristics shorten performant-kernel development for emerging hardware.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow", "application"),
    ),
    _claim(
        "section3_3_2_simplify_model_developer_utilization",
        "section_3_3_2",
        15,
        "simplify their utilization by model developers",
        "Record model-developer utilization and ergonomics effects.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow", "application"),
    ),
    _claim(
        "section3_3_2_facilitate_heuristic_generation",
        "section_3_3_2",
        15,
        "facilitate the heuristic generation process",
        "Provide an end-to-end generated-tiling-heuristic workflow.",
        "baseline_workflow",
        "not_implemented",
        _WORKFLOW_EVIDENCE,
        ("workflow", "pallas_fixture"),
    ),
    _claim(
        "section3_3_2_optimize_tiling_heuristics",
        "section_3_3_2",
        15,
        "employing AlphaEvolve to optimize tiling heuristics",
        "Run LibreEvolve against an executable tiling-heuristic candidate surface.",
        "kernel_discovery_and_evaluation",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus", "systems_fixtures"),
    ),
    _claim(
        "section3_3_2_gemini_training_matmul_kernel",
        "section_3_3_2",
        15,
        "important matrix multiplication kernel used to train Gemini",
        "Identify and retain the matrix-multiplication kernel and training workload under optimization.",
        "kernel_discovery_and_evaluation",
        "not_implemented",
        _SELF_TRAINING_EVIDENCE,
        ("pallas_fixture", "self_training"),
    ),
    _claim(
        "section3_3_2_minimize_actual_kernel_runtime",
        "section_3_3_2",
        15,
        "objective is to minimize the kernel's actual runtime",
        "Use measured kernel runtime as a minimized evaluator objective.",
        "kernel_discovery_and_evaluation",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_iterative_tiling_refinement",
        "section_3_3_2",
        15,
        "iteratively explores and refines tiling heuristics",
        "Apply the evolutionary loop to iterative tiling-heuristic refinement.",
        "kernel_discovery_and_evaluation",
        "partially_implemented",
        ("libreevolve/core/loop.py", "papers/kernel_tiling_shape_corpus_boundary.json"),
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_candidate_code_proposals",
        "section_3_3_2",
        15,
        "by proposing candidate code",
        "Use code proposals as the mutation surface for the tiling heuristic.",
        "kernel_discovery_and_evaluation",
        "partially_implemented",
        ("libreevolve/core/prompt.py", "libreevolve/core/diff.py"),
        ("pallas_fixture",),
    ),
    _claim(
        "section3_3_2_runtime_across_various_shapes",
        "section_3_3_2",
        15,
        "minimize this runtime on various input shapes",
        "Aggregate actual runtime over a varied input-shape set.",
        "kernel_discovery_and_evaluation",
        "partially_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_real_tpu_accelerator_measurement",
        "section_3_3_2",
        15,
        "on real TPU accelerators",
        "Measure kernel runtime on identified real TPU accelerators.",
        "kernel_discovery_and_evaluation",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_correctness_by_construction",
        "section_3_3_2",
        15,
        "correctness is maintained by construction",
        "Prove the bounded conditions supporting correctness by construction.",
        "kernel_discovery_and_evaluation",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_tiling_strategy_only_candidate_scope",
        "section_3_3_2",
        15,
        "optimizing the tiling strategy for this kernel",
        "Restrict candidate edits to the kernel's tiling strategy.",
        "kernel_discovery_and_evaluation",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_underlying_math_unchanged",
        "section_3_3_2",
        16,
        "its underlying mathematical operation",
        "Verify that candidate edits leave the underlying matrix operation unchanged.",
        "kernel_discovery_and_evaluation",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_automatic_realistic_shape_collection",
        "section_3_3_2",
        16,
        "automatically collect realistic kernel input shapes",
        "Emit an automatically collected realistic kernel input-shape corpus.",
        "kernel_discovery_and_evaluation",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_shape_corpus_from_kernel_users",
        "section_3_3_2",
        16,
        "from kernel users",
        "Record kernel-user provenance for collected input shapes.",
        "kernel_discovery_and_evaluation",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("shape_corpus", "application"),
    ),
    _claim(
        "section3_3_2_half_training_shape_split",
        "section_3_3_2",
        16,
        "Half of these input shapes form the training set",
        "Create a deterministic 50 percent training-shape split.",
        "kernel_discovery_and_evaluation",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_training_shapes_are_optimization_targets",
        "section_3_3_2",
        16,
        "providing the optimization targets during the evolutionary process",
        "Use the training-shape split as optimization targets during evolution.",
        "kernel_discovery_and_evaluation",
        "partially_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_half_evaluation_shape_split",
        "section_3_3_2",
        16,
        "remaining input shapes form the evaluation set",
        "Create a disjoint 50 percent held-out evaluation-shape split.",
        "kernel_discovery_and_evaluation",
        "not_implemented",
        _SHAPE_EVIDENCE,
        ("pallas_fixture", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_evaluation_tests_general_applicability",
        "section_3_3_2",
        16,
        "used to test the general applicability of the resulting heuristic",
        "Use held-out shapes to test heuristic generalization.",
        "kernel_discovery_and_evaluation",
        "partially_implemented",
        _SYSTEMS_EVIDENCE,
        ("pallas_fixture", "shape_corpus", "systems_fixtures"),
    ),
    _claim(
        "section3_3_2_average_twenty_three_percent_kernel_speedup",
        "section_3_3_2",
        16,
        "average 23% kernel speedup across all kernels",
        "Reproduce the average 23 percent kernel-speedup result with its aggregation denominator.",
        "kernel_production_result",
        "not_demonstrated",
        _SHAPE_EVIDENCE,
        ("calibration", "shape_corpus", "systems_fixtures"),
    ),
    _claim(
        "section3_3_2_expert_designed_heuristic_comparator",
        "section_3_3_2",
        16,
        "over the existing expert-designed heuristic",
        "Compare the evolved heuristic against the identified expert-designed incumbent.",
        "kernel_production_result",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE,
        ("calibration", "workflow", "shape_corpus"),
    ),
    _claim(
        "section3_3_2_one_percent_gemini_training_reduction",
        "section_3_3_2",
        16,
        "corresponding 1% reduction in Gemini's overall training time",
        "Reproduce the corresponding one percent Gemini training-time reduction.",
        "kernel_production_result",
        "not_demonstrated",
        _SELF_TRAINING_EVIDENCE,
        ("calibration", "application", "self_training"),
    ),
    _claim(
        "section3_3_2_optimization_months_to_days",
        "section_3_3_2",
        16,
        "reduced the kernel optimization time, from several months",
        "Reproduce the reduction in kernel optimization turnaround from months to days.",
        "kernel_production_result",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE,
        ("calibration", "workflow", "application"),
    ),
    _claim(
        "section3_3_2_dedicated_effort_to_automated_experimentation",
        "section_3_3_2",
        16,
        "dedicated engineering effort to just days of automated experimentation",
        "Calibrate dedicated engineering effort against automated-experimentation time.",
        "kernel_production_result",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE,
        ("calibration", "workflow", "application"),
    ),
    _claim(
        "section3_3_2_faster_optimized_kernel_deployment",
        "section_3_3_2",
        16,
        "This acceleration speeds up the deployment of optimized kernels",
        "Demonstrate that shorter optimization turnaround accelerates kernel deployment.",
        "kernel_production_result",
        "not_demonstrated",
        _SELF_TRAINING_EVIDENCE,
        ("application", "self_training"),
    ),
    _claim(
        "section3_3_2_engineers_focus_higher_level_work",
        "section_3_3_2",
        16,
        "dedicate their expertise to more strategic, higher-level optimization problems",
        "Demonstrate that automation shifts engineering effort to strategic higher-level work.",
        "kernel_production_result",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE,
        ("workflow", "application"),
    ),
    _claim(
        "section3_3_2_path_to_automated_manual_tuning",
        "section_3_3_2",
        16,
        "path towards automating the manual tuning process",
        "Demonstrate a path from manual tiling work to automated heuristic generation.",
        "kernel_deployment_and_self_optimization",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE,
        ("workflow", "application"),
    ),
    _claim(
        "section3_3_2_improved_gemini_kernel_ergonomics",
        "section_3_3_2",
        16,
        "improving the ergonomics of Gemini kernel usage",
        "Demonstrate improved ergonomics for Gemini kernel users.",
        "kernel_deployment_and_self_optimization",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE,
        ("workflow", "application"),
    ),
    _claim(
        "section3_3_2_tiling_heuristic_deployed_production",
        "section_3_3_2",
        16,
        "tiling heuristic discovered by AlphaEvolve has been deployed in production",
        "Provide reviewed production-deployment evidence for the discovered tiling heuristic.",
        "kernel_deployment_and_self_optimization",
        "not_demonstrated",
        _SELF_TRAINING_EVIDENCE,
        ("application", "self_training"),
    ),
    _claim(
        "section3_3_2_deployment_enhanced_training_efficiency",
        "section_3_3_2",
        16,
        "directly enhancing Gemini's training efficiency",
        "Link the production deployment to measured Gemini training-efficiency improvement.",
        "kernel_deployment_and_self_optimization",
        "not_demonstrated",
        _SELF_TRAINING_EVIDENCE,
        ("calibration", "application", "self_training"),
    ),
    _claim(
        "section3_3_2_team_research_engineering_velocity",
        "section_3_3_2",
        16,
        "Gemini team's research and engineering velocity",
        "Provide evidence that deployment improved the team's research and engineering velocity.",
        "kernel_deployment_and_self_optimization",
        "not_demonstrated",
        _SELF_TRAINING_EVIDENCE,
        ("application", "self_training"),
    ),
    _claim(
        "section3_3_2_gemini_optimizes_own_training",
        "section_3_3_2",
        16,
        "Gemini, through the capabilities of AlphaEvolve, optimizes its own training process",
        "Substantiate the claimed Gemini-through-AlphaEvolve self-training optimization loop.",
        "kernel_deployment_and_self_optimization",
        "not_demonstrated",
        _SELF_TRAINING_EVIDENCE,
        ("application", "self_training"),
    ),
)

EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in KERNEL_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveKernelClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveKernelClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveKernelClaimInventoryBoundaryIssue]


def alphaevolve_kernel_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Section 3.3.2 and Figure 7 claim inventory."""

    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _claim_record(root_path, spec, page_texts) for spec in KERNEL_CLAIM_SPECS
    ]
    status_counts = Counter(record["implementation_status"] for record in records)
    category_counts = Counter(record["category"] for record in records)
    missing_anchor_count = sum(
        1 for record in records if not record["source_anchor_present"]
    )
    missing_reference_count = sum(
        1
        for record in records
        for ref in (*record["evidence_refs"], *record["active_todo_refs"])
        if not ref["exists"]
        or (
            "required_phrase_present" in ref
            and not ref["required_phrase_present"]
        )
    )
    implementation_gap_count = sum(
        1
        for record in records
        if record["implementation_status"] != IMPLEMENTED_STATUS
    )
    todo_owned_gap_count = sum(
        1
        for record in records
        if record["implementation_status"] != IMPLEMENTED_STATUS
        and record["active_todo_refs"]
        and all(
            ref["exists"] and ref["required_phrase_present"]
            for ref in record["active_todo_refs"]
        )
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
        "schema": ALPHAEVOLVE_KERNEL_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "kernel_claim_inventory_ready": inventory_ready,
        "alphaevolve_kernel_result_reproduction_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": ["section_3_3_2", "figure_7"],
        "inventory_scope": {
            "included": [
                "all substantive Figure 7 matrix-product, tile-size, accelerator-shape, memory, fused-operation, and compiler-context claims",
                "all substantive Section 3.3.2 Gemini, JAX, Pallas, tiling-formulation, baseline-workflow, discovery, shape-corpus, evaluation, production-result, deployment, and self-optimization claims",
            ],
            "excluded": [
                "Sections 3.3.3 through 5 and Figures 8 through 14",
                "Table 3, detailed appendices, citations, and bibliography details",
                "an executable JAX/Pallas benchmark, Gemini training workload, kernel-user shape corpus, real TPU runtime, expert heuristic, or production deployment",
                "independent reproduction of Figure 7, the 23 percent kernel speedup, the 1 percent training-time reduction, or months-to-days turnaround",
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
            "This sidecar certifies a bounded claim-level inventory of 59 "
            "AlphaEvolve kernel-engineering claims from Section 3.3.2 and "
            "Figure 7. Status labels distinguish generic local evolutionary "
            "and systems-report support from absent JAX/Pallas behavior and "
            "undemonstrated published production outcomes. It does not claim "
            "a JAX/Pallas fixture, real TPU execution, Gemini workload or "
            "shape data, Figure 7 reproduction, the 23% or 1% results, "
            "production deployment, Gemini self-optimization, production "
            "scale, or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_kernel_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveKernelClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_kernel_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveKernelClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_kernel_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveKernelClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_KERNEL_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported kernel claim inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    if data.get("alphaevolve_kernel_result_reproduction_claim_ready") is not False:
        issues.append(
            _issue(
                "result_reproduction_overclaim",
                "kernel inventory must not claim result reproduction",
            )
        )
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(
            _issue(
                "parity_overclaim",
                "kernel inventory must not claim AlphaEvolve parity",
            )
        )
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
            issues.append(
                _issue(
                    f"invalid_{key}",
                    f"{key} drifted from the bounded kernel claim inventory",
                )
            )
    if len(EXPECTED_CLAIM_IDS) != EXPECTED_CLAIM_COUNT:
        issues.append(_issue("invalid_spec_count", "kernel claim count must remain 59"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "kernel claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in KERNEL_CLAIM_SPECS
            if spec["source_span_id"] not in EXPECTED_NAMED_SOURCE_SPAN_IDS
        }
    )
    if unknown_spans:
        issues.append(
            _issue(
                "unknown_source_span",
                f"unknown source spans: {', '.join(unknown_spans)}",
            )
        )
    unsupported_statuses = sorted(
        {
            spec["implementation_status"]
            for spec in KERNEL_CLAIM_SPECS
            if spec["implementation_status"]
            not in INCOMPLETE_STATUSES | {IMPLEMENTED_STATUS}
        }
    )
    if unsupported_statuses:
        issues.append(
            _issue(
                "unsupported_implementation_status",
                f"unsupported statuses: {', '.join(unsupported_statuses)}",
            )
        )
    unowned_gaps = sorted(
        record["claim_id"]
        for record in expected["claim_records"]
        if record["implementation_status"] != IMPLEMENTED_STATUS
        and not record["active_todo_refs"]
    )
    if unowned_gaps:
        issues.append(
            _issue(
                "unowned_implementation_gap",
                f"claims lack active TODO ownership: {', '.join(unowned_gaps)}",
            )
        )
    if not expected["source_artifact"]["identity_ok"]:
        issues.append(
            _issue(
                "source_pdf_identity_mismatch",
                "retained AlphaEvolve PDF identity does not match the pinned source",
            )
        )
    if expected["missing_anchor_count"]:
        issues.append(
            _issue(
                "missing_source_anchor",
                f"{expected['missing_anchor_count']} kernel claim anchors were not found",
            )
        )
    if expected["missing_reference_count"]:
        issues.append(
            _issue(
                "missing_local_reference",
                f"{expected['missing_reference_count']} evidence or TODO references are stale",
            )
        )
    expected_ready = (
        expected["source_artifact"]["identity_ok"]
        and expected["claim_count"] == EXPECTED_CLAIM_COUNT
        and expected["missing_anchor_count"] == 0
        and expected["missing_reference_count"] == 0
        and expected["todo_owned_gap_count"] == expected["implementation_gap_count"]
    )
    if data.get("kernel_claim_inventory_ready") is not expected_ready:
        issues.append(
            _issue(
                "invalid_kernel_claim_inventory_ready",
                "kernel_claim_inventory_ready does not match source, reference, and ownership checks",
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "59" not in claim_boundary
        or "JAX/Pallas fixture" not in claim_boundary
        or "Figure 7 reproduction" not in claim_boundary
        or "23% or 1% results" not in claim_boundary
        or "Gemini self-optimization" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must separate bounded kernel claims from Pallas, Figure 7, result, self-optimization, and parity proof",
            )
        )
    return AlphaEvolveKernelClaimInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=(
            data.get("boundary_status")
            if isinstance(data.get("boundary_status"), str)
            else None
        ),
        claim_count=(
            data.get("claim_count") if isinstance(data.get("claim_count"), int) else 0
        ),
        implemented_local_count=(
            data.get("implemented_local_count")
            if isinstance(data.get("implemented_local_count"), int)
            else 0
        ),
        implementation_gap_count=(
            data.get("implementation_gap_count")
            if isinstance(data.get("implementation_gap_count"), int)
            else 0
        ),
        missing_anchor_count=expected["missing_anchor_count"],
        missing_reference_count=expected["missing_reference_count"],
        issues=issues,
    )


def render_alphaevolve_kernel_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_kernel_claim_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve kernel claim inventory boundary",
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
        "source_anchor_present": _canonical(spec["source_anchor"])
        in _canonical(page_text),
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
    record: dict[str, Any] = {
        "path": path_label,
        "exists": _safe_is_file(path),
    }
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
    list[AlphaEvolveKernelClaimInventoryBoundaryIssue],
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
    return None, [
        _issue(
            "invalid_shape",
            "kernel claim inventory boundary must be a JSON object",
        )
    ]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveKernelClaimInventoryBoundaryIssue:
    return AlphaEvolveKernelClaimInventoryBoundaryIssue(code, message)
