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


ALPHAEVOLVE_HARDWARE_CLAIM_INVENTORY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_hardware_claim_inventory_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "section_3_3_3_claim_inventory_complete_without_executable_rtl_fixture_"
    "or_hardware_result_reproduction"
)
EXPECTED_CLAIM_COUNT = 35
IMPLEMENTED_STATUS = "implemented_local"
INCOMPLETE_STATUSES = frozenset(
    {"partially_implemented", "not_implemented", "not_demonstrated"}
)


_TODO_SPECS = {
    "fixture": (
        "docs/todo/code.md",
        "Add an executable Verilog/RTL optimization benchmark contract.",
    ),
    "workflow": (
        "docs/todo/code.md",
        "Add an RTL optimization workflow-baseline evidence contract.",
    ),
    "rtl_evidence": (
        "docs/todo/code.md",
        "Add RTL/EDA verification provenance for hardware-circuit optimization.",
    ),
    "rewrite": (
        "docs/todo/code.md",
        "Add TPU arithmetic-circuit rewrite artifact provenance.",
    ),
    "contribution": (
        "docs/todo/code.md",
        "Add Gemini-to-TPU self-contribution provenance for hardware results.",
    ),
}


def _claim(
    claim_id: str,
    source_anchor: str,
    claim: str,
    category: str,
    implementation_status: str,
    evidence_paths: tuple[str, ...],
    todo_ids: tuple[str, ...],
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "source_span_id": "section_3_3_3",
        "source_page": 16,
        "source_anchor": source_anchor,
        "claim": claim,
        "category": category,
        "implementation_status": implementation_status,
        "roadmap_section_id": "representative_benchmarks",
        "roadmap_phase": "longer_term",
        "evidence_paths": evidence_paths,
        "todo_ids": todo_ids,
    }


_WORKSPACE_EVIDENCE = (
    "libreevolve/problems/loader.py",
    "libreevolve/core/evaluator.py",
    "libreevolve/problems/examples/candidate_runner_c/config.yaml",
)
_HARDWARE_EVIDENCE = (
    "libreevolve/problems/benchmarks/systems_results.py",
    "papers/hardware_rtl_eda_evidence_boundary.json",
    "papers/systems_result_readiness_boundary.json",
)
_REWRITE_EVIDENCE = (
    "libreevolve/problems/benchmarks/systems_results.py",
    "papers/hardware_rewrite_artifact_boundary.json",
    "papers/hardware_rtl_eda_evidence_boundary.json",
)
_CONTRIBUTION_EVIDENCE = (
    "libreevolve/problems/benchmarks/systems_results.py",
    "papers/hardware_contribution_attribution_boundary.json",
    "papers/hardware_rtl_eda_evidence_boundary.json",
)
_WORKFLOW_EVIDENCE = (
    "libreevolve/problems/benchmarks/systems_results.py",
    "papers/hardware_rtl_eda_evidence_boundary.json",
)


