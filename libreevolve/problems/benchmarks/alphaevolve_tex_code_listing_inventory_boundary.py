from __future__ import annotations

import hashlib
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_citation_use_inventory_boundary import (
    EXPECTED_ENTRYPOINT,
    EXPECTED_TEX_CLOSURE_FILES,
    _consume_group,
    _normalize_whitespace,
    _read_source_archive,
    _section_headings,
    _section_path_at,
    _skip_whitespace,
    _tex_dependency_closure,
)
from libreevolve.problems.benchmarks.paper_bibliography import (
    EXPECTED_SOURCE_PAPER_ID,
)


ALPHAEVOLVE_TEX_CODE_LISTING_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_tex_code_listing_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "tex_code_listing_environments_and_lines_dispositioned_without_execution_"
    "or_whole_paper_semantic_exhaustiveness"
)
EXPECTED_LISTING_ENVIRONMENT_COUNT = 8
EXPECTED_MINTED_COUNT = 4
EXPECTED_LSTLISTING_COUNT = 3
EXPECTED_VERBATIM_COUNT = 1
EXPECTED_LINE_COUNT = 305
EXPECTED_NONBLANK_LINE_COUNT = 273
EXPECTED_BLANK_LINE_COUNT = 32
EXPECTED_BOUNDED_CLAIM_COMPONENT_LINE_COUNT = 214
EXPECTED_SOURCE_CONTEXT_ONLY_LINE_COUNT = 21
EXPECTED_ABBREVIATION_LINE_COUNT = 10
EXPECTED_STRUCTURAL_DIFF_HUNK_LINE_COUNT = 4
EXPECTED_STRUCTURAL_BLANK_LINE_COUNT = 32
EXPECTED_STRUCTURAL_DIFF_BLANK_LINE_COUNT = 24
EXPECTED_LISTING_CLAIM_REF_COUNT = 66
EXPECTED_LINE_CLAIM_REF_COUNT = 344
EXPECTED_UNIQUE_MAPPED_CLAIM_COUNT = 60

_SOURCE_INVENTORY_PATH = "papers/alphaevolve_source_inventory_boundary.json"
_SYSTEM_REQUIREMENT_INVENTORY_PATH = (
    "papers/alphaevolve_system_requirement_inventory_boundary.json"
)
_SCHEDULING_CLAIM_INVENTORY_PATH = (
    "papers/alphaevolve_scheduling_claim_inventory_boundary.json"
)
_APPENDIX_A_CLAIM_INVENTORY_PATH = (
    "papers/alphaevolve_appendix_a_claim_inventory_boundary.json"
)
_CLAIM_INVENTORY_PATHS = (
    _SYSTEM_REQUIREMENT_INVENTORY_PATH,
    _SCHEDULING_CLAIM_INVENTORY_PATH,
    _APPENDIX_A_CLAIM_INVENTORY_PATH,
)
_TODO_SPECS = (
    {
        "todo_id": "whole_paper_semantics_code",
        "path": "docs/todo/code.md",
        "required_phrase": (
            "Add exhaustive implementation-evidence mapping for AlphaEvolve"
        ),
    },
    {
        "todo_id": "whole_paper_semantics_paper",
        "path": "docs/todo/papers.md",
        "required_phrase": (
            "Extend the bounded AlphaEvolve claim inventories to the whole paper."
        ),
    },
    {
        "todo_id": "whole_paper_semantics_roadmap",
        "path": "docs/todo/roadmap.md",
        "required_phrase": "whole-paper requirement",
    },
)

