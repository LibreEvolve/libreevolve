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


ALPHAEVOLVE_RELATED_WORK_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_related_work_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "section_5_claim_inventory_complete_without_independent_positioning_"
    "review_or_comparison_result_reproduction"
)
EXPECTED_CLAIM_COUNT = 85
IMPLEMENTED_STATUS = "implemented_local"
SOURCE_CONTEXT_STATUS = "source_context_only"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)
SUPPORTED_STATUSES = INCOMPLETE_STATUSES | {
    IMPLEMENTED_STATUS,
    SOURCE_CONTEXT_STATUS,
}


_TODO_SPECS = {
    "related_work_code": (
        "docs/todo/code.md",
        "Add AlphaEvolve Section 5 Related Work taxonomy and positioning evidence.",
    ),
    "related_work_paper": (
        "docs/todo/papers.md",
        "Track AlphaEvolve Section 5 Related Work taxonomy and positioning evidence.",
    ),
    "operator": (
        "docs/todo/code.md",
        "Extend mutation-operator policy beyond the current fixed-edit boundary",
    ),
    "codebase": (
        "docs/todo/code.md",
        "Add codebase-scale benchmark evidence for multi-component generated",
    ),
    "multiobjective": (
        "docs/todo/code.md",
        "Promote multi-objective overlays to primary archive optimization.",
    ),
    "programmatic": (
        "docs/todo/code.md",
        "Extend AI-Co-Scientist representation-boundary evidence beyond the",
    ),
}


def _claim(
    claim_id: str,
    source_page: int,
    source_anchor: str,
    claim: str,
    category: str,
    implementation_status: str = SOURCE_CONTEXT_STATUS,
    evidence_paths: tuple[str, ...] = (
        "papers/alphaevolve_source_inventory_boundary.json",
    ),
    todo_ids: tuple[str, ...] = (),
    roadmap_section_id: str = "related_work_positioning",
    roadmap_phase: str = "longer_term",
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "source_span_id": "section_5",
        "source_page": source_page,
        "source_anchor": source_anchor,
        "claim": claim,
        "category": category,
        "implementation_status": implementation_status,
        "evidence_paths": evidence_paths,
        "todo_ids": todo_ids,
        "roadmap_section_id": roadmap_section_id,
        "roadmap_phase": roadmap_phase,
    }


