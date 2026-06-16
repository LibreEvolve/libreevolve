from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.documentation_claim_inventory import (
    documentation_claim_inventory_record,
)


DOCS_STATUS_LEDGER_BOUNDARY_SCHEMA = "libreevolve.docs_status_ledger_boundary.v1"
EXPECTED_BOUNDARY_STATUS = "docs_status_structural_freshness_inventory_without_semantic_map"
STATUS_LEDGER_PATH = "docs/status.md"
STATUS_CLAIM_INVENTORY_PATH = "papers/status_claim_inventory.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "status_ledger_heading",
    "implemented_today_bullet_inventory",
    "important_limits_bullet_inventory",
    "status_signal_term_inventory",
    "local_path_ref_existence_checks",
    "readme_status_route",
    "docs_index_status_route",
    "documentation_claim_inventory_status_fields",
    "paper_index_status_claim_inventory_comparison",
    "active_todo_owner_anchor",
    "per_bullet_source_test_sidecar_todo_map",
    "stale_status_prose_detector",
    "orphan_status_bullet_detector",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "per_bullet_source_test_sidecar_todo_map": "not_recorded_locally",
    "stale_status_prose_detector": "not_recorded_locally",
    "orphan_status_bullet_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_ROUTE_MARKERS = (
    {
        "route_id": "readme_current_status_route",
        "source_path": "README.md",
        "marker": "[docs/status.md](docs/status.md)",
    },
    {
        "route_id": "docs_index_paper_reviewer_status_route",
        "source_path": "docs/README.md",
        "marker": "[Current Status](./status.md)",
    },
    {
        "route_id": "todo_status_ledger_owner_anchor",
        "source_path": "docs/todo/readme.md",
        "marker": "Add `docs/status.md` ledger freshness and coverage evidence.",
    },
    {
        "route_id": "papers_index_status_claim_inventory_entry",
        "source_path": "papers/README.md",
        "marker": "papers/status_claim_inventory.json",
    },
)
STATUS_CLAIM_SUMMARY_FIELDS = (
    "row_count",
    "unique_local_artifact_count",
    "local_artifact_mention_record_count",
    "absence_phrase_count",
    "absence_signal_record_count",
)


@dataclass(frozen=True)
class DocsStatusLedgerBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class DocsStatusLedgerBoundaryValidation:
    ok: bool
    boundary_status: str | None
    status_ledger_bullet_count: int
    status_ledger_local_path_ref_count: int
    missing_route_marker_count: int
    missing_evidence_count: int
    issues: list[DocsStatusLedgerBoundaryIssue]


