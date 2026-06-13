from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CODEBASE_SCALE_BENCHMARK_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_codebase_scale_benchmark_boundary.v1"
)
CODEBASE_SCALE_RUNTIME_REPORT_SCHEMA = "libreevolve.codebase_scale_benchmark_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("Table 1", "2.1")
EXPECTED_BOUNDARY_STATUS = "runtime_scale_telemetry_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "retained_program_file_line_scale",
    "generated_program_count",
    "multi_file_program_count",
    "hundreds_line_program_count",
    "parent_relative_changed_files",
    "parent_relative_changed_lines",
    "static_file_references",
    "realistic_codebase_benchmark_fixture",
    "cross_file_dependency_edit_evidence",
    "arbitrary_language_runner_execution",
    "build_runner_execution_contract",
    "long_horizon_quality_progress",
    "valid_admitted_retained_rate_summary",
    "table1_code_scale_parity",
)
EXPECTED_MISSING_EVIDENCE = {
    "large_multi_component_benchmark_fixture": "not_recorded_locally",
    "hundreds_line_generated_program_success_curve": "not_recorded_locally",
    "cross_file_dependency_edit_evidence": "not_recorded_locally",
    "arbitrary_language_runner_execution": "not_recorded_locally",
    "build_runner_execution_contract": "not_recorded_locally",
    "long_horizon_quality_progress_on_codebase_task": "not_recorded_locally",
    "benchmark_valid_admitted_retained_rate_summary": "not_recorded_locally",
}


@dataclass(frozen=True)
class CodebaseScaleBenchmarkBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CodebaseScaleBenchmarkBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CodebaseScaleBenchmarkBoundaryIssue]


def codebase_scale_benchmark_boundary_record() -> dict[str, Any]:
    """Return the current AlphaEvolve Table 1 code-scale boundary."""

    return {
        "schema": CODEBASE_SCALE_BENCHMARK_BOUNDARY_SCHEMA,
        "runtime_report_schema": CODEBASE_SCALE_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Table 1 and Section 2.1 report whole-code-file, "
            "hundreds-line, arbitrary-language, multi-component algorithm "
            "evolution, so local parity needs benchmark-backed codebase-scale "
            "evidence rather than only current-run workspace telemetry"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "codebase_scale_benchmark_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has runtime telemetry for "
            "retained program file/line scale, generated candidate counts, "
            "multi-file and hundreds-line observations, parent-relative changed "
            "files/lines, static-file references, and threshold evidence, but "
            "does not claim realistic codebase fixtures, cross-file dependency "
            "edit evidence, arbitrary-language runner execution, build-runner "
            "contracts, long-horizon quality progress, benchmark valid/admitted/"
            "retained-rate summaries, or AlphaEvolve Table 1 code-scale parity."
        ),
    }


def validate_codebase_scale_benchmark_boundary(
    boundary: object | str | Path | None = None,
) -> CodebaseScaleBenchmarkBoundaryValidation:
    data, read_issues = _load_boundary(
        codebase_scale_benchmark_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CodebaseScaleBenchmarkBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CodebaseScaleBenchmarkBoundaryIssue] = []
    if data.get("schema") != CODEBASE_SCALE_BENCHMARK_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported codebase-scale boundary schema"))
    if data.get("runtime_report_schema") != CODEBASE_SCALE_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify codebase-scale benchmark reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['Table 1', '2.1']"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "Table 1" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve Table 1 code scale"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "codebase_scale_benchmark_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to codebase-scale reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "codebase-scale boundary must not claim Table 1 code-scale readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim code-scale parity"))
    return CodebaseScaleBenchmarkBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_codebase_scale_benchmark_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_codebase_scale_benchmark_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve codebase-scale benchmark boundary",
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
) -> tuple[dict[str, Any] | None, list[CodebaseScaleBenchmarkBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "codebase-scale boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[CodebaseScaleBenchmarkBoundaryIssue],
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
    issues: list[CodebaseScaleBenchmarkBoundaryIssue],
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


def _issue(code: str, message: str) -> CodebaseScaleBenchmarkBoundaryIssue:
    return CodebaseScaleBenchmarkBoundaryIssue(code, message)
