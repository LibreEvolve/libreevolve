from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.todo_canonical_gap_boundary import (
    todo_canonical_gap_boundary_record,
)


TODO_CANONICAL_GAP_ROLLUP_BOUNDARY_SCHEMA = (
    "libreevolve.todo_canonical_gap_rollup_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_canonical_gap_rollup_gate_with_exact_same_owner_duplicate_report"
)
SOURCE_CANONICAL_GAP_BOUNDARY_INPUT = "papers/todo_canonical_gap_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "canonical_gap_registry",
    "canonical_owner_policy",
    "derivative_relationship_policy",
    "source_and_implementation_evidence_links",
    "cross_document_rollup_policy",
    "duplicate_and_orphan_detection",
    "canonical_completion_reporting",
    "publication_and_owner_signoff",
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
    "canonical_raw_count_inflation_report": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
MISSING_EVIDENCE_TODO_COVERAGE_SPECS = (
    {
        "evidence_key": "canonical_gap_ids",
        "criterion_id": "canonical_gap_registry",
        "required_phrase": "canonical gap ids",
    },
    {
        "evidence_key": "canonical_owner_assignments",
        "criterion_id": "canonical_owner_policy",
        "required_phrase": "canonical owner assignments",
    },
    {
        "evidence_key": "derivative_documentation_relationships",
        "criterion_id": "derivative_relationship_policy",
        "required_phrase": "derivative documentation relationships",
    },
    {
        "evidence_key": "source_or_paper_anchor_mapping",
        "criterion_id": "source_and_implementation_evidence_links",
        "required_phrase": "source/paper anchor mapping",
    },
    {
        "evidence_key": "implementation_evidence_links",
        "criterion_id": "source_and_implementation_evidence_links",
        "required_phrase": "implementation evidence links",
    },
    {
        "evidence_key": "cross_document_rollup_rules",
        "criterion_id": "cross_document_rollup_policy",
        "required_phrase": "cross-document rollup rules",
    },
    {
        "evidence_key": "semantic_duplicate_detector",
        "criterion_id": "duplicate_and_orphan_detection",
        "required_phrase": "semantic duplicate detection",
    },
    {
        "evidence_key": "stale_completed_duplicate_detector",
        "criterion_id": "duplicate_and_orphan_detection",
        "required_phrase": "stale completed duplicate detection",
    },
    {
        "evidence_key": "orphaned_derivative_detector",
        "criterion_id": "derivative_relationship_policy",
        "required_phrase": "orphaned derivative detection",
    },
    {
        "evidence_key": "canonical_gap_completion_percent",
        "criterion_id": "canonical_completion_reporting",
        "required_phrase": "canonical gap completion percent",
    },
    {
        "evidence_key": "canonical_raw_count_inflation_report",
        "criterion_id": "canonical_completion_reporting",
        "required_phrase": "raw-count inflation report",
    },
    {
        "evidence_key": "owner_review_signoff",
        "criterion_id": "canonical_owner_policy",
        "required_phrase": "owner review signoff",
    },
)