RELATED_WORK_CLAIM_SPECS = (
    _claim(
        "evolutionary_programming_lineage",
        18,
        "AlphaEvolve extends a long tradition of research on evolutionary or genetic programming",
        "AlphaEvolve is positioned as extending evolutionary or genetic programming.",
        "evolutionary_methods",
    ),
    _claim(
        "mutation_crossover_pool_pattern",
        18,
        "one repeatedly uses a set of mutation and crossover operators to evolve a pool of programs",
        "Classical evolutionary programming repeatedly applies mutation and crossover operators to a program pool.",
        "evolutionary_methods",
    ),
    _claim(
        "classical_symbolic_regression_success",
        18,
        "classical evolutionary techniques have succeeded in symbolic regression applications",
        "Classical evolutionary techniques have succeeded in symbolic regression.",
        "evolutionary_methods",
    ),
    _claim(
        "classical_scientific_algorithmic_discovery_success",
        18,
        "automated scientific",
        "Classical evolutionary techniques have been used for automated scientific and algorithmic discovery.",
        "evolutionary_methods",
    ),
    _claim(
        "classical_scheduling_success",
        18,
        "and scheduling",
        "Classical evolutionary techniques have been used for scheduling problems.",
        "evolutionary_methods",
    ),
    _claim(
        "handwritten_operators_hard_to_design",
        19,
        "handwritten evolution operators, which can be hard to design",
        "Handwritten evolution operators can be hard to design.",
        "evolutionary_methods",
    ),
    _claim(
        "handwritten_operators_miss_domain_properties",
        19,
        "may fail to capture important properties of the domain",
        "Handwritten evolution operators may miss important domain properties.",
        "evolutionary_methods",
    ),
    _claim(
        "llm_constructed_mutation_operators",
        19,
        "uses LLMs to automate the construction of these operators",
        "AlphaEvolve uses LLMs to automate mutation-operator construction.",
        "evolutionary_methods",
        "partially_implemented",
        ("papers/mutation_operator_boundary.json",),
        ("operator", "related_work_code"),
        "candidate_workspace_fidelity",
        "near_term",
    ),
    _claim(
        "llm_world_knowledge_mutation",
        19,
        "leverages the LLM's world knowledge to mutate programs",
        "AlphaEvolve uses LLM world knowledge to construct program mutations.",
        "evolutionary_methods",
        "partially_implemented",
        ("papers/mutation_operator_boundary.json",),
        ("operator", "related_work_code"),
        "candidate_workspace_fidelity",
        "near_term",
    ),
    _claim(
        "no_predefined_allowed_mutation_set",
        19,
        "without the need to pre-define a set of allowed mutation operations",
        "AlphaEvolve does not require a predefined set of allowed mutation operations.",
        "evolutionary_methods",
        "partially_implemented",
        ("papers/mutation_operator_boundary.json",),
        ("operator", "related_work_code"),
        "candidate_workspace_fidelity",
        "near_term",
    ),
    _claim(
        "recent_llm_evolution_predecessors",
        19,
        "preceded by a body of recent efforts that combine LLMs and evolution",
        "AlphaEvolve follows recent work combining LLMs and evolution.",
        "funsearch_comparison",
    ),
    _claim(
        "extends_funsearch",
        19,
        "it extends the FunSearch system",
        "AlphaEvolve directly extends FunSearch.",
        "funsearch_comparison",
    ),
    _claim(
        "funsearch_mathematical_discovery",
        19,
        "as an approach to mathematical discovery",
        "FunSearch was introduced as an approach to mathematical discovery.",
        "funsearch_comparison",
    ),
    _claim(
        "funsearch_bayesian_acquisition_functions",
        19,
        "learning acquisition functions for Bayesian optimization",
        "FunSearch was used to learn Bayesian-optimization acquisition functions.",
        "funsearch_comparison",
    ),
    _claim(
        "funsearch_cognitive_models",
        19,
        "discovering cognitive models",
        "FunSearch was used to discover cognitive models.",
        "funsearch_comparison",
    ),
    _claim(
        "funsearch_graph_distances",
        19,
        "computing distances between graphs",
        "FunSearch was used to compute distances between graphs.",
        "funsearch_comparison",
    ),
    _claim(
        "funsearch_competitive_programming",
        19,
        "combinatorial competitive programming",
        "FunSearch was used for combinatorial competitive programming.",
        "funsearch_comparison",
    ),
    _claim(
        "three_funsearch_extensions",
        19,
        "AlphaEvolve goes beyond FunSearch and its recent reimplementation",
        "The paper identifies three direct extensions beyond FunSearch and its reimplementation.",
        "funsearch_comparison",
    ),
    _claim(
        "funsearch_single_python_function",
        19,
        "FunSearch only allowed the evolution of a single Python function",
        "FunSearch was limited to evolving one Python function.",
        "funsearch_comparison",
    ),
    _claim(
        "alphaevolve_entire_codebases",
        19,
        "AlphaEvolve allows evolution over entire codebases",
        "AlphaEvolve evolves entire codebases.",
        "funsearch_comparison",
        "partially_implemented",
        ("papers/codebase_scale_benchmark_boundary.json",),
        ("codebase", "related_work_code"),
        "candidate_workspace_fidelity",
        "near_term",
    ),
    _claim(
        "alphaevolve_wide_programming_languages",
        19,
        "written in a wide range of programming languages",
        "AlphaEvolve evolves codebases across a wide range of programming languages.",
        "funsearch_comparison",
        "partially_implemented",
        ("papers/candidate_language_runner_boundary.json",),
        ("codebase", "related_work_code"),
        "candidate_workspace_fidelity",
        "near_term",
    ),
    _claim(
        "funsearch_single_objective",
        19,
        "FunSearch optimized a single objective function",
        "FunSearch optimized one objective function.",
        "funsearch_comparison",
    ),
    _claim(
        "alphaevolve_multiobjective_optimization",
        19,
        "AlphaEvolve provides the ability to perform multiobjective optimization",
        "AlphaEvolve supports multiobjective optimization.",
        "funsearch_comparison",
        "partially_implemented",
        (
            "papers/objective_archive_boundary.json",
            "papers/roadmap_multi_objective_search_boundary.json",
        ),
        ("multiobjective", "related_work_code"),
        "multi_objective_search",
        "near_term",
    ),
    _claim(
        "funsearch_relatively_small_llms",
        19,
        "LLMs in FunSearch were relatively small",
        "FunSearch used relatively small LLMs.",
        "funsearch_comparison",
    ),
    _claim(
        "funsearch_code_only_llms",
        19,
        "solely trained on code",
        "FunSearch used LLMs trained solely on code.",
        "funsearch_comparison",
    ),
    _claim(
        "alphaevolve_frontier_llms",
        19,
        "AlphaEvolve uses frontier LLMs",
        "AlphaEvolve uses frontier LLMs.",
        "funsearch_comparison",
        "partially_implemented",
        ("papers/gemini_provider_parity_boundary.json",),
        ("related_work_code",),
        "provider_and_model_parity",
        "near_term",
    ),
    _claim(
        "alphaevolve_rich_natural_language_context_feedback",
        19,
        "rich forms of natural-language context and feedback",
        "AlphaEvolve gives frontier LLMs rich natural-language context and feedback.",
        "funsearch_comparison",
        "partially_implemented",
        (
            "papers/prompt_database_parity_boundary.json",
            "papers/primary_prompt_role_telemetry_boundary.json",
        ),
        ("related_work_code",),
        "prompt_context_system",
        "near_term",
    ),
    _claim(
        "funsearch_extensions_enable_harder_problems",
        19,
        "these extensions allow AlphaEvolve to address important challenging problems that were not amenable to FunSearch",
        "The three FunSearch extensions are reported to enable important problems that FunSearch could not address.",
        "funsearch_comparison",
        "not_demonstrated",
        ("papers/benchmark_fixture_readiness_boundary.json",),
        ("related_work_paper",),
    ),
    _claim(
        "llm_evolution_robot_policies",
        19,
        "discover programmatic policies for a set of simulated robots",
        "Prior LLM-guided evolution discovered programmatic robot policies.",
        "llm_guided_evolution",
    ),
    _claim(
        "llm_evolution_code_synthesis",
        19,
        "for code synthesis",
        "Prior LLM-guided evolution was applied to code synthesis.",
        "llm_guided_evolution",
    ),
    _claim(
        "llm_evolution_symbolic_regression",
        19,
        "scientific and mathematical tasks, including symbolic regression",
        "Prior LLM-guided evolution was applied to symbolic regression.",
        "llm_guided_evolution",
    ),
    _claim(
        "llm_evolution_combinatorial_heuristics",
        19,
        "discovering heuristics for combinatorial optimization",
        "Prior LLM-guided evolution discovered combinatorial-optimization heuristics.",
        "llm_guided_evolution",
    ),
    _claim(
        "llm_evolution_molecular_structures",
        19,
        "synthesizing molecular structures",
        "Prior LLM-guided evolution synthesized molecular structures.",
        "llm_guided_evolution",
    ),
    _claim(
        "llm_evolution_prompt_enhancement",
        19,
        "enhancing LLM prompts",
        "LLM-guided evolution has improved AI systems by enhancing prompts.",
        "llm_guided_evolution",
    ),
    _claim(
        "llm_evolution_neural_architectures",
        19,
        "searching over neural architectures",
        "LLM-guided evolution has improved AI systems through neural-architecture search.",
        "llm_guided_evolution",
    ),
    _claim(
        "alphaevolve_scale_distinction",
        19,
        "differs from these approaches in its scale",
        "AlphaEvolve is reported to differ from adjacent LLM-evolution methods in scale.",
        "llm_guided_evolution",
        "not_demonstrated",
        ("papers/codebase_scale_benchmark_boundary.json",),
        ("related_work_paper", "codebase"),
    ),
    _claim(
        "alphaevolve_flexibility_distinction",
        19,
        "flexibility",
        "AlphaEvolve is reported to differ from adjacent LLM-evolution methods in flexibility.",
        "llm_guided_evolution",
        "not_demonstrated",
        ("papers/related_work_taxonomy_boundary.json",),
        ("related_work_paper",),
    ),
    _claim(
        "alphaevolve_generality_distinction",
        19,
        "general applicability to a broad range of domains",
        "AlphaEvolve is reported to differ in general applicability across broad domains.",
        "llm_guided_evolution",
        "not_demonstrated",
        ("papers/benchmark_fixture_readiness_boundary.json",),
        ("related_work_paper",),
    ),
    _claim(
        "continuous_llm_finetuning_rl",
        19,
        "continuously finetuning the LLM through reinforcement learning",
        "Continuous LLM fine-tuning through reinforcement learning is identified as a complementary extension.",
        "llm_guided_evolution",
        "not_implemented",
        (
            "libreevolve/plugins/ttt_rl.py",
            "papers/related_work_taxonomy_boundary.json",
        ),
        ("related_work_code",),
    ),
    _claim(
        "llm_directed_concept_learning",
        19,
        "LLM-directed concept learning step that summarizes high-performing programs in the pool into natural language",
        "LLM-directed concept learning can summarize high-performing programs into natural language.",
        "llm_guided_evolution",
        "not_implemented",
        ("papers/related_work_taxonomy_boundary.json",),
        ("related_work_code",),
    ),
    _claim(
        "complementary_ideas_need_scale_study",
        19,
        "More investigation is required to understand the benefits of these ideas at the scale at which AlphaEvolve operates",
        "The benefits of fine-tuning and concept learning at AlphaEvolve scale remain an open research question.",
        "llm_guided_evolution",
    ),
    _claim(
        "ai_coscientist_evolutionary_use",
        19,
        "Evolutionary methods have also found use in the recent AI Co-Scientist work",
        "AI Co-Scientist also uses evolutionary methods.",
        "ai_coscientist_comparison",
    ),
    _claim(
        "ai_coscientist_distinct_agent_tasks",
        19,
        "distinct agents for tasks like hypothesis discovery, ranking of hypotheses, and literature review",
        "AI Co-Scientist uses distinct agents for hypothesis discovery, hypothesis ranking, and literature review.",
        "ai_coscientist_comparison",
    ),
    _claim(
        "ai_coscientist_natural_language_hypotheses",
        19,
        "represents scientific hypotheses",
        "AI Co-Scientist represents scientific hypotheses in natural language.",
        "ai_coscientist_comparison",
    ),
    _claim(
        "ai_coscientist_natural_language_evaluation_criteria",
        19,
        "evaluation criteria in natural language",
        "AI Co-Scientist represents evaluation criteria in natural language.",
        "ai_coscientist_comparison",
    ),
    _claim(
        "alphaevolve_code_representation",
        19,
        "AlphaEvolve focuses on evolving code",
        "AlphaEvolve represents its evolving hypotheses as code.",
        "ai_coscientist_comparison",
        IMPLEMENTED_STATUS,
        ("papers/programmatic_representation_boundary.json",),
        (),
        "candidate_workspace_fidelity",
        "implemented_surface",
    ),
    _claim(
        "alphaevolve_programmatic_evaluation_functions",
        19,
        "directs evolution using programmatic evaluation functions",
        "AlphaEvolve directs evolution through programmatic evaluation functions.",
        "ai_coscientist_comparison",
        IMPLEMENTED_STATUS,
        (
            "papers/programmatic_representation_boundary.json",
            "libreevolve/core/evaluator.py",
        ),
        (),
        "evaluation_cascade",
        "implemented_surface",
    ),
    _claim(
        "programmatic_choice_sidesteps_hallucinations",
        19,
        "This choice enables us to substantially sidestep LLM hallucinations",
        "Programmatic code and evaluation are reported to substantially sidestep LLM hallucinations.",
        "ai_coscientist_comparison",
        "not_demonstrated",
        ("papers/programmatic_representation_boundary.json",),
        ("programmatic", "related_work_paper"),
        "evaluation_cascade",
        "near_term",
    ),
    _claim(
        "programmatic_choice_enables_many_timesteps",
        19,
        "allows AlphaEvolve to carry on the evolution process for a large number of time steps",
        "The programmatic representation and evaluation choice is reported to enable long evolutionary runs.",
        "ai_coscientist_comparison",
        "not_demonstrated",
        ("papers/programmatic_representation_boundary.json",),
        ("programmatic", "related_work_paper"),
        "evaluation_cascade",
        "near_term",
    ),
    _claim(
        "natural_language_programmatic_combination_possible",
        19,
        "it is possible in principle to combine the two approaches",
        "The paper identifies a possible hybrid of AI Co-Scientist and AlphaEvolve.",
        "ai_coscientist_comparison",
        "not_implemented",
        ("papers/programmatic_representation_boundary.json",),
        ("programmatic", "related_work_code"),
        "evaluation_cascade",
        "longer_term",
    ),
    _claim(
        "natural_language_programmatic_hybrid_idioms",
        19,
        "flexible combination of natural-language and programmatic idioms",
        "A hybrid system could combine natural-language and programmatic idioms flexibly.",
        "ai_coscientist_comparison",
        "not_implemented",
        ("papers/programmatic_representation_boundary.json",),
        ("programmatic", "related_work_code"),
        "evaluation_cascade",
        "longer_term",
    ),
    _claim(
        "alphaevolve_code_superoptimization_view",
        20,
        "AlphaEvolve can be viewed as a method for code superoptimization",
        "AlphaEvolve can be viewed as code superoptimization.",
        "superoptimization",
        IMPLEMENTED_STATUS,
        ("libreevolve/core/loop.py",),
        (),
        "evolution_loop",
        "implemented_surface",
    ),
    _claim(
        "alphaevolve_iteratively_improves_initial_program",
        20,
        "iteratively improves an initial program",
        "AlphaEvolve iteratively improves an initial program.",
        "superoptimization",
        IMPLEMENTED_STATUS,
        ("libreevolve/core/loop.py",),
        (),
        "evolution_loop",
        "implemented_surface",
    ),
    _claim(
        "alphaevolve_uses_execution_feedback",
        20,
        "using execution feedback",
        "AlphaEvolve uses execution feedback to drive program improvement.",
        "superoptimization",
        IMPLEMENTED_STATUS,
        (
            "libreevolve/core/loop.py",
            "libreevolve/core/evaluator.py",
        ),
        (),
        "evaluation_cascade",
        "implemented_surface",
    ),
    _claim(
        "superoptimization_1980s_origin",
        20,
        "goes back to the 1980s",
        "Code superoptimization dates to the 1980s.",
        "superoptimization",
    ),
    _claim(
        "pre_llm_systematic_enumeration",
        20,
        "systematic enumeration",
        "Pre-LLM superoptimization used systematic enumeration.",
        "superoptimization",
    ),
    _claim(
        "pre_llm_genetic_search",
        20,
        "genetic search",
        "Pre-LLM superoptimization used genetic search.",
        "superoptimization",
    ),
    _claim(
        "pre_llm_monte_carlo_sampling",
        20,
        "Monte Carlo sampling",
        "Pre-LLM superoptimization used Monte Carlo sampling.",
        "superoptimization",
    ),
    _claim(
        "pre_llm_deep_reinforcement_learning",
        20,
        "deep reinforcement learning",
        "Pre-LLM superoptimization used deep reinforcement learning.",
        "superoptimization",
    ),
    _claim(
        "alphatensor_limited_matrix_setting",
        20,
        "limited settings that focus on a single problem such as matrix multiplication",
        "AlphaTensor is presented as a system for a limited matrix-multiplication setting.",
        "superoptimization",
    ),
    _claim(
        "alphatensor_provably_correct_algorithms",
        20,
        "discover provably correct algorithms",
        "AlphaTensor discovered provably correct algorithms.",
        "superoptimization",
    ),
    _claim(
        "llm_superoptimization_literature",
        20,
        "body of LLM-based approaches to superoptimization and algorithm discovery have emerged",
        "Recent work applies LLMs to superoptimization and algorithm discovery.",
        "superoptimization",
    ),
    _claim(
        "alphacode_programming_competitions",
        20,
        "success in simulated programming competitions as in the case of AlphaCode",
        "AlphaCode is cited as evidence of LLM success in simulated programming competitions.",
        "superoptimization",
    ),
    _claim(
        "llm_attention_kernel_optimization",
        20,
        "optimize certain operations in GPU kernels, such as the attention operation",
        "LLM agents have optimized attention operations in GPU kernels.",
        "superoptimization",
    ),
    _claim(
        "llm_user_specified_kernel_operations",
        20,
        "more general user-specified operations",
        "LLM agents have optimized general user-specified kernel operations.",
        "superoptimization",
    ),
    _claim(
        "llm_discovered_evolutionary_algorithms",
        20,
        "using LLMs to discover novel evolutionary algorithms",
        "Prior work used LLMs to discover evolutionary algorithms.",
        "superoptimization",
    ),
    _claim(
        "llm_trained_language_models",
        20,
        "train language models",
        "Prior work used LLM-guided methods to train language models.",
        "superoptimization",
    ),
    _claim(
        "llm_optimized_warehouse_scale_computers",
        20,
        "optimize warehouse-scale computers",
        "Prior work used LLMs to optimize warehouse-scale computers.",
        "superoptimization",
    ),
    _claim(
        "multi_agent_llm_math_coding",
        20,
        "multiple LLM agents that converse with each other to accomplish mathematical and coding tasks",
        "Prior work used conversing LLM agents for mathematical and coding tasks.",
        "superoptimization",
    ),
    _claim(
        "evolutionary_llm_approach_enables_harder_problems",
        20,
        "allows us to address significantly more challenging problems, as demonstrated in Section 3",
        "The paper attributes more challenging Section 3 results to its LLM evolutionary approach.",
        "superoptimization",
        "not_demonstrated",
        ("papers/benchmark_fixture_readiness_boundary.json",),
        ("related_work_paper",),
    ),
    _claim(
        "ai_for_science_broad_domains",
        20,
        "applied to a wide range of scientific disciplines and tasks, from protein structure prediction",
        "AI systems have been applied across protein structure, quantum physics, climate science, and other scientific tasks.",
        "ai_for_science",
    ),
    _claim(
        "llm_science_multiple_disciplines",
        20,
        "recent LLM-based methods that target scientific problems in multiple disciplines",
        "Recent LLM methods target scientific problems across multiple disciplines.",
        "ai_for_science",
    ),
    _claim(
        "llms_automate_scientific_stages",
        20,
        "automate several distinct stages of the scientific discovery process",
        "LLMs have been used to automate distinct scientific-discovery stages.",
        "ai_for_science",
    ),
    _claim(
        "llms_generate_rank_hypotheses",
        20,
        "generating and ranking hypotheses and ideas",
        "LLMs have been used to generate and rank hypotheses and ideas.",
        "ai_for_science",
    ),
    _claim(
        "llm_guided_tree_search_science",
        20,
        "LLM-guided tree search-based algorithms",
        "LLM-guided tree-search methods are especially related scientific-discovery work.",
        "ai_for_science",
    ),
    _claim(
        "llm_guided_evolutionary_science",
        20,
        "LLM-guided evolutionary algorithms",
        "LLM-guided evolutionary methods are especially related scientific-discovery work.",
        "ai_for_science",
    ),
    _claim(
        "llms_experimental_planning_design",
        20,
        "optimize experimental planning and design",
        "LLMs have been used to optimize experimental planning and design.",
        "ai_for_science",
    ),
    _claim(
        "llms_experiment_execution_workflow",
        20,
        "experiment execution and workflow",
        "LLMs have been used for experiment execution and workflow.",
        "ai_for_science",
    ),
    _claim(
        "llms_data_analysis_stage",
        20,
        "focusing on the data analysis stage",
        "LLM scientific-discovery work also targets data analysis.",
        "ai_for_science",
    ),
    _claim(
        "alphaevolve_programmatic_hypothesis_representation",
        20,
        "differs from most of these methods in its use of programmatic hypothesis representations",
        "AlphaEvolve differs from most AI-for-science methods by using programmatic hypothesis representations.",
        "ai_for_science",
        "partially_implemented",
        ("papers/programmatic_representation_boundary.json",),
        ("programmatic", "related_work_code"),
        "evaluation_cascade",
        "near_term",
    ),
    _claim(
        "alphaevolve_programmatic_evaluation_metrics",
        20,
        "programmatic hypothesis representations and evaluation metrics",
        "AlphaEvolve differs from most AI-for-science methods by using programmatic evaluation metrics.",
        "ai_for_science",
        IMPLEMENTED_STATUS,
        (
            "papers/programmatic_representation_boundary.json",
            "libreevolve/core/evaluator.py",
        ),
        (),
        "evaluation_cascade",
        "implemented_surface",
    ),
    _claim(
        "ai_advances_pure_mathematics",
        20,
        "AI systems have also contributed to advances in pure mathematics",
        "AI systems have contributed to advances in pure mathematics.",
        "mathematical_discovery",
    ),
    _claim(
        "funsearch_mathematical_witnesses",
        20,
        "discovering witnesses for",
        "FunSearch established LLM-guided evolution for discovering mathematical witnesses.",
        "mathematical_discovery",
    ),
    _claim(
        "funsearch_mathematical_counterexamples",
        20,
        "counterexamples to mathematical statements",
        "FunSearch established LLM-guided evolution for discovering counterexamples.",
        "mathematical_discovery",
    ),
    _claim(
        "witness_counterexample_complements_proof_search",
        20,
        "complementary to that of finding formal and informal proofs of mathematical statements",
        "Witness and counterexample discovery is complementary to formal and informal proof search.",
        "mathematical_discovery",
    ),
)

EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in RELATED_WORK_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveRelatedWorkClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveRelatedWorkClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implementation_relevant_claim_count: int
    source_context_claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveRelatedWorkClaimInventoryBoundaryIssue]


def alphaevolve_related_work_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _claim_record(root_path, spec, page_texts)
        for spec in RELATED_WORK_CLAIM_SPECS
    ]
    status_counts = Counter(record["implementation_status"] for record in records)
    category_counts = Counter(record["category"] for record in records)
    implementation_gap_count = sum(
        record["implementation_status"] in INCOMPLETE_STATUSES
        for record in records
    )
    implementation_relevant_claim_count = sum(
        record["implementation_status"] != SOURCE_CONTEXT_STATUS
        for record in records
    )
    todo_owned_gap_count = sum(
        record["implementation_status"] in INCOMPLETE_STATUSES
        and record["active_todo_refs"]
        and all(
            ref["exists"] and ref["required_phrase_present"]
            for ref in record["active_todo_refs"]
        )
        for record in records
    )
    missing_anchor_count = sum(
        not record["source_anchor_present"] for record in records
    )
    missing_reference_count = sum(
        not ref["exists"]
        for record in records
        for ref in record["evidence_refs"]
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
        "schema": ALPHAEVOLVE_RELATED_WORK_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "related_work_claim_inventory_ready": inventory_ready,
        "alphaevolve_related_work_positioning_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": ["section_5"],
        "inventory_scope": {
            "included": [
                "all prose claims in Section 5 Related Work on PDF pages 18 through 20",
                "evolutionary-method, FunSearch, LLM-evolution, AI-Co-Scientist, superoptimization, AI-for-science, and mathematical-discovery comparisons",
                "implementation relevance separated from source-context-only literature claims",
                "exact PDF-page anchors and active TODO ownership for every implementation gap",
            ],
            "excluded": [
                "reference-list bibliographic metadata and independent verification of cited-paper claims",
                "independent positioning-review signoff",
                "reproduction of AlphaEvolve or cited-system comparison results",
                "Figures 9 through 14, Table 3, and detailed appendix claims",
                "AlphaEvolve production-scale or system-parity proof",
            ],
        },
        "claim_count": len(records),
        "expected_claim_count": EXPECTED_CLAIM_COUNT,
        "category_counts": dict(sorted(category_counts.items())),
        "implementation_status_counts": dict(sorted(status_counts.items())),
        "implementation_relevant_claim_count": implementation_relevant_claim_count,
        "source_context_claim_count": status_counts[SOURCE_CONTEXT_STATUS],
        "implemented_local_count": status_counts[IMPLEMENTED_STATUS],
        "implementation_gap_count": implementation_gap_count,
        "todo_owned_gap_count": todo_owned_gap_count,
        "missing_anchor_count": missing_anchor_count,
        "missing_reference_count": missing_reference_count,
        "claim_records": records,
        "claim_boundary": (
            "This sidecar certifies a bounded claim-level inventory of 85 "
            "AlphaEvolve Section 5 Related Work prose claims. It separates "
            "59 source-context-only literature claims from 26 implementation-"
            "relevant AlphaEvolve claims so background citations are not "
            "miscounted as local implementation gaps. It does not claim "
            "bibliography exhaustiveness, independent cited-paper fact "
            "verification, independent positioning review, comparison-result "
            "reproduction, later figure/table/appendix exhaustiveness, "
            "production-scale evidence, or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_related_work_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveRelatedWorkClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_related_work_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveRelatedWorkClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_related_work_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveRelatedWorkClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_RELATED_WORK_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported related-work claim inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    if data.get("alphaevolve_related_work_positioning_claim_ready") is not False:
        issues.append(
            _issue(
                "positioning_overclaim",
                "claim inventory must not claim independently reviewed positioning",
            )
        )
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(_issue("parity_overclaim", "claim inventory must not claim AlphaEvolve parity"))
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
        "implementation_relevant_claim_count",
        "source_context_claim_count",
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
                    f"{key} drifted from the bounded related-work claim inventory",
                )
            )
    if len(EXPECTED_CLAIM_IDS) != EXPECTED_CLAIM_COUNT:
        issues.append(_issue("invalid_spec_count", "related-work claim count must remain 85"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "related-work claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in RELATED_WORK_CLAIM_SPECS
            if spec["source_span_id"] not in EXPECTED_NAMED_SOURCE_SPAN_IDS
        }
    )
    if unknown_spans:
        issues.append(_issue("unknown_source_span", f"unknown source spans: {', '.join(unknown_spans)}"))
    unsupported_statuses = sorted(
        {
            spec["implementation_status"]
            for spec in RELATED_WORK_CLAIM_SPECS
            if spec["implementation_status"] not in SUPPORTED_STATUSES
        }
    )
    if unsupported_statuses:
        issues.append(
            _issue(
                "unsupported_implementation_status",
                f"unsupported statuses: {', '.join(unsupported_statuses)}",
            )
        )
    source_context_with_todos = sorted(
        record["claim_id"]
        for record in expected["claim_records"]
        if record["implementation_status"] == SOURCE_CONTEXT_STATUS
        and record["active_todo_refs"]
    )
    if source_context_with_todos:
        issues.append(
            _issue(
                "source_context_misclassified_as_gap",
                "source-context-only claims must not create implementation TODOs: "
                + ", ".join(source_context_with_todos),
            )
        )
    unowned_gaps = sorted(
        record["claim_id"]
        for record in expected["claim_records"]
        if record["implementation_status"] in INCOMPLETE_STATUSES
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
        issues.append(_issue("source_pdf_identity_mismatch", "retained AlphaEvolve PDF identity does not match the pinned source"))
    if expected["missing_anchor_count"]:
        issues.append(
            _issue(
                "missing_source_anchor",
                f"{expected['missing_anchor_count']} related-work claim anchors were not found",
            )
        )
    if expected["missing_reference_count"]:
        issues.append(
            _issue(
                "missing_local_reference",
                f"{expected['missing_reference_count']} evidence references are stale",
            )
        )
    expected_ready = (
        expected["source_artifact"]["identity_ok"]
        and expected["claim_count"] == EXPECTED_CLAIM_COUNT
        and expected["missing_anchor_count"] == 0
        and expected["missing_reference_count"] == 0
        and expected["todo_owned_gap_count"] == expected["implementation_gap_count"]
    )
    if data.get("related_work_claim_inventory_ready") is not expected_ready:
        issues.append(
            _issue(
                "invalid_related_work_claim_inventory_ready",
                "readiness does not match source, reference, and TODO ownership checks",
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "85" not in claim_boundary
        or "59 source-context-only" not in claim_boundary
        or "independent positioning review" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must separate Section 5 coverage from positioning and parity proof",
            )
        )
    return AlphaEvolveRelatedWorkClaimInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=(
            data.get("boundary_status")
            if isinstance(data.get("boundary_status"), str)
            else None
        ),
        claim_count=(data.get("claim_count") if isinstance(data.get("claim_count"), int) else 0),
        implementation_relevant_claim_count=(
            data.get("implementation_relevant_claim_count")
            if isinstance(data.get("implementation_relevant_claim_count"), int)
            else 0
        ),
        source_context_claim_count=(
            data.get("source_context_claim_count")
            if isinstance(data.get("source_context_claim_count"), int)
            else 0
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


def render_alphaevolve_related_work_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_related_work_claim_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve related-work claim inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| claim_count | {validation.claim_count} |",
        f"| implementation_relevant_claim_count | {validation.implementation_relevant_claim_count} |",
        f"| source_context_claim_count | {validation.source_context_claim_count} |",
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
        "implementation_relevance": (
            "source_context_only"
            if spec["implementation_status"] == SOURCE_CONTEXT_STATUS
            else "implementation_relevant"
        ),
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
    list[AlphaEvolveRelatedWorkClaimInventoryBoundaryIssue],
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
    return None, [_issue("invalid_shape", "related-work claim inventory must be a JSON object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveRelatedWorkClaimInventoryBoundaryIssue:
    return AlphaEvolveRelatedWorkClaimInventoryBoundaryIssue(code, message)
