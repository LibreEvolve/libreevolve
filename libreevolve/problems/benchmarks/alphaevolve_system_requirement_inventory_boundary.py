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
    SOURCE_PDF_PATH,
    SOURCE_PAPER_ID,
    alphaevolve_source_inventory_boundary_record,
)


ALPHAEVOLVE_SYSTEM_REQUIREMENT_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_system_requirement_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "section_2_system_requirements_inventory_complete_without_whole_paper_claim_exhaustiveness"
)
EXPECTED_REQUIREMENT_COUNT = 56
IMPLEMENTED_STATUS = "implemented_local"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)


_TODO_SPECS = {
    "candidate_runner": (
        "docs/todo/code.md",
        "Extend the task-primary local candidate runner beyond host C smoke to",
    ),
    "markers": (
        "docs/todo/code.md",
        "Extend existing-codebase minimal-marker integration provenance beyond",
    ),
    "embedded_evaluate": (
        "docs/todo/code.md",
        "candidate-embedded `evaluate(eval_inputs)` entrypoint support",
    ),
    "process_exhibit": (
        "docs/todo/code.md",
        "Figure 1/Figure 2 process-exhibit report into rendered diagram",
    ),
    "task_spec": (
        "docs/todo/code.md",
        "Extend unified AlphaEvolve task-specification reports into full",
    ),
    "abstraction": (
        "docs/todo/code.md",
        "Add abstraction-choice metadata and benchmark evidence for candidate",
    ),
    "initial_program": (
        "docs/todo/code.md",
        "Add an AlphaEvolve-strict seed validity policy for complete initial",
    ),
    "codebase_scale": (
        "docs/todo/code.md",
        "Add codebase-scale benchmark evidence for multi-component generated",
    ),
    "table_1": (
        "docs/todo/code.md",
        "Keep Table 1 capability-comparison exhibit provenance scoped to row",
    ),
    "stochastic_prompt": (
        "docs/todo/code.md",
        "Add separate-source provenance for stochastic prompt-format",
    ),
    "prompt_packing": (
        "docs/todo/code.md",
        "Complete provider-token prompt section fitting beyond mutation prompts",
    ),
    "meta_prompt": (
        "docs/todo/code.md",
        "Calibrate meta-prompt scoring beyond absolute/improvement child rewards.",
    ),
    "prompt_database": (
        "docs/todo/code.md",
        "Promote the prompt-program store to a solution-database-equivalent",
    ),
    "prompt_context": (
        "docs/todo/code.md",
        "Extend structured prompt context policy beyond validated current fields.",
    ),
    "cascade": (
        "docs/todo/code.md",
        "Finish paper-facing evaluation-cascade promotion and attrition evidence.",
    ),
    "workload": (
        "docs/todo/code.md",
        "Add evaluator workload provenance for inner search and ML-training tasks.",
    ),
    "async_workers": (
        "docs/todo/code.md",
        "Complete asynchronous worker and concurrent proposal control beyond the",
    ),
    "distributed": (
        "docs/todo/code.md",
        "Complete distributed-pipeline topology evidence for controller, LLM samplers,",
    ),
    "hypothesis_tests": (
        "docs/todo/code.md",
        "Add statistical hypothesis-test gates to evaluation cascades.",
    ),
    "qualitative_feedback": (
        "docs/todo/code.md",
        "Add qualitative LLM-feedback criterion provenance.",
    ),
    "expensive_budget": (
        "docs/todo/code.md",
        "Add unified expensive-evaluation compute budgets and resumable state.",
    ),
    "accelerator_budget": (
        "docs/todo/code.md",
        "Add accelerator and worker budget stops plus budget resume state.",
    ),
    "descriptors": (
        "docs/todo/code.md",
        "Promote MAP-Elites descriptor modeling beyond insertion-time TF-IDF snapshot coordinates.",
    ),
    "multi_objective": (
        "docs/todo/code.md",
        "Promote multi-objective overlays to primary archive optimization.",
    ),
    "metric_diversity": (
        "docs/todo/code.md",
        "Extend metric-diverse inspiration selection provenance into benchmark",
    ),
    "evolutionary_database": (
        "docs/todo/code.md",
        "Replace bounded run-local resurfacing indexes with a durable",
    ),
    "sampling_balance": (
        "docs/todo/code.md",
        "Extend exploration/exploitation sampling-balance reports into calibrated",
    ),
    "figure_3": (
        "docs/todo/code.md",
        "Add Figure 3 supervised-learning example exhibit provenance.",
    ),
    "adaptive_mutation": (
        "docs/todo/code.md",
        "Calibrate and evaluate the adaptive mutation-output policy.",
    ),
    "model_mix": (
        "docs/todo/code.md",
        "Extend first-class Google/Gemini support to live AlphaEvolve model-mix",
    ),
    "sample_efficiency": (
        "docs/todo/code.md",
        "Add sample-efficiency reporting for AlphaEvolve-scale LLM proposal",
    ),
    "role_scheduler": (
        "docs/todo/code.md",
        "Promote role-scoped LLM routing from shared-bandit audit evidence to",
    ),
}