CRITERION_SPECS = (
    {
        "criterion_id": "canonical_gap_registry",
        "ledger_surface": "stable underlying AlphaEvolve gap ids across all TODO owner ledgers",
        "current_scope": "raw checklist items plus exact duplicate-title groups",
        "missing_rollup": "canonical gap ids and duplicate/derivative relationship registry",
        "sidecars": (
            "papers/todo_canonical_gap_boundary.json",
            "papers/todo_ledger_ownership_boundary.json",
        ),
        "active_todos": (
            {"path": "docs/todo/roadmap.md", "required_phrase": "canonical gap ids"},
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "duplicate/derivative relationship registry",
            },
        ),
        "validation_gate": "canonical gap-id registry",
        "readiness_status": "raw_checklist_without_underlying_gap_ids",
    },
    {
        "criterion_id": "canonical_owner_policy",
        "ledger_surface": "canonical owner assignments for code, ROADMAP, README, and papers ledgers",
        "current_scope": "owner files and raw active/completed counts",
        "missing_rollup": "canonical owner assignments and owner review signoff",
        "sidecars": (
            "papers/todo_ledger_ownership_boundary.json",
            "papers/todo_canonical_gap_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "canonical owner assignments",
            },
            {"path": "docs/todo/roadmap.md", "required_phrase": "owner review signoff"},
        ),
        "validation_gate": "canonical owner assignment policy",
        "readiness_status": "owner_file_inventory_without_canonical_owner_policy",
    },
    {
        "criterion_id": "derivative_relationship_policy",
        "ledger_surface": "document-specific TODOs that derive from one underlying capability gap",
        "current_scope": "exact normalized duplicate-title scan without semantic relationship labels",
        "missing_rollup": "derivative documentation relationships and orphaned derivative detection",
        "sidecars": (
            "papers/todo_canonical_gap_boundary.json",
            "papers/documentation_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "derivative documentation relationships",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "orphaned derivative detection",
            },
        ),
        "validation_gate": "derivative relationship and orphan detector",
        "readiness_status": "exact_duplicate_groups_without_derivative_registry",
    },
    {
        "criterion_id": "source_and_implementation_evidence_links",
        "ledger_surface": "source/paper anchors and implementation evidence for every canonical gap",
        "current_scope": "selected source-span and implementation-evidence sidecars",
        "missing_rollup": "source/paper anchor mapping and implementation evidence links",
        "sidecars": (
            "papers/roadmap_source_span_disposition_boundary.json",
            "papers/implementation_evidence_map_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "source/paper anchor mapping",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "implementation evidence links",
            },
        ),
        "validation_gate": "canonical gap evidence-link sufficiency map",
        "readiness_status": "selected_source_and_implementation_anchors_only",
    },
    {
        "criterion_id": "cross_document_rollup_policy",
        "ledger_surface": "raw checklist completion and canonical underlying-gap completion",
        "current_scope": "raw and weighted TODO-ledger percentages",
        "missing_rollup": "cross-document rollup rules and separate canonical completion denominator",
        "sidecars": (
            "papers/roadmap_readiness_boundary.json",
            "papers/roadmap_readiness_publication_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "cross-document rollup rules",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "raw checklist completion separately from canonical underlying-gap completion",
            },
        ),
        "validation_gate": "raw checklist versus canonical gap rollup report",
        "readiness_status": "raw_percentages_without_canonical_rollup",
    },
    {
        "criterion_id": "duplicate_and_orphan_detection",
        "ledger_surface": "semantic duplicates, stale completed duplicates, and orphaned derivatives",
        "current_scope": "exact duplicate-title groups without semantic stale/orphan detectors",
        "missing_rollup": "semantic duplicate detection, stale completed duplicate detection, and orphaned derivative detection",
        "sidecars": (
            "papers/todo_ledger_ownership_boundary.json",
            "papers/todo_canonical_gap_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "semantic duplicate detection",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "stale completed duplicate detection",
            },
        ),
        "validation_gate": "semantic duplicate and stale-completed duplicate detector",
        "readiness_status": "exact_title_duplicates_without_semantic_or_stale_detector",
    },
    {
        "criterion_id": "canonical_completion_reporting",
        "ledger_surface": "published completion percentages and raw-count inflation reports",
        "current_scope": "raw checklist completion plus exact-title inflation estimate without canonical completion percent",
        "missing_rollup": "canonical gap completion percent and canonical raw-count inflation report beyond exact-title duplicates",
        "sidecars": (
            "papers/todo_canonical_gap_boundary.json",
            "papers/roadmap_readiness_publication_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "canonical gap completion percent",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "raw-count inflation report",
            },
        ),
        "validation_gate": "canonical completion percent and raw inflation report",
        "readiness_status": "exact_title_inflation_without_canonical_completion_percent",
    },
    {
        "criterion_id": "publication_and_owner_signoff",
        "ledger_surface": "project-completion percentage reporting and owner-reviewed canonical rollups",
        "current_scope": "raw checklist percentages can still count overlapping TODOs more than once",
        "missing_rollup": "owner-reviewed publication boundary for distinct AlphaEvolve requirements",
        "sidecars": (
            "papers/roadmap_readiness_publication_boundary.json",
            "papers/documentation_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "can be counted multiple times",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "distinct AlphaEvolve requirement",
            },
        ),
        "validation_gate": "owner-reviewed canonical completion publication boundary",
        "readiness_status": "raw_checklist_publication_without_owner_reviewed_rollup",
    },
)


