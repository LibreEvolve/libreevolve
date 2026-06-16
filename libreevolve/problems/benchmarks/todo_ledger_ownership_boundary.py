from __future__ import annotations

import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TODO_LEDGER_OWNERSHIP_BOUNDARY_SCHEMA = "libreevolve.todo_ledger_ownership_boundary.v1"
EXPECTED_BOUNDARY_STATUS = "ledger_owner_inventory_without_canonical_gap_deduplication"
TODO_LINE_RE = re.compile(r"^- \[( |x)\]\s+(.+?)\s*$", flags=re.MULTILINE)
TITLE_NORMALIZE_RE = re.compile(r"[^a-z0-9]+")
EXPECTED_OWNER_GROUPS = (
    {
        "owner_id": "code",
        "owner_scope": "implementation",
        "active_path": "docs/todo/code.md",
        "completed_path": "docs/todo/Completed/code.md",
    },
    {
        "owner_id": "papers",
        "owner_scope": "paper_and_benchmark_evidence",
        "active_path": "docs/todo/papers.md",
        "completed_path": "docs/todo/Completed/papers.md",
    },
    {
        "owner_id": "readme",
        "owner_scope": "user_facing_documentation_truthfulness",
        "active_path": "docs/todo/readme.md",
        "completed_path": "docs/todo/Completed/readme.md",
    },
    {
        "owner_id": "roadmap",
        "owner_scope": "planning_priority_and_phase_evidence",
        "active_path": "docs/todo/roadmap.md",
        "completed_path": "docs/todo/Completed/roadmap.md",
    },
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "ledger_owner_inventory",
    "active_completed_marker_policy",
    "exact_normalized_title_duplicate_scan",
    "canonical_gap_ids",
    "derivative_relationships",
    "cross_document_rollup_rules",
    "source_or_paper_anchor_mapping",
    "implementation_evidence_links",
    "stale_duplicate_detector",
    "canonical_gap_completion_percent",
)
EXPECTED_MISSING_EVIDENCE = {
    "canonical_gap_ids": "not_recorded_locally",
    "derivative_relationships": "not_recorded_locally",
    "cross_document_rollup_rules": "not_recorded_locally",
    "source_or_paper_anchor_mapping": "not_recorded_locally",
    "implementation_evidence_links": "not_recorded_locally",
    "stale_duplicate_detector": "not_recorded_locally",
    "canonical_gap_completion_percent": "not_recorded_locally",
}


@dataclass(frozen=True)
class TodoLedgerOwnershipBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class TodoLedgerOwnershipBoundaryValidation:
    ok: bool
    boundary_status: str | None
    owner_record_count: int
    missing_evidence_count: int
    issues: list[TodoLedgerOwnershipBoundaryIssue]


