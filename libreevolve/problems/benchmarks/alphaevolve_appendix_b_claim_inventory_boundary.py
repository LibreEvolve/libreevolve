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


ALPHAEVOLVE_APPENDIX_B_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_appendix_b_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "appendix_b_figures_10_14_claim_inventory_complete_without_result_"
    "reproduction"
)
IMPLEMENTED_STATUS = "implemented_local"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)
REGISTRY_REF = "libreevolve/problems/benchmarks/alphaevolve_appendix_b.json"


_TODO_SPECS = {
    "artifacts_code": (
        "docs/todo/code.md",
        "Connect benchmark-grade fixtures to hardening and scope reports.",
    ),
    "artifacts_paper": (
        "docs/todo/papers.md",
        "Harden benchmark implementations beyond smoke-example fidelity.",
    ),
    "autocorrelation_code": (
        "docs/todo/code.md",
        "Add Appendix B.1-B.3 autocorrelation step-function provenance.",
    ),
    "autocorrelation_paper": (
        "docs/todo/papers.md",
        "Track Appendix B.1-B.3 autocorrelation step-function evidence.",
    ),
    "distance_code": (
        "docs/todo/code.md",
        "Add Appendix B.8 point-set distance-certificate provenance.",
    ),
    "distance_paper": (
        "docs/todo/papers.md",
        "Track Appendix B.8 point-set distance-certificate evidence.",
    ),
    "erdos_code": (
        "docs/todo/code.md",
        "Add Appendix B.5 minimum-overlap step-function provenance.",
    ),
    "erdos_paper": (
        "docs/todo/papers.md",
        "Track Appendix B.5 minimum-overlap step-function evidence.",
    ),
    "figures_code": (
        "docs/todo/code.md",
        "Add Appendix B figure-level construction provenance for Figures 10-14.",
    ),
    "figures_paper": (
        "docs/todo/papers.md",
        "Track Appendix B figure-level construction provenance for Figures 10-14.",
    ),
    "heilbronn_code": (
        "docs/todo/code.md",
        "Add Appendix B.9-B.10 Heilbronn minimum-area provenance.",
    ),
    "heilbronn_paper": (
        "docs/todo/papers.md",
        "Track Appendix B.9-B.10 Heilbronn minimum-area evidence.",
    ),
    "hexagon_code": (
        "docs/todo/code.md",
        "Add Appendix B.7 regular-hexagon packing provenance.",
    ),
    "hexagon_paper": (
        "docs/todo/papers.md",
        "Track Appendix B.7 regular-hexagon packing evidence.",
    ),
    "kissing_code": (
        "docs/todo/code.md",
        "Add kissing-number lemma certificate provenance for Appendix B.11.",
    ),
    "kissing_paper": (
        "docs/todo/papers.md",
        "Track kissing-number lemma certificate evidence for Appendix B.11.",
    ),
    "results_code": (
        "docs/todo/code.md",
        "Add Appendix B per-result metric and value provenance.",
    ),
    "results_paper": (
        "docs/todo/papers.md",
        "Track Appendix B per-result metric and value evidence.",
    ),
    "radii_code": (
        "docs/todo/code.md",
        "Add Appendix B.12-B.13 circle/rectangle sum-of-radii provenance.",
    ),
    "radii_paper": (
        "docs/todo/papers.md",
        "Track Appendix B.12-B.13 circle/rectangle sum-of-radii evidence.",
    ),
    "revision_code": (
        "docs/todo/code.md",
        "Add Appendix B result-version provenance for revised mathematical",
    ),
    "revision_paper": (
        "docs/todo/papers.md",
        "Track Appendix B result-version provenance for revised constants.",
    ),
    "rounding_code": (
        "docs/todo/code.md",
        "Add Appendix B.4 prior-bound rounding provenance.",
    ),
    "rounding_paper": (
        "docs/todo/papers.md",
        "Track Appendix B.4 prior-bound rounding evidence.",
    ),
    "sums_code": (
        "docs/todo/code.md",
        "Add Appendix B.6 finite-set witness provenance.",
    ),
    "sums_paper": (
        "docs/todo/papers.md",
        "Track Appendix B.6 finite-set witness evidence.",
    ),
    "uncertainty_code": (
        "docs/todo/code.md",
        "Add Appendix B.4 Hermite-polynomial certificate provenance.",
    ),
    "uncertainty_paper": (
        "docs/todo/papers.md",
        "Track Appendix B.4 Hermite-polynomial certificate evidence.",
    ),
    "uncertainty_similarity_code": (
        "docs/todo/code.md",
        "Add Appendix B.4 prior-construction similarity and hypothesis provenance.",
    ),
    "uncertainty_similarity_paper": (
        "docs/todo/papers.md",
        "Track Appendix B.4 prior-construction similarity and hypothesis evidence.",
    ),
}

_TODO_GROUPS = {
    "artifacts": ("artifacts_code", "artifacts_paper"),
    "autocorrelation": ("autocorrelation_code", "autocorrelation_paper"),
    "distance": ("distance_code", "distance_paper"),
    "erdos": ("erdos_code", "erdos_paper"),
    "figures": ("figures_code", "figures_paper"),
    "heilbronn": ("heilbronn_code", "heilbronn_paper"),
    "hexagon": ("hexagon_code", "hexagon_paper"),
    "kissing": ("kissing_code", "kissing_paper"),
    "results": ("results_code", "results_paper"),
    "radii": ("radii_code", "radii_paper"),
    "revision": ("revision_code", "revision_paper"),
    "rounding": ("rounding_code", "rounding_paper"),
    "sums": ("sums_code", "sums_paper"),
    "uncertainty": ("uncertainty_code", "uncertainty_paper"),
    "uncertainty_similarity": (
        "uncertainty_similarity_code",
        "uncertainty_similarity_paper",
    ),
}


def _todo_ids(*groups: str) -> tuple[str, ...]:
    return tuple(todo_id for group in groups for todo_id in _TODO_GROUPS[group])


def _evidence(*extra: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys((REGISTRY_REF, *extra)))


def _claim(
    claim_id: str,
    source_span_id: str,
    source_page: int,
    source_anchor: str,
    claim: str,
    category: str,
    implementation_status: str,
    todo_groups: tuple[str, ...],
    evidence_paths: tuple[str, ...] | None = None,
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
        "evidence_paths": evidence_paths or _evidence(),
        "todo_ids": _todo_ids(*todo_groups),
    }


def _appendix_claim(
    claim_id: str,
    section_id: str | None,
    source_page: int,
    source_anchor: str,
    claim: str,
    category: str,
    implementation_status: str,
    *todo_groups: str,
    evidence_paths: tuple[str, ...] | None = None,
) -> dict[str, Any]:
    span = "appendix_b" if section_id is None else f"appendix_b_{section_id}"
    return _claim(
        claim_id,
        span,
        source_page,
        source_anchor,
        claim,
        category,
        implementation_status,
        tuple(todo_groups),
        evidence_paths,
    )


