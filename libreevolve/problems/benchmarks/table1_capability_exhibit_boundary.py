from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TABLE1_CAPABILITY_EXHIBIT_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_table1_capability_exhibit_boundary.v1"
)
TABLE1_CAPABILITY_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.alphaevolve_table1_capability_exhibit_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_TABLE_ID = "alphaevolve_table_1_capability_comparison"
EXPECTED_BOUNDARY_STATUS = "table_exhibit_provenance_only"
EXPECTED_ROW_IDS = (
    "table1.function_vs_file_scope",
    "table1.code_length_scale",
    "table1.programming_language_scope",
    "table1.evaluator_workload_scope",
    "table1.llm_sample_efficiency",
    "table1.model_scale_effect",
    "table1.prompt_context_feedback",
    "table1.metric_optimization_scope",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stable_table_id",
    "stable_row_ids",
    "source_page_caption_location",
    "funsearch_alphaevolve_cell_text",
    "row_to_todo_report_mapping",
    "rendered_artifact_hashes",
    "table_exhibit_record_ready",
    "benchmark_backed_code_scale_parity",
    "arbitrary_language_runner_parity",
    "parallel_accelerator_evaluator_parity",
    "equal_budget_sample_efficiency_parity",
    "sota_model_scale_parity",
    "full_rich_context_feedback_parity",
    "multi_metric_benchmark_parity",
    "full_table1_parity",
)
EXPECTED_MISSING_EVIDENCE = {
    "benchmark_backed_code_scale_parity": "not_recorded_locally",
    "arbitrary_language_runner_parity": "not_recorded_locally",
    "parallel_accelerator_evaluator_parity": "not_recorded_locally",
    "equal_budget_sample_efficiency_parity": "not_recorded_locally",
    "sota_model_scale_parity": "not_recorded_locally",
    "full_rich_context_feedback_parity": "not_recorded_locally",
    "multi_metric_benchmark_parity": "not_recorded_locally",
    "full_table1_parity": "not_recorded_locally",
}


@dataclass(frozen=True)
class Table1CapabilityExhibitBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class Table1CapabilityExhibitBoundaryValidation:
    ok: bool
    boundary_status: str | None
    row_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[Table1CapabilityExhibitBoundaryIssue]


def table1_capability_exhibit_boundary_record() -> dict[str, Any]:
    """Return the current AlphaEvolve Table 1 exhibit/parity boundary."""

    return {
        "schema": TABLE1_CAPABILITY_EXHIBIT_BOUNDARY_SCHEMA,
        "runtime_report_schema": TABLE1_CAPABILITY_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "table_id": EXPECTED_TABLE_ID,
        "source_table_label": "Table 1",
        "local_pdf_page": 2,
        "caption": "Capabilities and typical behaviours of AlphaEvolve and our previous agent.",
        "row_ids": list(EXPECTED_ROW_IDS),
        "source_claim": (
            "AlphaEvolve Table 1 compares FunSearch and AlphaEvolve across "
            "eight capability and behavior rows, but reproducing the table "
            "artifact is not proof that each AlphaEvolve capability row is met"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "alphaevolve_table1_capability_exhibit_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can preserve AlphaEvolve "
            "Table 1 as a source-table exhibit with stable row ids, source "
            "page/caption location, FunSearch and AlphaEvolve cell text, "
            "row-to-gap mappings, and rendered artifact hashes, but does not "
            "claim benchmark-backed code-scale parity, arbitrary-language "
            "runner parity, parallel or accelerator evaluator parity, "
            "equal-budget sample-efficiency parity, SOTA model-scale parity, "
            "full rich-context feedback parity, multi-metric benchmark parity, "
            "or full Table 1 capability parity."
        ),
    }


def validate_table1_capability_exhibit_boundary(
    boundary: object | str | Path | None = None,
) -> Table1CapabilityExhibitBoundaryValidation:
    data, read_issues = _load_boundary(
        table1_capability_exhibit_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return Table1CapabilityExhibitBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[Table1CapabilityExhibitBoundaryIssue] = []
    if data.get("schema") != TABLE1_CAPABILITY_EXHIBIT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Table 1 capability-exhibit boundary schema"))
    if data.get("runtime_report_schema") != TABLE1_CAPABILITY_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify Table 1 capability-exhibit reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("table_id") != EXPECTED_TABLE_ID:
        issues.append(_issue("invalid_table_id", f"table_id must be {EXPECTED_TABLE_ID}"))
    if data.get("source_table_label") != "Table 1":
        issues.append(_issue("invalid_source_table_label", "source_table_label must be Table 1"))
    if data.get("local_pdf_page") != 2:
        issues.append(_issue("invalid_local_pdf_page", "local_pdf_page must be 2"))
    row_count = _validate_row_ids(data.get("row_ids"), issues)
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "not proof" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must distinguish table artifact from row proof"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "alphaevolve_table1_capability_exhibit_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to Table 1 exhibit reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Table 1 exhibit boundary must not claim capability parity"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim Table 1 parity"))
    return Table1CapabilityExhibitBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        row_count=row_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_table1_capability_exhibit_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_table1_capability_exhibit_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve Table 1 capability-exhibit boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| row_count | {validation.row_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[Table1CapabilityExhibitBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Table 1 capability-exhibit boundary must be a JSON object")]


def _validate_row_ids(
    value: object,
    issues: list[Table1CapabilityExhibitBoundaryIssue],
) -> int:
    if value != list(EXPECTED_ROW_IDS):
        issues.append(_issue("invalid_row_ids", "row_ids must match the eight Table 1 capability rows in order"))
        return len(value) if isinstance(value, list) else 0
    return len(EXPECTED_ROW_IDS)


def _validate_required_fields(
    value: object,
    issues: list[Table1CapabilityExhibitBoundaryIssue],
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
    issues: list[Table1CapabilityExhibitBoundaryIssue],
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


def _issue(code: str, message: str) -> Table1CapabilityExhibitBoundaryIssue:
    return Table1CapabilityExhibitBoundaryIssue(code, message)
