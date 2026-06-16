from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_GOOD_FIRST_FOLLOWUPS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_good_first_followups_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = "bounded_good_first_followups_priority_map_without_freshness_gate"
EXPECTED_ROADMAP_SECTION = "## Good First Follow-Ups"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "roadmap_priority_items",
    "active_todo_refs",
    "priority_rationale",
    "dependency_readiness_labels",
    "validation_gate_refs",
    "alphaevolve_impact_labels",
    "dependency_state_refresh",
    "stale_priority_detector",
    "priority_score_model",
    "ci_priority_freshness_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "owner_review_signoff": "not_recorded_locally",
}


GOOD_FIRST_FOLLOWUP_SPECS = (
    {
        "item_id": "durable_query_indexes",
        "ordinal": 1,
        "roadmap_required_phrase": "Persist database query indexes beyond run-local",
        "priority_rationale": (
            "Query surfaces are a small, bounded step from existing run-local "
            "resurfacing indexes toward AlphaEvolve-style database inspection."
        ),
        "dependency_readiness": "has_run_local_indexes_needs_durable_tables",
        "alphaevolve_impact": "program_database_resurfacing",
        "todo_refs": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": (
                    "Replace bounded run-local resurfacing indexes with a durable "
                    "evolutionary database"
                ),
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "add durable query/report surfaces over every candidate",
            },
        ),
        "validation_gates": (
            "durable database/query index tests",
            "run-artifact query/report sidecar",
            "paper-manifest validation",
        ),
    },
    {
        "item_id": "non_toy_benchmark_fixture",
        "ordinal": 2,
        "roadmap_required_phrase": "Add one non-toy benchmark run fixture",
        "priority_rationale": (
            "A bounded benchmark fixture can convert existing executable "
            "scaffolding into repeatable AlphaEvolve-style evidence."
        ),
        "dependency_readiness": "sorting_network_candidates_exist_needs_run_evidence",
        "alphaevolve_impact": "representative_benchmark_reproduction",
        "todo_refs": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add a rigorous sorting-network rediscovery benchmark fixture",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": (
                    "Add paper-facing sorting-network rediscovery evidence as a "
                    "realistic"
                ),
            },
        ),
        "validation_gates": (
            "repeated-seed run reports",
            "target-hit-rate summaries",
            "benchmark hardening certification",
        ),
    },
    {
        "item_id": "workspace_resume_coverage",
        "ordinal": 3,
        "roadmap_required_phrase": (
            "Add workspace resume coverage beyond current `best_workspace/` export"
        ),
        "priority_rationale": (
            "Resume coverage builds from current archive snapshots and best "
            "workspace export toward auditable long-running experiments."
        ),
        "dependency_readiness": "archive_restore_exists_needs_full_workspace_resume_contract",
        "alphaevolve_impact": "resumable_evolutionary_database",
        "todo_refs": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Replay archive event logs as an ordered migration restore engine",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add async/pending-work controller resume state",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "`best_workspace/`, `evaluator_artifacts/`, or `plugin_artifacts/`",
            },
        ),
        "validation_gates": (
            "archive event replay restore tests",
            "pending-work resume tests",
            "workspace artifact integrity report",
        ),
    },
    {
        "item_id": "feedback_calibration_reports",
        "ordinal": 4,
        "roadmap_required_phrase": "Emit real LLM feedback calibration reports",
        "priority_rationale": (
            "The report schema already exists, so the next useful step is an "
            "executed calibration fixture rather than more schema-only proof."
        ),
        "dependency_readiness": "report_contract_exists_needs_runtime_runner",
        "alphaevolve_impact": "multi_score_feedback_quality",
        "todo_refs": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "emit real LLM feedback calibration reports",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "No runtime feedback-calibration fixture emits",
            },
        ),
        "validation_gates": (
            "runtime feedback-calibration fixture",
            "grader ablation outputs",
            "feedback-calibration artifact inventory",
        ),
    },
)


@dataclass(frozen=True)
class RoadmapGoodFirstFollowupsBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapGoodFirstFollowupsBoundaryValidation:
    ok: bool
    boundary_status: str | None
    priority_item_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapGoodFirstFollowupsBoundaryIssue]


