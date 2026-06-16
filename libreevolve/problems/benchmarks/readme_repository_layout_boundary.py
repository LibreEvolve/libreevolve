from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_REPOSITORY_LAYOUT_BOUNDARY_SCHEMA = (
    "libreevolve.readme_repository_layout_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "readme_repository_layout_recorded_without_semantic_role_verifier"
)
README_PATH = "README.md"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "repository_layout_block_inventory",
    "layout_entry_path_existence_checks",
    "layout_summary_marker_checks",
    "module_evidence_path_checks",
    "custom_backend_layout_marker",
    "archival_old_route_record",
    "run_output_scope_record",
    "module_role_semantic_verifier",
    "new_top_level_detector",
    "new_major_docs_detector",
    "alphaevolve_parity_placeholder_classifier",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "module_role_semantic_verifier": "not_recorded_locally",
    "new_top_level_detector": "not_recorded_locally",
    "new_major_docs_detector": "not_recorded_locally",
    "alphaevolve_parity_placeholder_classifier": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_LAYOUT_ENTRIES = (
    {
        "entry_id": "libreevolve_package",
        "layout_path": "libreevolve",
        "line_marker": "libreevolve/",
        "summary_markers": (),
        "evidence_paths": ("libreevolve/__init__.py",),
    },
    {
        "entry_id": "core",
        "layout_path": "libreevolve/core",
        "line_marker": "core/",
        "summary_markers": ("orchestration", "prompting", "evaluation", "diffing", "database", "config"),
        "evidence_paths": (
            "libreevolve/core/loop.py",
            "libreevolve/core/prompt.py",
            "libreevolve/core/evaluator.py",
            "libreevolve/core/diff.py",
            "libreevolve/core/database.py",
            "libreevolve/core/config.py",
        ),
    },
    {
        "entry_id": "llm",
        "layout_path": "libreevolve/llm",
        "line_marker": "llm/",
        "summary_markers": ("OpenAI", "Anthropic", "Ollama", "custom backends", "ensemble routing"),
        "evidence_paths": (
            "libreevolve/llm/openai.py",
            "libreevolve/llm/anthropic.py",
            "libreevolve/llm/ollama.py",
            "libreevolve/llm/backend_registry.py",
            "libreevolve/llm/ensemble.py",
        ),
    },
    {
        "entry_id": "population",
        "layout_path": "libreevolve/population",
        "line_marker": "population/",
        "summary_markers": ("program records", "MAP-Elites", "island migration"),
        "evidence_paths": (
            "libreevolve/population/program.py",
            "libreevolve/population/map_elites.py",
            "libreevolve/population/islands.py",
        ),
    },
    {
        "entry_id": "plugins",
        "layout_path": "libreevolve/plugins",
        "line_marker": "plugins/",
        "summary_markers": ("optional lifecycle hooks", "paper-inspired plugins"),
        "evidence_paths": ("libreevolve/plugins/base.py",),
    },
    {
        "entry_id": "problems",
        "layout_path": "libreevolve/problems",
        "line_marker": "problems/",
        "summary_markers": ("examples", "problem loading"),
        "evidence_paths": (
            "libreevolve/problems/loader.py",
            "libreevolve/problems/examples",
        ),
    },
    {
        "entry_id": "tools",
        "layout_path": "libreevolve/tools",
        "line_marker": "tools/",
        "summary_markers": ("paper/source manifest validation",),
        "evidence_paths": ("libreevolve/tools/paper_manifest.py",),
    },
    {
        "entry_id": "docs",
        "layout_path": "docs",
        "line_marker": "docs/",
        "summary_markers": ("architecture", "configuration", "backend", "plugin", "artifact docs"),
        "evidence_paths": (
            "docs/architecture.md",
            "docs/configuration.md",
            "docs/backends.md",
            "docs/plugins.md",
            "docs/run-artifacts.md",
        ),
    },
    {
        "entry_id": "papers",
        "layout_path": "papers",
        "line_marker": "papers/",
        "summary_markers": ("tracked manifests", "ignored PDF cache", "retained source artifacts"),
        "evidence_paths": ("papers/README.md", "papers/download_manifest.csv"),
    },
    {
        "entry_id": "old",
        "layout_path": "old",
        "line_marker": "old/",
        "summary_markers": ("archival", "non-authoritative historical planning material"),
        "evidence_paths": ("old",),
    },
    {
        "entry_id": "runs",
        "layout_path": "runs",
        "line_marker": "runs/",
        "summary_markers": ("gitignored run outputs",),
        "evidence_paths": ("runs",),
    },
    {
        "entry_id": "tests",
        "layout_path": "tests",
        "line_marker": "tests/",
        "summary_markers": ("unit", "integration tests"),
        "evidence_paths": ("tests",),
    },
    {
        "entry_id": "agents",
        "layout_path": "AGENTS.md",
        "line_marker": "AGENTS.md",
        "summary_markers": ("agent-facing operating contract",),
        "evidence_paths": ("AGENTS.md",),
    },
)


