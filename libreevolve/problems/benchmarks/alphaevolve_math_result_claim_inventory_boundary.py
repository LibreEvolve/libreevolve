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


ALPHAEVOLVE_MATH_RESULT_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_math_result_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "section_3_2_figure_5_claim_inventory_complete_without_"
    "appendix_b_detail_or_result_reproduction"
)
EXPECTED_CLAIM_COUNT = 63
IMPLEMENTED_STATUS = "implemented_local"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)
FALSE_VERIFICATION_ATTRIBUTION = (
    "In all these cases, results were verified according to their provided "
    "mathematical definitions."
)
ACTUAL_IN_ALL_CASES_TEXT = (
    "In all these cases, the initial starting point was a simple or a random "
    "construction."
)


_TODO_SPECS = {
    "appendix_results": (
        "docs/todo/code.md",
        "Add Appendix B per-result metric and value provenance.",
    ),
    "autocorrelation": (
        "docs/todo/code.md",
        "Add Appendix B.1-B.3 autocorrelation step-function provenance.",
    ),
    "benchmark_fixtures": (
        "docs/todo/code.md",
        "Connect benchmark-grade fixtures to hardening and scope reports.",
    ),
    "circle_packing": (
        "docs/todo/code.md",
        "Add Appendix B.12-B.13 circle/rectangle sum-of-radii provenance.",
    ),
    "deployment": (
        "docs/todo/code.md",
        "Add constructive-math deployment, tailoring, and strategy-discovery",
    ),
    "distance": (
        "docs/todo/code.md",
        "Add Appendix B.8 point-set distance-certificate provenance.",
    ),
    "erdos": (
        "docs/todo/code.md",
        "Add Appendix B.5 minimum-overlap step-function provenance.",
    ),
    "figure5": (
        "docs/todo/code.md",
        "Add Figure 5 construction-exhibit provenance and visual artifacts.",
    ),
    "figure5_b12": (
        "docs/todo/code.md",
        "Add Figure 5 versus Appendix B.12 sum-of-radii precision provenance.",
    ),
    "figure5_reconciliation": (
        "docs/todo/code.md",
        "Add Figure 5-to-Appendix B result mapping and precision reconciliation.",
    ),
    "formulation": (
        "docs/todo/code.md",
        "Populate expert-reviewed problem-formulation metadata for benchmark definitions.",
    ),
    "handoff": (
        "docs/todo/code.md",
        "Add incumbent-construction handoff contracts for heuristic-search",
    ),
    "heilbronn": (
        "docs/todo/code.md",
        "Add Appendix B.9-B.10 Heilbronn minimum-area provenance.",
    ),
    "hexagon": (
        "docs/todo/code.md",
        "Add Appendix B.7 regular-hexagon packing provenance.",
    ),
    "kissing": (
        "docs/todo/code.md",
        "Add kissing-number lemma certificate provenance for Appendix B.11.",
    ),
    "math_outcomes": (
        "docs/todo/code.md",
        "Add aggregate constructive-math outcome coverage reports.",
    ),
    "paper_artifacts": (
        "docs/todo/code.md",
        "Add paper-artifact creator and assembler provenance for figures and",
    ),
    "stages": (
        "docs/todo/code.md",
        "Add constructive-math heuristic-stage sequence provenance.",
    ),
    "starting": (
        "docs/todo/code.md",
        "Add simple/random starting-construction provenance for constructive-math",
    ),
    "sums": (
        "docs/todo/code.md",
        "Add Appendix B.6 finite-set witness provenance.",
    ),
    "uncertainty": (
        "docs/todo/code.md",
        "Add Appendix B.4 Hermite-polynomial certificate provenance.",
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
    todo_ids: tuple[str, ...] = (),
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


def _figure_row(
    claim_id: str,
    source_anchor: str,
    claim: str,
    family_todo: str,
) -> dict[str, Any]:
    todo_ids = ("figure5", "figure5_reconciliation", family_todo)
    if claim_id == "figure5_sum_radii_2_6340_to_2_6358":
        todo_ids += ("figure5_b12",)
    return _claim(
        claim_id,
        "figure_5",
        12,
        source_anchor,
        claim,
        "figure_5_result_row",
        "not_demonstrated",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        todo_ids,
    )


MATH_RESULT_CLAIM_SPECS = (
    _claim(
        "section3_2_optimal_near_optimal_construction_frontier",
        "section_3_2",
        10,
        "discovering objects or constructions that possess optimal, or near-optimal, properties according to some measure",
        "Support discovery of objects or constructions optimized against a declared measure.",
        "math_research_context",
        "partially_implemented",
        (
            "papers/programmatic_representation_boundary.json",
            "papers/benchmark_fixture_readiness_boundary.json",
        ),
        ("benchmark_fixtures",),
    ),
    _claim(
        "section3_2_dense_geometric_packing_example",
        "section_3_2",
        10,
        "finding dense packings of geometric shapes",
        "Cover dense geometric packing with benchmark-grade construction evidence.",
        "math_research_context",
        "partially_implemented",
        (
            "papers/example_benchmark_scope.json",
            "libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",
        ),
        ("benchmark_fixtures", "circle_packing"),
    ),
    _claim(
        "section3_2_combinatorial_analytic_constraint_examples",
        "section_3_2",
        10,
        "identifying functions or sets satisfying specific combinatorial or analytic constraints",
        "Cover function and set constructions with analytic or combinatorial constraints.",
        "math_research_context",
        "partially_implemented",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("benchmark_fixtures", "appendix_results"),
    ),
    _claim(
        "section3_2_single_construction_surpasses_known_examples",
        "section_3_2",
        10,
        "finding a single construction that surpasses all previously known examples",
        "Demonstrate a construction that surpasses a sourced previous best.",
        "math_research_context",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes", "appendix_results"),
    ),
    _claim(
        "section3_2_new_lower_or_upper_bound",
        "section_3_2",
        10,
        "establishing new lower or upper bounds for the optimal value",
        "Certify new lower or upper bounds from discovered constructions.",
        "math_research_context",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes", "appendix_results"),
    ),
    _claim(
        "section3_2_vast_search_space_exploration",
        "section_3_2",
        10,
        "powerful tool for exploring the vast search space inherent in these problems",
        "Demonstrate effective search over large constructive-math spaces.",
        "math_research_context",
        "not_demonstrated",
        ("papers/benchmark_fixture_readiness_boundary.json",),
        ("deployment", "benchmark_fixtures"),
    ),
    _claim(
        "section3_2_diverse_open_challenges",
        "section_3_2",
        10,
        "successfully tackling a diverse array of open mathematical challenges",
        "Demonstrate successful search across diverse open mathematical challenges.",
        "math_research_context",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes", "deployment"),
    ),
    _claim(
        "section3_2_over_fifty_problem_instances",
        "section_3_2",
        10,
        "curated set of over 50 mathematical problems",
        "Reproduce a curated constructive-math portfolio with more than 50 problem instances.",
        "math_aggregate_outcome",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes",),
    ),
    _claim(
        "section3_2_more_than_five_branches",
        "section_3_2",
        10,
        "spanning more than five different branches of mathematics",
        "Reproduce constructive-math coverage across more than five branches.",
        "math_aggregate_outcome",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes",),
    ),
    _claim(
        "section3_2_named_branch_examples",
        "section_3_2",
        10,
        "including analysis, combinatorics, number theory, and geometry",
        "Record analysis, combinatorics, number theory, and geometry branch labels.",
        "math_aggregate_outcome",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes",),
    ),
    _claim(
        "section3_2_numerous_parameter_settings",
        "section_3_2",
        10,
        "evaluated across numerous specific parameter settings",
        "Record and execute numerous dimensions, sizes, or other parameter settings.",
        "math_aggregate_outcome",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes",),
    ),
    _claim(
        "section3_2_seventy_five_percent_rediscovery",
        "section_3_2",
        10,
        "In 75% of the cases AlphaEvolve rediscovered the best known constructions",
        "Recompute the reported roughly 75 percent best-known rediscovery rate.",
        "math_aggregate_outcome",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes",),
    ),
    _claim(
        "section3_2_twenty_percent_sota_improvement",
        "section_3_2",
        10,
        "in 20% of the cases it discovered a new object that is better than a previously known best construction",
        "Recompute the reported roughly 20 percent SOTA-improvement rate.",
        "math_aggregate_outcome",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes",),
    ),
    _claim(
        "section3_2_all_simple_or_random_starts",
        "section_3_2",
        10,
        "initial starting point was a simple or a random construction",
        "Prove that every claimed aggregate case started from a simple or random construction.",
        "math_aggregate_outcome",
        "not_demonstrated",
        ("papers/math_starting_construction_boundary.json",),
        ("starting",),
    ),
    _claim(
        "section3_2_broad_versatile_math_potential",
        "section_3_2",
        10,
        "broad potential as a versatile tool for mathematical research",
        "Support broad mathematical versatility with a reproduced result portfolio.",
        "math_aggregate_outcome",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("math_outcomes", "deployment"),
    ),
    _claim(
        "figure5_sota_breaking_constructions",
        "figure_5",
        12,
        "Examples of SOTA-breaking mathematical constructions discovered with AlphaEvolve",
        "Reproduce Figure 5's selected SOTA-breaking construction exhibits.",
        "figure_5_domain",
        "not_demonstrated",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("figure5",),
    ),
    _claim(
        "figure5_analysis_problem_scope",
        "figure_5",
        12,
        "problems in analysis (autocorrelation and uncertainty inequalities)",
        "Map Figure 5's autocorrelation and uncertainty analysis exhibits.",
        "figure_5_domain",
        "partially_implemented",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("figure5", "autocorrelation", "uncertainty"),
    ),
    _claim(
        "figure5_geometry_problem_scope",
        "figure_5",
        12,
        "geometry (packing and minimum/maximum distance problems)",
        "Map Figure 5's packing and minimum/maximum-distance geometry exhibits.",
        "figure_5_domain",
        "partially_implemented",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("figure5", "hexagon", "distance", "circle_packing"),
    ),
    _claim(
        "figure5_combinatorics_problem_scope",
        "figure_5",
        12,
        "combinatorics (Erdős’s minimum overlap problem and sums and differences of finite sets)",
        "Map Figure 5's minimum-overlap and sums/differences exhibits.",
        "figure_5_domain",
        "partially_implemented",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("figure5", "erdos", "sums"),
    ),
    _figure_row(
        "figure5_autocorrelation_c1_1_5098_to_1_5053",
        "1.5098 → 1.5053",
        "Reproduce Figure 5's 1.5098 to 1.5053 autocorrelation display.",
        "autocorrelation",
    ),
    _figure_row(
        "figure5_autocorrelation_c2_0_8892_to_0_8962",
        "0.8892 → 0.8962",
        "Reproduce Figure 5's 0.8892 to 0.8962 autocorrelation display.",
        "autocorrelation",
    ),
    _figure_row(
        "figure5_autocorrelation_c3_1_4581_to_1_4557",
        "1.4581 → 1.4557",
        "Reproduce Figure 5's 1.4581 to 1.4557 autocorrelation display.",
        "autocorrelation",
    ),
    _figure_row(
        "figure5_uncertainty_0_3523_to_0_3521",
        "0.3523 → 0.3521",
        "Reproduce Figure 5's 0.3523 to 0.3521 uncertainty display.",
        "uncertainty",
    ),
    _figure_row(
        "figure5_erdos_0_380926_to_0_380924",
        "0.380926 → 0.380924",
        "Reproduce and reconcile Figure 5's 0.380926 to 0.380924 minimum-overlap display.",
        "erdos",
    ),
    _figure_row(
        "figure5_sums_differences_1_1446_to_1_1584",
        "1.1446 → 1.1584",
        "Reproduce Figure 5's 1.1446 to 1.1584 sums/differences display.",
        "sums",
    ),
    _figure_row(
        "figure5_hexagon_outer_edge_4_000_to_3_942",
        "4.000 → 3.942",
        "Reproduce Figure 5's 4.000 to 3.942 hexagon outer-edge display.",
        "hexagon",
    ),
    _figure_row(
        "figure5_max_min_distance_12_890_to_12_889",
        "12.890 → 12.889",
        "Reproduce Figure 5's 12.890 to 12.889 max/min-distance display.",
        "distance",
    ),
    _figure_row(
        "figure5_sum_radii_2_6340_to_2_6358",
        "2.6340 → 2.6358",
        "Reproduce and reconcile Figure 5's 2.6340 to 2.6358 sum-of-radii display.",
        "circle_packing",
    ),
    _claim(
        "section3_2_versatility_and_speed_advantage",
        "section_3_2",
        12,
        "versatility and speed of application",
        "Measure constructive-math versatility and application speed.",
        "constructive_math_method",
        "not_demonstrated",
        ("papers/benchmark_fixture_readiness_boundary.json",),
        ("deployment",),
    ),
    _claim(
        "section3_2_rapid_deployment",
        "section_3_2",
        12,
        "can be rapidly deployed across a diverse range of mathematical construction problems and conjectures",
        "Demonstrate rapid deployment of one search method across mathematical tasks.",
        "constructive_math_method",
        "not_demonstrated",
        ("papers/benchmark_fixture_readiness_boundary.json",),
        ("deployment",),
    ),
    _claim(
        "section3_2_diverse_constructions_and_conjectures",
        "section_3_2",
        12,
        "diverse range of mathematical construction problems and conjectures",
        "Demonstrate coverage of diverse construction problems and conjectures.",
        "constructive_math_method",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("deployment", "math_outcomes"),
    ),
    _claim(
        "section3_2_less_expert_tailoring_than_bespoke",
        "section_3_2",
        12,
        "less initial problem-specific expert tailoring compared to traditional bespoke approaches",
        "Measure reduced initial expert tailoring against bespoke approaches.",
        "constructive_math_method",
        "not_demonstrated",
        ("papers/problem_formulation_provenance_boundary.json",),
        ("deployment", "formulation"),
    ),
    _claim(
        "section3_2_deep_insight_aids_formulation",
        "section_3_2",
        12,
        "deep mathematical insight naturally aids in problem formulation and search space definition",
        "Record expert mathematical input to formulation and search-space definition.",
        "constructive_math_method",
        "partially_implemented",
        ("papers/problem_formulation_provenance_boundary.json",),
        ("formulation",),
    ),
    _claim(
        "section3_2_autonomous_search_patterns_and_attack_strategies",
        "section_3_2",
        12,
        "autonomously discover effective search patterns and attack strategies",
        "Demonstrate autonomous discovery of effective search patterns and attack strategies.",
        "constructive_math_method",
        "not_demonstrated",
        ("papers/math_heuristic_stage_sequence_boundary.json",),
        ("deployment", "stages"),
    ),
    _claim(
        "section3_2_identifies_subtle_structures",
        "section_3_2",
        12,
        "identifying subtle structures within the problem landscape",
        "Trace accepted strategy gains to independently reviewed problem structure.",
        "constructive_math_method",
        "not_demonstrated",
        ("papers/problem_formulation_provenance_boundary.json",),
        ("deployment", "formulation"),
    ),
    _claim(
        "section3_2_efficient_large_scale_exploration",
        "section_3_2",
        12,
        "efficient, large-scale exploration across many different problems",
        "Measure efficient large-scale exploration across many problems.",
        "constructive_math_method",
        "not_demonstrated",
        ("papers/math_outcome_boundary.json",),
        ("deployment", "math_outcomes"),
    ),
    _claim(
        "section3_2_evolve_heuristics_not_direct_constructions",
        "section_3_2",
        12,
        "evolve heuristic search algorithms rather than directly evolving the constructions themselves",
        "Evolve executable construction-search heuristics instead of direct construction payloads.",
        "constructive_math_method",
        "partially_implemented",
        (
            "papers/programmatic_representation_boundary.json",
            "papers/math_heuristic_handoff_boundary.json",
        ),
        ("handoff",),
    ),
    _claim(
        "section3_2_iterative_refinement_strategy",
        "section_3_2",
        12,
        "we employed an iterative refinement strategy",
        "Execute iterative refinement over construction-search heuristics.",
        "constructive_math_method",
        "partially_implemented",
        ("papers/math_heuristic_handoff_boundary.json",),
        ("handoff", "stages"),
    ),
    _claim(
        "section3_2_fast_objective_evaluations_common_in_math",
        "section_3_2",
        12,
        "fast objective function evaluations—which are common in mathematics",
        "Support and measure fast objective evaluation for constructive-math search.",
        "constructive_math_method",
        "partially_implemented",
        ("papers/benchmark_fixture_readiness_boundary.json",),
        ("deployment", "benchmark_fixtures"),
    ),
    _claim(
        "section3_2_each_generation_evolves_search_heuristic_program",
        "section_3_2",
        12,
        "Each generation of AlphaEvolve was tasked with evolving a program representing a search heuristic",
        "Evolve a program representing a construction-search heuristic each generation.",
        "constructive_math_method",
        "partially_implemented",
        (
            "libreevolve/core/loop.py",
            "papers/math_heuristic_handoff_boundary.json",
        ),
        ("handoff",),
    ),
    _claim(
        "section3_2_fixed_time_budget_1000_seconds",
        "section_3_2",
        12,
        "given a fixed time budget (e.g., 1000 seconds)",
        "Give each heuristic an explicit fixed search budget, including a 1000-second comparable setting.",
        "constructive_math_method",
        "partially_implemented",
        ("papers/math_heuristic_handoff_boundary.json",),
        ("handoff",),
    ),
    _claim(
        "section3_2_previous_best_construction_handoff",
        "section_3_2",
        12,
        "shown the best construction found by the previous best heuristic",
        "Pass the previous best heuristic's construction to the next heuristic.",
        "constructive_math_method",
        "not_implemented",
        ("papers/math_heuristic_handoff_boundary.json",),
        ("handoff",),
    ),
    _claim(
        "section3_2_improve_starting_point_within_budget",
        "section_3_2",
        12,
        "leverage this starting point and the allotted time to find an even better construction",
        "Score whether a heuristic improves the incumbent within its allotted time.",
        "constructive_math_method",
        "partially_implemented",
        ("papers/math_heuristic_handoff_boundary.json",),
        ("handoff",),
    ),
    _claim(
        "section3_2_select_high_quality_solution_improvers",
        "section_3_2",
        12,
        "selects for heuristics that are effective at improving already high-quality solutions",
        "Select heuristics for improvements over already high-quality incumbent constructions.",
        "constructive_math_method",
        "partially_implemented",
        ("papers/math_heuristic_handoff_boundary.json",),
        ("handoff",),
    ),
    _claim(
        "section3_2_sequence_of_specialized_heuristics",
        "section_3_2",
        12,
        "final constructions were often the result of a sequence of different, specialized heuristics",
        "Record ordered sequences of specialized heuristics leading to final constructions.",
        "constructive_math_method",
        "not_implemented",
        ("papers/math_heuristic_stage_sequence_boundary.json",),
        ("stages",),
    ),
    _claim(
        "section3_2_early_broad_gain_heuristics",
        "section_3_2",
        12,
        "early heuristics proficient at making large gains from random or simple initial states",
        "Demonstrate early heuristic stages making large gains from simple or random starts.",
        "constructive_math_method",
        "not_implemented",
        ("papers/math_heuristic_stage_sequence_boundary.json",),
        ("stages", "starting"),
    ),
    _claim(
        "section3_2_late_fine_tuning_heuristics",
        "section_3_2",
        12,
        "later heuristics adept at fine-tuning near-optimal configurations",
        "Demonstrate later heuristic stages fine-tuning near-optimal configurations.",
        "constructive_math_method",
        "not_implemented",
        ("papers/math_heuristic_stage_sequence_boundary.json",),
        ("stages",),
    ),
    _claim(
        "section3_2_multi_stage_strategy_hard_to_replicate_manually",
        "section_3_2",
        12,
        "challenging to replicate manually",
        "Substantiate that discovered multi-stage strategies are difficult to reproduce manually.",
        "constructive_math_method",
        "not_demonstrated",
        ("papers/math_heuristic_stage_sequence_boundary.json",),
        ("stages", "deployment"),
    ),
    _claim(
        "section3_2_multi_stage_strategy_crucial_for_sota",
        "section_3_2",
        12,
        "proved crucial for surpassing the SOTA",
        "Ablate multi-stage adaptive search to show that it is crucial for SOTA gains.",
        "constructive_math_method",
        "not_demonstrated",
        ("papers/math_heuristic_stage_sequence_boundary.json",),
        ("stages", "deployment"),
    ),
    _claim(
        "section3_2_full_list_and_details_in_appendix_b",
        "section_3_2",
        12,
        "Full list of problems and details are provided in Appendix B",
        "Retain and index the source's Appendix B problem list and details.",
        "artifact_and_collaboration",
        "implemented_local",
        (
            "papers/alphaevolve_source_inventory_boundary.json",
            "libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",
        ),
        roadmap_section_id="documentation_truthfulness",
        roadmap_phase="near_term",
    ),
    _claim(
        "section3_2_autocorrelation_bounds_improved",
        "section_3_2",
        13,
        "improve the best known bounds on several autocorrelation inequalities",
        "Reproduce improvements to several autocorrelation-inequality bounds.",
        "math_domain_result",
        "not_demonstrated",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("autocorrelation", "appendix_results"),
    ),
    _claim(
        "section3_2_uncertainty_fourier_upper_bound",
        "section_3_2",
        13,
        "produce a refined configuration for a problem arising in Fourier analysis, by polishing an uncertainty principle construction",
        "Reproduce the refined Fourier uncertainty construction and improved upper bound.",
        "math_domain_result",
        "not_demonstrated",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("uncertainty", "appendix_results"),
    ),
    _claim(
        "section3_2_erdos_new_upper_bound",
        "section_3_2",
        13,
        "established a new upper bound for the minimum overlap problem",
        "Reproduce and verify the new Erdos minimum-overlap upper bound.",
        "math_domain_result",
        "not_demonstrated",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("erdos", "appendix_results"),
    ),
    _claim(
        "section3_2_kissing_number_d11_593_vs_592",
        "section_3_2",
        13,
        "finding a configuration of 593 non-overlapping unit spheres that can simultaneously touch a central unit sphere, surpassing the previous record of 592",
        "Reproduce and certify the dimension-11 kissing configuration of 593 versus 592.",
        "math_domain_result",
        "not_demonstrated",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("kissing", "appendix_results"),
    ),
    _claim(
        "section3_2_n_point_max_min_distance_packing",
        "section_3_2",
        13,
        "packing N points in a shape to minimize the ratio of the maximum and minimum distance",
        "Reproduce point packings minimizing the max/min-distance ratio.",
        "math_domain_result",
        "not_demonstrated",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("distance", "appendix_results"),
    ),
    _claim(
        "section3_2_polygon_in_polygon_packing",
        "section_3_2",
        13,
        "packing various polygons in other polygons in the most efficient way",
        "Reproduce efficient polygon-in-polygon packing results.",
        "math_domain_result",
        "not_demonstrated",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("hexagon", "appendix_results"),
    ),
    _claim(
        "section3_2_heilbronn_small_triangle_avoidance",
        "section_3_2",
        13,
        "variants of the Heilbronn problem concerning point sets avoiding small-area triangles",
        "Reproduce Heilbronn variants that avoid small-area triangles.",
        "math_domain_result",
        "not_demonstrated",
        ("libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",),
        ("heilbronn", "appendix_results"),
    ),
    _claim(
        "section3_2_new_constructions_in_companion_colab",
        "section_3_2",
        13,
        "new constructions found by AlphaEvolve can be found in the accompanying Google Colab",
        "Link and validate the companion Colab construction and verifier artifacts.",
        "artifact_and_collaboration",
        "not_demonstrated",
        ("papers/paper_artifact_linkage.json",),
        ("paper_artifacts", "benchmark_fixtures"),
    ),
    _claim(
        "section3_2_upcoming_math_paper_follow_on",
        "section_3_2",
        13,
        "More examples and details on these problems and the methods used will be provided in an upcoming paper",
        "Track the later mathematical exploration paper separately from the original specification.",
        "artifact_and_collaboration",
        "implemented_local",
        ("papers/follow_on_sources.json",),
        roadmap_section_id="documentation_truthfulness",
        roadmap_phase="near_term",
    ),
    _claim(
        "section3_2_most_discoveries_externally_suggested",
        "section_3_2",
        13,
        "Most of these discoveries are on open problems suggested to us by external mathematicians",
        "Record per-discovery evidence for externally suggested open problems.",
        "artifact_and_collaboration",
        "not_demonstrated",
        (
            "papers/problem_formulation_provenance_boundary.json",
            "papers/follow_on_sources.json",
        ),
        ("formulation",),
    ),
    _claim(
        "section3_2_javier_gomez_serrano_and_terence_tao",
        "section_3_2",
        13,
        "Javier Gomez Serrano and Terence Tao",
        "Preserve the named external-mathematician attribution in formulation provenance.",
        "artifact_and_collaboration",
        "partially_implemented",
        (
            "papers/problem_formulation_provenance_boundary.json",
            "papers/follow_on_sources.json",
        ),
        ("formulation",),
        roadmap_section_id="documentation_truthfulness",
        roadmap_phase="near_term",
    ),
    _claim(
        "section3_2_external_advice_on_input_formulation",
        "section_3_2",
        13,
        "advised on how to best formulate them as inputs to AlphaEvolve",
        "Populate expert-reviewed records for advice on AlphaEvolve input formulation.",
        "artifact_and_collaboration",
        "partially_implemented",
        ("papers/problem_formulation_provenance_boundary.json",),
        ("formulation",),
    ),
    _claim(
        "section3_2_ai_human_math_partnership_potential",
        "section_3_2",
        13,
        "potential for synergistic partnerships between AI-driven discovery engines like AlphaEvolve and human mathematical expertise",
        "Support AI-human mathematical partnership claims with populated provenance and reviewed outcomes.",
        "artifact_and_collaboration",
        "not_demonstrated",
        (
            "papers/problem_formulation_provenance_boundary.json",
            "papers/collaborator_feedback_provenance_boundary.json",
        ),
        ("formulation", "deployment"),
    ),
)


EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in MATH_RESULT_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveMathResultClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveMathResultClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveMathResultClaimInventoryBoundaryIssue]


def alphaevolve_math_result_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Section 3.2 and Figure 5 claim inventory."""

    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _claim_record(root_path, spec, page_texts)
        for spec in MATH_RESULT_CLAIM_SPECS
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
    correction = _source_fidelity_correction(root_path, page_texts)
    source_artifact = source_inventory["source_artifact"]
    inventory_ready = (
        source_artifact["identity_ok"]
        and source_inventory["named_structure_inventory_ready"]
        and len(records) == EXPECTED_CLAIM_COUNT
        and missing_anchor_count == 0
        and missing_reference_count == 0
        and todo_owned_gap_count == implementation_gap_count
        and correction["source_fidelity_correction_ready"]
    )
    return {
        "schema": ALPHAEVOLVE_MATH_RESULT_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "math_result_claim_inventory_ready": inventory_ready,
        "alphaevolve_result_reproduction_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": ["section_3_2", "figure_5"],
        "inventory_scope": {
            "included": [
                "all substantive Section 3.2 research-context, aggregate-outcome, method, result, artifact, and collaboration claims",
                "Figure 5's caption, three domain groupings, and all nine displayed before/after values",
                "the Section 3.2 source-fidelity correction for the previously misattributed blanket verification sentence",
            ],
            "excluded": [
                "Appendix B.1-B.13 detailed equations, proofs, witnesses, captions, and result-row exhaustiveness",
                "independent reproduction of Figure 5 or any mathematical result",
                "Sections 3.3 through 5, Figures 6 through 14, and Table 3",
                "citation, bibliography, equation, and unrelated footnote exhaustiveness",
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
        "source_fidelity_correction": correction,
        "claim_records": records,
        "claim_boundary": (
            "This sidecar certifies a bounded claim-level inventory of 63 "
            "AlphaEvolve constructive-math claims from Section 3.2 and Figure "
            "5 and verifies that the blanket result-verification sentence "
            "previously attributed locally is absent from the pinned source. "
            "Status labels distinguish local source/schema coverage from absent "
            "search-time behavior and undemonstrated published outcomes. It "
            "does not claim Appendix B detail exhaustiveness, companion Colab "
            "availability, independent mathematical verification, Figure 5 or "
            "result reproduction, production-scale evidence, or AlphaEvolve "
            "system parity."
        ),
    }


def validate_alphaevolve_math_result_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveMathResultClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_math_result_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveMathResultClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_math_result_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveMathResultClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_MATH_RESULT_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported math result claim inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    if data.get("alphaevolve_result_reproduction_claim_ready") is not False:
        issues.append(
            _issue(
                "result_reproduction_overclaim",
                "math result inventory must not claim result reproduction",
            )
        )
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(
            _issue(
                "parity_overclaim",
                "math result inventory must not claim AlphaEvolve parity",
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
        "source_fidelity_correction",
        "claim_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(
                _issue(
                    f"invalid_{key}",
                    f"{key} drifted from the bounded math result claim inventory",
                )
            )
    if len(EXPECTED_CLAIM_IDS) != EXPECTED_CLAIM_COUNT:
        issues.append(_issue("invalid_spec_count", "math result claim count must remain 63"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "math result claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in MATH_RESULT_CLAIM_SPECS
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
            for spec in MATH_RESULT_CLAIM_SPECS
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
                f"{expected['missing_anchor_count']} math claim anchors were not found",
            )
        )
    if expected["missing_reference_count"]:
        issues.append(
            _issue(
                "missing_local_reference",
                f"{expected['missing_reference_count']} evidence or TODO references are stale",
            )
        )
    if not expected["source_fidelity_correction"][
        "source_fidelity_correction_ready"
    ]:
        issues.append(
            _issue(
                "source_fidelity_correction_incomplete",
                "math outcome boundary must remove the false verification attribution and preserve the actual starting-point sentence",
            )
        )
    expected_ready = (
        expected["source_artifact"]["identity_ok"]
        and expected["claim_count"] == EXPECTED_CLAIM_COUNT
        and expected["missing_anchor_count"] == 0
        and expected["missing_reference_count"] == 0
        and expected["todo_owned_gap_count"] == expected["implementation_gap_count"]
        and expected["source_fidelity_correction"][
            "source_fidelity_correction_ready"
        ]
    )
    if data.get("math_result_claim_inventory_ready") is not expected_ready:
        issues.append(
            _issue(
                "invalid_math_result_claim_inventory_ready",
                "math_result_claim_inventory_ready does not match source, reference, ownership, and source-fidelity checks",
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "63" not in claim_boundary
        or "Appendix B detail exhaustiveness" not in claim_boundary
        or "result reproduction" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must separate bounded math claims from Appendix B detail, reproduction, and parity proof",
            )
        )
    return AlphaEvolveMathResultClaimInventoryBoundaryValidation(
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


def render_alphaevolve_math_result_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_math_result_claim_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve math result claim inventory boundary",
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


def _source_fidelity_correction(
    root: Path,
    page_texts: tuple[str, ...],
) -> dict[str, Any]:
    full_text = "\n".join(page_texts)
    math_boundary_path = root / "papers/math_outcome_boundary.json"
    math_boundary = _read_json(math_boundary_path)
    boundary_corrected = (
        isinstance(math_boundary, dict)
        and math_boundary.get("schema")
        == "libreevolve.alphaevolve_math_outcome_boundary.v2"
        and "verification_claim" not in math_boundary
        and math_boundary.get("section_3_2_blanket_verification_claim_status")
        == "not_present_in_pinned_source"
    )
    false_present = _canonical(FALSE_VERIFICATION_ATTRIBUTION) in _canonical(
        full_text
    )
    actual_present = _canonical(ACTUAL_IN_ALL_CASES_TEXT) in _canonical(full_text)
    return {
        "correction_id": "section_3_2_blanket_verification_misattribution",
        "incorrect_local_attribution": FALSE_VERIFICATION_ATTRIBUTION,
        "incorrect_attribution_present_in_pinned_pdf": false_present,
        "actual_source_text": ACTUAL_IN_ALL_CASES_TEXT,
        "actual_source_text_present_in_pinned_pdf": actual_present,
        "corrected_boundary_path": "papers/math_outcome_boundary.json",
        "corrected_boundary_exists": _safe_is_file(math_boundary_path),
        "corrected_boundary_schema": (
            math_boundary.get("schema") if isinstance(math_boundary, dict) else None
        ),
        "corrected_boundary_removes_false_attribution": boundary_corrected,
        "source_fidelity_correction_ready": (
            not false_present and actual_present and boundary_corrected
        ),
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
    list[AlphaEvolveMathResultClaimInventoryBoundaryIssue],
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
            "math result claim inventory boundary must be a JSON object",
        )
    ]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveMathResultClaimInventoryBoundaryIssue:
    return AlphaEvolveMathResultClaimInventoryBoundaryIssue(code, message)
