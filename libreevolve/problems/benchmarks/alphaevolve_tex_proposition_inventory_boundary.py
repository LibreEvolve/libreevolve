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
    "libreevolve.alphaevolve_tex_proposition_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "abstract_and_introduction_proposition_review_complete_without_"
    "remaining_paper_or_independent_semantic_exhaustiveness"
)
EXPECTED_REVIEWED_SENTENCE_COUNT = 37
EXPECTED_PROPOSITION_COUNT = 93
EXPECTED_REVIEWED_SENTENCE_IDS = tuple(
    f"tex_prose_sentence_{ordinal:04d}" for ordinal in range(1, 38)
)
EXPECTED_NEW_BOUNDED_CLAIM_IDS = (
    "introduction_algorithm_search_outperforms_direct_solution_search",
)
EXPECTED_REPAIRED_SENTENCE_CLAIM_IDS = (
    "abstract_complex_4x4_matrix_48_multiplications",
    "introduction_complex_4x4_matrix_48_multiplications",
    "introduction_erdos_minimum_overlap_result",
    "introduction_seventy_five_percent_math_best_known",
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
    """Review atomic propositions in retained Abstract and Introduction prose."""

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
    expected_source_files = ["introduction.tex", "main.tex"]
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
                "manual atomic-proposition statements and exact rendered-source quote offsets",
                "resolved bounded-claim mappings or explicit context, outlook, and interpretation dispositions",
            ],
            "excluded": [
                "the remaining 365 retained prose sentences",
                "separately audited captions, tables, equations, listings, footnotes, and explicit math constructs",
                "independent second-reviewer semantic agreement",
                "mathematical correctness, citation sufficiency, image-pixel semantics, or result reproduction",
                "AlphaEvolve system parity",
            ],
        },
        "claim_boundary": (
            "This boundary records a single-reviewer atomic-proposition decomposition "
            "for every retained Abstract and Introduction sentence. Complete disposition "
            "inside this 37-sentence scope does not cover the remaining 365 prose "
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
        issues.append(_issue("review_scope_incomplete", "Abstract and Introduction review scope is incomplete"))
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
