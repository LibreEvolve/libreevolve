from __future__ import annotations

import hashlib
import json
import unicodedata
from collections import Counter
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

from pypdf import PdfReader


ALPHAEVOLVE_SOURCE_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_source_inventory_boundary.v1"
)
SOURCE_PAPER_ID = "2506.13131"
SOURCE_PDF_PATH = "papers/2506.13131__AlphaEvolve.pdf"
EXPECTED_SOURCE_PDF_SHA256 = (
    "f092c8cbd65da89951ee6496374da9a54963f9035758c25ac6e4625f506df9ad"
)
EXPECTED_SOURCE_PDF_PAGE_COUNT = 44
EXPECTED_BOUNDARY_STATUS = (
    "complete_named_structure_inventory_without_claim_level_exhaustiveness"
)

_AUDIT_TODOS = (
    {
        "path": "docs/todo/code.md",
        "required_phrase": (
            "Add exhaustive implementation-evidence mapping for AlphaEvolve"
        ),
    },
    {
        "path": "docs/todo/roadmap.md",
        "required_phrase": (
            "Add ROADMAP AlphaEvolve source-span disposition coverage."
        ),
    },
)

_RELATED_WORK_TODOS = (
    {
        "path": "docs/todo/code.md",
        "required_phrase": (
            "Add AlphaEvolve Section 5 Related Work taxonomy and positioning evidence."
        ),
    },
    {
        "path": "docs/todo/papers.md",
        "required_phrase": (
            "Track AlphaEvolve Section 5 Related Work taxonomy and positioning evidence."
        ),
    },
)

