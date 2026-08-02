from __future__ import annotations

import hashlib
import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_tex_prose_inventory_boundary import (
    ALPHAEVOLVE_TEX_PROSE_INVENTORY_BOUNDARY_SCHEMA,
    EXPECTED_SENTENCE_COUNT,
    _CLAIM_INVENTORY_PATHS,
    _claim_catalog,
    alphaevolve_tex_prose_inventory_boundary_record,
)
from libreevolve.problems.benchmarks.paper_bibliography import (
    EXPECTED_SOURCE_PAPER_ID,
)


ALPHAEVOLVE_TEX_PROPOSITION_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_tex_proposition_inventory_boundary.v7"
)
EXPECTED_BOUNDARY_STATUS = (
    "abstract_through_section3_3_2_kernel_proposition_review_complete_without_"
    "remaining_paper_or_independent_semantic_exhaustiveness"
)
EXPECTED_REVIEWED_SENTENCE_COUNT = 195
EXPECTED_PROPOSITION_COUNT = 621
EXPECTED_REVIEWED_SENTENCE_IDS = tuple(
    f"tex_prose_sentence_{ordinal:04d}" for ordinal in range(1, 196)
)
EXPECTED_NEW_BOUNDED_CLAIM_IDS = (
    "introduction_algorithm_search_outperforms_direct_solution_search",
    "evaluation_sample_efficiency_enables_expensive_evaluation",
)
EXPECTED_REPAIRED_SENTENCE_CLAIM_IDS = (
    "abstract_complex_4x4_matrix_48_multiplications",
    "introduction_algorithm_discovery_instrumental_goal",
    "introduction_automatically_evaluable_problem_scope",
    "introduction_complex_4x4_matrix_48_multiplications",
    "introduction_erdos_minimum_overlap_result",
    "introduction_seventy_five_percent_math_best_known",
    "evolution_database_resurfacing",
    "evaluation_every_proposal",
    "prompt_explicit_context",
    "section2_evolutionary_metric_improvement",
    "section3_1_most_table2_simple_initial_program",
    "section3_1_natural_language_near_integrality_prompt",
    "section3_1_standard_gradient_baseline_components",
    "section3_2_evolve_heuristics_not_direct_constructions",
    "section3_2_fast_objective_evaluations_common_in_math",
    "section3_3_1_continuous_average_point_7_percent_recovery",
    "section3_3_1_debuggability_advantage",
    "section3_3_1_ease_of_deployment_advantage",
    "section3_3_1_mission_critical_operational_qualities",
    "section3_3_1_post_deployment_confirms_simulator",
    "section3_3_1_predictability_advantage",
    "section3_3_2_average_twenty_three_percent_kernel_speedup",
    "section3_3_2_one_percent_gemini_training_reduction",
    "section3_3_2_team_research_engineering_velocity",
    "task_problem_specific_abstraction_choice",
)


@dataclass(frozen=True)
class _PropositionSpec:
    source_quote: str
    statement: str
    disposition: str
    claim_refs: tuple[tuple[str, str], ...] = ()
    rationale: str | None = None


def _ref(inventory_name: str, claim_id: str) -> tuple[str, str]:
    return (_CLAIM_INVENTORY_PATHS[inventory_name], claim_id)


def _mapped(
    source_quote: str,
    statement: str,
    *claim_refs: tuple[str, str],
) -> _PropositionSpec:
    return _PropositionSpec(
        source_quote,
        statement,
        "existing_bounded_claim_mapping",
        claim_refs,
    )


def _reviewed_context(
    source_quote: str,
    statement: str,
    rationale: str,
    *,
    disposition: str = "source_context_only",
) -> _PropositionSpec:
    return _PropositionSpec(
        source_quote,
        statement,
        disposition,
        rationale=rationale,
    )


_PROPOSITION_SPECS: dict[str, tuple[_PropositionSpec, ...]] = {
    "tex_prose_sentence_0001": (
        _mapped(
            "AlphaEvolve, an evolutionary coding agent",
            "AlphaEvolve is presented as an evolutionary coding agent.",
            _ref("context", "abstract_substantial_llm_capability_uplift"),
        ),
        _mapped(
            "substantially enhances capabilities of state-of-the-art LLMs",
            "AlphaEvolve is reported to substantially enhance frontier-LLM capability.",
            _ref("context", "abstract_substantial_llm_capability_uplift"),
        ),
        _mapped(
            "tackling open scientific problems or optimizing critical pieces of computational infrastructure",
            "The claimed task scope includes open science and critical infrastructure optimization.",
            _ref("context", "abstract_broad_applicability"),
        ),
    ),
    "tex_prose_sentence_0002": (
        _mapped(
            "orchestrates an autonomous pipeline of LLMs",
            "AlphaEvolve autonomously orchestrates an LLM pipeline.",
            _ref("context", "abstract_autonomous_llm_code_pipeline"),
            _ref("system", "section2_autonomous_pipeline"),
        ),
        _mapped(
            "improve an algorithm by making direct changes to the code",
            "The pipeline improves algorithms through direct code edits.",
            _ref("context", "abstract_autonomous_llm_code_pipeline"),
        ),
    ),
    "tex_prose_sentence_0003": (
        _mapped(
            "Using an evolutionary approach",
            "AlphaEvolve uses evolutionary search.",
            _ref("context", "introduction_evolution_plus_llm_code_generation"),
            _ref("system", "section2_evolutionary_metric_improvement"),
        ),
        _mapped(
            "continuously receiving feedback from one or more evaluators",
            "One or more evaluators continuously feed results into evolution.",
            _ref("context", "abstract_continuous_evaluator_feedback"),
        ),
        _mapped(
            "iteratively improves the algorithm",
            "The evolutionary loop iteratively improves an algorithm.",
            _ref("related", "alphaevolve_iteratively_improves_initial_program"),
        ),
        _reviewed_context(
            "potentially leading to new scientific and practical discoveries",
            "The authors present discovery as a possible consequence of iteration.",
            "This is a hedged capability outlook, not a demonstrated result or a separate implementation requirement.",
            disposition="author_outlook",
        ),
    ),
    "tex_prose_sentence_0004": (
        _mapped(
            "demonstrate the broad applicability of this approach",
            "The paper claims broad applicability.",
            _ref("context", "abstract_broad_applicability"),
        ),
        _mapped(
            "a number of important computational problems",
            "The applicability claim depends on multiple material computational problems.",
            _ref("context", "abstract_broad_applicability"),
        ),
    ),
    "tex_prose_sentence_0005": (
        _mapped(
            "critical components of large-scale computational stacks at Google",
            "The reported systems scope is Google's large-scale compute stack.",
            _ref("context", "introduction_four_google_compute_stack_results"),
        ),
        _mapped(
            "developed a more efficient scheduling algorithm for data centers",
            "AlphaEvolve is reported to improve data-center scheduling.",
            _ref("context", "abstract_datacenter_scheduling_result"),
            _ref("scheduling", "section3_3_1_google_scale_borg_scheduling_problem"),
        ),
        _mapped(
            "found a functionally equivalent simplification in the circuit design of hardware accelerators",
            "AlphaEvolve is reported to simplify an accelerator circuit while preserving function.",
            _ref("context", "abstract_hardware_circuit_simplification_result"),
            _ref("hardware", "verification_confirms_functional_correctness"),
        ),
        _mapped(
            "accelerated the training of the LLM underpinning AlphaEvolve itself",
            "AlphaEvolve is reported to accelerate training of its own base LLM.",
            _ref("context", "abstract_base_llm_training_acceleration_result"),
            _ref("kernel", "section3_3_2_gemini_optimizes_own_training"),
        ),
    ),
    "tex_prose_sentence_0006": (
        _mapped(
            "discovered novel",
            "AlphaEvolve is reported to discover novel algorithms.",
            _ref("context", "abstract_novel_provably_correct_sota_algorithms"),
        ),
        _mapped(
            "provably correct algorithms",
            "The reported algorithms have correctness proof or certificate evidence.",
            _ref("context", "abstract_novel_provably_correct_sota_algorithms"),
        ),
        _mapped(
            "surpass state-of-the-art solutions",
            "The reported algorithms improve state-of-the-art baselines.",
            _ref("context", "abstract_novel_provably_correct_sota_algorithms"),
        ),
        _mapped(
            "a spectrum of problems in mathematics and computer science",
            "The reported algorithm results span mathematics and computer science.",
            _ref("context", "abstract_broad_applicability"),
        ),
        _mapped(
            "significantly expanding the scope of prior automated discovery methods",
            "AlphaEvolve is reported to exceed prior automated-discovery scope.",
            _ref("related", "alphaevolve_generality_distinction"),
        ),
    ),
    "tex_prose_sentence_0007": (
        _mapped(
            "developed a search algorithm that found a procedure",
            "AlphaEvolve evolves a search algorithm that produces a matrix procedure.",
            _ref("context", "introduction_algorithm_discovery_instrumental_goal"),
            _ref("matrix", "section3_1_tensor_decomposition_algorithm_representation"),
        ),
        _mapped(
            "multiply two 4 times 4 complex-valued matrices using 48 scalar multiplications",
            "The reported complex 4x4 multiplication procedure uses 48 scalar multiplications.",
            _ref("context", "abstract_complex_4x4_matrix_48_multiplications"),
        ),
        _mapped(
            "the first improvement, after 56 years, over Strassen's algorithm in this setting",
            "The 48-multiplication result is reported as the first improvement over Strassen in 56 years for this setting.",
            _ref("context", "abstract_first_strassen_improvement_56_years"),
        ),
    ),
    "tex_prose_sentence_0008": (
        _reviewed_context(
            "can have a significant impact in improving solutions of problems across many areas of science and computation",
            "The authors predict broad future impact for AlphaEvolve-like coding agents.",
            "This is explicitly framed as author belief and does not establish a reproduced capability.",
            disposition="author_outlook",
        ),
    ),
    "tex_prose_sentence_0009": (
        _reviewed_context(
            "Discovering new high-value knowledge",
            "High-value scientific or commercial discovery is the motivating problem class.",
            "This motivates the platform and is not independently a LibreEvolve behavior requirement.",
        ),
        _mapped(
            "a prolonged process of ideation, exploration, backtracking on unpromising hypotheses, experimentation, and validation",
            "Discovery requires long-horizon ideation, exploration, backtracking, experimentation, and validation.",
            _ref("context", "introduction_iterative_ideation_backtracking_validation"),
        ),
    ),
    "tex_prose_sentence_0010": (
        _reviewed_context(
            "much recent interest in using large language models (LLMs) to automate significant parts of this process",
            "Recent work seeks to automate discovery stages with LLMs.",
            "This is field context rather than an AlphaEvolve-specific implementation requirement.",
        ),
    ),
    "tex_prose_sentence_0011": (
        _reviewed_context(
            "the breathtaking power of recent LLMs",
            "Recent LLM capability motivates automated discovery research.",
            "This is background motivation and does not define a local parity gate.",
        ),
        _reviewed_context(
            "enhance their capabilities using test-time compute",
            "Test-time compute can improve LLM capability.",
            "This cited background claim is not an AlphaEvolve-specific system requirement.",
        ),
        _reviewed_context(
            "agents that combine language generation and action",
            "Language-and-action agents are another motivating development.",
            "This cited background claim is not an AlphaEvolve-specific system requirement.",
        ),
    ),
    "tex_prose_sentence_0012": (
        _reviewed_context(
            "improved performance across a range of established benchmarks",
            "Recent LLM and agent advances improved established benchmark performance.",
            "This is cited field context rather than a LibreEvolve result claim.",
        ),
        _mapped(
            "hypothesis generation",
            "Prior LLM systems have accelerated hypothesis generation.",
            _ref("related", "llms_generate_rank_hypotheses"),
        ),
        _mapped(
            "experiment design",
            "Prior LLM systems have accelerated experiment design.",
            _ref("related", "llms_experimental_planning_design"),
        ),
    ),
    "tex_prose_sentence_0013": (
        _reviewed_context(
            "making entirely new scientific or practical discoveries remains challenging",
            "End-to-end novel discovery remains difficult for LLM pipelines.",
            "This is the paper's motivating limitation, not a claimed local behavior.",
        ),
    ),
    "tex_prose_sentence_0014": (
        _mapped(
            "an LLM code superoptimization agent, called AlphaEvolve",
            "AlphaEvolve is presented as an LLM code-superoptimization agent.",
            _ref("related", "alphaevolve_code_superoptimization_view"),
        ),
        _mapped(
            "a combination of evolutionary computation and LLM-based code generation",
            "AlphaEvolve combines evolution with LLM code generation.",
            _ref("context", "introduction_evolution_plus_llm_code_generation"),
        ),
    ),
    "tex_prose_sentence_0015": (
        _mapped(
            "the broad spectrum of scientific and engineering discovery problems",
            "AlphaEvolve targets a broad scientific and engineering problem spectrum.",
            _ref("context", "abstract_broad_applicability"),
        ),
        _mapped(
            "the candidates of discovery can be automatically evaluated",
            "AlphaEvolve limits autonomous discovery to automatically evaluable candidates.",
            _ref("context", "introduction_automatically_evaluable_problem_scope"),
        ),
    ),
    "tex_prose_sentence_0016": (
        _mapped(
            "represents the candidates (for example, new mathematical objects or practical heuristics) as algorithms",
            "Candidate mathematical objects and heuristics are represented as algorithms.",
            _ref("context", "introduction_algorithmic_candidate_representation"),
        ),
        _mapped(
            "uses a set of LLMs to generate",
            "A set of LLMs generates candidate algorithms.",
            _ref("context", "introduction_llms_generate_critique_evolve_pool"),
        ),
        _mapped(
            "critique, and evolve a pool of such algorithms",
            "LLMs critique and evolve an algorithm pool.",
            _ref("context", "introduction_llms_generate_critique_evolve_pool"),
        ),
    ),
    "tex_prose_sentence_0017": (
        _mapped(
            "grounded using code execution",
            "Candidate evolution is grounded in code execution.",
            _ref("context", "introduction_execution_and_automatic_evaluation_grounding"),
        ),
        _mapped(
            "automatic evaluation",
            "Candidate evolution is grounded in automatic evaluation.",
            _ref("context", "introduction_execution_and_automatic_evaluation_grounding"),
        ),
    ),
    "tex_prose_sentence_0018": (
        _mapped(
            "allows AlphaEvolve to avoid any incorrect suggestions from the base LLM",
            "Evaluation is claimed to filter every incorrect base-LLM suggestion.",
            _ref("context", "introduction_avoid_incorrect_base_llm_suggestions"),
        ),
    ),
    "tex_prose_sentence_0019": (
        _mapped(
            "leverages modern LLMs' ability to respond to feedback",
            "Evolution supplies feedback that modern LLMs can act on.",
            _ref("system", "table1_rich_context_and_feedback"),
        ),
        _mapped(
            "substantially different from the initial candidate pool in syntax and function",
            "Evolved candidates are reported to diverge syntactically and functionally from the initial pool.",
            _ref("context", "introduction_syntax_and_function_divergence"),
        ),
    ),
    "tex_prose_sentence_0020": (
        _mapped(
            "discovering new algorithms is the intrinsic goal",
            "AlphaEvolve supports tasks where algorithm discovery is the final objective.",
            _ref("context", "introduction_algorithm_discovery_intrinsic_goal"),
        ),
        _mapped(
            "the solution of interest is not an algorithm itself but an algorithm can describe how that solution is to be constructed or found",
            "AlphaEvolve supports instrumental algorithms that construct or find non-algorithmic solutions.",
            _ref("context", "introduction_algorithm_discovery_instrumental_goal"),
        ),
    ),
    "tex_prose_sentence_0021": (
        _mapped(
            "discovering the algorithm is only an instrumental goal",
            "An evolved algorithm can be instrumental to a downstream solution.",
            _ref("context", "introduction_algorithm_discovery_instrumental_goal"),
        ),
        _mapped(
            "a surprisingly effective strategy compared to searching for the solution directly",
            "Algorithm-mediated search is reported to outperform direct solution search.",
            _ref(
                "context",
                "introduction_algorithm_search_outperforms_direct_solution_search",
            ),
        ),
    ),
    "tex_prose_sentence_0022": (
        _mapped(
            "combining evolutionary methods with coding LLMs has been previously explored in various specialized settings",
            "Prior work combined coding LLMs with evolution in specialized settings.",
            _ref("related", "recent_llm_evolution_predecessors"),
        ),
    ),
    "tex_prose_sentence_0023": (
        _mapped(
            "AlphaEvolve is a substantial enhancement of FunSearch",
            "AlphaEvolve is presented as a substantial FunSearch extension.",
            _ref("related", "extends_funsearch"),
            _ref("related", "three_funsearch_extensions"),
        ),
        _mapped(
            "used LLM-guided evolution to discover heuristics",
            "FunSearch used LLM-guided evolution to discover heuristics.",
            _ref("related", "funsearch_mathematical_discovery"),
        ),
        _mapped(
            "construct novel mathematical objects or to drive the operation of online algorithms",
            "FunSearch heuristics construct mathematical objects or operate online algorithms.",
            _ref("related", "extends_funsearch"),
        ),
    ),
    "tex_prose_sentence_0024": (
        _mapped(
            "discovering policies for simulated robots",
            "Prior LLM-guided evolution discovered simulated-robot policies.",
            _ref("related", "llm_evolution_robot_policies"),
        ),
        _mapped(
            "symbolic regression",
            "Prior LLM-guided evolution was applied to symbolic regression.",
            _ref("related", "llm_evolution_symbolic_regression"),
        ),
        _mapped(
            "heuristic functions for combinatorial optimization",
            "Prior LLM-guided evolution synthesized combinatorial-optimization heuristics.",
            _ref("related", "llm_evolution_combinatorial_heuristics"),
        ),
    ),
    "tex_prose_sentence_0025": (
        _mapped(
            "leverages state-of-the-art (SOTA) LLMs",
            "AlphaEvolve uses frontier LLMs.",
            _ref("related", "alphaevolve_frontier_llms"),
            _ref("system", "table1_benefits_from_sota_models"),
        ),
        _mapped(
            "evolve large pieces of code",
            "AlphaEvolve evolves large code artifacts.",
            _ref("context", "introduction_large_code_evolution"),
            _ref("related", "alphaevolve_entire_codebases"),
        ),
        _mapped(
            "complex algorithms spanning multiple functions and components",
            "The evolved algorithms can span multiple functions and components.",
            _ref("context", "introduction_large_code_evolution"),
            _ref("system", "table1_hundreds_of_lines"),
        ),
    ),
    "tex_prose_sentence_0026": (
        _mapped(
            "go significantly beyond its predecessors in scale",
            "AlphaEvolve is reported to exceed predecessors in scale.",
            _ref("related", "alphaevolve_scale_distinction"),
        ),
        _mapped(
            "generality",
            "AlphaEvolve is reported to exceed predecessors in generality.",
            _ref("related", "alphaevolve_generality_distinction"),
        ),
    ),
    "tex_prose_sentence_0027": (
        _mapped(
            "the use of an automated evaluation metric offers AlphaEvolve a key advantage",
            "Automated evaluation is presented as a key AlphaEvolve advantage.",
            _ref("context", "introduction_execution_and_automatic_evaluation_grounding"),
            _ref("context", "introduction_avoid_incorrect_base_llm_suggestions"),
        ),
        _mapped(
            "puts tasks that require manual experimentation out of our scope",
            "Tasks requiring manual experimentation are outside the autonomous scope.",
            _ref("context", "introduction_manual_experimentation_out_of_scope"),
        ),
    ),
    "tex_prose_sentence_0028": (
        _mapped(
            "problems in mathematics, computer science, and system optimization typically permit automated evaluation metrics",
            "Mathematics, computer science, and systems optimization commonly permit automated metrics.",
            _ref("context", "introduction_automated_metrics_across_domains"),
        ),
        _mapped(
            "our efforts on AlphaEvolve focus on these domains",
            "The paper's application portfolio focuses on automatically evaluable domains.",
            _ref("context", "introduction_automated_metrics_across_domains"),
        ),
    ),
    "tex_prose_sentence_0029": (
        _mapped(
            "well-known open problems in algorithm design",
            "The application portfolio includes open algorithm-design problems.",
            _ref("context", "abstract_broad_applicability"),
        ),
        _mapped(
            "constructive mathematics",
            "The application portfolio includes constructive mathematics.",
            _ref("context", "abstract_broad_applicability"),
        ),
        _mapped(
            "critical layers in the large-scale computation stacks at Google",
            "The application portfolio includes critical Google compute-stack layers.",
            _ref("context", "introduction_four_google_compute_stack_results"),
        ),
    ),
    "tex_prose_sentence_0030": (
        _mapped(
            "discovering fast algorithms for multiplying matrices",
            "The matrix application searches for faster multiplication algorithms.",
            _ref("matrix", "section3_1_low_rank_decomposition_search_objective"),
        ),
        _mapped(
            "a more specialized AI approach had been applied previously",
            "AlphaTensor is prior specialized matrix-multiplication work.",
            _ref("related", "alphatensor_limited_matrix_setting"),
        ),
    ),
    "tex_prose_sentence_0031": (
        _mapped(
            "Despite being general-purpose, AlphaEvolve goes beyond",
            "AlphaEvolve is reported to exceed a specialized predecessor despite being general purpose.",
            _ref("related", "alphaevolve_generality_distinction"),
            _ref("related", "alphatensor_limited_matrix_setting"),
        ),
        _mapped(
            "improving the SOTA for 14 matrix multiplication algorithms",
            "AlphaEvolve is reported to improve 14 matrix-multiplication state-of-the-art results.",
            _ref("context", "introduction_fourteen_matrix_sota_improvements"),
        ),
        _mapped(
            "AlphaEvolve improves [citation] 's algorithm",
            "The complex 4x4 result improves the cited prior algorithm.",
            _ref("context", "introduction_complex_4x4_matrix_48_multiplications"),
        ),
        _mapped(
            "48 multiplications to multiply 4 times 4 complex-valued matrices",
            "The reported complex 4x4 algorithm uses 48 multiplications.",
            _ref("context", "introduction_complex_4x4_matrix_48_multiplications"),
        ),
    ),
    "tex_prose_sentence_0032": (
        _mapped(
            "a broad range of open problems",
            "The constructive-mathematics portfolio covers a broad open-problem range.",
            _ref("context", "introduction_automated_metrics_across_domains"),
        ),
        _mapped(
            "discovering constructions (objects) with better properties than all previously known constructions",
            "Mathematical candidates are constructions optimized against prior best properties.",
            _ref("context", "introduction_algorithmic_candidate_representation"),
            _ref("system", "task_constructor_function_abstraction"),
        ),
        _mapped(
            "according to given mathematical definitions",
            "Construction quality is determined by task-defined mathematical definitions.",
            _ref("context", "introduction_automatically_evaluable_problem_scope"),
        ),
    ),
    "tex_prose_sentence_0033": (
        _mapped(
            "over 50",
            "AlphaEvolve was applied to more than 50 mathematical problems.",
            _ref("context", "introduction_over_fifty_math_problems_best_known"),
        ),
        _mapped(
            "match the best known constructions on approximately 75 percent of them",
            "The paper reports a roughly 75 percent best-known match rate.",
            _ref("context", "introduction_seventy_five_percent_math_best_known"),
        ),
        _reviewed_context(
            "in many cases these constructions are likely to already be optimal",
            "The authors infer that many matched constructions are probably optimal.",
            "This is a qualified interpretation, not a proved optimality result or local implementation requirement.",
            disposition="author_interpretation",
        ),
    ),
    "tex_prose_sentence_0034": (
        _mapped(
            "approximately 20 percent of the problems, AlphaEvolve surpasses the SOTA",
            "The paper reports state-of-the-art uplift on roughly 20 percent of the math portfolio.",
            _ref("context", "introduction_twenty_percent_math_sota_uplift"),
        ),
        _mapped(
            "discovers new",
            "The improved mathematical constructions are reported as new.",
            _ref("context", "abstract_novel_provably_correct_sota_algorithms"),
        ),
        _mapped(
            "provably better constructions",
            "The new constructions are reported as provably better.",
            _ref("context", "abstract_novel_provably_correct_sota_algorithms"),
        ),
    ),
    "tex_prose_sentence_0035": (
        _mapped(
            "an improvement on the Minimum Overlap Problem",
            "The portfolio includes a reported Minimum Overlap improvement.",
            _ref("context", "introduction_erdos_minimum_overlap_result"),
        ),
        _mapped(
            "an improved construction on the Kissing Numbers problem in 11 dimensions",
            "The portfolio includes a reported dimension-11 kissing-number improvement.",
            _ref("context", "introduction_kissing_number_d11_improvement"),
        ),
    ),
    "tex_prose_sentence_0036": (
        _mapped(
            "four engineering problems spanning different layers of Google's compute stack",
            "The paper reports four engineering applications across Google compute-stack layers.",
            _ref("context", "introduction_four_google_compute_stack_results"),
        ),
        _mapped(
            "scheduling heuristics for Google's cluster management system",
            "One application evolves Google cluster-scheduling heuristics.",
            _ref("scheduling", "section3_3_1_google_scale_borg_scheduling_problem"),
        ),
        _mapped(
            "matrix-multiplication kernels used to train LLMs",
            "One application optimizes LLM-training matrix-multiplication kernels.",
            _ref("kernel", "section3_3_2_gemini_training_matmul_kernel"),
        ),
        _mapped(
            "arithmetic circuits used within TPUs",
            "One application optimizes TPU arithmetic circuits.",
            _ref("hardware", "key_tpu_arithmetic_circuit_target"),
        ),
        _mapped(
            "the runtime of attention in Transformers",
            "One application optimizes Transformer attention runtime.",
            _ref("compiler", "flashattention_kernel_optimization_result"),
        ),
    ),
    "tex_prose_sentence_0037": (
        _reviewed_context(
            "these components are run repeatedly over a long period of time",
            "The target compute components execute repeatedly over long periods.",
            "This motivates systems value but does not define a distinct implementation behavior.",
        ),
        _reviewed_context(
            "any improvements are highly valuable",
            "The authors assign high value to small improvements in repeated components.",
            "This is a workload-value judgment rather than a separate parity requirement.",
        ),
    ),
}

