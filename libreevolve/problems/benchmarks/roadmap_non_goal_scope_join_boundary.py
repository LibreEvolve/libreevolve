from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.documentation_claim_inventory import (
    documentation_claim_inventory_record,
)
from libreevolve.problems.benchmarks.roadmap_non_goal_contradiction_boundary import (
    roadmap_non_goal_contradiction_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_non_goal_markdown_scan_boundary import (
    roadmap_non_goal_markdown_scan_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_non_goal_plugin_docstring_boundary import (
    roadmap_non_goal_plugin_docstring_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_non_goal_remediation_boundary import (
    roadmap_non_goal_remediation_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_non_goal_runtime_metadata_boundary import (
    roadmap_non_goal_runtime_metadata_boundary_record,
)


ROADMAP_NON_GOAL_SCOPE_JOIN_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_non_goal_scope_join_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "runtime_plugin_docs_paper_scope_join_without_owner_signoff"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stable_non_goal_ids",
    "bounded_documentation_surface_join",
    "markdown_corpus_scan_join",
    "runtime_metadata_scan_join",
    "plugin_docstring_scan_join",
    "paper_sidecar_join",
    "status_ledger_join",
    "remediation_route_join",
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
    "papers/roadmap_non_goal_remediation_boundary.json",
    "papers/documentation_claim_inventory.json",
)
PAPER_README_PATH = "papers/README.md"
STATUS_LEDGER_PATH = "docs/status.md"


@dataclass(frozen=True)
class RoadmapNonGoalScopeJoinBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapNonGoalScopeJoinBoundaryValidation:
    ok: bool
    boundary_status: str | None
    non_goal_join_count: int
    joined_scope_count: int
    missing_join_count: int
    contradiction_count: int
    missing_evidence_count: int
    issues: list[RoadmapNonGoalScopeJoinBoundaryIssue]


def roadmap_non_goal_scope_join_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the joined ROADMAP non-goal runtime/plugin/docs/paper map."""

    root_path = Path(root)
    contradiction = roadmap_non_goal_contradiction_boundary_record(root_path)
    markdown = roadmap_non_goal_markdown_scan_boundary_record(root_path)
    plugin = roadmap_non_goal_plugin_docstring_boundary_record(root_path)
    runtime = roadmap_non_goal_runtime_metadata_boundary_record(root_path)
    remediation = roadmap_non_goal_remediation_boundary_record(root_path)
    docs_inventory = documentation_claim_inventory_record(root_path)
    join_records = [
        _non_goal_join_record(
            root_path,
            non_goal,
            markdown,
            plugin,
            runtime,
            remediation,
            docs_inventory,
        )
        for non_goal in contradiction["non_goal_records"]
    ]
    missing_join_records = [
        missing
        for record in join_records
        for missing in record["missing_join_records"]
    ]
    contradiction_count = sum(
        record["joined_contradiction_count"] for record in join_records
    )
    return {
        "schema": ROADMAP_NON_GOAL_SCOPE_JOIN_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_sidecars": list(EXPECTED_SOURCE_SIDECARS),
        "source_sidecar_records": [
            _source_sidecar_record(root_path, path) for path in EXPECTED_SOURCE_SIDECARS
        ],
        "non_goal_join_count": len(join_records),
        "joined_scope_count": sum(len(record["joined_scopes"]) for record in join_records),
        "missing_join_count": len(missing_join_records),
        "missing_join_records": missing_join_records,
        "contradiction_count": contradiction_count,
        "non_goal_join_records": join_records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary joins the three stable ROADMAP non-goal ids across "
            "bounded documentation surfaces, the full Markdown corpus scan, "
            "runtime metadata source scans, built-in plugin docstring and "
            "registry scans, paper sidecar records, docs/status.md path "
            "references, and remediation-route ownership. It proves the "
            "current joined scope map has zero unresolved contradictions. It "
            "does not claim owner review signoff or a complete future-proof "
            "non-goal lifecycle gate."
        ),
    }


def validate_roadmap_non_goal_scope_join_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapNonGoalScopeJoinBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_non_goal_scope_join_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapNonGoalScopeJoinBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_non_goal_scope_join_boundary_record(root)
    issues: list[RoadmapNonGoalScopeJoinBoundaryIssue] = []
    if data.get("schema") != ROADMAP_NON_GOAL_SCOPE_JOIN_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP non-goal scope join schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "scope join must not claim owner-reviewed lifecycle readiness"))
    for key in (
        "source_sidecars",
        "source_sidecar_records",
        "non_goal_join_count",
        "joined_scope_count",
        "missing_join_count",
        "missing_join_records",
        "contradiction_count",
        "non_goal_join_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current scope-join inputs"))
    if data.get("missing_join_count") != 0:
        issues.append(_issue("missing_scope_join", "every stable non-goal id must join docs, runtime, plugin, paper, status, and remediation evidence"))
    if data.get("contradiction_count") != 0:
        issues.append(_issue("joined_contradiction_detected", "joined scope map contains unresolved contradiction evidence"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "joins the three stable ROADMAP non-goal ids" not in boundary_text
        or "zero unresolved contradictions" not in boundary_text
        or "does not claim owner review signoff" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate joined scope evidence from owner signoff"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapNonGoalScopeJoinBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        non_goal_join_count=data.get("non_goal_join_count") if isinstance(data.get("non_goal_join_count"), int) else 0,
        joined_scope_count=data.get("joined_scope_count") if isinstance(data.get("joined_scope_count"), int) else 0,
        missing_join_count=data.get("missing_join_count") if isinstance(data.get("missing_join_count"), int) else 0,
        contradiction_count=data.get("contradiction_count") if isinstance(data.get("contradiction_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_non_goal_scope_join_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_non_goal_scope_join_boundary(boundary)
    rows = [
        ("schema_status", "ok" if validation.ok else "invalid"),
        ("boundary_status", validation.boundary_status or "unknown"),
        ("non_goal_join_count", str(validation.non_goal_join_count)),
        ("joined_scope_count", str(validation.joined_scope_count)),
        ("missing_join_count", str(validation.missing_join_count)),
        ("contradiction_count", str(validation.contradiction_count)),
        ("missing_evidence_count", str(validation.missing_evidence_count)),
    ]
    lines = ["# ROADMAP non-goal scope join boundary", "", "| Field | Value |", "| --- | --- |"]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    if validation.issues:
        lines.extend(["", "## Issues"])
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in validation.issues)
    return "\n".join(lines) + "\n"


def _non_goal_join_record(
    root_path: Path,
    non_goal: dict[str, Any],
    markdown: dict[str, Any],
    plugin: dict[str, Any],
    runtime: dict[str, Any],
    remediation: dict[str, Any],
    docs_inventory: dict[str, Any],
) -> dict[str, Any]:
    non_goal_id = non_goal["non_goal_id"]
    docs_scope = _docs_scope_record(non_goal)
    markdown_scope = _markdown_scope_record(non_goal_id, markdown)
    plugin_scope = _plugin_scope_record(non_goal_id, plugin)
    runtime_scope = _runtime_scope_record(runtime)
    paper_scope = _paper_scope_record(root_path, non_goal_id)
    status_scope = _status_scope_record(non_goal_id, docs_inventory)
    remediation_scope = _remediation_scope_record(non_goal_id, remediation)
    scopes = {
        "documentation_surfaces": docs_scope,
        "markdown_corpus": markdown_scope,
        "runtime_metadata": runtime_scope,
        "plugin_docstrings": plugin_scope,
        "paper_sidecars": paper_scope,
        "status_ledger": status_scope,
        "remediation_routes": remediation_scope,
    }
    missing = [
        {
            "non_goal_id": non_goal_id,
            "scope": scope_id,
            "status": scope["join_status"],
        }
        for scope_id, scope in scopes.items()
        if scope["join_status"] != "joined"
    ]
    contradiction_count = (
        docs_scope["contradiction_count"]
        + markdown_scope["contradiction_count"]
        + plugin_scope["contradiction_count"]
        + runtime_scope["contradiction_count"]
        + remediation_scope["contradiction_count"]
    )
    return {
        "non_goal_id": non_goal_id,
        "roadmap_anchor": non_goal["roadmap_anchor"],
        "joined_scopes": scopes,
        "join_status": "joined_without_owner_signoff" if not missing and contradiction_count == 0 else "join_incomplete",
        "missing_join_records": missing,
        "joined_contradiction_count": contradiction_count,
    }


def _docs_scope_record(non_goal: dict[str, Any]) -> dict[str, Any]:
    surfaces = non_goal["constrained_surfaces"]
    missing_safe = [
        {
            "path": surface["path"],
            "required_safe_phrase": surface["required_safe_phrase"],
        }
        for surface in surfaces
        if not surface["required_safe_phrase_present"]
    ]
    contradiction_count = sum(
        len(surface["detected_forbidden_claims"]) for surface in surfaces
    )
    return {
        "join_status": "joined" if not missing_safe and contradiction_count == 0 else "missing_documentation_surface_evidence",
        "source": "papers/roadmap_non_goal_contradiction_boundary.json",
        "surface_paths": [surface["path"] for surface in surfaces],
        "surface_count": len(surfaces),
        "missing_safe_phrase_records": missing_safe,
        "contradiction_count": contradiction_count,
    }


def _markdown_scope_record(non_goal_id: str, markdown: dict[str, Any]) -> dict[str, Any]:
    record = _record_by_id(markdown["non_goal_records"], "non_goal_id", non_goal_id)
    contradiction_count = len(record.get("detected_forbidden_claim_records", [])) if record else 1
    return {
        "join_status": "joined" if record and contradiction_count == 0 else "missing_markdown_scan_evidence",
        "source": "papers/roadmap_non_goal_markdown_scan_boundary.json",
        "markdown_file_count": markdown["markdown_file_count"],
        "forbidden_phrase_count": len(record.get("forbidden_claim_phrases", [])) if record else 0,
        "contradiction_count": contradiction_count,
    }


def _plugin_scope_record(non_goal_id: str, plugin: dict[str, Any]) -> dict[str, Any]:
    relevance = (
        "direct_paper_inspired_plugin_guard"
        if non_goal_id == "paper_inspired_plugins_not_faithful_implementations"
        else "global_plugin_overclaim_guard"
    )
    contradiction_count = plugin["faithful_overclaim_count"] + plugin["missing_disclaimer_count"]
    return {
        "join_status": "joined" if contradiction_count == 0 else "plugin_scope_contradiction_detected",
        "source": "papers/roadmap_non_goal_plugin_docstring_boundary.json",
        "relevance": relevance,
        "plugin_source_file_count": plugin["plugin_source_file_count"],
        "builtin_plugin_count": plugin["builtin_plugin_count"],
        "paper_inspired_builtin_plugin_count": plugin["paper_inspired_builtin_plugin_count"],
        "contradiction_count": contradiction_count,
    }


def _runtime_scope_record(runtime: dict[str, Any]) -> dict[str, Any]:
    contradiction_count = runtime["contradiction_count"] + runtime["safe_phrase_missing_count"]
    return {
        "join_status": "joined" if contradiction_count == 0 else "runtime_scope_contradiction_detected",
        "source": "papers/roadmap_non_goal_runtime_metadata_boundary.json",
        "runtime_surface_count": runtime["runtime_surface_count"],
        "runtime_metadata_path_count": runtime["runtime_metadata_path_count"],
        "builtin_plugin_registry_count": runtime["builtin_plugin_registry_count"],
        "contradiction_count": contradiction_count,
    }


def _paper_scope_record(root_path: Path, non_goal_id: str) -> dict[str, Any]:
    readme_text = _read_text(root_path / PAPER_README_PATH)
    required_refs = [
        "papers/roadmap_non_goal_contradiction_boundary.json",
        "papers/roadmap_non_goal_markdown_scan_boundary.json",
        "papers/roadmap_non_goal_plugin_docstring_boundary.json",
        "papers/roadmap_non_goal_runtime_metadata_boundary.json",
        "papers/roadmap_non_goal_remediation_boundary.json",
    ]
    ref_records = [_source_sidecar_record(root_path, path) for path in required_refs]
    all_refs_present = all(record["exists"] for record in ref_records)
    paper_readme_refs_present = all(path in readme_text for path in required_refs)
    return {
        "join_status": "joined" if all_refs_present and paper_readme_refs_present else "missing_paper_sidecar_join",
        "source": PAPER_README_PATH,
        "non_goal_id": non_goal_id,
        "required_sidecar_refs": required_refs,
        "required_sidecar_ref_records": ref_records,
        "paper_readme_refs_present": paper_readme_refs_present,
    }


def _status_scope_record(non_goal_id: str, docs_inventory: dict[str, Any]) -> dict[str, Any]:
    required_refs = set(EXPECTED_SOURCE_SIDECARS)
    status_refs = set(docs_inventory.get("status_ledger_unique_local_path_refs", []))
    missing = sorted(required_refs - status_refs)
    return {
        "join_status": "joined" if not missing else "missing_status_ledger_refs",
        "source": STATUS_LEDGER_PATH,
        "non_goal_id": non_goal_id,
        "required_status_refs": sorted(required_refs),
        "missing_status_refs": missing,
    }


def _remediation_scope_record(non_goal_id: str, remediation: dict[str, Any]) -> dict[str, Any]:
    record = _record_by_id(remediation["remediation_route_records"], "route_id", non_goal_id)
    contradiction_count = 0 if record and record["owner_todo_required_phrase_present"] else 1
    return {
        "join_status": "joined" if record and contradiction_count == 0 else "missing_remediation_route",
        "source": "papers/roadmap_non_goal_remediation_boundary.json",
        "owner_todo_path": record.get("owner_todo_path") if record else None,
        "claim_update_surfaces": record.get("claim_update_surfaces", []) if record else [],
        "contradiction_count": contradiction_count,
    }


def _source_sidecar_record(root_path: Path, path: str) -> dict[str, Any]:
    return {
        "path": path,
        "exists": (root_path / path).is_file(),
    }


def _record_by_id(
    records: list[dict[str, Any]],
    id_key: str,
    record_id: str,
) -> dict[str, Any] | None:
    for record in records:
        if record.get(id_key) == record_id:
            return record
    return None


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapNonGoalScopeJoinBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP non-goal scope join boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapNonGoalScopeJoinBoundaryIssue],
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
    issues: list[RoadmapNonGoalScopeJoinBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapNonGoalScopeJoinBoundaryIssue:
    return RoadmapNonGoalScopeJoinBoundaryIssue(code, message)