def roadmap_good_first_followups_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP Good First Follow-Ups priority map."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    priority_records = [
        _priority_record(root_path, roadmap_text, spec)
        for spec in GOOD_FIRST_FOLLOWUP_SPECS
    ]
    active_todo_ref_count = sum(
        len(record["active_todo_refs"]) for record in priority_records
    )
    return {
        "schema": ROADMAP_GOOD_FIRST_FOLLOWUPS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "roadmap_section": EXPECTED_ROADMAP_SECTION,
        "roadmap_section_present": _contains_phrase(roadmap_text, EXPECTED_ROADMAP_SECTION),
        "priority_item_count": len(priority_records),
        "active_todo_ref_count": active_todo_ref_count,
        "priority_records": priority_records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the four current ROADMAP Good First "
            "Follow-Ups, links each to active TODO evidence, dependency "
            "readiness labels, validation gates, and AlphaEvolve impact labels. "
            "Dependency-state refresh, stale-priority detection, priority "
            "scoring, and CI priority freshness gating are recorded "
            "separately. It does not claim owner review signoff."
        ),
    }


def validate_roadmap_good_first_followups_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapGoodFirstFollowupsBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_good_first_followups_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapGoodFirstFollowupsBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_good_first_followups_boundary_record(root)
    issues: list[RoadmapGoodFirstFollowupsBoundaryIssue] = []
    if data.get("schema") != ROADMAP_GOOD_FIRST_FOLLOWUPS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP good-first boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP good-first boundary must not claim priority freshness readiness"))
    for key in (
        "roadmap_section",
        "roadmap_section_present",
        "priority_item_count",
        "active_todo_ref_count",
        "priority_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP/TODO inputs"))
    if data.get("roadmap_section_present") is not True:
        issues.append(_issue("missing_roadmap_section", "Good First Follow-Ups section was not found"))
    if data.get("priority_item_count") != len(GOOD_FIRST_FOLLOWUP_SPECS):
        issues.append(_issue("invalid_priority_item_count", "priority item count changed"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "CI priority freshness gating are recorded separately" not in boundary_text
        or "does not claim owner review signoff" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded priority map from freshness automation"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapGoodFirstFollowupsBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        priority_item_count=data.get("priority_item_count") if isinstance(data.get("priority_item_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_good_first_followups_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_good_first_followups_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP Good First Follow-Ups boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| priority_item_count | {validation.priority_item_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _priority_record(
    root: Path,
    roadmap_text: str,
    spec: dict[str, Any],
) -> dict[str, Any]:
    todo_refs = [
        _todo_ref_record(root, todo_ref)
        for todo_ref in spec["todo_refs"]
    ]
    return {
        "item_id": spec["item_id"],
        "ordinal": spec["ordinal"],
        "roadmap_required_phrase": spec["roadmap_required_phrase"],
        "roadmap_phrase_present": _contains_phrase(
            roadmap_text,
            spec["roadmap_required_phrase"],
        ),
        "priority_rationale": spec["priority_rationale"],
        "dependency_readiness": spec["dependency_readiness"],
        "alphaevolve_impact": spec["alphaevolve_impact"],
        "active_todo_refs": todo_refs,
        "active_todo_ref_count": len(todo_refs),
        "validation_gates": list(spec["validation_gates"]),
        "freshness_status": "bounded_static_map_no_stale_priority_detector",
    }


def _todo_ref_record(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": spec["required_phrase"],
        "required_phrase_present": _contains_phrase(text, spec["required_phrase"]),
        "active_marker_present": "- [ ]" in text,
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
) -> tuple[dict[str, Any] | None, list[RoadmapGoodFirstFollowupsBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP good-first boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapGoodFirstFollowupsBoundaryIssue],
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
    issues: list[RoadmapGoodFirstFollowupsBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapGoodFirstFollowupsBoundaryIssue:
    return RoadmapGoodFirstFollowupsBoundaryIssue(code=code, message=message)
