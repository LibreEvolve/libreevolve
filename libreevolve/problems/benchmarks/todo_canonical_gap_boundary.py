from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.todo_ledger_ownership_boundary import (
    todo_ledger_ownership_boundary_record,
)


TODO_CANONICAL_GAP_BOUNDARY_SCHEMA = "libreevolve.todo_canonical_gap_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "bounded_todo_canonical_gap_matrix_with_exact_stale_duplicate_detector"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "canonical_gap_criteria",
    "raw_ledger_counts",
    "exact_duplicate_group_count",
    "canonical_gap_ids",
    "canonical_owner_ledgers",
    "derivative_relationships",
    "source_or_paper_anchor_mapping",
    "implementation_evidence_links",
    "cross_document_rollup_rules",
    "semantic_duplicate_detector",
    "stale_duplicate_detector",
    "canonical_gap_completion_percent",
)
EXPECTED_MISSING_EVIDENCE = {
    "canonical_gap_ids": "not_recorded_locally",
    "canonical_owner_assignments": "not_recorded_locally",
    "derivative_documentation_relationships": "not_recorded_locally",
    "source_or_paper_anchor_mapping": "not_recorded_locally",
    "implementation_evidence_links": "not_recorded_locally",
    "cross_document_rollup_rules": "not_recorded_locally",
    "semantic_duplicate_detector": "not_recorded_locally",
    "stale_completed_duplicate_detector": "not_recorded_locally",
    "orphaned_derivative_detector": "not_recorded_locally",
    "canonical_gap_completion_percent": "not_recorded_locally",
    "raw_count_inflation_report": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "canonical_gap_ids",
        "ledger_surface": "active and completed TODO titles across owner ledgers",
        "current_scope": "raw checklist items plus exact normalized-title duplicate groups",
        "missing_readiness": "stable canonical underlying-gap ids shared across code, ROADMAP, README, and papers ledgers",
        "sidecars": ("papers/todo_ledger_ownership_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "canonical underlying-gap id",
            },
        ),
        "validation_gate": "canonical gap-id registry with stable ids and owner ledgers",
        "readiness_status": "raw_titles_without_gap_ids",
    },
    {
        "criterion_id": "canonical_owner_ledgers",
        "ledger_surface": "code, ROADMAP, README, and papers TODO owner files",
        "current_scope": "four owner ledgers with owner scopes and active/completed counts",
        "missing_readiness": "one canonical owner ledger per underlying gap plus allowed derivative ledgers",
        "sidecars": ("papers/todo_ledger_ownership_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "canonical owner assignments",
            },
        ),
        "validation_gate": "canonical owner assignment and derivative-owner policy",
        "readiness_status": "owner_file_inventory_only",
    },
    {
        "criterion_id": "derivative_relationships",
        "ledger_surface": "cross-document TODOs that represent one AlphaEvolve gap",
        "current_scope": "exact normalized duplicate-title groups without semantic relationship labels",
        "missing_readiness": "derivative/documentation relationship records and orphaned-derivative detection",
        "sidecars": (
            "papers/todo_ledger_ownership_boundary.json",
            "papers/documentation_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "derivative documentation relationships",
            },
        ),
        "validation_gate": "derivative relationship registry and orphan detector",
        "readiness_status": "exact_duplicate_groups_without_relationships",
    },
    {
        "criterion_id": "source_paper_anchor_mapping",
        "ledger_surface": "TODO rows linked to AlphaEvolve source spans and paper-index rows",
        "current_scope": "selected source-span and paper-status evidence sidecars",
        "missing_readiness": "source/paper anchor mapping for every canonical gap",
        "sidecars": (
            "papers/roadmap_source_span_disposition_boundary.json",
            "papers/status_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "source/paper anchor mapping",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "semantic evidence mapping for every paper-index status row",
            },
        ),
        "validation_gate": "canonical gap to source span and paper row mapping",
        "readiness_status": "selected_source_and_status_rows_only",
    },
    {
        "criterion_id": "implementation_evidence_links",
        "ledger_surface": "implementation, test, runtime-artifact, and sidecar links",
        "current_scope": "selected implementation evidence anchors plus structural docs inventories",
        "missing_readiness": "implementation evidence links for every canonical gap",
        "sidecars": (
            "papers/implementation_evidence_map_boundary.json",
            "papers/roadmap_claim_evidence_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "exhaustive implementation-evidence mapping",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "implementation evidence links",
            },
        ),
        "validation_gate": "canonical gap to implementation evidence sufficiency map",
        "readiness_status": "selected_anchor_map_without_gap_sufficiency",
    },
    {
        "criterion_id": "cross_document_rollup_rules",
        "ledger_surface": "raw checklist completion versus canonical gap completion",
        "current_scope": "raw TODO-ledger and weighted readiness percentages",
        "missing_readiness": "cross-document completion rollup rules for canonical gaps",
        "sidecars": (
            "papers/todo_ledger_ownership_boundary.json",
            "papers/roadmap_readiness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "cross-document rollup rules",
            },
        ),
        "validation_gate": "canonical gap completion rollup report",
        "readiness_status": "raw_and_weighted_checklist_counts_only",
    },
    {
        "criterion_id": "semantic_duplicate_detection",
        "ledger_surface": "near-duplicate TODOs with different wording",
        "current_scope": "exact normalized-title duplicate scan only",
        "missing_readiness": "semantic duplicate detector across active and completed ledgers",
        "sidecars": ("papers/todo_ledger_ownership_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "semantic duplicate detector",
            },
        ),
        "validation_gate": "semantic duplicate scan with reviewable groups",
        "readiness_status": "exact_title_duplicates_only",
    },
    {
        "criterion_id": "stale_duplicate_and_orphan_detection",
        "ledger_surface": "completed duplicates and derivative TODOs after implementation changes",
        "current_scope": "no stale duplicate or orphan derivative detector",
        "missing_readiness": "stale completed duplicate detector and orphaned derivative detector",
        "sidecars": ("papers/todo_ledger_ownership_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "stale completed duplicate detection",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "orphaned derivative detection",
            },
        ),
        "validation_gate": "stale duplicate and orphan derivative report",
        "readiness_status": "no_stale_or_orphan_detector",
    },
    {
        "criterion_id": "raw_count_inflation_reporting",
        "ledger_surface": "project completion percentage reporting",
        "current_scope": "raw and weighted checklist percentages without canonical underlying-gap denominator",
        "missing_readiness": "raw-count inflation report and canonical underlying-gap completion percentage",
        "sidecars": (
            "papers/todo_ledger_ownership_boundary.json",
            "papers/roadmap_readiness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "inflate the denominator",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "canonical underlying-gap completion",
            },
        ),
        "validation_gate": "published raw checklist versus canonical gap completion report",
        "readiness_status": "raw_count_completion_only",
    },
)