def _requirement(
    requirement_id: str,
    source_span_id: str,
    source_page: int,
    source_anchor: str,
    requirement: str,
    category: str,
    implementation_status: str,
    roadmap_section_id: str,
    roadmap_phase: str,
    evidence_paths: tuple[str, ...],
    todo_ids: tuple[str, ...] = (),
) -> dict[str, Any]:
    return {
        "requirement_id": requirement_id,
        "source_span_id": source_span_id,
        "source_page": source_page,
        "source_anchor": source_anchor,
        "requirement": requirement,
        "category": category,
        "implementation_status": implementation_status,
        "roadmap_section_id": roadmap_section_id,
        "roadmap_phase": roadmap_phase,
        "evidence_paths": evidence_paths,
        "todo_ids": todo_ids,
    }


SYSTEM_REQUIREMENT_SPECS = (
    _requirement(
        "table1_entire_code_file",
        "table_1",
        2,
        "evolves entire code file",
        "Evolve an entire code file rather than only one function.",
        "table_1_capability",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "near_term",
        (
            "papers/table1_capability_exhibit_boundary.json",
            "libreevolve/core/candidate.py",
            "tests/core/test_candidate.py",
        ),
        ("codebase_scale", "table_1"),
    ),
    _requirement(
        "table1_hundreds_of_lines",
        "table_1",
        2,
        "evolves up to hundreds of lines of code",
        "Demonstrate evolution of programs containing up to hundreds of lines.",
        "table_1_capability",
        "not_demonstrated",
        "candidate_workspace_fidelity",
        "longer_term",
        (
            "papers/table1_capability_exhibit_boundary.json",
            "papers/codebase_scale_benchmark_boundary.json",
            "tests/test_codebase_scale_benchmark_boundary.py",
        ),
        ("codebase_scale", "table_1"),
    ),
    _requirement(
        "table1_any_language",
        "table_1",
        2,
        "evolves any language",
        "Support task-defined candidate languages rather than a Python-first boundary.",
        "table_1_capability",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "longer_term",
        (
            "papers/candidate_language_runner_boundary.json",
            "libreevolve/core/evaluator.py",
            "tests/test_candidate_language_runner_boundary.py",
        ),
        ("candidate_runner", "table_1"),
    ),
    _requirement(
        "table1_expensive_parallel_accelerated_evaluation",
        "table_1",
        2,
        "can evaluate for hours, in parallel, on accelerators",
        "Support long-running parallel evaluation on accelerator-backed workers.",
        "table_1_capability",
        "partially_implemented",
        "async_resumable_runtime",
        "mid_term",
        (
            "papers/expensive_evaluation_budget_boundary.json",
            "papers/parallel_evaluation_readiness_boundary.json",
            "tests/test_expensive_evaluation_budget_boundary.py",
        ),
        ("accelerator_budget", "expensive_budget", "table_1"),
    ),
    _requirement(
        "table1_thousands_of_samples_suffice",
        "table_1",
        2,
        "thousands of LLM samples suffice",
        "Measure AlphaEvolve-scale proposal sample efficiency.",
        "table_1_capability",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        (
            "papers/sample_efficiency_boundary.json",
            "tests/test_sample_efficiency_boundary.py",
        ),
        ("sample_efficiency", "table_1"),
    ),
    _requirement(
        "table1_benefits_from_sota_models",
        "table_1",
        2,
        "benefits from SOTA LLMs",
        "Demonstrate improved search outcomes from stronger language models.",
        "table_1_capability",
        "not_demonstrated",
        "backend_scheduling_and_critique",
        "longer_term",
        (
            "papers/fast_strong_model_mix_boundary.json",
            "tests/test_fast_strong_model_mix_boundary.py",
        ),
        ("model_mix", "table_1"),
    ),
    _requirement(
        "table1_rich_context_and_feedback",
        "table_1",
        2,
        "rich context and feedback in prompts",
        "Build mutation prompts from rich task context, prior programs, and feedback.",
        "table_1_capability",
        "partially_implemented",
        "prompt_context_system",
        "near_term",
        (
            "papers/prompt_section_packing_boundary.json",
            "libreevolve/core/prompt.py",
            "tests/test_prompt_section_packing_boundary.py",
        ),
        ("prompt_context", "prompt_packing", "table_1"),
    ),
    _requirement(
        "table1_multiple_metrics",
        "table_1",
        2,
        "can simultaneously optimize multiple metrics",
        "Optimize multiple metrics as primary search objectives.",
        "table_1_capability",
        "partially_implemented",
        "multi_objective_search",
        "near_term",
        (
            "papers/objective_archive_boundary.json",
            "libreevolve/core/database.py",
            "tests/test_objective_archive_boundary.py",
        ),
        ("multi_objective", "table_1"),
    ),
    _requirement(
        "section2_autonomous_pipeline",
        "section_2",
        3,
        "orchestrates an autonomous pipeline of computations including queries to LLMs",
        "Orchestrate an autonomous computation and LLM-query pipeline.",
        "platform_overview",
        IMPLEMENTED_STATUS,
        "async_resumable_runtime",
        "near_term",
        (
            "papers/process_exhibit_boundary.json",
            "libreevolve/core/loop.py",
            "tests/core/test_loop.py",
        ),
    ),
    _requirement(
        "section2_user_specified_task",
        "section_2",
        3,
        "produces algorithms that address a user-specified task",
        "Accept a user-specified task and evolve executable candidate programs for it.",
        "platform_overview",
        IMPLEMENTED_STATUS,
        "candidate_workspace_fidelity",
        "near_term",
        (
            "papers/task_specification_boundary.json",
            "libreevolve/problems/loader.py",
            "tests/core/test_loader.py",
        ),
    ),
    _requirement(
        "section2_evolutionary_metric_improvement",
        "section_2",
        3,
        "gradually develops programs that improve the score on the automated evaluation metrics",
        "Use an evolutionary loop to improve automated evaluation scores.",
        "platform_overview",
        IMPLEMENTED_STATUS,
        "multi_objective_search",
        "near_term",
        (
            "papers/process_exhibit_boundary.json",
            "libreevolve/core/loop.py",
            "tests/core/test_loop.py",
        ),
    ),
    _requirement(
        "figure1_human_inputs",
        "figure_1",
        3,
        "sets evaluation criteria, provides initial solution and optional background knowledge",
        "Represent evaluation criteria, an initial solution, and optional background knowledge as task inputs.",
        "platform_overview",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "near_term",
        (
            "papers/process_exhibit_boundary.json",
            "papers/task_specification_boundary.json",
            "tests/test_task_specification_boundary.py",
        ),
        ("task_spec", "process_exhibit"),
    ),
    _requirement(
        "figure2_expanded_loop",
        "figure_2",
        4,
        "user provides an initial program (with components to evolve marked), evaluation code, and optional configurations",
        "Run the sample-prompt-generate-apply-evaluate-database loop over user task artifacts.",
        "platform_overview",
        IMPLEMENTED_STATUS,
        "async_resumable_runtime",
        "near_term",
        (
            "papers/process_exhibit_boundary.json",
            "libreevolve/core/loop.py",
            "tests/test_process_exhibit_boundary.py",
        ),
    ),
    _requirement(
        "task_scalar_metric_mapping",
        "section_2_1",
        3,
        "mapping a solution to a set of scalar evaluation metrics",
        "Map each candidate to finite scalar metrics that are maximized by convention.",
        "task_specification",
        IMPLEMENTED_STATUS,
        "evaluation_cascade",
        "near_term",
        (
            "papers/automated_evaluator_scope_boundary.json",
            "libreevolve/population/program.py",
            "tests/population/test_program.py",
        ),
    ),
    _requirement(
        "task_metric_maximization_convention",
        "section_2_1",
        3,
        "By convention, these metrics are maximized.",
        "Use maximization as the default metric direction while supporting explicit minimization.",
        "task_specification",
        IMPLEMENTED_STATUS,
        "evaluation_cascade",
        "near_term",
        (
            "libreevolve/problems/loader.py",
            "tests/core/test_loader.py",
        ),
    ),
    _requirement(
        "task_fixed_evaluate_signature",
        "section_2_1",
        4,
        "evaluate, with a fixed input/output signature, returning a dictionary of scalars",
        "Support the paper-style evaluate entrypoint with a fixed dictionary-of-scalars contract.",
        "task_specification",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "near_term",
        (
            "papers/task_specification_boundary.json",
            "libreevolve/core/evaluator.py",
            "tests/core/test_evaluator.py",
        ),
        ("embedded_evaluate", "task_spec"),
    ),
    _requirement(
        "task_evaluation_workload_range",
        "section_2_1",
        4,
        "executing this function may take only seconds on a single device or spawn extensive computations",
        "Represent and audit simple through extensive evaluator workloads.",
        "task_specification",
        "partially_implemented",
        "evaluation_cascade",
        "mid_term",
        (
            "papers/expensive_evaluation_budget_boundary.json",
            "libreevolve/core/evaluator.py",
            "tests/test_expensive_evaluation_budget_boundary.py",
        ),
        ("workload", "expensive_budget"),
    ),
    _requirement(
        "task_multiple_marked_components",
        "section_2_1",
        4,
        "support evolving multiple components across a codebase",
        "Evolve multiple marked components across a task workspace.",
        "task_specification",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "near_term",
        (
            "papers/existing_codebase_integration_boundary.json",
            "libreevolve/core/candidate.py",
            "tests/test_existing_codebase_integration_boundary.py",
        ),
        ("markers", "codebase_scale"),
    ),
    _requirement(
        "task_minimal_marker_integration",
        "section_2_1",
        4,
        "requiring only minimal changes, simply by adding special markers",
        "Integrate existing codebases through evolve-block markers with minimal source changes.",
        "task_specification",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "near_term",
        (
            "papers/existing_codebase_integration_boundary.json",
            "libreevolve/core/candidate.py",
            "tests/core/test_candidate.py",
        ),
        ("markers",),
    ),
    _requirement(
        "task_evolved_blocks_and_skeleton",
        "section_2_1",
        5,
        "the rest of the code forms a skeleton that ties the evolved pieces together",
        "Keep non-evolved code as a stable skeleton that invokes evolved blocks from evaluation.",
        "task_specification",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "near_term",
        (
            "papers/task_specification_boundary.json",
            "libreevolve/core/candidate.py",
            "tests/core/test_candidate.py",
        ),
        ("embedded_evaluate", "markers"),
    ),
    _requirement(
        "task_complete_initial_program",
        "section_2_1",
        5,
        "this initial implementation must be complete",
        "Require a complete evaluator-valid initial program for AlphaEvolve-strict runs.",
        "task_specification",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "near_term",
        (
            "papers/initial_program_validity_boundary.json",
            "libreevolve/core/loop.py",
            "tests/test_initial_program_validity_boundary.py",
        ),
        ("initial_program",),
    ),
    _requirement(
        "task_raw_representation_abstraction",
        "section_2_1",
        5,
        "evolve the solution in raw string representation",
        "Allow a task to select raw solution representation as the evolved abstraction.",
        "task_specification",
        "not_implemented",
        "candidate_workspace_fidelity",
        "mid_term",
        (
            "papers/candidate_abstraction_boundary.json",
            "tests/test_candidate_abstraction_boundary.py",
        ),
        ("abstraction",),
    ),
    _requirement(
        "task_constructor_function_abstraction",
        "section_2_1",
        5,
        "evolve a function of a definite form that specifies how to construct the solution from scratch",
        "Allow constructor-function candidate abstractions.",
        "task_specification",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "mid_term",
        (
            "papers/candidate_abstraction_boundary.json",
            "libreevolve/problems/examples/circle_packing/initial_programs/seed.py",
            "tests/test_candidate_abstraction_boundary.py",
        ),
        ("abstraction",),
    ),
    _requirement(
        "task_bespoke_search_abstraction",
        "section_2_1",
        5,
        "evolve a bespoke search algorithm to find the solution within some fixed compute budget",
        "Allow budgeted bespoke-search algorithms as candidate abstractions.",
        "task_specification",
        "partially_implemented",
        "candidate_workspace_fidelity",
        "mid_term",
        (
            "papers/candidate_abstraction_boundary.json",
            "papers/expensive_evaluation_budget_boundary.json",
            "tests/test_candidate_abstraction_boundary.py",
        ),
        ("abstraction", "expensive_budget"),
    ),
    _requirement(
        "task_solution_search_coevolution",
        "section_2_1",
        5,
        "co-evolve intermediate solutions and search algorithms together",
        "Co-evolve intermediate solutions with search algorithms tailored to improve them.",
        "task_specification",
        "not_implemented",
        "candidate_workspace_fidelity",
        "longer_term",
        (
            "papers/candidate_abstraction_boundary.json",
            "tests/test_candidate_abstraction_boundary.py",
        ),
        ("abstraction",),
    ),
    _requirement(
        "task_problem_specific_abstraction_choice",
        "section_2_1",
        5,
        "different levels of abstraction work better for different problems",
        "Select and justify the candidate abstraction for each problem.",
        "task_specification",
        "not_implemented",
        "candidate_workspace_fidelity",
        "mid_term",
        (
            "papers/candidate_abstraction_boundary.json",
            "papers/candidate_abstraction_bias_matrix.json",
            "tests/test_candidate_abstraction_boundary.py",
        ),
        ("abstraction",),
    ),
    _requirement(
        "task_symmetry_guided_abstraction_bias",
        "section_2_1",
        5,
        (
            "for problems with highly symmetric solutions it is advantageous "
            "to evolve constructor functions"
        ),
        (
            "Use solution symmetry evidence to prefer constructor functions and "
            "non-symmetry evidence to prefer bespoke search algorithms."
        ),
        "task_specification",
        "not_implemented",
        "candidate_workspace_fidelity",
        "mid_term",
        (
            "papers/candidate_abstraction_boundary.json",
            "papers/candidate_abstraction_bias_matrix.json",
            "tests/test_candidate_abstraction_bias.py",
        ),
        ("abstraction",),
    ),
    _requirement(
        "prompt_long_context_customization",
        "section_2_2",
        5,
        "supports various types of customization and providing long contexts as part of the primary evolution prompt",
        "Support configurable long-context primary evolution prompts.",
        "prompt_sampling",
        "partially_implemented",
        "prompt_context_system",
        "near_term",
        (
            "papers/prompt_section_packing_boundary.json",
            "libreevolve/core/prompt.py",
            "tests/test_prompt_section_packing_boundary.py",
        ),
        ("prompt_context", "prompt_packing"),
    ),
    _requirement(
        "prompt_prior_solutions_and_instructions",
        "section_2_2",
        5,
        "multiple previously discovered solutions sampled from the program database",
        "Include sampled prior solutions and mutation instructions in primary prompts.",
        "prompt_sampling",
        IMPLEMENTED_STATUS,
        "prompt_context_system",
        "near_term",
        (
            "libreevolve/core/prompt.py",
            "libreevolve/core/database.py",
            "tests/core/test_prompt.py",
        ),
    ),
    _requirement(
        "prompt_explicit_context",
        "section_2_2",
        5,
        "fixed human-written instructions, equations, code snippets, or relevant literature",
        "Accept explicit human instructions, equations, code snippets, and literature context.",
        "prompt_sampling",
        "partially_implemented",
        "prompt_context_system",
        "near_term",
        (
            "papers/prompt_section_packing_boundary.json",
            "libreevolve/core/prompt.py",
            "tests/core/test_prompt.py",
        ),
        ("prompt_context", "prompt_packing"),
    ),
    _requirement(
        "prompt_stochastic_formatting",
        "section_2_2",
        5,
        "template placeholders with human-provided alternatives for increased diversity",
        "Sample human-provided prompt alternatives from configured probability distributions.",
        "prompt_sampling",
        "partially_implemented",
        "prompt_context_system",
        "near_term",
        (
            "papers/stochastic_prompt_format_boundary.json",
            "libreevolve/core/prompt.py",
            "tests/test_stochastic_prompt_format_boundary.py",
        ),
        ("stochastic_prompt",),
    ),
    _requirement(
        "prompt_rendered_evaluation_results",
        "section_2_2",
        5,
        "Rendered evaluation results",
        "Render candidate programs, evaluator outputs, and scores into prompt context.",
        "prompt_sampling",
        "partially_implemented",
        "prompt_context_system",
        "near_term",
        (
            "papers/program_output_boundary.json",
            "libreevolve/core/prompt.py",
            "tests/test_program_output_boundary.py",
        ),
        ("prompt_context",),
    ),
    _requirement(
        "prompt_meta_evolution_database",
        "section_2_2",
        5,
        "Meta prompt evolution",
        "Generate and co-evolve prompt instructions and context in a separate prompt database.",
        "prompt_sampling",
        "partially_implemented",
        "prompt_context_system",
        "mid_term",
        (
            "papers/prompt_database_parity_boundary.json",
            "papers/meta_prompt_scoring_boundary.json",
            "tests/test_prompt_database_parity_boundary.py",
        ),
        ("meta_prompt", "prompt_database"),
    ),
    _requirement(
        "generation_model_agnostic",
        "section_2_3",
        5,
        "Although AlphaEvolve is model-agnostic",
        "Route generation through interchangeable model backends.",
        "creative_generation",
        IMPLEMENTED_STATUS,
        "backend_scheduling_and_critique",
        "near_term",
        (
            "libreevolve/llm/backend_registry.py",
            "libreevolve/llm/base.py",
            "tests/llm/test_backends.py",
        ),
    ),
    _requirement(
        "generation_stronger_model_effect",
        "section_2_3",
        5,
        "performs increasingly better as the underlying LLM improves",
        "Measure search-quality improvement as the underlying model improves.",
        "creative_generation",
        "not_demonstrated",
        "backend_scheduling_and_critique",
        "longer_term",
        (
            "papers/fast_strong_model_mix_boundary.json",
            "tests/test_fast_strong_model_mix_boundary.py",
        ),
        ("model_mix",),
    ),
    _requirement(
        "figure3_supervised_pipeline_exhibit",
        "figure_3",
        6,
        "Illustrative example of applying AlphaEvolve to evolving a supervised learning pipeline",
        "Reproduce the Figure 3 marked-file, assembled-prompt, generated-diff, and evaluator flow.",
        "creative_generation",
        "not_demonstrated",
        "representative_benchmarks",
        "longer_term",
        (
            "papers/figure3_supervised_exhibit_boundary.json",
            "tests/test_figure3_supervised_exhibit_boundary.py",
        ),
        ("figure_3",),
    ),
    _requirement(
        "generation_search_replace_blocks",
        "section_2_3",
        7,
        "sequence of diff blocks in a specific format",
        "Request and apply canonical SEARCH/REPLACE diff blocks.",
        "creative_generation",
        IMPLEMENTED_STATUS,
        "candidate_workspace_fidelity",
        "near_term",
        (
            "libreevolve/core/diff.py",
            "libreevolve/core/candidate.py",
            "tests/core/test_diff.py",
        ),
    ),
    _requirement(
        "generation_direct_full_code_output",
        "section_2_3",
        7,
        "output the entire code block directly",
        "Allow direct full-code replacement instead of localized diffs.",
        "creative_generation",
        IMPLEMENTED_STATUS,
        "candidate_workspace_fidelity",
        "near_term",
        (
            "papers/adaptive_mutation_mode_boundary.json",
            "libreevolve/core/candidate.py",
            "tests/test_adaptive_mutation_mode_boundary.py",
        ),
    ),
    _requirement(
        "generation_model_ensemble",
        "section_2_3",
        7,
        "employs an ensemble of large language models",
        "Generate proposals through a configurable ensemble of language models.",
        "creative_generation",
        IMPLEMENTED_STATUS,
        "backend_scheduling_and_critique",
        "near_term",
        (
            "libreevolve/llm/ensemble.py",
            "tests/llm/test_ensemble.py",
        ),
    ),
    _requirement(
        "generation_fast_strong_model_mix",
        "section_2_3",
        7,
        "combination of Gemini 2.0 Flash and Gemini 2.0 Pro",
        "Use and validate a high-throughput and high-capability model mix.",
        "creative_generation",
        "partially_implemented",
        "backend_scheduling_and_critique",
        "mid_term",
        (
            "papers/fast_strong_model_mix_boundary.json",
            "papers/llm_role_scheduler_boundary.json",
            "papers/gemini_provider_parity_boundary.json",
            "tests/test_fast_strong_model_mix_boundary.py",
        ),
        ("model_mix", "role_scheduler"),
    ),
    _requirement(
        "evaluation_every_proposal",
        "section_2_4",
        7,
        "each new solution proposed by the LLMs is automatically evaluated",
        "Automatically execute the evaluator for every accepted mutation payload.",
        "evaluation",
        IMPLEMENTED_STATUS,
        "evaluation_cascade",
        "near_term",
        (
            "libreevolve/core/evaluator.py",
            "libreevolve/core/loop.py",
            "tests/core/test_evaluator.py",
        ),
    ),
    _requirement(
        "evaluation_increasing_difficulty_cascade",
        "section_2_4",
        7,
        "ensembles of test cases of increasing difficulty",
        "Promote promising candidates through increasingly difficult evaluation stages.",
        "evaluation",
        "partially_implemented",
        "evaluation_cascade",
        "near_term",
        (
            "papers/evaluation_cascade_boundary.json",
            "papers/cascade_hypothesis_test_boundary.json",
            "tests/test_evaluation_cascade_boundary.py",
        ),
        ("cascade", "hypothesis_tests"),
    ),
    _requirement(
        "evaluation_llm_generated_feedback",
        "section_2_4",
        8,
        "graded using separate LLM calls and added to the dictionary of scores",
        "Use calibrated LLM graders as score signals or candidate-discard criteria.",
        "evaluation",
        "partially_implemented",
        "evaluation_cascade",
        "mid_term",
        (
            "papers/qualitative_feedback_boundary.json",
            "libreevolve/core/feedback.py",
            "tests/test_qualitative_feedback_boundary.py",
        ),
        ("qualitative_feedback",),
    ),
    _requirement(
        "evaluation_order_hundred_compute_hours_per_candidate",
        "section_2_4",
        8,
        "on the order of 100 compute-hours to evaluate any new solution",
        "Account for and bound roughly 100 compute-hours of work per candidate.",
        "evaluation",
        "partially_implemented",
        "async_resumable_runtime",
        "mid_term",
        (
            "papers/expensive_evaluation_budget_boundary.json",
            "papers/parallel_evaluation_readiness_boundary.json",
            "tests/test_expensive_evaluation_budget_boundary.py",
        ),
        ("expensive_budget", "accelerator_budget"),
    ),
    _requirement(
        "evaluation_sample_efficiency_enables_expensive_evaluation",
        "section_2_4",
        8,
        (
            "sample efficiency of AlphaEvolve makes it feasible to spend on "
            "the order of 100 compute-hours"
        ),
        (
            "Demonstrate that proposal sample efficiency makes roughly 100 "
            "compute-hours of evaluation per candidate feasible."
        ),
        "evaluation",
        "not_demonstrated",
        "sample_efficiency",
        "mid_term",
        (
            "papers/sample_efficiency_boundary.json",
            "papers/expensive_evaluation_budget_boundary.json",
            "tests/test_sample_efficiency_boundary.py",
        ),
        ("sample_efficiency",),
    ),
    _requirement(
        "evaluation_async_cluster_parallelism",
        "section_2_4",
        8,
        "distribute this work through asynchronous calls to an evaluation cluster",
        "Parallelize evaluator work through asynchronous distributed workers.",
        "evaluation",
        "partially_implemented",
        "async_resumable_runtime",
        "mid_term",
        (
            "papers/parallel_evaluation_readiness_boundary.json",
            "libreevolve/core/async_evaluator.py",
            "tests/test_parallel_evaluation_readiness_boundary.py",
        ),
        ("async_workers", "distributed", "accelerator_budget"),
    ),
    _requirement(
        "evaluation_multiple_user_scores",
        "section_2_4",
        8,
        "allows for optimizing multiple user-provided scores",
        "Treat multiple user-provided metrics as first-class search objectives.",
        "evaluation",
        "partially_implemented",
        "multi_objective_search",
        "near_term",
        (
            "papers/objective_archive_boundary.json",
            "libreevolve/core/database.py",
            "tests/test_objective_archive_boundary.py",
        ),
        ("multi_objective",),
    ),
    _requirement(
        "evaluation_multi_metric_single_target_uplift",
        "section_2_4",
        8,
        "optimizing for multiple metrics often improves results for the single target metric",
        "Demonstrate that multi-metric optimization improves a designated target metric.",
        "evaluation",
        "not_demonstrated",
        "multi_objective_search",
        "longer_term",
        (
            "papers/objective_archive_boundary.json",
            "papers/metric_diverse_prompt_boundary.json",
            "tests/test_objective_archive_boundary.py",
        ),
        ("multi_objective", "metric_diversity"),
    ),
    _requirement(
        "evaluation_metric_diverse_prompting",
        "section_2_4",
        8,
        "programs excelling under different evaluation criteria often possess distinct structures or logic",
        "Use metric-diverse high-performing programs as prompt inspirations.",
        "evaluation",
        "partially_implemented",
        "multi_objective_search",
        "near_term",
        (
            "papers/metric_diverse_prompt_boundary.json",
            "libreevolve/core/database.py",
            "tests/test_metric_diverse_prompt_boundary.py",
        ),
        ("metric_diversity",),
    ),
    _requirement(
        "evolution_results_attached_to_solutions",
        "section_2_5",
        8,
        "solutions with evaluation results (scores and program outputs) attached to them",
        "Persist scores and evaluator program outputs with candidate records.",
        "evolution",
        IMPLEMENTED_STATUS,
        "multi_objective_search",
        "near_term",
        (
            "papers/program_output_boundary.json",
            "libreevolve/population/program.py",
            "tests/test_program_output_boundary.py",
        ),
    ),
    _requirement(
        "evolution_database_resurfacing",
        "section_2_5",
        8,
        "primary goal of which is to optimally resurface previously explored ideas",
        "Resurface prior ideas by quality, diversity, feedback, output, and lineage evidence.",
        "evolution",
        "partially_implemented",
        "multi_objective_search",
        "mid_term",
        (
            "papers/evolutionary_database_boundary.json",
            "libreevolve/core/database.py",
            "tests/test_evolutionary_database_boundary.py",
        ),
        ("evolutionary_database",),
    ),
    _requirement(
        "evolution_exploration_exploitation_balance",
        "section_2_5",
        8,
        "balancing exploration and exploitation",
        "Balance exploitation of strong programs with diversity-preserving exploration.",
        "evolution",
        "partially_implemented",
        "multi_objective_search",
        "near_term",
        (
            "papers/sampling_balance_boundary.json",
            "libreevolve/population/sampling.py",
            "tests/test_sampling_balance_boundary.py",
        ),
        ("sampling_balance",),
    ),
    _requirement(
        "evolution_map_elites_and_islands",
        "section_2_5",
        8,
        "inspired by a combination of the MAP elites algorithm",
        "Combine a MAP-Elites quality-diversity archive with island populations.",
        "evolution",
        IMPLEMENTED_STATUS,
        "multi_objective_search",
        "near_term",
        (
            "papers/map_elites_descriptor_boundary.json",
            "libreevolve/population/map_elites.py",
            "libreevolve/population/islands.py",
            "tests/population/test_islands.py",
        ),
    ),
    _requirement(
        "distributed_asyncio_dependency_pipeline",
        "section_2_6",
        8,
        "implemented as an asynchronous computational pipeline (using the asyncio Python library)",
        "Run concurrent pipeline tasks that await unfinished dependencies.",
        "distributed_pipeline",
        "partially_implemented",
        "async_resumable_runtime",
        "mid_term",
        (
            "papers/distributed_pipeline_topology_boundary.json",
            "libreevolve/core/async_sampler.py",
            "libreevolve/core/async_evaluator.py",
            "tests/test_distributed_pipeline_topology_boundary.py",
        ),
        ("async_workers", "distributed"),
    ),
    _requirement(
        "distributed_controller_sampler_evaluator_nodes",
        "section_2_6",
        8,
        "comprises a controller, LLM samplers, and evaluation nodes",
        "Expose controller, LLM-sampler, and evaluator-node topology with worker ownership.",
        "distributed_pipeline",
        "partially_implemented",
        "async_resumable_runtime",
        "mid_term",
        (
            "papers/distributed_pipeline_topology_boundary.json",
            "libreevolve/core/loop.py",
            "tests/test_distributed_pipeline_topology_boundary.py",
        ),
        ("distributed",),
    ),
    _requirement(
        "distributed_throughput_budget_optimization",
        "section_2_6",
        8,
        "optimized for throughput (rather than the speed of any one particular computation)",
        "Optimize aggregate proposal/evaluation throughput under an overall compute budget.",
        "distributed_pipeline",
        "partially_implemented",
        "async_resumable_runtime",
        "mid_term",
        (
            "papers/distributed_pipeline_topology_boundary.json",
            "papers/expensive_evaluation_budget_boundary.json",
            "tests/test_distributed_pipeline_topology_boundary.py",
        ),
        ("distributed", "expensive_budget", "accelerator_budget"),
    ),
)