_PROPOSITION_SPECS.update(
    {
        "tex_prose_sentence_0038": (
            _mapped(
                "AlphaEvolve is a coding agent",
                "AlphaEvolve is presented as a coding agent.",
                _ref("system", "section2_autonomous_pipeline"),
            ),
            _mapped(
                "orchestrates an autonomous pipeline of computations including queries to LLMs",
                "The coding agent orchestrates an autonomous computation pipeline that queries LLMs.",
                _ref("system", "section2_autonomous_pipeline"),
            ),
            _mapped(
                "produces algorithms that address a user-specified task",
                "The pipeline produces algorithms for a user-specified task.",
                _ref("system", "section2_user_specified_task"),
            ),
        ),
        "tex_prose_sentence_0039": (
            _mapped(
                "the orchestrating procedure is an evolutionary algorithm",
                "The orchestration procedure is an evolutionary algorithm.",
                _ref("system", "section2_evolutionary_metric_improvement"),
            ),
            _mapped(
                "gradually develops programs that improve the score on the automated evaluation metrics associated with the task",
                "Evolution gradually develops programs that improve automated task metrics.",
                _ref("system", "section2_evolutionary_metric_improvement"),
            ),
        ),
        "tex_prose_sentence_0040": (
            _reviewed_context(
                "A high-level overview of AlphaEvolve is shown in [citation]",
                "The prose directs readers to the high-level overview figure.",
                "Figure navigation is source structure already covered by the figure inventory, not a separate implementation claim.",
            ),
            _reviewed_context(
                "[citation] gives an expanded view",
                "The prose directs readers to an expanded process figure.",
                "Figure navigation is source structure already covered by the figure inventory, not a separate implementation claim.",
            ),
        ),
        "tex_prose_sentence_0041": (
            _mapped(
                "AlphaEvolve tackles problems with machine-gradeable solutions",
                "AlphaEvolve's autonomous task scope requires machine-gradeable solutions.",
                _ref(
                    "context",
                    "introduction_automatically_evaluable_problem_scope",
                ),
            ),
            _mapped(
                "the user must provide a mechanism for automatically assessing generated solutions",
                "The user must supply an automatic candidate-assessment mechanism.",
                _ref("system", "task_scalar_metric_mapping"),
            ),
        ),
        "tex_prose_sentence_0042": (
            _mapped(
                "a function h mapping a solution to a set of scalar evaluation metrics",
                "The assessment mechanism maps each solution to scalar evaluation metrics.",
                _ref("system", "task_scalar_metric_mapping"),
            ),
        ),
        "tex_prose_sentence_0043": (
            _mapped(
                "these metrics are maximized",
                "Evaluation metrics are maximized by convention.",
                _ref("system", "task_metric_maximization_convention"),
            ),
        ),
        "tex_prose_sentence_0044": (
            _mapped(
                "h is typically implemented as a Python function",
                "The paper's current evaluator setup typically uses Python.",
                _ref("system", "task_fixed_evaluate_signature"),
            ),
            _mapped(
                "called evaluate",
                "The paper-style evaluator entrypoint is named evaluate.",
                _ref("system", "task_fixed_evaluate_signature"),
            ),
            _mapped(
                "with a fixed input/output signature",
                "The evaluate function has a fixed input/output signature.",
                _ref("system", "task_fixed_evaluate_signature"),
            ),
            _mapped(
                "returning a dictionary of scalars",
                "The evaluate function returns a dictionary of scalar metrics.",
                _ref("system", "task_fixed_evaluate_signature"),
            ),
        ),
        "tex_prose_sentence_0045": (
            _mapped(
                "executing this function may take only seconds on a single device",
                "An evaluator may complete in seconds on one device.",
                _ref("system", "task_evaluation_workload_range"),
            ),
            _mapped(
                "spawn extensive computations",
                "An evaluator may instead launch extensive computation.",
                _ref("system", "task_evaluation_workload_range"),
            ),
        ),
        "tex_prose_sentence_0046": (
            _mapped(
                "For mathematical problems, the function h is typically very simple",
                "The paper reports that mathematical-problem evaluators are typically simple.",
                _ref("system", "task_evaluation_workload_range"),
            ),
        ),
        "tex_prose_sentence_0047": (
            _mapped(
                "find largest possible graphs satisfying a given property",
                "The illustrative task searches for the largest graph satisfying a property.",
                _ref("system", "task_scalar_metric_mapping"),
                _ref("system", "task_constructor_function_abstraction"),
            ),
            _mapped(
                "h invokes the evolved code to generate a graph",
                "The evaluator invokes evolved constructor code to generate a graph.",
                _ref("system", "task_constructor_function_abstraction"),
            ),
            _mapped(
                "checks whether the property holds",
                "The evaluator checks the generated graph's required property.",
                _ref("system", "task_scalar_metric_mapping"),
            ),
            _mapped(
                "returns the size of the graph as the score",
                "The evaluator uses graph size as the scalar score.",
                _ref("system", "task_scalar_metric_mapping"),
            ),
        ),
        "tex_prose_sentence_0048": (
            _mapped(
                "h might involve performing an evolved search algorithm",
                "A complex evaluator may execute an evolved search algorithm.",
                _ref("system", "task_bespoke_search_abstraction"),
                _ref("system", "task_evaluation_workload_range"),
            ),
            _mapped(
                "training and evaluating a machine learning model",
                "A complex evaluator may train and evaluate a machine-learning model.",
                _ref("system", "task_evaluation_workload_range"),
            ),
        ),
        "tex_prose_sentence_0049": (
            _mapped(
                "support evolving multiple components across a codebase",
                "AlphaEvolve supports evolving multiple codebase components.",
                _ref("system", "task_multiple_marked_components"),
            ),
            _mapped(
                "exposes an input API where blocks of code can be annotated as to-be-evolved-by-the-system",
                "Its input API marks code blocks for evolution.",
                _ref("system", "task_multiple_marked_components"),
            ),
            _reviewed_context(
                "see Figure [citation] for an illustration",
                "The prose points to an API illustration.",
                "The cross-reference is navigation to separately inventoried Figure 3 evidence.",
            ),
        ),
        "tex_prose_sentence_0050": (
            _mapped(
                "integrating it with existing codebases while requiring only minimal changes",
                "The marker API is intended to integrate with existing codebases through minimal changes.",
                _ref("system", "task_minimal_marker_integration"),
            ),
            _mapped(
                "# EVOLVE-BLOCK-START and # EVOLVE-BLOCK-END",
                "Special start and end comments delimit evolved blocks.",
                _ref("system", "task_minimal_marker_integration"),
            ),
        ),
        "tex_prose_sentence_0051": (
            _mapped(
                "code inside such evolution blocks serves as the initial solution",
                "User code inside evolution blocks supplies the initial solution.",
                _ref("system", "task_evolved_blocks_and_skeleton"),
            ),
            _mapped(
                "the rest of the code forms a skeleton that ties the evolved pieces together",
                "Non-evolved code remains a skeleton connecting evolved pieces.",
                _ref("system", "task_evolved_blocks_and_skeleton"),
            ),
            _mapped(
                "they can be invoked from evaluate",
                "The skeleton makes evolved pieces callable from evaluate.",
                _ref("system", "task_evolved_blocks_and_skeleton"),
            ),
        ),
        "tex_prose_sentence_0052": (
            _mapped(
                "this initial implementation must be complete",
                "The initial implementation must be complete.",
                _ref("system", "task_complete_initial_program"),
            ),
            _mapped(
                "it can be rudimentary",
                "A complete initial implementation may be rudimentary.",
                _ref("system", "task_complete_initial_program"),
            ),
            _mapped(
                "single-line functions that return constants of the appropriate types",
                "A type-correct constant-returning function is an allowed rudimentary seed example.",
                _ref("system", "task_complete_initial_program"),
            ),
        ),
        "tex_prose_sentence_0053": (
            _mapped(
                "applied to the same problem in very different ways",
                "The same problem can use different evolved abstractions.",
                _ref("system", "task_problem_specific_abstraction_choice"),
            ),
            _mapped(
                "the evolved programs are not the final output but a means to discover solutions",
                "An evolved program may be instrumental to discovering the final solution.",
                _ref(
                    "context",
                    "introduction_algorithm_discovery_instrumental_goal",
                ),
            ),
        ),
        "tex_prose_sentence_0054": (
            _mapped(
                "evolve the solution in raw string representation",
                "AlphaEvolve can evolve a raw solution representation.",
                _ref("system", "task_raw_representation_abstraction"),
            ),
            _mapped(
                "evolve a function of a definite form that specifies how to construct the solution from scratch",
                "AlphaEvolve can evolve a fixed-form constructor function.",
                _ref("system", "task_constructor_function_abstraction"),
            ),
            _mapped(
                "evolve a bespoke search algorithm to find the solution within some fixed compute budget",
                "AlphaEvolve can evolve a budgeted bespoke search algorithm.",
                _ref("system", "task_bespoke_search_abstraction"),
            ),
            _mapped(
                "co-evolve intermediate solutions and search algorithms together",
                "AlphaEvolve can co-evolve intermediate solutions and search algorithms.",
                _ref("system", "task_solution_search_coevolution"),
            ),
            _mapped(
                "each search algorithm is specifically tailored to further improve upon a particular intermediate solution",
                "A co-evolved search algorithm is tailored to its paired intermediate solution.",
                _ref("system", "task_solution_search_coevolution"),
            ),
        ),
        "tex_prose_sentence_0055": (
            _mapped(
                "different levels of abstraction work better for different problems",
                "The paper reports problem-dependent performance across abstraction levels.",
                _ref("system", "task_problem_specific_abstraction_choice"),
            ),
        ),
        "tex_prose_sentence_0056": (
            _mapped(
                "for problems with highly symmetric solutions it is advantageous to evolve constructor functions",
                "The authors hypothesize that symmetric problems favor constructor functions.",
                _ref("system", "task_symmetry_guided_abstraction_bias"),
            ),
            _mapped(
                "these tend to be more concise",
                "Constructor functions are hypothesized to be more concise for symmetric solutions.",
                _ref("system", "task_symmetry_guided_abstraction_bias"),
            ),
            _mapped(
                "for problems with non-symmetric solutions it works better to evolve customized search algorithms",
                "The authors hypothesize that non-symmetric problems favor customized search algorithms.",
                _ref("system", "task_symmetry_guided_abstraction_bias"),
            ),
        ),
    }
)