_DISPOSITIONS: dict[str, dict[str, Any]] = {
    "background": {
        "audit_surface": "paper_context",
        "local_status": "background_only",
        "roadmap_section_id": "documentation_truthfulness",
        "roadmap_phase": "near_term",
        "sidecars": ("papers/documentation_truthfulness_boundary.json",),
        "todos": (),
    },
    "context": {
        "audit_surface": "platform_method_scope_and_headline_results",
        "local_status": (
            "mixed_implemented_partial_missing_and_undemonstrated"
        ),
        "roadmap_section_id": "documentation_truthfulness",
        "roadmap_phase": "near_term",
        "sidecars": (
            "papers/alphaevolve_context_claim_inventory_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "platform": {
        "audit_surface": "platform_overview",
        "local_status": "partially_implemented",
        "roadmap_section_id": "documentation_truthfulness",
        "roadmap_phase": "near_term",
        "sidecars": (
            "papers/process_exhibit_boundary.json",
            "papers/table1_capability_exhibit_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "task": {
        "audit_surface": "task_specification",
        "local_status": "partially_implemented",
        "roadmap_section_id": "candidate_workspace_fidelity",
        "roadmap_phase": "near_term",
        "sidecars": (
            "papers/task_specification_boundary.json",
            "papers/candidate_language_runner_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "prompting": {
        "audit_surface": "prompt_sampling_and_generation",
        "local_status": "partially_implemented",
        "roadmap_section_id": "prompt_context_system",
        "roadmap_phase": "near_term",
        "sidecars": (
            "papers/prompt_section_packing_boundary.json",
            "papers/llm_role_scheduler_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "evaluation": {
        "audit_surface": "evaluation",
        "local_status": "partially_implemented",
        "roadmap_section_id": "evaluation_cascade",
        "roadmap_phase": "near_term",
        "sidecars": (
            "papers/evaluation_cascade_boundary.json",
            "papers/evaluator_oracle_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "evolution": {
        "audit_surface": "evolutionary_database",
        "local_status": "partially_implemented",
        "roadmap_section_id": "multi_objective_search",
        "roadmap_phase": "near_term",
        "sidecars": (
            "papers/evolutionary_database_boundary.json",
            "papers/map_elites_descriptor_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "distributed": {
        "audit_surface": "distributed_pipeline",
        "local_status": "partially_implemented",
        "roadmap_section_id": "async_resumable_runtime",
        "roadmap_phase": "mid_term",
        "sidecars": (
            "papers/distributed_pipeline_topology_boundary.json",
            "papers/parallel_evaluation_readiness_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "matrix": {
        "audit_surface": "matrix_result_reproduction",
        "local_status": "missing_result_reproduction",
        "roadmap_section_id": "representative_benchmarks",
        "roadmap_phase": "longer_term",
        "sidecars": (
            "papers/matrix_suite_publication_artifacts.json",
            "papers/appendix_a_matrix_curation.json",
            "papers/alphaevolve_matrix_result_claim_inventory_boundary.json",
            "papers/alphaevolve_appendix_a_claim_inventory_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "math": {
        "audit_surface": "constructive_math_result_reproduction",
        "local_status": "missing_result_reproduction",
        "roadmap_section_id": "representative_benchmarks",
        "roadmap_phase": "longer_term",
        "sidecars": (
            "libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",
            "papers/math_outcome_boundary.json",
            "papers/alphaevolve_math_result_claim_inventory_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "systems": {
        "audit_surface": "systems_result_reproduction",
        "local_status": "missing_result_reproduction",
        "roadmap_section_id": "representative_benchmarks",
        "roadmap_phase": "longer_term",
        "sidecars": (
            "papers/systems_result_readiness_boundary.json",
            "papers/alphaevolve_scheduling_claim_inventory_boundary.json",
            "papers/alphaevolve_kernel_claim_inventory_boundary.json",
            "papers/alphaevolve_hardware_claim_inventory_boundary.json",
            "papers/alphaevolve_compiler_claim_inventory_boundary.json",
            "papers/hardware_rtl_eda_evidence_boundary.json",
            "papers/compiler_adoption_path_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "ablation": {
        "audit_surface": "ablation_result_reproduction",
        "local_status": "missing_result_reproduction",
        "roadmap_section_id": "representative_benchmarks",
        "roadmap_phase": "longer_term",
        "sidecars": (
            "papers/figure8_ablation_artifacts.json",
            "papers/alphaevolve_ablation_claim_inventory_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "related_work": {
        "audit_surface": "related_work_context_and_positioning",
        "local_status": (
            "mixed_implemented_partial_missing_undemonstrated_and_background_context"
        ),
        "roadmap_section_id": "related_work_positioning",
        "roadmap_phase": "near_term",
        "sidecars": (
            "papers/related_work_taxonomy_boundary.json",
            "papers/alphaevolve_related_work_claim_inventory_boundary.json",
        ),
        "todos": _RELATED_WORK_TODOS,
    },
    "discussion": {
        "audit_surface": "capability_self_improvement_and_limitations",
        "local_status": (
            "mixed_implemented_partial_missing_and_undemonstrated"
        ),
        "roadmap_section_id": "documentation_truthfulness",
        "roadmap_phase": "near_term",
        "sidecars": (
            "papers/alphaevolve_context_claim_inventory_boundary.json",
            "papers/self_improvement_distillation_boundary.json",
        ),
        "todos": _AUDIT_TODOS,
    },
    "provenance": {
        "audit_surface": "source_provenance",
        "local_status": "source_provenance_only",
        "roadmap_section_id": "documentation_truthfulness",
        "roadmap_phase": "near_term",
        "sidecars": (
            "papers/paper_author_metadata_boundary.json",
            "papers/system_contribution_provenance_boundary.json",
        ),
        "todos": (),
    },
}


def _span(
    span_id: str,
    source_kind: str,
    source_label: str,
    page_start: int,
    page_end: int,
    disposition_id: str,
    *anchors: tuple[int, str],
) -> dict[str, Any]:
    return {
        "span_id": span_id,
        "source_kind": source_kind,
        "source_label": source_label,
        "page_start": page_start,
        "page_end": page_end,
        "disposition_id": disposition_id,
        "anchors": anchors,
    }


NAMED_SOURCE_SPAN_SPECS = (
    _span(
        "abstract",
        "structure",
        "Abstract",
        1,
        1,
        "context",
        (1, "In this white paper, we present AlphaEvolve"),
    ),
    _span("section_1", "structure", "1. Introduction", 1, 3, "context", (1, "1. Introduction")),
    _span("section_2", "structure", "2. AlphaEvolve", 3, 4, "platform", (3, "2. AlphaEvolve")),
    _span("section_2_1", "structure", "2.1. Task specification", 3, 5, "task", (3, "2.1. Task specification")),
    _span("section_2_2", "structure", "2.2. Prompt sampling", 5, 5, "prompting", (5, "2.2. Prompt sampling")),
    _span("section_2_3", "structure", "2.3. Creative generation", 5, 7, "prompting", (5, "2.3. Creative generation")),
    _span("section_2_4", "structure", "2.4. Evaluation", 7, 8, "evaluation", (7, "2.4. Evaluation")),
    _span("section_2_5", "structure", "2.5. Evolution", 8, 8, "evolution", (8, "2.5. Evolution")),
    _span("section_2_6", "structure", "2.6. Distributed pipeline", 8, 8, "distributed", (8, "2.6. Distributed pipeline")),
    _span("section_3", "structure", "3. Results", 9, 17, "matrix", (9, "3. Results")),
    _span(
        "section_3_1",
        "structure",
        "3.1. Faster matrix multiplication via finding novel algorithms for tensor decomposition",
        9,
        10,
        "matrix",
        (9, "3.1. Faster matrix multiplication via finding novel algorithms for tensor decomposition"),
    ),
    _span(
        "section_3_2",
        "structure",
        "3.2. Finding tailored search algorithms for a wide range of open mathematical problems",
        10,
        13,
        "math",
        (10, "3.2. Finding tailored search algorithms for a wide range of open mathematical problems"),
    ),
    _span(
        "section_3_3",
        "structure",
        "3.3. Optimizing Google's computing ecosystem",
        13,
        17,
        "systems",
        (13, "3.3. Optimizing Google's computing ecosystem"),
    ),
    _span(
        "section_3_3_1",
        "structure",
        "3.3.1. Improving data center scheduling",
        13,
        15,
        "systems",
        (13, "3.3.1. Improving data center scheduling"),
    ),
    _span(
        "section_3_3_2",
        "structure",
        "3.3.2. Enhancing Gemini kernel engineering",
        15,
        16,
        "systems",
        (15, "3.3.2. Enhancing Gemini kernel engineering"),
    ),
    _span(
        "section_3_3_3",
        "structure",
        "3.3.3. Assisting in hardware circuit design",
        16,
        17,
        "systems",
        (16, "3.3.3. Assisting in hardware circuit design"),
    ),
    _span(
        "section_3_3_4",
        "structure",
        "3.3.4. Directly optimizing compiler-generated code",
        17,
        17,
        "systems",
        (17, "3.3.4. Directly optimizing compiler-generated code"),
    ),
    _span("section_4", "structure", "4. Ablations", 17, 18, "ablation", (17, "4. Ablations")),
    _span("section_5", "structure", "5. Related work", 18, 20, "related_work", (18, "5. Related work")),
    _span("section_6", "structure", "6. Discussion", 21, 21, "discussion", (21, "6. Discussion")),
    _span("acknowledgements", "structure", "Acknowledgements", 21, 22, "provenance", (21, "Acknowledgements")),
    _span("author_information", "structure", "Author information", 22, 23, "provenance", (22, "Author information")),
    _span("references", "structure", "References", 23, 33, "provenance", (23, "References")),
    _span(
        "appendix_a",
        "structure",
        "A. Faster matrix multiplication: Full results",
        34,
        37,
        "matrix",
        (34, "A. Faster matrix multiplication: Full results"),
    ),
    _span(
        "appendix_b",
        "structure",
        "B. Details of mathematical discoveries of AlphaEvolve",
        38,
        44,
        "math",
        (38, "B. Details of mathematical discoveries of AlphaEvolve"),
    ),
    _span("appendix_b_1", "structure", "B.1. First autocorrelation inequality", 38, 38, "math", (38, "B.1. First autocorrelation inequality")),
    _span("appendix_b_2", "structure", "B.2. Second autocorrelation inequality", 38, 38, "math", (38, "B.2. Second autocorrelation inequality")),
    _span("appendix_b_3", "structure", "B.3. Third autocorrelation inequality", 38, 38, "math", (38, "B.3. Third autocorrelation inequality")),
    _span("appendix_b_4", "structure", "B.4. An uncertainty inequality", 39, 39, "math", (39, "B.4. An uncertainty inequality")),
    _span("appendix_b_5", "structure", "B.5. Erdos' minimum overlap problem", 40, 40, "math", (40, "B.5. Erdos' minimum overlap problem")),
    _span("appendix_b_6", "structure", "B.6. Sums and differences of finite sets", 40, 41, "math", (40, "B.6. Sums and differences of finite sets")),
    _span("appendix_b_7", "structure", "B.7. Packing unit regular hexagons inside a regular hexagon", 41, 41, "math", (41, "B.7. Packing unit regular hexagons inside a regular hexagon")),
    _span("appendix_b_8", "structure", "B.8. Minimizing the ratio of maximum to minimum distance", 41, 41, "math", (41, "B.8. Minimizing the ratio of maximum to minimum distance")),
    _span("appendix_b_9", "structure", "B.9. The Heilbronn problem for triangles", 42, 42, "math", (42, "B.9. The Heilbronn problem for triangles")),
    _span("appendix_b_10", "structure", "B.10. The Heilbronn problem for convex regions", 42, 42, "math", (42, "B.10. The Heilbronn problem for convex regions")),
    _span("appendix_b_11", "structure", "B.11. Kissing number in dimension 11", 42, 43, "math", (42, "B.11. Kissing number in dimension 11")),
    _span("appendix_b_12", "structure", "B.12. Packing circles inside a unit square to maximize sum of radii", 43, 44, "math", (43, "B.12. Packing circles inside a unit square to maximize sum of radii")),
    _span("appendix_b_13", "structure", "B.13. Packing circles inside a rectangle of perimeter 4 to maximize sum of radii", 44, 44, "math", (44, "B.13. Packing circles inside a rectangle of perimeter 4 to maximize sum of radii")),
    _span("figure_1", "figure", "Figure 1", 3, 3, "platform", (3, "Figure 1 AlphaEvolve high-level overview")),
    _span("figure_2", "figure", "Figure 2", 4, 4, "distributed", (4, "Figure 2 Expanded view of the AlphaEvolve discovery process")),
    _span("figure_3", "figure", "Figure 3", 6, 6, "task", (6, "Figure 3 Illustrative example of applying AlphaEvolve")),
    _span("figure_4", "figure", "Figure 4", 11, 11, "matrix", (11, "Figure 4 Changes proposed by AlphaEvolve")),
    _span("figure_5", "figure", "Figure 5", 12, 12, "math", (12, "Figure 5 Examples of SOTA-breaking mathematical constructions")),
    _span("figure_6", "figure", "Figure 6", 14, 14, "systems", (14, "Figure 6 Left The heuristic function discovered by AlphaEvolve")),
    _span("figure_7", "figure", "Figure 7", 15, 15, "systems", (15, "Figure 7 Visualization of the tiling heuristic problem")),
    _span("figure_8", "figure", "Figure 8", 18, 18, "ablation", (18, "Figure 8 Left Ablations of AlphaEvolve")),
    _span(
        "figure_9",
        "figure",
        "Figure 9 (parts a-c)",
        35,
        37,
        "matrix",
        (35, "Figure 9a Magnified version of Figure 4"),
        (36, "Figure 9b Magnified version of Figure 4"),
        (37, "Figure 9c Magnified version of Figure 4"),
    ),
    _span("figure_10", "figure", "Figure 10", 40, 40, "math", (40, "Figure 10 Construction found by AlphaEvolve")),
    _span("figure_11", "figure", "Figure 11", 41, 41, "math", (41, "Figure 11 Constructions of the packing problems")),
    _span("figure_12", "figure", "Figure 12", 42, 42, "math", (42, "Figure 12 Left 16 points in 2 dimensions")),
    _span("figure_13", "figure", "Figure 13", 43, 43, "math", (43, "Figure 13 New constructions found by AlphaEvolve")),
    _span("figure_14", "figure", "Figure 14", 44, 44, "math", (44, "Figure 14 New constructions found by AlphaEvolve")),
    _span("table_1", "table", "Table 1", 2, 2, "platform", (2, "Table 1 Capabilities and typical behaviours of AlphaEvolve")),
    _span("table_2", "table", "Table 2", 9, 9, "matrix", (9, "Table 2 Upper bounds on the rank of the tensor")),
    _span("table_3", "table", "Table 3", 34, 34, "matrix", (34, "Table 3 Full version of Table 2")),
)

EXPECTED_NAMED_SOURCE_SPAN_IDS = tuple(
    spec["span_id"] for spec in NAMED_SOURCE_SPAN_SPECS
)


@dataclass(frozen=True)
class AlphaEvolveSourceInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveSourceInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    span_count: int
    anchor_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveSourceInventoryBoundaryIssue]


def alphaevolve_source_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Build the named-structure inventory from the retained AlphaEvolve PDF."""

    root_path = Path(root)
    source_artifact, page_texts = _source_artifact(root_path)
    records = [_span_record(root_path, spec, page_texts) for spec in NAMED_SOURCE_SPAN_SPECS]
    kind_counts = Counter(record["source_kind"] for record in records)
    status_counts = Counter(record["local_status"] for record in records)
    anchor_count = sum(len(record["anchor_checks"]) for record in records)
    missing_anchor_count = sum(
        1
        for record in records
        for anchor in record["anchor_checks"]
        if not anchor["present"]
    )
    missing_reference_count = sum(
        1
        for record in records
        for ref in (*record["sidecar_refs"], *record["active_todo_refs"])
        if not ref["exists"]
        or ("required_phrase_present" in ref and not ref["required_phrase_present"])
    )
    return {
        "schema": ALPHAEVOLVE_SOURCE_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "named_structure_inventory_ready": (
            source_artifact["identity_ok"]
            and missing_anchor_count == 0
            and missing_reference_count == 0
            and len(records) == len(EXPECTED_NAMED_SOURCE_SPAN_IDS)
        ),
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "inventory_scope": {
            "included": [
                "abstract and named main-text sections and subsections",
                "acknowledgements, author information, and references",
                "named appendices and Appendix B subsections",
                "numbered figures, treating Figure 9 parts a-c as one figure span",
                "numbered tables",
            ],
            "excluded": [
                "sentence, paragraph, equation, footnote, and citation-level requirements",
                "semantic decomposition of every capability or result claim",
                "proof that local implementations reproduce AlphaEvolve behavior or results",
            ],
        },
        "span_count": len(records),
        "expected_span_count": len(EXPECTED_NAMED_SOURCE_SPAN_IDS),
        "source_kind_counts": dict(sorted(kind_counts.items())),
        "local_status_counts": dict(sorted(status_counts.items())),
        "anchor_count": anchor_count,
        "missing_anchor_count": missing_anchor_count,
        "missing_reference_count": missing_reference_count,
        "span_records": records,
        "claim_boundary": (
            "This sidecar certifies a complete inventory of the retained PDF's "
            "named structural spans: abstract, sections, subsections, appendices, "
            "figures, and tables. It does not claim sentence-, paragraph-, "
            "equation-, footnote-, citation-, or requirement-level exhaustiveness; "
            "semantic sufficiency of implementation dispositions; reproduction of "
            "AlphaEvolve results; or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_source_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveSourceInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_source_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveSourceInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_source_inventory_boundary_record(root)
    issues: list[AlphaEvolveSourceInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_SOURCE_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported source inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(_issue("parity_overclaim", "named source coverage must not claim AlphaEvolve parity"))
    for key in (
        "source_artifact",
        "inventory_scope",
        "span_count",
        "expected_span_count",
        "source_kind_counts",
        "local_status_counts",
        "anchor_count",
        "missing_anchor_count",
        "missing_reference_count",
        "span_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from the retained source inventory"))
    source_artifact = expected["source_artifact"]
    if not source_artifact["identity_ok"]:
        issues.append(_issue("source_pdf_identity_mismatch", "retained AlphaEvolve PDF identity or page count does not match the pinned source"))
    if expected["missing_anchor_count"]:
        issues.append(_issue("missing_source_anchor", f"{expected['missing_anchor_count']} declared source anchors were not found on their pinned pages"))
    if expected["missing_reference_count"]:
        issues.append(_issue("missing_local_reference", f"{expected['missing_reference_count']} sidecar or active TODO references are missing or stale"))
    expected_ready = (
        source_artifact["identity_ok"]
        and expected["missing_anchor_count"] == 0
        and expected["missing_reference_count"] == 0
    )
    if data.get("named_structure_inventory_ready") is not expected_ready:
        issues.append(_issue("invalid_named_structure_inventory_ready", "named_structure_inventory_ready does not match source and reference checks"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "named structural spans" not in boundary_text
        or "requirement-level exhaustiveness" not in boundary_text
        or "AlphaEvolve system parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must distinguish named structure coverage from requirement and parity proof"))
    return AlphaEvolveSourceInventoryBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        span_count=data.get("span_count") if isinstance(data.get("span_count"), int) else 0,
        anchor_count=data.get("anchor_count") if isinstance(data.get("anchor_count"), int) else 0,
        missing_anchor_count=expected["missing_anchor_count"],
        missing_reference_count=expected["missing_reference_count"],
        issues=issues,
    )


def render_alphaevolve_source_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_source_inventory_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve source inventory boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| span_count | {validation.span_count} |",
        f"| anchor_count | {validation.anchor_count} |",
        f"| missing_anchor_count | {validation.missing_anchor_count} |",
        f"| missing_reference_count | {validation.missing_reference_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _source_artifact(root: Path) -> tuple[dict[str, Any], list[str]]:
    path = root / SOURCE_PDF_PATH
    try:
        stat = path.stat()
    except Exception as exc:  # pragma: no cover - exact pypdf errors vary.
        return (
            {
                "path": SOURCE_PDF_PATH,
                "exists": _safe_is_file(path),
                "expected_sha256": EXPECTED_SOURCE_PDF_SHA256,
                "actual_sha256": None,
                "expected_page_count": EXPECTED_SOURCE_PDF_PAGE_COUNT,
                "page_count": 0,
                "identity_ok": False,
                "error": type(exc).__name__,
            },
            [],
        )
    artifact, page_texts = _cached_source_artifact(
        str(path.resolve()),
        stat.st_mtime_ns,
        stat.st_size,
    )
    return dict(artifact), list(page_texts)


@lru_cache(maxsize=8)
def _cached_source_artifact(
    resolved_path: str,
    _mtime_ns: int,
    _size: int,
) -> tuple[dict[str, Any], tuple[str, ...]]:
    path = Path(resolved_path)
    try:
        payload = path.read_bytes()
        reader = PdfReader(path, strict=True)
        page_texts = tuple(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:  # pragma: no cover - exact pypdf errors vary.
        return (
            {
                "path": SOURCE_PDF_PATH,
                "exists": _safe_is_file(path),
                "expected_sha256": EXPECTED_SOURCE_PDF_SHA256,
                "actual_sha256": None,
                "expected_page_count": EXPECTED_SOURCE_PDF_PAGE_COUNT,
                "page_count": 0,
                "identity_ok": False,
                "error": type(exc).__name__,
            },
            (),
        )
    actual_sha256 = hashlib.sha256(payload).hexdigest()
    page_count = len(page_texts)
    return (
        {
            "path": SOURCE_PDF_PATH,
            "exists": True,
            "expected_sha256": EXPECTED_SOURCE_PDF_SHA256,
            "actual_sha256": actual_sha256,
            "expected_page_count": EXPECTED_SOURCE_PDF_PAGE_COUNT,
            "page_count": page_count,
            "identity_ok": (
                actual_sha256 == EXPECTED_SOURCE_PDF_SHA256
                and page_count == EXPECTED_SOURCE_PDF_PAGE_COUNT
            ),
            "error": None,
        },
        page_texts,
    )


def _span_record(
    root: Path,
    spec: dict[str, Any],
    page_texts: list[str],
) -> dict[str, Any]:
    disposition = _DISPOSITIONS[spec["disposition_id"]]
    anchor_checks = []
    for page_number, phrase in spec["anchors"]:
        page_text = page_texts[page_number - 1] if page_number <= len(page_texts) else ""
        anchor_checks.append(
            {
                "page": page_number,
                "phrase": phrase,
                "present": _canonical(phrase) in _canonical(page_text),
            }
        )
    sidecar_refs = [
        {"path": path, "exists": (root / path).is_file()}
        for path in disposition["sidecars"]
    ]
    active_todo_refs = []
    for todo in disposition["todos"]:
        path = root / todo["path"]
        text = _read_text(path)
        active_todo_refs.append(
            {
                "path": todo["path"],
                "required_phrase": todo["required_phrase"],
                "exists": path.is_file(),
                "required_phrase_present": todo["required_phrase"] in text,
            }
        )
    return {
        "span_id": spec["span_id"],
        "source_kind": spec["source_kind"],
        "source_label": spec["source_label"],
        "page_start": spec["page_start"],
        "page_end": spec["page_end"],
        "anchor_checks": anchor_checks,
        "all_anchors_present": all(check["present"] for check in anchor_checks),
        "audit_surface": disposition["audit_surface"],
        "local_status": disposition["local_status"],
        "roadmap_section_id": disposition["roadmap_section_id"],
        "roadmap_phase": disposition["roadmap_phase"],
        "sidecar_refs": sidecar_refs,
        "active_todo_refs": active_todo_refs,
    }


def _canonical(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value).casefold()
    return "".join(character for character in normalized if character.isalnum())


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _safe_is_file(path: Path) -> bool:
    try:
        return path.is_file()
    except OSError:
        return False


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveSourceInventoryBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "source inventory boundary must be a JSON object")]


def _issue(code: str, message: str) -> AlphaEvolveSourceInventoryBoundaryIssue:
    return AlphaEvolveSourceInventoryBoundaryIssue(code=code, message=message)
