from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_source_span_disposition_boundary import (
    roadmap_source_span_disposition_boundary_record,
)


ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_source_span_coverage_boundary.v5"
)
EXPECTED_BOUNDARY_STATUS = (
    "named_structure_plus_299_bounded_claims_without_whole_paper_claim_walk"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "coverage_surface_records",
    "named_source_inventory_input",
    "named_source_span_disposition_input",
    "paper_status_row_count",
    "claim_level_requirement_inventory",
    "application_result_claim_matrix",
    "status_row_to_roadmap_disposition_map",
    "missing_partial_todo_proof",
    "non_goal_decision_map",
    "phase_priority_map",
    "ci_source_span_exhaustiveness_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "claim_level_requirement_inventory": "299_bounded_claims_remaining_sections_3_3_3_to_5_and_remaining_exhibits_appendices_not_recorded",
    "application_result_claim_matrix": "not_recorded_locally",
    "status_row_to_roadmap_disposition_map": "not_recorded_locally",
    "missing_partial_todo_proof": "not_recorded_locally",
    "non_goal_decision_map": "not_recorded_locally",
    "phase_priority_map": "not_recorded_locally",
    "ci_source_span_exhaustiveness_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


COVERAGE_SURFACE_SPECS = (
    {
        "surface_id": "main_text_section_walk",
        "source_surface": "AlphaEvolve main-text sections and requirement claims",
        "current_scope": "PDF-verified named main-text sections plus 50 Table 1/Section 2 system requirements, 41 Abstract/Introduction/Discussion/collaborator claims, 41 Section 3.1/Table 2/Figure 4 matrix-result claims, 63 Section 3.2/Figure 5 constructive-math claims, 45 Section 3.3 opening/Section 3.3.1/Figure 6 scheduling claims, and 59 Section 3.3.2/Figure 7 kernel-engineering claims with implementation and TODO disposition",
        "missing_readiness": "claim-level extraction for Sections 3.3.3-5, remaining exhibits, appendices, and source details with semantic implementation and TODO disposition",
        "sidecars": (
            "papers/roadmap_source_span_disposition_boundary.json",
            "papers/implementation_evidence_map_boundary.json",
            "papers/alphaevolve_system_requirement_inventory_boundary.json",
            "papers/alphaevolve_context_claim_inventory_boundary.json",
            "papers/alphaevolve_matrix_result_claim_inventory_boundary.json",
            "papers/alphaevolve_math_result_claim_inventory_boundary.json",
            "papers/alphaevolve_scheduling_claim_inventory_boundary.json",
            "papers/alphaevolve_kernel_claim_inventory_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "named sections, figures, tables, and",
            },
        ),
        "validation_gate": "section-level source-span disposition matrix",
        "readiness_status": "299_bounded_claims_complete_remaining_sections_3_3_3_to_5_and_exhibits_appendices_unmapped",
    },
    {
        "surface_id": "figure_exhibit_matrix",
        "source_surface": "AlphaEvolve figures and process/result exhibits",
        "current_scope": "all 14 numbered figure spans are page- and anchor-verified; Figures 1-3 have claim-level system requirements, Figure 4 has claim-level matrix dispositions, Figure 5 has claim-level constructive-math dispositions, Figure 6 has claim-level scheduling dispositions, Figure 7 has claim-level kernel-engineering dispositions, and selected figures have specialized artifact boundaries",
        "missing_readiness": "Figure 4-7 reproduction evidence plus claim-level exhibit decomposition and reproduction evidence for Figures 8-14",
        "sidecars": (
            "papers/alphaevolve_system_requirement_inventory_boundary.json",
            "papers/process_exhibit_boundary.json",
            "papers/figure3_supervised_exhibit_boundary.json",
            "papers/figure6_scheduling_exhibit_boundary.json",
            "papers/figure7_pallas_tiling_exhibit_boundary.json",
            "papers/figure8_ablation_artifacts.json",
            "papers/figure4_matrix_discovery_artifacts.json",
            "papers/figure9_matrix_diff_artifacts.json",
            "papers/alphaevolve_math_result_claim_inventory_boundary.json",
            "papers/alphaevolve_scheduling_claim_inventory_boundary.json",
            "papers/alphaevolve_kernel_claim_inventory_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "figures",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "rendered diagram",
            },
        ),
        "validation_gate": "figure/table artifact disposition matrix",
        "readiness_status": "figures_1_7_bounded_claim_inventory_without_remaining_figure_reproduction",
    },
    {
        "surface_id": "table_capability_matrix",
        "source_surface": "AlphaEvolve tables and capability/result comparison claims",
        "current_scope": "all three numbered table spans are page- and anchor-verified; all eight Table 1 capability rows and all sixteen selected Table 2 rank rows have claim-level dispositions",
        "missing_readiness": "Table 2 result reproduction plus Table 3 row- and claim-level disposition with reproduction evidence",
        "sidecars": (
            "papers/alphaevolve_system_requirement_inventory_boundary.json",
            "papers/table1_capability_exhibit_boundary.json",
            "papers/matrix_rank_table_artifacts.json",
            "papers/matrix_suite_publication_artifacts.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "tables",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Table 1",
            },
        ),
        "validation_gate": "table row to ROADMAP/TODO disposition matrix",
        "readiness_status": "table_1_claim_inventory_complete_without_tables_2_3_reproduction",
    },
    {
        "surface_id": "appendix_a_matrix_targets",
        "source_surface": "Appendix A matrix-target registry and related artifacts",
        "current_scope": "Appendix A and its Figure 9/Table 3 spans are page- and anchor-verified alongside target identities and selected runtime artifacts",
        "missing_readiness": "all Appendix A result rows linked to implementation evidence and claim-level TODO proof",
        "sidecars": (
            "papers/appendix_a_matrix_curation.json",
            "papers/appendix_a_matrix_resource_frontier.json",
            "papers/appendix_a_matrix_row_note_artifacts.json",
            "papers/matrix_tensor_rank_runtime_boundary.json",
            "papers/matrix_cascade_run_runtime_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "appendix",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Appendix A",
            },
        ),
        "validation_gate": "Appendix A row-to-roadmap disposition matrix",
        "readiness_status": "named_appendix_a_complete_without_result_row_exhaustiveness",
    },
    {
        "surface_id": "appendix_b_constructive_math",
        "source_surface": "Appendix B constructive-math families and result claims",
        "current_scope": "Section 3.2 and Figure 5 have 63 claim-level dispositions; Appendix B, all 13 named subsections, and Figures 10-14 are page- and anchor-verified alongside bounded math boundaries",
        "missing_readiness": "Appendix B result claims linked to reproduction evidence, domain TODOs, and non-goal decisions",
        "sidecars": (
            "papers/math_outcome_boundary.json",
            "papers/math_starting_construction_boundary.json",
            "papers/math_heuristic_handoff_boundary.json",
            "papers/math_heuristic_stage_sequence_boundary.json",
            "papers/alphaevolve_math_result_claim_inventory_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "benchmark family",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Appendix B",
            },
        ),
        "validation_gate": "Appendix B family/result disposition matrix",
        "readiness_status": "named_appendix_b_complete_without_result_claim_exhaustiveness",
    },
    {
        "surface_id": "application_result_claims",
        "source_surface": "AlphaEvolve application-result claims for systems, kernels, hardware, and compiler work",
        "current_scope": "all named Section 3.3 application subsections and Figures 6-7 are page- and anchor-verified; the Section 3.3 opening, Section 3.3.1, and Figure 6 have 45 scheduling claim dispositions, and Section 3.3.2 and Figure 7 have 59 kernel-engineering claim dispositions alongside systems absence/readiness boundaries",
        "missing_readiness": "Section 3.3.3-3.3.4 application-result claim matrix with reproduction artifacts, phase priority, and domain TODO/non-goal proof",
        "sidecars": (
            "papers/systems_result_readiness_boundary.json",
            "papers/alphaevolve_scheduling_claim_inventory_boundary.json",
            "papers/alphaevolve_kernel_claim_inventory_boundary.json",
            "papers/compiler_stack_context_boundary.json",
            "papers/compiler_adoption_path_boundary.json",
            "papers/hardware_rtl_eda_evidence_boundary.json",
            "papers/hardware_rewrite_artifact_boundary.json",
            "papers/magellan_boundary.json",
            "papers/archagent_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "application-result claim",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Keep named AlphaEvolve application-context rows background-only",
            },
        ),
        "validation_gate": "application-result claim to ROADMAP/TODO disposition matrix",
        "readiness_status": "scheduling_and_kernel_claim_matrices_complete_without_remaining_application_claims",
    },
    {
        "surface_id": "paper_status_row_dispositions",
        "source_surface": "paper-index status rows and source-specific sidecars",
        "current_scope": "paper-index rows and structural status-claim inventory without complete ROADMAP disposition",
        "missing_readiness": "all paper/status sidecar rows mapped to ROADMAP dispositions or explicit non-goals",
        "sidecars": (
            "papers/status_claim_inventory.json",
            "papers/roadmap_source_span_disposition_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "paper/status sidecar rows",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "semantic evidence mapping for every paper-index status row",
            },
        ),
        "validation_gate": "paper-status row to ROADMAP disposition map",
        "readiness_status": "status_rows_not_exhaustively_roadmapped",
    },
    {
        "surface_id": "todo_non_goal_phase_proof",
        "source_surface": "missing/partial source spans, non-goals, and phase priority",
        "current_scope": "separate TODO, non-goal, and phase-sequence boundaries",
        "missing_readiness": "proof every missing/partial span has an active TODO, non-goal decision, and phase priority",
        "sidecars": (
            "papers/todo_canonical_gap_boundary.json",
            "papers/roadmap_non_goal_contradiction_boundary.json",
            "papers/roadmap_phase_sequence_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "domain-specific missing/partial TODO proof",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "phase-priority map",
            },
        ),
        "validation_gate": "missing/partial source-span TODO and phase proof",
        "readiness_status": "separate_boundaries_without_span_level_join",
    },
)