def todo_ledger_ownership_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return TODO-ledger ownership and duplicate-audit boundary evidence."""

    root_path = Path(root)
    owner_records: list[dict[str, Any]] = []
    task_records: list[dict[str, Any]] = []
    for group in EXPECTED_OWNER_GROUPS:
        active_record = _ledger_count_record(root_path, group["active_path"], "active")
        completed_record = _ledger_count_record(root_path, group["completed_path"], "completed")
        owner_records.append(
            {
                "owner_id": group["owner_id"],
                "owner_scope": group["owner_scope"],
                "active_path": group["active_path"],
                "completed_path": group["completed_path"],
                "active_count": active_record["active_count"] + completed_record["active_count"],
                "completed_count": active_record["completed_count"] + completed_record["completed_count"],
                "total_count": active_record["total_count"] + completed_record["total_count"],
                "active_ledger_completed_marker_count": active_record["completed_count"],
                "completed_ledger_active_marker_count": completed_record["active_count"],
                "active_ledger_exists": active_record["exists"],
                "completed_ledger_exists": completed_record["exists"],
            }
        )
        task_records.extend(
            _task_records(root_path, group["active_path"], group["owner_id"], "active")
        )
        task_records.extend(
            _task_records(root_path, group["completed_path"], group["owner_id"], "completed")
        )
    duplicate_groups = _duplicate_title_groups(task_records)
    active_count = sum(record["active_count"] for record in owner_records)
    completed_count = sum(record["completed_count"] for record in owner_records)
    total_count = active_count + completed_count
    return {
        "schema": TODO_LEDGER_OWNERSHIP_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "owner_record_count": len(owner_records),
        "owner_records": owner_records,
        "raw_todo_ledger_active_count": active_count,
        "raw_todo_ledger_completed_count": completed_count,
        "raw_todo_ledger_total_count": total_count,
        "raw_todo_ledger_completion_percent": _percent(completed_count, total_count),
        "active_ledger_completed_marker_count": sum(
            record["active_ledger_completed_marker_count"] for record in owner_records
        ),
        "completed_ledger_active_marker_count": sum(
            record["completed_ledger_active_marker_count"] for record in owner_records
        ),
        "marker_policy_status": _marker_policy_status(owner_records),
        "duplicate_detection_policy": "exact_normalized_title_only",
        "likely_duplicate_title_group_count": len(duplicate_groups),
        "likely_duplicate_title_groups": duplicate_groups,
        "canonical_gap_completion_status": "not_available_without_gap_ids",
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records TODO-ledger owner files, active/completed "
            "marker policy, raw checklist counts, and an exact normalized-title "
            "duplicate scan. It does not claim canonical underlying-gap ids, "
            "derivative cross-document relationships, rollup rules, source or "
            "paper anchor mappings, implementation evidence links, stale "
            "duplicate detection, or canonical-gap completion percentages."
        ),
    }


def validate_todo_ledger_ownership_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> TodoLedgerOwnershipBoundaryValidation:
    data, read_issues = _load_boundary(
        todo_ledger_ownership_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return TodoLedgerOwnershipBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = todo_ledger_ownership_boundary_record(root)
    issues: list[TodoLedgerOwnershipBoundaryIssue] = []
    if data.get("schema") != TODO_LEDGER_OWNERSHIP_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TODO-ledger ownership boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "TODO-ledger ownership boundary must not claim canonical gap readiness"))
    for key in (
        "owner_record_count",
        "owner_records",
        "raw_todo_ledger_active_count",
        "raw_todo_ledger_completed_count",
        "raw_todo_ledger_total_count",
        "raw_todo_ledger_completion_percent",
        "active_ledger_completed_marker_count",
        "completed_ledger_active_marker_count",
        "likely_duplicate_title_group_count",
        "likely_duplicate_title_groups",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current TODO ledgers"))
    if data.get("marker_policy_status") != expected["marker_policy_status"]:
        issues.append(_issue("invalid_marker_policy_status", "marker policy status drifted from active/completed ledgers"))
    if data.get("duplicate_detection_policy") != "exact_normalized_title_only":
        issues.append(_issue("invalid_duplicate_detection_policy", "duplicate scan must stay scoped to exact normalized titles"))
    if data.get("canonical_gap_completion_status") != "not_available_without_gap_ids":
        issues.append(_issue("invalid_canonical_gap_completion_status", "canonical gap completion must not be available without gap ids"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim canonical underlying-gap ids" not in boundary_text
        or "canonical-gap completion percentages" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate raw ledgers from canonical gap completion"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return TodoLedgerOwnershipBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        owner_record_count=data.get("owner_record_count") if isinstance(data.get("owner_record_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_todo_ledger_ownership_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_todo_ledger_ownership_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "TODO ledger ownership boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| owner_record_count | {validation.owner_record_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _ledger_count_record(root: Path, relative_path: str, ledger_kind: str) -> dict[str, Any]:
    path = root / relative_path
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        text = ""
        exists = False
    else:
        exists = True
    active_count = 0
    completed_count = 0
    for match in TODO_LINE_RE.finditer(text):
        if match.group(1) == " ":
            active_count += 1
        else:
            completed_count += 1
    return {
        "path": relative_path,
        "ledger_kind": ledger_kind,
        "exists": exists,
        "active_count": active_count,
        "completed_count": completed_count,
        "total_count": active_count + completed_count,
    }


def _task_records(root: Path, relative_path: str, owner_id: str, ledger_kind: str) -> list[dict[str, Any]]:
    path = root / relative_path
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return []
    records: list[dict[str, Any]] = []
    line_starts = _line_starts(text)
    for match in TODO_LINE_RE.finditer(text):
        line_number = _line_number(line_starts, match.start())
        title = match.group(2).strip()
        records.append(
            {
                "owner_id": owner_id,
                "ledger_kind": ledger_kind,
                "path": relative_path,
                "line_start": line_number,
                "status": "completed" if match.group(1) == "x" else "active",
                "title": title,
                "normalized_title": _normalize_title(title),
            }
        )
    return records


def _duplicate_title_groups(task_records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for record in task_records:
        normalized = record["normalized_title"]
        if normalized:
            groups[normalized].append(record)
    duplicate_groups: list[dict[str, Any]] = []
    for normalized_title, records in sorted(groups.items()):
        if len(records) < 2:
            continue
        owners = sorted({record["owner_id"] for record in records})
        duplicate_groups.append(
            {
                "normalized_title": normalized_title,
                "record_count": len(records),
                "owner_ids": owners,
                "cross_owner": len(owners) > 1,
                "records": records,
            }
        )
    return duplicate_groups


def _marker_policy_status(owner_records: list[dict[str, Any]]) -> str:
    active_completed = sum(
        record["active_ledger_completed_marker_count"] for record in owner_records
    )
    completed_active = sum(
        record["completed_ledger_active_marker_count"] for record in owner_records
    )
    if active_completed == 0 and completed_active == 0:
        return "active_ledgers_unchecked_completed_ledgers_checked"
    if active_completed > 0 and completed_active > 0:
        return "active_and_completed_ledgers_have_cross_markers"
    if active_completed > 0:
        return "active_ledgers_contain_completed_markers"
    return "completed_ledgers_contain_active_markers"


def _normalize_title(title: str) -> str:
    normalized = TITLE_NORMALIZE_RE.sub(" ", title.lower().replace("`", " ")).strip()
    return " ".join(normalized.split())


def _percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 3)


def _line_starts(text: str) -> list[int]:
    starts = [0]
    for index, char in enumerate(text):
        if char == "\n":
            starts.append(index + 1)
    return starts


def _line_number(line_starts: list[int], offset: int) -> int:
    line = 1
    for index, start in enumerate(line_starts, start=1):
        if start > offset:
            break
        line = index
    return line


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[TodoLedgerOwnershipBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "TODO-ledger ownership boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[TodoLedgerOwnershipBoundaryIssue],
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
    issues: list[TodoLedgerOwnershipBoundaryIssue],
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


def _issue(code: str, message: str) -> TodoLedgerOwnershipBoundaryIssue:
    return TodoLedgerOwnershipBoundaryIssue(code=code, message=message)
