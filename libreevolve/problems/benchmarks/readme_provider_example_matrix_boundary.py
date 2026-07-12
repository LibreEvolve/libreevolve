from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_PROVIDER_EXAMPLE_MATRIX_BOUNDARY_SCHEMA = (
    "libreevolve.readme_provider_example_matrix_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "readme_provider_examples_static_matrix_without_live_provider_smoke"
)
README_PATH = "README.md"
BACKENDS_PATH = "docs/backends.md"
CONFIGURATION_PATH = "docs/configuration.md"
ENV_EXAMPLE_PATH = ".env.example"
CLI_PATH = "libreevolve/cli.py"
CONFIG_PATH = "libreevolve/core/config.py"
INTEGRATION_TEST_PATH = "tests/integration/test_hello_world.py"
EXPECTED_PROVIDER_COMMANDS = (
    {
        "provider": "openai",
        "path": README_PATH,
        "marker": (
            'py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world '
            '--max-generations 10 --backends "openai:<openai-model-id>"'
        ),
        "placeholder": "<openai-model-id>",
        "required_env": "OPENAI_API_KEY",
    },
    {
        "provider": "anthropic",
        "path": README_PATH,
        "marker": (
            'py -3.12 -m libreevolve run libreevolve/problems/examples/sorting '
            '--max-generations 10 --backends "anthropic:<anthropic-model-id>"'
        ),
        "placeholder": "<anthropic-model-id>",
        "required_env": "ANTHROPIC_API_KEY",
    },
    {
        "provider": "gemini",
        "path": README_PATH,
        "marker": (
            'py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world '
            '--max-generations 10 --backends "gemini:<gemini-model-id>"'
        ),
        "placeholder": "<gemini-model-id>",
        "required_env": "GOOGLE_API_KEY or GEMINI_API_KEY",
    },
    {
        "provider": "ollama",
        "path": README_PATH,
        "marker": (
            'py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world '
            '--max-generations 10 --backends "ollama:<installed-ollama-model>"'
        ),
        "placeholder": "<installed-ollama-model>",
        "required_env": "OLLAMA_HOST",
    },
)
EXPECTED_CONTRACT_MARKERS = (
    {
        "record_kind": "readme_account_model_guidance",
        "path": README_PATH,
        "marker": "available in\nyour account or local Ollama install",
    },
    {
        "record_kind": "readme_provider_failure_scope",
        "path": README_PATH,
        "marker": "credentials, model IDs, local Ollama state, or account access",
    },
    {
        "record_kind": "env_openai_placeholder",
        "path": ENV_EXAMPLE_PATH,
        "marker": "OPENAI_API_KEY=sk-your-openai-key-here",
    },
    {
        "record_kind": "env_anthropic_placeholder",
        "path": ENV_EXAMPLE_PATH,
        "marker": "ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here",
    },
    {
        "record_kind": "env_gemini_placeholder",
        "path": ENV_EXAMPLE_PATH,
        "marker": "GEMINI_API_KEY=your-gemini-key-here",
    },
    {
        "record_kind": "env_ollama_host_placeholder",
        "path": ENV_EXAMPLE_PATH,
        "marker": "OLLAMA_HOST=http://localhost:11434",
    },
    {
        "record_kind": "cli_backend_shorthand",
        "path": CLI_PATH,
        "marker": 'bd = [{"type": t, "model": m} for b in backends for t, _, m in [b.partition(":")]]',
    },
    {
        "record_kind": "cli_openai_preflight_env",
        "path": CLI_PATH,
        "marker": '"openai": "OPENAI_API_KEY"',
    },
    {
        "record_kind": "cli_anthropic_preflight_env",
        "path": CLI_PATH,
        "marker": '"anthropic": "ANTHROPIC_API_KEY"',
    },
    {
        "record_kind": "cli_gemini_preflight_env",
        "path": CLI_PATH,
        "marker": '("GOOGLE_API_KEY", "GEMINI_API_KEY")',
    },
    {
        "record_kind": "config_custom_class_path",
        "path": CONFIG_PATH,
        "marker": "_require_custom_backend_class_path",
    },
    {
        "record_kind": "config_custom_kwargs",
        "path": CONFIG_PATH,
        "marker": "_validate_custom_backend_kwargs",
    },
    {
        "record_kind": "backends_custom_class_path_doc",
        "path": BACKENDS_PATH,
        "marker": "Configured custom backends use `type: custom` plus an importable\n`class_path`",
    },
    {
        "record_kind": "backends_custom_kwargs_doc",
        "path": BACKENDS_PATH,
        "marker": "optional JSON-safe `kwargs`",
    },
    {
        "record_kind": "configuration_backend_shorthand_doc",
        "path": CONFIGURATION_PATH,
        "marker": "`--backends`, `-b` as `type:model`",
    },
    {
        "record_kind": "configuration_backend_placeholder_doc",
        "path": CONFIGURATION_PATH,
        "marker": "openai:<openai-model-id>",
    },
    {
        "record_kind": "integration_anthropic_only_skip",
        "path": INTEGRATION_TEST_PATH,
        "marker": 'os.getenv("ANTHROPIC_API_KEY")',
    },
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_provider_command_markers",
    "readme_account_model_guidance",
    "readme_provider_failure_scope",
    "env_example_provider_placeholders",
    "cli_backend_shorthand_contract",
    "cli_builtin_provider_env_preflight",
    "config_custom_backend_class_path_contract",
    "docs_custom_backend_contract",
    "configuration_backend_shorthand_contract",
    "integration_anthropic_skip_marker",
    "live_openai_model_availability_probe",
    "live_anthropic_model_availability_probe",
    "live_gemini_model_availability_probe",
    "live_ollama_inventory_probe",
    "credential_safe_provider_smoke_matrix",
    "account_specific_model_id_provenance",
    "ci_provider_matrix",
    "live_gemini_flash_pro_pair_evidence",
)
EXPECTED_MISSING_EVIDENCE = {
    "live_openai_model_availability_probe": "not_recorded_locally",
    "live_anthropic_model_availability_probe": "not_recorded_locally",
    "live_gemini_model_availability_probe": "not_recorded_locally",
    "live_ollama_inventory_probe": "not_recorded_locally",
    "credential_safe_provider_smoke_matrix": "not_recorded_locally",
    "account_specific_model_id_provenance": "not_recorded_locally",
    "ci_provider_matrix": "not_recorded_locally",
    "live_gemini_flash_pro_pair_evidence": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeProviderExampleMatrixBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeProviderExampleMatrixBoundaryValidation:
    ok: bool
    boundary_status: str | None
    provider_command_record_count: int
    missing_provider_command_record_count: int
    contract_marker_record_count: int
    missing_contract_marker_count: int
    missing_evidence_count: int
    issues: list[ReadmeProviderExampleMatrixBoundaryIssue]


def readme_provider_example_matrix_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the README provider-example smoke-matrix boundary record."""

    root_path = Path(root)
    paths = {
        README_PATH,
        BACKENDS_PATH,
        CONFIGURATION_PATH,
        ENV_EXAMPLE_PATH,
        CLI_PATH,
        CONFIG_PATH,
        INTEGRATION_TEST_PATH,
    }
    texts = {path: _read_text(root_path / path) for path in paths}
    command_records = [
        _provider_command_record(
            provider=spec["provider"],
            path=spec["path"],
            text=texts[spec["path"]],
            marker=spec["marker"],
            placeholder=spec["placeholder"],
            required_env=spec["required_env"],
        )
        for spec in EXPECTED_PROVIDER_COMMANDS
    ]
    contract_records = [
        _marker_record(
            spec["record_kind"],
            spec["path"],
            texts[spec["path"]],
            spec["marker"],
        )
        for spec in EXPECTED_CONTRACT_MARKERS
    ]
    missing_command_records = [
        record
        for record in command_records
        if record["command_marker_status"] != "command_marker_present"
    ]
    missing_contract_records = [
        record
        for record in contract_records
        if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": README_PROVIDER_EXAMPLE_MATRIX_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "docs_paths": [BACKENDS_PATH, CONFIGURATION_PATH],
        "code_paths": [CLI_PATH, CONFIG_PATH, INTEGRATION_TEST_PATH],
        "env_example_path": ENV_EXAMPLE_PATH,
        "provider_command_record_count": len(command_records),
        "missing_provider_command_record_count": len(missing_command_records),
        "missing_provider_command_records": missing_command_records,
        "provider_command_records": command_records,
        "contract_marker_record_count": len(contract_records),
        "missing_contract_marker_count": len(missing_contract_records),
        "missing_contract_marker_records": missing_contract_records,
        "contract_marker_records": contract_records,
        "provider_example_matrix_status": (
            "readme_provider_example_static_contract_present"
            if not missing_command_records and not missing_contract_records
            else "readme_provider_example_static_contract_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README OpenAI, Anthropic, Gemini, and Ollama "
            "placeholder command markers, README account/local-model guidance, "
            "provider failure-scope wording, .env.example provider placeholders, "
            "CLI type:model backend-shorthand construction and built-in "
            "credential preflight markers, config and docs custom-backend "
            "class_path/kwargs contract markers, configuration-guide shorthand "
            "markers, and the Anthropic-only credential-gated integration-test "
            "skip marker. It does not claim live OpenAI model availability, "
            "live Anthropic or Gemini model availability, local Ollama inventory, a "
            "credential-safe provider smoke matrix, account-specific model-id "
            "provenance, a CI provider matrix, or live Gemini Flash/Pro pair evidence."
        ),
    }


def validate_readme_provider_example_matrix_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeProviderExampleMatrixBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_provider_example_matrix_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return ReadmeProviderExampleMatrixBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_provider_example_matrix_boundary_record(root)
    issues: list[ReadmeProviderExampleMatrixBoundaryIssue] = []
    if data.get("schema") != README_PROVIDER_EXAMPLE_MATRIX_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README provider example matrix boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README provider example matrix must not claim live provider smoke proof"))
    for key in (
        "readme_path",
        "docs_paths",
        "code_paths",
        "env_example_path",
        "provider_command_record_count",
        "missing_provider_command_record_count",
        "missing_provider_command_records",
        "provider_command_records",
        "contract_marker_record_count",
        "missing_contract_marker_count",
        "missing_contract_marker_records",
        "contract_marker_records",
        "provider_example_matrix_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current README provider-example inputs"))
    if data.get("provider_command_record_count") != len(EXPECTED_PROVIDER_COMMANDS):
        issues.append(_issue("invalid_provider_command_record_count", "all expected provider README commands must be recorded"))
    if data.get("missing_provider_command_record_count") != 0:
        issues.append(_issue("missing_provider_command_marker", "README provider command markers are incomplete"))
    if data.get("missing_contract_marker_count") != 0:
        issues.append(_issue("missing_provider_contract_marker", "provider example contract markers are incomplete"))
    if data.get("provider_example_matrix_status") != "readme_provider_example_static_contract_present":
        issues.append(_issue("invalid_provider_example_matrix_status", "README provider example static contract must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README OpenAI, Anthropic, Gemini, and Ollama placeholder command markers" not in boundary_text
        or "CLI type:model backend-shorthand construction" not in boundary_text
        or "does not claim live OpenAI model availability" not in boundary_text
        or "live Gemini Flash/Pro pair evidence" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate static provider examples from live provider smoke proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmeProviderExampleMatrixBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        provider_command_record_count=data.get("provider_command_record_count") if isinstance(data.get("provider_command_record_count"), int) else 0,
        missing_provider_command_record_count=data.get("missing_provider_command_record_count") if isinstance(data.get("missing_provider_command_record_count"), int) else 0,
        contract_marker_record_count=data.get("contract_marker_record_count") if isinstance(data.get("contract_marker_record_count"), int) else 0,
        missing_contract_marker_count=data.get("missing_contract_marker_count") if isinstance(data.get("missing_contract_marker_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_provider_example_matrix_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_readme_provider_example_matrix_boundary(boundary)
    lines = [
        "README provider example matrix boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| provider_command_record_count | {validation.provider_command_record_count} |",
        f"| missing_provider_command_record_count | {validation.missing_provider_command_record_count} |",
        f"| contract_marker_record_count | {validation.contract_marker_record_count} |",
        f"| missing_contract_marker_count | {validation.missing_contract_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _provider_command_record(
    *,
    provider: str,
    path: str,
    text: str,
    marker: str,
    placeholder: str,
    required_env: str,
) -> dict[str, Any]:
    return {
        "provider": provider,
        "path": path,
        "required_marker": marker,
        "placeholder": placeholder,
        "required_env": required_env,
        "command_marker_status": (
            "command_marker_present" if marker in text else "command_marker_missing"
        ),
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
) -> tuple[dict[str, Any] | None, list[ReadmeProviderExampleMatrixBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README provider example matrix boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeProviderExampleMatrixBoundaryIssue],
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
    issues: list[ReadmeProviderExampleMatrixBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeProviderExampleMatrixBoundaryIssue:
    return ReadmeProviderExampleMatrixBoundaryIssue(code, message)
