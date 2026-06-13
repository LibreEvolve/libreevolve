from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ARCHIVE_EVENT_REPLAY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_archive_event_replay_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_AUDIT_SCHEMA = "libreevolve.archive_event_replay_audit.v1"
EXPECTED_MIGRATION_REPLAY_POLICY_SCHEMA = (
    "libreevolve.island_migration_replay_policy.v1"
)
EXPECTED_BOUNDARY_STATUS = "archive_snapshot_restore_with_audit_only_event_replay"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "archive_events_jsonl_schema_validation",
    "non_decreasing_migration_sequence_validation",
    "archive_state_cursor_snapshot_restore",
    "archive_contents_cell_elite_snapshot_restore",
    "accepted_history_program_snapshot_join",
    "archive_event_replay_audit_schema",
    "final_migration_placement_audit",
    "archive_contents_comparison",
    "migration_replay_policy_no_restore_engine_flag",
    "cli_cursor_restore_entrypoint",
    "cli_full_archive_restore_entrypoint",
    "ordered_archive_event_restore_engine",
    "skip_event_reconstruction",
    "replacement_history_replay",
    "descriptor_policy_mismatch_restore_failure",
    "controller_pending_work_restore",
)
EXPECTED_MISSING_EVIDENCE = {
    "ordered_archive_event_restore_engine": "not_recorded_locally",
    "skip_event_reconstruction": "not_recorded_locally",
    "replacement_history_replay": "not_recorded_locally",
    "descriptor_policy_mismatch_restore_failure": "not_recorded_locally",
    "controller_pending_work_restore": "not_recorded_locally",
}


@dataclass(frozen=True)
class ArchiveEventReplayBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ArchiveEventReplayBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ArchiveEventReplayBoundaryIssue]


def archive_event_replay_boundary_record() -> dict[str, Any]:
    """Return the archive-event audit versus restore-engine boundary."""

    return {
        "schema": ARCHIVE_EVENT_REPLAY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve's evolutionary database is active population state, "
            "so archive resume should distinguish durable current-state "
            "snapshots from ordered migration-event replay"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_audit_schema": EXPECTED_RUNTIME_AUDIT_SCHEMA,
        "migration_replay_policy_schema": EXPECTED_MIGRATION_REPLAY_POLICY_SCHEMA,
        "runtime_report_status": "archive_event_replay_audit_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve validates archive_events.jsonl, "
            "checks non-decreasing migration sequences, restores archive cursor "
            "state and current cell/elite archive contents from manifest snapshots "
            "joined with accepted history, and emits an archive-event replay audit "
            "that compares final migration placements against archive contents. "
            "It does not claim ordered archive-event restore-engine support, skip "
            "event reconstruction, replacement-history replay, descriptor-policy "
            "mismatch restore failures, or controller pending-work restore."
        ),
    }


def validate_archive_event_replay_boundary(
    boundary: object | str | Path | None = None,
) -> ArchiveEventReplayBoundaryValidation:
    data, read_issues = _load_boundary(
        archive_event_replay_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ArchiveEventReplayBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ArchiveEventReplayBoundaryIssue] = []
    if data.get("schema") != ARCHIVE_EVENT_REPLAY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported archive-event replay boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "active population state" not in source_claim
        or "ordered migration-event replay" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify archive population-state replay"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_audit_schema") != EXPECTED_RUNTIME_AUDIT_SCHEMA:
        issues.append(_issue("invalid_runtime_audit_schema", f"runtime_audit_schema must be {EXPECTED_RUNTIME_AUDIT_SCHEMA}"))
    if data.get("migration_replay_policy_schema") != EXPECTED_MIGRATION_REPLAY_POLICY_SCHEMA:
        issues.append(_issue("invalid_migration_replay_policy_schema", f"migration_replay_policy_schema must be {EXPECTED_MIGRATION_REPLAY_POLICY_SCHEMA}"))
    if data.get("runtime_report_status") != "archive_event_replay_audit_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to archive-event replay audits"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "archive-event replay boundary must not claim restore-engine readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim ordered archive-event restore-engine support" not in boundary_text
        or "replacement-history replay" not in boundary_text
        or "controller pending-work restore" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate audit-only archive replay from restore-engine readiness"))
    return ArchiveEventReplayBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_archive_event_replay_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_archive_event_replay_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Archive-event replay boundary",
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
) -> tuple[dict[str, Any] | None, list[ArchiveEventReplayBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "archive-event replay boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ArchiveEventReplayBoundaryIssue],
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
    issues: list[ArchiveEventReplayBoundaryIssue],
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


def _issue(code: str, message: str) -> ArchiveEventReplayBoundaryIssue:
    return ArchiveEventReplayBoundaryIssue(code, message)
