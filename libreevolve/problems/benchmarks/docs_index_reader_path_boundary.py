from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DOCS_INDEX_READER_PATH_BOUNDARY_SCHEMA = "libreevolve.docs_index_reader_path_boundary.v1"
EXPECTED_BOUNDARY_STATUS = "docs_index_routes_recorded_without_semantic_scope_verifier"
DOCS_README_PATH = "docs/README.md"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "docs_index_reader_path_inventory",
    "docs_index_operational_guide_inventory",
    "docs_index_boundary_marker_inventory",
    "route_target_existence_checks",
    "target_heading_marker_checks",
    "whole_documentation_cleanup_marker",
    "route_purpose_semantic_verifier",
    "target_scope_agreement_verifier",
    "new_major_doc_detector",
    "misplaced_claim_detector",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "route_purpose_semantic_verifier": "not_recorded_locally",
    "target_scope_agreement_verifier": "not_recorded_locally",
    "new_major_doc_detector": "not_recorded_locally",
    "misplaced_claim_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_ROUTES = (
    {
        "route_id": "root_readme_entry",
        "route_group": "intro",
        "link_marker": "[README](../README.md)",
        "target_path": "README.md",
        "target_markers": ("# LibreEvolve", "## Requirements", "## Documentation Map"),
    },
    {
        "route_id": "new_user_problem_format",
        "route_group": "reader_path",
        "link_marker": "[Problem Format](./problem-format.md)",
        "target_path": "docs/problem-format.md",
        "target_markers": ("# Problem Format",),
    },
    {
        "route_id": "operator_run_artifacts",
        "route_group": "reader_path",
        "link_marker": "[Run Artifacts](./run-artifacts.md)",
        "target_path": "docs/run-artifacts.md",
        "target_markers": ("# Run Artifacts",),
    },
    {
        "route_id": "operator_configuration",
        "route_group": "reader_path",
        "link_marker": "[Configuration](./configuration.md)",
        "target_path": "docs/configuration.md",
        "target_markers": ("# Configuration",),
    },
    {
        "route_id": "operator_backends",
        "route_group": "reader_path",
        "link_marker": "[Backends](./backends.md)",
        "target_path": "docs/backends.md",
        "target_markers": ("# Backends",),
    },
    {
        "route_id": "contributor_development",
        "route_group": "reader_path",
        "link_marker": "[Development](./development.md)",
        "target_path": "docs/development.md",
        "target_markers": ("# Development",),
    },
    {
        "route_id": "contributor_todo",
        "route_group": "reader_path",
        "link_marker": "[todo](./todo/)",
        "target_path": "docs/todo",
        "target_markers": (),
    },
    {
        "route_id": "contributor_agents",
        "route_group": "reader_path",
        "link_marker": "[AGENTS.md](../AGENTS.md)",
        "target_path": "AGENTS.md",
        "target_markers": ("# AGENTS.md",),
    },
    {
        "route_id": "paper_reviewer_status",
        "route_group": "reader_path",
        "link_marker": "[Current Status](./status.md)",
        "target_path": "docs/status.md",
        "target_markers": ("# Current Implementation Status",),
    },
    {
        "route_id": "paper_reviewer_roadmap",
        "route_group": "reader_path",
        "link_marker": "[ROADMAP](../ROADMAP.md)",
        "target_path": "ROADMAP.md",
        "target_markers": ("# Roadmap",),
    },
    {
        "route_id": "paper_reviewer_papers",
        "route_group": "reader_path",
        "link_marker": "[papers/README.md](../papers/README.md)",
        "target_path": "papers/README.md",
        "target_markers": ("# Local Paper Cache", "## Implementation status"),
    },
    {
        "route_id": "guide_architecture",
        "route_group": "operational_guide",
        "link_marker": "[Architecture](./architecture.md)",
        "target_path": "docs/architecture.md",
        "target_markers": ("# Architecture",),
    },
    {
        "route_id": "guide_plugins",
        "route_group": "operational_guide",
        "link_marker": "[Plugins](./plugins.md)",
        "target_path": "docs/plugins.md",
        "target_markers": ("# Plugins",),
    },
    {
        "route_id": "guide_paper_cache",
        "route_group": "operational_guide",
        "link_marker": "[Paper Cache](../papers/README.md)",
        "target_path": "papers/README.md",
        "target_markers": ("# Local Paper Cache",),
    },
)
EXPECTED_BOUNDARY_MARKERS = (
    "The root README should stay short enough to be useful on a first read.",
    "Detailed runtime behavior belongs in the operational guides above.",
    "The full implementation and absence-boundary ledger belongs in",
    "Long-term status belongs in `ROADMAP.md` and `docs/todo/`.",
    "Paper-derived claims belong in `papers/README.md` and validated JSON sidecars.",
    "Tracked material under `old/` is archival and non-authoritative.",
    "AlphaEvolve-alignment cleanup is a whole-documentation task.",
)


@dataclass(frozen=True)
class DocsIndexReaderPathBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class DocsIndexReaderPathBoundaryValidation:
    ok: bool
    boundary_status: str | None
    route_record_count: int
    missing_route_record_count: int
    boundary_marker_count: int
    missing_evidence_count: int
    issues: list[DocsIndexReaderPathBoundaryIssue]