_PROPOSITION_SPECS.update(
    {
        "tex_prose_sentence_0173": (
            _mapped(
                "Training large models like Gemini",
                "Gemini is included in the large-model training workload under discussion.",
                _ref("kernel", "section3_3_2_gemini_training_compute_demand"),
            ),
            _mapped(
                "requires substantial computational resources",
                "The Gemini training workload is reported to require substantial compute.",
                _ref("kernel", "section3_3_2_gemini_training_compute_demand"),
            ),
        ),
        "tex_prose_sentence_0174": (
            _mapped(
                "Gemini is built on JAX",
                "The reported Gemini implementation is based on JAX.",
                _ref("kernel", "section3_3_2_gemini_built_on_jax"),
            ),
            _mapped(
                "Pallas is an extension to JAX",
                "Pallas is described as a JAX extension.",
                _ref("kernel", "section3_3_2_pallas_extends_jax"),
            ),
            _mapped(
                "enables writing",
                "Pallas enables authors to write specialized programs.",
                _ref("kernel", "section3_3_2_custom_specialized_kernel_programs"),
            ),
            _mapped(
                "custom",
                "The Pallas programs can be customized.",
                _ref("kernel", "section3_3_2_custom_specialized_kernel_programs"),
            ),
            _mapped(
                "highly specialized programs",
                "The Pallas programs can be highly specialized.",
                _ref("kernel", "section3_3_2_custom_specialized_kernel_programs"),
            ),
            _mapped(
                "(kernels)",
                "The specialized programs are kernels.",
                _ref("kernel", "section3_3_2_custom_specialized_kernel_programs"),
            ),
            _mapped(
                "tailored for optimal execution",
                "The kernels are tailored for optimal execution.",
                _ref("kernel", "section3_3_2_optimal_accelerator_execution"),
            ),
            _mapped(
                "on hardware accelerators",
                "The execution target is hardware accelerators.",
                _ref("kernel", "section3_3_2_optimal_accelerator_execution"),
            ),
        ),
        "tex_prose_sentence_0175": (
            _mapped(
                "efficient Pallas kernels",
                "The reported optimization depends on efficient Pallas kernels.",
                _ref("kernel", "section3_3_2_pallas_kernel_training_importance"),
            ),
            _mapped(
                "training performance",
                "The affected target is Gemini training performance.",
                _ref("kernel", "section3_3_2_pallas_kernel_training_importance"),
            ),
        ),
        "tex_prose_sentence_0176": (
            _mapped(
                "critical aspect of kernel optimization",
                "Tiling is characterized as a critical kernel-optimization concern.",
                _ref("kernel", "section3_3_2_matmul_tiling_is_critical_optimization"),
            ),
            _mapped(
                "tuning the tiling strategy",
                "The optimization surface is the tiling strategy.",
                _ref("kernel", "section3_3_2_matmul_tiling_is_critical_optimization"),
            ),
            _mapped(
                "for matrix multiplication operations",
                "The tiling strategy applies to matrix multiplication.",
                _ref("kernel", "section3_3_2_matmul_tiling_is_critical_optimization"),
            ),
            _reviewed_context(
                "see [citation]",
                "The prose points to Figure 7 for the matrix-multiplication tiling problem.",
                "This is a figure locator; Figure 7 and its visual semantics are dispositioned separately.",
            ),
        ),
        "tex_prose_sentence_0177": (
            _mapped(
                "dividing a large matrix multiplication computation",
                "Tiling divides a large matrix-multiplication computation.",
                _ref("kernel", "section3_3_2_tiling_divides_large_matmul"),
            ),
            _mapped(
                "into smaller subproblems",
                "The division produces smaller subproblems.",
                _ref("kernel", "section3_3_2_tiling_divides_large_matmul"),
            ),
            _mapped(
                "balance computation",
                "Tiling is intended to balance computation.",
                _ref("kernel", "section3_3_2_balance_compute_and_data_movement"),
            ),
            _mapped(
                "with data movement",
                "The balancing counterpart is data movement.",
                _ref("kernel", "section3_3_2_balance_compute_and_data_movement"),
            ),
            _mapped(
                "key to accelerating the overall computation",
                "The compute/data-movement balance is reported to accelerate the overall computation.",
                _ref("kernel", "section3_3_2_tiling_accelerates_overall_computation"),
            ),
        ),
        "tex_prose_sentence_0178": (
            _mapped(
                "kernel engineers rely on",
                "Kernel engineers are described as relying on baseline tuning workflows.",
                _ref("kernel", "section3_3_2_search_based_autotuning_baseline"),
            ),
            _mapped(
                "search-based autotuning",
                "One baseline workflow is search-based autotuning.",
                _ref("kernel", "section3_3_2_search_based_autotuning_baseline"),
            ),
            _mapped(
                "manually crafted heuristics",
                "Another baseline workflow uses manually crafted heuristics.",
                _ref("kernel", "section3_3_2_manual_heuristic_baseline"),
            ),
            _mapped(
                "near-optimal tiling configurations",
                "The baseline workflows seek near-optimal tiling configurations.",
                _ref("kernel", "section3_3_2_near_optimal_configs_varied_shapes"),
            ),
            _mapped(
                "various input shapes",
                "The tiling configurations must cover varied input shapes.",
                _ref("kernel", "section3_3_2_near_optimal_configs_varied_shapes"),
            ),
        ),
        "tex_prose_sentence_0179": (
            _mapped(
                "Search-based tuning interrupts the research workflow",
                "Search-based tuning is reported to interrupt the research workflow.",
                _ref("kernel", "section3_3_2_autotuning_interrupts_workflow"),
            ),
            _mapped(
                "necessitating retuning",
                "The workflow requires repeated retuning.",
                _ref("kernel", "section3_3_2_retune_every_shape_change"),
            ),
            _mapped(
                "every input shape change",
                "Retuning is reported for every input-shape change.",
                _ref("kernel", "section3_3_2_retune_every_shape_change"),
            ),
        ),
        "tex_prose_sentence_0180": (
            _mapped(
                "manually crafting effective tiling heuristics",
                "The manual workflow crafts effective tiling heuristics.",
                _ref("kernel", "section3_3_2_manual_heuristic_bottleneck"),
            ),
            _mapped(
                "major engineering bottleneck",
                "Manual heuristic authoring is reported as a major engineering bottleneck.",
                _ref("kernel", "section3_3_2_manual_heuristic_bottleneck"),
            ),
            _mapped(
                "due to its complexity",
                "The bottleneck is attributed to the workflow's complexity.",
                _ref("kernel", "section3_3_2_manual_heuristic_bottleneck"),
            ),
            _mapped(
                "deep understanding of both kernel functionality",
                "Manual heuristic design requires deep kernel-functionality expertise.",
                _ref("kernel", "section3_3_2_deep_kernel_functionality_expertise"),
            ),
            _mapped(
                "hardware intricacies",
                "Manual heuristic design requires deep hardware expertise.",
                _ref("kernel", "section3_3_2_deep_hardware_expertise"),
            ),
        ),
        "tex_prose_sentence_0181": (
            _mapped(
                "key advantage of a performant heuristic",
                "Shape-general performance is characterized as a key heuristic advantage.",
                _ref("kernel", "section3_3_2_high_performance_arbitrary_shapes"),
            ),
            _mapped(
                "deliver high performance",
                "A performant heuristic should deliver high performance.",
                _ref("kernel", "section3_3_2_high_performance_arbitrary_shapes"),
            ),
            _mapped(
                "across arbitrary input shapes",
                "The high-performance requirement spans arbitrary input shapes.",
                _ref("kernel", "section3_3_2_high_performance_arbitrary_shapes"),
            ),
        ),
        "tex_prose_sentence_0182": (
            _mapped(
                "expedite the design of performant kernels",
                "The proposed workflow aims to accelerate performant-kernel design.",
                _ref("kernel", "section3_3_2_expedite_emerging_hardware_kernels"),
            ),
            _mapped(
                "for emerging hardware",
                "The accelerated kernel-design target includes emerging hardware.",
                _ref("kernel", "section3_3_2_expedite_emerging_hardware_kernels"),
            ),
            _mapped(
                "simplify their utilization",
                "The proposed workflow aims to simplify kernel utilization.",
                _ref("kernel", "section3_3_2_simplify_model_developer_utilization"),
            ),
            _mapped(
                "by model developers",
                "The intended kernel users include model developers.",
                _ref("kernel", "section3_3_2_simplify_model_developer_utilization"),
            ),
            _mapped(
                "facilitate the heuristic generation process",
                "The stated goal is to facilitate heuristic generation.",
                _ref("kernel", "section3_3_2_facilitate_heuristic_generation"),
            ),
        ),
        "tex_prose_sentence_0183": (
            _mapped(
                "employing AlphaEvolve",
                "AlphaEvolve is the proposed optimization system.",
                _ref("kernel", "section3_3_2_optimize_tiling_heuristics"),
            ),
            _mapped(
                "optimize tiling heuristics",
                "AlphaEvolve optimizes tiling heuristics.",
                _ref("kernel", "section3_3_2_optimize_tiling_heuristics"),
            ),
            _mapped(
                "important matrix multiplication kernel",
                "The optimization target is a material matrix-multiplication kernel.",
                _ref("kernel", "section3_3_2_gemini_training_matmul_kernel"),
            ),
            _mapped(
                "used to train Gemini",
                "The target kernel is used in Gemini training.",
                _ref("kernel", "section3_3_2_gemini_training_matmul_kernel"),
            ),
        ),
        "tex_prose_sentence_0184": (
            _mapped(
                "minimize the kernel's actual runtime",
                "The optimization objective minimizes measured kernel runtime.",
                _ref("kernel", "section3_3_2_minimize_actual_kernel_runtime"),
            ),
        ),
        "tex_prose_sentence_0185": (
            _mapped(
                "AlphaEvolve iteratively explores",
                "AlphaEvolve iteratively explores the heuristic search space.",
                _ref("kernel", "section3_3_2_iterative_tiling_refinement"),
            ),
            _mapped(
                "refines tiling heuristics",
                "The iteration refines tiling heuristics.",
                _ref("kernel", "section3_3_2_iterative_tiling_refinement"),
            ),
            _mapped(
                "proposing candidate code",
                "The proposal surface is candidate code.",
                _ref("kernel", "section3_3_2_candidate_code_proposals"),
            ),
            _mapped(
                "minimize this runtime",
                "Candidate proposals seek to minimize runtime.",
                _ref("kernel", "section3_3_2_runtime_across_various_shapes"),
            ),
            _mapped(
                "various input shapes",
                "Runtime is evaluated over varied input shapes.",
                _ref("kernel", "section3_3_2_runtime_across_various_shapes"),
            ),
            _mapped(
                "real TPU accelerators",
                "Runtime is measured on real TPU accelerators.",
                _ref("kernel", "section3_3_2_real_tpu_accelerator_measurement"),
            ),
        ),
        "tex_prose_sentence_0186": (
            _mapped(
                "correctness is maintained by construction",
                "Kernel correctness is claimed to be maintained by construction.",
                _ref("kernel", "section3_3_2_correctness_by_construction"),
            ),
            _mapped(
                "optimizing the tiling strategy",
                "Candidate optimization is restricted to the tiling strategy.",
                _ref("kernel", "section3_3_2_tiling_strategy_only_candidate_scope"),
            ),
            _mapped(
                "rather than altering its underlying mathematical operation",
                "The underlying mathematical operation is not altered.",
                _ref("kernel", "section3_3_2_underlying_math_unchanged"),
            ),
        ),
        "tex_prose_sentence_0187": (
            _mapped(
                "training",
                "The collected shape corpus includes a training split.",
                _ref("kernel", "section3_3_2_automatic_realistic_shape_collection"),
            ),
            _mapped(
                "evaluation datasets",
                "The collected shape corpus includes an evaluation split.",
                _ref("kernel", "section3_3_2_automatic_realistic_shape_collection"),
            ),
            _mapped(
                "automatically collect",
                "The shape corpus is collected automatically.",
                _ref("kernel", "section3_3_2_automatic_realistic_shape_collection"),
            ),
            _mapped(
                "realistic kernel input shapes",
                "The collected inputs are realistic kernel shapes.",
                _ref("kernel", "section3_3_2_automatic_realistic_shape_collection"),
            ),
            _mapped(
                "from kernel users",
                "The shape corpus is sourced from kernel users.",
                _ref("kernel", "section3_3_2_shape_corpus_from_kernel_users"),
            ),
        ),
        "tex_prose_sentence_0188": (
            _mapped(
                "Half of these input shapes",
                "Half of the collected input shapes are allocated to training.",
                _ref("kernel", "section3_3_2_half_training_shape_split"),
            ),
            _mapped(
                "form the training set",
                "The first half forms the training set.",
                _ref("kernel", "section3_3_2_half_training_shape_split"),
            ),
            _mapped(
                "optimization targets",
                "Training shapes provide optimization targets.",
                _ref("kernel", "section3_3_2_training_shapes_are_optimization_targets"),
            ),
            _mapped(
                "during the evolutionary process",
                "The optimization targets are used during evolution.",
                _ref("kernel", "section3_3_2_training_shapes_are_optimization_targets"),
            ),
        ),
        "tex_prose_sentence_0189": (
            _mapped(
                "remaining input shapes",
                "The remaining half of the shape corpus is reserved for evaluation.",
                _ref("kernel", "section3_3_2_half_evaluation_shape_split"),
            ),
            _mapped(
                "form the evaluation set",
                "The reserved shapes form the evaluation set.",
                _ref("kernel", "section3_3_2_half_evaluation_shape_split"),
            ),
            _mapped(
                "test the general applicability",
                "The evaluation split tests general applicability.",
                _ref("kernel", "section3_3_2_evaluation_tests_general_applicability"),
            ),
            _mapped(
                "resulting heuristic",
                "General applicability is tested for the evolved heuristic.",
                _ref("kernel", "section3_3_2_evaluation_tests_general_applicability"),
            ),
        ),
        "tex_prose_sentence_0190": (
            _mapped(
                "automated approach enables AlphaEvolve",
                "The heuristic-discovery workflow is automated through AlphaEvolve.",
                _ref("kernel", "section3_3_2_optimize_tiling_heuristics"),
            ),
            _mapped(
                "discover a heuristic",
                "AlphaEvolve discovers a tiling heuristic.",
                _ref("kernel", "section3_3_2_optimize_tiling_heuristics"),
            ),
            _mapped(
                "average 23 percent kernel speedup",
                "The discovered heuristic is reported to yield a 23-percent average kernel speedup.",
                _ref("kernel", "section3_3_2_average_twenty_three_percent_kernel_speedup"),
            ),
            _mapped(
                "across all kernels",
                "The reported average speedup spans all evaluated kernels.",
                _ref("kernel", "section3_3_2_average_twenty_three_percent_kernel_speedup"),
            ),
            _mapped(
                "existing expert-designed heuristic",
                "The kernel-speed comparator is the existing expert-designed heuristic.",
                _ref("kernel", "section3_3_2_expert_designed_heuristic_comparator"),
            ),
            _mapped(
                "corresponding 1 percent reduction",
                "The kernel speedup is reported to correspond to a 1-percent training-time reduction.",
                _ref("kernel", "section3_3_2_one_percent_gemini_training_reduction"),
            ),
            _mapped(
                "overall training time",
                "The 1-percent reduction applies to Gemini's overall training time.",
                _ref("kernel", "section3_3_2_one_percent_gemini_training_reduction"),
            ),
        ),
        "tex_prose_sentence_0191": (
            _mapped(
                "use of AlphaEvolve significantly reduced",
                "AlphaEvolve is reported to reduce kernel-optimization time materially.",
                _ref("kernel", "section3_3_2_optimization_months_to_days"),
            ),
            _mapped(
                "kernel optimization time",
                "Kernel-optimization time is the workflow-duration metric.",
                _ref("kernel", "section3_3_2_optimization_months_to_days"),
            ),
            _mapped(
                "several months",
                "The prior kernel-optimization workflow took several months.",
                _ref("kernel", "section3_3_2_optimization_months_to_days"),
            ),
            _mapped(
                "dedicated engineering effort",
                "The prior workflow required dedicated engineering effort.",
                _ref("kernel", "section3_3_2_dedicated_effort_to_automated_experimentation"),
            ),
            _mapped(
                "days of automated experimentation",
                "The AlphaEvolve workflow is reported to take days of automated experimentation.",
                _ref("kernel", "section3_3_2_dedicated_effort_to_automated_experimentation"),
            ),
        ),
        "tex_prose_sentence_0192": (
            _mapped(
                "speeds up the deployment",
                "The optimization acceleration is reported to speed deployment.",
                _ref("kernel", "section3_3_2_faster_optimized_kernel_deployment"),
            ),
            _mapped(
                "optimized kernels",
                "The faster deployment applies to optimized kernels.",
                _ref("kernel", "section3_3_2_faster_optimized_kernel_deployment"),
            ),
            _mapped(
                "kernel engineers",
                "The reported workflow changes how kernel engineers spend their expertise.",
                _ref("kernel", "section3_3_2_engineers_focus_higher_level_work"),
            ),
            _mapped(
                "more strategic",
                "Kernel engineers can focus on more strategic work.",
                _ref("kernel", "section3_3_2_engineers_focus_higher_level_work"),
            ),
            _mapped(
                "higher-level optimization problems",
                "The redirected work consists of higher-level optimization problems.",
                _ref("kernel", "section3_3_2_engineers_focus_higher_level_work"),
            ),
        ),
        "tex_prose_sentence_0193": (
            _mapped(
                "AlphaEvolve offers a path",
                "AlphaEvolve is presented as a path toward tuning automation.",
                _ref("kernel", "section3_3_2_path_to_automated_manual_tuning"),
            ),
            _mapped(
                "automating the manual tuning process",
                "The proposed path automates manual tuning.",
                _ref("kernel", "section3_3_2_path_to_automated_manual_tuning"),
            ),
            _mapped(
                "improving the ergonomics",
                "The proposed path is claimed to improve ergonomics.",
                _ref("kernel", "section3_3_2_improved_gemini_kernel_ergonomics"),
            ),
            _mapped(
                "Gemini kernel usage",
                "The ergonomics claim applies to Gemini kernel usage.",
                _ref("kernel", "section3_3_2_improved_gemini_kernel_ergonomics"),
            ),
        ),
        "tex_prose_sentence_0194": (
            _mapped(
                "tiling heuristic discovered by AlphaEvolve",
                "AlphaEvolve is reported to have discovered the tiling heuristic.",
                _ref("kernel", "section3_3_2_tiling_heuristic_deployed_production"),
            ),
            _mapped(
                "deployed in production",
                "The discovered tiling heuristic is reported as production-deployed.",
                _ref("kernel", "section3_3_2_tiling_heuristic_deployed_production"),
            ),
            _mapped(
                "enhancing Gemini's training efficiency",
                "Production deployment is reported to enhance Gemini training efficiency.",
                _ref("kernel", "section3_3_2_deployment_enhanced_training_efficiency"),
            ),
            _mapped(
                "Gemini team",
                "The reported deployment affects the Gemini team.",
                _ref("kernel", "section3_3_2_team_research_engineering_velocity"),
            ),
            _mapped(
                "research and engineering velocity",
                "Production deployment is reported to improve research and engineering velocity.",
                _ref("kernel", "section3_3_2_team_research_engineering_velocity"),
            ),
        ),
        "tex_prose_sentence_0195": (
            _reviewed_context(
                "marks a novel instance",
                "The authors characterize the deployment as a novel instance.",
                "Novelty is an author interpretation, not a separate implementation requirement.",
                disposition="author_interpretation",
            ),
            _mapped(
                "through the capabilities of AlphaEvolve",
                "AlphaEvolve provides the mechanism for Gemini's reported self-optimization.",
                _ref("kernel", "section3_3_2_gemini_optimizes_own_training"),
            ),
            _mapped(
                "optimizes its own training process",
                "Gemini is reported to optimize its own training process.",
                _ref("kernel", "section3_3_2_gemini_optimizes_own_training"),
            ),
        ),
    }
)

