from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEVELOPMENT_WORKFLOW_BOUNDARY_SCHEMA = "libreevolve.development_workflow_boundary.v1"
EXPECTED_BOUNDARY_STATUS = "development_workflow_static_inventory_without_semantic_drift_gate"
DEVELOPMENT_DOC_PATH = "docs/development.md"
PYPROJECT_PATH = "pyproject.toml"
PRECOMMIT_PATH = ".pre-commit-config.yaml"
WORKFLOW_PATH = ".github/workflows/tests.yml"
README_PATH = "README.md"
DOCS_INDEX_PATH = "docs/README.md"
RELEASE_CHECKLIST_PATH = "docs/release-checklist.md"
RUN_ARTIFACTS_PATH = "docs/run-artifacts.md"
PAPERS_README_PATH = "papers/README.md"
AGENTS_TEST_PATH = "tests/test_agents_docs.py"
README_TODO_PATH = "docs/todo/readme.md"

EXPECTED_DEVELOPMENT_MARKERS = (
    ("python_version_launcher", DEVELOPMENT_DOC_PATH, "py -3.12"),
    ("editable_dev_install", DEVELOPMENT_DOC_PATH, 'py -3.12 -m pip install -e ".[dev]"'),
    ("precommit_install", DEVELOPMENT_DOC_PATH, "py -3.12 -m pre_commit install"),
    ("dotenv_override", DEVELOPMENT_DOC_PATH, "loads `.env` during run setup with `override=True`"),
    ("unit_test_command", DEVELOPMENT_DOC_PATH, 'py -3.12 -m pytest tests/ -m "not integration" --tb=short'),
    ("integration_test_command", DEVELOPMENT_DOC_PATH, "py -3.12 -m pytest tests/integration/ -m integration"),
    ("precommit_run_command", DEVELOPMENT_DOC_PATH, "py -3.12 -m pre_commit run --all-files"),
    ("diff_check_command", DEVELOPMENT_DOC_PATH, "git diff --check"),
    ("paper_manifest_rehydrate", DEVELOPMENT_DOC_PATH, "py -3.12 -m libreevolve.tools.paper_manifest --rehydrate"),
    ("paper_manifest_validate", DEVELOPMENT_DOC_PATH, "py -3.12 -m libreevolve.tools.paper_manifest"),
    ("paper_manifest_require_local_pdfs", DEVELOPMENT_DOC_PATH, "py -3.12 -m libreevolve.tools.paper_manifest --require-local-pdfs"),
    ("paper_manifest_json", DEVELOPMENT_DOC_PATH, "use `--json` when auditing"),
    ("release_checklist_route", DEVELOPMENT_DOC_PATH, "[docs/release-checklist.md](release-checklist.md)"),
    ("ci_path_scope", DEVELOPMENT_DOC_PATH, "path-scoped\n`push` / `pull_request` events"),
    ("secret_scan_baseline", DEVELOPMENT_DOC_PATH, "The secret scan uses `.secrets.baseline`."),
    ("repository_conventions", DEVELOPMENT_DOC_PATH, "## Repository conventions"),
    ("suggested_docs_architecture", DEVELOPMENT_DOC_PATH, "[Architecture](./architecture.md)"),
    ("suggested_docs_problem_format", DEVELOPMENT_DOC_PATH, "[Problem Format](./problem-format.md)"),
    ("suggested_docs_configuration", DEVELOPMENT_DOC_PATH, "[Configuration](./configuration.md)"),
    ("suggested_docs_plugins", DEVELOPMENT_DOC_PATH, "[Plugins](./plugins.md)"),
)
EXPECTED_RUNTIME_DEPENDENCY_MARKERS = (
    "numpy",
    "scikit-learn",
    "anthropic",
    "openai",
    "ollama",
    "pyyaml",
    "click",
    "python-dotenv",
    "packaging",
    "pypdf",
)
EXPECTED_DEV_DEPENDENCY_MARKERS = (
    "pytest",
    "pytest-mock",
    "pre-commit",
    "detect-secrets",
)
EXPECTED_TOOL_ANCHORS = (
    ("pyproject_python_requirement", PYPROJECT_PATH, 'requires-python = ">=3.11"'),
    ("pyproject_dev_extra", PYPROJECT_PATH, "[project.optional-dependencies]"),
    ("pyproject_console_script", PYPROJECT_PATH, 'libreevolve = "libreevolve.cli:cli"'),
    ("precommit_detect_secrets", PRECOMMIT_PATH, "detect-secrets"),
    ("precommit_baseline", PRECOMMIT_PATH, ".secrets.baseline"),
    ("workflow_path_docs", WORKFLOW_PATH, '"docs/**"'),
    ("workflow_path_papers", WORKFLOW_PATH, '"papers/**"'),
    ("workflow_path_todo", WORKFLOW_PATH, '"tests/**"'),
    ("workflow_secret_scan", WORKFLOW_PATH, "Run detect-secrets"),
    ("workflow_unit_tests", WORKFLOW_PATH, 'python -m pytest tests/ -m "not integration" --tb=short'),
    ("workflow_paper_manifest", WORKFLOW_PATH, "python -m libreevolve.tools.paper_manifest --root ."),
    ("workflow_boundary_tests", WORKFLOW_PATH, 'Path("tests").glob("test_*boundary.py")'),
    ("workflow_release_artifact", WORKFLOW_PATH, "Release Artifact Smoke"),
    ("workflow_integration_skip", WORKFLOW_PATH, "ANTHROPIC_API_KEY is not configured; skipping integration tests."),
)
EXPECTED_CROSS_DOC_ANCHORS = (
    ("readme_operational_docs_scope", README_PATH, "operational details belong in `docs/`"),
    ("docs_index_development_route", DOCS_INDEX_PATH, "[Development](./development.md)"),
    ("release_checklist_local_scope", RELEASE_CHECKLIST_PATH, "## Required Local Evidence"),
    ("run_artifacts_release_scope", RUN_ARTIFACTS_PATH, "release-smoke checklist exist"),
    ("papers_release_checklist_sidecar", PAPERS_README_PATH, "papers/release_checklist_documentation_boundary.json"),
    ("papers_ci_sidecar", PAPERS_README_PATH, "papers/ci_workflow_coverage_boundary.json"),
    ("agents_detect_secrets_test", AGENTS_TEST_PATH, "test_development_docs_track_detect_secrets_baseline_workflow"),
    ("agents_workflow_test", AGENTS_TEST_PATH, "test_tests_workflow_covers_docs_papers_and_todo_changes"),
    ("active_todo_owner", README_TODO_PATH, "Add development-guide workflow and convention drift evidence."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "development_doc_workflow_markers",
    "development_doc_runtime_dependency_markers",
    "development_doc_dev_dependency_markers",
    "pyproject_dependency_and_script_anchors",
    "precommit_secret_scan_anchor",
    "github_actions_path_and_job_anchors",
    "paper_manifest_command_anchors",
    "release_checklist_and_run_artifact_anchors",
    "suggested_contributor_doc_routes",
    "focused_agent_doc_tests",
    "active_todo_owner_anchor",
    "per_command_executable_transcripts",
    "dependency_version_semantic_map",
    "ci_path_filter_semantic_map",
    "paper_manifest_fresh_checkout_transcript",
    "release_smoke_transcript",
    "repository_convention_source_map",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "per_command_executable_transcripts": "not_recorded_locally",
    "dependency_version_semantic_map": "not_recorded_locally",
    "ci_path_filter_semantic_map": "not_recorded_locally",
    "paper_manifest_fresh_checkout_transcript": "not_recorded_locally",
    "release_smoke_transcript": "not_recorded_locally",
    "repository_convention_source_map": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class DevelopmentWorkflowBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class DevelopmentWorkflowBoundaryValidation:
    ok: bool
    boundary_status: str | None
    development_marker_count: int
    runtime_dependency_marker_count: int
    dev_dependency_marker_count: int
    tool_anchor_count: int
    cross_doc_anchor_count: int
    missing_marker_count: int
    missing_evidence_count: int
    issues: list[DevelopmentWorkflowBoundaryIssue]


def development_workflow_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return a static inventory for the development guide workflow contract."""

    root_path = Path(root)
    development_text = _read_text(root_path / DEVELOPMENT_DOC_PATH)
    texts = {
        path: _read_text(root_path / path)
        for path in (
            DEVELOPMENT_DOC_PATH,
            PYPROJECT_PATH,
            PRECOMMIT_PATH,
            WORKFLOW_PATH,
            README_PATH,
            DOCS_INDEX_PATH,
            RELEASE_CHECKLIST_PATH,
            RUN_ARTIFACTS_PATH,
            PAPERS_README_PATH,
            AGENTS_TEST_PATH,
            README_TODO_PATH,
        )
    }
    development_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_DEVELOPMENT_MARKERS
    ]
    runtime_dependency_records = [
        _marker_record(f"runtime_dependency_{marker}", DEVELOPMENT_DOC_PATH, development_text, marker)
        for marker in EXPECTED_RUNTIME_DEPENDENCY_MARKERS
    ]
    dev_dependency_records = [
        _marker_record(f"dev_dependency_{marker}", DEVELOPMENT_DOC_PATH, development_text, marker)
        for marker in EXPECTED_DEV_DEPENDENCY_MARKERS
    ]
    tool_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_TOOL_ANCHORS
    ]
    cross_doc_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_CROSS_DOC_ANCHORS
    ]
    all_marker_records = (
        development_records
        + runtime_dependency_records
        + dev_dependency_records
        + tool_anchor_records
        + cross_doc_anchor_records
    )
    missing_marker_records = [
        record for record in all_marker_records if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": DEVELOPMENT_WORKFLOW_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "development_doc_path": DEVELOPMENT_DOC_PATH,
        "pyproject_path": PYPROJECT_PATH,
        "precommit_path": PRECOMMIT_PATH,
        "workflow_path": WORKFLOW_PATH,
        "development_marker_count": len(development_records),
        "development_marker_records": development_records,
        "runtime_dependency_marker_count": len(runtime_dependency_records),
        "runtime_dependency_marker_records": runtime_dependency_records,
        "dev_dependency_marker_count": len(dev_dependency_records),
        "dev_dependency_marker_records": dev_dependency_records,
        "tool_anchor_count": len(tool_anchor_records),
        "tool_anchor_records": tool_anchor_records,
        "cross_doc_anchor_count": len(cross_doc_anchor_records),
        "cross_doc_anchor_records": cross_doc_anchor_records,
        "missing_marker_count": len(missing_marker_records),
        "missing_marker_records": missing_marker_records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records static docs/development.md workflow markers "
            "for Python launcher guidance, editable install, pre-commit setup, "
            ".env behavior, test/pre-commit/diff/paper-manifest commands, CI "
            "scope, release-checklist routing, dependency lists, repository "
            "conventions, suggested contributor docs, pyproject/pre-commit/"
            "workflow anchors, focused agent-doc tests, and active TODO "
            "ownership. It does not claim per-command executable transcripts, "
            "dependency-version semantic parity, CI path-filter semantic proof, "
            "fresh-checkout paper-manifest transcripts, release-smoke "
            "transcripts, repository-convention source mapping, or owner review "
            "signoff."
        ),
    }


def validate_development_workflow_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> DevelopmentWorkflowBoundaryValidation:
    data, read_issues = _load_boundary(
        development_workflow_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return DevelopmentWorkflowBoundaryValidation(False, None, 0, 0, 0, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = development_workflow_boundary_record(root)
    issues: list[DevelopmentWorkflowBoundaryIssue] = []
    if data.get("schema") != DEVELOPMENT_WORKFLOW_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported development workflow boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "development workflow boundary must not claim semantic drift proof"))
    for key in (
        "development_doc_path",
        "pyproject_path",
        "precommit_path",
        "workflow_path",
        "development_marker_count",
        "development_marker_records",
        "runtime_dependency_marker_count",
        "runtime_dependency_marker_records",
        "dev_dependency_marker_count",
        "dev_dependency_marker_records",
        "tool_anchor_count",
        "tool_anchor_records",
        "cross_doc_anchor_count",
        "cross_doc_anchor_records",
        "missing_marker_count",
        "missing_marker_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current development workflow inputs"))
    if data.get("development_marker_count") != len(EXPECTED_DEVELOPMENT_MARKERS):
        issues.append(_issue("invalid_development_marker_count", "development workflow markers changed"))
    if data.get("runtime_dependency_marker_count") != len(EXPECTED_RUNTIME_DEPENDENCY_MARKERS):
        issues.append(_issue("invalid_runtime_dependency_marker_count", "runtime dependency markers changed"))
    if data.get("dev_dependency_marker_count") != len(EXPECTED_DEV_DEPENDENCY_MARKERS):
        issues.append(_issue("invalid_dev_dependency_marker_count", "development dependency markers changed"))
    if data.get("missing_marker_count") != 0:
        issues.append(_issue("missing_development_workflow_marker", "development workflow evidence anchors are incomplete"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "static docs/development.md workflow markers" not in boundary_text
        or "does not claim per-command executable transcripts" not in boundary_text
        or "owner review signoff" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate static workflow markers from semantic drift proof"))
    return DevelopmentWorkflowBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        development_marker_count=data.get("development_marker_count") if isinstance(data.get("development_marker_count"), int) else 0,
        runtime_dependency_marker_count=data.get("runtime_dependency_marker_count") if isinstance(data.get("runtime_dependency_marker_count"), int) else 0,
        dev_dependency_marker_count=data.get("dev_dependency_marker_count") if isinstance(data.get("dev_dependency_marker_count"), int) else 0,
        tool_anchor_count=data.get("tool_anchor_count") if isinstance(data.get("tool_anchor_count"), int) else 0,
        cross_doc_anchor_count=data.get("cross_doc_anchor_count") if isinstance(data.get("cross_doc_anchor_count"), int) else 0,
        missing_marker_count=data.get("missing_marker_count") if isinstance(data.get("missing_marker_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_development_workflow_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_development_workflow_boundary(boundary)
    lines = [
        "Development workflow boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| development_marker_count | {validation.development_marker_count} |",
        f"| runtime_dependency_marker_count | {validation.runtime_dependency_marker_count} |",
        f"| dev_dependency_marker_count | {validation.dev_dependency_marker_count} |",
        f"| tool_anchor_count | {validation.tool_anchor_count} |",
        f"| cross_doc_anchor_count | {validation.cross_doc_anchor_count} |",
        f"| missing_marker_count | {validation.missing_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _marker_record(record_id: str, path: str, text: str, marker: str) -> dict[str, Any]:
    return {
        "record_id": record_id,
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
) -> tuple[dict[str, Any] | None, list[DevelopmentWorkflowBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "development workflow boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[DevelopmentWorkflowBoundaryIssue],
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
    issues: list[DevelopmentWorkflowBoundaryIssue],
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


def _issue(code: str, message: str) -> DevelopmentWorkflowBoundaryIssue:
    return DevelopmentWorkflowBoundaryIssue(code, message)
