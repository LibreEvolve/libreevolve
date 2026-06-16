from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BACKEND_CLI_PROVIDER_GUARDRAIL_BOUNDARY_SCHEMA = (
    "libreevolve.backend_cli_provider_guardrail_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "backend_docs_cli_provider_guardrail_without_first_class_cli_backend_contract"
)
BACKENDS_PATH = "docs/backends.md"
CODE_TODO_PATH = "docs/todo/code.md"
README_TODO_PATH = "docs/todo/readme.md"
README_PATH = "README.md"
ROADMAP_PATH = "ROADMAP.md"
PAPERS_README_PATH = "papers/README.md"
CONFIGURATION_PATH = "docs/configuration.md"
EXPECTED_MARKERS = (
    {
        "record_kind": "backends_provider_lanes_heading",
        "path": BACKENDS_PATH,
        "marker": "## Provider lanes",
    },
    {
        "record_kind": "backends_builtin_sdk_lane",
        "path": BACKENDS_PATH,
        "marker": "Built-in SDK adapters: OpenAI, Anthropic, and Ollama",
    },
    {
        "record_kind": "backends_custom_import_path_lane",
        "path": BACKENDS_PATH,
        "marker": "Custom import-path backends: `type: custom` loads",
    },
    {
        "record_kind": "backends_cli_provider_lane",
        "path": BACKENDS_PATH,
        "marker": "Subprocess/CLI-authenticated providers: Codex-authenticated",
    },
    {
        "record_kind": "backends_cli_not_first_class",
        "path": BACKENDS_PATH,
        "marker": "not a first-class provider lane in the committed backend\n  contract",
    },
    {
        "record_kind": "backends_custom_wrapper_limitation",
        "path": BACKENDS_PATH,
        "marker": "A user can write a custom wrapper around a CLI",
    },
    {
        "record_kind": "backends_code_todo_link",
        "path": BACKENDS_PATH,
        "marker": "[docs/todo/code.md](todo/code.md)",
    },
    {
        "record_kind": "backends_forbidden_claim_guidance",
        "path": BACKENDS_PATH,
        "marker": "Do not use custom-wrapper examples to claim Codex-authenticated",
    },
    {
        "record_kind": "backends_missing_cli_contract_fields",
        "path": BACKENDS_PATH,
        "marker": "command discovery, auth/session\nprovenance without secret capture",
    },
    {
        "record_kind": "backends_missing_manifest_smoke_fields",
        "path": BACKENDS_PATH,
        "marker": "manifest/report fields, and credential-safe smoke tests",
    },
    {
        "record_kind": "code_todo_cli_backend_contract",
        "path": CODE_TODO_PATH,
        "marker": "Define a first-class subprocess/CLI LLM backend contract",
    },
    {
        "record_kind": "readme_todo_backend_doc_guardrail",
        "path": README_TODO_PATH,
        "marker": "Add backend-doc guardrail for CLI-authenticated provider support.",
    },
    {
        "record_kind": "readme_todo_backend_doc_required_result",
        "path": README_TODO_PATH,
        "marker": "implement the first-class subprocess/CLI backend contract",
    },
)
CLAIM_SURFACE_PATHS = (
    BACKENDS_PATH,
    CONFIGURATION_PATH,
    README_PATH,
    ROADMAP_PATH,
    PAPERS_README_PATH,
)
FORBIDDEN_SUPPORTED_CLAIM_PHRASES = (
    "Codex-authenticated providers are supported",
    "Codex CLI backend is supported",
    "first-class Codex-authenticated provider support is implemented",
    "first-class local CLI provider support is implemented",
    "local CLI providers are supported",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "backends_provider_lane_taxonomy",
    "backends_builtin_sdk_lane",
    "backends_custom_import_path_lane",
    "backends_cli_provider_guardrail",
    "backends_custom_wrapper_limitation",
    "backends_subprocess_cli_contract_link",
    "backends_missing_cli_contract_fields",
    "code_todo_cli_backend_contract",
    "readme_todo_backend_doc_guardrail",
    "claim_surface_forbidden_supported_claim_scan",
    "first_class_cli_backend_contract",
    "cli_backend_manifest_schema",
    "credential_safe_cli_backend_smoke",
    "cli_provider_attempt_accounting",
    "cli_provider_diagnostics",
)
EXPECTED_MISSING_EVIDENCE = {
    "first_class_cli_backend_contract": "not_recorded_locally",
    "cli_backend_manifest_schema": "not_recorded_locally",
    "credential_safe_cli_backend_smoke": "not_recorded_locally",
    "cli_provider_attempt_accounting": "not_recorded_locally",
    "cli_provider_diagnostics": "not_recorded_locally",
}


@dataclass(frozen=True)
class BackendCliProviderGuardrailBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class BackendCliProviderGuardrailBoundaryValidation:
    ok: bool
    boundary_status: str | None
    marker_record_count: int
    missing_marker_count: int
    forbidden_claim_count: int
    missing_evidence_count: int
    issues: list[BackendCliProviderGuardrailBoundaryIssue]


