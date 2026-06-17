from __future__ import annotations

import json
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_TESTING_BOUNDARY_SCHEMA = "libreevolve.readme_testing_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "readme_testing_commands_structural_map_without_selection_transcript"
)
README_PATH = "README.md"
README_TODO_PATH = "docs/todo/readme.md"
PYPROJECT_PATH = "pyproject.toml"
WORKFLOW_PATH = ".github/workflows/tests.yml"
INTEGRATION_TEST_PATH = "tests/integration/test_hello_world.py"
AGENTS_TEST_PATH = "tests/test_agents_docs.py"
CI_BOUNDARY_PATH = "papers/ci_workflow_coverage_boundary.json"

README_NON_INTEGRATION_COMMAND = (
    'py -3.12 -m pytest tests/ -m "not integration" --tb=short'
)
README_INTEGRATION_COMMAND = (
    "py -3.12 -m pytest tests/integration/ -m integration --tb=short"
)
CI_NON_INTEGRATION_COMMAND = (
    'python -m pytest tests/ -m "not integration" --tb=short'
)
CI_INTEGRATION_COMMAND = (
    "python -m pytest tests/integration/ -m integration --tb=short -rs"
)
INTEGRATION_SKIP_MARKER = (
    '@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="no API key")'
)
EXPECTED_README_MARKERS = (
    ("testing_heading", "## Testing"),
    ("non_integration_intro", "Run the non-integration tests:"),
    ("non_integration_command", README_NON_INTEGRATION_COMMAND),
    (
        "integration_intro",
        "Run integration tests only when the required provider credentials are present:",
    ),
    ("integration_command", README_INTEGRATION_COMMAND),
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("pytest_testpaths", PYPROJECT_PATH, 'testpaths = ["tests"]'),
    (
        "pytest_integration_marker",
        PYPROJECT_PATH,
        "integration: marks tests requiring API keys",
    ),
    ("ci_non_integration_command", WORKFLOW_PATH, CI_NON_INTEGRATION_COMMAND),
    (
        "ci_integration_skip_message",
        WORKFLOW_PATH,
        "ANTHROPIC_API_KEY is not configured; skipping integration tests.",
    ),
    ("ci_integration_command", WORKFLOW_PATH, CI_INTEGRATION_COMMAND),
    ("integration_pytest_marker", INTEGRATION_TEST_PATH, "@pytest.mark.integration"),
    (
        "integration_skip_marker",
        INTEGRATION_TEST_PATH,
        INTEGRATION_SKIP_MARKER,
    ),
    (
        "agents_non_integration_command_anchor",
        AGENTS_TEST_PATH,
        README_NON_INTEGRATION_COMMAND,
    ),
    (
        "agents_workflow_integration_job_anchor",
        AGENTS_TEST_PATH,
        'assert "integration" in workflow["jobs"]',
    ),
    (
        "ci_workflow_boundary_optional_integration_anchor",
        CI_BOUNDARY_PATH,
        "optional credential-gated integration job",
    ),
    (
        "readme_todo_owner",
        README_TODO_PATH,
        "Add README testing-command marker and environment evidence.",
    ),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_testing_command_markers",
    "pytest_marker_registration",
    "ci_non_integration_command_anchor",
    "ci_credential_gated_integration_command_anchor",
    "integration_test_skip_markers",
    "agents_docs_command_anchor",
    "ci_workflow_boundary_anchor",
    "active_todo_owner_anchor",
    "python_pytest_version_transcript",
    "selected_non_integration_test_count",
    "selected_integration_test_count",
    "credential_skip_transcript",
    "failure_attribution_matrix",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "python_pytest_version_transcript": "not_recorded_locally",
    "selected_non_integration_test_count": "not_recorded_locally",
    "selected_integration_test_count": "not_recorded_locally",
    "credential_skip_transcript": "not_recorded_locally",
    "failure_attribution_matrix": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeTestingBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeTestingBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readme_marker_count: int
    missing_readme_marker_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    pytest_marker_count: int
    integration_test_marker_count: int
    credential_skip_marker_count: int
    missing_evidence_count: int
    issues: list[ReadmeTestingBoundaryIssue]


def readme_testing_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the README testing-command structural evidence map."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    integration_text = _read_text(root_path / INTEGRATION_TEST_PATH)
    texts = {
        path: _read_text(root_path / path)
        for path in (
            PYPROJECT_PATH,
            WORKFLOW_PATH,
            INTEGRATION_TEST_PATH,
            AGENTS_TEST_PATH,
            CI_BOUNDARY_PATH,
            README_TODO_PATH,
        )
    }
    readme_marker_records = [
        _marker_record(record_id, README_PATH, readme_text, marker)
        for record_id, marker in EXPECTED_README_MARKERS
    ]
    evidence_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_EVIDENCE_ANCHORS
    ]
    pytest_config = _pytest_config_record(root_path / PYPROJECT_PATH)
    command_records = [
        _command_record("readme_non_integration", README_PATH, readme_text, README_NON_INTEGRATION_COMMAND),
        _command_record("readme_integration", README_PATH, readme_text, README_INTEGRATION_COMMAND),
        _command_record("ci_non_integration", WORKFLOW_PATH, texts[WORKFLOW_PATH], CI_NON_INTEGRATION_COMMAND),
        _command_record("ci_integration", WORKFLOW_PATH, texts[WORKFLOW_PATH], CI_INTEGRATION_COMMAND),
    ]
    missing_readme_markers = [
        record for record in readme_marker_records if record["marker_status"] != "marker_present"
    ]
    missing_evidence_anchors = [
        record for record in evidence_anchor_records if record["marker_status"] != "marker_present"
    ]
    integration_test_marker_count = integration_text.count("@pytest.mark.integration")
    credential_skip_marker_count = integration_text.count(INTEGRATION_SKIP_MARKER)
    map_present = (
        not missing_readme_markers
        and not missing_evidence_anchors
        and pytest_config["testpaths"] == ["tests"]
        and "integration: marks tests requiring API keys" in pytest_config["markers"]
        and integration_test_marker_count == 2
        and credential_skip_marker_count == 2
        and all(record["command_status"] == "command_present" for record in command_records)
    )
    return {
        "schema": README_TESTING_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "pytest_config_path": PYPROJECT_PATH,
        "workflow_path": WORKFLOW_PATH,
        "integration_test_path": INTEGRATION_TEST_PATH,
        "agent_docs_test_path": AGENTS_TEST_PATH,
        "sidecar_paths": [CI_BOUNDARY_PATH],
        "todo_paths": [README_TODO_PATH],
        "readme_marker_count": len(readme_marker_records),
        "missing_readme_marker_count": len(missing_readme_markers),
        "missing_readme_marker_records": missing_readme_markers,
        "readme_marker_records": readme_marker_records,
        "command_record_count": len(command_records),
        "command_records": command_records,
        "pytest_config_record": pytest_config,
        "pytest_marker_count": len(pytest_config["markers"]),
        "integration_test_marker_count": integration_test_marker_count,
        "credential_skip_marker_count": credential_skip_marker_count,
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "readme_testing_map_status": (
            "readme_testing_structural_map_present"
            if map_present
            else "readme_testing_structural_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records README Testing command markers, pytest "
            "testpaths and integration marker registration, GitHub Actions "
            "non-integration and credential-gated integration commands, "
            "ANTHROPIC_API_KEY skip wiring, integration-test skip decorators, "
            "AGENTS.md command-test anchors, CI workflow sidecar anchors, and "
            "active TODO ownership. It does not claim Python/pytest version "
            "transcripts, selected non-integration or integration test counts, "
            "credential-skip transcript proof, a failure-attribution matrix, "
            "or owner review signoff."
        ),
    }


