from __future__ import annotations

import json
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from pypdf import PdfReader

from libreevolve.problems.benchmarks.ablation_registry import (
    EXPECTED_VARIANT_IDS_BY_TARGET_FAMILY,
)
from libreevolve.problems.benchmarks.alphaevolve_source_inventory_boundary import (
    EXPECTED_NAMED_SOURCE_SPAN_IDS,
    SOURCE_PAPER_ID,
    SOURCE_PDF_PATH,
    alphaevolve_source_inventory_boundary_record,
)


ALPHAEVOLVE_ABLATION_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_ablation_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "section_4_and_figure_8_claim_inventory_complete_without_executed_"
    "equal_budget_ablation_or_result_reproduction"
)
EXPECTED_CLAIM_COUNT = 51
IMPLEMENTED_STATUS = "implemented_local"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)
EXPECTED_FIGURE8_PANEL_VARIANT_IDS = {
    "matrix_tensor_decomposition": (
        "full_system",
        "no_meta_prompt_evolution",
        "small_base_llm_only",
        "no_context_in_prompt",
        "no_full_file_evolution",
        "no_evolution",
    ),
    "kissing_number_sphere_packing": (
        "full_system",
        "no_context_in_prompt",
        "no_evolution",
    ),
}
EXPECTED_FIGURE8_SERIES_COUNT = 9