@dataclass(frozen=True)
class ReadmeRepositoryLayoutBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeRepositoryLayoutBoundaryValidation:
    ok: bool
    boundary_status: str | None
    layout_entry_count: int
    missing_layout_entry_count: int
    missing_evidence_path_count: int
    missing_evidence_count: int
    issues: list[ReadmeRepositoryLayoutBoundaryIssue]


def readme_repository_layout_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded README Repository Layout inventory."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    layout_block = _extract_repository_layout_block(readme_text)
    entry_records = [
        _layout_entry_record(root_path, layout_block, entry)
        for entry in EXPECTED_LAYOUT_ENTRIES
    ]
    missing_entries = [
        record for record in entry_records if record["entry_status"] != "entry_path_and_markers_present"
    ]
    missing_evidence_paths = sorted(
        {
            path
            for record in entry_records
            for path in record["missing_evidence_paths"]
        }
    )
    return {
        "schema": README_REPOSITORY_LAYOUT_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "layout_block_status": "layout_block_present" if layout_block else "layout_block_missing",
        "layout_entry_count": len(entry_records),
        "missing_layout_entry_count": len(missing_entries),
        "missing_layout_entry_records": missing_entries,
        "layout_entry_records": entry_records,
        "missing_evidence_path_count": len(missing_evidence_paths),
        "missing_evidence_paths": missing_evidence_paths,
        "custom_backend_layout_status": (
            "custom_backend_marker_present"
            if _entry_has_marker(entry_records, "llm", "custom backends")
            else "custom_backend_marker_missing"
        ),
        "archival_old_layout_status": (
            "archival_old_layout_present"
            if _entry_has_marker(entry_records, "old", "archival")
            else "archival_old_layout_missing"
        ),
        "run_output_scope_status": (
            "run_output_scope_present"
            if _entry_has_marker(entry_records, "runs", "gitignored run outputs")
            else "run_output_scope_missing"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README Repository Layout code block, "
            "layout-entry path existence checks, summary marker checks, module "
            "evidence path checks, custom-backend layout marker, archival old/ "
            "record, and gitignored runs/ scope record. It does not claim "
            "semantic module-role verification, new top-level detection, new "
            "major-doc detection, AlphaEvolve-parity placeholder classification, "
            "or owner review signoff."
        ),
    }


