from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_source_inventory_boundary import (
    alphaevolve_source_inventory_boundary_record,
)


ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_source_span_disposition_boundary.v2"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = (
    "named_span_dispositions_plus_132_bounded_claims_without_whole_paper_exhaustiveness"
)
STATUS_CLAIM_INVENTORY_PATH = "papers/status_claim_inventory.json"
SOURCE_INVENTORY_PATH = "papers/alphaevolve_source_inventory_boundary.json"
CONTEXT_CLAIM_INVENTORY_PATH = (
    "papers/alphaevolve_context_claim_inventory_boundary.json"
)
MATRIX_RESULT_CLAIM_INVENTORY_PATH = (
    "papers/alphaevolve_matrix_result_claim_inventory_boundary.json"
)
SYSTEM_REQUIREMENT_INVENTORY_PATH = (
    "papers/alphaevolve_system_requirement_inventory_boundary.json"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "pdf_verified_named_source_span_dispositions",
    "roadmap_section_links",
    "active_todo_links",
    "paper_status_row_inventory_count",
    "claim_level_requirement_inventory",
    "application_result_claim_matrix",
    "status_row_to_roadmap_disposition_map",
    "missing_partial_todo_proof",
    "ci_source_span_exhaustiveness_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "claim_level_requirement_inventory": "132_bounded_claims_remaining_sections_3_2_to_5_and_remaining_exhibits_appendices_not_recorded",
    "application_result_claim_matrix": "not_recorded_locally",
    "status_row_to_roadmap_disposition_map": "not_recorded_locally",
    "missing_partial_todo_proof": "not_recorded_locally",
    "ci_source_span_exhaustiveness_gate": "not_recorded_locally",
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
    source_inventory = alphaevolve_source_inventory_boundary_record(root_path)
    disposition_records = [
        _disposition_record(span) for span in source_inventory["span_records"]
    ]
    status_row_ids = _status_claim_row_ids(root_path)
    return {
        "schema": ROADMAP_SOURCE_SPAN_DISPOSITION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_boundary_input": SOURCE_INVENTORY_PATH,
        "implementation_evidence_map_input": (
            "papers/implementation_evidence_map_boundary.json"
        ),
        "context_claim_inventory_input": CONTEXT_CLAIM_INVENTORY_PATH,
        "matrix_result_claim_inventory_input": MATRIX_RESULT_CLAIM_INVENTORY_PATH,
        "system_requirement_inventory_input": SYSTEM_REQUIREMENT_INVENTORY_PATH,
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
        "completed_evidence": {
            "pdf_named_structure_walk": "38_structure_spans",
            "figure_table_matrix": "14_figures_and_3_tables",
            "appendix_matrix": "appendix_a_appendix_b_and_13_appendix_b_subsections",
            "named_application_sections": "section_3_3_and_4_named_subsections",
            "section_2_system_requirements": "50_pdf_anchored_requirement_dispositions",
            "context_claims": "41_pdf_anchored_abstract_introduction_discussion_and_collaborator_dispositions",
            "matrix_result_claims": "41_pdf_anchored_section_3_1_table_2_figure_4_and_footnote_3_dispositions",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records ROADMAP dispositions for all 55 PDF-verified "
            "named AlphaEvolve structural spans, including sections, figures, "
            "tables, appendices, source pages, local status, roadmap section, "
            "phase bucket, sidecars, and active audit TODO links, plus 132 "
            "bounded claim-level records: 50 Table 1/Section 2 system "
            "requirements and 41 Abstract, Introduction, Discussion, and "
            "collaborator-context claims, plus 41 Section 3.1, Table 2, "
            "Figure 4, and footnote 3 matrix-result claims. It does not "
            "claim whole-paper sentence-, paragraph-, equation-, footnote-, "
            "citation-, or requirement-level exhaustiveness, a claim-level application-result matrix, complete "
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
        "implementation_evidence_map_input",
        "context_claim_inventory_input",
        "matrix_result_claim_inventory_input",
        "system_requirement_inventory_input",
        "source_status_inventory_input",
        "disposition_record_count",
        "disposition_records",
        "disposition_source_ref_count",
        "paper_status_row_count",
        "paper_status_row_ids",
        "paper_status_row_dispositioned_count",
        "paper_status_row_disposition_status",
        "completed_evidence",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current source-span inputs"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "all 55 PDF-verified named AlphaEvolve structural spans" not in boundary_text
        or "requirement-level exhaustiveness" not in boundary_text
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


def _disposition_record(span: dict[str, Any]) -> dict[str, Any]:
    page_start = span["page_start"]
    page_end = span["page_end"]
    page_ref = str(page_start) if page_start == page_end else f"{page_start}-{page_end}"
    return {
        "span_id": span["span_id"],
        "source_kind": span["source_kind"],
        "source_label": span["source_label"],
        "source_refs": [f"2506.13131:pages {page_ref}"],
        "source_ref_count": 1,
        "source_anchor_count": len(span["anchor_checks"]),
        "source_anchors_verified": span["all_anchors_present"],
        "local_claim_status": span["local_status"],
        "roadmap_section_id": span["roadmap_section_id"],
        "roadmap_phase": span["roadmap_phase"],
        "coverage_scope": "named_structure_span",
        "sidecar_refs": [ref["path"] for ref in span["sidecar_refs"]],
        "todo_refs": [
            {"path": ref["path"], "required_phrase": ref["required_phrase"]}
            for ref in span["active_todo_refs"]
        ],
        "disposition_status": "named_structure_disposition_only",
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
