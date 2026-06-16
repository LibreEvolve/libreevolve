from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_PROVIDER_AUTH_BOUNDARY_SCHEMA = "libreevolve.readme_provider_auth_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "readme_provider_auth_static_markers_without_live_provider_proof"
)
ENV_EXAMPLE_PATH = ".env.example"
README_PATH = "README.md"
BACKENDS_PATH = "docs/backends.md"
CONFIGURATION_PATH = "docs/configuration.md"
DEVELOPMENT_PATH = "docs/development.md"
CLI_PATH = "libreevolve/cli.py"
WORKFLOW_PATH = ".github/workflows/tests.yml"
INTEGRATION_TEST_PATH = "tests/integration/test_hello_world.py"
SECRETS_BASELINE_PATH = ".secrets.baseline"
EXPECTED_PROVIDER_VARIABLES = {
    "OPENAI_API_KEY": "sk-your-openai-key-here",
    "ANTHROPIC_API_KEY": "sk-ant-your-anthropic-key-here",
    "OLLAMA_HOST": "http://localhost:11434",
}
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "env_example_provider_variables",
    "env_example_placeholder_safety",
    "readme_env_guidance",
    "backends_env_guidance",
    "configuration_env_guidance",
    "development_env_guidance",
    "cli_dotenv_override",
    "cli_credential_preflight",
    "integration_test_credential_skip",
    "github_actions_integration_secret",
    "secret_scan_baseline_marker",
    "backend_registry_auth_reflection",
    "live_provider_account_probe",
    "provider_auth_drift_ci_gate",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "backend_registry_auth_reflection": "not_recorded_locally",
    "live_provider_account_probe": "not_recorded_locally",
    "provider_auth_drift_ci_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeProviderAuthBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeProviderAuthBoundaryValidation:
    ok: bool
    boundary_status: str | None
    env_variable_count: int
    missing_marker_count: int
    unsafe_placeholder_count: int
    missing_evidence_count: int
    issues: list[ReadmeProviderAuthBoundaryIssue]


