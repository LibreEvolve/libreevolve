from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.implementation_evidence_map_boundary import (
    implementation_evidence_map_boundary_record,
)


ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_source_span_disposition_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "core_anchor_dispositions_without_exhaustive_source_span_matrix"
STATUS_CLAIM_INVENTORY_PATH = "papers/status_claim_inventory.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "core_requirement_anchor_dispositions",
    "roadmap_section_links",
    "active_todo_links",
    "paper_status_row_inventory_count",
    "exhaustive_pdf_section_walk",
    "figure_table_appendix_matrix",
    "application_result_claim_matrix",
    "status_row_to_roadmap_disposition_map",
    "missing_partial_todo_proof",
    "ci_source_span_exhaustiveness_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "exhaustive_pdf_section_walk": "not_recorded_locally",
    "figure_table_appendix_matrix": "not_recorded_locally",
    "application_result_claim_matrix": "not_recorded_locally",
    "status_row_to_roadmap_disposition_map": "not_recorded_locally",
    "missing_partial_todo_proof": "not_recorded_locally",
    "ci_source_span_exhaustiveness_gate": "not_recorded_locally",
}
ROADMAP_SECTION_BY_REQUIREMENT = {
    "alphaevolve_program_markers": "candidate_workspace_fidelity",
    "alphaevolve_evaluator_cascade": "evaluation_cascade",
    "alphaevolve_llm_sampling_and_prompting": "prompt_context_system",
    "alphaevolve_evolutionary_database": "multi_objective_search",
    "alphaevolve_async_distributed_pipeline": "async_resumable_runtime",
    "alphaevolve_published_benchmarks": "representative_benchmarks",
}
ROADMAP_PHASE_BY_REQUIREMENT = {
    "alphaevolve_program_markers": "near_term",
    "alphaevolve_evaluator_cascade": "mid_term",
    "alphaevolve_llm_sampling_and_prompting": "mid_term",
    "alphaevolve_evolutionary_database": "mid_term",
    "alphaevolve_async_distributed_pipeline": "mid_term",
    "alphaevolve_published_benchmarks": "longer_term",
}


@dataclass(frozen=True)
class RoadmapSourceSpanDispositionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapSourceSpanDispositionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    disposition_record_count: int
    missing_evidence_count: int
    issues: list[RoadmapSourceSpanDispositionBoundaryIssue]


def roadmap_source_span_disposition_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the ROADMAP source-span disposition boundary."""

    root_path = Path(root)
    evidence_map = implementation_evidence_map_boundary_record()
    disposition_records = [
        _disposition_record(requirement)
        for requirement in evidence_map["requirements"]
    ]
    status_row_ids = _status_claim_row_ids(root_path)
    return {
        "schema": ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_boundary_input": "papers/implementation_evidence_map_boundary.json",
        "source_status_inventory_input": STATUS_CLAIM_INVENTORY_PATH,
        "disposition_record_count": len(disposition_records),
        "disposition_records": disposition_records,
        "disposition_source_ref_count": sum(
            len(record["source_refs"]) for record in disposition_records
        ),
        "paper_status_row_count": len(status_row_ids),
        "paper_status_row_ids": status_row_ids,
        "paper_status_row_dispositioned_count": 1 if EXPECTED_SOURCE_PAPER_ID in status_row_ids else 0,
        "paper_status_row_disposition_status": (
            "paper_index_rows_not_exhaustively_roadmapped"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records ROADMAP dispositions for the six core "
            "AlphaEvolve requirement anchors already present in the "
            "implementation-evidence map, including source refs, local "
            "status, roadmap section, phase bucket, sidecars, and TODO links. "
            "It does not claim an exhaustive retained-PDF section walk, "
            "figure/table/appendix/application-result matrix, complete "
            "paper-index row to ROADMAP disposition map, proof that every "
            "missing or partial source span has a live TODO, or a CI "
            "source-span exhaustiveness gate."
        ),
    }


def validate_roadmap_source_span_disposition_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapSourceSpanDispositionBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_source_span_disposition_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapSourceSpanDispositionBoundaryValidation(
            False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_source_span_disposition_boundary_record(root)
    issues: list[RoadmapSourceSpanDispositionBoundaryIssue] = []
    if data.get("schema") != ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP source-span disposition boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP source-span disposition boundary must not claim exhaustive coverage"))
    for key in (
        "source_boundary_input",
        "source_status_inventory_input",
        "disposition_record_count",
        "disposition_records",
        "disposition_source_ref_count",
        "paper_status_row_count",
        "paper_status_row_ids",
        "paper_status_row_dispositioned_count",
        "paper_status_row_disposition_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current source-span inputs"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim an exhaustive retained-PDF section walk" not in boundary_text
        or "complete paper-index row to ROADMAP disposition map" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate core anchor dispositions from exhaustive source-span coverage"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapSourceSpanDispositionBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        disposition_record_count=data.get("disposition_record_count") if isinstance(data.get("disposition_record_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_source_span_disposition_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_source_span_disposition_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP source-span disposition boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| disposition_record_count | {validation.disposition_record_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _disposition_record(requirement: dict[str, Any]) -> dict[str, Any]:
    requirement_id = requirement["requirement_id"]
    return {
        "requirement_id": requirement_id,
        "source_refs": list(requirement["source_refs"]),
        "source_ref_count": len(requirement["source_refs"]),
        "local_claim_status": requirement["claim_status"],
        "roadmap_section_id": ROADMAP_SECTION_BY_REQUIREMENT[requirement_id],
        "roadmap_phase": ROADMAP_PHASE_BY_REQUIREMENT[requirement_id],
        "coverage_scope": requirement["coverage_scope"],
        "sidecar_refs": list(requirement["sidecar_refs"]),
        "todo_refs": list(requirement["todo_refs"]),
        "disposition_status": "core_anchor_only_not_exhaustive_source_span",
    }


def _status_claim_row_ids(root: Path) -> list[str]:
    path = root / STATUS_CLAIM_INVENTORY_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    rows = data.get("rows")
    if not isinstance(rows, list):
        return []
    row_ids = [row.get("id") for row in rows if isinstance(row, dict)]
    return [row_id for row_id in row_ids if isinstance(row_id, str)]


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapSourceSpanDispositionBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP source-span disposition boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapSourceSpanDispositionBoundaryIssue],
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
    issues: list[RoadmapSourceSpanDispositionBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapSourceSpanDispositionBoundaryIssue:
    return RoadmapSourceSpanDispositionBoundaryIssue(code=code, message=message)