_LISTING_SPECS = (
    {
        "listing_id": "methods_canonical_diff_format",
        "source_file": "methods.tex",
        "begin_line": 83,
        "environment": "verbatim",
        "language": None,
        "normalized_options": None,
        "source_page": 7,
        "source_span_id": "section_2_3",
        "source_label": "subsec:generation",
        "semantic_role": "canonical_search_replace_format",
        "line_semantic_role": "canonical_diff_format_component",
        "expected_line_count": 5,
        "expected_nonblank_line_count": 5,
        "display_first_line_number": None,
    },
    {
        "listing_id": "figure3_marked_program",
        "source_file": "grounding_example.tex",
        "begin_line": 7,
        "environment": "minted",
        "language": "python",
        "normalized_options": "fontsize=\\tiny, bgcolor=backcolour",
        "source_page": 6,
        "source_span_id": "figure_3",
        "source_label": "fig:grounding-api",
        "semantic_role": "figure3_marked_program",
        "line_semantic_role": "figure3_marked_program_component",
        "expected_line_count": 24,
        "expected_nonblank_line_count": 17,
        "display_first_line_number": None,
    },
    {
        "listing_id": "figure3_generated_diff",
        "source_file": "grounding_example.tex",
        "begin_line": 41,
        "environment": "minted",
        "language": "python",
        "normalized_options": (
            "fontsize=\\tiny, bgcolor=backcolour, escapeinside=||, "
            "breaksymbolleft={}"
        ),
        "source_page": 6,
        "source_span_id": "figure_3",
        "source_label": "fig:grounding-llm",
        "semantic_role": "figure3_generated_diff",
        "line_semantic_role": "figure3_generated_diff_component",
        "expected_line_count": 22,
        "expected_nonblank_line_count": 20,
        "display_first_line_number": None,
    },
    {
        "listing_id": "figure3_assembled_prompt",
        "source_file": "grounding_example.tex",
        "begin_line": 77,
        "environment": "minted",
        "language": "python",
        "normalized_options": (
            "fontsize=\\tiny, bgcolor=backcolour, escapeinside=||, "
            "breaksymbolleft={}"
        ),
        "source_page": 6,
        "source_span_id": "figure_3",
        "source_label": "fig:grounding-prompt",
        "semantic_role": "figure3_assembled_prompt",
        "line_semantic_role": "figure3_assembled_prompt_component",
        "expected_line_count": 54,
        "expected_nonblank_line_count": 38,
        "display_first_line_number": None,
    },
    {
        "listing_id": "figure6_scheduling_heuristic",
        "source_file": "results.tex",
        "begin_line": 126,
        "environment": "minted",
        "language": "python",
        "normalized_options": "linenos, breaklines=false,",
        "source_page": 14,
        "source_span_id": "figure_6",
        "source_label": "fig:alphaevolve_heuristic",
        "semantic_role": "figure6_scheduling_heuristic",
        "line_semantic_role": "figure6_scheduling_heuristic_component",
        "expected_line_count": 7,
        "expected_nonblank_line_count": 6,
        "display_first_line_number": 1,
    },
    {
        "listing_id": "figure9_program_diff_part_1",
        "source_file": "discovered_program_appendix.tex",
        "begin_line": 5,
        "environment": "lstlisting",
        "language": None,
        "normalized_options": (
            "style=pydiff, backgroundcolor=\\color{backcolour}"
        ),
        "source_page": 35,
        "source_span_id": "figure_9",
        "source_label": "fig:relaxed-opt-diff-appendix-1",
        "semantic_role": "figure9_program_diff_part_1",
        "line_semantic_role": "figure9_program_diff_component",
        "expected_line_count": 65,
        "expected_nonblank_line_count": 63,
        "display_first_line_number": 1,
    },
    {
        "listing_id": "figure9_program_diff_part_2",
        "source_file": "discovered_program_appendix.tex",
        "begin_line": 85,
        "environment": "lstlisting",
        "language": None,
        "normalized_options": (
            "style=pydiff, backgroundcolor=\\color{backcolour}, firstnumber=66"
        ),
        "source_page": 36,
        "source_span_id": "figure_9",
        "source_label": "fig:relaxed-opt-diff-appendix-2",
        "semantic_role": "figure9_program_diff_part_2",
        "line_semantic_role": "figure9_program_diff_component",
        "expected_line_count": 65,
        "expected_nonblank_line_count": 62,
        "display_first_line_number": 66,
    },
    {
        "listing_id": "figure9_program_diff_part_3",
        "source_file": "discovered_program_appendix.tex",
        "begin_line": 164,
        "environment": "lstlisting",
        "language": None,
        "normalized_options": (
            "style=pydiff, backgroundcolor=\\color{backcolour}, firstnumber=131"
        ),
        "source_page": 37,
        "source_span_id": "figure_9",
        "source_label": "fig:relaxed-opt-diff-appendix-3",
        "semantic_role": "figure9_program_diff_part_3",
        "line_semantic_role": "figure9_program_diff_component",
        "expected_line_count": 63,
        "expected_nonblank_line_count": 62,
        "display_first_line_number": 131,
    },
)
_LISTING_SPEC_BY_LOCATION = {
    (spec["source_file"], spec["begin_line"]): spec for spec in _LISTING_SPECS
}

_DEFAULT_NONSTRUCTURAL_CLAIMS = {
    "methods_canonical_diff_format": ("generation_search_replace_blocks",),
    "figure3_marked_program": ("figure3_supervised_pipeline_exhibit",),
    "figure3_generated_diff": ("figure3_supervised_pipeline_exhibit",),
    "figure3_assembled_prompt": ("figure3_supervised_pipeline_exhibit",),
}