def backend_cli_provider_guardrail_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the backend-guide CLI-provider guardrail boundary."""

    root_path = Path(root)
    paths = {
        BACKENDS_PATH,
        CODE_TODO_PATH,
        README_TODO_PATH,
        CONFIGURATION_PATH,
        README_PATH,
        ROADMAP_PATH,
        PAPERS_README_PATH,
    }
    texts = {path: _read_text(root_path / path) for path in paths}
    marker_records = [
        _marker_record(
            spec["record_kind"],
            spec["path"],
            texts[spec["path"]],
            spec["marker"],
        )
        for spec in EXPECTED_MARKERS
    ]
    missing_marker_records = [
        record for record in marker_records if record["marker_status"] != "marker_present"
    ]
    forbidden_claim_records = _forbidden_claim_records(texts)
    return {
        "schema": BACKEND_CLI_PROVIDER_GUARDRAIL_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "backends_path": BACKENDS_PATH,
        "todo_paths": [CODE_TODO_PATH, README_TODO_PATH],
        "claim_surface_paths": list(CLAIM_SURFACE_PATHS),
        "marker_record_count": len(marker_records),
        "missing_marker_count": len(missing_marker_records),
        "missing_marker_records": missing_marker_records,
        "marker_records": marker_records,
        "forbidden_supported_claim_phrases": list(FORBIDDEN_SUPPORTED_CLAIM_PHRASES),
        "forbidden_claim_count": len(forbidden_claim_records),
        "forbidden_claim_records": forbidden_claim_records,
        "backend_cli_provider_guardrail_status": (
            "backend_docs_cli_provider_guardrail_present"
            if not missing_marker_records and not forbidden_claim_records
            else "backend_docs_cli_provider_guardrail_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records docs/backends.md provider-lane taxonomy, "
            "built-in SDK adapter wording, custom import-path backend wording, "
            "subprocess/CLI-authenticated provider guardrail wording, custom "
            "CLI-wrapper limitation wording, the subprocess/CLI backend "
            "contract TODO link, missing CLI contract field markers, README "
            "TODO ownership, and a narrow scan for unsupported positive "
            "Codex/local CLI provider-support claims across backend, "
            "configuration, README, ROADMAP, and papers-index claim surfaces. "
            "It does not claim a first-class CLI backend contract, CLI backend "
            "manifest schema, credential-safe CLI backend smoke, CLI provider "
            "attempt accounting, or CLI provider diagnostics."
        ),
    }


def validate_backend_cli_provider_guardrail_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> BackendCliProviderGuardrailBoundaryValidation:
    data, read_issues = _load_boundary(
        backend_cli_provider_guardrail_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return BackendCliProviderGuardrailBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = backend_cli_provider_guardrail_boundary_record(root)
    issues: list[BackendCliProviderGuardrailBoundaryIssue] = []
    if data.get("schema") != BACKEND_CLI_PROVIDER_GUARDRAIL_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported backend CLI-provider guardrail boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "backend CLI-provider guardrail must not claim first-class CLI backend support"))
    for key in (
        "backends_path",
        "todo_paths",
        "claim_surface_paths",
        "marker_record_count",
        "missing_marker_count",
        "missing_marker_records",
        "marker_records",
        "forbidden_supported_claim_phrases",
        "forbidden_claim_count",
        "forbidden_claim_records",
        "backend_cli_provider_guardrail_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current backend CLI-provider guardrail inputs"))
    if data.get("marker_record_count") != len(EXPECTED_MARKERS):
        issues.append(_issue("invalid_marker_record_count", "all expected backend CLI-provider guardrail markers must be recorded"))
    if data.get("missing_marker_count") != 0:
        issues.append(_issue("missing_backend_cli_provider_guardrail_marker", "backend CLI-provider guardrail markers are incomplete"))
    if data.get("forbidden_claim_count") != 0:
        issues.append(_issue("forbidden_cli_provider_supported_claim", "claim surfaces include unsupported CLI-provider support wording"))
    if data.get("backend_cli_provider_guardrail_status") != "backend_docs_cli_provider_guardrail_present":
        issues.append(_issue("invalid_backend_cli_provider_guardrail_status", "backend CLI-provider guardrail must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "docs/backends.md provider-lane taxonomy" not in boundary_text
        or "custom CLI-wrapper limitation wording" not in boundary_text
        or "does not claim a first-class CLI backend contract" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate backend-doc guardrails from first-class CLI backend support"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return BackendCliProviderGuardrailBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        marker_record_count=data.get("marker_record_count") if isinstance(data.get("marker_record_count"), int) else 0,
        missing_marker_count=data.get("missing_marker_count") if isinstance(data.get("missing_marker_count"), int) else 0,
        forbidden_claim_count=data.get("forbidden_claim_count") if isinstance(data.get("forbidden_claim_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_backend_cli_provider_guardrail_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_backend_cli_provider_guardrail_boundary(boundary)
    lines = [
        "Backend CLI-provider guardrail boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| marker_record_count | {validation.marker_record_count} |",
        f"| missing_marker_count | {validation.missing_marker_count} |",
        f"| forbidden_claim_count | {validation.forbidden_claim_count} |",
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


def _forbidden_claim_records(texts: dict[str, str]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for path in CLAIM_SURFACE_PATHS:
        text = texts.get(path, "")
        for phrase in FORBIDDEN_SUPPORTED_CLAIM_PHRASES:
            if phrase not in text:
                continue
            records.append(
                {
                    "path": path,
                    "forbidden_phrase": phrase,
                    "claim_status": "forbidden_supported_claim_present",
                }
            )
    return records


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[BackendCliProviderGuardrailBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "backend CLI-provider guardrail boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[BackendCliProviderGuardrailBoundaryIssue],
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
    issues: list[BackendCliProviderGuardrailBoundaryIssue],
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


def _issue(code: str, message: str) -> BackendCliProviderGuardrailBoundaryIssue:
    return BackendCliProviderGuardrailBoundaryIssue(code, message)