EXPECTED_REQUIREMENT_IDS = tuple(
    spec["requirement_id"] for spec in SYSTEM_REQUIREMENT_SPECS
)


@dataclass(frozen=True)
class AlphaEvolveSystemRequirementInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveSystemRequirementInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    requirement_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveSystemRequirementInventoryBoundaryIssue]


def alphaevolve_system_requirement_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Table 1 and Section 2 system-requirement inventory."""

    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _requirement_record(root_path, spec, page_texts)
        for spec in SYSTEM_REQUIREMENT_SPECS
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
        and len(records) == EXPECTED_REQUIREMENT_COUNT
        and missing_anchor_count == 0
        and missing_reference_count == 0
        and todo_owned_gap_count == implementation_gap_count
    )
    return {
        "schema": ALPHAEVOLVE_SYSTEM_REQUIREMENT_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "section_2_requirement_inventory_ready": inventory_ready,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "inventory_scope": {
            "included": [
                "all eight AlphaEvolve capability rows in Table 1",
                "implementation-bearing prose requirements in Sections 2.1 through 2.6",
                "system behavior shown or stated in Figures 1, 2, and 3",
            ],
            "excluded": [
                "Introduction claims outside Table 1 and Section 2",
                "Sections 3 through 6, appendices, and result reproduction claims",
                "equation, footnote, citation, and bibliography-level extraction",
                "independent reviewer proof that the bounded requirement decomposition is semantically exhaustive",
                "AlphaEvolve production scale, benchmark results, or system parity",
            ],
        },
        "requirement_count": len(records),
        "expected_requirement_count": EXPECTED_REQUIREMENT_COUNT,
        "category_counts": dict(sorted(category_counts.items())),
        "implementation_status_counts": dict(sorted(status_counts.items())),
        "implemented_local_count": status_counts[IMPLEMENTED_STATUS],
        "implementation_gap_count": implementation_gap_count,
        "todo_owned_gap_count": todo_owned_gap_count,
        "missing_anchor_count": missing_anchor_count,
        "missing_reference_count": missing_reference_count,
        "requirement_records": records,
        "claim_boundary": (
            "This sidecar certifies a bounded claim-level inventory of 56 "
            "implementation-bearing AlphaEvolve requirements from Table 1, "
            "Sections 2.1 through 2.6, and Figures 1 through 3. Local status "
            "labels distinguish implemented behavior from partial, missing, "
            "and undemonstrated claims. It does not claim whole-paper claim-level "
            "exhaustiveness, semantic reviewer signoff, benchmark reproduction, "
            "production-scale evidence, or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_system_requirement_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveSystemRequirementInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_system_requirement_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveSystemRequirementInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_system_requirement_inventory_boundary_record(root)
    issues: list[AlphaEvolveSystemRequirementInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_SYSTEM_REQUIREMENT_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported system requirement inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(_issue("parity_overclaim", "system requirement inventory must not claim AlphaEvolve parity"))
    for key in (
        "source_artifact",
        "source_inventory_schema",
        "source_inventory_span_count",
        "inventory_scope",
        "requirement_count",
        "expected_requirement_count",
        "category_counts",
        "implementation_status_counts",
        "implemented_local_count",
        "implementation_gap_count",
        "todo_owned_gap_count",
        "missing_anchor_count",
        "missing_reference_count",
        "requirement_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from the bounded system requirement inventory"))
    if len(EXPECTED_REQUIREMENT_IDS) != EXPECTED_REQUIREMENT_COUNT:
        issues.append(_issue("invalid_spec_count", "system requirement spec count must remain 56"))
    if len(set(EXPECTED_REQUIREMENT_IDS)) != len(EXPECTED_REQUIREMENT_IDS):
        issues.append(_issue("duplicate_requirement_id", "system requirement ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in SYSTEM_REQUIREMENT_SPECS
            if spec["source_span_id"] not in EXPECTED_NAMED_SOURCE_SPAN_IDS
        }
    )
    if unknown_spans:
        issues.append(_issue("unknown_source_span", f"unknown source spans: {', '.join(unknown_spans)}"))
    unsupported_statuses = sorted(
        {
            spec["implementation_status"]
            for spec in SYSTEM_REQUIREMENT_SPECS
            if spec["implementation_status"]
            not in INCOMPLETE_STATUSES | {IMPLEMENTED_STATUS}
        }
    )
    if unsupported_statuses:
        issues.append(_issue("unsupported_implementation_status", f"unsupported statuses: {', '.join(unsupported_statuses)}"))
    unowned_gaps = sorted(
        record["requirement_id"]
        for record in expected["requirement_records"]
        if record["implementation_status"] != IMPLEMENTED_STATUS
        and not record["active_todo_refs"]
    )
    if unowned_gaps:
        issues.append(_issue("unowned_implementation_gap", f"requirements lack active TODO ownership: {', '.join(unowned_gaps)}"))
    if not expected["source_artifact"]["identity_ok"]:
        issues.append(_issue("source_pdf_identity_mismatch", "retained AlphaEvolve PDF identity does not match the pinned source"))
    if expected["missing_anchor_count"]:
        issues.append(_issue("missing_source_anchor", f"{expected['missing_anchor_count']} requirement anchors were not found on their pinned pages"))
    if expected["missing_reference_count"]:
        issues.append(_issue("missing_local_reference", f"{expected['missing_reference_count']} evidence or TODO references are missing or stale"))
    expected_ready = (
        expected["source_artifact"]["identity_ok"]
        and expected["requirement_count"] == EXPECTED_REQUIREMENT_COUNT
        and expected["missing_anchor_count"] == 0
        and expected["missing_reference_count"] == 0
        and expected["todo_owned_gap_count"] == expected["implementation_gap_count"]
    )
    if data.get("section_2_requirement_inventory_ready") is not expected_ready:
        issues.append(_issue("invalid_section_2_requirement_inventory_ready", "section_2_requirement_inventory_ready does not match source, reference, and ownership checks"))
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "56 implementation-bearing AlphaEvolve requirements" not in claim_boundary
        or "whole-paper claim-level exhaustiveness" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded Section 2 coverage from whole-paper and parity proof"))
    return AlphaEvolveSystemRequirementInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        requirement_count=data.get("requirement_count") if isinstance(data.get("requirement_count"), int) else 0,
        implemented_local_count=data.get("implemented_local_count") if isinstance(data.get("implemented_local_count"), int) else 0,
        implementation_gap_count=data.get("implementation_gap_count") if isinstance(data.get("implementation_gap_count"), int) else 0,
        missing_anchor_count=expected["missing_anchor_count"],
        missing_reference_count=expected["missing_reference_count"],
        issues=issues,
    )


def render_alphaevolve_system_requirement_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_system_requirement_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve system requirement inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| requirement_count | {validation.requirement_count} |",
        f"| implemented_local_count | {validation.implemented_local_count} |",
        f"| implementation_gap_count | {validation.implementation_gap_count} |",
        f"| missing_anchor_count | {validation.missing_anchor_count} |",
        f"| missing_reference_count | {validation.missing_reference_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _requirement_record(
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
        "requirement_id": spec["requirement_id"],
        "source_span_id": spec["source_span_id"],
        "source_page": page_number,
        "source_anchor": spec["source_anchor"],
        "source_anchor_present": _canonical(spec["source_anchor"]) in _canonical(page_text),
        "requirement": spec["requirement"],
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
    list[AlphaEvolveSystemRequirementInventoryBoundaryIssue],
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
    return None, [_issue("invalid_shape", "system requirement inventory boundary must be a JSON object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveSystemRequirementInventoryBoundaryIssue:
    return AlphaEvolveSystemRequirementInventoryBoundaryIssue(code=code, message=message)