def docs_index_reader_path_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the docs/README reader-path and boundary marker record."""

    root_path = Path(root)
    docs_text = _read_text(root_path / DOCS_README_PATH)
    route_records = [_route_record(root_path, docs_text, route) for route in EXPECTED_ROUTES]
    missing_route_records = [
        record for record in route_records if record["route_status"] != "route_target_and_markers_present"
    ]
    boundary_marker_records = [
        _marker_record("documentation_boundary", DOCS_README_PATH, docs_text, marker)
        for marker in EXPECTED_BOUNDARY_MARKERS
    ]
    missing_boundary_marker_records = [
        record for record in boundary_marker_records if record["marker_status"] != "marker_present"
    ]
    route_group_counts: dict[str, int] = {}
    for record in route_records:
        route_group_counts[record["route_group"]] = route_group_counts.get(record["route_group"], 0) + 1
    return {
        "schema": DOCS_INDEX_READER_PATH_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "docs_readme_path": DOCS_README_PATH,
        "route_record_count": len(route_records),
        "route_group_counts": dict(sorted(route_group_counts.items())),
        "missing_route_record_count": len(missing_route_records),
        "missing_route_records": missing_route_records,
        "route_records": route_records,
        "boundary_marker_count": len(boundary_marker_records),
        "missing_boundary_marker_count": len(missing_boundary_marker_records),
        "missing_boundary_marker_records": missing_boundary_marker_records,
        "boundary_marker_records": boundary_marker_records,
        "whole_documentation_cleanup_status": (
            "marker_present"
            if "AlphaEvolve-alignment cleanup is a whole-documentation task" in docs_text
            else "marker_missing"
        ),
        "docs_index_marker_status": (
            "docs_index_routes_and_boundary_markers_present"
            if not missing_route_records and not missing_boundary_marker_records
            else "docs_index_routes_or_boundary_markers_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records docs/README reader paths, operational-guide "
            "routes, documentation-boundary markers, route target existence "
            "checks, target heading marker checks, and the whole-documentation "
            "AlphaEvolve-alignment cleanup marker. It does not claim semantic "
            "route-purpose verification, target-scope agreement verification, "
            "new-major-doc detection, misplaced-claim detection, or owner "
            "review signoff."
        ),
    }


def validate_docs_index_reader_path_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> DocsIndexReaderPathBoundaryValidation:
    data, read_issues = _load_boundary(
        docs_index_reader_path_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return DocsIndexReaderPathBoundaryValidation(False, None, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = docs_index_reader_path_boundary_record(root)
    issues: list[DocsIndexReaderPathBoundaryIssue] = []
    if data.get("schema") != DOCS_INDEX_READER_PATH_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported docs-index reader-path boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "docs-index reader-path boundary must not claim semantic routing proof"))
    for key in (
        "docs_readme_path",
        "route_record_count",
        "route_group_counts",
        "missing_route_record_count",
        "missing_route_records",
        "route_records",
        "boundary_marker_count",
        "missing_boundary_marker_count",
        "missing_boundary_marker_records",
        "boundary_marker_records",
        "whole_documentation_cleanup_status",
        "docs_index_marker_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current docs-index inputs"))
    if data.get("missing_route_record_count") != 0:
        issues.append(_issue("missing_docs_index_route", "docs/README route records are incomplete"))
    if data.get("missing_boundary_marker_count") != 0:
        issues.append(_issue("missing_docs_index_boundary_marker", "docs/README boundary markers are incomplete"))
    if data.get("whole_documentation_cleanup_status") != "marker_present":
        issues.append(_issue("missing_whole_documentation_cleanup_marker", "docs/README must keep the whole-documentation cleanup marker"))
    if data.get("docs_index_marker_status") != "docs_index_routes_and_boundary_markers_present":
        issues.append(_issue("invalid_docs_index_marker_status", "docs-index routes and boundary markers must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "docs/README reader paths" not in boundary_text
        or "whole-documentation AlphaEvolve-alignment cleanup marker" not in boundary_text
        or "does not claim semantic route-purpose verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate docs-index markers from semantic routing proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return DocsIndexReaderPathBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        route_record_count=data.get("route_record_count") if isinstance(data.get("route_record_count"), int) else 0,
        missing_route_record_count=data.get("missing_route_record_count") if isinstance(data.get("missing_route_record_count"), int) else 0,
        boundary_marker_count=data.get("boundary_marker_count") if isinstance(data.get("boundary_marker_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_docs_index_reader_path_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_docs_index_reader_path_boundary(boundary)
    lines = [
        "Docs index reader-path boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| route_record_count | {validation.route_record_count} |",
        f"| missing_route_record_count | {validation.missing_route_record_count} |",
        f"| boundary_marker_count | {validation.boundary_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _route_record(root_path: Path, docs_text: str, route: dict[str, Any]) -> dict[str, Any]:
    target_path = str(route["target_path"])
    target = root_path / target_path
    target_text = _read_text(target)
    link_present = str(route["link_marker"]) in docs_text
    target_exists = target.exists()
    missing_target_markers = [
        marker for marker in route["target_markers"] if marker not in target_text
    ]
    route_status = (
        "route_target_and_markers_present"
        if link_present and target_exists and not missing_target_markers
        else "route_target_or_markers_missing"
    )
    return {
        "route_id": route["route_id"],
        "route_group": route["route_group"],
        "link_marker": route["link_marker"],
        "target_path": target_path,
        "link_status": "link_present" if link_present else "link_missing",
        "target_status": "target_present" if target_exists else "target_missing",
        "missing_target_markers": missing_target_markers,
        "route_status": route_status,
    }


def _marker_record(kind: str, path: str, text: str, marker: str) -> dict[str, Any]:
    return {
        "record_kind": kind,
        "path": path,
        "required_marker": marker,
        "marker_status": "marker_present" if marker in text else "marker_missing",
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[DocsIndexReaderPathBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "docs-index reader-path boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[DocsIndexReaderPathBoundaryIssue],
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
    issues: list[DocsIndexReaderPathBoundaryIssue],
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


def _issue(code: str, message: str) -> DocsIndexReaderPathBoundaryIssue:
    return DocsIndexReaderPathBoundaryIssue(code, message)