def docs_status_ledger_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the docs/status.md ledger freshness boundary record."""

    root_path = Path(root)
    status_text = _read_text(root_path / STATUS_LEDGER_PATH)
    claim_inventory = documentation_claim_inventory_record(root_path)
    route_records = [_route_marker_record(root_path, marker) for marker in EXPECTED_ROUTE_MARKERS]
    missing_route_records = [
        record for record in route_records if record["marker_status"] != "marker_present"
    ]
    status_claim_inventory = _status_claim_inventory_summary(root_path)
    section_counts = claim_inventory.get("status_ledger_section_counts", {})
    return {
        "schema": DOCS_STATUS_LEDGER_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "status_ledger_path": STATUS_LEDGER_PATH,
        "status_ledger_heading_status": (
            "heading_present"
            if "# Current Implementation Status" in status_text
            else "heading_missing"
        ),
        "status_ledger_inventory_status": claim_inventory.get(
            "status_ledger_inventory_status"
        ),
        "status_ledger_bullet_count": claim_inventory.get("status_ledger_bullet_count"),
        "status_ledger_section_counts": section_counts,
        "implemented_today_bullet_count": (
            section_counts.get("implemented_today") if isinstance(section_counts, dict) else None
        ),
        "important_limits_bullet_count": (
            section_counts.get("important_limits") if isinstance(section_counts, dict) else None
        ),
        "status_ledger_signal_term_count": claim_inventory.get(
            "status_ledger_signal_term_count"
        ),
        "status_ledger_signal_record_count": claim_inventory.get(
            "status_ledger_signal_record_count"
        ),
        "status_ledger_local_path_ref_count": claim_inventory.get(
            "status_ledger_local_path_ref_count"
        ),
        "status_ledger_unique_local_path_ref_count": claim_inventory.get(
            "status_ledger_unique_local_path_ref_count"
        ),
        "status_ledger_missing_local_path_refs": claim_inventory.get(
            "status_ledger_missing_local_path_refs"
        ),
        "status_ledger_local_path_ref_status": claim_inventory.get(
            "status_ledger_local_path_ref_status"
        ),
        "route_marker_record_count": len(route_records),
        "missing_route_marker_count": len(missing_route_records),
        "missing_route_marker_records": missing_route_records,
        "route_marker_records": route_records,
        "documentation_claim_inventory_status_field_names": [
            key
            for key in sorted(claim_inventory)
            if key.startswith("status_ledger_")
        ],
        "status_claim_inventory_path": STATUS_CLAIM_INVENTORY_PATH,
        "status_claim_inventory_summary": status_claim_inventory,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the docs/status.md heading, implemented-today "
            "and important-limits bullet inventory, status-signal terms, local "
            "backtick path existence checks, README and docs-index routes, "
            "documentation-claim inventory status fields, paper-index status "
            "claim inventory summary fields, and the active TODO owner anchor. "
            "It does not claim a per-bullet source/test/sidecar/TODO map, stale "
            "status prose detector, orphan status bullet detector, or owner "
            "review signoff."
        ),
    }


def validate_docs_status_ledger_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> DocsStatusLedgerBoundaryValidation:
    data, read_issues = _load_boundary(
        docs_status_ledger_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return DocsStatusLedgerBoundaryValidation(False, None, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = docs_status_ledger_boundary_record(root)
    issues: list[DocsStatusLedgerBoundaryIssue] = []
    if data.get("schema") != DOCS_STATUS_LEDGER_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported docs/status ledger boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "docs/status ledger boundary must not claim semantic freshness proof"))
    for key in (
        "status_ledger_path",
        "status_ledger_heading_status",
        "status_ledger_inventory_status",
        "status_ledger_bullet_count",
        "status_ledger_section_counts",
        "implemented_today_bullet_count",
        "important_limits_bullet_count",
        "status_ledger_signal_term_count",
        "status_ledger_signal_record_count",
        "status_ledger_local_path_ref_count",
        "status_ledger_unique_local_path_ref_count",
        "status_ledger_missing_local_path_refs",
        "status_ledger_local_path_ref_status",
        "route_marker_record_count",
        "missing_route_marker_count",
        "missing_route_marker_records",
        "route_marker_records",
        "documentation_claim_inventory_status_field_names",
        "status_claim_inventory_path",
        "status_claim_inventory_summary",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current docs/status inputs"))
    if data.get("status_ledger_heading_status") != "heading_present":
        issues.append(_issue("missing_status_ledger_heading", "docs/status.md must keep the current-status heading"))
    if data.get("status_ledger_local_path_ref_status") != "all_status_ledger_local_path_refs_present":
        issues.append(_issue("missing_status_ledger_local_path_ref", "docs/status.md local path refs must resolve"))
    if data.get("missing_route_marker_count") != 0:
        issues.append(_issue("missing_route_marker", "status-ledger route markers are incomplete"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "docs/status.md heading" not in boundary_text
        or "paper-index status claim inventory summary fields" not in boundary_text
        or "does not claim a per-bullet source/test/sidecar/TODO map" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate structural status-ledger evidence from semantic freshness proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return DocsStatusLedgerBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        status_ledger_bullet_count=(
            data.get("status_ledger_bullet_count")
            if isinstance(data.get("status_ledger_bullet_count"), int)
            else 0
        ),
        status_ledger_local_path_ref_count=(
            data.get("status_ledger_local_path_ref_count")
            if isinstance(data.get("status_ledger_local_path_ref_count"), int)
            else 0
        ),
        missing_route_marker_count=(
            data.get("missing_route_marker_count")
            if isinstance(data.get("missing_route_marker_count"), int)
            else 0
        ),
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_docs_status_ledger_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_docs_status_ledger_boundary(boundary)
    lines = [
        "Docs status ledger boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| status_ledger_bullet_count | {validation.status_ledger_bullet_count} |",
        f"| status_ledger_local_path_ref_count | {validation.status_ledger_local_path_ref_count} |",
        f"| missing_route_marker_count | {validation.missing_route_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _route_marker_record(root_path: Path, route: dict[str, str]) -> dict[str, Any]:
    source_path = route["source_path"]
    text = _read_text(root_path / source_path)
    marker = route["marker"]
    return {
        "route_id": route["route_id"],
        "source_path": source_path,
        "target_path": STATUS_LEDGER_PATH,
        "marker": marker,
        "marker_status": "marker_present" if marker in text else "marker_missing",
    }


def _status_claim_inventory_summary(root_path: Path) -> dict[str, Any]:
    path = root_path / STATUS_CLAIM_INVENTORY_PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return {
            "summary_status": "status_claim_inventory_unreadable_or_missing",
            "path": STATUS_CLAIM_INVENTORY_PATH,
            **{field: None for field in STATUS_CLAIM_SUMMARY_FIELDS},
        }
    if not isinstance(data, dict):
        return {
            "summary_status": "status_claim_inventory_invalid_shape",
            "path": STATUS_CLAIM_INVENTORY_PATH,
            **{field: None for field in STATUS_CLAIM_SUMMARY_FIELDS},
        }
    return {
        "summary_status": "status_claim_inventory_summary_recorded",
        "path": STATUS_CLAIM_INVENTORY_PATH,
        **{field: data.get(field) for field in STATUS_CLAIM_SUMMARY_FIELDS},
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[DocsStatusLedgerBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "docs/status ledger boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[DocsStatusLedgerBoundaryIssue],
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
    issues: list[DocsStatusLedgerBoundaryIssue],
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


def _issue(code: str, message: str) -> DocsStatusLedgerBoundaryIssue:
    return DocsStatusLedgerBoundaryIssue(code, message)
