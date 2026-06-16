from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_DOCUMENTATION_MAP_BOUNDARY_SCHEMA = (
    "libreevolve.readme_documentation_map_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "readme_documentation_map_routes_recorded_without_semantic_purpose_verifier"
)
README_PATH = "README.md"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_documentation_map_route_inventory",
    "route_target_existence_checks",
    "route_summary_marker_checks",
    "target_heading_marker_checks",
    "docs_index_delegation_record",
    "archival_old_route_record",
    "agent_contract_route_record",
    "route_purpose_semantic_verifier",
    "new_major_doc_detector",
    "misplaced_claim_detector",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "route_purpose_semantic_verifier": "not_recorded_locally",
    "new_major_doc_detector": "not_recorded_locally",
    "misplaced_claim_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_ROUTES = (
    {
        "route_id": "docs_index",
        "link_text": "docs/README.md",
        "target_path": "docs/README.md",
        "readme_markers": ("reader paths and documentation boundaries",),
        "target_markers": ("# Documentation", "## Reader Paths", "## Documentation Boundaries"),
        "route_scope": "docs_index_delegation",
    },
    {
        "route_id": "architecture",
        "link_text": "docs/architecture.md",
        "target_path": "docs/architecture.md",
        "readme_markers": ("runtime architecture",),
        "target_markers": ("# Architecture",),
        "route_scope": "operational_guide",
    },
    {
        "route_id": "configuration",
        "link_text": "docs/configuration.md",
        "target_path": "docs/configuration.md",
        "readme_markers": ("config fields and CLI",),
        "target_markers": ("# Configuration",),
        "route_scope": "operational_guide",
    },
    {
        "route_id": "backends",
        "link_text": "docs/backends.md",
        "target_path": "docs/backends.md",
        "readme_markers": ("provider adapters and custom backends",),
        "target_markers": ("# Backends",),
        "route_scope": "operational_guide",
    },
    {
        "route_id": "plugins",
        "link_text": "docs/plugins.md",
        "target_path": "docs/plugins.md",
        "readme_markers": ("plugin hooks and built-in plugins",),
        "target_markers": ("# Plugins",),
        "route_scope": "operational_guide",
    },
    {
        "route_id": "run_artifacts",
        "link_text": "docs/run-artifacts.md",
        "target_path": "docs/run-artifacts.md",
        "readme_markers": ("files written under `runs/`",),
        "target_markers": ("# Run Artifacts",),
        "route_scope": "operational_guide",
    },
    {
        "route_id": "status",
        "link_text": "docs/status.md",
        "target_path": "docs/status.md",
        "readme_markers": ("detailed implementation and absence ledger",),
        "target_markers": ("# Current Implementation Status",),
        "route_scope": "status_ledger",
    },
    {
        "route_id": "roadmap",
        "link_text": "ROADMAP.md",
        "target_path": "ROADMAP.md",
        "readme_markers": ("practical implementation priorities",),
        "target_markers": ("# Roadmap",),
        "route_scope": "planning_priority",
    },
    {
        "route_id": "papers_index",
        "link_text": "papers/README.md",
        "target_path": "papers/README.md",
        "readme_markers": ("paper cache, status rows, and claim",),
        "target_markers": ("# Local Paper Cache", "## Implementation status"),
        "route_scope": "paper_boundary_evidence",
    },
    {
        "route_id": "todo_ledgers",
        "link_text": "docs/todo/",
        "target_path": "docs/todo",
        "readme_markers": ("active and completed gap ledgers",),
        "target_markers": (),
        "route_scope": "todo_gap_ledgers",
    },
    {
        "route_id": "agents_contract",
        "link_text": "AGENTS.md",
        "target_path": "AGENTS.md",
        "readme_markers": ("agent-facing operating contract",),
        "target_markers": ("# AGENTS.md",),
        "route_scope": "agent_contract",
    },
)


@dataclass(frozen=True)
class ReadmeDocumentationMapBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeDocumentationMapBoundaryValidation:
    ok: bool
    boundary_status: str | None
    route_record_count: int
    missing_route_record_count: int
    missing_evidence_count: int
    issues: list[ReadmeDocumentationMapBoundaryIssue]