@dataclass(frozen=True)
class TodoCanonicalGapBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class TodoCanonicalGapBoundaryValidation:
    ok: bool
    boundary_status: str | None
    criterion_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[TodoCanonicalGapBoundaryIssue]


def todo_canonical_gap_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded TODO canonical-gap readiness matrix."""

    root_path = Path(root)
    ownership = todo_ledger_ownership_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    return {
        "schema": TODO_CANONICAL_GAP_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "raw_todo_ledger_active_count": ownership["raw_todo_ledger_active_count"],
        "raw_todo_ledger_completed_count": ownership["raw_todo_ledger_completed_count"],
        "raw_todo_ledger_total_count": ownership["raw_todo_ledger_total_count"],
        "raw_todo_ledger_completion_percent": ownership[
            "raw_todo_ledger_completion_percent"
        ],
        "exact_duplicate_group_count": ownership["likely_duplicate_title_group_count"],
        "duplicate_detection_policy": ownership["duplicate_detection_policy"],
        "exact_stale_completed_duplicate_group_count": ownership[
            "exact_stale_completed_duplicate_group_count"
        ],
        "exact_stale_completed_duplicate_status": ownership[
            "exact_stale_completed_duplicate_status"
        ],
        "canonical_gap_completion_status": "not_available_without_gap_ids",
        "criterion_count": len(records),
        "active_todo_ref_count": active_todo_ref_count,
        "sidecar_ref_count": sidecar_ref_count,
        "criterion_records": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a TODO-ledger canonical-gap readiness matrix "
            "over the current raw owner-ledger counts and exact duplicate-title "
            "groups, plus a bounded exact stale-completed duplicate detector "
            "from the ownership sidecar. It does not claim canonical gap ids, canonical owner "
            "assignments, derivative documentation relationships, source or "
            "paper anchor mappings, implementation evidence links, cross-"
            "document rollup rules, semantic duplicate detection, stale "
            "completed duplicate detection beyond exact title matches, "
            "orphaned derivative detection, raw-"
            "count inflation reporting, canonical gap completion percentages, "
            "or owner review signoff."
        ),
    }


def validate_todo_canonical_gap_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> TodoCanonicalGapBoundaryValidation:
    data, read_issues = _load_boundary(
        todo_canonical_gap_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return TodoCanonicalGapBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = todo_canonical_gap_boundary_record(root)
    issues: list[TodoCanonicalGapBoundaryIssue] = []
    if data.get("schema") != TODO_CANONICAL_GAP_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TODO canonical-gap boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "TODO canonical-gap boundary must not claim canonical gap readiness"))
    for key in (
        "raw_todo_ledger_active_count",
        "raw_todo_ledger_completed_count",
        "raw_todo_ledger_total_count",
        "raw_todo_ledger_completion_percent",
        "exact_duplicate_group_count",
        "duplicate_detection_policy",
        "exact_stale_completed_duplicate_group_count",
        "exact_stale_completed_duplicate_status",
        "canonical_gap_completion_status",
        "criterion_count",
        "active_todo_ref_count",
        "sidecar_ref_count",
        "criterion_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current TODO-ledger inputs"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim canonical gap ids" not in boundary_text
        or "bounded exact stale-completed duplicate detector" not in boundary_text
        or "semantic duplicate detection" not in boundary_text
        or "canonical gap completion percentages" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate raw TODO counts from canonical gap readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return TodoCanonicalGapBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        criterion_count=data.get("criterion_count") if isinstance(data.get("criterion_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_todo_canonical_gap_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_todo_canonical_gap_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "TODO canonical gap boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| criterion_count | {validation.criterion_count} |",
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
        "ledger_surface": spec["ledger_surface"],
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
) -> tuple[dict[str, Any] | None, list[TodoCanonicalGapBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "TODO canonical-gap boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[TodoCanonicalGapBoundaryIssue],
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
    issues: list[TodoCanonicalGapBoundaryIssue],
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


def _issue(code: str, message: str) -> TodoCanonicalGapBoundaryIssue:
    return TodoCanonicalGapBoundaryIssue(code=code, message=message)