@dataclass(frozen=True)
class TodoCanonicalGapRollupBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class TodoCanonicalGapRollupBoundaryValidation:
    ok: bool
    boundary_status: str | None
    rollup_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[TodoCanonicalGapRollupBoundaryIssue]


def todo_canonical_gap_rollup_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded TODO canonical-gap rollup publication gate."""

    root_path = Path(root)
    source_boundary = todo_canonical_gap_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    missing_evidence_todo_coverage = _missing_evidence_todo_coverage_report(
        records,
        EXPECTED_MISSING_EVIDENCE,
    )
    return {
        "schema": TODO_CANONICAL_GAP_ROLLUP_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_canonical_gap_boundary_input": SOURCE_CANONICAL_GAP_BOUNDARY_INPUT,
        "source_criterion_count": source_boundary["criterion_count"],
        "source_active_todo_ref_count": source_boundary["active_todo_ref_count"],
        "source_sidecar_ref_count": source_boundary["sidecar_ref_count"],
        "source_missing_evidence_count": len(source_boundary["missing_evidence"]),
        "source_canonical_gap_completion_status": source_boundary[
            "canonical_gap_completion_status"
        ],
        "source_exact_stale_completed_duplicate_group_count": source_boundary[
            "exact_stale_completed_duplicate_group_count"
        ],
        "source_exact_stale_completed_duplicate_status": source_boundary[
            "exact_stale_completed_duplicate_status"
        ],
        "source_exact_duplicate_raw_count_inflation_report": source_boundary[
            "exact_duplicate_raw_count_inflation_report"
        ],
        "source_exact_duplicate_record_count": source_boundary[
            "exact_duplicate_record_count"
        ],
        "source_exact_duplicate_inflation_count": source_boundary[
            "exact_duplicate_inflation_count"
        ],
        "source_exact_duplicate_collapsed_total_estimate": source_boundary[
            "exact_duplicate_collapsed_total_estimate"
        ],
        "source_exact_duplicate_owner_status_report": source_boundary[
            "exact_duplicate_owner_status_report"
        ],
        "source_exact_duplicate_cross_owner_group_count": source_boundary[
            "exact_duplicate_cross_owner_group_count"
        ],
        "source_exact_duplicate_completed_only_group_count": source_boundary[
            "exact_duplicate_completed_only_group_count"
        ],
        "source_exact_duplicate_active_involved_group_count": source_boundary[
            "exact_duplicate_active_involved_group_count"
        ],
        "source_exact_same_owner_completed_duplicate_group_count": source_boundary[
            "exact_same_owner_completed_duplicate_group_count"
        ],
        "source_exact_same_owner_completed_duplicate_status": source_boundary[
            "exact_same_owner_completed_duplicate_status"
        ],
        "rollup_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "rollup_criteria": records,
        "missing_evidence_todo_coverage_status": (
            missing_evidence_todo_coverage["coverage_status"]
        ),
        "missing_evidence_todo_coverage_count": (
            missing_evidence_todo_coverage["coverage_count"]
        ),
        "missing_evidence_todo_coverage_records": (
            missing_evidence_todo_coverage["records"]
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a canonical-gap rollup publication gate. It "
            "does not claim canonical gap ids, canonical owner assignments, "
            "derivative documentation relationships, source/paper anchor "
            "mapping, implementation evidence links, cross-document rollup "
            "rules, semantic duplicate detection, canonical owner assignment "
            "readiness beyond the exact duplicate owner/status profile, stale "
            "completed duplicate detection beyond exact normalized-title "
            "matches, same-owner completed duplicate cleanup beyond exact "
            "title matches, orphaned "
            "derivative detection, canonical gap completion "
            "percent, canonical raw-count inflation report beyond exact title "
            "matches, or owner review signoff. It records active TODO coverage "
            "for each missing evidence key without claiming those missing "
            "fields are implemented."
        ),
    }


def validate_todo_canonical_gap_rollup_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> TodoCanonicalGapRollupBoundaryValidation:
    data, read_issues = _load_boundary(
        todo_canonical_gap_rollup_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return TodoCanonicalGapRollupBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = todo_canonical_gap_rollup_boundary_record(root)
    issues: list[TodoCanonicalGapRollupBoundaryIssue] = []
    if data.get("schema") != TODO_CANONICAL_GAP_ROLLUP_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported TODO canonical-gap rollup boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "TODO canonical-gap rollup boundary must not claim canonical completion readiness"))
    for key in (
        "source_canonical_gap_boundary_input",
        "source_criterion_count",
        "source_active_todo_ref_count",
        "source_sidecar_ref_count",
        "source_missing_evidence_count",
        "source_canonical_gap_completion_status",
        "source_exact_stale_completed_duplicate_group_count",
        "source_exact_stale_completed_duplicate_status",
        "source_exact_duplicate_raw_count_inflation_report",
        "source_exact_duplicate_record_count",
        "source_exact_duplicate_inflation_count",
        "source_exact_duplicate_collapsed_total_estimate",
        "source_exact_duplicate_owner_status_report",
        "source_exact_duplicate_cross_owner_group_count",
        "source_exact_duplicate_completed_only_group_count",
        "source_exact_duplicate_active_involved_group_count",
        "source_exact_same_owner_completed_duplicate_group_count",
        "source_exact_same_owner_completed_duplicate_status",
        "rollup_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "rollup_criteria",
        "missing_evidence_todo_coverage_status",
        "missing_evidence_todo_coverage_count",
        "missing_evidence_todo_coverage_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current TODO canonical-gap inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim canonical gap ids" not in boundary_text
        or "exact normalized-title matches" not in boundary_text
        or "canonical gap completion percent" not in boundary_text
        or "owner review signoff" not in boundary_text
        or "active TODO coverage for each missing evidence key" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate raw checklist counts from canonical gap completion"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return TodoCanonicalGapRollupBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        rollup_criterion_count=data.get("rollup_criterion_count") if isinstance(data.get("rollup_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_todo_canonical_gap_rollup_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_todo_canonical_gap_rollup_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "TODO canonical gap rollup boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| rollup_criterion_count | {validation.rollup_criterion_count} |",
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
        "ledger_surface": spec["ledger_surface"],
        "current_scope": spec["current_scope"],
        "missing_rollup": spec["missing_rollup"],
        "sidecar_refs": [_sidecar_ref(root, path) for path in spec["sidecars"]],
        "active_todo_refs": [
            _active_todo_ref(root, todo) for todo in spec["active_todos"]
        ],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _missing_evidence_todo_coverage_report(
    records: list[dict[str, Any]],
    missing_evidence: dict[str, str],
) -> dict[str, Any]:
    todo_refs: dict[tuple[str, str], dict[str, Any]] = {}
    for record in records:
        criterion_id = record["criterion_id"]
        for todo_ref in record["active_todo_refs"]:
            todo_refs[(criterion_id, todo_ref["required_phrase"])] = todo_ref
    coverage_records: list[dict[str, Any]] = []
    for spec in MISSING_EVIDENCE_TODO_COVERAGE_SPECS:
        key = spec["evidence_key"]
        todo_ref = todo_refs.get((spec["criterion_id"], spec["required_phrase"]))
        coverage_records.append(
            {
                "evidence_key": key,
                "missing_evidence_status": missing_evidence.get(key),
                "criterion_id": spec["criterion_id"],
                "todo_path": todo_ref.get("path") if todo_ref else None,
                "required_phrase": spec["required_phrase"],
                "todo_exists": bool(todo_ref and todo_ref["exists"]),
                "required_phrase_present": bool(
                    todo_ref and todo_ref["required_phrase_present"]
                ),
                "coverage_claim": "active_todo_ref_only",
            }
        )
    all_covered = all(
        record["todo_exists"] and record["required_phrase_present"]
        for record in coverage_records
    ) and {
        record["evidence_key"] for record in coverage_records
    } == set(missing_evidence)
    return {
        "coverage_status": (
            "all_missing_evidence_keys_have_active_todo_coverage"
            if all_covered
            else "missing_evidence_key_todo_coverage_incomplete"
        ),
        "coverage_count": len(coverage_records),
        "records": coverage_records,
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
) -> tuple[dict[str, Any] | None, list[TodoCanonicalGapRollupBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "TODO canonical-gap rollup boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[TodoCanonicalGapRollupBoundaryIssue],
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
    issues: list[TodoCanonicalGapRollupBoundaryIssue],
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


def _issue(code: str, message: str) -> TodoCanonicalGapRollupBoundaryIssue:
    return TodoCanonicalGapRollupBoundaryIssue(code=code, message=message)
