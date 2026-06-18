from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


JSONL_DURABILITY_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_jsonl_durability_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "strict_jsonl_append_with_read_fail_closed_and_advisory_writer_locks"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "strict_json_serialization",
    "finite_json_validation",
    "append_side_torn_final_record_repair",
    "newline_terminated_record_writes",
    "fsync_after_append",
    "quarantine_diagnostics",
    "quarantine_retention_modes",
    "strict_reader_schema_validation",
    "read_side_torn_final_record_repair",
    "read_side_fail_closed_unterminated_record_policy",
    "show_resume_reader_coverage",
    "archive_restore_reader_coverage",
    "controller_budget_reader_coverage",
    "manifest_summary_reader_coverage",
    "plugin_context_reader_coverage",
    "multi_writer_serialization",
    "append_ordering_sequence_ownership",
    "repair_quarantine_atomicity",
    "cross_platform_locking_policy",
    "concurrent_writer_tests",
)
EXPECTED_MISSING_EVIDENCE = {
    "append_ordering_sequence_ownership": "not_recorded_locally",
    "repair_quarantine_atomicity": "not_recorded_locally",
}


@dataclass(frozen=True)
class JsonlDurabilityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class JsonlDurabilityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[JsonlDurabilityBoundaryIssue]


def jsonl_durability_boundary_record() -> dict[str, Any]:
    """Return the strict-JSONL append versus durable async-state boundary."""

    return {
        "schema": JSONL_DURABILITY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve-style long-running search needs durable run streams "
            "that can be trusted during inspection, resume, and future "
            "async/distributed writer execution"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "implemented_runtime_evidence": {
            "strict_json_serialization": "strict_json_dumps_rejects_non_finite_and_duplicate_keys",
            "finite_json_validation": "strict_object_validation_before_append",
            "append_side_torn_final_record_repair": "repair_trailing_partial_jsonl_before_append",
            "newline_terminated_record_writes": "managed_appends_write_one_newline_terminated_record",
            "fsync_after_append": "append_helper_flushes_and_fsyncs",
            "quarantine_diagnostics": "invalid_record_and_torn_fragment_diagnostics",
            "quarantine_retention_modes": "redacted_hash_and_off_snapshot_retention",
            "strict_reader_schema_validation": "iter_strict_jsonl_objects_validates_json_objects_per_line",
            "read_side_torn_final_record_repair": "iter_strict_jsonl_objects_opt_in_repair_torn_final_record_quarantine",
            "read_side_fail_closed_unterminated_record_policy": "iter_strict_jsonl_objects_rejects_newline_missing_final_record_by_default",
            "show_resume_reader_coverage": "show_restore_and_history_join_readers_use_iter_strict_jsonl_objects",
            "archive_restore_reader_coverage": "load_archive_event_records_uses_iter_strict_jsonl_objects",
            "controller_budget_reader_coverage": "controller_budget_replay_and_audit_readers_use_iter_strict_jsonl_objects",
            "manifest_summary_reader_coverage": "strict_jsonl_stream_summaries_use_iter_strict_jsonl_objects",
            "plugin_context_reader_coverage": "ttt_rl_restore_counts_unterminated_final_grpo_row_as_invalid",
            "multi_writer_serialization": "append_strict_jsonl_locks_stream_and_quarantine_paths_in_stable_order",
            "cross_platform_locking_policy": "msvcrt_locking_on_windows_and_fcntl_flock_on_posix",
            "concurrent_writer_tests": "subprocess_writers_append_80_valid_rows_to_one_stream",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records strict local JSONL serialization, finite JSON "
            "validation, append-side torn-final-record repair, newline-terminated "
            "record writes, fsync after append, quarantine diagnostics, retention "
            "modes, per-line strict reader validation, default fail-closed "
            "unterminated-final-record handling, opt-in read-side torn-record "
            "repair, and show/archive/controller/manifest/plugin reader "
            "coverage through the strict reader boundary. It also records "
            "helper-managed advisory interprocess append serialization, "
            "Windows/POSIX lock selection, stable stream/quarantine lock "
            "ordering, and a subprocess concurrent-writer test. It does not "
            "claim semantic append ordering ownership, crash-atomic "
            "repair/quarantine transactions, or AlphaEvolve-grade durable "
            "async run-state parity."
        ),
    }


def validate_jsonl_durability_boundary(
    boundary: object | str | Path | None = None,
) -> JsonlDurabilityBoundaryValidation:
    data, read_issues = _load_boundary(
        jsonl_durability_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return JsonlDurabilityBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[JsonlDurabilityBoundaryIssue] = []
    if data.get("schema") != JSONL_DURABILITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported JSONL durability boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "durable run streams" not in source_claim
        or "async/distributed writer execution" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify durable run-stream scope"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "JSONL durability boundary must not claim durable async run-state parity"))
    implemented_count = _validate_implemented_runtime_evidence(
        data.get("implemented_runtime_evidence"), issues
    )
    if implemented_count != 18:
        issues.append(_issue("invalid_implemented_runtime_evidence_count", "implemented runtime evidence count must be 18"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "default fail-closed unterminated-final-record handling" not in boundary_text
        or "advisory interprocess append serialization" not in boundary_text
        or "semantic append ordering ownership" not in boundary_text
        or "AlphaEvolve-grade durable async run-state parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate strict append behavior from durable async run-state parity"))
    return JsonlDurabilityBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_jsonl_durability_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_jsonl_durability_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "JSONL durability boundary",
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
) -> tuple[dict[str, Any] | None, list[JsonlDurabilityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "JSONL durability boundary must be a JSON object")]


def _validate_implemented_runtime_evidence(
    value: object,
    issues: list[JsonlDurabilityBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_implemented_runtime_evidence", "implemented_runtime_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS) - set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_implemented_runtime_evidence", f"implemented_runtime_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_implemented_runtime_evidence", f"implemented_runtime_evidence has unknown keys: {', '.join(extra)}"))
    for key, evidence_status in value.items():
        if not isinstance(key, str) or not isinstance(evidence_status, str) or not evidence_status:
            issues.append(_issue("invalid_implemented_runtime_evidence_entry", "implemented runtime evidence entries must be non-empty text"))
            break
    return len(actual_keys)


def _validate_required_fields(
    value: object,
    issues: list[JsonlDurabilityBoundaryIssue],
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
    issues: list[JsonlDurabilityBoundaryIssue],
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


def _issue(code: str, message: str) -> JsonlDurabilityBoundaryIssue:
    return JsonlDurabilityBoundaryIssue(code, message)
