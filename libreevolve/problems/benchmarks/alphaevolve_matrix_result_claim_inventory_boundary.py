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


ALPHAEVOLVE_MATRIX_RESULT_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_matrix_result_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "section_3_1_table_2_figure_4_claim_inventory_complete_without_"
    "appendix_a_or_result_reproduction"
)
EXPECTED_CLAIM_COUNT = 41
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
    "cascade": (
        "docs/todo/code.md",
        "Extend matrix cascade-run provenance to stochastic discovery and scale.",
    ),
    "figure4": (
        "docs/todo/code.md",
        "Add Figure 4 matrix-discovery exhibit provenance.",
    ),
    "figure9": (
        "docs/todo/code.md",
        "Add Appendix A Figure 9a-9c magnified matrix-diff exhibit provenance.",
    ),
    "historicity": (
        "docs/todo/code.md",
        "Wire matrix headline historicity artifacts into runner/export outputs.",
    ),
    "initial_ideas": (
        "docs/todo/code.md",
        "Add structured initial-program idea provenance for benchmark seeds.",
    ),
    "near_integrality": (
        "docs/todo/code.md",
        "Add a matrix coefficient-domain prompt/evaluator contract for",
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
    "tensor_rank": (
        "docs/todo/code.md",
        "Add matrix tensor-rank applicability and recursive-use caveats.",
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


def _table_row(
    claim_id: str,
    source_anchor: str,
    dimensions: str,
    best_known_rank: int,
    alphaevolve_rank: int,
) -> dict[str, Any]:
    return _claim(
        claim_id,
        "table_2",
        9,
        source_anchor,
        (
            f"Table 2 reports {dimensions} best-known rank {best_known_rank} "
            f"and AlphaEvolve rank {alphaevolve_rank}."
        ),
        "table_2_row_result",
        "not_demonstrated",
        (
            "libreevolve/problems/benchmarks/alphaevolve_appendix_a_matrix.json",
            "papers/matrix_rank_table_artifacts.json",
        ),
        ("suite", "table_export", "baseline_citations"),
    )


MATRIX_RESULT_CLAIM_SPECS = (
    _claim(
        "table2_best_known_reference_comparison",
        "table_2",
        9,
        "⟨𝑚, 𝑛, 𝑝⟩ best known [reference] AlphaEvolve",
        "Table 2 compares AlphaEvolve ranks with cited best-known ranks.",
        "table_2_structure",
        "partially_implemented",
        (
            "papers/matrix_rank_table_artifacts.json",
            "papers/appendix_a_matrix_baseline_citations.json",
        ),
        ("table_export", "baseline_citations"),
    ),
    _table_row("table2_mm_2x4x5_rank32", "⟨2, 4, 5⟩ 33 [42] 32", "<2,4,5>", 33, 32),
    _table_row("table2_mm_2x4x7_rank45", "⟨2, 4, 7⟩ 46 [93] 45", "<2,4,7>", 46, 45),
    _table_row("table2_mm_2x4x8_rank51", "⟨2, 4, 8⟩ 52 [93] 51", "<2,4,8>", 52, 51),
    _table_row("table2_mm_2x5x6_rank47", "⟨2, 5, 6⟩ 48 [93] 47", "<2,5,6>", 48, 47),
    _table_row("table2_mm_3x3x3_rank23", "⟨3, 3, 3⟩ 23 [52] 23", "<3,3,3>", 23, 23),
    _table_row("table2_mm_3x4x6_rank54", "⟨3, 4, 6⟩ 56 [48] 54", "<3,4,6>", 56, 54),
    _table_row("table2_mm_3x4x7_rank63", "⟨3, 4, 7⟩ 66 [91] 63", "<3,4,7>", 66, 63),
    _table_row("table2_mm_3x4x8_rank74", "⟨3, 4, 8⟩ 75 [91] 74", "<3,4,8>", 75, 74),
    _table_row("table2_mm_3x5x6_rank68", "⟨3, 5, 6⟩ 70 [48] 68", "<3,5,6>", 70, 68),
    _table_row("table2_mm_3x5x7_rank80", "⟨3, 5, 7⟩ 82 [91] 80", "<3,5,7>", 82, 80),
    _table_row("table2_mm_4x4x4_rank48", "⟨4, 4, 4⟩ 49 [95] 48", "<4,4,4>", 49, 48),
    _table_row("table2_mm_4x4x5_rank61", "⟨4, 4, 5⟩ 62 [47] 61", "<4,4,5>", 62, 61),
    _table_row("table2_mm_4x4x7_rank85", "⟨4, 4, 7⟩ 87 [93] 85", "<4,4,7>", 87, 85),
    _table_row("table2_mm_4x4x8_rank96", "⟨4, 4, 8⟩ 98 [95] 96", "<4,4,8>", 98, 96),
    _table_row("table2_mm_4x5x6_rank90", "⟨4, 5, 6⟩ 93 [48] 90", "<4,5,6>", 93, 90),
    _table_row("table2_mm_5x5x5_rank93", "⟨5, 5, 5⟩ 93 [72] 93", "<5,5,5>", 93, 93),
    _claim(
        "table2_mnp_le_5_match_or_surpass_exact",
        "table_2",
        9,
        "for all parameters𝑚, 𝑛, 𝑝 ≤ 5, AlphaEvolve either matched or surpassed the best known solutions, and provided exact algorithms",
        "For every m,n,p <= 5 target, match or surpass the best-known rank with an exact algorithm.",
        "table_2_scope_result",
        "not_demonstrated",
        (
            "papers/appendix_a_matrix_subset_scope_artifacts.json",
            "papers/matrix_suite_publication_artifacts.json",
        ),
        ("subset_scope", "suite"),
    ),
    _claim(
        "table2_complex_rows_exact_real_and_complex",
        "table_2",
        9,
        "the algorithms discovered byAlphaEvolveuse complex-valued multiplications which can be used for exact multiplication of complex or real-valued matrices",
        "Certify the declared complex-valued rows for exact complex and real matrix multiplication.",
        "table_2_scope_result",
        "not_demonstrated",
        (
            "papers/matrix_scalar_field_runtime_boundary.json",
            "papers/matrix_suite_publication_artifacts.json",
        ),
        ("scalar_field", "suite"),
    ),
    _claim(
        "table2_decompositions_in_companion_colab",
        "table_2",
        9,
        "The decompositions shown in this table can be found in the accompanying Google Colab",
        "Publish the Table 2 decompositions in a linked reproducible notebook.",
        "table_2_scope_result",
        "not_demonstrated",
        ("papers/matrix_suite_publication_artifacts.json",),
        ("suite", "table_export"),
    ),
    _claim(
        "section3_1_tensor_rank_equals_scalar_multiplications",
        "section_3_1",
        9,
        "The rank (number of terms) of the decomposition exactly specifies the number of scalar multiplications needed to compute the matrix product",
        "Treat tensor-decomposition rank as the scalar-multiplication count for comparable algorithms.",
        "matrix_method",
        "partially_implemented",
        ("papers/matrix_tensor_rank_runtime_boundary.json",),
        ("tensor_rank",),
    ),
    _claim(
        "section3_1_standard_gradient_baseline_components",
        "section_3_1",
        9,
        "standardgradient-basedalgorithm(including an initializer, a reconstruction loss function, and an Adam optimizer",
        "Start matrix search from a standard gradient solver with initializer, reconstruction loss, and Adam.",
        "matrix_method",
        "not_implemented",
        ("papers/matrix_baseline_component_runtime_boundary.json",),
        ("baseline",),
    ),
    _claim(
        "section3_1_sophisticated_algorithms_outperform_approaches",
        "section_3_1",
        10,
        "able to develop sophisticated tensor decomposition algorithms that outperform existing approaches",
        "Demonstrate evolved tensor-decomposition algorithms that outperform prior approaches.",
        "matrix_method",
        "not_demonstrated",
        ("papers/matrix_suite_publication_artifacts.json",),
        ("suite", "baseline_citations"),
    ),
    _claim(
        "section3_1_multi_seed_evaluation_cascade",
        "section_3_1",
        10,
        "run the algorithm, initialized with multiple random seeds using the evaluation cascade described in Section 2.4",
        "Run each target with multiple random seeds through the evaluation cascade.",
        "matrix_method",
        "partially_implemented",
        ("papers/matrix_cascade_run_runtime_boundary.json",),
        ("cascade",),
    ),
    _claim(
        "section3_1_best_rank_and_seed_hit_fraction",
        "section_3_1",
        10,
        "best (lowest) rank achieved on each target as well as the fraction of seeds that achieved this rank",
        "Report each target's best rank and the fraction of seeds attaining it.",
        "matrix_method",
        "partially_implemented",
        (
            "libreevolve/problems/benchmarks/matrix_results.py",
            "papers/matrix_cascade_run_runtime_boundary.json",
        ),
        ("cascade", "suite"),
    ),
    _claim(
        "section3_1_integer_half_integer_rounding_exactness",
        "section_3_1",
        10,
        "we round each element to the nearest integer or the nearest half-integer",
        "Round candidate coefficients to integers or half-integers before exactness verification.",
        "matrix_method",
        "not_implemented",
        ("papers/matrix_near_integrality_runtime_boundary.json",),
        ("near_integrality",),
    ),
    _claim(
        "section3_1_natural_language_near_integrality_prompt",
        "section_3_1",
        10,
        "to encourage the algorithm to generate near-integral solutions, we include this request in natural language in the LLM’s prompt",
        "Inject a natural-language near-integrality instruction into matrix-search prompts.",
        "matrix_method",
        "not_implemented",
        ("papers/matrix_near_integrality_runtime_boundary.json",),
        ("near_integrality",),
    ),
    _claim(
        "section3_1_fourteen_target_sota_improvements",
        "section_3_1",
        10,
        "improve the state of the art for 14 different matrix multiplication targets",
        "Reproduce state-of-the-art improvements on 14 matrix targets.",
        "matrix_headline_result",
        "not_demonstrated",
        (
            "papers/matrix_rank_table_artifacts.json",
            "papers/matrix_suite_publication_artifacts.json",
        ),
        ("suite", "table_export"),
    ),
    _claim(
        "section3_1_recursive_strassen_rank49_any_field",
        "section_3_1",
        10,
        "applying the algorithm of Strassen[95] recursively results in an algorithm with rank (number of scalar multiplications) equal to 49, which works over any field",
        "Support the recursive Strassen rank-49 any-field baseline with evidence.",
        "matrix_headline_result",
        "not_demonstrated",
        ("papers/matrix_headline_historicity_artifacts.json",),
        ("historicity",),
    ),
    _claim(
        "section3_1_fawzi_rank47_field_two",
        "section_3_1",
        10,
        "For the very specific case of multiplying in the field with 2 elements, Fawzi et al.[26] found an algorithm with rank 47",
        "Support the Fawzi rank-47 field-of-two comparison with evidence.",
        "matrix_headline_result",
        "not_demonstrated",
        ("papers/matrix_headline_historicity_artifacts.json",),
        ("historicity", "scalar_field"),
    ),
    _claim(
        "section3_1_fifty_six_year_open_problem",
        "section_3_1",
        10,
        "For 56 years, designing an algorithm with rank less than 49 over any field with characteristic 0 was an open problem",
        "Independently substantiate the 56-year characteristic-zero historicity claim.",
        "matrix_headline_result",
        "not_demonstrated",
        ("papers/matrix_headline_historicity_artifacts.json",),
        ("historicity",),
    ),
    _claim(
        "section3_1_first_rank48_complex_4x4",
        "section_3_1",
        10,
        "AlphaEvolveis the first method to find a rank-48 algorithm to multiply two4 × 4 complex-valued matrices",
        "Reproduce and independently certify the first rank-48 complex 4x4 algorithm claim.",
        "matrix_headline_result",
        "not_demonstrated",
        (
            "papers/matrix_headline_historicity_artifacts.json",
            "papers/matrix_suite_publication_artifacts.json",
        ),
        ("historicity", "suite", "scalar_field"),
    ),
    _claim(
        "section3_1_significant_initial_program_changes",
        "section_3_1",
        10,
        "AlphaEvolve makes significant changes to the initial program",
        "Demonstrate significant accepted changes from the initial matrix-search program.",
        "matrix_initialization_and_collaboration",
        "not_demonstrated",
        ("papers/figure4_matrix_discovery_artifacts.json",),
        ("figure4",),
    ),
    _claim(
        "section3_1_original_ideas_increasingly_better",
        "section_3_1",
        10,
        "introducing several original ideas to design increasingly better algorithms",
        "Trace original evolved ideas to increasingly better matrix-search outcomes.",
        "matrix_initialization_and_collaboration",
        "not_demonstrated",
        ("papers/figure4_matrix_discovery_artifacts.json",),
        ("figure4",),
    ),
    _claim(
        "section3_1_most_table2_simple_initial_program",
        "section_3_1",
        10,
        "most results in Table 2 (including⟨4, 4, 4⟩) were obtained from a simple initial program",
        "Record which Table 2 targets used a simple initial program.",
        "matrix_initialization_and_collaboration",
        "not_demonstrated",
        ("papers/initial_program_seed_variant_matrix.json",),
        ("initial_ideas",),
    ),
    _claim(
        "section3_1_researcher_ideas_boost_performance",
        "section_3_1",
        10,
        "seeding the initial program with our own ideas (such as adding stochasticity to the evaluation function or using evolutionary approaches) could further boost performance",
        "Demonstrate equal-budget gains from researcher-seeded stochastic or evolutionary ideas.",
        "matrix_initialization_and_collaboration",
        "not_demonstrated",
        ("papers/initial_program_seed_variant_matrix.json",),
        ("initial_ideas",),
    ),
    _claim(
        "section3_1_scientific_collaboration_possibility",
        "section_3_1",
        10,
        "highlighting the possibility of scientific collaboration between researchers and AlphaEvolve",
        "Support researcher-agent collaboration claims with executed provenance and review.",
        "matrix_initialization_and_collaboration",
        "not_demonstrated",
        (
            "papers/initial_program_seed_variant_matrix.json",
            "papers/initial_program_idea_provenance_boundary.json",
        ),
        ("initial_ideas",),
    ),
    _claim(
        "section3_1_footnote_non_tensor_nonrecursive_caveat",
        "section_3_1",
        10,
        "There exist algorithms using fewer than 49 multiplications, but they do not correspond to decompositions of the matrix multiplication tensor, and they cannot be applied recursively",
        "Preserve the non-tensor, non-recursive caveat for algorithms below 49 multiplications.",
        "matrix_headline_result",
        "partially_implemented",
        ("papers/matrix_tensor_rank_runtime_boundary.json",),
        ("tensor_rank",),
    ),
    _claim(
        "figure4_full_diff_and_figure9_linkage",
        "figure_4",
        11,
        "The full diff is outlined on the left (see magnified version in Figures 9a to 9c)",
        "Link the Figure 4 full diff to concrete magnified Figure 9 artifacts.",
        "figure_4_exhibit",
        "partially_implemented",
        (
            "papers/figure4_matrix_discovery_artifacts.json",
            "papers/figure9_matrix_diff_artifacts.json",
        ),
        ("figure4", "figure9"),
    ),
    _claim(
        "figure4_optimizer_init_loss_sweep_changes",
        "figure_4",
        11,
        "extensive changes across several components, including the optimizer and weight initialization (top right), the loss function (middle right), and hyperparameter sweep (bottom right)",
        "Reproduce Figure 4's optimizer, initialization, loss, and sweep changes.",
        "figure_4_exhibit",
        "not_demonstrated",
        (
            "papers/figure4_matrix_discovery_artifacts.json",
            "papers/matrix_sweep_space_runtime_boundary.json",
        ),
        ("figure4", "sweep"),
    ),
    _claim(
        "figure4_fifteen_mutation_lineage",
        "figure_4",
        11,
        "These changes are highly non-trivial, requiring 15 mutations during the evolutionary process",
        "Reproduce the accepted 15-mutation lineage shown by Figure 4.",
        "figure_4_exhibit",
        "not_demonstrated",
        ("papers/figure4_matrix_discovery_artifacts.json",),
        ("figure4",),
    ),
)


EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in MATRIX_RESULT_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveMatrixResultClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveMatrixResultClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveMatrixResultClaimInventoryBoundaryIssue]


def alphaevolve_matrix_result_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Section 3.1, Table 2, and Figure 4 claim inventory."""

    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _claim_record(root_path, spec, page_texts)
        for spec in MATRIX_RESULT_CLAIM_SPECS
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
        "schema": ALPHAEVOLVE_MATRIX_RESULT_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "matrix_result_claim_inventory_ready": inventory_ready,
        "alphaevolve_result_reproduction_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": ["section_3_1", "table_2", "figure_4"],
        "inventory_scope": {
            "included": [
                "all sixteen selected matrix-rank rows in Table 2",
                "Table 2 aggregate, exactness, scalar-field, and notebook claims",
                "Section 3.1 matrix-search protocol, rank, historicity, initialization, and collaboration claims",
                "the Section 3.1 footnote 3 tensor-rank and recursive-use caveat",
                "Figure 4 diff, component-change, and mutation-lineage claims",
            ],
            "excluded": [
                "Appendix A Table 3 rows, curation notes, resource-frontier claims, and Figures 9a through 9c details",
                "Sections 3.2 through 5 and Figures 5 through 8",
                "independent result reproduction or external historicity review",
                "equation-, citation-, bibliography-, and all-other-footnote-level exhaustiveness",
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
            "This sidecar certifies a bounded claim-level inventory of 41 "
            "AlphaEvolve matrix-result claims from Section 3.1, Table 2, "
            "Figure 4, and footnote 3. Status labels distinguish local schemas "
            "and deterministic controls from absent search-time behavior and "
            "undemonstrated published outcomes. It does not claim Appendix A "
            "claim exhaustiveness, stochastic rediscovery, exact decomposition "
            "reproduction, independent historicity review, production-scale "
            "evidence, AlphaEvolve result reproduction, or AlphaEvolve system "
            "parity."
        ),
    }


def validate_alphaevolve_matrix_result_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveMatrixResultClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_matrix_result_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveMatrixResultClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_matrix_result_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveMatrixResultClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_MATRIX_RESULT_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported matrix result claim inventory schema"))
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
                "matrix result inventory must not claim result reproduction",
            )
        )
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(
            _issue(
                "parity_overclaim",
                "matrix result inventory must not claim AlphaEvolve parity",
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
                    f"{key} drifted from the bounded matrix result claim inventory",
                )
            )
    if len(EXPECTED_CLAIM_IDS) != EXPECTED_CLAIM_COUNT:
        issues.append(_issue("invalid_spec_count", "matrix result claim count must remain 41"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "matrix result claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in MATRIX_RESULT_CLAIM_SPECS
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
            for spec in MATRIX_RESULT_CLAIM_SPECS
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
                f"{expected['missing_anchor_count']} matrix claim anchors were not found",
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
    if data.get("matrix_result_claim_inventory_ready") is not expected_ready:
        issues.append(
            _issue(
                "invalid_matrix_result_claim_inventory_ready",
                "matrix_result_claim_inventory_ready does not match source, reference, and ownership checks",
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "41" not in claim_boundary
        or "Appendix A claim exhaustiveness" not in claim_boundary
        or "AlphaEvolve result reproduction" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must separate bounded matrix claims from reproduction and parity proof",
            )
        )
    return AlphaEvolveMatrixResultClaimInventoryBoundaryValidation(
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


def render_alphaevolve_matrix_result_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_matrix_result_claim_inventory_boundary(
        boundary
    )
    lines = [
        "AlphaEvolve matrix result claim inventory boundary",
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
    list[AlphaEvolveMatrixResultClaimInventoryBoundaryIssue],
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
    return None, [_issue("invalid_shape", "matrix result claim inventory must be an object")]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveMatrixResultClaimInventoryBoundaryIssue:
    return AlphaEvolveMatrixResultClaimInventoryBoundaryIssue(
        code=code,
        message=message,
    )