_PROPOSITION_SPECS.update(
    {
        "tex_prose_sentence_0137": (
            _reviewed_context(
                "Analysis",
                "Analysis is the category heading for the following mathematical examples.",
                "This is document structure rather than a standalone implementation requirement.",
            ),
        ),
        "tex_prose_sentence_0138": (
            _reviewed_context(
                "Autocorrelation inequalities.",
                "Autocorrelation inequalities is a problem label for the following result.",
                "The result sentence owns the substantive bounded claim.",
            ),
        ),
        "tex_prose_sentence_0139": (
            _mapped(
                "AlphaEvolve was able to improve",
                "AlphaEvolve is reported to improve autocorrelation-inequality bounds.",
                _ref("math", "section3_2_autocorrelation_bounds_improved"),
            ),
            _mapped(
                "the best known bounds",
                "The improved autocorrelation bounds were the best known bounds.",
                _ref("math", "section3_2_autocorrelation_bounds_improved"),
            ),
            _mapped(
                "several autocorrelation inequalities",
                "The reported improvement covers several autocorrelation inequalities.",
                _ref("math", "section3_2_autocorrelation_bounds_improved"),
            ),
        ),
        "tex_prose_sentence_0140": (
            _reviewed_context(
                "Uncertainty principles.",
                "Uncertainty principles is a problem label for the following result.",
                "The result sentence owns the substantive bounded claim.",
            ),
        ),
        "tex_prose_sentence_0141": (
            _mapped(
                "AlphaEvolve was able to produce a refined configuration",
                "AlphaEvolve is reported to produce a refined configuration.",
                _ref("math", "section3_2_uncertainty_fourier_upper_bound"),
            ),
            _mapped(
                "for a problem arising in Fourier analysis",
                "The refined-configuration problem arises in Fourier analysis.",
                _ref("math", "section3_2_uncertainty_fourier_upper_bound"),
            ),
            _mapped(
                "by polishing an uncertainty principle construction",
                "The refinement polishes an uncertainty-principle construction.",
                _ref("math", "section3_2_uncertainty_fourier_upper_bound"),
            ),
            _mapped(
                "leading to a slightly better upper bound",
                "The polished construction is reported to yield a slightly better upper bound.",
                _ref("math", "section3_2_uncertainty_fourier_upper_bound"),
            ),
        ),
        "tex_prose_sentence_0142": (
            _reviewed_context(
                "Combinatorics and number theory",
                "Combinatorics and number theory is a category heading.",
                "This is document structure rather than a standalone implementation requirement.",
            ),
        ),
        "tex_prose_sentence_0143": (
            _reviewed_context(
                "Erd o s's minimum overlap problem.",
                "The Erdos minimum-overlap text is a problem label for the following result.",
                "The result sentence owns the substantive bounded claim.",
            ),
        ),
        "tex_prose_sentence_0144": (
            _mapped(
                "AlphaEvolve established a new upper bound",
                "AlphaEvolve is reported to establish a new upper bound.",
                _ref("math", "section3_2_erdos_new_upper_bound"),
            ),
            _mapped(
                "for the minimum overlap problem",
                "The new upper bound applies to the minimum-overlap problem.",
                _ref("math", "section3_2_erdos_new_upper_bound"),
            ),
            _mapped(
                "slightly improving upon the previous record",
                "The reported upper bound slightly improves the previous record.",
                _ref("math", "section3_2_erdos_new_upper_bound"),
            ),
        ),
        "tex_prose_sentence_0145": (
            _reviewed_context(
                "Geometry and packing",
                "Geometry and packing is a category heading.",
                "This is document structure rather than a standalone implementation requirement.",
            ),
        ),
        "tex_prose_sentence_0146": (
            _reviewed_context(
                "Kissing number problem.",
                "Kissing number problem is a problem label for the following result.",
                "The result sentence owns the substantive bounded claim.",
            ),
        ),
        "tex_prose_sentence_0147": (
            _mapped(
                "In 11 dimensions",
                "The reported kissing-number result is in dimension 11.",
                _ref("math", "section3_2_kissing_number_d11_593_vs_592"),
            ),
            _mapped(
                "AlphaEvolve improved the lower bound on the kissing number",
                "AlphaEvolve is reported to improve the kissing-number lower bound.",
                _ref("math", "section3_2_kissing_number_d11_593_vs_592"),
            ),
            _mapped(
                "finding a configuration of 593",
                "The reported dimension-11 configuration contains 593 spheres.",
                _ref("math", "section3_2_kissing_number_d11_593_vs_592"),
            ),
            _mapped(
                "non-overlapping unit spheres",
                "The 593 spheres are non-overlapping unit spheres.",
                _ref("math", "section3_2_kissing_number_d11_593_vs_592"),
            ),
            _mapped(
                "simultaneously touch a central unit sphere",
                "All 593 spheres can simultaneously touch a central unit sphere.",
                _ref("math", "section3_2_kissing_number_d11_593_vs_592"),
            ),
            _mapped(
                "surpassing the previous record of 592",
                "The 593-sphere configuration is reported to surpass the previous record of 592.",
                _ref("math", "section3_2_kissing_number_d11_593_vs_592"),
            ),
        ),
        "tex_prose_sentence_0148": (
            _reviewed_context(
                "Packing problems.",
                "Packing problems is a problem label for the following results.",
                "The result sentence owns the substantive bounded claims.",
            ),
        ),
        "tex_prose_sentence_0149": (
            _mapped(
                "AlphaEvolve achieved several new results in packing problems",
                "AlphaEvolve is reported to achieve several new packing results.",
                _ref("math", "section3_2_n_point_max_min_distance_packing"),
                _ref("math", "section3_2_polygon_in_polygon_packing"),
                _ref("math", "section3_2_heilbronn_small_triangle_avoidance"),
            ),
            _mapped(
                "packing N points in a shape",
                "One reported packing task places N points in a shape.",
                _ref("math", "section3_2_n_point_max_min_distance_packing"),
            ),
            _mapped(
                "to minimize the ratio of the maximum and minimum distance",
                "The N-point packing objective minimizes the maximum-to-minimum distance ratio.",
                _ref("math", "section3_2_n_point_max_min_distance_packing"),
            ),
            _mapped(
                "packing various polygons in other polygons",
                "Another reported task packs various polygons inside other polygons.",
                _ref("math", "section3_2_polygon_in_polygon_packing"),
            ),
            _mapped(
                "in the most efficient way",
                "The polygon-in-polygon task seeks the most efficient packing.",
                _ref("math", "section3_2_polygon_in_polygon_packing"),
            ),
            _mapped(
                "variants of the Heilbronn problem",
                "The reported packing results include variants of the Heilbronn problem.",
                _ref("math", "section3_2_heilbronn_small_triangle_avoidance"),
            ),
            _mapped(
                "concerning point sets",
                "The reported Heilbronn variants concern point sets.",
                _ref("math", "section3_2_heilbronn_small_triangle_avoidance"),
            ),
            _mapped(
                "avoiding small-area triangles",
                "The reported Heilbronn point sets avoid small-area triangles.",
                _ref("math", "section3_2_heilbronn_small_triangle_avoidance"),
            ),
        ),
        "tex_prose_sentence_0150": (
            _mapped(
                "The full list of problems appears in Appendix [citation]",
                "The paper reports that the full problem list appears in Appendix B.",
                _ref("math", "section3_2_full_list_and_details_in_appendix_b"),
            ),
            _mapped(
                "new constructions found by AlphaEvolve",
                "The linked constructions are attributed to AlphaEvolve.",
                _ref("math", "section3_2_new_constructions_in_companion_colab"),
            ),
            _mapped(
                "the new constructions found by AlphaEvolve can be found in .",
                "The source links an external companion artifact containing the reported constructions.",
                _ref("math", "section3_2_new_constructions_in_companion_colab"),
            ),
        ),
        "tex_prose_sentence_0151": (
            _mapped(
                "More examples",
                "The authors plan to provide more examples in a follow-on paper.",
                _ref("math", "section3_2_upcoming_math_paper_follow_on"),
            ),
            _mapped(
                "details on these problems",
                "The authors plan to provide more problem details in a follow-on paper.",
                _ref("math", "section3_2_upcoming_math_paper_follow_on"),
            ),
            _mapped(
                "the methods used",
                "The authors plan to provide method details in a follow-on paper.",
                _ref("math", "section3_2_upcoming_math_paper_follow_on"),
            ),
            _mapped(
                "will be provided in an upcoming paper",
                "The additional examples, problem details, and method details are planned for an upcoming paper.",
                _ref("math", "section3_2_upcoming_math_paper_follow_on"),
            ),
        ),
        "tex_prose_sentence_0152": (
            _mapped(
                "Most of these discoveries are on open problems",
                "Most reported discoveries in this set concern open problems.",
                _ref("math", "section3_2_most_discoveries_externally_suggested"),
            ),
            _mapped(
                "suggested to us by external mathematicians",
                "External mathematicians suggested most of the reported open problems.",
                _ref("math", "section3_2_most_discoveries_externally_suggested"),
            ),
            _mapped(
                "Javier Gomez Serrano",
                "Javier Gomez Serrano is named among the external mathematicians.",
                _ref("math", "section3_2_javier_gomez_serrano_and_terence_tao"),
            ),
            _mapped(
                "Terence Tao",
                "Terence Tao is named among the external mathematicians.",
                _ref("math", "section3_2_javier_gomez_serrano_and_terence_tao"),
            ),
            _mapped(
                "also advised",
                "The named external mathematicians also provided formulation advice.",
                _ref("math", "section3_2_external_advice_on_input_formulation"),
            ),
            _mapped(
                "how to best formulate them",
                "The advice addressed how best to formulate the problems.",
                _ref("math", "section3_2_external_advice_on_input_formulation"),
            ),
            _mapped(
                "as inputs to AlphaEvolve",
                "The advised formulations were inputs to AlphaEvolve.",
                _ref("math", "section3_2_external_advice_on_input_formulation"),
            ),
        ),
        "tex_prose_sentence_0153": (
            _reviewed_context(
                "This highlights",
                "The authors interpret the preceding examples as evidence for a partnership opportunity.",
                "The inferential framing is author interpretation; the partnership proposition is mapped separately.",
                disposition="author_interpretation",
            ),
            _mapped(
                "potential for synergistic partnerships",
                "The authors claim potential for synergistic AI-human mathematical partnerships.",
                _ref("math", "section3_2_ai_human_math_partnership_potential"),
            ),
            _mapped(
                "AI-driven discovery engines like AlphaEvolve",
                "The proposed partnership includes AI-driven discovery engines such as AlphaEvolve.",
                _ref("math", "section3_2_ai_human_math_partnership_potential"),
            ),
            _mapped(
                "human mathematical expertise",
                "The proposed partnership includes human mathematical expertise.",
                _ref("math", "section3_2_ai_human_math_partnership_potential"),
            ),
        ),
    }
)

_PROPOSITION_SPECS.update(
    {
        "tex_prose_sentence_0077": (
            _mapped(
                "each new solution proposed by the LLMs is automatically evaluated",
                "Every newly proposed solution is automatically evaluated.",
                _ref("system", "evaluation_every_proposal"),
            ),
            _mapped(
                "To track AlphaEvolve's progress",
                "Automatic evaluation tracks evolutionary progress.",
                _ref("system", "evaluation_every_proposal"),
            ),
            _mapped(
                "select which ideas to propagate in future generations",
                "Evaluation results inform which ideas are resurfaced in future generations.",
                _ref("system", "evolution_database_resurfacing"),
            ),
        ),
        "tex_prose_sentence_0078": (
            _mapped(
                "executing the user-provided evaluation function h on the generated solution",
                "Evaluation executes the user-provided function on a generated solution.",
                _ref("system", "evaluation_every_proposal"),
                _ref("system", "task_scalar_metric_mapping"),
            ),
        ),
        "tex_prose_sentence_0079": (
            _reviewed_context(
                "supports optional mechanisms to make this evaluation more flexible and more efficient",
                "The prose introduces optional evaluation mechanisms for flexibility and efficiency.",
                "The substantive mechanisms are decomposed in the following cascade, feedback, and parallel-evaluation sentences.",
            ),
        ),
        "tex_prose_sentence_0080": (
            _mapped(
                "ensembles of test cases of increasing difficulty",
                "An evaluation cascade can contain test ensembles of increasing difficulty.",
                _ref("system", "evaluation_increasing_difficulty_cascade"),
            ),
            _mapped(
                "evaluated on the next stage only if they achieve sufficiently promising results in all earlier stages",
                "Candidates advance only after promising results in every earlier stage.",
                _ref("system", "evaluation_increasing_difficulty_cascade"),
            ),
        ),
        "tex_prose_sentence_0081": (
            _mapped(
                "prune out less promising solutions more quickly",
                "The evaluation cascade prunes weak candidates early.",
                _ref("system", "evaluation_increasing_difficulty_cascade"),
            ),
        ),
        "tex_prose_sentence_0082": (
            _mapped(
                "new solutions are initially evaluated on a small scale",
                "New candidates are initially evaluated at small scale.",
                _ref("system", "evaluation_increasing_difficulty_cascade"),
            ),
            _mapped(
                "before being subjected to the main test cases",
                "Main test cases run only after the small-scale evaluation.",
                _ref("system", "evaluation_increasing_difficulty_cascade"),
            ),
            _mapped(
                "filter out faulty programs early",
                "Small-scale evaluation is intended to reject faulty programs early.",
                _ref("system", "evaluation_increasing_difficulty_cascade"),
            ),
        ),
        "tex_prose_sentence_0083": (
            _mapped(
                "desirable solutions have certain characteristics that are difficult to capture precisely in the user-provided evaluation function h",
                "Some desirable candidate qualities are difficult to encode in the user evaluator.",
                _ref("system", "evaluation_llm_generated_feedback"),
            ),
            _mapped(
                "simplicity of the discovered program",
                "Program simplicity is given as an example of a difficult-to-encode quality.",
                _ref("system", "evaluation_llm_generated_feedback"),
            ),
        ),
        "tex_prose_sentence_0084": (
            _mapped(
                "graded using separate LLM calls",
                "Separate LLM calls can grade qualitative candidate properties.",
                _ref("system", "evaluation_llm_generated_feedback"),
            ),
            _mapped(
                "added to the dictionary of scores to steer evolution",
                "LLM grades can become score signals that steer evolution.",
                _ref("system", "evaluation_llm_generated_feedback"),
            ),
            _mapped(
                "used to discard solutions when a criterion is not fulfilled",
                "LLM grades can act as candidate-discard criteria.",
                _ref("system", "evaluation_llm_generated_feedback"),
            ),
        ),
        "tex_prose_sentence_0085": (
            _mapped(
                "the sample efficiency of AlphaEvolve makes it feasible",
                "The paper claims AlphaEvolve is sample-efficient enough to make expensive evaluation feasible.",
                _ref(
                    "system",
                    "evaluation_sample_efficiency_enables_expensive_evaluation",
                ),
            ),
            _mapped(
                "on the order of 100 compute-hours to evaluate any new solution",
                "A candidate evaluation may consume roughly 100 compute-hours.",
                _ref(
                    "system",
                    "evaluation_order_hundred_compute_hours_per_candidate",
                ),
            ),
        ),
        "tex_prose_sentence_0086": (
            _mapped(
                "individual evaluations are parallelized to reduce their wall-clock duration",
                "Individual evaluations need parallelism to reduce wall-clock duration.",
                _ref("system", "evaluation_async_cluster_parallelism"),
            ),
            _mapped(
                "slow down the rate at which new generations appear",
                "Long serial evaluations reduce generation throughput.",
                _ref(
                    "system",
                    "evaluation_order_hundred_compute_hours_per_candidate",
                ),
                _ref("system", "evaluation_async_cluster_parallelism"),
            ),
            _mapped(
                "limiting the ability of the evolutionary algorithm to apply several consecutive mutations",
                "Reduced generation throughput limits consecutive mutation depth.",
                _ref("system", "evaluation_async_cluster_parallelism"),
            ),
        ),
        "tex_prose_sentence_0087": (
            _mapped(
                "evaluation is embarrassingly parallel",
                "The paper reports that many application evaluators are embarrassingly parallel.",
                _ref("system", "evaluation_async_cluster_parallelism"),
            ),
            _mapped(
                "running a search algorithm from multiple randomized initializations",
                "Multiple randomized search initializations are an evaluation-parallelism example.",
                _ref("system", "evaluation_async_cluster_parallelism"),
            ),
            _mapped(
                "distribute this work through asynchronous calls to an evaluation cluster",
                "AlphaEvolve distributes evaluation through asynchronous cluster calls.",
                _ref("system", "evaluation_async_cluster_parallelism"),
            ),
        ),
        "tex_prose_sentence_0088": (
            _mapped(
                "optimizing multiple user-provided scores",
                "AlphaEvolve supports multiple user-provided optimization scores.",
                _ref("system", "evaluation_multiple_user_scores"),
            ),
            _mapped(
                "achieve a high score under one or multiple evaluation metrics",
                "Candidate objects may target one metric or several metrics.",
                _ref("system", "evaluation_multiple_user_scores"),
            ),
        ),
        "tex_prose_sentence_0089": (
            _mapped(
                "an intrinsic",
                "Multiple-score optimization can be intrinsically valuable when multiple outcomes matter.",
                _ref("system", "evaluation_multiple_user_scores"),
            ),
            _mapped(
                "instrumental value",
                "Multiple-score optimization can be instrumentally valuable to a target metric.",
                _ref("system", "evaluation_multi_metric_single_target_uplift"),
            ),
        ),
        "tex_prose_sentence_0090": (
            _mapped(
                "developing solutions for multiple evaluation metrics",
                "Some applications intrinsically require performance across multiple metrics.",
                _ref("system", "evaluation_multiple_user_scores"),
            ),
            _mapped(
                "one solution that is strong on all of them simultaneously",
                "A single candidate may need to be strong on all metrics simultaneously.",
                _ref("system", "evaluation_multiple_user_scores"),
            ),
            _mapped(
                "optimizing for multiple metrics often improves results for the single target metric",
                "The paper reports target-metric uplift from multi-metric optimization.",
                _ref("system", "evaluation_multi_metric_single_target_uplift"),
            ),
        ),
        "tex_prose_sentence_0091": (
            _reviewed_context(
                "programs excelling under different evaluation criteria often possess distinct structures or logic",
                "The authors hypothesize that different metric elites often have distinct program structure or logic.",
                "The sentence explicitly presents this causal explanation as a possibility rather than a demonstrated system result.",
                disposition="author_interpretation",
            ),
            _mapped(
                "incorporating examples of these diverse, high-performing programs",
                "Metric-diverse high-performing programs are incorporated into model prompts.",
                _ref("system", "evaluation_metric_diverse_prompting"),
            ),
            _mapped(
                "each representing a different definition of ``good''",
                "Each metric-diverse prompt example represents a different evaluation definition of good.",
                _ref("system", "evaluation_metric_diverse_prompting"),
            ),
            _mapped(
                "stimulate the generation of more varied candidate solutions",
                "Metric-diverse prompt examples are intended to increase candidate diversity.",
                _ref("system", "evaluation_metric_diverse_prompting"),
            ),
            _mapped(
                "increasing the chances of discovering novel approaches that are highly effective for the target metric",
                "The proposed diversity mechanism is intended to improve target-metric discovery probability.",
                _ref("system", "evaluation_multi_metric_single_target_uplift"),
                _ref("system", "evaluation_metric_diverse_prompting"),
            ),
        ),
        "tex_prose_sentence_0092": (
            _mapped(
                "continually generates a growing number of solutions",
                "Evolution continually grows the solution population.",
                _ref("system", "evolution_results_attached_to_solutions"),
            ),
            _mapped(
                "scores",
                "Evaluation scores are attached to generated solutions.",
                _ref("system", "evolution_results_attached_to_solutions"),
            ),
            _mapped(
                "program outputs",
                "Program outputs are attached to generated solutions.",
                _ref("system", "evolution_results_attached_to_solutions"),
            ),
        ),
        "tex_prose_sentence_0093": (
            _mapped(
                "solutions are stored in an evolutionary database",
                "Generated solutions are stored in an evolutionary database.",
                _ref("system", "evolution_database_resurfacing"),
            ),
            _mapped(
                "optimally resurface previously explored ideas in future generations",
                "The database is intended to resurface prior ideas in future generations.",
                _ref("system", "evolution_database_resurfacing"),
            ),
        ),
        "tex_prose_sentence_0094": (
            _mapped(
                "balancing exploration and exploitation",
                "The evolutionary database must balance exploration and exploitation.",
                _ref("system", "evolution_exploration_exploitation_balance"),
            ),
            _mapped(
                "continuously improve the best programs",
                "Exploitation is intended to continuously improve strong programs.",
                _ref("system", "evolution_exploration_exploitation_balance"),
            ),
            _mapped(
                "maintaining diversity",
                "The database is intended to preserve solution diversity.",
                _ref("system", "evolution_exploration_exploitation_balance"),
            ),
            _mapped(
                "encourage exploration of the entire search space",
                "Diversity is intended to encourage broad search-space exploration.",
                _ref("system", "evolution_exploration_exploitation_balance"),
            ),
        ),
        "tex_prose_sentence_0095": (
            _mapped(
                "inspired by a combination of the MAP elites algorithm",
                "The evolutionary database is inspired by MAP-Elites.",
                _ref("system", "evolution_map_elites_and_islands"),
            ),
            _mapped(
                "island-based population models",
                "The evolutionary database is also inspired by island population models.",
                _ref("system", "evolution_map_elites_and_islands"),
            ),
        ),
        "tex_prose_sentence_0096": (
            _mapped(
                "an asynchronous computational pipeline (using the asyncio Python library)",
                "AlphaEvolve uses a Python asyncio computational pipeline.",
                _ref("system", "distributed_asyncio_dependency_pipeline"),
            ),
            _mapped(
                "many computations are run concurrently",
                "The pipeline runs many computations concurrently.",
                _ref("system", "distributed_asyncio_dependency_pipeline"),
            ),
            _mapped(
                "each computation blocking (waiting) whenever its next step relies on the result of another, yet unfinished computation",
                "A pipeline computation waits when its next step depends on unfinished work.",
                _ref("system", "distributed_asyncio_dependency_pipeline"),
            ),
        ),
        "tex_prose_sentence_0097": (
            _mapped(
                "a controller",
                "The asynchronous pipeline includes a controller.",
                _ref("system", "distributed_controller_sampler_evaluator_nodes"),
            ),
            _mapped(
                "LLM samplers",
                "The asynchronous pipeline includes LLM samplers.",
                _ref("system", "distributed_controller_sampler_evaluator_nodes"),
            ),
            _mapped(
                "evaluation nodes",
                "The asynchronous pipeline includes evaluation nodes.",
                _ref("system", "distributed_controller_sampler_evaluator_nodes"),
            ),
        ),
        "tex_prose_sentence_0098": (
            _mapped(
                "optimized for throughput (rather than the speed of any one particular computation)",
                "The pipeline optimizes aggregate throughput rather than individual-operation latency.",
                _ref("system", "distributed_throughput_budget_optimization"),
            ),
            _mapped(
                "maximize the number of ideas that can be proposed and evaluated",
                "Throughput optimization targets the number of proposed and evaluated ideas.",
                _ref("system", "distributed_throughput_budget_optimization"),
            ),
            _mapped(
                "within a specific overall computation budget",
                "Pipeline throughput is optimized under an overall compute budget.",
                _ref("system", "distributed_throughput_budget_optimization"),
            ),
        ),
    }
)