# Ranges use retained-TeX source line numbers. Structural blank, abbreviation,
# and hunk lines are filtered before these semantic mappings are applied.
_LINE_CLAIM_RANGES = (
    (
        "figure3_marked_program",
        18,
        24,
        (
            "task_evolved_blocks_and_skeleton",
        ),
    ),
    (
        "figure3_marked_program",
        8,
        25,
        (
            "task_multiple_marked_components",
            "task_minimal_marker_integration",
            "task_evolved_blocks_and_skeleton",
        ),
        (8, 13, 17, 25),
    ),
    (
        "figure3_marked_program",
        29,
        31,
        ("task_fixed_evaluate_signature",),
    ),
    (
        "figure3_marked_program",
        31,
        31,
        ("task_scalar_metric_mapping",),
    ),
    (
        "figure3_generated_diff",
        45,
        63,
        ("generation_search_replace_blocks",),
    ),
    (
        "figure3_assembled_prompt",
        78,
        82,
        (
            "prompt_prior_solutions_and_instructions",
            "prompt_long_context_customization",
        ),
    ),
    (
        "figure3_assembled_prompt",
        86,
        96,
        ("prompt_prior_solutions_and_instructions",),
    ),
    (
        "figure3_assembled_prompt",
        100,
        102,
        ("prompt_prior_solutions_and_instructions",),
    ),
    (
        "figure3_assembled_prompt",
        123,
        131,
        ("prompt_prior_solutions_and_instructions",),
    ),
    (
        "figure3_assembled_prompt",
        84,
        84,
        ("prompt_rendered_evaluation_results",),
    ),
    (
        "figure3_assembled_prompt",
        104,
        117,
        ("prompt_rendered_evaluation_results",),
    ),
    (
        "figure3_assembled_prompt",
        120,
        120,
        ("generation_search_replace_blocks",),
    ),
    (
        "figure3_assembled_prompt",
        128,
        131,
        ("generation_search_replace_blocks",),
    ),
    (
        "figure6_scheduling_heuristic",
        129,
        129,
        ("figure6_function_signature",),
    ),
    (
        "figure6_scheduling_heuristic",
        130,
        130,
        ("figure6_cpu_residual_definition",),
    ),
    (
        "figure6_scheduling_heuristic",
        131,
        131,
        ("figure6_memory_residual_definition",),
    ),
    (
        "figure6_scheduling_heuristic",
        133,
        133,
        ("figure6_negative_residual_sum",),
    ),
    (
        "figure6_scheduling_heuristic",
        134,
        134,
        ("figure6_memory_over_cpu_cross_ratio",),
    ),
    (
        "figure6_scheduling_heuristic",
        135,
        135,
        ("figure6_cpu_over_memory_cross_ratio",),
    ),
    (
        "figure9_program_diff_part_1",
        10,
        13,
        ("figure9_adam_to_adamw",),
    ),
    (
        "figure9_program_diff_part_1",
        12,
        12,
        ("figure9_adamw_weight_decay",),
    ),
    (
        "figure9_program_diff_part_1",
        17,
        21,
        (
            "figure9_initialization_scale_factor",
            "figure9_complex64_normal_initialization",
        ),
    ),
    (
        "figure9_program_diff_part_1",
        27,
        33,
        ("figure9_gradient_noise",),
    ),
    (
        "figure9_program_diff_part_1",
        35,
        43,
        ("figure9_decomposition_noise",),
    ),
    (
        "figure9_program_diff_part_1",
        37,
        39,
        ("figure9_decomposition_noise_linear_decay",),
    ),
    (
        "figure9_program_diff_part_1",
        45,
        49,
        ("figure9_clip_cycle_2000_steps",),
    ),
    (
        "figure9_program_diff_part_1",
        51,
        56,
        ("figure9_cosine_clip_threshold",),
    ),
    (
        "figure9_program_diff_part_1",
        58,
        70,
        ("figure9_soft_clip_real_component",),
    ),
    (
        "figure9_program_diff_part_1",
        63,
        70,
        ("figure9_soft_clip_excess_slope",),
    ),
    (
        "figure9_program_diff_part_2",
        87,
        100,
        (
            "figure9_soft_clip_imaginary_component",
            "figure9_soft_clip_excess_slope",
        ),
    ),
    (
        "figure9_program_diff_part_2",
        110,
        115,
        ("figure9_target_tensor_noise",),
    ),
    (
        "figure9_program_diff_part_2",
        117,
        126,
        (
            "figure9_hallucination_probability",
            "figure9_hallucination_replacement_scale",
        ),
    ),
    (
        "figure9_program_diff_part_2",
        128,
        132,
        ("figure9_hallucination_applied_to_factors",),
    ),
    (
        "figure9_program_diff_part_2",
        136,
        137,
        ("figure9_reconstruction_uses_noisy_target",),
    ),
    (
        "figure9_program_diff_part_2",
        140,
        140,
        ("figure9_real_total_loss",),
    ),
    (
        "figure9_program_diff_part_2",
        142,
        149,
        ("figure9_min_real_imag_half_integer_distance",),
    ),
    (
        "figure9_program_diff_part_2",
        143,
        147,
        ("figure9_real_half_integer_distance",),
    ),
    (
        "figure9_program_diff_part_2",
        144,
        148,
        ("figure9_imaginary_half_integer_distance",),
    ),
    (
        "figure9_program_diff_part_3",
        165,
        166,
        ("figure9_integer_distance",),
    ),
    (
        "figure9_program_diff_part_3",
        168,
        171,
        ("figure9_combined_half_integer_and_integer_loss",),
    ),
    (
        "figure9_program_diff_part_3",
        173,
        175,
        ("figure9_discretization_factor_average",),
    ),
    (
        "figure9_program_diff_part_3",
        177,
        179,
        ("figure9_discretization_weight_linear_schedule",),
    ),
    (
        "figure9_program_diff_part_3",
        181,
        185,
        ("figure9_half_integer_cycle_length",),
    ),
    (
        "figure9_program_diff_part_3",
        186,
        189,
        ("figure9_half_integer_cosine_multiplier",),
    ),
    (
        "figure9_program_diff_part_3",
        187,
        189,
        ("figure9_half_integer_start_floor",),
    ),
    (
        "figure9_program_diff_part_3",
        191,
        194,
        ("figure9_total_loss_adds_discretization",),
    ),
    (
        "figure9_program_diff_part_3",
        196,
        200,
        ("figure9_quadratic_large_value_penalty",),
    ),
    (
        "figure9_program_diff_part_3",
        201,
        201,
        ("figure9_large_value_penalty_weight",),
    ),
    (
        "figure9_program_diff_part_3",
        203,
        203,
        ("figure9_real_total_loss",),
    ),
    (
        "figure9_program_diff_part_3",
        210,
        212,
        ("figure9_sweep_init_scale_range",),
    ),
    (
        "figure9_program_diff_part_3",
        211,
        213,
        ("figure9_sweep_learning_rate_range",),
    ),
    (
        "figure9_program_diff_part_3",
        214,
        214,
        ("figure9_sweep_discretization_weight",),
    ),
    (
        "figure9_program_diff_part_3",
        215,
        215,
        ("figure9_sweep_hallucination_probability",),
    ),
    (
        "figure9_program_diff_part_3",
        216,
        216,
        ("figure9_sweep_hallucination_scale",),
    ),
    (
        "figure9_program_diff_part_3",
        217,
        217,
        ("figure9_sweep_decomposition_noise",),
    ),
    (
        "figure9_program_diff_part_3",
        218,
        218,
        ("figure9_sweep_target_noise",),
    ),
    (
        "figure9_program_diff_part_3",
        219,
        219,
        ("figure9_sweep_weight_decay",),
    ),
    (
        "figure9_program_diff_part_3",
        220,
        220,
        ("figure9_sweep_clip_min",),
    ),
    (
        "figure9_program_diff_part_3",
        221,
        221,
        ("figure9_sweep_clip_max",),
    ),
    (
        "figure9_program_diff_part_3",
        222,
        222,
        ("figure9_sweep_large_value_penalty",),
    ),
    (
        "figure9_program_diff_part_3",
        223,
        224,
        ("figure9_sweep_gradient_noise",),
    ),
    (
        "figure9_program_diff_part_3",
        225,
        225,
        ("figure9_sweep_half_integer_start",),
    ),
)