def readme_documentation_map_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded README Documentation Map routing record."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    route_records = [
        _route_record(root_path, readme_text, route)
        for route in EXPECTED_ROUTES
    ]
    missing_route_records = [
        record
        for record in route_records
        if record["route_status"] != "route_target_and_markers_present"
    ]
    route_scopes = sorted({record["route_scope"] for record in route_records})
    return {
        "schema": README_DOCUMENTATION_MAP_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "route_record_count": len(route_records),
        "missing_route_record_count": len(missing_route_records),
        "missing_route_records": missing_route_records,
        "route_records": route_records,
        "route_scopes": route_scopes,
        "docs_index_delegation_status": _route_status(route_records, "docs_index"),
        "archival_old_route_status": (
            "archival_route_present"
            if "`old/` is archival" in readme_text
            or "old/` is archival" in readme_text
            else "archival_route_missing"
        ),
        "agent_contract_route_status": _route_status(route_records, "agents_contract"),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README Documentation Map route inventory, "
            "route target existence checks, route summary marker checks, target "
            "heading marker checks, docs-index delegation, archival old/ routing, "
            "and AGENTS.md operating-contract routing. It does not claim semantic "
            "route-purpose verification, detection of newly added major docs, "
            "misplaced-claim detection, or owner review signoff."
        ),
    }


def validate_readme_documentation_map_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeDocumentationMapBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_documentation_map_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeDocumentationMapBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_documentation_map_boundary_record(root)
    issues: list[ReadmeDocumentationMapBoundaryIssue] = []
    if data.get("schema") != README_DOCUMENTATION_MAP_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README Documentation Map boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README Documentation Map boundary must not claim semantic routing proof"))
    for key in (
        "readme_path",
        "route_record_count",
        "missing_route_record_count",
        "missing_route_records",
        "route_records",
        "route_scopes",
        "docs_index_delegation_status",
        "archival_old_route_status",
        "agent_contract_route_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current README Documentation Map inputs"))
    if data.get("missing_route_record_count") != 0:
        issues.append(_issue("missing_documentation_map_route", "README Documentation Map routes must have targets and configured markers"))
    if data.get("docs_index_delegation_status") != "route_target_and_markers_present":
        issues.append(_issue("invalid_docs_index_delegation_status", "docs/README.md route must be present"))
    if data.get("archival_old_route_status") != "archival_route_present":
        issues.append(_issue("invalid_archival_old_route_status", "README must preserve old/ archival routing"))
    if data.get("agent_contract_route_status") != "route_target_and_markers_present":
        issues.append(_issue("invalid_agent_contract_route_status", "README must preserve AGENTS.md routing"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README Documentation Map route inventory" not in boundary_text
        or "route target existence checks" not in boundary_text
        or "docs-index delegation" not in boundary_text
        or "does not claim semantic route-purpose verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate route inventory from semantic routing proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmeDocumentationMapBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        route_record_count=data.get("route_record_count") if isinstance(data.get("route_record_count"), int) else 0,
        missing_route_record_count=data.get("missing_route_record_count") if isinstance(data.get("missing_route_record_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_documentation_map_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_documentation_map_boundary(boundary)
    lines = [
        "README Documentation Map boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| route_record_count | {validation.route_record_count} |",
        f"| missing_route_record_count | {validation.missing_route_record_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _route_record(root: Path, readme_text: str, route: dict[str, Any]) -> dict[str, Any]:
    target_path = str(route["target_path"])
    target = root / target_path
    target_text = _read_text(target)
    readme_markers = tuple(route["readme_markers"])
    target_markers = tuple(route["target_markers"])
    link_markers = (
        f"[{route['link_text']}]({target_path})",
        f"[{route['link_text']}]({target_path}/)",
    )
    link_present = any(marker in readme_text for marker in link_markers)
    readme_missing = [marker for marker in readme_markers if marker not in readme_text]
    target_missing = [marker for marker in target_markers if marker not in target_text]
    target_exists = target.exists()
    route_status = (
        "route_target_and_markers_present"
        if link_present and target_exists and not readme_missing and not target_missing
        else "route_target_or_markers_missing"
    )
    return {
        "route_id": route["route_id"],
        "route_scope": route["route_scope"],
        "link_text": route["link_text"],
        "target_path": target_path,
        "target_exists": target_exists,
        "readme_link_present": link_present,
        "readme_missing_markers": readme_missing,
        "target_missing_markers": target_missing,
        "route_status": route_status,
    }


def _route_status(route_records: list[dict[str, Any]], route_id: str) -> str:
    for record in route_records:
        if record["route_id"] == route_id:
            return str(record["route_status"])
    return "route_missing"


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ReadmeDocumentationMapBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README Documentation Map boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeDocumentationMapBoundaryIssue],
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
    issues: list[ReadmeDocumentationMapBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeDocumentationMapBoundaryIssue:
    return ReadmeDocumentationMapBoundaryIssue(code, message)
