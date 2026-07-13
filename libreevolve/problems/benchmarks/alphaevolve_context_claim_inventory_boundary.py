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


ALPHAEVOLVE_CONTEXT_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_context_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "abstract_introduction_discussion_claim_inventory_complete_without_"
    "results_sections_or_appendix_exhaustiveness"
)
EXPECTED_CLAIM_COUNT = 41
IMPLEMENTED_STATUS = "implemented_local"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)


_TODO_SPECS = {
    "abstraction": (
        "docs/todo/code.md",
        "Add abstraction-choice metadata and benchmark evidence for candidate",
    ),
    "automated_scope": (
        "docs/todo/code.md",
        "Extend automated-evaluator scope policy into robust environment fixtures.",
    ),
    "backtracking": (
        "docs/todo/code.md",
        "Extend observed controller redirect evidence into explicit backtracking",
    ),
    "benchmark_fixtures": (
        "docs/todo/code.md",
        "Connect benchmark-grade fixtures to hardening and scope reports.",
    ),
    "codebase_scale": (
        "docs/todo/code.md",
        "Add codebase-scale benchmark evidence for multi-component generated",
    ),
    "collaborator": (
        "docs/todo/code.md",
        "Populate broad collaborator-feedback evidence for robustness claims.",
    ),
    "critique": (
        "docs/todo/code.md",
        "Extend critique reviewer pools beyond synchronous first/last-valid",
    ),
    "divergence": (
        "docs/todo/code.md",
        "Extend initial-pool divergence reporting beyond bounded syntactic and",
    ),
    "incorrect_filter": (
        "docs/todo/code.md",
        "Extend execution-grounded filtering evidence into independent audit",
    ),
    "matrix_historicity": (
        "docs/todo/code.md",
        "Wire matrix headline historicity artifacts into runner/export outputs.",
    ),
    "matrix_suite": (
        "docs/todo/code.md",
        "Generate suite matrix tensor artifacts and per-seed hit-rate reports.",
    ),
    "math_outcomes": (
        "docs/todo/code.md",
        "Add aggregate constructive-math outcome coverage reports.",
    ),
    "problem_formulation": (
        "docs/todo/code.md",
        "Populate expert-reviewed problem-formulation metadata for benchmark definitions.",
    ),
    "qualitative_feedback": (
        "docs/todo/code.md",
        "Add qualitative LLM-feedback criterion provenance.",
    ),
    "repeated_sampling": (
        "docs/todo/code.md",
        "Add repeated-sampling baseline reports for test-time-compute uplift",
    ),
    "sample_efficiency": (
        "docs/todo/code.md",
        "Add sample-efficiency reporting for AlphaEvolve-scale LLM proposal",
    ),
    "self_improvement": (
        "docs/todo/code.md",
        "Add self-improvement and distillation evidence boundaries for",
    ),
    "self_improvement_cadence": (
        "docs/todo/code.md",
        "Add self-improvement feedback-loop cadence and environment ROI",
    ),
    "systems_calibration": (
        "docs/todo/code.md",
        "Populate Section 3.3 result-claim calibration fields for systems reports.",
    ),
    "systems_fixtures": (
        "docs/todo/code.md",
        "Connect real systems fixtures to held-out and reference-correctness",
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
    roadmap_section_id: str,
    roadmap_phase: str,
    evidence_paths: tuple[str, ...],
    todo_ids: tuple[str, ...] = (),
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


CONTEXT_CLAIM_SPECS = (
    _claim(
        "abstract_substantial_llm_capability_uplift",
        "abstract",
        1,
        "evolutionary coding agent that substantially enhances capabilities of state-of-the-art LLMs",
        "Substantially enhance state-of-the-art LLM capability through evolutionary coding.",
        "abstract_platform",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        (
            "papers/sample_efficiency_boundary.json",
            "papers/repeated_sampling_baseline_boundary.json",
        ),
        ("sample_efficiency", "repeated_sampling"),
    ),
    _claim(
        "abstract_autonomous_llm_code_pipeline",
        "abstract",
        1,
        "orchestrates an autonomous pipeline of LLMs, whose task is to improve an algorithm by making direct changes to the code",
        "Orchestrate LLMs that improve algorithms through direct code changes.",
        "abstract_platform",
        "implemented_local",
        "documentation_truthfulness",
        "near_term",
        (
            "libreevolve/core/loop.py",
            "libreevolve/core/diff.py",
            "tests/core/test_loop.py",
        ),
    ),
    _claim(
        "abstract_continuous_evaluator_feedback",
        "abstract",
        1,
        "continuously receiving feedback from one or more evaluators",
        "Feed one or more evaluator results back into the evolutionary process.",
        "abstract_platform",
        "partially_implemented",
        "evaluation_cascade",
        "near_term",
        (
            "libreevolve/core/evaluator.py",
            "papers/evaluator_oracle_boundary.json",
        ),
        ("qualitative_feedback",),
    ),
    _claim(
        "abstract_broad_applicability",
        "abstract",
        1,
        "demonstrate the broad applicability of this approach",
        "Demonstrate broad applicability across materially different problem domains.",
        "abstract_platform",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/roadmap_representative_benchmark_portfolio_boundary.json",),
        ("benchmark_fixtures",),
    ),
    _claim(
        "abstract_datacenter_scheduling_result",
        "abstract",
        1,
        "developed a more efficient scheduling algorithm for data centers",
        "Reproduce the reported data-center scheduling improvement.",
        "abstract_results",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/systems_result_readiness_boundary.json",),
        ("systems_fixtures", "systems_calibration"),
    ),
    _claim(
        "abstract_hardware_circuit_simplification_result",
        "abstract",
        1,
        "found a functionally equivalent simplification in the circuit design of hardware accelerators",
        "Reproduce a functionally equivalent hardware-circuit simplification.",
        "abstract_results",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        (
            "papers/hardware_rewrite_artifact_boundary.json",
            "papers/systems_result_readiness_boundary.json",
        ),
        ("systems_fixtures", "systems_calibration"),
    ),
    _claim(
        "abstract_base_llm_training_acceleration_result",
        "abstract",
        1,
        "accelerated the training of the LLM underpinning AlphaEvolve itself",
        "Reproduce a measured acceleration of the platform's own base-LLM training.",
        "abstract_results",
        "not_demonstrated",
        "self_improvement",
        "longer_term",
        (
            "papers/gemini_self_training_loop_boundary.json",
            "papers/self_improvement_distillation_boundary.json",
        ),
        ("self_improvement",),
    ),
    _claim(
        "abstract_novel_provably_correct_sota_algorithms",
        "abstract",
        1,
        "discovered novel, provably correct algorithms that surpass state-of-the-art solutions",
        "Produce novel algorithms with independent correctness and state-of-the-art evidence.",
        "abstract_results",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes", "problem_formulation"),
    ),
    _claim(
        "abstract_complex_4x4_matrix_48_multiplications",
        "abstract",
        1,
        "multiply two 4 × 4 complex-valued matrices using 48 scalar multiplications",
        "Reproduce and certify the 48-multiplication complex 4x4 matrix algorithm.",
        "abstract_results",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/matrix_suite_publication_artifacts.json",),
        ("matrix_suite", "matrix_historicity"),
    ),
    _claim(
        "abstract_first_strassen_improvement_56_years",
        "abstract",
        1,
        "first improvement, after 56 years, over Strassen's algorithm",
        "Support the historical first-improvement claim with executable and source evidence.",
        "abstract_results",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/matrix_headline_historicity_artifacts.json",),
        ("matrix_historicity",),
    ),
    _claim(
        "introduction_iterative_ideation_backtracking_validation",
        "section_1",
        1,
        "prolonged process of ideation, exploration, backtracking on unpromising hypotheses, experimentation, and validation",
        "Sustain ideation, exploration, explicit backtracking, experimentation, and validation.",
        "introduction_method",
        "partially_implemented",
        "multi_objective_search",
        "near_term",
        (
            "papers/process_exhibit_boundary.json",
            "papers/controller_backtracking_boundary.json",
        ),
        ("backtracking",),
    ),
    _claim(
        "introduction_evolution_plus_llm_code_generation",
        "section_1",
        1,
        "combination of evolutionary computation and LLM-based code generation",
        "Combine evolutionary search with LLM-generated code mutations.",
        "introduction_method",
        "implemented_local",
        "documentation_truthfulness",
        "near_term",
        (
            "libreevolve/core/loop.py",
            "libreevolve/llm/ensemble.py",
            "tests/core/test_loop.py",
        ),
    ),
    _claim(
        "introduction_automatically_evaluable_problem_scope",
        "section_1",
        2,
        "discovery problems in which the candidates of discovery can be automatically evaluated",
        "Restrict autonomous search to candidates with an automated evaluator.",
        "introduction_method",
        "implemented_local",
        "evaluation_cascade",
        "near_term",
        (
            "papers/automated_evaluator_scope_boundary.json",
            "libreevolve/core/evaluator.py",
        ),
    ),
    _claim(
        "introduction_algorithmic_candidate_representation",
        "section_1",
        2,
        "represents the candidates (for example, new mathematical objects or practical heuristics) as algorithms",
        "Represent mathematical objects and practical heuristics as executable algorithms.",
        "introduction_method",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "near_term",
        (
            "papers/programmatic_representation_boundary.json",
            "papers/candidate_abstraction_boundary.json",
        ),
        ("abstraction",),
    ),
    _claim(
        "introduction_llms_generate_critique_evolve_pool",
        "section_1",
        2,
        "uses a set of LLMs to generate, critique, and evolve a pool of such algorithms",
        "Use multiple LLM roles to generate, critique, and evolve an algorithm pool.",
        "introduction_method",
        "partially_implemented",
        "prompt_context_system",
        "near_term",
        (
            "papers/critique_reviewer_pool_boundary.json",
            "libreevolve/llm/ensemble.py",
        ),
        ("critique",),
    ),
    _claim(
        "introduction_execution_and_automatic_evaluation_grounding",
        "section_1",
        2,
        "grounded using code execution and automatic evaluation",
        "Ground candidate selection in code execution and automatic evaluation.",
        "introduction_method",
        "implemented_local",
        "evaluation_cascade",
        "near_term",
        (
            "libreevolve/core/evaluator.py",
            "tests/core/test_evaluator.py",
        ),
    ),
    _claim(
        "introduction_avoid_incorrect_base_llm_suggestions",
        "section_1",
        2,
        "allows AlphaEvolve to avoid any incorrect suggestions from the base LLM",
        "Reject incorrect base-LLM suggestions with independently audited reliability.",
        "introduction_method",
        "partially_implemented",
        "evaluation_cascade",
        "near_term",
        ("papers/incorrect_suggestion_audit_boundary.json",),
        ("incorrect_filter",),
    ),
    _claim(
        "introduction_syntax_and_function_divergence",
        "section_1",
        2,
        "substantially different from the initial candidate pool in syntax and function",
        "Demonstrate evolved candidates that diverge from the initial pool in syntax and function.",
        "introduction_method",
        "partially_implemented",
        "multi_objective_search",
        "mid_term",
        ("papers/initial_pool_divergence_boundary.json",),
        ("divergence",),
    ),
    _claim(
        "introduction_algorithm_discovery_intrinsic_goal",
        "section_1",
        2,
        "discovering new algorithms is the intrinsic goal",
        "Support tasks where algorithm discovery itself is the objective.",
        "introduction_method",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "near_term",
        ("papers/candidate_abstraction_boundary.json",),
        ("abstraction",),
    ),
    _claim(
        "introduction_algorithm_discovery_instrumental_goal",
        "section_1",
        2,
        "discovering the algorithm is only an instrumental goal",
        "Support tasks where an evolved algorithm is instrumental to a downstream result.",
        "introduction_method",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "near_term",
        ("papers/candidate_abstraction_boundary.json",),
        ("abstraction",),
    ),
    _claim(
        "introduction_large_code_evolution",
        "section_1",
        2,
        "leverages state-of-the-art (SOTA) LLMs to evolve large pieces of code",
        "Demonstrate evolution of large multi-component code artifacts.",
        "introduction_method",
        "not_demonstrated",
        "candidate_workspace_fidelity",
        "longer_term",
        ("papers/codebase_scale_benchmark_boundary.json",),
        ("codebase_scale",),
    ),
    _claim(
        "introduction_manual_experimentation_out_of_scope",
        "section_1",
        2,
        "puts tasks that require manual experimentation out of our scope",
        "Keep manual-experimentation tasks outside the autonomous claim boundary.",
        "introduction_method",
        "implemented_local",
        "evaluation_cascade",
        "near_term",
        ("papers/automated_evaluator_scope_boundary.json",),
    ),
    _claim(
        "introduction_automated_metrics_across_domains",
        "section_1",
        2,
        "problems in mathematics, computer science, and system optimization typically permit automated evaluation metrics",
        "Demonstrate robust automated evaluators across mathematics, computer science, and systems optimization.",
        "introduction_method",
        "partially_implemented",
        "representative_benchmarks",
        "longer_term",
        (
            "papers/automated_evaluator_scope_boundary.json",
            "papers/roadmap_representative_benchmark_portfolio_boundary.json",
        ),
        ("automated_scope", "benchmark_fixtures"),
    ),
    _claim(
        "introduction_fourteen_matrix_sota_improvements",
        "section_1",
        3,
        "improving the SOTA for 14 matrix multiplication algorithms",
        "Reproduce and certify state-of-the-art improvements for 14 matrix algorithms.",
        "introduction_results",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/matrix_suite_publication_artifacts.json",),
        ("matrix_suite", "matrix_historicity"),
    ),
    _claim(
        "introduction_over_fifty_math_problems_best_known",
        "section_1",
        3,
        "large number (over 50) of such problems and match the best known constructions",
        "Run over 50 mathematical problems and reproduce the reported best-known matches.",
        "introduction_results",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes", "benchmark_fixtures"),
    ),
    _claim(
        "introduction_twenty_percent_math_sota_uplift",
        "section_1",
        3,
        "On ∼20% of the problems, AlphaEvolve surpasses the SOTA",
        "Reproduce the reported roughly 20 percent mathematical state-of-the-art uplift rate.",
        "introduction_results",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes",),
    ),
    _claim(
        "introduction_erdos_minimum_overlap_result",
        "section_1",
        3,
        "improvement on the Minimum Overlap Problem set by Erdős",
        "Reproduce and independently verify the Minimum Overlap Problem improvement.",
        "introduction_results",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes", "problem_formulation"),
    ),
    _claim(
        "introduction_four_google_compute_stack_results",
        "section_1",
        3,
        "four engineering problems spanning different layers of Google's compute stack",
        "Reproduce four systems results across distinct compute-stack layers.",
        "introduction_results",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/systems_result_readiness_boundary.json",),
        ("systems_fixtures", "systems_calibration"),
    ),
    _claim(
        "discussion_llm_evaluator_evolution_power",
        "section_6",
        21,
        "surprising power of combining state-of-the-art LLMs with automated evaluation metrics within an evolutionary framework",
        "Demonstrate capability uplift from the combined LLM, evaluator, and evolutionary system.",
        "discussion_capability",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        (
            "papers/sample_efficiency_boundary.json",
            "papers/repeated_sampling_baseline_boundary.json",
        ),
        ("sample_efficiency", "repeated_sampling"),
    ),
    _claim(
        "discussion_candidate_representation_modes",
        "section_6",
        21,
        "searching for the solution directly, finding a function that constructs it from scratch, or evolving a search algorithm to find it",
        "Support direct solutions, constructive functions, and evolved search algorithms as task-defined representations.",
        "discussion_capability",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "mid_term",
        (
            "papers/candidate_abstraction_boundary.json",
            "papers/programmatic_representation_boundary.json",
        ),
        ("abstraction",),
    ),
    _claim(
        "discussion_representation_biases",
        "section_6",
        21,
        "different ways comes with different biases",
        "Measure how candidate-representation choices bias search outcomes.",
        "discussion_capability",
        "not_demonstrated",
        "candidate_workspace_fidelity",
        "longer_term",
        ("papers/candidate_abstraction_bias_matrix.json",),
        ("abstraction",),
    ),
    _claim(
        "discussion_base_llm_uplift_over_repeated_sampling",
        "section_6",
        21,
        "significantly enhances the capability of the base LLM (compared to, e.g., repeated sampling)",
        "Demonstrate statistically significant capability uplift over equal-budget repeated sampling.",
        "discussion_capability",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        ("papers/repeated_sampling_baseline_boundary.json",),
        ("sample_efficiency", "repeated_sampling"),
    ),
    _claim(
        "discussion_machine_feedback_test_time_scaling",
        "section_6",
        21,
        "machine feedback is able to sustain test-time compute scaling",
        "Demonstrate sustained test-time-compute scaling from machine feedback.",
        "discussion_capability",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        (
            "papers/sample_efficiency_boundary.json",
            "papers/repeated_sampling_baseline_boundary.json",
        ),
        ("sample_efficiency", "repeated_sampling"),
    ),
    _claim(
        "discussion_distill_augmented_performance",
        "section_6",
        21,
        "distilling the AlphaEvolve-augmented performance of the base LLMs into the next generation",
        "Distill evolution-augmented capability into a later base-model generation.",
        "discussion_self_improvement",
        "not_implemented",
        "self_improvement",
        "longer_term",
        ("papers/self_improvement_distillation_boundary.json",),
        ("self_improvement",),
    ),
    _claim(
        "discussion_self_improve_infrastructure_and_base_llms",
        "section_6",
        21,
        "increase the efficiency of its own infrastructure and of (future versions of) its base LLMs",
        "Use evolved results to improve the platform infrastructure and future base models.",
        "discussion_self_improvement",
        "not_implemented",
        "self_improvement",
        "longer_term",
        ("papers/self_improvement_distillation_boundary.json",),
        ("self_improvement",),
    ),
    _claim(
        "discussion_moderate_gain_months_cadence",
        "section_6",
        21,
        "gains are moderate and the feedback loops for improving the next version of AlphaEvolve are on the order of months",
        "Measure self-improvement gain magnitude and multi-month feedback-loop cadence.",
        "discussion_self_improvement",
        "not_demonstrated",
        "self_improvement",
        "longer_term",
        ("papers/self_improvement_cadence_boundary.json",),
        ("self_improvement_cadence",),
    ),
    _claim(
        "discussion_expand_robust_evaluator_environments",
        "section_6",
        21,
        "value of setting up more environments (problems) with robust evaluation functions",
        "Create additional robust evaluator-backed problem environments.",
        "discussion_self_improvement",
        "not_implemented",
        "representative_benchmarks",
        "longer_term",
        (
            "papers/self_improvement_cadence_boundary.json",
            "papers/automated_evaluator_scope_boundary.json",
        ),
        ("self_improvement_cadence", "automated_scope"),
    ),
    _claim(
        "discussion_automated_evaluator_limitation",
        "section_6",
        21,
        "main limitation of AlphaEvolve is that it handles problems for which it is possible to devise an automated evaluator",
        "Declare automated evaluator availability as the principal autonomous-use boundary.",
        "discussion_limitation",
        "implemented_local",
        "evaluation_cascade",
        "near_term",
        ("papers/automated_evaluator_scope_boundary.json",),
    ),
    _claim(
        "discussion_llm_evaluation_not_optimized",
        "section_6",
        21,
        "does allow for LLM-provided evaluation of ideas, this is not a setting we have optimized for",
        "Support LLM-provided idea evaluation while preserving its unoptimized evidence boundary.",
        "discussion_limitation",
        "partially_implemented",
        "evaluation_cascade",
        "mid_term",
        (
            "papers/automated_evaluator_scope_boundary.json",
            "papers/qualitative_feedback_boundary.json",
        ),
        ("qualitative_feedback",),
    ),
    _claim(
        "discussion_high_level_idea_feedback_before_code",
        "section_6",
        21,
        "LLMs providing feedback on high-level ideas before transitioning to an implementation stage",
        "Add an explicit high-level-idea feedback stage before implementation search.",
        "discussion_limitation",
        "not_implemented",
        "prompt_context_system",
        "longer_term",
        (
            "papers/qualitative_feedback_boundary.json",
            "papers/candidate_abstraction_boundary.json",
        ),
        ("qualitative_feedback", "problem_formulation"),
    ),
    _claim(
        "acknowledgements_collaborator_feedback_shaped_tool",
        "acknowledgements",
        21,
        "all early users and collaborators of AlphaEvolve for their diverse use cases and insightful feedback, which shaped it into a more robust and versatile tool",
        "Support robustness and versatility claims with diverse collaborator-use-case feedback provenance.",
        "collaborator_context",
        "not_demonstrated",
        "documentation_truthfulness",
        "longer_term",
        ("papers/collaborator_feedback_provenance_boundary.json",),
        ("collaborator",),
    ),
)


EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in CONTEXT_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveContextClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveContextClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveContextClaimInventoryBoundaryIssue]


def alphaevolve_context_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Abstract, Introduction, and Discussion claim inventory."""

    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _claim_record(root_path, spec, page_texts) for spec in CONTEXT_CLAIM_SPECS
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
        "schema": ALPHAEVOLVE_CONTEXT_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "context_claim_inventory_ready": inventory_ready,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": [
            "abstract",
            "section_1",
            "section_6",
            "acknowledgements",
        ],
        "inventory_scope": {
            "included": [
                "platform, method, scope, and headline-result claims in the Abstract",
                "platform, method, scope, and headline-result claims in the Introduction",
                "capability, self-improvement, and limitation claims in the Discussion",
                "the Acknowledgements claim that collaborator feedback shaped robustness and versatility",
            ],
            "excluded": [
                "Table 1 and Sections 2.1 through 2.6, covered by the separate system-requirement inventory",
                "detailed claims in Sections 3 through 5 and Figures 4 through 14",
                "Tables 2 and 3, appendices, equations, footnotes, citations, and bibliography entries",
                "independent reviewer proof of semantic exhaustiveness",
                "AlphaEvolve production scale, result reproduction, or system parity",
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
            "This sidecar certifies a bounded claim-level inventory of 41 "
            "AlphaEvolve platform, method, scope, headline-result, capability, "
            "self-improvement, limitation, and collaborator-context claims from "
            "the Abstract, Introduction, Discussion, and one Acknowledgements "
            "sentence. It does not claim detailed Results, Ablations, Related "
            "Work, figure, table, appendix, equation, footnote, citation, or "
            "bibliography exhaustiveness; independent semantic reviewer signoff; "
            "result reproduction; production-scale evidence; or AlphaEvolve "
            "system parity."
        ),
    }


def validate_alphaevolve_context_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveContextClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_context_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveContextClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_context_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveContextClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_CONTEXT_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported context claim inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(
            _issue(
                "parity_overclaim",
                "context claim inventory must not claim AlphaEvolve parity",
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
                    f"{key} drifted from the bounded context claim inventory",
                )
            )
    if len(EXPECTED_CLAIM_IDS) != EXPECTED_CLAIM_COUNT:
        issues.append(_issue("invalid_spec_count", "context claim count must remain 41"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "context claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in CONTEXT_CLAIM_SPECS
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
            for spec in CONTEXT_CLAIM_SPECS
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
                f"{expected['missing_anchor_count']} context claim anchors were not found",
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
    if data.get("context_claim_inventory_ready") is not expected_ready:
        issues.append(
            _issue(
                "invalid_context_claim_inventory_ready",
                "context_claim_inventory_ready does not match source, reference, and ownership checks",
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "41" not in claim_boundary
        or "detailed Results" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must separate context coverage from result and parity proof",
            )
        )
    return AlphaEvolveContextClaimInventoryBoundaryValidation(
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


def render_alphaevolve_context_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_context_claim_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve context claim inventory boundary",
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
            if isinstance(payload.get("schema"), str):
                record["schema"] = payload["schema"]
            if isinstance(payload.get("boundary_status"), str):
                record["boundary_status"] = payload["boundary_status"]
            if isinstance(payload.get("claim_ready"), bool):
                record["claim_ready"] = payload["claim_ready"]
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
    list[AlphaEvolveContextClaimInventoryBoundaryIssue],
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
    return None, [_issue("invalid_shape", "context claim inventory must be an object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveContextClaimInventoryBoundaryIssue:
    return AlphaEvolveContextClaimInventoryBoundaryIssue(code=code, message=message)