_LISTING_BEGIN_RE = re.compile(
    r"\\begin\s*\{(minted|lstlisting|verbatim)\}"
)


@dataclass(frozen=True)
class AlphaEvolveTexCodeListingInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveTexCodeListingInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    listing_environment_count: int
    line_count: int
    unmapped_line_count: int
    unresolved_reference_count: int
    issues: list[AlphaEvolveTexCodeListingInventoryBoundaryIssue]


def alphaevolve_tex_code_listing_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Inventory and disposition every retained TeX code-listing line."""

    root_path = Path(root)
    source_artifact, archive_texts, source_errors = _read_source_archive(root_path)
    tex_texts = {
        name: text
        for name, text in archive_texts.items()
        if name.casefold().endswith(".tex")
    }
    closure = _tex_dependency_closure(tex_texts, EXPECTED_ENTRYPOINT)
    parsed_listings, parse_errors = _parse_listing_environments(tex_texts, closure)
    claim_paths, named_span_ids, reference_errors = _reference_ids(root_path)
    listings, lines, disposition_errors = _disposition_records(
        parsed_listings,
        claim_paths,
        named_span_ids,
    )
    source_errors = sorted(set([*source_errors, *reference_errors]))
    parse_errors = sorted(set([*parse_errors, *disposition_errors]))
    environment_counts = Counter(
        listing["environment"] for listing in listings
    )
    disposition_counts = Counter(line["disposition"] for line in lines)
    listing_claim_ref_count = sum(
        len(listing["claim_refs"]) for listing in listings
    )
    line_claim_ref_count = sum(len(line["claim_refs"]) for line in lines)
    unique_mapped_claim_ids = sorted(
        {
            ref["claim_id"]
            for line in lines
            for ref in line["claim_refs"]
        }
    )
    unresolved_reference_count = sum(
        1
        for record in [*listings, *lines]
        for ref in [*record["claim_refs"], *record["named_span_refs"]]
        if not ref["resolved"]
    )
    todo_refs = [_todo_ref(root_path, spec) for spec in _TODO_SPECS]
    todo_ownership_ready = all(
        ref["exists"] and ref["required_phrase_present"] for ref in todo_refs
    )
    unmapped_line_count = disposition_counts["unmapped"]
    ready = (
        source_artifact["identity_ok"]
        and closure == list(EXPECTED_TEX_CLOSURE_FILES)
        and not source_errors
        and not parse_errors
        and len(listings) == EXPECTED_LISTING_ENVIRONMENT_COUNT
        and len(lines) == EXPECTED_LINE_COUNT
        and environment_counts["minted"] == EXPECTED_MINTED_COUNT
        and environment_counts["lstlisting"] == EXPECTED_LSTLISTING_COUNT
        and environment_counts["verbatim"] == EXPECTED_VERBATIM_COUNT
        and disposition_counts["bounded_claim_component"]
        == EXPECTED_BOUNDED_CLAIM_COMPONENT_LINE_COUNT
        and disposition_counts["source_context_only_baseline_line"]
        == EXPECTED_SOURCE_CONTEXT_ONLY_LINE_COUNT
        and disposition_counts["source_context_only_abbreviation_line"]
        == EXPECTED_ABBREVIATION_LINE_COUNT
        and disposition_counts["structural_diff_hunk_line"]
        == EXPECTED_STRUCTURAL_DIFF_HUNK_LINE_COUNT
        and disposition_counts["structural_blank_line"]
        == EXPECTED_STRUCTURAL_BLANK_LINE_COUNT
        and disposition_counts["structural_diff_blank_line"]
        == EXPECTED_STRUCTURAL_DIFF_BLANK_LINE_COUNT
        and listing_claim_ref_count == EXPECTED_LISTING_CLAIM_REF_COUNT
        and line_claim_ref_count == EXPECTED_LINE_CLAIM_REF_COUNT
        and len(unique_mapped_claim_ids) == EXPECTED_UNIQUE_MAPPED_CLAIM_COUNT
        and unmapped_line_count == 0
        and unresolved_reference_count == 0
        and todo_ownership_ready
    )
    nonblank_line_count = sum(bool(line["raw_text"].strip()) for line in lines)
    blank_line_count = len(lines) - nonblank_line_count
    listing_breakdown = {
        listing["listing_id"]: {
            "environment": listing["environment"],
            "source_file": listing["source_file"],
            "source_page": listing["source_page"],
            "line_count": listing["line_count"],
            "nonblank_line_count": listing["nonblank_line_count"],
            "claim_ref_count": len(listing["claim_refs"]),
        }
        for listing in listings
    }
    return {
        "schema": ALPHAEVOLVE_TEX_CODE_LISTING_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "retained_listing_inventory_ready": ready,
        "listing_line_disposition_ready": ready,
        "listing_execution_ready": False,
        "figure_result_reproduction_ready": False,
        "whole_paper_proposition_exhaustiveness_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "new_claim_count": 0,
        "source_artifact": source_artifact,
        "source_errors": source_errors,
        "parse_errors": parse_errors,
        "source_closure": closure,
        "listing_environment_count": len(listings),
        "minted_count": environment_counts["minted"],
        "lstlisting_count": environment_counts["lstlisting"],
        "verbatim_count": environment_counts["verbatim"],
        "line_count": len(lines),
        "nonblank_line_count": nonblank_line_count,
        "blank_line_count": blank_line_count,
        "bounded_claim_component_line_count": disposition_counts[
            "bounded_claim_component"
        ],
        "source_context_only_line_count": disposition_counts[
            "source_context_only_baseline_line"
        ],
        "abbreviation_line_count": disposition_counts[
            "source_context_only_abbreviation_line"
        ],
        "structural_diff_hunk_line_count": disposition_counts[
            "structural_diff_hunk_line"
        ],
        "structural_blank_line_count": disposition_counts[
            "structural_blank_line"
        ],
        "structural_diff_blank_line_count": disposition_counts[
            "structural_diff_blank_line"
        ],
        "listing_claim_ref_count": listing_claim_ref_count,
        "line_claim_ref_count": line_claim_ref_count,
        "unique_mapped_claim_count": len(unique_mapped_claim_ids),
        "unique_mapped_claim_ids": unique_mapped_claim_ids,
        "unmapped_line_count": unmapped_line_count,
        "unresolved_reference_count": unresolved_reference_count,
        "listing_breakdown": listing_breakdown,
        "listing_environment_records": listings,
        "line_records": lines,
        "active_todo_refs": todo_refs,
        "todo_ownership_ready": todo_ownership_ready,
        "inventory_scope": {
            "included": [
                "all minted, lstlisting, and verbatim environments in the recursive main.tex closure",
                "all 305 physical source lines between the eight retained listing environment boundaries",
                "line-level bounded-claim, baseline-context, abbreviation, hunk, or blank disposition",
                "60 existing bounded claim ids represented by Section 2.3, Figure 3, Figure 6, and Figure 9 listing lines",
                "source anchors, hashes, environment options, languages, and display-line metadata",
            ],
            "excluded": [
                "inline texttt fragments and code rendered only inside bitmap or PDF figure assets",
                "expansion of ellipsis and bracketed abbreviation markers into omitted source",
                "execution, compilation, or behavioral verification of abbreviated paper snippets",
                "pixel-exact minted or listings package rendering reproduction",
                "new semantic claims beyond references to existing bounded inventories",
                "whole-paper proposition exhaustiveness, result reproduction, or AlphaEvolve system parity",
            ],
        },
        "claim_boundary": (
            "This sidecar certifies source-pinned environment and physical-line "
            "disposition for all 8 retained TeX code listings and all 305 lines "
            "inside them. It maps 214 lines through 344 references to 60 "
            "existing bounded claims, classifies 21 unchanged Figure 9 lines "
            "as source context, 10 ellipsis lines as abbreviations, 4 lines as "
            "diff hunk syntax, 32 lines as structural blanks, and 24 plus-only "
            "lines as structural diff blanks. It adds zero claims and does not "
            "establish omitted-code recovery, snippet execution, figure-result "
            "reproduction, whole-paper proposition exhaustiveness, or "
            "AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_tex_code_listing_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveTexCodeListingInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_tex_code_listing_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveTexCodeListingInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_tex_code_listing_inventory_boundary_record(root)
    issues: list[AlphaEvolveTexCodeListingInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_TEX_CODE_LISTING_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TeX code-listing inventory schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    for key, code in (
        ("listing_execution_ready", "listing_execution_overclaim"),
        ("figure_result_reproduction_ready", "figure_reproduction_overclaim"),
        (
            "whole_paper_proposition_exhaustiveness_ready",
            "proposition_exhaustiveness_overclaim",
        ),
        ("alphaevolve_parity_claim_ready", "parity_overclaim"),
    ):
        if data.get(key) is not False:
            issues.append(_issue(code, f"{key} must remain false for listing disposition evidence"))
    if data.get("new_claim_count") != 0:
        issues.append(_issue("new_claim_overclaim", "listing disposition must add zero bounded claims"))
    for key in (
        "source_artifact",
        "source_errors",
        "parse_errors",
        "source_closure",
        "listing_environment_count",
        "minted_count",
        "lstlisting_count",
        "verbatim_count",
        "line_count",
        "nonblank_line_count",
        "blank_line_count",
        "bounded_claim_component_line_count",
        "source_context_only_line_count",
        "abbreviation_line_count",
        "structural_diff_hunk_line_count",
        "structural_blank_line_count",
        "structural_diff_blank_line_count",
        "listing_claim_ref_count",
        "line_claim_ref_count",
        "unique_mapped_claim_count",
        "unique_mapped_claim_ids",
        "unmapped_line_count",
        "unresolved_reference_count",
        "listing_breakdown",
        "listing_environment_records",
        "line_records",
        "active_todo_refs",
        "todo_ownership_ready",
        "inventory_scope",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from the retained TeX listing inventory"))
    for key in ("retained_listing_inventory_ready", "listing_line_disposition_ready"):
        if data.get(key) is not expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} does not match source, parser, reference, and TODO checks"))
    if not expected["source_artifact"]["identity_ok"]:
        issues.append(_issue("source_archive_identity_mismatch", "retained AlphaEvolve TeX archive identity does not match the pinned source"))
    if expected["source_errors"]:
        issues.append(_issue("source_inventory_incomplete", "TeX code-listing inventory inputs are incomplete"))
    if expected["parse_errors"] or expected["unmapped_line_count"]:
        issues.append(_issue("listing_line_parse_incomplete", "one or more retained listing lines lack a stable disposition"))
    if not expected["retained_listing_inventory_ready"]:
        issues.append(_issue("listing_inventory_incomplete", "retained listing counts or dispositions do not match the source contract"))
    if expected["unresolved_reference_count"]:
        issues.append(_issue("unresolved_listing_reference", "one or more claim or named-span references are unresolved"))
    if not expected["todo_ownership_ready"]:
        issues.append(_issue("unowned_remaining_listing_gap", "remaining execution, semantic, and reproduction gaps require active TODO ownership"))
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "all 8 retained TeX code listings and all 305 lines" not in claim_boundary
        or "60 existing bounded claims" not in claim_boundary
        or "adds zero claims" not in claim_boundary
        or "does not establish omitted-code recovery" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate listing-line disposition from execution, reproduction, and parity claims"))
    return AlphaEvolveTexCodeListingInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=(
            data.get("boundary_status")
            if isinstance(data.get("boundary_status"), str)
            else None
        ),
        listing_environment_count=(
            data.get("listing_environment_count")
            if isinstance(data.get("listing_environment_count"), int)
            else 0
        ),
        line_count=(
            data.get("line_count") if isinstance(data.get("line_count"), int) else 0
        ),
        unmapped_line_count=(
            data.get("unmapped_line_count")
            if isinstance(data.get("unmapped_line_count"), int)
            else 0
        ),
        unresolved_reference_count=(
            data.get("unresolved_reference_count")
            if isinstance(data.get("unresolved_reference_count"), int)
            else 0
        ),
        issues=issues,
    )


def render_alphaevolve_tex_code_listing_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_tex_code_listing_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve TeX code-listing inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| listing_environment_count | {validation.listing_environment_count} |",
        f"| line_count | {validation.line_count} |",
        f"| unmapped_line_count | {validation.unmapped_line_count} |",
        f"| unresolved_reference_count | {validation.unresolved_reference_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _parse_listing_environments(
    tex_texts: dict[str, str],
    closure: list[str],
) -> tuple[list[dict[str, Any]], list[str]]:
    records: list[dict[str, Any]] = []
    errors: list[str] = []
    seen_locations: set[tuple[str, int]] = set()
    for source_file in closure:
        text = tex_texts.get(source_file, "")
        headings = _section_headings(text)
        for match in _LISTING_BEGIN_RE.finditer(text):
            environment = match.group(1)
            begin_line = _line_number(text, match.start())
            location = (source_file, begin_line)
            spec = _LISTING_SPEC_BY_LOCATION.get(location)
            if spec is None:
                errors.append(
                    f"unexpected_listing_environment:{source_file}:{begin_line}:{environment}"
                )
                continue
            seen_locations.add(location)
            cursor = match.end()
            options: str | None = None
            language: str | None = None
            if environment in {"minted", "lstlisting"}:
                cursor = _skip_whitespace(text, cursor)
                if cursor < len(text) and text[cursor] == "[":
                    options, next_cursor = _consume_group(text, cursor, "[", "]")
                    if options is None:
                        errors.append(
                            f"malformed_listing_options:{source_file}:{begin_line}"
                        )
                        continue
                    cursor = next_cursor
            if environment == "minted":
                cursor = _skip_whitespace(text, cursor)
                language, next_cursor = _consume_group(text, cursor, "{", "}")
                if language is None:
                    errors.append(
                        f"missing_minted_language:{source_file}:{begin_line}"
                    )
                    continue
                cursor = next_cursor
            newline = text.find("\n", cursor)
            if newline < 0 or text[cursor:newline].strip():
                errors.append(
                    f"listing_begin_not_line_terminated:{source_file}:{begin_line}"
                )
                continue
            content_start = newline + 1
            end_match = re.search(
                rf"\\end\s*\{{{re.escape(environment)}\}}",
                text[content_start:],
            )
            if end_match is None:
                errors.append(
                    f"unterminated_listing_environment:{source_file}:{begin_line}:{environment}"
                )
                continue
            content_end = content_start + end_match.start()
            end_start = content_start + end_match.start()
            end_end = content_start + end_match.end()
            raw_content = text[content_start:content_end]
            normalized_options = (
                _normalize_whitespace(options) if options is not None else None
            )
            line_count = len(raw_content.splitlines())
            nonblank_line_count = sum(
                bool(line.strip()) for line in raw_content.splitlines()
            )
            if environment != spec["environment"]:
                errors.append(
                    f"listing_environment_mismatch:{source_file}:{begin_line}"
                )
            if language != spec["language"]:
                errors.append(f"listing_language_mismatch:{source_file}:{begin_line}")
            if normalized_options != spec["normalized_options"]:
                errors.append(f"listing_options_mismatch:{source_file}:{begin_line}")
            if line_count != spec["expected_line_count"]:
                errors.append(f"listing_line_count_mismatch:{source_file}:{begin_line}")
            if nonblank_line_count != spec["expected_nonblank_line_count"]:
                errors.append(
                    f"listing_nonblank_line_count_mismatch:{source_file}:{begin_line}"
                )
            records.append(
                {
                    **spec,
                    "_source_text": text,
                    "_content_start": content_start,
                    "_content_end": content_end,
                    "_begin_start": match.start(),
                    "_begin_end": cursor,
                    "_end_start": end_start,
                    "_end_end": end_end,
                    "_headings": headings,
                    "raw_options": options,
                    "normalized_options": normalized_options,
                    "language": language,
                    "raw_content": raw_content,
                }
            )
    missing_locations = sorted(set(_LISTING_SPEC_BY_LOCATION) - seen_locations)
    errors.extend(
        f"missing_listing_environment:{source_file}:{begin_line}"
        for source_file, begin_line in missing_locations
    )
    records.sort(key=lambda item: (closure.index(item["source_file"]), item["begin_line"]))
    return records, sorted(set(errors))


def _disposition_records(
    parsed_listings: list[dict[str, Any]],
    claim_paths: dict[str, str],
    named_span_ids: set[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    listing_records: list[dict[str, Any]] = []
    line_records: list[dict[str, Any]] = []
    errors: list[str] = []
    for listing in parsed_listings:
        text = listing["_source_text"]
        content_start = listing["_content_start"]
        physical_lines = listing["raw_content"].splitlines(keepends=True)
        listing_lines: list[dict[str, Any]] = []
        cursor = content_start
        for ordinal, physical_line in enumerate(physical_lines, start=1):
            raw_text = physical_line.rstrip("\r\n")
            source_line = _line_number(text, cursor)
            structural_kind = _structural_line_kind(raw_text)
            claim_ids = (
                []
                if structural_kind is not None
                else _line_claim_ids(listing["listing_id"], source_line)
            )
            claim_refs = _claim_ref_records(claim_ids, claim_paths)
            if structural_kind is not None:
                disposition = structural_kind
                semantic_role = structural_kind
            elif claim_refs:
                disposition = "bounded_claim_component"
                semantic_role = listing["line_semantic_role"]
            elif listing["listing_id"].startswith("figure9_program_diff_part_"):
                disposition = "source_context_only_baseline_line"
                semantic_role = "figure9_unchanged_baseline_context"
            else:
                disposition = "unmapped"
                semantic_role = "unmapped"
                errors.append(
                    f"unmapped_listing_line:{listing['source_file']}:{source_line}"
                )
            display_first = listing["display_first_line_number"]
            line_record = {
                "listing_line_id": f"{listing['listing_id']}_line_{ordinal:03d}",
                "listing_id": listing["listing_id"],
                "source_file": listing["source_file"],
                "source_line": source_line,
                "source_column": _column_number(text, cursor),
                "source_page": listing["source_page"],
                "section_path": _section_path_at(listing["_headings"], cursor),
                "content_line_ordinal": ordinal,
                "display_line_number": (
                    display_first + ordinal - 1
                    if isinstance(display_first, int)
                    else None
                ),
                "raw_text": raw_text,
                "normalized_text": _normalize_whitespace(raw_text),
                "text_sha256": hashlib.sha256(raw_text.encode("utf-8")).hexdigest(),
                "diff_marker": _diff_marker(raw_text),
                "semantic_role": semantic_role,
                "disposition": disposition,
                "claim_refs": claim_refs,
                "named_span_refs": [],
            }
            listing_lines.append(line_record)
            line_records.append(line_record)
            cursor += len(physical_line)
        listing_claim_ids: list[str] = []
        for line in listing_lines:
            for ref in line["claim_refs"]:
                if ref["claim_id"] not in listing_claim_ids:
                    listing_claim_ids.append(ref["claim_id"])
        listing_claim_refs = _claim_ref_records(listing_claim_ids, claim_paths)
        named_span_ref = _named_span_ref(listing["source_span_id"], named_span_ids)
        if not named_span_ref["resolved"]:
            errors.append(f"unresolved_listing_span:{listing['source_span_id']}")
        disposition_counts = Counter(line["disposition"] for line in listing_lines)
        listing_records.append(
            {
                "listing_id": listing["listing_id"],
                "source_file": listing["source_file"],
                "begin_line": listing["begin_line"],
                "end_line": _line_number(text, listing["_end_start"]),
                "source_page": listing["source_page"],
                "source_span_id": listing["source_span_id"],
                "source_label": listing["source_label"],
                "section_path": _section_path_at(
                    listing["_headings"], listing["_begin_start"]
                ),
                "environment": listing["environment"],
                "language": listing["language"],
                "raw_options": listing["raw_options"],
                "normalized_options": listing["normalized_options"],
                "semantic_role": listing["semantic_role"],
                "disposition": "bounded_claim_listing",
                "begin_command": text[
                    listing["_begin_start"] : listing["_begin_end"]
                ],
                "begin_command_sha256": hashlib.sha256(
                    text[listing["_begin_start"] : listing["_begin_end"]].encode(
                        "utf-8"
                    )
                ).hexdigest(),
                "content_sha256": hashlib.sha256(
                    listing["raw_content"].encode("utf-8")
                ).hexdigest(),
                "line_count": len(listing_lines),
                "nonblank_line_count": sum(
                    bool(line["raw_text"].strip()) for line in listing_lines
                ),
                "bounded_claim_component_line_count": disposition_counts[
                    "bounded_claim_component"
                ],
                "source_context_only_line_count": disposition_counts[
                    "source_context_only_baseline_line"
                ],
                "abbreviation_line_count": disposition_counts[
                    "source_context_only_abbreviation_line"
                ],
                "structural_line_count": sum(
                    count
                    for disposition, count in disposition_counts.items()
                    if disposition.startswith("structural_")
                ),
                "unmapped_line_count": disposition_counts["unmapped"],
                "line_ids": [line["listing_line_id"] for line in listing_lines],
                "claim_refs": listing_claim_refs,
                "named_span_refs": [named_span_ref],
            }
        )
    return listing_records, line_records, sorted(set(errors))


def _structural_line_kind(raw_text: str) -> str | None:
    stripped = raw_text.strip()
    if not stripped:
        return "structural_blank_line"
    if stripped in {"+", "-"}:
        return "structural_diff_blank_line"
    if stripped.startswith("@@ "):
        return "structural_diff_hunk_line"
    if stripped.strip("|") in {"...", "[...]"}:
        return "source_context_only_abbreviation_line"
    return None


def _line_claim_ids(listing_id: str, source_line: int) -> list[str]:
    claim_ids = list(_DEFAULT_NONSTRUCTURAL_CLAIMS.get(listing_id, ()))
    for range_spec in _LINE_CLAIM_RANGES:
        range_listing_id, start, end, range_claim_ids, *explicit_lines = range_spec
        if range_listing_id != listing_id or not start <= source_line <= end:
            continue
        if explicit_lines and source_line not in explicit_lines[0]:
            continue
        for claim_id in range_claim_ids:
            if claim_id not in claim_ids:
                claim_ids.append(claim_id)
    return claim_ids


def _diff_marker(raw_text: str) -> str:
    stripped = raw_text.lstrip()
    if stripped.startswith("@@ "):
        return "hunk"
    if raw_text.startswith("+"):
        return "addition"
    if raw_text.startswith("-"):
        return "deletion"
    if raw_text.startswith(" "):
        return "context"
    return "none"


def _claim_ref_records(
    claim_ids: list[str],
    claim_paths: dict[str, str],
) -> list[dict[str, Any]]:
    return [
        {
            "inventory_path": claim_paths.get(claim_id),
            "claim_id": claim_id,
            "resolved": claim_id in claim_paths,
        }
        for claim_id in claim_ids
    ]


def _named_span_ref(span_id: str, named_span_ids: set[str]) -> dict[str, Any]:
    return {
        "inventory_path": _SOURCE_INVENTORY_PATH,
        "span_id": span_id,
        "resolved": span_id in named_span_ids,
    }


def _reference_ids(
    root: Path,
) -> tuple[dict[str, str], set[str], list[str]]:
    claim_paths: dict[str, str] = {}
    errors: list[str] = []
    for relative_path in _CLAIM_INVENTORY_PATHS:
        data = _read_json_object(root / relative_path)
        if data is None:
            errors.append(f"missing_or_invalid_reference_inventory:{relative_path}")
            continue
        records = data.get("requirement_records") or data.get("claim_records")
        if not isinstance(records, list):
            errors.append(f"missing_reference_records:{relative_path}")
            continue
        for record in records:
            if not isinstance(record, dict):
                continue
            claim_id = record.get("requirement_id") or record.get("claim_id")
            if not isinstance(claim_id, str):
                continue
            if claim_id in claim_paths and claim_paths[claim_id] != relative_path:
                errors.append(f"duplicate_claim_id:{claim_id}")
            claim_paths[claim_id] = relative_path
    source_inventory = _read_json_object(root / _SOURCE_INVENTORY_PATH)
    named_span_ids: set[str] = set()
    if source_inventory is None:
        errors.append(
            f"missing_or_invalid_reference_inventory:{_SOURCE_INVENTORY_PATH}"
        )
    else:
        records = source_inventory.get("span_records")
        if isinstance(records, list):
            named_span_ids = {
                record["span_id"]
                for record in records
                if isinstance(record, dict) and isinstance(record.get("span_id"), str)
            }
        else:
            errors.append(f"missing_reference_records:{_SOURCE_INVENTORY_PATH}")
    return claim_paths, named_span_ids, errors


def _read_json_object(path: Path) -> dict[str, Any] | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _todo_ref(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = root / spec["path"]
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        text = ""
    return {
        **spec,
        "exists": path.is_file(),
        "required_phrase_present": spec["required_phrase"] in text,
    }


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _column_number(text: str, offset: int) -> int:
    return offset - text.rfind("\n", 0, offset)


def _load_boundary(
    boundary: object,
) -> tuple[object, list[AlphaEvolveTexCodeListingInventoryBoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            boundary = boundary.read_text(encoding="utf-8")
        except OSError as exc:
            return None, [_issue("boundary_read_error", str(exc))]
    if isinstance(boundary, str):
        try:
            boundary = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("boundary_json_error", str(exc))]
    if not isinstance(boundary, dict):
        return None, [_issue("invalid_boundary_type", "boundary must be a JSON object")]
    return boundary, []


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveTexCodeListingInventoryBoundaryIssue:
    return AlphaEvolveTexCodeListingInventoryBoundaryIssue(code, message)