_TODO_SPECS = {
    "execution": (
        "docs/todo/code.md",
        "Execute the source-faithful AlphaEvolve Section 4 ablation suite.",
    ),
    "paper": (
        "docs/todo/papers.md",
        "Track source-faithful AlphaEvolve Section 4 ablation evidence.",
    ),
    "full_file": (
        "docs/todo/code.md",
        "Bind the `No full-file evolution` ablation to loss-function-only",
    ),
    "exhibit": (
        "docs/todo/papers.md",
        "Track Figure 8 ablation-curve exhibit provenance as paper evidence.",
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


_EVOLUTION_EVIDENCE = (
    "libreevolve/core/database.py",
    "libreevolve/core/loop.py",
    "libreevolve/population/map_elites.py",
    "libreevolve/population/islands.py",
)
_CONTEXT_EVIDENCE = (
    "libreevolve/core/prompt.py",
    "libreevolve/core/config.py",
    "libreevolve/problems/benchmarks/alphaevolve_ablations.json",
    "tests/test_ablation_registry.py",
)
_REPORT_EVIDENCE = (
    "libreevolve/problems/benchmarks/alphaevolve_ablations.json",
    "libreevolve/problems/benchmarks/ablation_registry.py",
    "libreevolve/problems/benchmarks/ablation_results.py",
    "tests/test_ablation_registry.py",
    "tests/test_ablation_results.py",
)
_EXHIBIT_EVIDENCE = _REPORT_EVIDENCE + (
    "libreevolve/problems/benchmarks/ablation_exhibits.py",
    "tests/test_ablation_exhibits.py",
    "papers/figure8_ablation_artifacts.json",
)
_META_PROMPT_EVIDENCE = (
    "libreevolve/core/loop.py",
    "libreevolve/core/prompt.py",
    "libreevolve/problems/benchmarks/alphaevolve_ablations.json",
    "papers/meta_prompt_scoring_boundary.json",
)
_FULL_FILE_EVIDENCE = (
    "libreevolve/core/candidate.py",
    "libreevolve/core/diff.py",
    "libreevolve/problems/loader.py",
    "libreevolve/problems/benchmarks/alphaevolve_ablations.json",
)
_MODEL_MIX_EVIDENCE = (
    "libreevolve/llm/ensemble.py",
    "libreevolve/problems/benchmarks/alphaevolve_ablations.json",
    "papers/fast_strong_model_mix_boundary.json",
)


ABLATION_CLAIM_SPECS = (
    _claim(
        "section4_ablation_experiments_reported",
        "section_4",
        17,
        "We carried out ablations on two tasks",
        "Independently execute rather than merely declare the paper's ablation experiments.",
        "ablation_setup",
        "not_demonstrated",
        _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "section4_two_task_families",
        "section_4",
        17,
        "ablations on two tasks",
        "Preserve the two-task-family experiment scope.",
        "ablation_setup",
        "partially_implemented",
        _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "section4_matrix_tensor_decomposition_task",
        "section_4",
        17,
        "finding tensor decompositions for faster matrix multiplication",
        "Bind the matrix panel to tensor-decomposition targets.",
        "ablation_setup",
        "partially_implemented",
        _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "section4_matrix_faster_multiplication_goal",
        "section_4",
        17,
        "for faster matrix multiplication",
        "Retain faster matrix multiplication as the tensor-decomposition task motivation.",
        "ablation_setup",
        "partially_implemented",
        _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "section4_kissing_lower_bound_task",
        "section_4",
        17,
        "computing lower bounds on kissing numbers",
        "Bind the kissing panel to lower-bound construction targets.",
        "ablation_setup",
        "partially_implemented",
        _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "section4_component_efficacy_goal",
        "section_4",
        17,
        "aiming to understand the efficacy of the following components",
        "Keep component efficacy as the ablation purpose rather than treating variants as labels only.",
        "ablation_setup",
        "partially_implemented",
        _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "evolutionary_approach_used",
        "section_4",
        17,
        "AlphaEvolve utilizes an evolutionary approach",
        "Use an evolutionary search process.",
        "evolution_ablation",
        "implemented_local",
        _EVOLUTION_EVIDENCE,
        (),
    ),
    _claim(
        "previous_programs_stored_in_database",
        "section_4",
        17,
        "previously generated programs are stored in a database",
        "Persist generated programs in the evolutionary database.",
        "evolution_ablation",
        "implemented_local",
        _EVOLUTION_EVIDENCE,
        (),
    ),
    _claim(
        "previous_programs_drive_subsequent_improvement",
        "section_4",
        17,
        "used to obtain better programs in subsequent iterations",
        "Demonstrate that database-selected programs improve subsequent candidates under controlled budgets.",
        "evolution_ablation",
        "partially_implemented",
        _EVOLUTION_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "no_evolution_repeats_same_initial_program",
        "section_4",
        17,
        "repeatedly feeds the same initial program to the language model",
        "Make every no-evolution proposal use the same initial program without evolutionary feedback.",
        "evolution_ablation",
        "not_implemented",
        _EVOLUTION_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "no_evolution_variant_name",
        "section_4",
        17,
        "We refer to this approach as No evolution",
        "Preserve the `No evolution` source label and semantics.",
        "evolution_ablation",
        "partially_implemented",
        _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "powerful_models_large_context_windows",
        "section_4",
        17,
        "powerful language models with large context windows",
        "Record model capability and context-window evidence for the full comparator.",
        "prompt_context_ablation",
        "partially_implemented",
        _CONTEXT_EVIDENCE + _MODEL_MIX_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "context_significantly_improves_output",
        "section_4",
        17,
        "output can be improved significantly",
        "Measure the claimed significant context contribution rather than infer it from prompt support.",
        "prompt_context_ablation",
        "not_demonstrated",
        _CONTEXT_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "problem_specific_prompt_context",
        "section_4",
        17,
        "providing problem-specific context in the prompt",
        "Provide and classify problem-specific prompt context in the full comparator.",
        "prompt_context_ablation",
        "partially_implemented",
        _CONTEXT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "no_context_removes_explicit_context",
        "section_4",
        17,
        "where no explicit context is added to the prompt",
        "Remove explicit problem-specific context without conflating the variant with no evolution.",
        "prompt_context_ablation",
        "not_implemented",
        _CONTEXT_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "no_context_variant_name",
        "section_4",
        17,
        "We refer to this approach as No context in the prompt",
        "Preserve the `No context in the prompt` source label and explicit-context boundary.",
        "prompt_context_ablation",
        "partially_implemented",
        _CONTEXT_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "figure8_left_matrix_panel",
        "figure_8",
        18,
        "low-rank tensor decomposition for faster matrix multiplication",
        "Preserve the left matrix tensor-decomposition panel identity.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_right_kissing_panel",
        "figure_8",
        18,
        "sphere packings for improving kissing numbers",
        "Preserve the right sphere-packing/kissing-number panel identity.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_curve_per_setting",
        "figure_8",
        18,
        "Each curve shows the performance of an individual setting",
        "Link each rendered curve to one concrete full or ablated setting.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_increasing_compute_budget",
        "figure_8",
        18,
        "with increasing compute budget",
        "Report curves over increasing comparable compute-budget fractions.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_average_over_targets",
        "figure_8",
        18,
        "averaged over all considered targets",
        "Compute and retain cross-target curve aggregation from per-target records.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_higher_metric_is_better",
        "figure_8",
        18,
        "higher values on the target metric are better",
        "Require higher-is-better target metric direction.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_intra_target_standard_deviation",
        "figure_8",
        18,
        "The shades indicate intra-target standard deviation",
        "Derive and render intra-target standard-deviation bands.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_three_independent_runs",
        "figure_8",
        18,
        "averaged over three independent runs of AlphaEvolve",
        "Back every setting/target curve with exactly three independent runs.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_different_random_seeds",
        "figure_8",
        18,
        "initialized with different random seeds",
        "Retain distinct seed identities and initialization provenance.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_matrix_full_method_series",
        "figure_8",
        18,
        "Full method",
        "Include `Full method` in the matrix panel.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_matrix_no_meta_prompt_series",
        "figure_8",
        18,
        "No meta prompt evolution",
        "Include `No meta prompt evolution` only in the matrix panel.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_matrix_small_base_series",
        "figure_8",
        18,
        "Small base LLM only",
        "Include `Small base LLM only` only in the matrix panel.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_matrix_no_context_series",
        "figure_8",
        18,
        "No context in the prompt",
        "Include `No context in the prompt` in the matrix panel.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_matrix_no_full_file_series",
        "figure_8",
        18,
        "No full-file evolution",
        "Include `No full-file evolution` only in the matrix panel.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_matrix_no_evolution_series",
        "figure_8",
        18,
        "No evolution",
        "Include `No evolution` in the matrix panel.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_kissing_full_method_series",
        "figure_8",
        18,
        "Full method",
        "Include `Full method` in the kissing-number panel.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_kissing_no_context_series",
        "figure_8",
        18,
        "No context in the prompt",
        "Include `No context in the prompt` in the kissing-number panel.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "figure8_kissing_no_evolution_series",
        "figure_8",
        18,
        "No evolution",
        "Include `No evolution` in the kissing-number panel and no matrix-only variants.",
        "figure8_exhibit",
        "partially_implemented",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "meta_prompts_used",
        "section_4",
        18,
        "AlphaEvolve also uses meta prompts",
        "Provide an enabled meta-prompt comparator with retained call and lineage evidence.",
        "meta_prompt_ablation",
        "partially_implemented",
        _META_PROMPT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "meta_prompts_improve_llm_prompts",
        "section_4",
        18,
        "improve the prompts that are provided to the language model",
        "Measure prompt-policy improvement attributable to meta prompts.",
        "meta_prompt_ablation",
        "partially_implemented",
        _META_PROMPT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "meta_prompts_can_surpass_human_prompter",
        "section_4",
        18,
        "potentially surpass the performance one can obtain using a human prompter",
        "Provide a controlled human-prompter comparator before claiming uplift.",
        "meta_prompt_ablation",
        "not_demonstrated",
        _META_PROMPT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "meta_prompt_disabled_for_tensor_task",
        "section_4",
        18,
        "we disable it for the task of tensor decomposition",
        "Execute the no-meta-prompt variant on tensor decomposition only.",
        "meta_prompt_ablation",
        "not_implemented",
        _META_PROMPT_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "no_meta_prompt_variant_name",
        "section_4",
        18,
        "We refer to this approach as No meta prompt evolution",
        "Preserve the `No meta prompt evolution` label and target scope.",
        "meta_prompt_ablation",
        "partially_implemented",
        _META_PROMPT_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "full_file_contrast_with_funsearch",
        "section_4",
        18,
        "Unlike previous approaches such as FunSearch",
        "Retain the source comparison without treating local metadata as a reproduced FunSearch comparator.",
        "full_file_ablation",
        "not_demonstrated",
        _FULL_FILE_EVIDENCE,
        ("execution", "paper", "full_file"),
    ),
    _claim(
        "entire_codebase_evolution",
        "section_4",
        18,
        "AlphaEvolve can evolve an entire codebase",
        "Support and demonstrate full-codebase mutation beyond bounded local workspace edits.",
        "full_file_ablation",
        "partially_implemented",
        _FULL_FILE_EVIDENCE,
        ("execution", "paper", "full_file"),
    ),
    _claim(
        "single_function_contrast",
        "section_4",
        18,
        "instead of focusing on a single function",
        "Preserve the full-codebase versus single-function comparison in executable edit-surface evidence.",
        "full_file_ablation",
        "partially_implemented",
        _FULL_FILE_EVIDENCE,
        ("execution", "paper", "full_file"),
    ),
    _claim(
        "full_file_ablation_tensor_context",
        "section_4",
        18,
        "alternative in the context of tensor decomposition",
        "Execute the full-file edit-surface ablation on tensor decomposition.",
        "full_file_ablation",
        "not_implemented",
        _FULL_FILE_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper", "full_file"),
    ),
    _claim(
        "no_full_file_only_loss_function_evolved",
        "section_4",
        18,
        "where only the loss function is evolved",
        "Restrict the matrix ablation to the loss function rather than generic diff or single-file edits.",
        "full_file_ablation",
        "not_implemented",
        _FULL_FILE_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper", "full_file"),
    ),
    _claim(
        "no_full_file_variant_name",
        "section_4",
        18,
        "We refer to this approach as No full-file evolution",
        "Preserve the `No full-file evolution` label and loss-function-only boundary.",
        "full_file_ablation",
        "partially_implemented",
        _FULL_FILE_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper", "full_file"),
    ),
    _claim(
        "small_large_model_mixture",
        "section_4",
        18,
        "AlphaEvolve relies on a mixture of small and large language models",
        "Bind the full comparator to auditable small/large model capability tiers and routing.",
        "model_mix_ablation",
        "partially_implemented",
        _MODEL_MIX_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "model_mix_high_sample_diversity",
        "section_4",
        18,
        "in order to obtain highly diverse samples",
        "Measure sample diversity attributable to the small/large model mixture.",
        "model_mix_ablation",
        "not_demonstrated",
        _MODEL_MIX_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "small_base_only_alternative",
        "section_4",
        18,
        "only a single small base model is used",
        "Execute mutation generation with one verified small base model and no larger-model routing or fallback.",
        "model_mix_ablation",
        "not_implemented",
        _MODEL_MIX_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "small_base_only_variant_name",
        "section_4",
        18,
        "We refer to this approach as Small base LLM only",
        "Preserve the `Small base LLM only` label and matrix-only target scope.",
        "model_mix_ablation",
        "partially_implemented",
        _MODEL_MIX_EVIDENCE + _REPORT_EVIDENCE,
        ("execution", "paper"),
    ),
    _claim(
        "figure8_reports_full_and_alternative_results",
        "section_4",
        18,
        "Figure 8 shows the results of the all-inclusive AlphaEvolve approach",
        "Emit independently executed full-system and applicable alternative result curves.",
        "ablation_result",
        "not_demonstrated",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
    _claim(
        "each_component_significant_improvement",
        "section_4",
        18,
        "each of the components is responsible for a significant improvement in the results",
        "Do not claim significant component contributions without reproduced measurements and an explicit significance interpretation.",
        "ablation_result",
        "not_demonstrated",
        _EXHIBIT_EVIDENCE,
        ("execution", "paper", "exhibit"),
    ),
)

EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in ABLATION_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveAblationClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveAblationClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveAblationClaimInventoryBoundaryIssue]


def alphaevolve_ablation_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the Section 4 and Figure 8 claim-level implementation audit."""

    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _claim_record(root_path, spec, page_texts) for spec in ABLATION_CLAIM_SPECS
    ]
    category_counts = Counter(record["category"] for record in records)
    status_counts = Counter(record["implementation_status"] for record in records)
    missing_anchor_count = sum(
        1 for record in records if not record["source_anchor_present"]
    )
    missing_reference_count = sum(
        1
        for record in records
        for ref in record["evidence_refs"]
        if not ref["exists"]
    ) + sum(
        1
        for record in records
        for ref in record["active_todo_refs"]
        if not ref["exists"] or not ref["required_phrase_present"]
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
    registry_panel_variant_ids = {
        panel_id: list(variant_ids)
        for panel_id, variant_ids in EXPECTED_VARIANT_IDS_BY_TARGET_FAMILY.items()
    }
    expected_panel_variant_ids = {
        panel_id: list(variant_ids)
        for panel_id, variant_ids in EXPECTED_FIGURE8_PANEL_VARIANT_IDS.items()
    }
    source_shape_matches = registry_panel_variant_ids == expected_panel_variant_ids
    source_artifact = source_inventory["source_artifact"]
    inventory_ready = (
        source_artifact["identity_ok"]
        and source_inventory["named_structure_inventory_ready"]
        and len(records) == EXPECTED_CLAIM_COUNT
        and missing_anchor_count == 0
        and missing_reference_count == 0
        and todo_owned_gap_count == implementation_gap_count
        and source_shape_matches
    )
    return {
        "schema": ALPHAEVOLVE_ABLATION_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "ablation_claim_inventory_ready": inventory_ready,
        "alphaevolve_ablation_result_reproduction_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": ["section_4", "figure_8"],
        "figure8_source_shape": {
            "expected_panel_variant_ids": expected_panel_variant_ids,
            "registry_panel_variant_ids": registry_panel_variant_ids,
            "expected_series_count": EXPECTED_FIGURE8_SERIES_COUNT,
            "registry_series_count": sum(
                len(variant_ids)
                for variant_ids in EXPECTED_VARIANT_IDS_BY_TARGET_FAMILY.values()
            ),
            "matches_source": source_shape_matches,
        },
        "inventory_scope": {
            "included": [
                "all substantive Section 4 experiment-setup, component-definition, target-scope, and result claims",
                "Figure 8 caption, axes, aggregation, direction, seed, uncertainty-band, panel, and panel-specific series claims",
                "source-fidelity correction from an all-six-variants-on-both-panels Cartesian contract to six matrix series and three kissing-number series",
            ],
            "excluded": [
                "Section 5 related-work claim exhaustiveness and Figures 9 through 14",
                "Table 3, detailed appendices, citations, equations, and bibliography details",
                "executed equal-budget matrix or kissing-number ablation runs, cross-target aggregate curves, or rendered Figure 8 artifacts",
                "independent reproduction of the paper's significant-improvement conclusion",
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
            "This sidecar certifies a bounded claim-level inventory of 51 "
            "AlphaEvolve Section 4 and Figure 8 ablation claims. It preserves "
            "the source's six matrix series and three kissing-number series, "
            "rather than an incorrect full Cartesian product. Registry, result-"
            "schema, and exhibit metadata are partial implementation evidence, "
            "not actual runs. It does not claim executed equal-budget ablations, "
            "component isolation, three-seed measurements, aggregate curves, "
            "rendered Figure 8 evidence, significant improvement, result "
            "reproduction, production scale, or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_ablation_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveAblationClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_ablation_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveAblationClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_ablation_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveAblationClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_ABLATION_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ablation claim inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    if data.get("alphaevolve_ablation_result_reproduction_claim_ready") is not False:
        issues.append(
            _issue(
                "result_reproduction_overclaim",
                "ablation inventory must not claim result reproduction",
            )
        )
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(
            _issue("parity_overclaim", "ablation inventory must not claim AlphaEvolve parity")
        )
    for key in (
        "source_artifact",
        "source_inventory_schema",
        "source_inventory_span_count",
        "source_span_ids",
        "figure8_source_shape",
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
                    f"{key} drifted from the bounded ablation claim inventory",
                )
            )
    if len(EXPECTED_CLAIM_IDS) != EXPECTED_CLAIM_COUNT:
        issues.append(_issue("invalid_spec_count", "ablation claim count must remain 51"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "ablation claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in ABLATION_CLAIM_SPECS
            if spec["source_span_id"] not in EXPECTED_NAMED_SOURCE_SPAN_IDS
        }
    )
    if unknown_spans:
        issues.append(
            _issue("unknown_source_span", f"unknown source spans: {', '.join(unknown_spans)}")
        )
    unsupported_statuses = sorted(
        {
            spec["implementation_status"]
            for spec in ABLATION_CLAIM_SPECS
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
                f"{expected['missing_anchor_count']} ablation claim anchors were not found",
            )
        )
    if expected["missing_reference_count"]:
        issues.append(
            _issue(
                "missing_local_reference",
                f"{expected['missing_reference_count']} evidence or TODO references are stale",
            )
        )
    if not expected["figure8_source_shape"]["matches_source"]:
        issues.append(
            _issue(
                "figure8_source_shape_mismatch",
                "registry target coverage does not match the six-series/three-series source shape",
            )
        )
    expected_ready = (
        expected["source_artifact"]["identity_ok"]
        and expected["claim_count"] == EXPECTED_CLAIM_COUNT
        and expected["missing_anchor_count"] == 0
        and expected["missing_reference_count"] == 0
        and expected["todo_owned_gap_count"] == expected["implementation_gap_count"]
        and expected["figure8_source_shape"]["matches_source"]
    )
    if data.get("ablation_claim_inventory_ready") is not expected_ready:
        issues.append(
            _issue(
                "invalid_ablation_claim_inventory_ready",
                "ablation_claim_inventory_ready does not match source, reference, ownership, and panel-shape checks",
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "51" not in claim_boundary
        or "six matrix series" not in claim_boundary
        or "three kissing-number series" not in claim_boundary
        or "actual runs" not in claim_boundary
        or "significant improvement" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must separate bounded Section 4 claims from execution, result, and parity proof",
            )
        )
    return AlphaEvolveAblationClaimInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=(
            data.get("boundary_status")
            if isinstance(data.get("boundary_status"), str)
            else None
        ),
        claim_count=(data.get("claim_count") if isinstance(data.get("claim_count"), int) else 0),
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


def render_alphaevolve_ablation_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_ablation_claim_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve ablation claim inventory boundary",
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
    list[AlphaEvolveAblationClaimInventoryBoundaryIssue],
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
        _issue("invalid_shape", "ablation claim inventory boundary must be a JSON object")
    ]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveAblationClaimInventoryBoundaryIssue:
    return AlphaEvolveAblationClaimInventoryBoundaryIssue(code, message)
