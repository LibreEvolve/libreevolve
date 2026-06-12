from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROGRAM_OUTPUT_BOUNDARY_SCHEMA = "libreevolve.program_output_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_PROGRAM_OUTPUT_INDEX_SCHEMA = "libreevolve.program_output_index.v1"
EXPECTED_BOUNDARY_STATUS = "exact_current_run_output_lookup_not_semantic_retrieval"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "evaluator_program_output_capture",
    "strict_json_redaction_and_truncation",
    "bounded_value_previews",
    "source_key_records",
    "output_sha256_records",
    "runtime_program_output_index",
    "valid_output_program_resurfacing_source",
    "exact_source_key_query_api",
    "exact_output_hash_query_api",
    "defensive_current_run_snapshots",
    "durable_output_query_table",
    "schema_aware_output_retrieval",
    "semantic_output_similarity_search",
    "cross_run_output_index",
    "full_output_content_ranking",
    "replayable_output_sampling_policy",
)
EXPECTED_MISSING_EVIDENCE = {
    "durable_output_query_table": "not_recorded_locally",
    "schema_aware_output_retrieval": "not_recorded_locally",
    "semantic_output_similarity_search": "not_recorded_locally",
    "cross_run_output_index": "not_recorded_locally",
    "full_output_content_ranking": "not_recorded_locally",
    "replayable_output_sampling_policy": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProgramOutputBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProgramOutputBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ProgramOutputBoundaryIssue]


def program_output_boundary_record() -> dict[str, Any]:
    """Return the exact current-run output lookup versus semantic retrieval boundary."""

    return {
        "schema": PROGRAM_OUTPUT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve stores generated solutions with attached evaluation "
            "results and program outputs so useful prior programs can be "
            "resurfaced during evolution"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "program_output_index_schema": EXPECTED_PROGRAM_OUTPUT_INDEX_SCHEMA,
        "runtime_report_status": "bounded_current_run_program_output_index_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can capture evaluator "
            "outputs/program_output payloads, redact and truncate them through "
            "strict JSON policy, emit bounded value previews, source-key and "
            "output-hash records, expose runtime.history.program_output_index, "
            "include valid output-bearing programs as a current-run resurfacing "
            "source, and query defensive current-run snapshots by exact source "
            "key or exact output hash. It does not claim durable output query "
            "tables, schema-aware output retrieval, semantic output similarity "
            "search, cross-run output indexes, full output-content ranking, or "
            "replayable output-driven sampling policy."
        ),
    }


def validate_program_output_boundary(
    boundary: object | str | Path | None = None,
) -> ProgramOutputBoundaryValidation:
    data, read_issues = _load_boundary(
        program_output_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ProgramOutputBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ProgramOutputBoundaryIssue] = []
    if data.get("schema") != PROGRAM_OUTPUT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported program-output boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "program outputs" not in source_claim
        or "resurfaced during evolution" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify attached program-output resurfacing"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("program_output_index_schema") != EXPECTED_PROGRAM_OUTPUT_INDEX_SCHEMA:
        issues.append(_issue("invalid_program_output_index_schema", f"program_output_index_schema must be {EXPECTED_PROGRAM_OUTPUT_INDEX_SCHEMA}"))
    if data.get("runtime_report_status") != "bounded_current_run_program_output_index_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to bounded current-run program-output evidence"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "program-output boundary must not claim durable or semantic output retrieval readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim durable output query tables" not in boundary_text
        or "schema-aware output retrieval" not in boundary_text
        or "semantic output similarity search" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate exact current-run output lookup from durable semantic retrieval"))
    return ProgramOutputBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_program_output_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_program_output_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Program output boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ProgramOutputBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "program-output boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ProgramOutputBoundaryIssue],
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
    issues: list[ProgramOutputBoundaryIssue],
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


def _issue(code: str, message: str) -> ProgramOutputBoundaryIssue:
    return ProgramOutputBoundaryIssue(code, message)