def validate_readme_testing_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeTestingBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_testing_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeTestingBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_testing_boundary_record(root)
    issues: list[ReadmeTestingBoundaryIssue] = []
    if data.get("schema") != README_TESTING_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README testing boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README testing boundary must not claim command transcript proof"))
    for key in (
        "readme_path",
        "pytest_config_path",
        "workflow_path",
        "integration_test_path",
        "agent_docs_test_path",
        "sidecar_paths",
        "todo_paths",
        "readme_marker_count",
        "missing_readme_marker_count",
        "missing_readme_marker_records",
        "readme_marker_records",
        "command_record_count",
        "command_records",
        "pytest_config_record",
        "pytest_marker_count",
        "integration_test_marker_count",
        "credential_skip_marker_count",
        "evidence_anchor_count",
        "missing_evidence_anchor_count",
        "missing_evidence_anchor_records",
        "evidence_anchor_records",
        "readme_testing_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current README testing inputs"))
    if data.get("missing_readme_marker_count") != 0:
        issues.append(_issue("missing_readme_testing_marker", "README testing command markers are incomplete"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_readme_testing_evidence_anchor", "README testing evidence anchors are incomplete"))
    if data.get("readme_testing_map_status") != "readme_testing_structural_map_present":
        issues.append(_issue("invalid_readme_testing_map_status", "README testing structural map must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README Testing command markers" not in boundary_text
        or "does not claim Python/pytest version transcripts" not in boundary_text
        or "credential-skip transcript proof" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate structural command evidence from transcript proof"))
    return ReadmeTestingBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readme_marker_count=data.get("readme_marker_count") if isinstance(data.get("readme_marker_count"), int) else 0,
        missing_readme_marker_count=data.get("missing_readme_marker_count") if isinstance(data.get("missing_readme_marker_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        pytest_marker_count=data.get("pytest_marker_count") if isinstance(data.get("pytest_marker_count"), int) else 0,
        integration_test_marker_count=data.get("integration_test_marker_count") if isinstance(data.get("integration_test_marker_count"), int) else 0,
        credential_skip_marker_count=data.get("credential_skip_marker_count") if isinstance(data.get("credential_skip_marker_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_testing_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_testing_boundary(boundary)
    lines = [
        "README testing boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| readme_marker_count | {validation.readme_marker_count} |",
        f"| missing_readme_marker_count | {validation.missing_readme_marker_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_evidence_anchor_count | {validation.missing_evidence_anchor_count} |",
        f"| pytest_marker_count | {validation.pytest_marker_count} |",
        f"| integration_test_marker_count | {validation.integration_test_marker_count} |",
        f"| credential_skip_marker_count | {validation.credential_skip_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _pytest_config_record(path: Path) -> dict[str, Any]:
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
        return {
            "path": PYPROJECT_PATH,
            "testpaths": [],
            "markers": [],
            "config_status": "pytest_config_unreadable_or_missing",
        }
    options = data.get("tool", {}).get("pytest", {}).get("ini_options", {})
    testpaths = options.get("testpaths", [])
    markers = options.get("markers", [])
    if not isinstance(testpaths, list):
        testpaths = []
    if not isinstance(markers, list):
        markers = []
    string_markers = [marker for marker in markers if isinstance(marker, str)]
    return {
        "path": PYPROJECT_PATH,
        "testpaths": [item for item in testpaths if isinstance(item, str)],
        "markers": string_markers,
        "integration_marker_registered": (
            "integration: marks tests requiring API keys" in string_markers
        ),
        "config_status": "pytest_config_recorded",
    }


def _command_record(
    command_id: str,
    path: str,
    text: str,
    command: str,
) -> dict[str, Any]:
    return {
        "command_id": command_id,
        "path": path,
        "command": command,
        "command_status": "command_present" if command in text else "command_missing",
    }


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
) -> tuple[dict[str, Any] | None, list[ReadmeTestingBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README testing boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeTestingBoundaryIssue],
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
    issues: list[ReadmeTestingBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeTestingBoundaryIssue:
    return ReadmeTestingBoundaryIssue(code, message)