HARDWARE_CLAIM_SPECS = (
    _claim(
        "specialized_hardware_tpu_example",
        "Specialized hardware, such as Google's Tensor Processing Units (TPUs)",
        "Represent TPUs as the paper's example of specialized AI hardware.",
        "hardware_design_context",
        "not_implemented",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence"),
    ),
    _claim(
        "specialized_hardware_resource_efficiency_at_scale",
        "crucial for achieving the resource efficiency required to run modern AI systems at scale",
        "Preserve the source claim that specialized hardware enables resource-efficient AI at scale without treating it as a local result.",
        "hardware_design_context",
        "not_demonstrated",
        _HARDWARE_EVIDENCE,
        ("fixture",),
    ),
    _claim(
        "chip_design_complexity",
        "designing new computer chips is a complex and time-consuming process",
        "Preserve chip-design complexity as source context rather than a locally measured outcome.",
        "hardware_workflow_context",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE,
        ("workflow",),
    ),
    _claim(
        "chip_design_often_spans_years",
        "often spanning years",
        "Keep the paper's years-scale chip-design statement contextual unless a matched local baseline exists.",
        "hardware_workflow_context",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE,
        ("workflow",),
    ),
    _claim(
        "rtl_optimization_critical_step",
        "Register-Transfer Level (RTL) optimization, a critical step in this process",
        "Provide an executable RTL-optimization stage rather than only hardware-report metadata.",
        "hardware_workflow_context",
        "not_implemented",
        _WORKSPACE_EVIDENCE + _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence"),
    ),
    _claim(
        "rtl_manual_hardware_description_rewriting",
        "involves manually rewriting hardware descriptions",
        "Represent the manual hardware-description rewrite baseline and compare it with evolved source edits.",
        "hardware_workflow_context",
        "partially_implemented",
        _WORKSPACE_EVIDENCE + _WORKFLOW_EVIDENCE,
        ("fixture", "workflow"),
    ),
    _claim(
        "rtl_power_metric",
        "improve metrics like power, performance, and area",
        "Evaluate power as a declared RTL optimization metric with artifact-backed provenance.",
        "hardware_workflow_context",
        "partially_implemented",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence", "workflow"),
    ),
    _claim(
        "rtl_performance_metric",
        "improve metrics like power, performance, and area",
        "Evaluate performance or timing as a declared RTL optimization metric with artifact-backed provenance.",
        "hardware_workflow_context",
        "partially_implemented",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence", "workflow"),
    ),
    _claim(
        "rtl_area_metric",
        "improve metrics like power, performance, and area",
        "Evaluate area as a declared RTL optimization metric with artifact-backed provenance.",
        "hardware_workflow_context",
        "partially_implemented",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence", "workflow"),
    ),
    _claim(
        "rtl_manual_iteration_can_take_months",
        "demanding months of iteration",
        "Keep the months-of-iteration statement contextual until a source-backed or matched local workflow baseline exists.",
        "hardware_workflow_context",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE,
        ("workflow",),
    ),
    _claim(
        "rtl_requires_highly_skilled_engineers",
        "by highly skilled engineers",
        "Record the engineer-expertise assumption behind the manual RTL workflow baseline.",
        "hardware_workflow_context",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE,
        ("workflow",),
    ),
    _claim(
        "already_highly_optimized_verilog_target",
        "already highly optimized Verilog implementation",
        "Provide a baseline-supported Verilog target whose pre-evolution optimization state is documented.",
        "hardware_optimization_task",
        "not_implemented",
        _WORKSPACE_EVIDENCE + _REWRITE_EVIDENCE,
        ("fixture", "rewrite"),
    ),
    _claim(
        "key_tpu_arithmetic_circuit_target",
        "key TPU arithmetic circuit",
        "Identify and execute against a concrete arithmetic-circuit benchmark without presenting an open analogue as proprietary TPU RTL.",
        "hardware_optimization_task",
        "not_implemented",
        _HARDWARE_EVIDENCE + _REWRITE_EVIDENCE,
        ("fixture", "rtl_evidence", "rewrite"),
    ),
    _claim(
        "matrix_multiplication_unit_context",
        "within the matrix multiplication unit",
        "Record the arithmetic circuit's matrix-multiplication-unit context.",
        "hardware_optimization_task",
        "partially_implemented",
        _REWRITE_EVIDENCE,
        ("fixture", "rewrite"),
    ),
    _claim(
        "reduce_area_objective",
        "optimization objectives were to reduce both area and power consumption",
        "Represent area reduction as an optimization objective, not an achieved local or paper-quantified result.",
        "hardware_optimization_task",
        "partially_implemented",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence"),
    ),
    _claim(
        "reduce_power_objective",
        "optimization objectives were to reduce both area and power consumption",
        "Represent power reduction as an optimization objective, not an achieved local or paper-quantified result.",
        "hardware_optimization_task",
        "partially_implemented",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence"),
    ),
    _claim(
        "preserve_core_functionality_objective",
        "while preserving the component's core functionality",
        "Make preservation of the circuit's core function a mandatory candidate gate.",
        "hardware_optimization_task",
        "partially_implemented",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence"),
    ),
    _claim(
        "robust_verification_requirement",
        "final proposal must pass robust verification methods",
        "Require robust verification of the final RTL proposal without claiming the paper names a specific method.",
        "hardware_verification",
        "partially_implemented",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence"),
    ),
    _claim(
        "verification_confirms_functional_correctness",
        "confirm that the modified circuit maintains functional correctness",
        "Use verification to establish functional equivalence or correctness of each accepted circuit.",
        "hardware_verification",
        "partially_implemented",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence"),
    ),
    _claim(
        "simple_code_rewrite_discovered",
        "able to find a simple code rewrite",
        "Do not claim discovery of the paper's simple rewrite without source, candidate, and run artifacts.",
        "hardware_discovery_result",
        "not_demonstrated",
        _REWRITE_EVIDENCE,
        ("fixture", "rewrite"),
    ),
    _claim(
        "unnecessary_bits_removed",
        "removed unnecessary bits",
        "Do not claim unnecessary-bit removal without exact changed spans, signals, and semantic verification evidence.",
        "hardware_discovery_result",
        "not_demonstrated",
        _REWRITE_EVIDENCE,
        ("fixture", "rewrite"),
    ),
    _claim(
        "tpu_designer_correctness_validation",
        "validated by TPU designers for correctness",
        "Do not claim TPU-designer correctness validation without a real review and signoff artifact.",
        "hardware_discovery_result",
        "not_demonstrated",
        _HARDWARE_EVIDENCE + _CONTRIBUTION_EVIDENCE,
        ("rtl_evidence", "contribution"),
    ),
    _claim(
        "downstream_synthesis_independent_rediscovery",
        "independently caught by downstream synthesis tools",
        "Do not claim independent downstream-synthesis rediscovery without identified tool output and an audit linking the same change.",
        "hardware_discovery_result",
        "not_demonstrated",
        _HARDWARE_EVIDENCE + _CONTRIBUTION_EVIDENCE,
        ("fixture", "rtl_evidence", "contribution"),
    ),
    _claim(
        "refine_source_rtl_capability",
        "capability to refine source RTL",
        "Demonstrate source-RTL refinement through an executable HDL fixture rather than generic text mutation alone.",
        "hardware_design_flow",
        "partially_implemented",
        _WORKSPACE_EVIDENCE + _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence"),
    ),
    _claim(
        "early_design_flow_optimization_value",
        "provide optimizations early in the design flow",
        "Demonstrate that an evolved edit is useful at the RTL stage before downstream synthesis.",
        "hardware_design_flow",
        "not_demonstrated",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence", "workflow"),
    ),
    _claim(
        "integrated_into_upcoming_tpu",
        "Integrated into an upcoming TPU",
        "Do not claim upcoming-TPU integration without identified integration milestones and review evidence.",
        "hardware_deployment_and_attribution",
        "not_demonstrated",
        _CONTRIBUTION_EVIDENCE,
        ("rtl_evidence", "contribution"),
    ),
    _claim(
        "gemini_first_direct_tpu_arithmetic_contribution",
        "Gemini's first direct contribution to TPU arithmetic circuits",
        "Do not claim Gemini firstness or direct TPU contribution without scoped novelty and attribution evidence.",
        "hardware_deployment_and_attribution",
        "not_demonstrated",
        _CONTRIBUTION_EVIDENCE,
        ("contribution",),
    ),
    _claim(
        "alphaevolve_mediated_hardware_contribution",
        "achieved via AlphaEvolve",
        "Do not attribute a hardware contribution to an AlphaEvolve run without model, backend, run, edit, and review provenance.",
        "hardware_deployment_and_attribution",
        "not_demonstrated",
        _CONTRIBUTION_EVIDENCE,
        ("contribution",),
    ),
    _claim(
        "path_for_future_hardware_contributions",
        "paving the way for future contributions",
        "Keep future hardware contributions as a forward-looking paper statement, not a demonstrated LibreEvolve result.",
        "hardware_deployment_and_attribution",
        "not_demonstrated",
        _CONTRIBUTION_EVIDENCE,
        ("contribution",),
    ),
    _claim(
        "changes_communicated_directly_in_verilog",
        "communicates the suggested changes directly in Verilog",
        "Emit reviewable Verilog candidate edits as first-class workspace artifacts.",
        "hardware_adoption",
        "partially_implemented",
        _WORKSPACE_EVIDENCE + _REWRITE_EVIDENCE,
        ("fixture", "rewrite"),
    ),
    _claim(
        "verilog_standard_hardware_engineering_language",
        "standard language used by hardware engineers",
        "Preserve the paper's Verilog adoption context and identify the HDL used by any local fixture.",
        "hardware_adoption",
        "not_demonstrated",
        _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence"),
    ),
    _claim(
        "direct_verilog_fosters_trust",
        "fostering trust",
        "Do not claim hardware-engineer trust from direct Verilog output without review or user evidence.",
        "hardware_adoption",
        "not_demonstrated",
        _HARDWARE_EVIDENCE,
        ("rtl_evidence", "workflow"),
    ),
    _claim(
        "direct_verilog_simplifies_adoption",
        "simplifying adoption",
        "Do not claim simplified adoption without an identified hardware-review and integration workflow.",
        "hardware_adoption",
        "not_demonstrated",
        _HARDWARE_EVIDENCE + _CONTRIBUTION_EVIDENCE,
        ("rtl_evidence", "contribution", "workflow"),
    ),
    _claim(
        "llm_code_evolution_assists_hardware_design",
        "LLM-powered code evolution assists in hardware design",
        "Demonstrate LLM-guided RTL evolution on an executable hardware-design task before claiming this capability locally.",
        "hardware_adoption",
        "not_demonstrated",
        _WORKSPACE_EVIDENCE + _HARDWARE_EVIDENCE,
        ("fixture", "rtl_evidence"),
    ),
    _claim(
        "potential_time_to_market_reduction",
        "potentially reducing time to market",
        "Keep time-to-market reduction explicitly potential unless matched workflow and deployment evidence exists.",
        "hardware_adoption",
        "not_demonstrated",
        _WORKFLOW_EVIDENCE + _CONTRIBUTION_EVIDENCE,
        ("workflow", "rtl_evidence", "contribution"),
    ),
)