def validate_readme_repository_layout_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeRepositoryLayoutBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_repository_layout_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeRepositoryLayoutBoundaryValidation(False, None, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = readme_repository_layout_boundary_record(root)
    issues: list[ReadmeRepositoryLayoutBoundaryIssue] = []
    if data.get("schema") != README_REPOSITORY_LAYOUT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README repository-layout boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README repository-layout boundary must not claim semantic module-role proof"))
    for key in (
        "readme_path",
        "layout_block_status",
        "layout_entry_count",
        "missing_layout_entry_count",
        "missing_layout_entry_records",
        "layout_entry_records",
        "missing_evidence_path_count",
        "missing_evidence_paths",
        "custom_backend_layout_status",
        "archival_old_layout_status",
        "run_output_scope_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current README layout inputs"))
    if data.get("layout_block_status") != "layout_block_present":
        issues.append(_issue("missing_layout_block", "README must keep the Repository Layout code block"))
    if data.get("missing_layout_entry_count") != 0:
        issues.append(_issue("missing_layout_entry", "README Repository Layout entries are incomplete"))
    if data.get("missing_evidence_path_count") != 0:
        issues.append(_issue("missing_layout_evidence_path", "README Repository Layout evidence paths are missing"))
    if data.get("custom_backend_layout_status") != "custom_backend_marker_present":
        issues.append(_issue("missing_custom_backend_layout_marker", "README llm/ layout entry must mention custom backends"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README Repository Layout code block" not in boundary_text
        or "custom-backend layout marker" not in boundary_text
        or "does not claim semantic module-role verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate layout inventory from semantic module-role proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmeRepositoryLayoutBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        layout_entry_count=data.get("layout_entry_count") if isinstance(data.get("layout_entry_count"), int) else 0,
        missing_layout_entry_count=(
            data.get("missing_layout_entry_count")
            if isinstance(data.get("missing_layout_entry_count"), int)
            else 0
        ),
        missing_evidence_path_count=(
            data.get("missing_evidence_path_count")
            if isinstance(data.get("missing_evidence_path_count"), int)
            else 0
        ),
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_repository_layout_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_repository_layout_boundary(boundary)
    lines = [
        "README Repository Layout boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| layout_entry_count | {validation.layout_entry_count} |",
        f"| missing_layout_entry_count | {validation.missing_layout_entry_count} |",
        f"| missing_evidence_path_count | {validation.missing_evidence_path_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _extract_repository_layout_block(readme_text: str) -> str:
    marker = "## Repository Layout"
    marker_index = readme_text.find(marker)
    if marker_index < 0:
        return ""
    fence_start = readme_text.find("```text", marker_index)
    if fence_start < 0:
        return ""
    content_start = readme_text.find("\n", fence_start)
    if content_start < 0:
        return ""
    fence_end = readme_text.find("```", content_start + 1)
    if fence_end < 0:
        return ""
    return readme_text[content_start + 1:fence_end]


def _layout_entry_record(root: Path, layout_block: str, entry: dict[str, Any]) -> dict[str, Any]:
    layout_path = str(entry["layout_path"])
    line_marker = str(entry["line_marker"])
    matching_lines = [
        line.strip()
        for line in layout_block.splitlines()
        if line.strip().startswith(line_marker)
    ]
    entry_line = matching_lines[0] if matching_lines else ""
    missing_summary_markers = [
        marker for marker in entry["summary_markers"] if marker not in entry_line
    ]
    evidence_paths = [str(path) for path in entry["evidence_paths"]]
    missing_evidence_paths = [
        path for path in evidence_paths if not (root / path).exists()
    ]
    layout_path_exists = (root / layout_path).exists()
    entry_status = (
        "entry_path_and_markers_present"
        if entry_line
        and layout_path_exists
        and not missing_summary_markers
        and not missing_evidence_paths
        else "entry_path_or_markers_missing"
    )
    return {
        "entry_id": entry["entry_id"],
        "layout_path": layout_path,
        "line_marker": line_marker,
        "entry_line": entry_line,
        "layout_path_exists": layout_path_exists,
        "missing_summary_markers": missing_summary_markers,
        "evidence_paths": evidence_paths,
        "missing_evidence_paths": missing_evidence_paths,
        "entry_status": entry_status,
    }


def _entry_has_marker(
    entry_records: list[dict[str, Any]],
    entry_id: str,
    marker: str,
) -> bool:
    for record in entry_records:
        if record["entry_id"] == entry_id:
            return marker in record["entry_line"]
    return False


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ReadmeRepositoryLayoutBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README repository-layout boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeRepositoryLayoutBoundaryIssue],
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
    issues: list[ReadmeRepositoryLayoutBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeRepositoryLayoutBoundaryIssue:
    return ReadmeRepositoryLayoutBoundaryIssue(code, message)