_PROPOSITION_SPECS.update(
    {
        "tex_prose_sentence_0057": (
            _mapped(
                "AlphaEvolve leverages SOTA LLMs",
                "AlphaEvolve uses state-of-the-art LLMs in its generation pipeline.",
                _ref("system", "generation_model_ensemble"),
            ),
            _mapped(
                "supports various types of customization",
                "The primary evolution prompt supports multiple customization types.",
                _ref("system", "prompt_long_context_customization"),
            ),
            _mapped(
                "providing long contexts as part of the primary evolution prompt",
                "The primary evolution prompt supports long context.",
                _ref("system", "prompt_long_context_customization"),
            ),
        ),
        "tex_prose_sentence_0058": (
            _mapped(
                "multiple previously discovered solutions sampled from the program database",
                "Primary prompts include multiple sampled prior solutions.",
                _ref("system", "prompt_prior_solutions_and_instructions"),
            ),
            _mapped(
                "system instructions on how to propose changes to a particular solution",
                "Primary prompts instruct the model how to modify a selected solution.",
                _ref("system", "prompt_prior_solutions_and_instructions"),
            ),
        ),
        "tex_prose_sentence_0059": (
            _reviewed_context(
                "users can further tailor prompts to their specific needs in different ways",
                "The prose introduces a list of prompt-tailoring mechanisms.",
                "The substantive prompt mechanisms are decomposed in the following four sentences.",
            ),
        ),
        "tex_prose_sentence_0060": (
            _mapped(
                "details about the problem being solved",
                "Explicit prompt context can describe the problem.",
                _ref("system", "prompt_explicit_context"),
            ),
            _mapped(
                "fixed human-written instructions",
                "Explicit prompt context can contain fixed human instructions.",
                _ref("system", "prompt_explicit_context"),
            ),
            _mapped(
                "equations",
                "Explicit prompt context can contain equations.",
                _ref("system", "prompt_explicit_context"),
            ),
            _mapped(
                "code snippets",
                "Explicit prompt context can contain code snippets.",
                _ref("system", "prompt_explicit_context"),
            ),
            _mapped(
                "relevant literature (e.g., pdf files)",
                "Explicit prompt context can contain literature such as PDFs.",
                _ref("system", "prompt_explicit_context"),
            ),
        ),
        "tex_prose_sentence_0061": (
            _mapped(
                "template placeholders with human-provided alternatives",
                "Stochastic prompt formatting uses placeholders with human-provided alternatives.",
                _ref("system", "prompt_stochastic_formatting"),
            ),
            _mapped(
                "for increased diversity",
                "Stochastic prompt formatting is intended to increase diversity.",
                _ref("system", "prompt_stochastic_formatting"),
            ),
            _mapped(
                "instantiated using probability distributions",
                "Prompt alternatives are sampled from probability distributions.",
                _ref("system", "prompt_stochastic_formatting"),
            ),
            _mapped(
                "provided in a separate config file",
                "The probability distributions are provided through a separate configuration file.",
                _ref("system", "prompt_stochastic_formatting"),
            ),
        ),
        "tex_prose_sentence_0062": (
            _mapped(
                "this will include a program",
                "Rendered evaluation context usually includes the candidate program.",
                _ref("system", "prompt_rendered_evaluation_results"),
            ),
            _mapped(
                "the result of executing that program",
                "Rendered evaluation context usually includes program output.",
                _ref("system", "prompt_rendered_evaluation_results"),
            ),
            _mapped(
                "the scores assigned by the evaluate function",
                "Rendered evaluation context usually includes evaluator scores.",
                _ref("system", "prompt_rendered_evaluation_results"),
            ),
        ),
        "tex_prose_sentence_0063": (
            _mapped(
                "instructions and context suggested by the LLM itself",
                "Meta-prompt evolution lets an LLM suggest prompt instructions and context.",
                _ref("system", "prompt_meta_evolution_database"),
            ),
            _mapped(
                "in an additional prompt-generation step",
                "Meta-prompt suggestions are generated in an additional model step.",
                _ref("system", "prompt_meta_evolution_database"),
            ),
            _mapped(
                "co-evolved",
                "Prompt instructions and context are co-evolved.",
                _ref("system", "prompt_meta_evolution_database"),
            ),
            _mapped(
                "in a separate database analogous to the solution programs",
                "Meta prompts use a separate database analogous to the solution database.",
                _ref("system", "prompt_meta_evolution_database"),
            ),
        ),
        "tex_prose_sentence_0064": (
            _mapped(
                "leverages the capabilities of SOTA LLMs",
                "Creative generation uses state-of-the-art LLM capability.",
                _ref("system", "generation_model_ensemble"),
            ),
            _mapped(
                "digest information about previously developed solutions",
                "The generation model consumes information about prior solutions.",
                _ref("system", "prompt_prior_solutions_and_instructions"),
            ),
            _mapped(
                "propose new, diverse ways to improve the solutions",
                "The generation model proposes diverse solution improvements.",
                _ref("system", "generation_model_ensemble"),
            ),
        ),
        "tex_prose_sentence_0065": (
            _mapped(
                "AlphaEvolve is model-agnostic",
                "AlphaEvolve is designed to be model-agnostic.",
                _ref("system", "generation_model_agnostic"),
            ),
            _mapped(
                "performs increasingly better as the underlying LLM improves",
                "The paper reports increasing search performance with stronger underlying LLMs.",
                _ref("system", "generation_stronger_model_effect"),
            ),
        ),
        "tex_prose_sentence_0066": (
            _mapped(
                "asks an LLM to modify existing code, especially within larger codebases",
                "The generation path asks LLMs to modify existing code, including larger codebases.",
                _ref("system", "generation_search_replace_blocks"),
            ),
            _mapped(
                "provided as a sequence of diff blocks in a specific format",
                "Code modifications are requested as specifically formatted diff blocks.",
                _ref("system", "generation_search_replace_blocks"),
            ),
        ),
        "tex_prose_sentence_0067": (
            _mapped(
                "the exact segment to match in the current program version",
                "The SEARCH block must exactly match current program text.",
                _ref("system", "generation_search_replace_blocks"),
            ),
        ),
        "tex_prose_sentence_0068": (
            _mapped(
                "the new segment that will replace the original one",
                "The REPLACE block supplies replacement text for the matched segment.",
                _ref("system", "generation_search_replace_blocks"),
            ),
        ),
        "tex_prose_sentence_0069": (
            _mapped(
                "targeted updates to specific parts of the code",
                "SEARCH/REPLACE blocks enable targeted code updates.",
                _ref("system", "generation_search_replace_blocks"),
            ),
        ),
        "tex_prose_sentence_0070": (
            _mapped(
                "the code being evolved is very short",
                "Short evolved code can use complete-output mode.",
                _ref("system", "generation_direct_full_code_output"),
            ),
            _mapped(
                "a complete rewrite is more appropriate than a small modification",
                "Complete-output mode can be selected when rewriting is more appropriate than a diff.",
                _ref("system", "generation_direct_full_code_output"),
            ),
            _mapped(
                "output the entire code block directly, rather than using the diff format",
                "The LLM can be instructed to output the full code block instead of a diff.",
                _ref("system", "generation_direct_full_code_output"),
            ),
        ),
        "tex_prose_sentence_0071": (
            _mapped(
                "employs an ensemble of large language models",
                "AlphaEvolve generates with an LLM ensemble.",
                _ref("system", "generation_model_ensemble"),
            ),
        ),
        "tex_prose_sentence_0072": (
            _mapped(
                "Gemini 2.0 Flash",
                "The reported AlphaEvolve ensemble includes Gemini 2.0 Flash.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
            _mapped(
                "Gemini 2.0 Pro",
                "The reported AlphaEvolve ensemble includes Gemini 2.0 Pro.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
        ),
        "tex_prose_sentence_0073": (
            _mapped(
                "balance computational throughput with the quality of generated solutions",
                "The ensemble is intended to balance generation throughput and solution quality.",
                _ref("system", "generation_model_ensemble"),
                _ref("system", "generation_fast_strong_model_mix"),
            ),
        ),
        "tex_prose_sentence_0074": (
            _mapped(
                "Gemini 2.0 Flash, with its lower latency",
                "Gemini 2.0 Flash is used as the lower-latency model.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
            _mapped(
                "enables a higher rate of candidate generation",
                "The lower-latency model increases candidate-generation rate.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
            _mapped(
                "increasing the number of ideas explored per unit of time",
                "Higher candidate throughput increases ideas explored per unit time.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
        ),
        "tex_prose_sentence_0075": (
            _mapped(
                "Gemini 2.0 Pro, possessing greater capabilities",
                "Gemini 2.0 Pro is used as the higher-capability model.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
            _mapped(
                "provides occasional, higher-quality suggestions",
                "The higher-capability model provides less frequent, higher-quality suggestions.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
            _mapped(
                "significantly advance the evolutionary search",
                "Higher-quality suggestions can substantially advance search.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
            _mapped(
                "potentially lead to breakthroughs",
                "The paper attributes breakthrough potential to higher-capability suggestions.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
        ),
        "tex_prose_sentence_0076": (
            _mapped(
                "optimizes the overall discovery process",
                "The reported model mix is intended to optimize discovery.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
            _mapped(
                "maximizing the volume of evaluated ideas",
                "The fast model is intended to maximize evaluated-idea volume.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
            _mapped(
                "retaining the potential for substantial improvements driven by the more powerful model",
                "The strong model preserves the possibility of substantial improvements.",
                _ref("system", "generation_fast_strong_model_mix"),
            ),
        ),
    }
)

_PROPOSITION_SPECS.update(
    {
        "tex_prose_sentence_0099": (
            _reviewed_context(
                "accelerating machine learning computations",
                "Matrix multiplication supports accelerated machine-learning computation.",
                "This is domain motivation rather than an AlphaEvolve-specific implementation requirement.",
            ),
            _reviewed_context(
                "enabling realistic computer graphics",
                "Matrix multiplication supports realistic computer graphics.",
                "This is domain motivation rather than an AlphaEvolve-specific implementation requirement.",
            ),
            _reviewed_context(
                "matrix multiplication serves as a fundamental operation underpinning numerous critical algorithms and applications within computer science",
                "Matrix multiplication underpins numerous important computer-science algorithms and applications.",
                "This is general mathematical-computing context and does not define local parity behavior.",
            ),
        ),
        "tex_prose_sentence_0100": (
            _reviewed_context(
                "Since the pioneering work of [citation] , it has been known that",
                "The tensor-decomposition representation is attributed historically to pioneering prior work.",
                "The attribution is literature context; the substantive representation claim is mapped separately.",
            ),
            _mapped(
                "a rich space of algorithms for multiplying two matrices can be represented as decompositions of a given 3D tensor into rank-one tensors",
                "A broad class of matrix-multiplication algorithms can be represented as rank-one decompositions of a three-dimensional tensor.",
                _ref(
                    "matrix",
                    "section3_1_tensor_decomposition_algorithm_representation",
                ),
            ),
        ),
        "tex_prose_sentence_0101": (
            _mapped(
                "The rank (number of terms)",
                "The decomposition rank is its number of terms.",
                _ref(
                    "matrix",
                    "section3_1_tensor_rank_equals_scalar_multiplications",
                ),
            ),
            _mapped(
                "exactly specifies the number of scalar multiplications needed to compute the matrix product",
                "The decomposition rank exactly specifies the scalar-multiplication count for the matrix product.",
                _ref(
                    "matrix",
                    "section3_1_tensor_rank_equals_scalar_multiplications",
                ),
            ),
        ),
        "tex_prose_sentence_0102": (
            _mapped(
                "to develop faster matrix multiplication algorithms one needs to find low-rank decompositions of particular tensors",
                "Faster matrix multiplication is sought through low-rank decompositions of the corresponding tensors.",
                _ref(
                    "matrix",
                    "section3_1_low_rank_decomposition_search_objective",
                ),
            ),
        ),
        "tex_prose_sentence_0103": (
            _reviewed_context(
                "This problem has been tackled with many approaches",
                "The tensor-decomposition search problem has been tackled through many prior approaches.",
                "This is broad prior-work context; the listed approach families are dispositioned separately.",
            ),
            _reviewed_context(
                "specialized alternating least squares solvers",
                "Specialized alternating-least-squares solvers have been applied to the decomposition problem.",
                "This is prior-work context rather than a distinct AlphaEvolve implementation requirement.",
            ),
            _reviewed_context(
                "deep reinforcement learning",
                "Deep reinforcement learning has been applied to the decomposition problem.",
                "This is prior-work context rather than a distinct AlphaEvolve implementation requirement.",
            ),
            _reviewed_context(
                "custom search algorithms",
                "Custom search algorithms have been applied to the decomposition problem.",
                "This is prior-work context rather than a distinct AlphaEvolve implementation requirement.",
            ),
            _reviewed_context(
                "despite decades of effort",
                "The matrix-decomposition search problem has received decades of effort.",
                "This is historical problem context; the unresolved-rank claim is mapped separately.",
            ),
            _mapped(
                "even for the simple case of multiplying two 3 times 3 matrices, the minimum achievable rank is not known",
                "The minimum achievable rank for 3x3 matrix multiplication is reported as unknown.",
                _ref("matrix", "section3_1_3x3_minimum_rank_unknown"),
            ),
            _reviewed_context(
                "showcasing the difficulty of the problem",
                "The unresolved 3x3 rank is interpreted as evidence that the problem is difficult.",
                "This is the authors' interpretation of the historical evidence, not a separate system capability.",
                disposition="author_interpretation",
            ),
        ),
        "tex_prose_sentence_0104": (
            _mapped(
                "Starting from the problem description",
                "The matrix experiment supplies the problem description as model context.",
                _ref("system", "prompt_explicit_context"),
            ),
            _mapped(
                "a standard gradient-based algorithm",
                "The matrix search starts from a standard gradient-based algorithm.",
                _ref(
                    "matrix",
                    "section3_1_standard_gradient_baseline_components",
                ),
            ),
            _mapped(
                "including an initializer",
                "The gradient baseline includes an initializer.",
                _ref(
                    "matrix",
                    "section3_1_standard_gradient_baseline_components",
                ),
            ),
            _mapped(
                "a reconstruction loss function",
                "The gradient baseline includes a reconstruction loss.",
                _ref(
                    "matrix",
                    "section3_1_standard_gradient_baseline_components",
                ),
            ),
            _mapped(
                "an Adam optimizer",
                "The gradient baseline includes an Adam optimizer.",
                _ref(
                    "matrix",
                    "section3_1_standard_gradient_baseline_components",
                ),
            ),
            _mapped(
                "develop sophisticated tensor decomposition algorithms that outperform existing approaches",
                "AlphaEvolve is reported to develop sophisticated tensor-decomposition algorithms that outperform prior approaches.",
                _ref(
                    "matrix",
                    "section3_1_sophisticated_algorithms_outperform_approaches",
                ),
            ),
        ),
        "tex_prose_sentence_0105": (
            _mapped(
                "To evaluate each evolved program",
                "Every evolved matrix-search program is evaluated.",
                _ref("system", "evaluation_every_proposal"),
            ),
            _mapped(
                "choose a set of matrix multiplication targets",
                "Matrix-search evaluation uses a set of matrix-multiplication targets.",
                _ref("matrix", "section3_1_multi_seed_evaluation_cascade"),
            ),
            _mapped(
                "run the algorithm, initialized with multiple random seeds",
                "Each matrix target is run from multiple randomized initializations.",
                _ref("matrix", "section3_1_multi_seed_evaluation_cascade"),
            ),
            _mapped(
                "using the evaluation cascade described in [citation]",
                "The multi-seed matrix runs use the Section 2.4 evaluation cascade.",
                _ref("matrix", "section3_1_multi_seed_evaluation_cascade"),
            ),
        ),
        "tex_prose_sentence_0106": (
            _mapped(
                "the best (lowest) rank achieved on each target",
                "Evaluation records the lowest rank achieved for each matrix target.",
                _ref(
                    "matrix",
                    "section3_1_best_rank_and_seed_hit_fraction",
                ),
            ),
            _mapped(
                "the fraction of seeds that achieved this rank",
                "Evaluation records the fraction of seeds attaining the best rank.",
                _ref(
                    "matrix",
                    "section3_1_best_rank_and_seed_hit_fraction",
                ),
            ),
            _mapped(
                "providing a signal for AlphaEvolve to hill-climb",
                "The matrix metrics provide a signal for evolutionary hill climbing.",
                _ref("system", "section2_evolutionary_metric_improvement"),
            ),
        ),
        "tex_prose_sentence_0107": (
            _mapped(
                "To ensure the exactness of the decomposition and avoid any potential numerical error",
                "Coefficient rounding is intended to ensure exact decompositions and avoid numerical error.",
                _ref(
                    "matrix",
                    "section3_1_integer_half_integer_rounding_exactness",
                ),
            ),
            _mapped(
                "round each element to the nearest integer or the nearest half-integer",
                "Evaluation rounds every decomposition element to an integer or half-integer.",
                _ref(
                    "matrix",
                    "section3_1_integer_half_integer_rounding_exactness",
                ),
            ),
            _mapped(
                "encourage the algorithm to generate near-integral solutions",
                "The matrix prompt is intended to encourage near-integral candidates.",
                _ref(
                    "matrix",
                    "section3_1_natural_language_near_integrality_prompt",
                ),
            ),
            _mapped(
                "include this request in natural language in the LLM's prompt",
                "A natural-language near-integrality request is included in the LLM prompt.",
                _ref(
                    "matrix",
                    "section3_1_natural_language_near_integrality_prompt",
                ),
            ),
        ),
        "tex_prose_sentence_0108": (
            _reviewed_context(
                "In Table [citation] , one can see",
                "The prose directs readers to the matrix-result table.",
                "This is navigation to separately inventoried Table 2 evidence.",
            ),
            _mapped(
                "the various algorithms developed by AlphaEvolve improve the state of the art for 14 different matrix multiplication targets",
                "AlphaEvolve is reported to improve the state of the art on 14 matrix targets.",
                _ref("matrix", "section3_1_fourteen_target_sota_improvements"),
            ),
        ),
        "tex_prose_sentence_0109": (
            _mapped(
                "for multiplying two 4 times 4 matrices, applying the algorithm of [citation] recursively",
                "Recursive application of the Strassen algorithm provides the 4x4 baseline.",
                _ref(
                    "matrix",
                    "section3_1_recursive_strassen_rank49_any_field",
                ),
            ),
            _mapped(
                "rank (number of scalar multiplications) equal to 49",
                "The recursive 4x4 baseline has rank and scalar-multiplication count 49.",
                _ref(
                    "matrix",
                    "section3_1_recursive_strassen_rank49_any_field",
                ),
                _ref(
                    "matrix",
                    "section3_1_tensor_rank_equals_scalar_multiplications",
                ),
            ),
            _mapped(
                "which works over any field",
                "The recursive rank-49 baseline works over any field.",
                _ref(
                    "matrix",
                    "section3_1_recursive_strassen_rank49_any_field",
                ),
            ),
        ),
        "tex_prose_sentence_0110": (
            _mapped(
                "For the very specific case of multiplying in the field with 2 elements, [citation] found an algorithm with rank 47",
                "Prior work found a rank-47 algorithm specifically over the two-element field.",
                _ref("matrix", "section3_1_fawzi_rank47_field_two"),
            ),
        ),
        "tex_prose_sentence_0111": (
            _mapped(
                "For 56 years, designing an algorithm with rank less than 49 over any field with characteristic 0 was an open problem",
                "A characteristic-zero matrix algorithm below rank 49 is reported to have remained open for 56 years.",
                _ref("matrix", "section3_1_fifty_six_year_open_problem"),
            ),
        ),
        "tex_prose_sentence_0112": (
            _mapped(
                "the first method",
                "AlphaEvolve is reported as the first method to achieve the stated complex 4x4 rank.",
                _ref("matrix", "section3_1_first_rank48_complex_4x4"),
            ),
            _mapped(
                "find a rank- 48 algorithm to multiply two 4 times 4 complex-valued matrices",
                "AlphaEvolve is reported to find a rank-48 complex 4x4 matrix-multiplication algorithm.",
                _ref("matrix", "section3_1_first_rank48_complex_4x4"),
            ),
        ),
        "tex_prose_sentence_0113": (
            _reviewed_context(
                "As shown in Figure [citation]",
                "The prose directs readers to the evolved-program diff figure.",
                "This is navigation to separately inventoried Figure 4 evidence.",
            ),
            _mapped(
                "makes significant changes to the initial program",
                "AlphaEvolve is reported to make significant changes to the initial matrix program.",
                _ref("matrix", "section3_1_significant_initial_program_changes"),
            ),
            _mapped(
                "introducing several original ideas",
                "The evolved matrix program is reported to introduce several original ideas.",
                _ref("matrix", "section3_1_original_ideas_increasingly_better"),
            ),
            _mapped(
                "design increasingly better algorithms",
                "The original evolved ideas are reported to produce increasingly better algorithms.",
                _ref("matrix", "section3_1_original_ideas_increasingly_better"),
            ),
        ),
        "tex_prose_sentence_0114": (
            _mapped(
                "most results in Table [citation]",
                "Most Table 2 matrix results were obtained from a simple initial program.",
                _ref("matrix", "section3_1_most_table2_simple_initial_program"),
            ),
            _mapped(
                "including 4, 4, 4",
                "The 4x4x4 result is among the results obtained from a simple initial program.",
                _ref("matrix", "section3_1_most_table2_simple_initial_program"),
            ),
            _mapped(
                "were obtained from a simple initial program",
                "The referenced Table 2 results used a simple initial program.",
                _ref("matrix", "section3_1_most_table2_simple_initial_program"),
            ),
            _mapped(
                "for some parameters, seeding the initial program with our own ideas",
                "Some matrix parameter settings used researcher ideas in the initial program.",
                _ref("matrix", "section3_1_researcher_ideas_boost_performance"),
            ),
            _mapped(
                "adding stochasticity to the evaluation function",
                "Researcher seeding included stochasticity in the evaluation function.",
                _ref("matrix", "section3_1_researcher_ideas_boost_performance"),
            ),
            _mapped(
                "using evolutionary approaches",
                "Researcher seeding included evolutionary approaches.",
                _ref("matrix", "section3_1_researcher_ideas_boost_performance"),
            ),
            _mapped(
                "could further boost performance",
                "Researcher-provided initial ideas are reported to improve performance for some parameters.",
                _ref("matrix", "section3_1_researcher_ideas_boost_performance"),
            ),
            _mapped(
                "highlighting the possibility of scientific collaboration between researchers and AlphaEvolve",
                "The result is presented as evidence for possible researcher-AlphaEvolve scientific collaboration.",
                _ref("matrix", "section3_1_scientific_collaboration_possibility"),
            ),
        ),
    }
)

_PROPOSITION_SPECS.update(
    {
        "tex_prose_sentence_0115": (
            _reviewed_context(
                "A significant frontier in mathematical research",
                "The discovery of optimized mathematical constructions is presented as an important research frontier.",
                "The significance label is author framing rather than a separate implementation requirement.",
                disposition="author_interpretation",
            ),
            _mapped(
                "discovering objects or constructions",
                "The constructive-math task class searches for mathematical objects or constructions.",
                _ref(
                    "math",
                    "section3_2_optimal_near_optimal_construction_frontier",
                ),
            ),
            _mapped(
                "optimal, or near-optimal, properties according to some measure",
                "Constructive-math candidates target optimal or near-optimal values under a declared measure.",
                _ref(
                    "math",
                    "section3_2_optimal_near_optimal_construction_frontier",
                ),
            ),
        ),
        "tex_prose_sentence_0116": (
            _mapped(
                "finding dense packings of geometric shapes",
                "Dense geometric packing is one constructive-math problem class.",
                _ref("math", "section3_2_dense_geometric_packing_example"),
            ),
            _mapped(
                "identifying functions or sets satisfying specific combinatorial",
                "Functions or sets under combinatorial constraints form another problem class.",
                _ref(
                    "math",
                    "section3_2_combinatorial_analytic_constraint_examples",
                ),
            ),
            _mapped(
                "analytic constraints",
                "Functions or sets under analytic constraints form another problem class.",
                _ref(
                    "math",
                    "section3_2_combinatorial_analytic_constraint_examples",
                ),
            ),
        ),
        "tex_prose_sentence_0117": (
            _mapped(
                "Progress often relies on finding a single construction",
                "Progress on a constructive-math problem may depend on one construction.",
                _ref(
                    "math",
                    "section3_2_single_construction_surpasses_known_examples",
                ),
            ),
            _mapped(
                "surpasses all previously known examples",
                "The decisive construction surpasses every previously known example.",
                _ref(
                    "math",
                    "section3_2_single_construction_surpasses_known_examples",
                ),
            ),
            _mapped(
                "establishing new lower",
                "A superior construction can establish a new lower bound on the optimum.",
                _ref("math", "section3_2_new_lower_or_upper_bound"),
            ),
            _mapped(
                "upper bounds for the optimal value",
                "A superior construction can establish a new upper bound on the optimum.",
                _ref("math", "section3_2_new_lower_or_upper_bound"),
            ),
        ),
        "tex_prose_sentence_0118": (
            _reviewed_context(
                "AlphaEvolve serves as a powerful tool",
                "AlphaEvolve is characterized as a powerful constructive-math tool.",
                "The qualitative power label is author interpretation; the search and result claims are mapped separately.",
                disposition="author_interpretation",
            ),
            _mapped(
                "for exploring",
                "AlphaEvolve is used to explore constructive-math search spaces.",
                _ref("math", "section3_2_vast_search_space_exploration"),
            ),
            _mapped(
                "vast search space inherent in these problems",
                "The targeted constructive-math problems have vast search spaces.",
                _ref("math", "section3_2_vast_search_space_exploration"),
            ),
            _mapped(
                "successfully tackling a diverse array of open mathematical challenges",
                "AlphaEvolve is reported to tackle diverse open mathematical challenges successfully.",
                _ref("math", "section3_2_diverse_open_challenges"),
            ),
        ),
        "tex_prose_sentence_0119": (
            _reviewed_context(
                "To assess its capabilities",
                "The constructive-math portfolio is presented as a capability assessment.",
                "This states the experiment's purpose rather than an additional system requirement.",
            ),
            _mapped(
                "a curated set",
                "The mathematical evaluation portfolio is curated.",
                _ref("math", "section3_2_over_fifty_problem_instances"),
            ),
            _mapped(
                "over 50 mathematical problems",
                "The reported portfolio contains more than 50 mathematical problems.",
                _ref("math", "section3_2_over_fifty_problem_instances"),
            ),
            _mapped(
                "more than five different branches of mathematics",
                "The reported portfolio spans more than five mathematical branches.",
                _ref("math", "section3_2_more_than_five_branches"),
            ),
            _mapped(
                "including analysis",
                "Analysis is one named portfolio branch.",
                _ref("math", "section3_2_named_branch_examples"),
            ),
            _mapped(
                "combinatorics",
                "Combinatorics is one named portfolio branch.",
                _ref("math", "section3_2_named_branch_examples"),
            ),
            _mapped(
                "number theory",
                "Number theory is one named portfolio branch.",
                _ref("math", "section3_2_named_branch_examples"),
            ),
            _mapped(
                "geometry",
                "Geometry is one named portfolio branch.",
                _ref("math", "section3_2_named_branch_examples"),
            ),
            _mapped(
                "numerous specific parameter settings",
                "The reported portfolio evaluates numerous parameter settings.",
                _ref("math", "section3_2_numerous_parameter_settings"),
            ),
            _mapped(
                "different dimensions",
                "Different dimensions are one evaluated parameter family.",
                _ref("math", "section3_2_numerous_parameter_settings"),
            ),
            _mapped(
                "sizes",
                "Different sizes are one evaluated parameter family.",
                _ref("math", "section3_2_numerous_parameter_settings"),
            ),
        ),
        "tex_prose_sentence_0120": (
            _mapped(
                "In 75 percent of the cases AlphaEvolve rediscovered the best known constructions",
                "AlphaEvolve is reported to rediscover best-known constructions in 75 percent of cases.",
                _ref("math", "section3_2_seventy_five_percent_rediscovery"),
            ),
            _mapped(
                "in 20 percent of the cases it discovered a new object",
                "AlphaEvolve is reported to discover a new object in 20 percent of cases.",
                _ref("math", "section3_2_twenty_percent_sota_improvement"),
            ),
            _mapped(
                "better than a previously known best construction",
                "The reported new objects improve on previous best-known constructions.",
                _ref("math", "section3_2_twenty_percent_sota_improvement"),
            ),
            _mapped(
                "thereby improving the SOTA",
                "The reported 20-percent cases improve the state of the art.",
                _ref("math", "section3_2_twenty_percent_sota_improvement"),
            ),
        ),
        "tex_prose_sentence_0121": (
            _mapped(
                "In all these cases, the initial starting point was a simple or a random construction",
                "Every aggregate constructive-math case is reported to start from a simple or random construction.",
                _ref("math", "section3_2_all_simple_or_random_starts"),
            ),
        ),
        "tex_prose_sentence_0122": (
            _mapped(
                "These results underscore AlphaEvolve's broad potential",
                "The reported results are presented as evidence of broad mathematical potential.",
                _ref("math", "section3_2_broad_versatile_math_potential"),
            ),
            _mapped(
                "a versatile tool for mathematical research",
                "AlphaEvolve is presented as a versatile mathematical-research tool.",
                _ref("math", "section3_2_broad_versatile_math_potential"),
            ),
        ),
        "tex_prose_sentence_0123": (
            _mapped(
                "A significant advantage of the AlphaEvolve configuration used here is its versatility",
                "The reported AlphaEvolve configuration claims versatility as a significant advantage.",
                _ref("math", "section3_2_versatility_and_speed_advantage"),
            ),
            _mapped(
                "speed of application",
                "The reported AlphaEvolve configuration is claimed to be fast to apply.",
                _ref("math", "section3_2_versatility_and_speed_advantage"),
            ),
        ),
        "tex_prose_sentence_0124": (
            _mapped(
                "focused on evolving heuristic search programs",
                "The core constructive-math methodology evolves heuristic search programs.",
                _ref(
                    "math",
                    "section3_2_evolve_heuristics_not_direct_constructions",
                ),
            ),
            _reviewed_context(
                "detailed below",
                "The prose points forward to the detailed search methodology.",
                "This is document navigation rather than a separate implementation requirement.",
            ),
            _mapped(
                "rapidly deployed",
                "The constructive-math methodology is reported to deploy rapidly.",
                _ref("math", "section3_2_rapid_deployment"),
            ),
            _mapped(
                "a diverse range of mathematical construction problems",
                "The methodology is reported to cover diverse construction problems.",
                _ref(
                    "math",
                    "section3_2_diverse_constructions_and_conjectures",
                ),
            ),
            _mapped(
                "conjectures",
                "The methodology is reported to cover mathematical conjectures.",
                _ref(
                    "math",
                    "section3_2_diverse_constructions_and_conjectures",
                ),
            ),
            _mapped(
                "often requiring less initial problem-specific expert tailoring compared to traditional bespoke approaches",
                "The methodology is reported often to need less initial task-specific expertise than bespoke approaches.",
                _ref(
                    "math",
                    "section3_2_less_expert_tailoring_than_bespoke",
                ),
            ),
        ),
        "tex_prose_sentence_0125": (
            _mapped(
                "deep mathematical insight naturally aids in problem formulation",
                "Deep mathematical expertise helps formulate constructive-math problems.",
                _ref("math", "section3_2_deep_insight_aids_formulation"),
            ),
            _mapped(
                "search space definition",
                "Deep mathematical expertise helps define the search space.",
                _ref("math", "section3_2_deep_insight_aids_formulation"),
            ),
            _mapped(
                "often demonstrates a capacity to autonomously discover effective search patterns",
                "AlphaEvolve is reported often to demonstrate autonomous discovery of effective search patterns.",
                _ref(
                    "math",
                    "section3_2_autonomous_search_patterns_and_attack_strategies",
                ),
            ),
            _mapped(
                "attack strategies",
                "AlphaEvolve is reported to discover effective attack strategies autonomously.",
                _ref(
                    "math",
                    "section3_2_autonomous_search_patterns_and_attack_strategies",
                ),
            ),
            _mapped(
                "by identifying subtle structures within the problem landscape",
                "The reported autonomous strategies arise from identifying subtle problem structure.",
                _ref("math", "section3_2_identifies_subtle_structures"),
            ),
        ),
        "tex_prose_sentence_0126": (
            _mapped(
                "This allows for",
                "Autonomous pattern and structure discovery is claimed to enable the reported exploration regime.",
                _ref("math", "section3_2_efficient_large_scale_exploration"),
            ),
            _mapped(
                "efficient",
                "The methodology is reported to explore mathematical problems efficiently.",
                _ref("math", "section3_2_efficient_large_scale_exploration"),
            ),
            _mapped(
                "large-scale exploration",
                "The methodology is reported to support large-scale exploration.",
                _ref("math", "section3_2_efficient_large_scale_exploration"),
            ),
            _mapped(
                "across many different problems",
                "The reported large-scale exploration spans many different problems.",
                _ref("math", "section3_2_efficient_large_scale_exploration"),
            ),
        ),
        "tex_prose_sentence_0127": (
            _reviewed_context(
                "The key methodological innovation enabling these discoveries",
                "Heuristic-program evolution is characterized as the key enabler of the reported discoveries.",
                "The key-enabler label is author interpretation; the actual search representation is mapped separately.",
                disposition="author_interpretation",
            ),
            _mapped(
                "evolve heuristic search algorithms",
                "AlphaEvolve evolves heuristic search algorithms for constructive math.",
                _ref(
                    "math",
                    "section3_2_evolve_heuristics_not_direct_constructions",
                ),
            ),
            _mapped(
                "rather than directly evolving the constructions themselves",
                "The methodology evolves search heuristics instead of direct construction payloads.",
                _ref(
                    "math",
                    "section3_2_evolve_heuristics_not_direct_constructions",
                ),
            ),
        ),
        "tex_prose_sentence_0128": (
            _mapped(
                "For many problems",
                "The reported constructive-math setup uses iterative refinement across many problems.",
                _ref("math", "section3_2_iterative_refinement_strategy"),
            ),
            _mapped(
                "we employed an iterative refinement strategy",
                "The constructive-math search uses an iterative refinement strategy.",
                _ref("math", "section3_2_iterative_refinement_strategy"),
            ),
            _mapped(
                "particularly those with fast objective function evaluations",
                "Iterative refinement is particularly applicable when objective evaluation is fast.",
                _ref(
                    "math",
                    "section3_2_fast_objective_evaluations_common_in_math",
                ),
            ),
            _mapped(
                "which are common in mathematics",
                "Fast objective-function evaluations are reported to be common in mathematics.",
                _ref(
                    "math",
                    "section3_2_fast_objective_evaluations_common_in_math",
                ),
            ),
        ),
        "tex_prose_sentence_0129": (
            _mapped(
                "Each generation of AlphaEvolve was tasked with evolving a program",
                "Every generation evolves a program in the reported constructive-math setup.",
                _ref(
                    "math",
                    "section3_2_each_generation_evolves_search_heuristic_program",
                ),
            ),
            _mapped(
                "representing a search heuristic",
                "The evolved program represents a search heuristic.",
                _ref(
                    "math",
                    "section3_2_each_generation_evolves_search_heuristic_program",
                ),
            ),
        ),
        "tex_prose_sentence_0130": (
            _mapped(
                "given a fixed time budget",
                "Each evolved heuristic receives a fixed execution-time budget.",
                _ref("math", "section3_2_fixed_time_budget_1000_seconds"),
            ),
            _mapped(
                "1000 seconds",
                "One reported fixed-budget example is 1000 seconds.",
                _ref("math", "section3_2_fixed_time_budget_1000_seconds"),
            ),
            _mapped(
                "shown the best construction",
                "Each evolved heuristic receives an incumbent best construction.",
                _ref("math", "section3_2_previous_best_construction_handoff"),
            ),
            _mapped(
                "found by the previous best heuristic",
                "The incumbent construction comes from the previous best heuristic.",
                _ref("math", "section3_2_previous_best_construction_handoff"),
            ),
        ),
        "tex_prose_sentence_0131": (
            _mapped(
                "leverage this starting point",
                "The evolved heuristic starts from the handed-off incumbent construction.",
                _ref("math", "section3_2_improve_starting_point_within_budget"),
            ),
            _mapped(
                "the allotted time",
                "The evolved heuristic must operate within its allotted time.",
                _ref("math", "section3_2_improve_starting_point_within_budget"),
            ),
            _mapped(
                "find an even better construction",
                "The evolved heuristic aims to improve the incumbent construction.",
                _ref("math", "section3_2_improve_starting_point_within_budget"),
            ),
        ),
        "tex_prose_sentence_0132": (
            _mapped(
                "selects for heuristics",
                "Evolution selects among constructive-math heuristics.",
                _ref(
                    "math",
                    "section3_2_select_high_quality_solution_improvers",
                ),
            ),
            _mapped(
                "effective at improving",
                "Heuristic selection favors demonstrated incumbent improvement.",
                _ref(
                    "math",
                    "section3_2_select_high_quality_solution_improvers",
                ),
            ),
            _mapped(
                "already high-quality solutions",
                "The selection target includes already high-quality incumbent solutions.",
                _ref(
                    "math",
                    "section3_2_select_high_quality_solution_improvers",
                ),
            ),
        ),
        "tex_prose_sentence_0133": (
            _mapped(
                "final constructions were often the result of a sequence",
                "Final constructions often result from an ordered heuristic sequence.",
                _ref("math", "section3_2_sequence_of_specialized_heuristics"),
            ),
            _mapped(
                "different, specialized heuristics",
                "The reported sequence contains distinct specialized heuristics.",
                _ref("math", "section3_2_sequence_of_specialized_heuristics"),
            ),
            _mapped(
                "discovered by AlphaEvolve",
                "AlphaEvolve discovers the specialized heuristic stages.",
                _ref("math", "section3_2_sequence_of_specialized_heuristics"),
            ),
            _mapped(
                "early heuristics proficient at making large gains",
                "Early heuristic stages are reported to make large gains.",
                _ref("math", "section3_2_early_broad_gain_heuristics"),
            ),
            _mapped(
                "random",
                "Early heuristic stages can begin from random states.",
                _ref("math", "section3_2_early_broad_gain_heuristics"),
            ),
            _mapped(
                "simple initial states",
                "Early heuristic stages can begin from simple initial states.",
                _ref("math", "section3_2_early_broad_gain_heuristics"),
            ),
            _mapped(
                "later heuristics adept at fine-tuning",
                "Later heuristic stages are reported to perform fine tuning.",
                _ref("math", "section3_2_late_fine_tuning_heuristics"),
            ),
            _mapped(
                "near-optimal configurations",
                "Later heuristic stages target near-optimal configurations.",
                _ref("math", "section3_2_late_fine_tuning_heuristics"),
            ),
        ),
        "tex_prose_sentence_0134": (
            _mapped(
                "automated discovery",
                "AlphaEvolve automates discovery of the reported search strategies.",
                _ref(
                    "math",
                    "section3_2_multi_stage_strategy_hard_to_replicate_manually",
                ),
            ),
            _mapped(
                "multi-stage",
                "The discovered search strategies contain multiple stages.",
                _ref(
                    "math",
                    "section3_2_multi_stage_strategy_hard_to_replicate_manually",
                ),
            ),
            _mapped(
                "adaptive search strategies",
                "The discovered multi-stage search strategies are adaptive.",
                _ref(
                    "math",
                    "section3_2_multi_stage_strategy_hard_to_replicate_manually",
                ),
            ),
            _mapped(
                "challenging to replicate manually",
                "The reported multi-stage strategies are difficult to reproduce manually.",
                _ref(
                    "math",
                    "section3_2_multi_stage_strategy_hard_to_replicate_manually",
                ),
            ),
            _mapped(
                "proved crucial for surpassing the SOTA",
                "The reported multi-stage strategies are claimed to be crucial for state-of-the-art gains.",
                _ref("math", "section3_2_multi_stage_strategy_crucial_for_sota"),
            ),
        ),
        "tex_prose_sentence_0135": (
            _reviewed_context(
                "Below are high-level descriptions",
                "The prose introduces the following high-level result summaries.",
                "This is document structure rather than a separate implementation requirement.",
            ),
            _reviewed_context(
                "problems where AlphaEvolve yielded new results",
                "The following examples are selected from problems with reported new results.",
                "The specific result claims are dispositioned in the following sentences and result inventory.",
            ),
        ),
        "tex_prose_sentence_0136": (
            _mapped(
                "Full list of problems",
                "Appendix B is reported to contain the full mathematical problem list.",
                _ref("math", "section3_2_full_list_and_details_in_appendix_b"),
            ),
            _mapped(
                "details are provided in Appendix [citation]",
                "Appendix B is reported to contain details for the mathematical problems.",
                _ref("math", "section3_2_full_list_and_details_in_appendix_b"),
            ),
        ),
    }
)

_PROPOSITION_SPECS.update(
    {
        "tex_prose_sentence_0154": (
            _reviewed_context(
                "scientific applications presented in preceding sections",
                "The prose contrasts the following systems results with earlier scientific applications.",
                "This is a cross-section transition rather than a standalone implementation requirement.",
            ),
            _mapped(
                "AlphaEvolve has been used",
                "AlphaEvolve is reported to have been used on infrastructure applications.",
                _ref(
                    "scheduling",
                    "section3_3_mission_critical_infrastructure_real_world_impact",
                ),
            ),
            _mapped(
                "improve performance of mission-critical infrastructure",
                "The reported infrastructure use improves mission-critical performance.",
                _ref(
                    "scheduling",
                    "section3_3_mission_critical_infrastructure_real_world_impact",
                ),
            ),
            _mapped(
                "deliver real-world impact",
                "The reported infrastructure use delivers real-world impact.",
                _ref(
                    "scheduling",
                    "section3_3_mission_critical_infrastructure_real_world_impact",
                ),
            ),
        ),
        "tex_prose_sentence_0155": (
            _mapped(
                "Efficiently scheduling compute jobs",
                "The scheduling problem seeks efficient placement of compute jobs.",
                _ref(
                    "scheduling",
                    "section3_3_1_google_scale_borg_scheduling_problem",
                ),
            ),
            _mapped(
                "onto a cluster of machines",
                "The compute jobs are scheduled onto a machine cluster.",
                _ref(
                    "scheduling",
                    "section3_3_1_google_scale_borg_scheduling_problem",
                ),
            ),
            _mapped(
                "critical optimization problem",
                "Efficient cluster scheduling is characterized as a critical optimization problem.",
                _ref(
                    "scheduling",
                    "section3_3_1_google_scale_borg_scheduling_problem",
                ),
            ),
            _mapped(
                "at the scale of Google's data centers",
                "The reported scheduling problem operates at Google data-center scale.",
                _ref(
                    "scheduling",
                    "section3_3_1_google_scale_borg_scheduling_problem",
                ),
            ),
            _mapped(
                "orchestrated by Borg",
                "Borg orchestrates the referenced Google data centers.",
                _ref(
                    "scheduling",
                    "section3_3_1_google_scale_borg_scheduling_problem",
                ),
            ),
        ),
        "tex_prose_sentence_0156": (
            _mapped(
                "assigning jobs to available machines",
                "The scheduling task assigns jobs to available machines.",
                _ref(
                    "scheduling",
                    "section3_3_1_assign_jobs_from_requirements_and_capacity",
                ),
            ),
            _mapped(
                "job resource requirements",
                "Job resource requirements constrain assignment.",
                _ref(
                    "scheduling",
                    "section3_3_1_assign_jobs_from_requirements_and_capacity",
                ),
            ),
            _mapped(
                "machine capacity",
                "Machine capacity constrains assignment.",
                _ref(
                    "scheduling",
                    "section3_3_1_assign_jobs_from_requirements_and_capacity",
                ),
            ),
        ),
        "tex_prose_sentence_0157": (
            _mapped(
                "Inefficient assignments can result in stranded resources",
                "Inefficient scheduling assignments can strand resources.",
                _ref(
                    "scheduling",
                    "section3_3_1_inefficient_assignments_strand_resources",
                ),
            ),
            _mapped(
                "a machine can no longer accept jobs",
                "A resource imbalance can leave a machine unable to accept jobs.",
                _ref(
                    "scheduling",
                    "section3_3_1_one_resource_exhausted_other_resource_free",
                ),
            ),
            _mapped(
                "run out of one kind of resource",
                "The machine can become unavailable after exhausting one resource type.",
                _ref(
                    "scheduling",
                    "section3_3_1_one_resource_exhausted_other_resource_free",
                ),
            ),
            _mapped(
                "(e.g., memory)",
                "Memory is one example of an exhausted resource.",
                _ref(
                    "scheduling",
                    "section3_3_1_one_resource_exhausted_other_resource_free",
                ),
            ),
            _mapped(
                "still has other resources free",
                "Other machine resources can remain free after one resource is exhausted.",
                _ref(
                    "scheduling",
                    "section3_3_1_one_resource_exhausted_other_resource_free",
                ),
            ),
            _mapped(
                "(e.g., CPU)",
                "CPU is one example of a resource that can remain free.",
                _ref(
                    "scheduling",
                    "section3_3_1_one_resource_exhausted_other_resource_free",
                ),
            ),
        ),
        "tex_prose_sentence_0158": (
            _mapped(
                "Improvements in scheduling efficiency",
                "Scheduling-efficiency improvements are the proposed recovery mechanism.",
                _ref(
                    "scheduling",
                    "section3_3_1_more_jobs_same_compute_footprint",
                ),
            ),
            _mapped(
                "recover these stranded resources",
                "Scheduling-efficiency improvements can recover stranded resources.",
                _ref(
                    "scheduling",
                    "section3_3_1_more_jobs_same_compute_footprint",
                ),
            ),
            _mapped(
                "more jobs to be completed",
                "Recovered resources can allow completion of more jobs.",
                _ref(
                    "scheduling",
                    "section3_3_1_more_jobs_same_compute_footprint",
                ),
            ),
            _mapped(
                "same amount of computational footprint",
                "The additional jobs use the same computational footprint.",
                _ref(
                    "scheduling",
                    "section3_3_1_more_jobs_same_compute_footprint",
                ),
            ),
        ),
        "tex_prose_sentence_0159": (
            _reviewed_context(
                "This recovery is essential",
                "The authors characterize stranded-resource recovery as essential.",
                "The essentiality judgment is author interpretation; the capacity-growth requirement is mapped separately.",
                disposition="author_interpretation",
            ),
            _mapped(
                "accommodate growing compute needs",
                "Resource recovery is intended to accommodate growing compute demand.",
                _ref(
                    "scheduling",
                    "section3_3_1_growth_without_proportional_resource_increase",
                ),
            ),
            _mapped(
                "without a proportional increase in resource consumption",
                "Compute growth is intended to avoid proportional resource-consumption growth.",
                _ref(
                    "scheduling",
                    "section3_3_1_growth_without_proportional_resource_increase",
                ),
            ),
        ),
        "tex_prose_sentence_0160": (
            _mapped(
                "this problem is challenging",
                "The scheduling problem is characterized as challenging.",
                _ref(
                    "scheduling",
                    "section3_3_1_debuggability_scale_and_bin_packing_challenge",
                ),
            ),
            _mapped(
                "typical engineering difficulties",
                "The scheduling problem includes ordinary engineering difficulties.",
                _ref(
                    "scheduling",
                    "section3_3_1_debuggability_scale_and_bin_packing_challenge",
                ),
            ),
            _mapped(
                "debuggability",
                "Debuggability is one scheduling engineering difficulty.",
                _ref(
                    "scheduling",
                    "section3_3_1_debuggability_scale_and_bin_packing_challenge",
                ),
            ),
            _mapped(
                "scale",
                "Scale is one scheduling engineering difficulty.",
                _ref(
                    "scheduling",
                    "section3_3_1_debuggability_scale_and_bin_packing_challenge",
                ),
            ),
            _mapped(
                "classically difficult bin-packing problem",
                "The engineering difficulties compound a classically difficult bin-packing problem.",
                _ref(
                    "scheduling",
                    "section3_3_1_debuggability_scale_and_bin_packing_challenge",
                ),
            ),
        ),
        "tex_prose_sentence_0161": (
            _mapped(
                "framing the online job scheduling problem",
                "The formulation treats online job scheduling as the source problem.",
                _ref(
                    "scheduling",
                    "section3_3_1_online_two_variable_vector_bin_packing",
                ),
            ),
            _mapped(
                "as a vector bin-packing problem",
                "The online scheduler is formulated as vector bin packing.",
                _ref(
                    "scheduling",
                    "section3_3_1_online_two_variable_vector_bin_packing",
                ),
            ),
            _mapped(
                "with two variables",
                "The vector-bin-packing formulation has two variables.",
                _ref(
                    "scheduling",
                    "section3_3_1_online_two_variable_vector_bin_packing",
                ),
            ),
        ),
        "tex_prose_sentence_0162": (
            _mapped(
                "machines represent bins",
                "Machines are represented as vector-bin-packing bins.",
                _ref(
                    "scheduling",
                    "section3_3_1_machines_bins_cpu_memory_capacity",
                ),
            ),
            _mapped(
                "defined capacities",
                "The machine bins have defined capacities.",
                _ref(
                    "scheduling",
                    "section3_3_1_machines_bins_cpu_memory_capacity",
                ),
            ),
            _mapped(
                "CPU",
                "CPU is one machine-capacity dimension.",
                _ref(
                    "scheduling",
                    "section3_3_1_machines_bins_cpu_memory_capacity",
                ),
            ),
            _mapped(
                "memory",
                "Memory is one machine-capacity dimension.",
                _ref(
                    "scheduling",
                    "section3_3_1_machines_bins_cpu_memory_capacity",
                ),
            ),
            _mapped(
                "incoming jobs are items",
                "Incoming jobs are represented as vector-bin-packing items.",
                _ref(
                    "scheduling",
                    "section3_3_1_jobs_items_resource_demands",
                ),
            ),
            _mapped(
                "specific resource demands",
                "The incoming-job items carry specific resource demands.",
                _ref(
                    "scheduling",
                    "section3_3_1_jobs_items_resource_demands",
                ),
            ),
        ),
        "tex_prose_sentence_0163": (
            _mapped(
                "A heuristic function takes as input",
                "A heuristic function consumes scheduling inputs.",
                _ref(
                    "scheduling",
                    "section3_3_1_heuristic_required_and_free_inputs",
                ),
            ),
            _mapped(
                "a pending job",
                "The pending job is one heuristic input entity.",
                _ref(
                    "scheduling",
                    "section3_3_1_heuristic_required_and_free_inputs",
                ),
            ),
            _mapped(
                "CPU and memory requirements",
                "The heuristic receives the pending job's CPU and memory requirements.",
                _ref(
                    "scheduling",
                    "section3_3_1_heuristic_required_and_free_inputs",
                ),
            ),
            _mapped(
                "a potential machine",
                "A potential machine is the other heuristic input entity.",
                _ref(
                    "scheduling",
                    "section3_3_1_heuristic_required_and_free_inputs",
                ),
            ),
            _mapped(
                "CPU and memory availability",
                "The heuristic receives the potential machine's CPU and memory availability.",
                _ref(
                    "scheduling",
                    "section3_3_1_heuristic_required_and_free_inputs",
                ),
            ),
        ),
        "tex_prose_sentence_0164": (
            _mapped(
                "outputs a priority score",
                "The heuristic outputs a priority score.",
                _ref(
                    "scheduling",
                    "section3_3_1_heuristic_outputs_machine_priority",
                ),
            ),
            _mapped(
                "for the machine",
                "The priority score applies to the candidate machine.",
                _ref(
                    "scheduling",
                    "section3_3_1_heuristic_outputs_machine_priority",
                ),
            ),
        ),
        "tex_prose_sentence_0165": (
            _mapped(
                "The Borg scheduler",
                "Borg is the scheduler consuming the heuristic score.",
                _ref(
                    "scheduling",
                    "section3_3_1_borg_uses_highest_priority_among_other_objectives",
                ),
            ),
            _mapped(
                "assigns the pending job",
                "Borg assigns the pending job after scoring.",
                _ref(
                    "scheduling",
                    "section3_3_1_borg_uses_highest_priority_among_other_objectives",
                ),
            ),
            _mapped(
                "machine with the highest priority score",
                "The heuristic favors the candidate machine with the highest score.",
                _ref(
                    "scheduling",
                    "section3_3_1_borg_uses_highest_priority_among_other_objectives",
                ),
            ),
            _mapped(
                "determined by the heuristic function",
                "The heuristic function determines the machine-priority score.",
                _ref(
                    "scheduling",
                    "section3_3_1_borg_uses_highest_priority_among_other_objectives",
                ),
            ),
            _mapped(
                "among other objectives",
                "Borg uses scheduler objectives beyond the heuristic ranking.",
                _ref(
                    "scheduling",
                    "section3_3_1_borg_uses_highest_priority_among_other_objectives",
                ),
            ),
        ),
        "tex_prose_sentence_0166": (
            _mapped(
                "only influences the ranking of machines",
                "The heuristic is restricted to ranking candidate machines.",
                _ref(
                    "scheduling",
                    "section3_3_1_rank_only_borg_feasible_machines",
                ),
            ),
            _mapped(
                "already determined by Borg",
                "Borg determines the candidate-machine set before heuristic ranking.",
                _ref(
                    "scheduling",
                    "section3_3_1_rank_only_borg_feasible_machines",
                ),
            ),
            _mapped(
                "to be available",
                "Borg limits ranking to machines it considers available.",
                _ref(
                    "scheduling",
                    "section3_3_1_rank_only_borg_feasible_machines",
                ),
            ),
            _mapped(
                "capable of running each pending job",
                "Borg limits ranking to machines capable of running the pending job.",
                _ref(
                    "scheduling",
                    "section3_3_1_rank_only_borg_feasible_machines",
                ),
            ),
            _mapped(
                "scheduling decisions are effectively correct by construction",
                "The rank-only feasibility boundary is claimed to make scheduling decisions effectively correct by construction.",
                _ref(
                    "scheduling",
                    "section3_3_1_effectively_correct_by_construction",
                ),
            ),
        ),
        "tex_prose_sentence_0167": (
            _mapped(
                "An early version of AlphaEvolve was used",
                "An early AlphaEvolve version was used for scheduling discovery.",
                _ref("scheduling", "section3_3_1_early_alphaevolve_version"),
            ),
            _mapped(
                "discover a remarkably simple yet effective heuristic function",
                "AlphaEvolve is reported to discover a scheduling heuristic.",
                _ref(
                    "scheduling",
                    "section3_3_1_simple_effective_heuristic_discovery",
                ),
            ),
            _mapped(
                "remarkably simple",
                "The discovered scheduling heuristic is characterized as remarkably simple.",
                _ref(
                    "scheduling",
                    "section3_3_1_simple_effective_heuristic_discovery",
                ),
            ),
            _mapped(
                "effective heuristic function",
                "The discovered scheduling heuristic is reported to be effective.",
                _ref(
                    "scheduling",
                    "section3_3_1_simple_effective_heuristic_discovery",
                ),
            ),
            _reviewed_context(
                "shown in [citation]",
                "The prose points to Figure 6 for the heuristic function.",
                "This is a figure locator; Figure 6 code and visual semantics are dispositioned separately.",
            ),
            _mapped(
                "evolving from the existing one in production",
                "The discovered heuristic evolved from the production incumbent.",
                _ref(
                    "scheduling",
                    "section3_3_1_evolved_from_production_incumbent",
                ),
            ),
        ),
        "tex_prose_sentence_0168": (
            _mapped(
                "a simulator of our data centers",
                "The scheduling evaluation uses a data-center simulator.",
                _ref(
                    "scheduling",
                    "section3_3_1_historical_fleet_snapshot_simulator_feedback",
                ),
            ),
            _mapped(
                "provide feedback to AlphaEvolve",
                "The data-center simulator provides AlphaEvolve feedback.",
                _ref(
                    "scheduling",
                    "section3_3_1_historical_fleet_snapshot_simulator_feedback",
                ),
            ),
            _mapped(
                "historical snapshots",
                "Simulator feedback is based on historical snapshots.",
                _ref(
                    "scheduling",
                    "section3_3_1_historical_fleet_snapshot_simulator_feedback",
                ),
            ),
            _mapped(
                "workloads",
                "The historical simulator snapshots include workloads.",
                _ref(
                    "scheduling",
                    "section3_3_1_historical_fleet_snapshot_simulator_feedback",
                ),
            ),
            _mapped(
                "capacity",
                "The historical simulator snapshots include capacity.",
                _ref(
                    "scheduling",
                    "section3_3_1_historical_fleet_snapshot_simulator_feedback",
                ),
            ),
            _mapped(
                "across Google",
                "The historical snapshots span Google's fleet.",
                _ref(
                    "scheduling",
                    "section3_3_1_historical_fleet_snapshot_simulator_feedback",
                ),
            ),
        ),
        "tex_prose_sentence_0169": (
            _mapped(
                "measure the performance of AlphaEvolve's heuristic function",
                "The evolved scheduling heuristic is measured on a test dataset.",
                _ref(
                    "scheduling",
                    "section3_3_1_unseen_recent_workload_capacity_generalization",
                ),
            ),
            _mapped(
                "unseen test dataset",
                "The scheduling test dataset is unseen during evolution.",
                _ref(
                    "scheduling",
                    "section3_3_1_unseen_recent_workload_capacity_generalization",
                ),
            ),
            _mapped(
                "recent workloads",
                "The unseen scheduling test dataset contains recent workloads.",
                _ref(
                    "scheduling",
                    "section3_3_1_unseen_recent_workload_capacity_generalization",
                ),
            ),
            _mapped(
                "capacity",
                "The unseen scheduling test dataset contains capacity data.",
                _ref(
                    "scheduling",
                    "section3_3_1_unseen_recent_workload_capacity_generalization",
                ),
            ),
            _mapped(
                "ensure generalization",
                "The unseen recent test set is intended to test generalization.",
                _ref(
                    "scheduling",
                    "section3_3_1_unseen_recent_workload_capacity_generalization",
                ),
            ),
        ),
        "tex_prose_sentence_0170": (
            _mapped(
                "AlphaEvolve's heuristic function outperforms the one in production",
                "The evolved heuristic is reported to outperform the production incumbent.",
                _ref(
                    "scheduling",
                    "section3_3_1_outperforms_production_heuristic",
                ),
            ),
            _mapped(
                "rolled out AlphaEvolve's heuristic function",
                "The evolved heuristic was rolled out after outperforming the incumbent.",
                _ref("scheduling", "section3_3_1_entire_fleet_rollout"),
            ),
            _mapped(
                "to the entire fleet",
                "The reported scheduling rollout covered the entire fleet.",
                _ref("scheduling", "section3_3_1_entire_fleet_rollout"),
            ),
        ),
        "tex_prose_sentence_0171": (
            _mapped(
                "Post-deployment measurements",
                "The reported scheduling result uses post-deployment measurements.",
                _ref(
                    "scheduling",
                    "section3_3_1_post_deployment_confirms_simulator",
                ),
            ),
            _mapped(
                "across Google",
                "The post-deployment measurements span Google's fleet.",
                _ref(
                    "scheduling",
                    "section3_3_1_post_deployment_confirms_simulator",
                ),
            ),
            _mapped(
                "confirmed the simulator results",
                "The post-deployment fleet measurements are reported to confirm simulator results.",
                _ref(
                    "scheduling",
                    "section3_3_1_post_deployment_confirms_simulator",
                ),
            ),
            _mapped(
                "continuously recovers",
                "The deployed heuristic is reported to recover resources continuously.",
                _ref(
                    "scheduling",
                    "section3_3_1_continuous_average_point_7_percent_recovery",
                ),
            ),
            _mapped(
                "on average 0.7 percent",
                "The reported average recovered-resource fraction is 0.7 percent.",
                _ref(
                    "scheduling",
                    "section3_3_1_continuous_average_point_7_percent_recovery",
                ),
            ),
            _mapped(
                "fleet-wide compute resources",
                "The 0.7-percent recovery metric applies to fleet-wide compute resources.",
                _ref(
                    "scheduling",
                    "section3_3_1_continuous_average_point_7_percent_recovery",
                ),
            ),
            _mapped(
                "which would otherwise be stranded",
                "The recovered compute resources would otherwise be stranded.",
                _ref(
                    "scheduling",
                    "section3_3_1_recovered_resources_otherwise_stranded",
                ),
            ),
        ),
        "tex_prose_sentence_0172": (
            _mapped(
                "AlphaEvolve was chosen over a deep reinforcement learning approach",
                "AlphaEvolve's code heuristic was selected over deep reinforcement learning.",
                _ref(
                    "scheduling",
                    "section3_3_1_chosen_over_deep_reinforcement_learning",
                ),
            ),
            _mapped(
                "code solution",
                "The selected AlphaEvolve scheduling output is a code solution.",
                _ref(
                    "scheduling",
                    "section3_3_1_code_solution_better_performance",
                ),
            ),
            _mapped(
                "leads to better performance",
                "The code solution is reported to outperform the deep-RL approach.",
                _ref(
                    "scheduling",
                    "section3_3_1_code_solution_better_performance",
                ),
            ),
            _mapped(
                "interpretability",
                "Interpretability is a reported advantage of the code solution.",
                _ref(
                    "scheduling",
                    "section3_3_1_interpretability_advantage",
                ),
            ),
            _mapped(
                "debuggability",
                "Debuggability is a reported advantage of the code solution.",
                _ref("scheduling", "section3_3_1_debuggability_advantage"),
            ),
            _mapped(
                "predictability",
                "Predictability is a reported advantage of the code solution.",
                _ref("scheduling", "section3_3_1_predictability_advantage"),
            ),
            _mapped(
                "ease of deployment",
                "Ease of deployment is a reported advantage of the code solution.",
                _ref(
                    "scheduling",
                    "section3_3_1_ease_of_deployment_advantage",
                ),
            ),
            _mapped(
                "essential qualities for a mission-critical system",
                "The reported operational advantages are characterized as essential for a mission-critical system.",
                _ref(
                    "scheduling",
                    "section3_3_1_mission_critical_operational_qualities",
                ),
            ),
        ),
    }
)


@dataclass(frozen=True)
class AlphaEvolveTexPropositionInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveTexPropositionInventoryBoundaryValidation:
    ok: bool
    schema: str | None
    reviewed_sentence_count: int
    proposition_count: int
    remaining_sentence_count: int
    unmapped_proposition_count: int
    unresolved_reference_count: int
    issues: list[AlphaEvolveTexPropositionInventoryBoundaryIssue]


def alphaevolve_tex_proposition_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Review atomic propositions through retained Section 3.3.2 kernels."""

    root_path = Path(root)
    prose = alphaevolve_tex_prose_inventory_boundary_record(root_path)
    sentence_by_id = {
        record.get("sentence_id"): record
        for record in prose.get("sentence_records", [])
        if isinstance(record, dict) and isinstance(record.get("sentence_id"), str)
    }
    claim_catalog, catalog_errors = _claim_catalog(root_path)
    parse_errors: list[str] = []
    proposition_records: list[dict[str, Any]] = []
    reviewed_sentence_records: list[dict[str, Any]] = []
    proposition_ordinal = 0

    if set(_PROPOSITION_SPECS) != set(EXPECTED_REVIEWED_SENTENCE_IDS):
        parse_errors.append("review_spec_sentence_ids_drift")

    for sentence_id in EXPECTED_REVIEWED_SENTENCE_IDS:
        sentence = sentence_by_id.get(sentence_id)
        if not isinstance(sentence, dict):
            parse_errors.append(f"missing_source_sentence:{sentence_id}")
            continue
        proposition_ids: list[str] = []
        rendered_text = sentence.get("rendered_text")
        if not isinstance(rendered_text, str):
            parse_errors.append(f"invalid_source_sentence_text:{sentence_id}")
            continue
        for sentence_ordinal, spec in enumerate(
            _PROPOSITION_SPECS.get(sentence_id, ()),
            start=1,
        ):
            proposition_ordinal += 1
            proposition_id = f"tex_proposition_{proposition_ordinal:04d}"
            proposition_ids.append(proposition_id)
            quote_count = rendered_text.count(spec.source_quote)
            quote_start = rendered_text.find(spec.source_quote)
            if quote_count != 1:
                parse_errors.append(
                    f"source_quote_occurrence_count:{proposition_id}:{quote_count}"
                )
            claim_refs: list[dict[str, Any]] = []
            for inventory_path, claim_id in spec.claim_refs:
                metadata = claim_catalog.get((inventory_path, claim_id))
                implementation_status = (
                    metadata.get("implementation_status")
                    if isinstance(metadata, dict)
                    else None
                )
                claim_refs.append(
                    {
                        "inventory_path": inventory_path,
                        "claim_id": claim_id,
                        "resolved": metadata is not None,
                        "implementation_status": implementation_status,
                    }
                )
            implementation_relevant = any(
                ref["implementation_status"] != "source_context_only"
                for ref in claim_refs
                if ref["resolved"]
            )
            proposition_records.append(
                {
                    "proposition_id": proposition_id,
                    "sentence_id": sentence_id,
                    "sentence_proposition_ordinal": sentence_ordinal,
                    "source_file": sentence.get("source_file"),
                    "source_line": sentence.get("source_line"),
                    "source_end_line": sentence.get("source_end_line"),
                    "source_quote": spec.source_quote,
                    "source_quote_start": quote_start,
                    "source_quote_end": (
                        quote_start + len(spec.source_quote)
                        if quote_start >= 0
                        else -1
                    ),
                    "source_quote_sha256": hashlib.sha256(
                        spec.source_quote.encode("utf-8")
                    ).hexdigest(),
                    "statement": spec.statement,
                    "disposition": spec.disposition,
                    "claim_refs": claim_refs,
                    "implementation_relevant": implementation_relevant,
                    "review_rationale": spec.rationale,
                }
            )
        reviewed_sentence_records.append(
            {
                "sentence_id": sentence_id,
                "source_file": sentence.get("source_file"),
                "source_line": sentence.get("source_line"),
                "source_text_sha256": sentence.get("source_text_sha256"),
                "rendered_text_sha256": hashlib.sha256(
                    rendered_text.encode("utf-8")
                ).hexdigest(),
                "proposition_count": len(proposition_ids),
                "proposition_ids": proposition_ids,
                "review_status": "manual_static_semantic_decomposition_complete",
            }
        )

    disposition_counts = Counter(
        record["disposition"] for record in proposition_records
    )
    unresolved_reference_count = sum(
        not ref["resolved"]
        for record in proposition_records
        for ref in record["claim_refs"]
    )
    unmapped_proposition_count = disposition_counts["unmapped"]
    reviewed_sentence_count = len(reviewed_sentence_records)
    remaining_sentence_count = max(
        0, EXPECTED_SENTENCE_COUNT - reviewed_sentence_count
    )
    source_files = sorted(
        {
            str(record["source_file"])
            for record in reviewed_sentence_records
            if isinstance(record.get("source_file"), str)
        }
    )
    expected_source_files = [
        "introduction.tex",
        "main.tex",
        "methods.tex",
        "results.tex",
    ]
    source_prose_ready = bool(
        prose.get("schema") == ALPHAEVOLVE_TEX_PROSE_INVENTORY_BOUNDARY_SCHEMA
        and prose.get("prose_disposition_ready") is True
        and prose.get("sentence_count") == EXPECTED_SENTENCE_COUNT
    )
    review_scope_complete = bool(
        source_prose_ready
        and not catalog_errors
        and not parse_errors
        and reviewed_sentence_count == EXPECTED_REVIEWED_SENTENCE_COUNT
        and len(proposition_records) == EXPECTED_PROPOSITION_COUNT
        and source_files == expected_source_files
        and unresolved_reference_count == 0
        and unmapped_proposition_count == 0
    )
    return {
        "schema": ALPHAEVOLVE_TEX_PROPOSITION_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "source_prose_schema": prose.get("schema"),
        "source_prose_boundary_status": prose.get("boundary_status"),
        "source_prose_ready": source_prose_ready,
        "proposition_inventory_ready": review_scope_complete,
        "review_scope_complete": review_scope_complete,
        "whole_paper_semantic_exhaustiveness_claim_ready": False,
        "independent_semantic_review_ready": False,
        "mathematical_correctness_claim_ready": False,
        "result_reproduction_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_errors": sorted(catalog_errors),
        "parse_errors": sorted(parse_errors),
        "source_sentence_count": prose.get("sentence_count", 0),
        "reviewed_sentence_count": reviewed_sentence_count,
        "remaining_sentence_count": remaining_sentence_count,
        "reviewed_sentence_fraction": (
            reviewed_sentence_count / EXPECTED_SENTENCE_COUNT
        ),
        "reviewed_source_files": source_files,
        "remaining_source_files": sorted(
            {
                str(record.get("source_file"))
                for record in prose.get("sentence_records", [])
                if isinstance(record, dict)
                and isinstance(record.get("source_file"), str)
                and record.get("source_file") not in source_files
            }
        ),
        "proposition_count": len(proposition_records),
        "disposition_counts": dict(sorted(disposition_counts.items())),
        "claim_reference_count": sum(
            len(record["claim_refs"]) for record in proposition_records
        ),
        "unique_claim_reference_count": len(
            {
                (ref["inventory_path"], ref["claim_id"])
                for record in proposition_records
                for ref in record["claim_refs"]
            }
        ),
        "implementation_relevant_proposition_count": sum(
            bool(record["implementation_relevant"])
            for record in proposition_records
        ),
        "unmapped_proposition_count": unmapped_proposition_count,
        "unresolved_reference_count": unresolved_reference_count,
        "new_bounded_claim_ids": list(EXPECTED_NEW_BOUNDED_CLAIM_IDS),
        "repaired_sentence_claim_ids": list(
            EXPECTED_REPAIRED_SENTENCE_CLAIM_IDS
        ),
        "reviewed_sentence_records": reviewed_sentence_records,
        "proposition_records": proposition_records,
        "inventory_scope": {
            "included": [
                "all 8 retained Abstract sentences in main.tex",
                "all 29 retained Introduction sentences in introduction.tex",
                "all 61 retained Methods sentences in methods.tex",
                "all 16 retained Section 3.1 matrix-result sentences in results.tex",
                "all 39 retained Section 3.2 sentences in results.tex",
                "all 19 retained Section 3.3 opening and Section 3.3.1 scheduling sentences in results.tex",
                "all 23 retained Section 3.3.2 Gemini kernel-engineering sentences in results.tex",
                "manual atomic-proposition statements and exact rendered-source quote offsets",
                "resolved bounded-claim mappings or explicit context, outlook, and interpretation dispositions",
            ],
            "excluded": [
                "the remaining 207 retained prose sentences",
                "separately audited captions, tables, equations, listings, footnotes, and explicit math constructs",
                "independent second-reviewer semantic agreement",
                "mathematical correctness, citation sufficiency, image-pixel semantics, or result reproduction",
                "AlphaEvolve system parity",
            ],
        },
        "claim_boundary": (
            "This boundary records a single-reviewer atomic-proposition decomposition "
            "for every retained sentence from the Abstract through Section 3.3.2 "
            "Gemini kernel engineering. Complete disposition inside this 195-sentence "
            "scope does not cover the remaining 207 prose "
            "sentences and does not prove independent semantic exhaustiveness, "
            "mathematical correctness, result reproduction, or AlphaEvolve parity."
        ),
    }


def validate_alphaevolve_tex_proposition_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveTexPropositionInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_tex_proposition_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveTexPropositionInventoryBoundaryValidation(
            False, None, 0, 0, EXPECTED_SENTENCE_COUNT, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_tex_proposition_inventory_boundary_record(root)
    issues: list[AlphaEvolveTexPropositionInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_TEX_PROPOSITION_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TeX proposition schema"))
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
    if data.get("source_prose_ready") is not True:
        issues.append(_issue("source_prose_incomplete", "source prose inventory must validate first"))
    if data.get("proposition_inventory_ready") is not True:
        issues.append(_issue("proposition_inventory_incomplete", "scoped proposition inventory is incomplete"))
    if data.get("review_scope_complete") is not True:
        issues.append(
            _issue(
                "review_scope_incomplete",
                "Abstract through Section 3.2 methodology review scope is incomplete",
            )
        )
    for field in (
        "whole_paper_semantic_exhaustiveness_claim_ready",
        "independent_semantic_review_ready",
        "mathematical_correctness_claim_ready",
        "result_reproduction_claim_ready",
        "alphaevolve_parity_claim_ready",
    ):
        if data.get(field) is not False:
            issues.append(_issue(f"{field}_overclaim", f"{field} must remain false"))
    for field in (
        "source_prose_schema",
        "source_prose_boundary_status",
        "source_errors",
        "parse_errors",
        "source_sentence_count",
        "reviewed_sentence_count",
        "remaining_sentence_count",
        "reviewed_sentence_fraction",
        "reviewed_source_files",
        "remaining_source_files",
        "proposition_count",
        "disposition_counts",
        "claim_reference_count",
        "unique_claim_reference_count",
        "implementation_relevant_proposition_count",
        "unmapped_proposition_count",
        "unresolved_reference_count",
        "new_bounded_claim_ids",
        "repaired_sentence_claim_ids",
        "reviewed_sentence_records",
        "proposition_records",
        "inventory_scope",
        "claim_boundary",
    ):
        if data.get(field) != expected.get(field):
            issues.append(
                _issue(
                    f"invalid_{field}",
                    f"{field} does not match the reviewed source boundary",
                )
            )
    if expected.get("source_errors") or expected.get("parse_errors"):
        issues.append(_issue("source_or_parse_errors", "source, claim, or proposition parsing reported errors"))
    return AlphaEvolveTexPropositionInventoryBoundaryValidation(
        ok=not issues,
        schema=data.get("schema") if isinstance(data.get("schema"), str) else None,
        reviewed_sentence_count=(
            data.get("reviewed_sentence_count")
            if isinstance(data.get("reviewed_sentence_count"), int)
            else 0
        ),
        proposition_count=(
            data.get("proposition_count")
            if isinstance(data.get("proposition_count"), int)
            else 0
        ),
        remaining_sentence_count=(
            data.get("remaining_sentence_count")
            if isinstance(data.get("remaining_sentence_count"), int)
            else EXPECTED_SENTENCE_COUNT
        ),
        unmapped_proposition_count=(
            data.get("unmapped_proposition_count")
            if isinstance(data.get("unmapped_proposition_count"), int)
            else 0
        ),
        unresolved_reference_count=(
            data.get("unresolved_reference_count")
            if isinstance(data.get("unresolved_reference_count"), int)
            else 0
        ),
        issues=issues,
    )


def render_alphaevolve_tex_proposition_inventory_boundary_summary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> str:
    validation = validate_alphaevolve_tex_proposition_inventory_boundary(
        boundary,
        root=root,
    )
    rows = [
        ("schema_status", "ok" if validation.schema else "missing"),
        ("reviewed_sentence_count", validation.reviewed_sentence_count),
        ("proposition_count", validation.proposition_count),
        ("remaining_sentence_count", validation.remaining_sentence_count),
        ("unmapped_proposition_count", validation.unmapped_proposition_count),
        ("unresolved_reference_count", validation.unresolved_reference_count),
        ("validation_status", "ok" if validation.ok else "issues"),
    ]
    lines = [
        "# AlphaEvolve TeX proposition inventory boundary",
        "",
        "| field | value |",
        "| --- | --- |",
        *(f"| {field} | {value} |" for field, value in rows),
    ]
    if validation.issues:
        lines.extend(
            [
                "",
                "## Issues",
                "",
                *(f"- `{issue.code}`: {issue.message}" for issue in validation.issues),
            ]
        )
    return "\n".join(lines) + "\n"


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[
    dict[str, Any] | None,
    list[AlphaEvolveTexPropositionInventoryBoundaryIssue],
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
    return None, [_issue("invalid_shape", "TeX proposition inventory must be an object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveTexPropositionInventoryBoundaryIssue:
    return AlphaEvolveTexPropositionInventoryBoundaryIssue(code, message)
