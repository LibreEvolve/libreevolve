from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_source_span_coverage_boundary import (
    roadmap_source_span_coverage_boundary_record,
)


ROADMAP_SOURCE_SPAN_EXHAUSTIVENESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_source_span_exhaustiveness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "named_structure_exhaustiveness_gate_without_claim_level_walk"
)
SOURCE_COVERAGE_BOUNDARY_INPUT = "papers/roadmap_source_span_coverage_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "pdf_section_walk",
    "figure_table_appendix_matrix",
    "application_claim_matrix",
    "status_row_disposition_map",
    "missing_partial_todo_proof",
    "non_goal_decision_map",
    "phase_priority_map",
    "ci_exhaustiveness_and_owner_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "claim_level_requirement_inventory": "not_recorded_locally",
    "claim_level_figure_table_appendix_matrix": "not_recorded_locally",
    "application_result_claim_matrix": "not_recorded_locally",
    "status_row_to_roadmap_disposition_map": "not_recorded_locally",
    "missing_partial_domain_todo_proof": "not_recorded_locally",
    "non_goal_decision_map": "not_recorded_locally",
    "claim_level_phase_priority_map": "not_recorded_locally",
    "ci_source_span_exhaustiveness_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "pdf_section_walk",
        "source_surface": "retained AlphaEvolve source PDF sections and requirement spans",
        "current_scope": "all 38 named structural spans are page- and anchor-verified",
        "missing_exhaustiveness": "sentence-, paragraph-, and claim-level requirement extraction",
        "sidecars": (
            "papers/roadmap_source_span_coverage_boundary.json",
            "papers/roadmap_source_span_disposition_boundary.json",
        ),
        "active_todos": (
            {"path": "docs/todo/roadmap.md", "required_phrase": "claim-level requirement and figure/table/appendix"},
            {"path": "docs/todo/roadmap.md", "required_phrase": "every relevant AlphaEvolve source span"},
        ),
        "validation_gate": "retained PDF section-walk exhaustiveness gate",
        "readiness_status": "named_structure_walk_complete_without_claim_level_requirements",
    },
    {
        "criterion_id": "figure_table_appendix_matrix",
        "source_surface": "figures, tables, appendices, benchmark families, and appendix rows",
        "current_scope": "all 14 figures, 3 tables, 2 appendices, and 13 Appendix B subsections have named-span dispositions",
        "missing_exhaustiveness": "claim- and result-row-level exhibit matrix with reproduction evidence",
        "sidecars": (
            "papers/roadmap_source_span_coverage_boundary.json",
            "papers/implementation_evidence_map_boundary.json",
        ),
        "active_todos": (
            {"path": "docs/todo/roadmap.md", "required_phrase": "figure/table/appendix matrix"},
            {"path": "docs/todo/roadmap.md", "required_phrase": "benchmark family"},
        ),
        "validation_gate": "figure/table/appendix joined matrix gate",
        "readiness_status": "named_exhibit_matrix_complete_without_claim_level_rows",
    },
    {
        "criterion_id": "application_claim_matrix",
        "source_surface": "AlphaEvolve application-result claims and named application contexts",
        "current_scope": "application-context sidecars without complete claim-to-roadmap matrix",
        "missing_exhaustiveness": "application-result claim matrix with implementation/non-goal disposition",
        "sidecars": (
            "papers/roadmap_source_span_coverage_boundary.json",
            "papers/status_claim_inventory.json",
        ),
        "active_todos": (
            {"path": "docs/todo/roadmap.md", "required_phrase": "application-result claim matrix"},
            {"path": "docs/todo/roadmap.md", "required_phrase": "application-result claim"},
        ),
        "validation_gate": "application claim disposition matrix gate",
        "readiness_status": "application_context_rows_without_complete_claim_matrix",
    },
    {
        "criterion_id": "status_row_disposition_map",
        "source_surface": "paper-index status rows and paper/status sidecar rows",
        "current_scope": "53 paper-index rows with only the AlphaEvolve source row dispositioned",
        "missing_exhaustiveness": "status-row to ROADMAP disposition map for all paper/status sidecar rows",
        "sidecars": (
            "papers/status_claim_inventory.json",
            "papers/roadmap_source_span_disposition_boundary.json",
        ),
        "active_todos": (
            {"path": "docs/todo/roadmap.md", "required_phrase": "status-row to ROADMAP disposition map"},
            {"path": "docs/todo/roadmap.md", "required_phrase": "all paper/status sidecar rows"},
        ),
        "validation_gate": "paper status-row disposition exhaustiveness gate",
        "readiness_status": "one_status_row_dispositioned",
    },
    {
        "criterion_id": "span_status_classification",
        "source_surface": "source-span status labels across implementation, missing, partial, background-only, and non-goal states",
        "current_scope": "all 55 named spans have local status, ROADMAP section, and phase classifications",
        "missing_exhaustiveness": "semantic claim-level status classification and explicit non-goal decisions",
        "sidecars": (
            "papers/documentation_claim_inventory.json",
            "papers/roadmap_non_goal_contradiction_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "local status classes",
            },
            {"path": "docs/todo/roadmap.md", "required_phrase": "non-goal decision map"},
        ),
        "validation_gate": "per-span status classification gate",
        "readiness_status": "named_span_status_registry_complete_without_claim_level_semantics",
    },
    {
        "criterion_id": "missing_partial_todo_proof",
        "source_surface": "missing and partial source spans linked to code, README, roadmap, or papers TODOs",
        "current_scope": "separate TODO owner ledgers and canonical-gap boundaries",
        "missing_exhaustiveness": "proof every missing or partial span has a linked TODO or explicit non-goal",
        "sidecars": (
            "papers/todo_canonical_gap_rollup_boundary.json",
            "papers/roadmap_source_span_coverage_boundary.json",
        ),
        "active_todos": (
            {"path": "docs/todo/roadmap.md", "required_phrase": "missing/partial TODO proof"},
            {"path": "docs/todo/roadmap.md", "required_phrase": "domain-specific missing/partial TODO proof"},
        ),
        "validation_gate": "missing/partial span TODO proof gate",
        "readiness_status": "todo_ledgers_without_span_level_join",
    },
    {
        "criterion_id": "phase_priority_map",
        "source_surface": "phase priorities for missing, partial, and non-goal source spans",
        "current_scope": "all 55 named spans carry near-, mid-, or longer-term ROADMAP phases",
        "missing_exhaustiveness": "claim-level priority and dependency mapping for application-result work",
        "sidecars": (
            "papers/roadmap_phase_sequence_boundary.json",
            "papers/roadmap_source_span_coverage_boundary.json",
        ),
        "active_todos": (
            {"path": "docs/todo/roadmap.md", "required_phrase": "phase-priority map"},
            {"path": "docs/todo/roadmap.md", "required_phrase": "phase-priority"},
        ),
        "validation_gate": "source-span phase-priority gate",
        "readiness_status": "named_span_phase_map_complete_without_claim_level_priorities",
    },
    {
        "criterion_id": "ci_exhaustiveness_and_owner_signoff",
        "source_surface": "CI source-span exhaustiveness gate, undispositioned row detector, and owner signoff",
        "current_scope": "bounded generated sidecars without CI exhaustiveness gate",
        "missing_exhaustiveness": "CI source-span exhaustiveness gate plus owner review signoff",
        "sidecars": (
            "papers/roadmap_source_span_coverage_boundary.json",
            "papers/documentation_claim_inventory.json",
        ),
        "active_todos": (
            {"path": "docs/todo/roadmap.md", "required_phrase": "CI source-span exhaustiveness gate"},
            {"path": "docs/todo/roadmap.md", "required_phrase": "owner review signoff"},
        ),
        "validation_gate": "CI source-span exhaustiveness and owner signoff gate",
        "readiness_status": "bounded_sidecars_without_ci_exhaustiveness_gate",
    },
)


