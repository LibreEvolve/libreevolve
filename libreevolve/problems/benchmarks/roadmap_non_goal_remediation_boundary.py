from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_non_goal_contradiction_boundary import (
    roadmap_non_goal_contradiction_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_non_goal_markdown_scan_boundary import (
    roadmap_non_goal_markdown_scan_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_non_goal_plugin_docstring_boundary import (
    roadmap_non_goal_plugin_docstring_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_non_goal_runtime_metadata_boundary import (
    roadmap_non_goal_runtime_metadata_boundary_record,
)


ROADMAP_NON_GOAL_REMEDIATION_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_non_goal_remediation_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "contradiction_remediation_report_with_scope_join_without_signoff"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "bounded_contradiction_inventory",
    "markdown_corpus_contradiction_scan",
    "plugin_docstring_overclaim_scan",
    "runtime_metadata_contradiction_scan",
    "future_hit_todo_routing",
    "claim_update_routing",
    "runtime_plugin_scope_join",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_SOURCE_SIDECARS = (
    "papers/roadmap_non_goal_contradiction_boundary.json",
    "papers/roadmap_non_goal_markdown_scan_boundary.json",
    "papers/roadmap_non_goal_plugin_docstring_boundary.json",
    "papers/roadmap_non_goal_runtime_metadata_boundary.json",
    "papers/roadmap_non_goal_scope_join_boundary.json",
)
REMEDIATION_ROUTE_SPECS = (
    {
        "route_id": "normal_local_use_no_service_database_required",
        "owner_todo_path": "docs/todo/roadmap.md",
        "owner_todo_required_phrase": "contradiction-remediation report",
        "claim_update_surfaces": ("ROADMAP.md", "README.md", "docs/status.md"),
    },
    {
        "route_id": "no_arbitrary_language_codebase_support_before_runners",
        "owner_todo_path": "docs/todo/readme.md",
        "owner_todo_required_phrase": "implementation-evidence mapping",
        "claim_update_surfaces": ("README.md", "docs/run-artifacts.md", "docs/status.md"),
    },
    {
        "route_id": "paper_inspired_plugins_not_faithful_implementations",
        "owner_todo_path": "docs/todo/papers.md",
        "owner_todo_required_phrase": "paper-facing classification",
        "claim_update_surfaces": ("README.md", "docs/architecture.md", "docs/status.md", "papers/README.md"),
    },
)


@dataclass(frozen=True)
class RoadmapNonGoalRemediationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapNonGoalRemediationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    source_scan_count: int
    unresolved_contradiction_count: int
    remediation_route_count: int
    missing_evidence_count: int
    issues: list[RoadmapNonGoalRemediationBoundaryIssue]


def roadmap_non_goal_remediation_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the ROADMAP non-goal contradiction remediation report."""

    root_path = Path(root)
    contradiction = roadmap_non_goal_contradiction_boundary_record(root_path)
    markdown = roadmap_non_goal_markdown_scan_boundary_record(root_path)
    plugin = roadmap_non_goal_plugin_docstring_boundary_record(root_path)
    runtime = roadmap_non_goal_runtime_metadata_boundary_record(root_path)
    source_scans = (
        {
            "scan_id": "bounded_documentation_inventory",
            "sidecar": EXPECTED_SOURCE_SIDECARS[0],
            "contradiction_count": contradiction["contradiction_count"],
            "unresolved_record_count": contradiction["contradiction_count"],
        },
        {
            "scan_id": "markdown_corpus_scan",
            "sidecar": EXPECTED_SOURCE_SIDECARS[1],
            "contradiction_count": markdown["contradiction_count"],
            "unresolved_record_count": markdown["contradiction_count"],
        },
        {
            "scan_id": "plugin_docstring_scan",
            "sidecar": EXPECTED_SOURCE_SIDECARS[2],
            "contradiction_count": plugin["faithful_overclaim_count"],
            "unresolved_record_count": plugin["faithful_overclaim_count"],
        },
        {
            "scan_id": "runtime_metadata_scan",
            "sidecar": EXPECTED_SOURCE_SIDECARS[3],
            "contradiction_count": runtime["contradiction_count"],
            "unresolved_record_count": runtime["contradiction_count"],
        },
        {
            "scan_id": "runtime_plugin_docs_paper_scope_join",
            "sidecar": EXPECTED_SOURCE_SIDECARS[4],
            "contradiction_count": 0,
            "unresolved_record_count": 0,
        },
    )
    unresolved_count = sum(record["unresolved_record_count"] for record in source_scans)
    route_records = [_remediation_route_record(root_path, spec) for spec in REMEDIATION_ROUTE_SPECS]
    return {
        "schema": ROADMAP_NON_GOAL_REMEDIATION_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_sidecars": list(EXPECTED_SOURCE_SIDECARS),
        "source_scan_count": len(source_scans),
        "source_scan_records": list(source_scans),
        "unresolved_contradiction_count": unresolved_count,
        "remediation_route_count": len(route_records),
        "remediation_route_records": route_records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a non-goal contradiction-remediation report "
            "over the bounded documentation inventory, Markdown corpus scan, "
            "plugin docstring scan, and runtime metadata scan. It rejects "
            "contradictory support claims by requiring zero unresolved hits and "
            "routes any future hit to TODO ownership and claim-update surfaces. "
            "The joined runtime/plugin/docs/paper scope proof is recorded "
            "separately. It does not claim owner review signoff."
        ),
    }


def validate_roadmap_non_goal_remediation_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapNonGoalRemediationBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_non_goal_remediation_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapNonGoalRemediationBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_non_goal_remediation_boundary_record(root)
    issues: list[RoadmapNonGoalRemediationBoundaryIssue] = []
    if data.get("schema") != ROADMAP_NON_GOAL_REMEDIATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP non-goal remediation boundary schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "remediation boundary must not claim full lifecycle readiness"))
    for key in (
        "source_sidecars",
        "source_scan_count",
        "source_scan_records",
        "unresolved_contradiction_count",
        "remediation_route_count",
        "remediation_route_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current remediation inputs"))
    if data.get("unresolved_contradiction_count") != 0:
        issues.append(_issue("unresolved_contradiction_detected", "non-goal contradictions must be remediated before readiness can advance"))
    _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "contradiction-remediation report" not in boundary_text
        or "requiring zero unresolved hits" not in boundary_text
        or "routes any future hit to TODO ownership" not in boundary_text
        or "joined runtime/plugin/docs/paper scope proof is recorded separately" not in boundary_text
        or "does not claim owner review signoff" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate remediation routing from scope join and owner signoff"))
    return RoadmapNonGoalRemediationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        source_scan_count=data.get("source_scan_count") if isinstance(data.get("source_scan_count"), int) else 0,
        unresolved_contradiction_count=data.get("unresolved_contradiction_count") if isinstance(data.get("unresolved_contradiction_count"), int) else 0,
        remediation_route_count=data.get("remediation_route_count") if isinstance(data.get("remediation_route_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_non_goal_remediation_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_non_goal_remediation_boundary(boundary)
    rows = [
        ("schema_status", "ok" if validation.ok else "invalid"),
        ("boundary_status", validation.boundary_status or "unknown"),
        ("source_scan_count", str(validation.source_scan_count)),
        ("unresolved_contradiction_count", str(validation.unresolved_contradiction_count)),
        ("remediation_route_count", str(validation.remediation_route_count)),
        ("missing_evidence_count", str(validation.missing_evidence_count)),
    ]
    lines = ["# ROADMAP non-goal remediation boundary", "", "| Field | Value |", "| --- | --- |"]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    if validation.issues:
        lines.extend(["", "## Issues"])
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in validation.issues)
    return "\n".join(lines) + "\n"


def _remediation_route_record(root_path: Path, spec: dict[str, Any]) -> dict[str, Any]:
    todo_path = root_path / spec["owner_todo_path"]
    todo_text = _read_text(todo_path)
    return {
        "route_id": spec["route_id"],
        "owner_todo_path": spec["owner_todo_path"],
        "owner_todo_exists": todo_path.is_file(),
        "owner_todo_required_phrase": spec["owner_todo_required_phrase"],
        "owner_todo_required_phrase_present": spec["owner_todo_required_phrase"] in todo_text,
        "claim_update_surfaces": list(spec["claim_update_surfaces"]),
    }


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapNonGoalRemediationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP non-goal remediation boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapNonGoalRemediationBoundaryIssue],
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
    issues: list[RoadmapNonGoalRemediationBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    if expected_keys - actual_keys:
        issues.append(_issue("missing_missing_evidence_key", "missing_evidence lacks expected keys"))
    if actual_keys - expected_keys:
        issues.append(_issue("extra_missing_evidence_key", "missing_evidence includes unknown keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _issue(code: str, message: str) -> RoadmapNonGoalRemediationBoundaryIssue:
    return RoadmapNonGoalRemediationBoundaryIssue(code, message)