EXPECTED_CLAIM_IDS = tuple(spec["claim_id"] for spec in HARDWARE_CLAIM_SPECS)


@dataclass(frozen=True)
class AlphaEvolveHardwareClaimInventoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveHardwareClaimInventoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_count: int
    implemented_local_count: int
    implementation_gap_count: int
    missing_anchor_count: int
    missing_reference_count: int
    issues: list[AlphaEvolveHardwareClaimInventoryBoundaryIssue]


def alphaevolve_hardware_claim_inventory_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the Section 3.3.3 hardware claim-level implementation audit."""

    root_path = Path(root)
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    page_texts = _source_page_texts(root_path)
    records = [
        _claim_record(root_path, spec, page_texts) for spec in HARDWARE_CLAIM_SPECS
    ]
    category_counts = Counter(record["category"] for record in records)
    status_counts = Counter(record["implementation_status"] for record in records)
    missing_anchor_count = sum(
        1 for record in records if not record["source_anchor_present"]
    )
    missing_reference_count = sum(
        1
        for record in records
        for ref in record["evidence_refs"]
        if not ref["exists"]
    ) + sum(
        1
        for record in records
        for ref in record["active_todo_refs"]
        if not ref["exists"] or not ref["required_phrase_present"]
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
        "schema": ALPHAEVOLVE_HARDWARE_CLAIM_INVENTORY_BOUNDARY_SCHEMA,
        "source_paper_id": SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "hardware_claim_inventory_ready": inventory_ready,
        "alphaevolve_hardware_result_reproduction_claim_ready": False,
        "alphaevolve_parity_claim_ready": False,
        "source_artifact": source_artifact,
        "source_inventory_schema": source_inventory["schema"],
        "source_inventory_span_count": source_inventory["span_count"],
        "source_span_ids": ["section_3_3_3"],
        "inventory_scope": {
            "included": [
                "all substantive Section 3.3.3 hardware-design context, RTL workflow, optimization-task, verification, rewrite-result, design-flow, deployment, attribution, adoption, and time-to-market claims",
                "source-fidelity distinctions between optimization objectives and achieved outcomes, between required robust verification and a named or reproduced method, and between potential and demonstrated impact",
            ],
            "excluded": [
                "Section 3.3.4 through Section 5 and Figures 8 through 14",
                "Table 3, detailed appendices, citations, and bibliography details",
                "a proprietary TPU circuit, executable open Verilog analogue, HDL simulator, synthesis or PPA toolchain, formal-equivalence lane, designer signoff, or chip-integration record",
                "independent reproduction of the unnecessary-bit rewrite, TPU integration, Gemini first-direct-contribution attribution, adoption, trust, or time-to-market statements",
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
            "This sidecar certifies a bounded claim-level inventory of 35 "
            "AlphaEvolve hardware-circuit-design claims from Section 3.3.3. "
            "Status labels distinguish generic text-workspace, candidate-runner, "
            "and hardware-report schema support from absent executable Verilog/RTL "
            "behavior and undemonstrated paper outcomes. It does not claim a TPU "
            "circuit or open RTL fixture, HDL simulation, synthesis/PPA, robust or "
            "formal verification results, the unnecessary-bit rewrite, designer "
            "validation, downstream-synthesis rediscovery, upcoming-TPU integration, "
            "Gemini attribution, trust/adoption impact, time-to-market improvement, "
            "production scale, or AlphaEvolve system parity."
        ),
    }


def validate_alphaevolve_hardware_claim_inventory_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> AlphaEvolveHardwareClaimInventoryBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_hardware_claim_inventory_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveHardwareClaimInventoryBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = alphaevolve_hardware_claim_inventory_boundary_record(root)
    issues: list[AlphaEvolveHardwareClaimInventoryBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_HARDWARE_CLAIM_INVENTORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported hardware claim inventory schema"))
    if data.get("source_paper_id") != SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    if data.get("alphaevolve_hardware_result_reproduction_claim_ready") is not False:
        issues.append(
            _issue(
                "result_reproduction_overclaim",
                "hardware inventory must not claim result reproduction",
            )
        )
    if data.get("alphaevolve_parity_claim_ready") is not False:
        issues.append(
            _issue(
                "parity_overclaim",
                "hardware inventory must not claim AlphaEvolve parity",
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
                    f"{key} drifted from the bounded hardware claim inventory",
                )
            )
    if len(EXPECTED_CLAIM_IDS) != EXPECTED_CLAIM_COUNT:
        issues.append(_issue("invalid_spec_count", "hardware claim count must remain 35"))
    if len(set(EXPECTED_CLAIM_IDS)) != len(EXPECTED_CLAIM_IDS):
        issues.append(_issue("duplicate_claim_id", "hardware claim ids must be unique"))
    unknown_spans = sorted(
        {
            spec["source_span_id"]
            for spec in HARDWARE_CLAIM_SPECS
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
            for spec in HARDWARE_CLAIM_SPECS
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
                f"{expected['missing_anchor_count']} hardware claim anchors were not found",
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
    if data.get("hardware_claim_inventory_ready") is not expected_ready:
        issues.append(
            _issue(
                "invalid_hardware_claim_inventory_ready",
                "hardware_claim_inventory_ready does not match source, reference, and ownership checks",
            )
        )
    claim_boundary = data.get("claim_boundary")
    if (
        not isinstance(claim_boundary, str)
        or "35" not in claim_boundary
        or "Verilog/RTL behavior" not in claim_boundary
        or "synthesis/PPA" not in claim_boundary
        or "unnecessary-bit rewrite" not in claim_boundary
        or "upcoming-TPU integration" not in claim_boundary
        or "time-to-market improvement" not in claim_boundary
        or "AlphaEvolve system parity" not in claim_boundary
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must separate bounded hardware claims from RTL execution, result, deployment, impact, and parity proof",
            )
        )
    return AlphaEvolveHardwareClaimInventoryBoundaryValidation(
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


def render_alphaevolve_hardware_claim_inventory_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_hardware_claim_inventory_boundary(boundary)
    lines = [
        "AlphaEvolve hardware claim inventory boundary",
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
    list[AlphaEvolveHardwareClaimInventoryBoundaryIssue],
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
            "hardware claim inventory boundary must be a JSON object",
        )
    ]


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveHardwareClaimInventoryBoundaryIssue:
    return AlphaEvolveHardwareClaimInventoryBoundaryIssue(code, message)
