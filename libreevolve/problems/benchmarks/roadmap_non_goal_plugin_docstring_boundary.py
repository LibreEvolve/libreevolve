from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.plugins.registry import builtin_plugin_registry
from libreevolve.problems.benchmarks.roadmap_non_goal_contradiction_boundary import (
    roadmap_non_goal_contradiction_boundary_record,
)


ROADMAP_NON_GOAL_PLUGIN_DOCSTRING_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_non_goal_plugin_docstring_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "plugin_docstring_scan_without_runtime_or_promotion_gate"
)
SOURCE_NON_GOAL_BOUNDARY_INPUT = "papers/roadmap_non_goal_contradiction_boundary.json"
PLUGIN_SOURCE_ROOT = "libreevolve/plugins"
FORBIDDEN_PLUGIN_FAITHFUL_CLAIM_PHRASES = (
    "faithful implementation",
    "faithful implementations",
    "faithfully implement",
    "faithfully implements",
    "implements the full paper",
    "implements the paper",
    "paper-faithful",
)
DISCLAIMER_TERMS = (
    "does not implement",
    "does not enforce",
    "does not execute",
    "not the",
    "accumulates examples only",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stable_non_goal_ids",
    "plugin_source_file_inventory",
    "plugin_docstring_scan",
    "builtin_plugin_registry_labels",
    "paper_inspiration_label_scan",
    "faithful_claim_phrase_scan",
    "paper_inspired_plugin_disclaimer_scan",
    "runtime_metadata_scan",
    "ci_non_goal_promotion_gate",
    "intentional_promotion_workflow",
    "claim_surface_remediation",
    "runtime_plugin_scope_join",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "runtime_metadata_scan": "not_recorded_locally",
    "ci_non_goal_promotion_gate": "not_recorded_locally",
    "intentional_promotion_workflow": "not_recorded_locally",
    "claim_surface_remediation": "not_recorded_locally",
    "runtime_plugin_scope_join": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class RoadmapNonGoalPluginDocstringBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapNonGoalPluginDocstringBoundaryValidation:
    ok: bool
    boundary_status: str | None
    plugin_source_file_count: int
    builtin_plugin_count: int
    docstring_record_count: int
    faithful_overclaim_count: int
    missing_disclaimer_count: int
    missing_evidence_count: int
    issues: list[RoadmapNonGoalPluginDocstringBoundaryIssue]


def roadmap_non_goal_plugin_docstring_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the ROADMAP non-goal plugin source/docstring scan."""

    root_path = Path(root)
    source_boundary = roadmap_non_goal_contradiction_boundary_record(root_path)
    source_files = _plugin_source_files(root_path)
    file_records = [_plugin_source_file_record(root_path, path) for path in source_files]
    registry_records = _builtin_plugin_records()
    docstring_records = [
        docstring
        for file_record in file_records
        for docstring in file_record["docstring_records"]
    ]
    faithful_hit_records = [
        hit
        for file_record in file_records
        for hit in file_record["faithful_overclaim_hit_records"]
    ]
    class_docstrings = {
        record["qualname"]: record["docstring"]
        for record in docstring_records
        if record["node_kind"] == "class"
    }
    paper_inspired_scope_records = [
        _paper_inspired_scope_record(record, class_docstrings)
        for record in registry_records
        if record["paper_inspiration"]
        and record["paper_inspiration"] != "external_plugin_entry_point"
    ]
    missing_disclaimer_records = [
        record
        for record in paper_inspired_scope_records
        if record["class_docstring_present"]
        and not record["non_faithful_disclaimer_present"]
    ]
    return {
        "schema": ROADMAP_NON_GOAL_PLUGIN_DOCSTRING_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_non_goal_boundary_input": SOURCE_NON_GOAL_BOUNDARY_INPUT,
        "source_non_goal_count": source_boundary["non_goal_count"],
        "plugin_source_root": PLUGIN_SOURCE_ROOT,
        "plugin_source_file_count": len(source_files),
        "plugin_source_files": [path.as_posix() for path in source_files],
        "plugin_source_file_records": file_records,
        "source_read_error_count": sum(
            1 for record in file_records if record["read_status"] != "ok"
        ),
        "builtin_plugin_count": len(registry_records),
        "builtin_plugin_records": registry_records,
        "paper_inspired_builtin_plugin_count": len(paper_inspired_scope_records),
        "paper_inspired_plugin_scope_records": paper_inspired_scope_records,
        "missing_disclaimer_count": len(missing_disclaimer_records),
        "missing_disclaimer_records": missing_disclaimer_records,
        "docstring_record_count": len(docstring_records),
        "forbidden_phrase_count": len(FORBIDDEN_PLUGIN_FAITHFUL_CLAIM_PHRASES),
        "faithful_overclaim_count": len(faithful_hit_records),
        "faithful_overclaim_hit_records": faithful_hit_records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary scans built-in plugin Python source files, AST "
            "docstrings, registry labels, and paper-inspiration labels for "
            "faithful-implementation overclaims. It does not claim runtime "
            "metadata scanning, CI promotion enforcement, intentional "
            "promotion workflow, joined runtime/plugin/docs/paper scope proof, "
            "or owner-reviewed remediation readiness."
        ),
    }


def validate_roadmap_non_goal_plugin_docstring_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapNonGoalPluginDocstringBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_non_goal_plugin_docstring_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapNonGoalPluginDocstringBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_non_goal_plugin_docstring_boundary_record(root)
    issues: list[RoadmapNonGoalPluginDocstringBoundaryIssue] = []
    if data.get("schema") != ROADMAP_NON_GOAL_PLUGIN_DOCSTRING_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP non-goal plugin docstring schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "plugin docstring scan must not claim full non-goal promotion readiness"))
    for key in (
        "source_non_goal_count",
        "plugin_source_root",
        "plugin_source_file_count",
        "plugin_source_files",
        "plugin_source_file_records",
        "source_read_error_count",
        "builtin_plugin_count",
        "builtin_plugin_records",
        "paper_inspired_builtin_plugin_count",
        "paper_inspired_plugin_scope_records",
        "missing_disclaimer_count",
        "missing_disclaimer_records",
        "docstring_record_count",
        "forbidden_phrase_count",
        "faithful_overclaim_count",
        "faithful_overclaim_hit_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current plugin source inputs"))
    if data.get("source_read_error_count") != 0:
        issues.append(_issue("source_read_error", "plugin source files must be readable for docstring scanning"))
    if data.get("faithful_overclaim_count") != 0:
        issues.append(_issue("faithful_overclaim_detected", "plugin source contains faithful-implementation overclaim phrases"))
    if data.get("missing_disclaimer_count") != 0:
        issues.append(_issue("missing_plugin_disclaimer", "paper-inspired built-in plugin docstrings must retain non-faithful scope disclaimers"))
    required_count = _validate_required_fields(
        data.get("required_evidence_fields"), issues
    )
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "AST docstrings" not in boundary_text
        or "does not claim runtime metadata scanning" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate plugin docstring scan from full promotion readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapNonGoalPluginDocstringBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        plugin_source_file_count=data.get("plugin_source_file_count") if isinstance(data.get("plugin_source_file_count"), int) else 0,
        builtin_plugin_count=data.get("builtin_plugin_count") if isinstance(data.get("builtin_plugin_count"), int) else 0,
        docstring_record_count=data.get("docstring_record_count") if isinstance(data.get("docstring_record_count"), int) else 0,
        faithful_overclaim_count=data.get("faithful_overclaim_count") if isinstance(data.get("faithful_overclaim_count"), int) else 0,
        missing_disclaimer_count=data.get("missing_disclaimer_count") if isinstance(data.get("missing_disclaimer_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_non_goal_plugin_docstring_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_non_goal_plugin_docstring_boundary(boundary)
    rows = [
        ("schema_status", "ok" if validation.ok else "invalid"),
        ("boundary_status", validation.boundary_status or "unknown"),
        ("plugin_source_file_count", str(validation.plugin_source_file_count)),
        ("builtin_plugin_count", str(validation.builtin_plugin_count)),
        ("docstring_record_count", str(validation.docstring_record_count)),
        ("faithful_overclaim_count", str(validation.faithful_overclaim_count)),
        ("missing_disclaimer_count", str(validation.missing_disclaimer_count)),
        ("missing_evidence_count", str(validation.missing_evidence_count)),
    ]
    lines = ["# ROADMAP non-goal plugin docstring boundary", "", "| Field | Value |", "| --- | --- |"]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    if validation.issues:
        lines.extend(["", "## Issues"])
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in validation.issues)
    return "\n".join(lines) + "\n"


def _plugin_source_files(root_path: Path) -> list[Path]:
    plugin_root = root_path / PLUGIN_SOURCE_ROOT
    if not plugin_root.exists():
        return []
    return sorted(
        (path.relative_to(root_path) for path in plugin_root.glob("*.py")),
        key=lambda path: path.as_posix(),
    )


def _plugin_source_file_record(root_path: Path, relative_path: Path) -> dict[str, Any]:
    path = root_path / relative_path
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {
            "path": relative_path.as_posix(),
            "read_status": "read_error",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "docstring_records": [],
            "faithful_overclaim_hit_records": [],
        }
    try:
        tree = ast.parse(text, filename=relative_path.as_posix())
    except SyntaxError as exc:
        return {
            "path": relative_path.as_posix(),
            "read_status": "syntax_error",
            "error_type": type(exc).__name__,
            "error": str(exc),
            "docstring_records": [],
            "faithful_overclaim_hit_records": _faithful_phrase_hits(
                relative_path, text
            ),
        }
    return {
        "path": relative_path.as_posix(),
        "read_status": "ok",
        "docstring_records": _docstring_records(relative_path, tree),
        "faithful_overclaim_hit_records": _faithful_phrase_hits(relative_path, text),
    }


def _docstring_records(relative_path: Path, tree: ast.AST) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    module_doc = ast.get_docstring(tree)
    if module_doc:
        records.append(_docstring_record(relative_path, "module", "<module>", tree, module_doc))
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            doc = ast.get_docstring(node)
            if doc:
                records.append(_docstring_record(relative_path, "class", node.name, node, doc))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            doc = ast.get_docstring(node)
            if doc:
                records.append(_docstring_record(relative_path, "function", node.name, node, doc))
    return sorted(records, key=lambda record: (record["line_start"], record["qualname"]))


def _docstring_record(
    relative_path: Path,
    node_kind: str,
    qualname: str,
    node: ast.AST,
    docstring: str,
) -> dict[str, Any]:
    lowered = docstring.lower()
    return {
        "path": relative_path.as_posix(),
        "node_kind": node_kind,
        "qualname": qualname,
        "line_start": getattr(node, "lineno", 1),
        "docstring": docstring,
        "paper_inspired_term_present": "inspired" in lowered,
        "non_faithful_disclaimer_present": any(
            term in lowered for term in DISCLAIMER_TERMS
        ),
    }


def _faithful_phrase_hits(relative_path: Path, text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    lowered_lines = [line.lower() for line in text.splitlines()]
    for phrase in FORBIDDEN_PLUGIN_FAITHFUL_CLAIM_PHRASES:
        phrase_lower = phrase.lower()
        for line_number, line in enumerate(lowered_lines, start=1):
            column = line.find(phrase_lower)
            if column == -1:
                continue
            hits.append(
                {
                    "path": relative_path.as_posix(),
                    "line_start": line_number,
                    "phrase": phrase,
                    "column_start": column + 1,
                }
            )
    return hits


def _builtin_plugin_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for label, definition in sorted(builtin_plugin_registry().items()):
        plugin_class = definition.plugin_class
        records.append(
            {
                "label": label,
                "plugin_class": plugin_class.__name__,
                "plugin_module": plugin_class.__module__,
                "paper_inspiration": definition.paper_inspiration,
                "option_names": sorted(definition.option_schema),
            }
        )
    return records


def _paper_inspired_scope_record(
    registry_record: dict[str, Any],
    class_docstrings: dict[str, str],
) -> dict[str, Any]:
    class_name = registry_record["plugin_class"]
    docstring = class_docstrings.get(class_name, "")
    lowered = docstring.lower()
    return {
        "label": registry_record["label"],
        "plugin_class": class_name,
        "paper_inspiration": registry_record["paper_inspiration"],
        "class_docstring_present": bool(docstring),
        "paper_inspired_term_present": "inspired" in lowered,
        "non_faithful_disclaimer_present": any(
            term in lowered for term in DISCLAIMER_TERMS
        ),
        "docstring": docstring,
    }


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapNonGoalPluginDocstringBoundaryIssue]]:
    if isinstance(boundary, dict):
        return boundary, []
    if isinstance(boundary, (str, Path)):
        path = Path(boundary)
        try:
            return json.loads(path.read_text(encoding="utf-8")), []
        except OSError as exc:
            return None, [_issue("read_error", f"could not read boundary: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [_issue("json_error", f"could not parse boundary JSON: {exc}")]
    return None, [_issue("invalid_boundary_type", "boundary must be a dict or JSON path")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapNonGoalPluginDocstringBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    for field in EXPECTED_REQUIRED_EVIDENCE_FIELDS:
        if field not in value:
            issues.append(_issue("missing_required_evidence_field", f"missing required evidence field: {field}"))
    return len(value)


def _validate_missing_evidence(
    value: object,
    issues: list[RoadmapNonGoalPluginDocstringBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be a dict"))
        return 0
    for field, expected_status in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(field) != expected_status:
            issues.append(_issue(f"invalid_missing_evidence_{field}", f"missing_evidence[{field!r}] must be {expected_status!r}"))
    unexpected = sorted(set(value) - set(EXPECTED_MISSING_EVIDENCE))
    for field in unexpected:
        issues.append(_issue("unexpected_missing_evidence_field", f"unexpected missing evidence field: {field}"))
    return len(value)


def _issue(
    code: str,
    message: str,
) -> RoadmapNonGoalPluginDocstringBoundaryIssue:
    return RoadmapNonGoalPluginDocstringBoundaryIssue(code=code, message=message)