@dataclass(frozen=True)
class RoadmapSourceSpanCoverageBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapSourceSpanCoverageBoundaryValidation:
    ok: bool
    boundary_status: str | None
    coverage_surface_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapSourceSpanCoverageBoundaryIssue]


def roadmap_source_span_coverage_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP AlphaEvolve source-span coverage matrix."""

    root_path = Path(root)
    disposition = roadmap_source_span_disposition_boundary_record(root_path)
    records = [_coverage_surface_record(root_path, spec) for spec in COVERAGE_SURFACE_SPECS]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    return {
        "schema": ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "named_source_inventory_input": "papers/alphaevolve_source_inventory_boundary.json",
        "named_source_span_disposition_input": "papers/roadmap_source_span_disposition_boundary.json",
        "named_source_span_disposition_count": disposition["disposition_record_count"],
        "paper_status_row_count": disposition["paper_status_row_count"],
        "paper_status_row_dispositioned_count": disposition[
            "paper_status_row_dispositioned_count"
        ],
        "coverage_surface_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "coverage_surface_records": records,
        "completed_evidence": {
            "named_structure_span_count": disposition["disposition_record_count"],
            "named_structure_source_ref_count": disposition["disposition_source_ref_count"],
            "named_structure_scope": "38_structure_14_figure_3_table_spans",
            "section_2_system_requirement_count": 50,
            "section_2_system_requirement_scope": "table_1_sections_2_1_through_2_6_figures_1_through_3",
            "context_claim_count": 41,
            "context_claim_scope": "abstract_introduction_discussion_and_collaborator_context",
            "matrix_result_claim_count": 41,
            "matrix_result_claim_scope": "section_3_1_table_2_figure_4_and_footnote_3",
            "math_result_claim_count": 63,
            "math_result_claim_scope": "section_3_2_and_figure_5",
            "scheduling_claim_count": 45,
            "scheduling_claim_scope": "section_3_3_opening_section_3_3_1_and_figure_6",
            "kernel_claim_count": 59,
            "kernel_claim_scope": "section_3_3_2_and_figure_7",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a ROADMAP-level AlphaEvolve source-span "
            "coverage matrix for all 55 PDF-verified named main-text sections, "
            "figures, tables, Appendix A/B spans, and named application sections, "
            "plus 299 bounded claim-level records across Table 1, Section 2, "
            "the Abstract, Introduction, Discussion, collaborator context, "
            "Section 3.1, Table 2, Figure 4, footnote 3, Section 3.2, Figure 5, "
            "the Section 3.3 opening, Section 3.3.1, Figure 6, Section 3.3.2, and Figure 7, "
            "paper-status rows, and TODO/non-goal/phase proof. It does not "
            "claim whole-paper claim-level requirement exhaustiveness, a complete application-result claim matrix, "
            "status-row to ROADMAP disposition map, missing/partial TODO "
            "proof, non-goal decision map, phase-priority map, CI source-span "
            "exhaustiveness gate, or owner review signoff."
        ),
    }


def validate_roadmap_source_span_coverage_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapSourceSpanCoverageBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_source_span_coverage_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapSourceSpanCoverageBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = roadmap_source_span_coverage_boundary_record(root)
    issues: list[RoadmapSourceSpanCoverageBoundaryIssue] = []
    if data.get("schema") != ROADMAP_SOURCE_SPAN_COVERAGE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP source-span coverage boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP source-span coverage boundary must not claim exhaustive readiness"))
    for key in (
        "named_source_inventory_input",
        "named_source_span_disposition_input",
        "named_source_span_disposition_count",
        "paper_status_row_count",
        "paper_status_row_dispositioned_count",
        "coverage_surface_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "coverage_surface_records",
        "completed_evidence",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current source-span coverage inputs"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "all 55 PDF-verified named" not in boundary_text
        or "claim-level requirement exhaustiveness" not in boundary_text
        or "complete application-result claim matrix" not in boundary_text
        or "CI source-span exhaustiveness gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded coverage mapping from exhaustive source-span proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapSourceSpanCoverageBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        coverage_surface_count=data.get("coverage_surface_count") if isinstance(data.get("coverage_surface_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_source_span_coverage_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_source_span_coverage_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP source-span coverage boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| coverage_surface_count | {validation.coverage_surface_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _coverage_surface_record(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "surface_id": spec["surface_id"],
        "source_surface": spec["source_surface"],
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "sidecar_refs": [
            {"path": path, "exists": (root / path).exists()}
            for path in spec["sidecars"]
        ],
        "active_todo_refs": [_local_ref_record(root, todo_ref) for todo_ref in spec["active_todos"]],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _local_ref_record(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": spec["required_phrase"],
        "required_phrase_present": _contains_phrase(text, spec["required_phrase"]),
        "exists": (root / path).exists(),
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized_text = " ".join(text.casefold().split())
    normalized_phrase = " ".join(phrase.casefold().split())
    return normalized_phrase in normalized_text


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapSourceSpanCoverageBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP source-span coverage boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapSourceSpanCoverageBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_evidence_field", f"missing required evidence fields: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_evidence_field", f"unknown required evidence fields: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[RoadmapSourceSpanCoverageBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> RoadmapSourceSpanCoverageBoundaryIssue:
    return RoadmapSourceSpanCoverageBoundaryIssue(code=code, message=message)