def _figure_claim(
    claim_id: str,
    figure_number: int,
    source_page: int,
    source_anchor: str,
    claim: str,
    category: str,
    implementation_status: str,
    *todo_groups: str,
) -> dict[str, Any]:
    return _claim(
        claim_id,
        f"figure_{figure_number}",
        source_page,
        source_anchor,
        claim,
        category,
        implementation_status,
        tuple(dict.fromkeys(("figures", *todo_groups))),
    )


APPENDIX_B_CLAIM_SPECS = (
    _appendix_claim(
        "appendix_b_colab_data_and_verification_code",
        None,
        38,
        "data and verification code for all constructions reported in this section",
        "The accompanying Google Colab contains data and verification code for every Appendix B construction.",
        "publication_artifact",
        "partially_implemented",
        "artifacts",
        "results",
        evidence_paths=_evidence(
            "papers/companion_sources.json",
            "papers/paper_artifact_linkage.json",
        ),
    ),
    # B.1 First autocorrelation inequality.
    _appendix_claim("b1_autoconvolution_definition", "1", 38, "define the autoconvolution of f as", "Autoconvolution is defined by the integral of f(t-x)f(x) over the real line.", "mathematical_definition", "partially_implemented", "autocorrelation", evidence_paths=_evidence("papers/autoconvolution_boundary.json")),
    _appendix_claim("b1_c1_largest_constant", "1", 38, "Let C1 denote the largest constant satisfying", "C1 is the largest constant satisfying the first autocorrelation inequality.", "problem_definition", "partially_implemented", "autocorrelation"),
    _appendix_claim("b1_equation_1_max_autoconvolution", "1", 38, "Let C1 denote the largest constant satisfying", "Equation (1) lower-bounds the maximum autoconvolution on [-1/2,1/2] by C1 times the squared integral on [-1/4,1/4].", "mathematical_definition", "not_implemented", "autocorrelation"),
    _appendix_claim("b1_nonnegative_real_functions", "1", 38, "for all non-negative f", "The C1 inequality ranges over all non-negative real-valued functions.", "problem_definition", "partially_implemented", "autocorrelation"),
    _appendix_claim("b1_additive_combinatorics_origin", "1", 38, "This problem arises in additive combinatorics", "The first autocorrelation inequality arises in additive combinatorics.", "problem_context", "not_implemented", "autocorrelation"),
    _appendix_claim("b1_sidon_set_relation", "1", 38, "relating to the size of Sidon sets", "The first autocorrelation inequality relates to the size of Sidon sets.", "problem_context", "not_implemented", "autocorrelation"),
    _appendix_claim("b1_known_lower_bound_1_28", "1", 38, "It is currently known that", "The known lower bound is 1.28 <= C1.", "known_bound", "partially_implemented", "autocorrelation"),
    _appendix_claim("b1_known_upper_bound_1_5098", "1", 38, "1.28 <= C1 <= 1.5098", "The prior known upper bound is C1 <= 1.5098.", "known_bound", "partially_implemented", "autocorrelation"),
    _appendix_claim("b1_lower_bound_source_17", "1", 38, "lower bound achieved in [17]", "Reference [17] supplies the stated C1 lower bound.", "source_attribution", "partially_implemented", "autocorrelation"),
    _appendix_claim("b1_upper_bound_source_70", "1", 38, "upper bound achieved in [70]", "Reference [70] supplies the prior C1 upper bound.", "source_attribution", "partially_implemented", "autocorrelation"),
    _appendix_claim("b1_prior_step_function_construction", "1", 38, "via a step function construction", "The prior C1 upper bound uses a step-function construction.", "known_construction", "partially_implemented", "autocorrelation"),
    _appendix_claim("b1_alphaevolve_600_intervals", "1", 38, "step function with 600 equally-spaced intervals", "AlphaEvolve found a 600-interval step function.", "reported_construction", "not_demonstrated", "autocorrelation", "results"),
    _appendix_claim("b1_alphaevolve_equal_spacing", "1", 38, "600 equally-spaced intervals", "The reported B.1 intervals are equally spaced.", "reported_construction", "not_demonstrated", "autocorrelation"),
    _appendix_claim("b1_alphaevolve_domain", "1", 38, "on [-1/4, 1/4]", "The reported B.1 step function is defined on [-1/4,1/4].", "reported_construction", "not_demonstrated", "autocorrelation"),
    _appendix_claim("b1_alphaevolve_bound_1_5053", "1", 38, "better upper bound C1 <= 1.5053", "AlphaEvolve reports the improved bound C1 <= 1.5053.", "reported_result", "not_demonstrated", "autocorrelation", "results"),
    # B.2 Second autocorrelation inequality.
    _appendix_claim("b2_c2_smallest_constant", "2", 38, "Let C2 be the smallest constant", "C2 is the smallest constant satisfying the second autocorrelation inequality.", "problem_definition", "partially_implemented", "autocorrelation"),
    _appendix_claim("b2_norm_inequality", "2", 38, "for which one has", "The B.2 inequality bounds the squared L2 norm of f*f by C2 times its L1 and Linfinity norms.", "mathematical_definition", "not_implemented", "autocorrelation"),
    _appendix_claim("b2_nonnegative_real_functions", "2", 38, "for all non-negative f", "The C2 inequality ranges over all non-negative real-valued functions.", "problem_definition", "partially_implemented", "autocorrelation"),
    _appendix_claim("b2_known_lower_bound_0_88922", "2", 38, "0.88922 <= C2 <= 1", "The known lower bound is 0.88922 <= C2.", "known_bound", "partially_implemented", "autocorrelation"),
    _appendix_claim("b2_known_upper_bound_1", "2", 38, "0.88922 <= C2 <= 1", "The known upper bound is C2 <= 1.", "known_bound", "partially_implemented", "autocorrelation"),
    _appendix_claim("b2_lower_bound_step_source_70", "2", 38, "lower bound coming from a step function construction [70]", "The prior C2 lower bound comes from a step-function construction in [70].", "source_attribution", "partially_implemented", "autocorrelation"),
    _appendix_claim("b2_alphaevolve_50_intervals", "2", 38, "step function with 50 equally-spaced intervals", "AlphaEvolve found a 50-interval step function.", "reported_construction", "not_demonstrated", "autocorrelation", "results"),
    _appendix_claim("b2_alphaevolve_equal_spacing", "2", 38, "50 equally-spaced intervals", "The reported B.2 intervals are equally spaced.", "reported_construction", "not_demonstrated", "autocorrelation"),
    _appendix_claim("b2_alphaevolve_domain", "2", 38, "on [-1/4, 1/4]", "The reported B.2 step function is defined on [-1/4,1/4].", "reported_construction", "not_demonstrated", "autocorrelation"),
    _appendix_claim("b2_alphaevolve_bound_0_8962", "2", 38, "better lower bound 0.8962 <= C2", "AlphaEvolve reports the improved bound 0.8962 <= C2.", "reported_result", "not_demonstrated", "autocorrelation", "results"),
    # B.3 Third autocorrelation inequality.
    _appendix_claim("b3_c3_largest_constant", "3", 38, "Let C3 be the largest constant satisfying", "C3 is the largest constant satisfying the third autocorrelation inequality.", "problem_definition", "partially_implemented", "autocorrelation"),
    _appendix_claim("b3_absolute_autoconvolution_inequality", "3", 38, "Let C3 be the largest constant satisfying", "The B.3 inequality lower-bounds the maximum absolute autoconvolution on [-1/2,1/2].", "mathematical_definition", "not_implemented", "autocorrelation"),
    _appendix_claim("b3_signed_real_functions", "3", 38, "for any function f", "The C3 inequality permits signed real-valued functions.", "problem_definition", "partially_implemented", "autocorrelation"),
    _appendix_claim("b3_c3_at_most_c1", "3", 38, "Clearly C3 <= C1", "The source states C3 <= C1.", "mathematical_relation", "not_implemented", "autocorrelation"),
    _appendix_claim("b3_c3_c1_signed_reason", "3", 38, "since we now allow f to take positive and negative values", "The C3 <= C1 relation follows from allowing signed functions.", "mathematical_reasoning", "not_implemented", "autocorrelation"),
    _appendix_claim("b3_prior_bound_1_45810", "3", 38, "upper bound C3 <= 1.45810", "A prior step function gives C3 <= 1.45810.", "known_bound", "partially_implemented", "autocorrelation"),
    _appendix_claim("b3_prior_source_104_page_75", "3", 38, "[104, page 75]", "Reference [104, page 75] supplies the prior C3 upper bound.", "source_attribution", "partially_implemented", "autocorrelation"),
    _appendix_claim("b3_alphaevolve_400_intervals", "3", 38, "step function with 400 equally-spaced intervals", "AlphaEvolve found a 400-interval step function.", "reported_construction", "not_demonstrated", "autocorrelation", "results"),
    _appendix_claim("b3_alphaevolve_equal_spacing_and_domain", "3", 38, "400 equally-spaced intervals on [-1/4, 1/4]", "The reported B.3 intervals are equally spaced on [-1/4,1/4].", "reported_construction", "not_demonstrated", "autocorrelation"),
    _appendix_claim("b3_alphaevolve_bound_1_4557", "3", 38, "better upper bound C3 <= 1.4557", "AlphaEvolve reports the improved bound C3 <= 1.4557.", "reported_result", "not_demonstrated", "autocorrelation", "results"),
    # B.4 Uncertainty inequality and revision note.
    _appendix_claim("b4_fourier_transform_definition", "4", 39, "define the Fourier transform", "B.4 defines the Fourier transform using the exp(-2 pi i x xi) kernel.", "mathematical_definition", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_a_function_definition", "4", 39, "A(f) := inf", "A(f) is the smallest radius beyond which f is non-negative.", "mathematical_definition", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_c4_largest_constant", "4", 39, "Let C4 be the largest constant", "C4 is the largest constant satisfying the uncertainty inequality.", "problem_definition", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_uncertainty_product_inequality", "4", 39, "largest constant for which one has", "The uncertainty inequality lower-bounds A(f)A(f-hat) by C4.", "mathematical_definition", "not_implemented", "uncertainty"),
    _appendix_claim("b4_even_function_condition", "4", 39, "for all even f", "The C4 problem ranges over even functions.", "problem_definition", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_negative_origin_condition", "4", 39, "for all even f with max", "Both f(0) and f-hat(0) must be negative.", "problem_definition", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_known_lower_bound_0_2025", "4", 39, "0.2025 <= C4 <= 0.3523", "The known lower bound is 0.2025 <= C4.", "known_bound", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_known_upper_bound_0_3523", "4", 39, "0.2025 <= C4 <= 0.3523", "The rounded prior upper bound is C4 <= 0.3523.", "known_bound", "partially_implemented", "rounding"),
    _appendix_claim("b4_prior_source_33", "4", 39, "It is known [33]", "Reference [33] supplies the prior C4 bounds and construction approach.", "source_attribution", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_paper_stated_0_353", "4", 39, "upper bound is stated as 0.353", "The prior paper displays its upper bound as 0.353.", "rounding_provenance", "partially_implemented", "rounding"),
    _appendix_claim("b4_rounding_to_fourth_digit_0_3523", "4", 39, "rounding their solution to the fourth digit gives 0.3523", "Rounding the prior solution to four digits gives 0.3523.", "rounding_provenance", "partially_implemented", "rounding"),
    _appendix_claim("b4_first_version_result_0_3521", "4", 39, "improved the upper bound to C4 <= 0.3521", "AlphaEvolve's first-version construction reports C4 <= 0.3521.", "reported_result", "not_demonstrated", "uncertainty", "results"),
    _appendix_claim("b4_similar_linear_combination", "4", 39, "with a similar linear combination as in [33]", "The reported construction uses a linear combination similar to [33].", "reported_method", "partially_implemented", "uncertainty_similarity"),
    _appendix_claim("b4_refined_constants_found_by_alphaevolve", "4", 39, "refined constants that were found by AlphaEvolve", "AlphaEvolve found refined constants for the test function.", "reported_construction", "not_demonstrated", "uncertainty", "results"),
    _appendix_claim("b4_test_function_upper_bound_method", "4", 39, "one constructs a specific test function", "A qualifying test function provides an upper bound through A(f)A(f-hat).", "method_derivation", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_test_function_polynomial_gaussian_form", "4", 39, "test function is sought in the form", "The test function has polynomial-times-Gaussian form P(x)exp(-pi x^2).", "method_derivation", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_even_polynomial_hermite_basis", "4", 39, "even polynomial constructed as a linear combination", "P is an even linear combination of Hermite polynomials H_(4k).", "method_derivation", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_hermite_fourier_eigenfunction", "4", 39, "Fourier transform of", "The Hermite-Gaussian basis is a Fourier eigenbasis with factor i^n.", "method_derivation", "not_implemented", "uncertainty"),
    _appendix_claim("b4_fourier_invariant_p", "4", 39, "the Fourier transform of f", "For the H_(4k) combination, f-hat(xi)=P(xi)exp(-pi xi^2).", "method_derivation", "not_implemented", "uncertainty"),
    _appendix_claim("b4_a_related_to_largest_root", "4", 39, "A(f) is related to the largest positive root", "A(f) and A(f-hat) are determined by largest positive roots of P.", "method_derivation", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_eventual_positive_root_condition", "4", 39, "P(x) >= 0 for large", "If P is eventually non-negative, A(f) is its largest positive root.", "method_derivation", "not_implemented", "uncertainty"),
    _appendix_claim("b4_a_f_equals_a_fhat", "4", 39, "Specifically, if P(x)", "The self-Fourier construction makes A(f)=A(f-hat).", "method_derivation", "not_implemented", "uncertainty"),
    _appendix_claim("b4_c4_at_most_a_squared", "4", 39, "inequality becomes C4 <=", "The construction reduces the upper bound to C4 <= A(f)^2.", "method_derivation", "not_implemented", "uncertainty"),
    _appendix_claim("b4_coefficient_search_constraints", "4", 39, "method involves finding coefficients", "The method searches Hermite coefficients subject to origin and eventual-positivity constraints while minimizing the largest root.", "method_derivation", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_p_zero_condition", "4", 39, "P(0) = 0", "The optimization imposes P(0)=0 to simplify constraints.", "method_derivation", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_x_squared_factor", "4", 39, "has a factor of x2", "P(0)=0 gives P an x^2 factor.", "method_derivation", "not_implemented", "uncertainty"),
    _appendix_claim("b4_rmax_root_of_quotient", "4", 39, "largest positive root of P(x)/x2", "r_max is the largest positive root of P(x)/x^2.", "method_derivation", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_bound_rmax_squared_over_2pi", "4", 39, "upper bound on C4 derived from this construction", "The reported construction evaluates the upper bound as r_max^2/(2 pi).", "method_derivation", "partially_implemented", "uncertainty"),
    _appendix_claim("b4_reported_coefficients", "4", 39, "[c0, c1, c2]", "The reported coefficients are approximately 0.32925, -0.01159, and -8.9216e-5.", "reported_construction", "not_demonstrated", "uncertainty", "results"),
    _appendix_claim("b4_coefficients_yield_0_3521", "4", 39, "yields the improved upper bound C4 <= 0.3521", "The reported coefficients and root calculation yield C4 <= 0.3521.", "reported_result", "not_demonstrated", "uncertainty", "results"),
    _appendix_claim("b4_qualitative_similarity_to_33", "4", 39, "linear combination is very similar to the one found in [33]", "The AlphaEvolve combination is qualitatively similar to [33].", "qualitative_result", "not_demonstrated", "uncertainty_similarity"),
    _appendix_claim("b4_empirical_near_optimal_hypothesis", "4", 39, "empirically confirming their hypothesis", "The qualitative similarity is presented as empirical confirmation that the prior construction is nearly optimal.", "qualitative_result", "not_demonstrated", "uncertainty_similarity"),
    _appendix_claim("b4_henry_cohn_postpublication_note", "4", 39, "Henry Cohn pointed out", "Henry Cohn identified a newer refined approach after the first manuscript version.", "revision_provenance", "partially_implemented", "revision"),
    _appendix_claim("b4_reference_18_constant_0_3284", "4", 39, "better constant 0.3284", "Reference [18] reports the better constant 0.3284.", "revision_provenance", "partially_implemented", "revision"),
    _appendix_claim("b4_refined_approach_incorporated", "4", 39, "incorporating their refined approach into AlphaEvolve", "The refined [18] approach was incorporated into AlphaEvolve.", "reported_method", "not_demonstrated", "revision"),
    _appendix_claim("b4_revised_result_0_3216", "4", 39, "improved our reported constant further to 0.3216", "The revised AlphaEvolve result reports C4=0.3216.", "reported_result", "not_demonstrated", "revision", "results"),
    _appendix_claim("b4_revision_details_in_colab", "4", 39, "details, we refer to the accompanying Google Colab", "Details of the revised B.4 result are delegated to the companion Colab.", "publication_artifact", "partially_implemented", "revision", "artifacts"),
    # Figure 10 and B.5.
    _figure_claim("figure10_alphaevolve_minimum_overlap_construction", 10, 40, "Construction found by AlphaEvolve for the minimum overlap problem", "Figure 10 displays an AlphaEvolve minimum-overlap construction.", "figure_caption", "not_demonstrated", "erdos"),
    _figure_claim("figure10_single_step_function_panel", 10, 40, "Figure 10", "Figure 10 is a single step-function trace rather than a multi-panel exhibit.", "figure_visual", "not_demonstrated", "erdos"),
    _figure_claim("figure10_step_values_zero_to_one", 10, 40, "Figure 10", "The plotted step function stays visually within the stated [0,1] value range.", "figure_visual", "not_demonstrated", "erdos"),
    _figure_claim("figure10_support_near_quarter_interval", 10, 40, "Figure 10", "The plotted construction has visible support inside approximately [-1/4,1/4].", "figure_visual", "not_demonstrated", "erdos"),
    _appendix_claim("b5_c5_largest_constant", "5", 40, "Let C5 be the largest constant", "C5 is the largest constant satisfying the minimum-overlap inequality.", "problem_definition", "partially_implemented", "erdos"),
    _appendix_claim("b5_original_overlap_integral", "5", 40, "sup", "The original formulation takes a supremum over shifts of the overlap integral of f(t)g(x+t).", "mathematical_definition", "partially_implemented", "erdos"),
    _appendix_claim("b5_f_g_nonnegative_unit_range", "5", 40, "for all non-negative f, g", "The source functions f and g map [-1,1] into [0,1].", "problem_definition", "partially_implemented", "erdos"),
    _appendix_claim("b5_f_plus_g_one", "5", 40, "with f + g = 1", "The source formulation requires f+g=1 on [-1,1].", "problem_definition", "partially_implemented", "erdos"),
    _appendix_claim("b5_integral_f_one", "5", 40, "with f + g = 1 on", "The source formulation normalizes the integral of f to one.", "problem_definition", "partially_implemented", "erdos"),
    _appendix_claim("b5_zero_extension", "5", 40, "extend f, g by zero outside", "The source formulation extends f and g by zero outside [-1,1].", "problem_definition", "partially_implemented", "erdos"),
    _appendix_claim("b5_controls_minimum_overlap_asymptotics", "5", 40, "controls the asymptotics of the Minimum Overlap Problem", "C5 controls asymptotics of the Erdos minimum-overlap problem.", "problem_context", "partially_implemented", "erdos"),
    _appendix_claim("b5_known_lower_bound_0_379005", "5", 40, "0.379005 <= C5 <= 0.380927", "The known lower bound is 0.379005 <= C5.", "known_bound", "partially_implemented", "erdos"),
    _appendix_claim("b5_known_upper_bound_0_380927", "5", 40, "0.379005 <= C5 <= 0.380927", "The prior known upper bound is C5 <= 0.380927.", "known_bound", "partially_implemented", "erdos"),
    _appendix_claim("b5_lower_bound_source_107", "5", 40, "lower bound was obtained in [107]", "Reference [107] supplies the lower bound using convex programming.", "source_attribution", "partially_implemented", "erdos"),
    _appendix_claim("b5_equivalent_step_function_infimum", "5", 40, "constant is equal to the infimum", "Reference [40] identifies C5 with an infimum over step functions h on [0,2].", "mathematical_relation", "partially_implemented", "erdos"),
    _appendix_claim("b5_step_function_value_and_integral_constraints", "5", 40, "values in [0, 1]", "The equivalent h has values in [0,1] and integral one on [0,2].", "mathematical_definition", "partially_implemented", "erdos"),
    _appendix_claim("b5_shift_objective", "5", 40, "max", "The equivalent objective maximizes the shifted overlap integral h(x)(1-h(x+k)) over k.", "mathematical_definition", "partially_implemented", "erdos"),
    _appendix_claim("b5_prior_upper_step_construction_40", "5", 40, "in [40] by a step function construction", "Reference [40] obtains the prior upper bound from a step-function construction.", "source_attribution", "partially_implemented", "erdos"),
    _appendix_claim("b5_figure10_slight_improvement", "5", 40, "step function depicted in Figure 10 does ever so slightly better", "The Figure 10 step function is reported to improve the prior bound slightly.", "reported_construction", "not_demonstrated", "erdos", "figures"),
    _appendix_claim("b5_alphaevolve_bound_0_380924", "5", 40, "upper bound of C5 <= 0.380924", "AlphaEvolve reports C5 <= 0.380924.", "reported_result", "not_demonstrated", "erdos", "results"),
    # B.6 Sums and differences.
    _appendix_claim("b6_c6_largest_constant", "6", 40, "Let C6 be the largest constant", "C6 is the largest constant satisfying the stated finite-set asymptotic property.", "problem_definition", "partially_implemented", "sums", evidence_paths=_evidence("papers/sums_differences_boundary.json")),
    _appendix_claim("b6_arbitrarily_large_integer_sets", "6", 40, "arbitrarily large finite sets of integers A, B", "The C6 property concerns arbitrarily large finite integer sets A and B.", "problem_definition", "partially_implemented", "sums"),
    _appendix_claim("b6_small_sumset_condition", "6", 40, "|A + B|", "The sets must have |A+B| asymptotically bounded by a constant times |A|.", "mathematical_definition", "partially_implemented", "sums"),
    _appendix_claim("b6_large_difference_condition", "6", 40, "|A - B|", "The difference set must grow at least as |A+B| raised to C6 up to a constant.", "mathematical_definition", "partially_implemented", "sums"),
    _appendix_claim("b6_sumset_definition", "6", 40, "denote the sumset and difference set", "A+B is defined as all a+b with a in A and b in B.", "mathematical_definition", "not_implemented", "sums"),
    _appendix_claim("b6_difference_set_definition", "6", 40, "denote the sumset and difference set", "A-B is defined as all a-b with a in A and b in B.", "mathematical_definition", "not_implemented", "sums"),
    _appendix_claim("b6_little_less_notation", "6", 40, "notation X", "X << Y means X <= CY for a set-independent constant C for sufficiently large sets.", "mathematical_definition", "not_implemented", "sums"),
    _appendix_claim("b6_little_greater_notation", "6", 40, "notation X", "X >> Y means X >= C'Y for a positive set-independent constant C' for sufficiently large sets.", "mathematical_definition", "not_implemented", "sums"),
    _appendix_claim("b6_known_bounds_equation_2", "6", 40, "1.14465 <= C6", "Equation (2) gives 1.14465 <= C6 <= 4/3.", "known_bound", "partially_implemented", "sums"),
    _appendix_claim("b6_upper_bound_source_39_corollary_3", "6", 41, "Corollary 3", "Reference [39, Corollary 3] supplies the C6 upper bound.", "source_attribution", "partially_implemented", "sums"),
    _appendix_claim("b6_lower_bound_source_39_theorem_1", "6", 41, "Theorem 1", "Reference [39, Theorem 1] supplies the prior C6 lower bound.", "source_attribution", "partially_implemented", "sums"),
    _appendix_claim("b6_gyarmati_lower_bound_tool", "6", 41, "main tool for the lower bound", "The stated Gyarmati et al. finite-set inequality is the main lower-bound tool.", "method_derivation", "partially_implemented", "sums"),
    _appendix_claim("b6_equation_3_formula", "6", 41, "C6 >= 1", "Equation (3) lower-bounds C6 using log(|U-U|/|U+U|) divided by log(2 max(U)+1).", "mathematical_definition", "partially_implemented", "sums"),
    _appendix_claim("b6_u_admissibility_conditions", "6", 41, "for any finite set U of non-negative integers", "Equation (3) requires finite non-negative U containing zero with |U-U| <= 2 max(U)+1.", "problem_definition", "partially_implemented", "sums"),
    _appendix_claim("b6_u1_size_2003", "6", 41, "set U1 of size 2003", "AlphaEvolve found an admissible set U1 of size 2003.", "reported_construction", "not_demonstrated", "sums", "results"),
    _appendix_claim("b6_u1_bound_1_1479", "6", 41, "1.1479 <= C6", "U1 is reported to improve the lower bound to 1.1479 <= C6.", "reported_result", "not_demonstrated", "sums", "results"),
    _appendix_claim("b6_u2_size_54265", "6", 41, "set U2 of size 54265", "AlphaEvolve found an admissible set U2 of size 54265.", "reported_construction", "not_demonstrated", "sums", "results"),
    _appendix_claim("b6_u2_bound_1_1584", "6", 41, "1.1584 <= C6", "U2 is reported to improve the lower bound to 1.1584 <= C6.", "reported_result", "not_demonstrated", "sums", "results"),
    # Figure 11 and B.7.
    _figure_claim("figure11_two_packing_panels", 11, 41, "Constructions of the packing problems", "Figure 11 contains separate left and right regular-hexagon packing panels.", "figure_visual", "not_demonstrated", "hexagon"),
    _figure_claim("figure11_left_11_hexagons", 11, 41, "Left: Packing 11 unit hexagons", "The left panel depicts 11 unit regular hexagons.", "figure_caption", "not_demonstrated", "hexagon"),
    _figure_claim("figure11_left_outer_side_3_931", 11, 41, "side length 3.931", "The left panel reports outer side length 3.931.", "figure_caption", "not_demonstrated", "hexagon"),
    _figure_claim("figure11_right_12_hexagons", 11, 41, "Right: Packing 12 unit hexagons", "The right panel depicts 12 unit regular hexagons.", "figure_caption", "not_demonstrated", "hexagon"),
    _figure_claim("figure11_right_outer_side_3_942", 11, 41, "side length 3.942", "The right panel reports outer side length 3.942.", "figure_caption", "not_demonstrated", "hexagon"),
    _figure_claim("figure11_blue_inner_red_outer_geometry", 11, 41, "Figure 11", "Both panels visually distinguish blue inner hexagons from a red outer boundary.", "figure_visual", "not_demonstrated", "hexagon"),
    _appendix_claim("b7_problem_n_disjoint_unit_hexagons", "7", 41, "packing n disjoint regular hexagons with unit side length", "B.7 packs n disjoint unit-side regular hexagons.", "problem_definition", "partially_implemented", "hexagon"),
    _appendix_claim("b7_minimize_outer_side_length", "7", 41, "minimizing the side length of the outer hexagon", "The B.7 objective minimizes the enclosing regular hexagon side length.", "problem_definition", "partially_implemented", "hexagon"),
    _appendix_claim("b7_prior_n11_3_943", "7", 41, "side lengths 3.943 and 4.0", "The prior n=11 outer side length is 3.943.", "known_bound", "partially_implemented", "hexagon"),
    _appendix_claim("b7_prior_n12_4_0", "7", 41, "side lengths 3.943 and 4.0", "The prior n=12 outer side length is 4.0.", "known_bound", "partially_implemented", "hexagon"),
    _appendix_claim("b7_prior_source_29", "7", 41, "respectively [29]", "Reference [29] supplies the prior B.7 constructions.", "source_attribution", "partially_implemented", "hexagon"),
    _appendix_claim("b7_alphaevolve_n11_3_931", "7", 41, "improve these bounds to 3.931", "AlphaEvolve reports outer side length 3.931 for n=11.", "reported_result", "not_demonstrated", "hexagon", "results"),
    _appendix_claim("b7_alphaevolve_n12_3_942", "7", 41, "3.931 and 3.942", "AlphaEvolve reports outer side length 3.942 for n=12.", "reported_result", "not_demonstrated", "hexagon", "results"),
    # Figure 12 and B.8.
    _figure_claim("figure12_two_distance_panels", 12, 42, "Left: 16 points in 2 dimensions", "Figure 12 contains separate 2D and 3D point-set panels.", "figure_visual", "not_demonstrated", "distance"),
    _figure_claim("figure12_left_16_points_2d", 12, 42, "16 points in 2 dimensions", "The left panel depicts 16 points in two dimensions.", "figure_caption", "not_demonstrated", "distance"),
    _figure_claim("figure12_left_ratio_12_889266112", 12, 42, "12.889266112", "The left panel reports max/min distance ratio approximately sqrt(12.889266112).", "figure_caption", "not_demonstrated", "distance"),
    _figure_claim("figure12_right_14_points_3d", 12, 42, "14 points in 3 dimensions", "The right panel depicts 14 points in three dimensions.", "figure_caption", "not_demonstrated", "distance"),
    _figure_claim("figure12_right_ratio_4_165849767", 12, 42, "4.165849767", "The right panel reports max/min distance ratio approximately sqrt(4.165849767).", "figure_caption", "not_demonstrated", "distance"),
    _figure_claim("figure12_red_maximum_distance_edges", 12, 42, "Both constructions improve", "Figure 12 uses red edges to identify maximum-distance pairs.", "figure_visual", "not_demonstrated", "distance"),
    _figure_claim("figure12_blue_minimum_distance_edges", 12, 42, "Both constructions improve", "Figure 12 uses blue edges to identify minimum-distance pairs.", "figure_visual", "not_demonstrated", "distance"),
    _appendix_claim("b8_objective_n_points_d_dimensions", "8", 41, "find n points in the d-dimensional space", "B.8 chooses n points in d-dimensional space.", "problem_definition", "partially_implemented", "distance"),
    _appendix_claim("b8_minimize_max_min_ratio", "8", 41, "minimize the ratio between the maximum and minimum pairwise distances", "The B.8 objective minimizes maximum pairwise distance divided by minimum pairwise distance.", "problem_definition", "partially_implemented", "distance"),
    _appendix_claim("b8_two_new_constructions", "8", 41, "found two new constructions", "AlphaEvolve reports two improved B.8 constructions.", "reported_construction", "not_demonstrated", "distance", "results"),
    _appendix_claim("b8_2d_prior_sqrt_12_890", "8", 41, "best known bound of", "The prior 16-point 2D bound is sqrt(12.890) from [29].", "known_bound", "partially_implemented", "distance"),
    _appendix_claim("b8_squared_ratio_convention", "8", 41, "square of the ratio is reported", "The source and reference [29] report the square of the ratio rather than the ratio itself.", "metric_convention", "partially_implemented", "distance"),
    _appendix_claim("b8_3d_prior_sqrt_4_168", "8", 42, "best known bound of", "The prior 14-point 3D bound is sqrt(4.168) from [29].", "known_bound", "partially_implemented", "distance"),
    _appendix_claim("b8_both_improve_best_known", "8", 42, "Both constructions improve the best known bounds", "Both reported B.8 constructions improve the prior bounds.", "reported_result", "not_demonstrated", "distance", "results"),
    # B.9, B.10, and Figure 13.
    _appendix_claim("b9_triangle_unit_area_domain", "9", 42, "points on or inside a triangle with unit area", "B.9 places n points on or inside a unit-area triangle.", "problem_definition", "partially_implemented", "heilbronn"),
    _appendix_claim("b9_maximize_smallest_triangle_area", "9", 42, "area of the smallest triangle formed by these points is maximized", "The B.9 objective maximizes the minimum area among triangles formed by the points.", "problem_definition", "partially_implemented", "heilbronn"),
    _appendix_claim("b9_n11_prior_0_036", "9", 42, "For n = 11, the SOTA was 0.036", "The prior n=11 triangle-domain bound is 0.036 from [29].", "known_bound", "partially_implemented", "heilbronn"),
    _appendix_claim("b9_n11_result_larger_0_0365", "9", 42, "minimum area larger than 0.0365", "AlphaEvolve reports an n=11 construction with minimum triangle area greater than 0.0365.", "reported_result", "not_demonstrated", "heilbronn", "results"),
    _appendix_claim("b10_convex_unit_area_domain", "10", 42, "points on or inside a convex region with unit area", "B.10 places n points on or inside a unit-area convex region.", "problem_definition", "partially_implemented", "heilbronn"),
    _appendix_claim("b10_maximize_smallest_triangle_area", "10", 42, "area of the smallest triangle formed by these points is maximized", "The B.10 objective maximizes the minimum area among triangles formed by the points.", "problem_definition", "partially_implemented", "heilbronn"),
    _appendix_claim("b10_two_improved_bounds", "10", 42, "improved two of the best known bounds", "AlphaEvolve reports improvements for two convex-region instances.", "reported_result", "not_demonstrated", "heilbronn", "results"),
    _appendix_claim("b10_n13_prior_0_0306", "10", 42, "For n = 13, the SOTA was 0.0306", "The prior n=13 convex-region bound is 0.0306 from [29].", "known_bound", "partially_implemented", "heilbronn"),
    _appendix_claim("b10_n13_result_0_0309", "10", 42, "improved it to 0.0309", "AlphaEvolve reports 0.0309 for n=13.", "reported_result", "not_demonstrated", "heilbronn", "results"),
    _appendix_claim("b10_n14_prior_0_0277", "10", 42, "For n = 14, the SOTA was 0.0277", "The prior n=14 convex-region bound is 0.0277 from [29].", "known_bound", "partially_implemented", "heilbronn"),
    _appendix_claim("b10_n14_result_0_0278", "10", 42, "improved it to 0.0278", "AlphaEvolve reports 0.0278 for n=14.", "reported_result", "not_demonstrated", "heilbronn", "results"),
    _figure_claim("figure13_three_heilbronn_panels", 13, 43, "two variants of the Heilbronn problem", "Figure 13 contains one triangle-domain and two convex-region panels.", "figure_visual", "not_demonstrated", "heilbronn"),
    _figure_claim("figure13_left_11_points_area_0_0365", 13, 43, "Left: 11 points in a unit-area triangle", "The left panel shows 11 points in a unit-area triangle with all formed triangle areas at least 0.0365.", "figure_caption", "not_demonstrated", "heilbronn"),
    _figure_claim("figure13_middle_13_points_area_0_0309", 13, 43, "Middle: 13 points inside a convex region", "The middle panel shows 13 points in a unit-area convex region with all formed triangle areas at least 0.0309.", "figure_caption", "not_demonstrated", "heilbronn"),
    _figure_claim("figure13_right_14_points_area_0_0278", 13, 43, "Right: 14 points inside a unit convex region", "The right panel shows 14 points in a unit-area convex region with minimum triangle area at least 0.0278.", "figure_caption", "not_demonstrated", "heilbronn"),
    _figure_claim("figure13_blue_points_black_domains", 13, 43, "Figure 13", "Figure 13 visually distinguishes blue points from black triangle or convex-region boundaries.", "figure_visual", "not_demonstrated", "heilbronn"),
    # B.11 kissing number and Lemma 1.
    _appendix_claim("b11_kissing_problem_definition", "11", 42, "how many disjoint unit spheres can be packed tangent", "The kissing problem asks how many disjoint unit spheres can touch a central unit sphere.", "problem_definition", "partially_implemented", "kissing"),
    _appendix_claim("b11_d_dimensional_kissing_number", "11", 42, "called the d-dimensional kissing number", "The maximum count in dimension d is the d-dimensional kissing number.", "mathematical_definition", "partially_implemented", "kissing"),
    _appendix_claim("b11_prior_d11_lower_bound_592", "11", 42, "best known lower bound was 592", "The prior dimension-11 lower bound is 592 from [31].", "known_bound", "partially_implemented", "kissing"),
    _appendix_claim("b11_alphaevolve_lower_bound_593", "11", 43, "this to 593", "AlphaEvolve reports a dimension-11 kissing lower bound of 593.", "reported_result", "not_demonstrated", "kissing", "results"),
    _appendix_claim("b11_593_integral_vectors", "11", 43, "593 many 11-dimensional non-zero points with integral coordinates", "The reported witness has 593 nonzero integral vectors in 11 dimensions.", "reported_construction", "not_demonstrated", "kissing", "results"),
    _appendix_claim("b11_strict_norm_distance_condition", "11", 43, "maximum norm of these points is smaller than their minimum pairwise distance", "The witness is claimed to have max norm strictly below minimum pairwise distance.", "reported_construction", "not_demonstrated", "kissing"),
    _appendix_claim("b11_lemma_implies_593", "11", 43, "this implies the kissing number in dimension 11 is at least 593", "Lemma 1 converts the reported vectors into a 593-sphere kissing configuration.", "proof_statement", "not_demonstrated", "kissing", "results"),
    _appendix_claim("b11_lemma_nonzero_set_condition", "11", 43, "set of points satisfying", "Lemma 1 requires that C exclude the origin.", "proof_statement", "partially_implemented", "kissing"),
    _appendix_claim("b11_lemma_distance_norm_condition", "11", 43, "min", "Lemma 1 requires minimum pairwise distance at least the maximum norm.", "proof_statement", "partially_implemented", "kissing"),
    _appendix_claim("b11_lemma_center_transformation", "11", 43, "form a valid kissing configuration", "Lemma 1 maps x to 2x/||x|| as unit-sphere centers.", "proof_statement", "partially_implemented", "kissing"),
    _appendix_claim("b11_lemma_kissing_lower_bound_cardinality", "11", 43, "kissing number in dimension d is at least", "Lemma 1 concludes that the kissing number is at least |C|.", "proof_statement", "partially_implemented", "kissing"),
    _appendix_claim("b11_proof_inner_product_equation_4", "11", 43, "inequality", "Equation (4) derives 2<x,y> <= ||x|| ||y|| from the distance/norm premise.", "proof_step", "not_implemented", "kissing"),
    _appendix_claim("b11_proof_minimum_geometric_mean", "11", 43, "minimum of two positive numbers", "The proof uses min(a,b) <= sqrt(ab) for positive a and b.", "proof_step", "not_implemented", "kissing"),
    _appendix_claim("b11_transformed_centers_norm_two", "11", 43, "have norm 2", "The transformed centers have norm two and are tangent to the central unit sphere.", "proof_step", "not_implemented", "kissing"),
    _appendix_claim("b11_nonoverlap_distance_at_least_two", "11", 43, "spheres do not overlap", "Non-overlap is equivalent to transformed center distance at least two.", "proof_step", "not_implemented", "kissing"),
    _appendix_claim("b11_nonoverlap_inner_product_equivalence", "11", 43, "After simplifying, this is equivalent", "The transformed distance inequality is equivalent to 2<x,y> <= ||x|| ||y||.", "proof_step", "not_implemented", "kissing"),
    _appendix_claim("b11_proof_valid_configuration_conclusion", "11", 43, "form a valid kissing configuration", "The proof concludes that the transformed centers define a valid kissing configuration.", "proof_step", "not_implemented", "kissing"),
    # B.12, B.13, and Figure 14.
    _appendix_claim("b12_unit_square_circle_problem", "12", 43, "pack n disjoint circles inside a unit square", "B.12 packs n disjoint circles inside a unit square.", "problem_definition", "partially_implemented", "radii"),
    _appendix_claim("b12_maximize_sum_of_radii", "12", 43, "maximize the sum of their radii", "The B.12 objective maximizes the circles' total radius.", "problem_definition", "partially_implemented", "radii"),
    _appendix_claim("b12_two_new_constructions", "12", 43, "found two new constructions", "AlphaEvolve reports two state-of-the-art B.12 constructions.", "reported_construction", "not_demonstrated", "radii", "results"),
    _appendix_claim("b12_n26_prior_2_634", "12", 44, "For n = 26, the SOTA was 2.634", "The prior n=26 sum of radii is 2.634.", "known_bound", "partially_implemented", "radii"),
    _appendix_claim("b12_n26_result_2_635", "12", 44, "improved it to 2.635", "AlphaEvolve reports sum of radii 2.635 for n=26.", "reported_result", "not_demonstrated", "radii", "results"),
    _appendix_claim("b12_n32_prior_2_936", "12", 44, "For n = 32, the SOTA was 2.936", "The prior n=32 sum of radii is 2.936.", "known_bound", "partially_implemented", "radii"),
    _appendix_claim("b12_n32_result_2_937", "12", 44, "improved it to 2.937", "AlphaEvolve reports sum of radii 2.937 for n=32.", "reported_result", "not_demonstrated", "radii", "results"),
    _appendix_claim("b13_perimeter4_rectangle_problem", "13", 44, "pack n disjoint circles inside a rectangle of perimeter 4", "B.13 packs n disjoint circles in a rectangle of perimeter four.", "problem_definition", "partially_implemented", "radii"),
    _appendix_claim("b13_maximize_sum_of_radii", "13", 44, "maximize the sum of their radii", "The B.13 objective maximizes the circles' total radius.", "problem_definition", "partially_implemented", "radii"),
    _appendix_claim("b13_n21_new_construction", "13", 44, "new construction for n = 21", "AlphaEvolve reports a new B.13 construction for n=21.", "reported_construction", "not_demonstrated", "radii", "results"),
    _appendix_claim("b13_n21_prior_2_364", "13", 44, "state of the art from 2.364", "The prior n=21 perimeter-four rectangle sum is 2.364 from [29].", "known_bound", "partially_implemented", "radii"),
    _appendix_claim("b13_n21_result_2_3658", "13", 44, "to 2.3658", "AlphaEvolve reports sum of radii 2.3658 for n=21.", "reported_result", "not_demonstrated", "radii", "results"),
    _figure_claim("figure14_three_circle_packing_panels", 14, 44, "New constructions found by AlphaEvolve", "Figure 14 contains two unit-square panels and one perimeter-four rectangle panel.", "figure_visual", "not_demonstrated", "radii"),
    _figure_claim("figure14_left_26_circles_2_635", 14, 44, "Left: 26 circles in a unit square", "The left panel shows 26 circles in a unit square with sum of radii at least 2.635.", "figure_caption", "not_demonstrated", "radii"),
    _figure_claim("figure14_middle_32_circles_2_937", 14, 44, "Middle: 32 circles in a unit square", "The middle panel shows 32 circles in a unit square with sum of radii at least 2.937.", "figure_caption", "not_demonstrated", "radii"),
    _figure_claim("figure14_right_21_circles_2_365", 14, 44, "Right: 21 circles in a rectangle", "The right panel shows 21 circles in a perimeter-four rectangle with displayed sum of radii at least 2.365.", "figure_caption", "not_demonstrated", "radii"),
    _figure_claim("figure14_circle_counts_visible", 14, 44, "Figure 14", "The rendered panels visually contain 26, 32, and 21 circles respectively.", "figure_visual", "not_demonstrated", "radii"),
)

EXPECTED_CLAIM_COUNT = len(APPENDIX_B_CLAIM_SPECS)
EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in APPENDIX_B_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveAppendixBClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveAppendixBClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveAppendixBClaimInventoryBoundaryIssue]


def alphaevolve_appendix_b_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Appendix B and Figures 10-14 claim inventory."""

    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _claim_record(root_path, spec, page_texts)
        for spec in APPENDIX_B_CLAIM_SPECS
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
        "schema": ALPHAEVOLVE_APPENDIX_B_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "appendix_b_claim_inventory_ready": inventory_ready,
        "alphaevolve_result_reproduction_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": [
            "appendix_b",
            *(f"appendix_b_{index}" for index in range(1, 14)),
            *(f"figure_{index}" for index in range(10, 15)),
        ],
        "inventory_scope": {
            "included": [
                "all substantive Appendix B prose, definitions, equations, bounds, method derivations, result statements, revision notes, lemma statements, and proof steps on PDF pages 38-44",
                "all captions and panel-level visual assertions in Figures 10-14, including panel counts, displayed construction classes, and Figure 12 distance-edge legend semantics",
                "all 19 construction/result instances already named by the Appendix B registry, without treating registry metadata as result reproduction",
                "exact PDF-page anchors plus both code-TODO and paper-TODO ownership for every implementation gap",
            ],
            "excluded": [
                "independent verification of cited prior bounds or mathematical arguments",
                "companion Colab construction payloads, verifier code, or claim-to-cell mapping",
                "local reconstruction, rendering, certificate generation, or recomputation of any Appendix B witness",
                "stochastic rediscovery of any published Appendix B result",
                "citation and bibliography exhaustiveness outside the cited Appendix B assertions",
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
            "This sidecar certifies a bounded claim-level inventory of "
            f"{EXPECTED_CLAIM_COUNT} AlphaEvolve Appendix B and Figures 10-14 "
            "claims across all 13 subsections, all 19 named result instances, "
            "five figure captions, and their visible panel semantics. Registry "
            "metadata is classified only as partial implementation, while "
            "published constructions and outcomes remain undemonstrated. It "
            "does not claim companion Colab retention, executable mathematical "
            "verification, construction payloads, rendered exhibit reproduction, "
            "result recomputation, stochastic rediscovery, AlphaEvolve result "
            "reproduction, or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_appendix_b_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveAppendixBClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_appendix_b_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveAppendixBClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_appendix_b_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveAppendixBClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_APPENDIX_B_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Appendix B claim inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("alphaevolve_result_reproduction_claim_ready") is not False:
        issues.append(_issue("result_reproduction_overclaim", "Appendix B inventory must not claim result reproduction"))
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(_issue("parity_overclaim", "Appendix B inventory must not claim AlphaEvolve parity"))
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
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from the bounded Appendix B claim inventory"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "Appendix B claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in APPENDIX_B_CLAIM_SPECS
            if spec["source_span_id"] not in EXPECTED_NAMED_SOURCE_SPAN_IDS
        }
    )
    if unknown_spans:
        issues.append(_issue("unknown_source_span", f"unknown source spans: {', '.join(unknown_spans)}"))
    unsupported_statuses = sorted(
        {
            spec["implementation_status"]
            for spec in APPENDIX_B_CLAIM_SPECS
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
        issues.append(_issue("missing_source_anchor", f"{expected['missing_anchor_count']} Appendix B claim anchors were not found"))
    if expected["missing_reference_count"]:
        issues.append(_issue("missing_local_reference", f"{expected['missing_reference_count']} evidence or TODO references are stale"))
    expected_ready = (
        expected["source_artifact"]["identity_ok"]
        and expected["claim_count"] == EXPECTED_CLAIM_COUNT
        and expected["missing_anchor_count"] == 0
        and expected["missing_reference_count"] == 0
        and expected["todo_owned_gap_count"] == expected["implementation_gap_count"]
    )
    if data.get("appendix_b_claim_inventory_ready") is not expected_ready:
        issues.append(_issue("invalid_appendix_b_claim_inventory_ready", "Appendix B readiness does not match source, reference, and TODO ownership checks"))
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or str(EXPECTED_CLAIM_COUNT) not in claim_boundary
        or "all 19 named result instances" not in claim_boundary
        or "AlphaEvolve result reproduction" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded Appendix B coverage from reproduction and parity proof"))
    return AlphaEvolveAppendixBClaimInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        claim_count=data.get("claim_count") if isinstance(data.get("claim_count"), int) else 0,
        implemented_local_count=data.get("implemented_local_count") if isinstance(data.get("implemented_local_count"), int) else 0,
        implementation_gap_count=data.get("implementation_gap_count") if isinstance(data.get("implementation_gap_count"), int) else 0,
        missing_anchor_count=expected["missing_anchor_count"],
        missing_reference_count=expected["missing_reference_count"],
        issues=issues,
    )


def render_alphaevolve_appendix_b_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_appendix_b_claim_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve Appendix B claim inventory boundary",
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
    list[AlphaEvolveAppendixBClaimInventoryBoundaryIssue],
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
    return None, [_issue("invalid_shape", "Appendix B claim inventory must be an object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveAppendixBClaimInventoryBoundaryIssue:
    return AlphaEvolveAppendixBClaimInventoryBoundaryIssue(code=code, message=message)