@dataclass(frozen=True)
class RoadmapSourceSpanExhaustivenessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapSourceSpanExhaustivenessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    exhaustiveness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapSourceSpanExhaustivenessBoundaryIssue]


def roadmap_source_span_exhaustiveness_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP source-span exhaustiveness gate."""

    root_path = Path(root)
    source_boundary = roadmap_source_span_coverage_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    return {
        "schema": ROADMAP_SOURCE_SPAN_EXHAUSTIVENESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_coverage_boundary_input": SOURCE_COVERAGE_BOUNDARY_INPUT,
        "source_coverage_surface_count": source_boundary["coverage_surface_count"],
        "source_named_span_disposition_count": source_boundary[
            "named_source_span_disposition_count"
        ],
        "source_paper_status_row_count": source_boundary["paper_status_row_count"],
        "source_paper_status_row_dispositioned_count": source_boundary["paper_status_row_dispositioned_count"],
        "source_missing_evidence_count": len(source_boundary["missing_evidence"]),
        "exhaustiveness_criterion_count": len(records),
        "sidecar_ref_count": sum(len(record["sidecar_refs"]) for record in records),
        "active_todo_ref_count": sum(len(record["active_todo_refs"]) for record in records),
        "exhaustiveness_criteria": records,
        "completed_evidence": {
            "named_structure_span_count": source_boundary[
                "named_source_span_disposition_count"
            ],
            "named_structure_inventory": "pdf_page_and_anchor_verified",
            "named_span_status_and_phase_map": "recorded",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a complete named-structure gate for all 55 "
            "PDF-verified sections, figures, tables, and appendices. It does "
            "not claim sentence- or claim-level requirement exhaustiveness, a "
            "claim-level figure/table/appendix matrix, application-result claim matrix, status-row to ROADMAP "
            "disposition map, missing/partial TODO proof, non-goal decision "
            "map, phase-priority map, CI source-span exhaustiveness gate, or "
            "owner review signoff."
        ),
    }


def validate_roadmap_source_span_exhaustiveness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapSourceSpanExhaustivenessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_source_span_exhaustiveness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapSourceSpanExhaustivenessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_source_span_exhaustiveness_boundary_record(root)
    issues: list[RoadmapSourceSpanExhaustivenessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_SOURCE_SPAN_EXHAUSTIVENESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP source-span exhaustiveness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP source-span exhaustiveness boundary must not claim exhaustive source-span coverage"))
    for key in (
        "source_coverage_boundary_input",
        "source_coverage_surface_count",
        "source_named_span_disposition_count",
        "source_paper_status_row_count",
        "source_paper_status_row_dispositioned_count",
        "source_missing_evidence_count",
        "exhaustiveness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "exhaustiveness_criteria",
        "completed_evidence",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current source-span coverage inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "complete named-structure gate for all 55" not in boundary_text
        or "claim-level requirement exhaustiveness" not in boundary_text
        or "CI source-span exhaustiveness gate" not in boundary_text
        or "owner review signoff" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded coverage from exhaustive source-span disposition"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapSourceSpanExhaustivenessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        exhaustiveness_criterion_count=data.get("exhaustiveness_criterion_count") if isinstance(data.get("exhaustiveness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_source_span_exhaustiveness_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_source_span_exhaustiveness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP source-span exhaustiveness boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| exhaustiveness_criterion_count | {validation.exhaustiveness_criterion_count} |",
        f"| sidecar_ref_count | {validation.sidecar_ref_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _criterion_record(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "criterion_id": spec["criterion_id"],
        "source_surface": spec["source_surface"],
        "current_scope": spec["current_scope"],
        "missing_exhaustiveness": spec["missing_exhaustiveness"],
        "sidecar_refs": [_sidecar_ref(root, path) for path in spec["sidecars"]],
        "active_todo_refs": [_active_todo_ref(root, todo) for todo in spec["active_todos"]],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _sidecar_ref(root: Path, path: str) -> dict[str, Any]:
    return {"path": path, "exists": (root / path).exists()}


def _active_todo_ref(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    required_phrase = spec["required_phrase"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": required_phrase,
        "required_phrase_present": _contains_phrase(text, required_phrase),
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
) -> tuple[dict[str, Any] | None, list[RoadmapSourceSpanExhaustivenessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP source-span exhaustiveness boundary must be a JSON object")]


def _validate_required_fields(value: object, issues: list[RoadmapSourceSpanExhaustivenessBoundaryIssue]) -> int:
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


def _validate_missing_evidence(value: object, issues: list[RoadmapSourceSpanExhaustivenessBoundaryIssue]) -> int:
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


def _issue(code: str, message: str) -> RoadmapSourceSpanExhaustivenessBoundaryIssue:
    return RoadmapSourceSpanExhaustivenessBoundaryIssue(code=code, message=message)