def readme_provider_auth_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the README provider-auth setup drift boundary record."""

    root_path = Path(root)
    texts = {
        ENV_EXAMPLE_PATH: _read_text(root_path / ENV_EXAMPLE_PATH),
        README_PATH: _read_text(root_path / README_PATH),
        BACKENDS_PATH: _read_text(root_path / BACKENDS_PATH),
        CONFIGURATION_PATH: _read_text(root_path / CONFIGURATION_PATH),
        DEVELOPMENT_PATH: _read_text(root_path / DEVELOPMENT_PATH),
        CLI_PATH: _read_text(root_path / CLI_PATH),
        WORKFLOW_PATH: _read_text(root_path / WORKFLOW_PATH),
        INTEGRATION_TEST_PATH: _read_text(root_path / INTEGRATION_TEST_PATH),
        SECRETS_BASELINE_PATH: _read_text(root_path / SECRETS_BASELINE_PATH),
    }
    env_records = _env_variable_records(texts[ENV_EXAMPLE_PATH])
    expected_env_records = [
        record for record in env_records if record["name"] in EXPECTED_PROVIDER_VARIABLES
    ]
    placeholder_records = [
        _placeholder_record(record["name"], record["value"])
        for record in expected_env_records
    ]
    marker_records = [
        _marker_record("readme_env_file", README_PATH, texts[README_PATH], "Optional provider credentials in `.env`"),
        _marker_record("readme_provider_failure_scope", README_PATH, texts[README_PATH], "credentials, model IDs, local Ollama state, or account access"),
        _marker_record("backends_openai_key", BACKENDS_PATH, texts[BACKENDS_PATH], "OPENAI_API_KEY=..."),
        _marker_record("backends_anthropic_key", BACKENDS_PATH, texts[BACKENDS_PATH], "ANTHROPIC_API_KEY=..."),
        _marker_record("backends_ollama_host", BACKENDS_PATH, texts[BACKENDS_PATH], "OLLAMA_HOST=http://localhost:11434"),
        _marker_record("backends_override_true", BACKENDS_PATH, texts[BACKENDS_PATH], "override=True"),
        _marker_record("configuration_dotenv_override", CONFIGURATION_PATH, texts[CONFIGURATION_PATH], "override=True"),
        _marker_record("configuration_provider_env_names", CONFIGURATION_PATH, texts[CONFIGURATION_PATH], "OPENAI_API_KEY"),
        _marker_record("configuration_anthropic_env_name", CONFIGURATION_PATH, texts[CONFIGURATION_PATH], "ANTHROPIC_API_KEY"),
        _marker_record("configuration_ollama_env_name", CONFIGURATION_PATH, texts[CONFIGURATION_PATH], "OLLAMA_HOST"),
        _marker_record("development_env_block", DEVELOPMENT_PATH, texts[DEVELOPMENT_PATH], "Create a `.env` file in the repository root"),
        _marker_record("cli_dotenv_load", CLI_PATH, texts[CLI_PATH], "load_dotenv(dotenv_path=path, override=True)"),
        _marker_record("cli_required_env", CLI_PATH, texts[CLI_PATH], '"openai": "OPENAI_API_KEY"'),
        _marker_record("cli_required_anthropic_env", CLI_PATH, texts[CLI_PATH], '"anthropic": "ANTHROPIC_API_KEY"'),
        _marker_record("workflow_anthropic_secret", WORKFLOW_PATH, texts[WORKFLOW_PATH], "secrets.ANTHROPIC_API_KEY"),
        _marker_record("integration_anthropic_skip", INTEGRATION_TEST_PATH, texts[INTEGRATION_TEST_PATH], 'os.getenv("ANTHROPIC_API_KEY")'),
        _marker_record("secret_scan_baseline", SECRETS_BASELINE_PATH, texts[SECRETS_BASELINE_PATH], '"plugins_used"'),
    ]
    env_missing_records = [
        {
            "name": name,
            "expected_value": expected_value,
            "record_status": "env_variable_missing",
        }
        for name, expected_value in EXPECTED_PROVIDER_VARIABLES.items()
        if not any(
            record["name"] == name and record["value"] == expected_value
            for record in env_records
        )
    ]
    missing_marker_records = [
        record for record in marker_records if record["marker_status"] != "marker_present"
    ]
    unsafe_placeholder_records = [
        record for record in placeholder_records if record["placeholder_status"] != "placeholder_safe"
    ]
    return {
        "schema": README_PROVIDER_AUTH_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "env_example_path": ENV_EXAMPLE_PATH,
        "readme_path": README_PATH,
        "docs_paths": [BACKENDS_PATH, CONFIGURATION_PATH, DEVELOPMENT_PATH],
        "code_paths": [CLI_PATH, INTEGRATION_TEST_PATH],
        "workflow_path": WORKFLOW_PATH,
        "secret_scan_path": SECRETS_BASELINE_PATH,
        "expected_provider_variables": dict(EXPECTED_PROVIDER_VARIABLES),
        "env_variable_count": len(expected_env_records),
        "env_variable_records": expected_env_records,
        "env_missing_count": len(env_missing_records),
        "env_missing_records": env_missing_records,
        "placeholder_records": placeholder_records,
        "unsafe_placeholder_count": len(unsafe_placeholder_records),
        "unsafe_placeholder_records": unsafe_placeholder_records,
        "marker_record_count": len(marker_records),
        "missing_marker_count": len(missing_marker_records),
        "missing_marker_records": missing_marker_records,
        "marker_records": marker_records,
        "provider_auth_marker_status": (
            "provider_auth_static_markers_present"
            if not env_missing_records
            and not missing_marker_records
            and not unsafe_placeholder_records
            else "provider_auth_static_markers_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the .env.example provider variables, "
            "placeholder safety, README provider-auth guidance, backend, "
            "configuration, and development-guide dotenv markers, CLI dotenv "
            "override and credential-preflight markers, integration-test "
            "credential skip markers, GitHub Actions Anthropic secret markers, "
            "and the secret-scan baseline marker. It does not claim complete "
            "backend-registry auth reflection, live provider account probes, a "
            "provider-auth drift CI gate, or owner review signoff."
        ),
    }


def validate_readme_provider_auth_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeProviderAuthBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_provider_auth_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeProviderAuthBoundaryValidation(False, None, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = readme_provider_auth_boundary_record(root)
    issues: list[ReadmeProviderAuthBoundaryIssue] = []
    if data.get("schema") != README_PROVIDER_AUTH_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README provider-auth boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README provider-auth boundary must not claim live provider proof"))
    for key in (
        "env_example_path",
        "readme_path",
        "docs_paths",
        "code_paths",
        "workflow_path",
        "secret_scan_path",
        "expected_provider_variables",
        "env_variable_count",
        "env_variable_records",
        "env_missing_count",
        "env_missing_records",
        "placeholder_records",
        "unsafe_placeholder_count",
        "unsafe_placeholder_records",
        "marker_record_count",
        "missing_marker_count",
        "missing_marker_records",
        "marker_records",
        "provider_auth_marker_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current provider-auth inputs"))
    if data.get("env_variable_count") != len(EXPECTED_PROVIDER_VARIABLES):
        issues.append(_issue("invalid_env_variable_count", "all expected provider variables must be recorded"))
    if data.get("env_missing_count") != 0:
        issues.append(_issue("missing_env_variable", ".env.example provider variables are incomplete"))
    if data.get("missing_marker_count") != 0:
        issues.append(_issue("missing_provider_auth_marker", "provider-auth markers are incomplete"))
    if data.get("unsafe_placeholder_count") != 0:
        issues.append(_issue("unsafe_provider_placeholder", ".env.example contains unsafe provider placeholders"))
    if data.get("provider_auth_marker_status") != "provider_auth_static_markers_present":
        issues.append(_issue("invalid_provider_auth_marker_status", "provider-auth static markers must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or ".env.example provider variables" not in boundary_text
        or "CLI dotenv override and credential-preflight markers" not in boundary_text
        or "does not claim complete backend-registry auth reflection" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate provider-auth markers from live provider proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmeProviderAuthBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        env_variable_count=data.get("env_variable_count") if isinstance(data.get("env_variable_count"), int) else 0,
        missing_marker_count=data.get("missing_marker_count") if isinstance(data.get("missing_marker_count"), int) else 0,
        unsafe_placeholder_count=data.get("unsafe_placeholder_count") if isinstance(data.get("unsafe_placeholder_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_provider_auth_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_provider_auth_boundary(boundary)
    lines = [
        "README provider-auth boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| env_variable_count | {validation.env_variable_count} |",
        f"| missing_marker_count | {validation.missing_marker_count} |",
        f"| unsafe_placeholder_count | {validation.unsafe_placeholder_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _env_variable_records(text: str) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for index, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.split("=", 1)
        records.append(
            {
                "line": index,
                "name": name.strip(),
                "value": value.strip(),
                "record_status": "env_variable_recorded",
            }
        )
    return records


def _placeholder_record(name: str, value: str) -> dict[str, Any]:
    safe = (
        value in EXPECTED_PROVIDER_VARIABLES.values()
        and (value.startswith("sk-your-") or value.startswith("sk-ant-your-") or value == "http://localhost:11434")
    )
    return {
        "name": name,
        "value": value,
        "placeholder_status": "placeholder_safe" if safe else "placeholder_unsafe",
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
) -> tuple[dict[str, Any] | None, list[ReadmeProviderAuthBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README provider-auth boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeProviderAuthBoundaryIssue],
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
    issues: list[ReadmeProviderAuthBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeProviderAuthBoundaryIssue:
    return ReadmeProviderAuthBoundaryIssue(code, message)
