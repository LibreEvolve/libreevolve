from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_INSTALL_SMOKE_BOUNDARY_SCHEMA = "libreevolve.readme_install_smoke_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "readme_editable_install_ci_markers_without_clean_transcript"
)
README_PATH = "README.md"
PYPROJECT_PATH = "pyproject.toml"
WORKFLOW_PATH = ".github/workflows/tests.yml"
DEVELOPMENT_PATH = "docs/development.md"
EXPECTED_INSTALL_COMMAND = 'py -3.12 -m pip install -e ".[dev]"'
EXPECTED_CI_INSTALL_COMMAND = 'python -m pip install -e ".[dev]"'
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_editable_install_command",
    "readme_python_launcher_guidance",
    "pyproject_python_requirement",
    "pyproject_dev_extra",
    "workflow_python_312_setup",
    "workflow_editable_install_commands",
    "development_guide_editable_install_command",
    "clean_environment_install_transcript",
    "python_pip_version_record",
    "dev_dependency_import_smoke",
    "install_failure_classification",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "clean_environment_install_transcript": "not_recorded_locally",
    "python_pip_version_record": "not_recorded_locally",
    "dev_dependency_import_smoke": "not_recorded_locally",
    "install_failure_classification": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeInstallSmokeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeInstallSmokeBoundaryValidation:
    ok: bool
    boundary_status: str | None
    ci_install_marker_count: int
    missing_marker_count: int
    missing_evidence_count: int
    issues: list[ReadmeInstallSmokeBoundaryIssue]


def readme_install_smoke_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the README editable-install smoke boundary record."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    pyproject_text = _read_text(root_path / PYPROJECT_PATH)
    workflow_text = _read_text(root_path / WORKFLOW_PATH)
    development_text = _read_text(root_path / DEVELOPMENT_PATH)
    marker_records = [
        _marker_record("readme_install_command", README_PATH, readme_text, EXPECTED_INSTALL_COMMAND),
        _marker_record("readme_python_launcher", README_PATH, readme_text, "use `py -3.12`, not `python`"),
        _marker_record("pyproject_python_requirement", PYPROJECT_PATH, pyproject_text, 'requires-python = ">=3.11"'),
        _marker_record("pyproject_dev_pytest", PYPROJECT_PATH, pyproject_text, "pytest>=8.0"),
        _marker_record("pyproject_dev_build", PYPROJECT_PATH, pyproject_text, "build>=1.2"),
        _marker_record("workflow_python_312", WORKFLOW_PATH, workflow_text, 'python-version: "3.12"'),
        _marker_record("workflow_editable_install", WORKFLOW_PATH, workflow_text, EXPECTED_CI_INSTALL_COMMAND),
        _marker_record("development_install_command", DEVELOPMENT_PATH, development_text, EXPECTED_INSTALL_COMMAND),
    ]
    missing_marker_records = [
        record for record in marker_records if record["marker_status"] != "marker_present"
    ]
    ci_install_marker_count = len(
        re.findall(re.escape(EXPECTED_CI_INSTALL_COMMAND), workflow_text)
    )
    return {
        "schema": README_INSTALL_SMOKE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "pyproject_path": PYPROJECT_PATH,
        "workflow_path": WORKFLOW_PATH,
        "development_path": DEVELOPMENT_PATH,
        "readme_install_command": EXPECTED_INSTALL_COMMAND,
        "ci_install_command": EXPECTED_CI_INSTALL_COMMAND,
        "ci_install_marker_count": ci_install_marker_count,
        "marker_record_count": len(marker_records),
        "missing_marker_count": len(missing_marker_records),
        "missing_marker_records": missing_marker_records,
        "marker_records": marker_records,
        "install_marker_status": (
            "readme_install_markers_present"
            if not missing_marker_records and ci_install_marker_count > 0
            else "readme_install_markers_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README editable-install command, Python "
            "launcher guidance, pyproject Python and dev-extra markers, GitHub "
            "Actions Python 3.12 setup plus editable-install commands, and the "
            "development-guide editable-install command. It does not claim a "
            "fresh clean-environment install transcript, Python and pip version "
            "record, dev-dependency import smoke, install-failure classification, "
            "or owner review signoff."
        ),
    }


def validate_readme_install_smoke_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeInstallSmokeBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_install_smoke_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeInstallSmokeBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = readme_install_smoke_boundary_record(root)
    issues: list[ReadmeInstallSmokeBoundaryIssue] = []
    if data.get("schema") != README_INSTALL_SMOKE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README install-smoke boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README install smoke boundary must not claim clean install proof"))
    for key in (
        "readme_path",
        "pyproject_path",
        "workflow_path",
        "development_path",
        "readme_install_command",
        "ci_install_command",
        "ci_install_marker_count",
        "marker_record_count",
        "missing_marker_count",
        "missing_marker_records",
        "marker_records",
        "install_marker_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current README install-smoke inputs"))
    if data.get("ci_install_marker_count", 0) <= 0:
        issues.append(_issue("missing_ci_install_marker", "workflow must include editable install command"))
    if data.get("missing_marker_count") != 0:
        issues.append(_issue("missing_install_marker", "README install-smoke markers are incomplete"))
    if data.get("install_marker_status") != "readme_install_markers_present":
        issues.append(_issue("invalid_install_marker_status", "README install markers must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README editable-install command" not in boundary_text
        or "GitHub Actions Python 3.12 setup" not in boundary_text
        or "does not claim a fresh clean-environment install transcript" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate README install markers from clean install proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmeInstallSmokeBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        ci_install_marker_count=data.get("ci_install_marker_count") if isinstance(data.get("ci_install_marker_count"), int) else 0,
        missing_marker_count=data.get("missing_marker_count") if isinstance(data.get("missing_marker_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_install_smoke_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_install_smoke_boundary(boundary)
    lines = [
        "README install smoke boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| ci_install_marker_count | {validation.ci_install_marker_count} |",
        f"| missing_marker_count | {validation.missing_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


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
) -> tuple[dict[str, Any] | None, list[ReadmeInstallSmokeBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README install-smoke boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeInstallSmokeBoundaryIssue],
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
    issues: list[ReadmeInstallSmokeBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeInstallSmokeBoundaryIssue:
    return ReadmeInstallSmokeBoundaryIssue(code, message)
