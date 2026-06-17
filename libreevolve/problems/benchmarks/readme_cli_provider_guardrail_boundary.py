from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_CLI_PROVIDER_GUARDRAIL_BOUNDARY_SCHEMA = (
    "libreevolve.readme_cli_provider_guardrail_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "readme_codex_cli_lane_without_benchmark_ready_parity"
)
README_PATH = "README.md"
BACKENDS_PATH = "docs/backends.md"
CODE_TODO_PATH = "docs/todo/code.md"
README_TODO_PATH = "docs/todo/readme.md"
ROADMAP_PATH = "ROADMAP.md"
PAPERS_README_PATH = "papers/README.md"
EXPECTED_MARKERS = (
    {
        "record_kind": "readme_backend_feature_bullet",
        "path": README_PATH,
        "marker": "OpenAI, Anthropic, Ollama, experimental Codex CLI, and custom import-path",
    },
    {
        "record_kind": "readme_cli_provider_guardrail",
        "path": README_PATH,
        "marker": (
            "The built-in Codex CLI adapter (`type: codex`) is an experimental local CLI\n"
            "  lane for authenticated `codex exec` sessions."
        ),
    },
    {
        "record_kind": "readme_cli_provider_evidence_scope",
        "path": README_PATH,
        "marker": "not yet benchmark- or\n  paper-claim-ready",
    },
    {
        "record_kind": "readme_cli_provider_contract_link",
        "path": README_PATH,
        "marker": "[docs/todo/code.md](docs/todo/code.md)",
    },
    {
        "record_kind": "code_todo_cli_backend_contract",
        "path": CODE_TODO_PATH,
        "marker": "Finish the subprocess/CLI LLM backend contract",
    },
    {
        "record_kind": "code_todo_command_resolution",
        "path": CODE_TODO_PATH,
        "marker": "resolves the local `codex exec`\n    command",
    },
    {
        "record_kind": "code_todo_auth_session_provenance",
        "path": CODE_TODO_PATH,
        "marker": "redacted auth-home metadata",
    },
    {
        "record_kind": "code_todo_transcript_hashing",
        "path": CODE_TODO_PATH,
        "marker": "libreevolve.codex_cli_transcript.v1",
    },
    {
        "record_kind": "code_todo_manifest_report_fields",
        "path": CODE_TODO_PATH,
        "marker": "runtime manifest/report field integration",
    },
    {
        "record_kind": "readme_todo_cli_guardrail_owner",
        "path": README_TODO_PATH,
        "marker": "Keep README guardrails for experimental subprocess/CLI-authenticated LLM",
    },
    {
        "record_kind": "readme_todo_distinguish_lanes",
        "path": README_TODO_PATH,
        "marker": "limited to experimental Codex CLI plumbing",
    },
    {
        "record_kind": "backends_builtin_custom_lanes",
        "path": BACKENDS_PATH,
        "marker": "LibreEvolve supports configured built-in, CLI, and custom backend types",
    },
    {
        "record_kind": "backends_codex_cli_lane",
        "path": BACKENDS_PATH,
        "marker": "Built-in CLI adapters: `type: codex` delegates generation",
    },
    {
        "record_kind": "backends_custom_import_path_lane",
        "path": BACKENDS_PATH,
        "marker": "Custom import-path backends",
    },
    {
        "record_kind": "backends_custom_class_path_contract",
        "path": BACKENDS_PATH,
        "marker": "Configured custom backends use `type: custom` plus an importable\n`class_path`",
    },
)
CLAIM_SURFACE_PATHS = (README_PATH, ROADMAP_PATH, PAPERS_README_PATH)
FORBIDDEN_SUPPORTED_CLAIM_PHRASES = (
    "Codex CLI runs are benchmark-ready",
    "Codex CLI runs are paper-ready",
    "Codex CLI backend has provider-native token accounting",
    "Codex CLI backend has live model preflight",
    "local CLI providers are benchmark-ready",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_backend_feature_bullet",
    "readme_cli_provider_guardrail",
    "readme_cli_provider_contract_link",
    "code_todo_cli_backend_contract",
    "code_todo_command_resolution",
    "code_todo_auth_session_provenance",
    "code_todo_transcript_hashing",
    "code_todo_manifest_report_fields",
    "readme_todo_cli_guardrail_owner",
    "backends_builtin_custom_lanes",
    "backends_codex_cli_lane",
    "claim_surface_forbidden_supported_claim_scan",
    "benchmark_ready_cli_provider_contract",
    "cli_backend_manifest_report_integration",
    "credential_safe_cli_backend_smoke",
    "cli_model_availability_preflight",
    "provider_budget_accounting_for_cli_backend",
    "provider_diagnostics_for_cli_backend",
)
EXPECTED_MISSING_EVIDENCE = {
    "benchmark_ready_cli_provider_contract": "not_recorded_locally",
    "cli_backend_manifest_report_integration": "not_recorded_locally",
    "credential_safe_cli_backend_smoke": "not_recorded_locally",
    "cli_model_availability_preflight": "not_recorded_locally",
    "provider_budget_accounting_for_cli_backend": "not_recorded_locally",
    "provider_diagnostics_for_cli_backend": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeCliProviderGuardrailBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeCliProviderGuardrailBoundaryValidation:
    ok: bool
    boundary_status: str | None
    marker_record_count: int
    missing_marker_count: int
    forbidden_claim_count: int
    missing_evidence_count: int
    issues: list[ReadmeCliProviderGuardrailBoundaryIssue]


def readme_cli_provider_guardrail_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the README CLI-authenticated provider guardrail boundary."""

    root_path = Path(root)
    paths = {
        README_PATH,
        BACKENDS_PATH,
        CODE_TODO_PATH,
        README_TODO_PATH,
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
        "schema": README_CLI_PROVIDER_GUARDRAIL_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "docs_paths": [BACKENDS_PATH],
        "todo_paths": [CODE_TODO_PATH, README_TODO_PATH],
        "claim_surface_paths": list(CLAIM_SURFACE_PATHS),
        "marker_record_count": len(marker_records),
        "missing_marker_count": len(missing_marker_records),
        "missing_marker_records": missing_marker_records,
        "marker_records": marker_records,
        "forbidden_supported_claim_phrases": list(FORBIDDEN_SUPPORTED_CLAIM_PHRASES),
        "forbidden_claim_count": len(forbidden_claim_records),
        "forbidden_claim_records": forbidden_claim_records,
        "cli_provider_guardrail_status": (
            "readme_cli_provider_guardrail_present"
            if not missing_marker_records and not forbidden_claim_records
            else "readme_cli_provider_guardrail_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README built-in/custom/Codex CLI "
            "backend feature bullet, the README guardrail separating "
            "experimental Codex CLI plumbing from benchmark-ready provider "
            "parity, the link to the subprocess/CLI backend contract TODO, "
            "code TODO markers for command resolution, auth/session provenance, "
            "transcript hashing, manifest/report gaps, README TODO ownership, "
            "backend-doc built-in/custom/Codex lane markers, and a narrow scan "
            "for unsupported positive Codex/local CLI benchmark-parity claims "
            "in README, ROADMAP, and papers/README. It does not claim "
            "benchmark-ready CLI provider parity, CLI backend manifest/report "
            "integration, credential-safe CLI backend smoke, model availability "
            "preflight, provider budget accounting for CLI backends, or "
            "provider diagnostics for CLI backends."
        ),
    }


def validate_readme_cli_provider_guardrail_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeCliProviderGuardrailBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_cli_provider_guardrail_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return ReadmeCliProviderGuardrailBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_cli_provider_guardrail_boundary_record(root)
    issues: list[ReadmeCliProviderGuardrailBoundaryIssue] = []
    if data.get("schema") != README_CLI_PROVIDER_GUARDRAIL_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README CLI-provider guardrail boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README CLI-provider guardrail must not claim benchmark-ready CLI provider parity"))
    for key in (
        "readme_path",
        "docs_paths",
        "todo_paths",
        "claim_surface_paths",
        "marker_record_count",
        "missing_marker_count",
        "missing_marker_records",
        "marker_records",
        "forbidden_supported_claim_phrases",
        "forbidden_claim_count",
        "forbidden_claim_records",
        "cli_provider_guardrail_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current README CLI-provider guardrail inputs"))
    if data.get("marker_record_count") != len(EXPECTED_MARKERS):
        issues.append(_issue("invalid_marker_record_count", "all expected README CLI-provider guardrail markers must be recorded"))
    if data.get("missing_marker_count") != 0:
        issues.append(_issue("missing_cli_provider_guardrail_marker", "README CLI-provider guardrail markers are incomplete"))
    if data.get("forbidden_claim_count") != 0:
        issues.append(_issue("forbidden_cli_provider_supported_claim", "claim surfaces include unsupported CLI-provider parity wording"))
    if data.get("cli_provider_guardrail_status") != "readme_cli_provider_guardrail_present":
        issues.append(_issue("invalid_cli_provider_guardrail_status", "README CLI-provider guardrail must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "separating experimental Codex CLI plumbing" not in boundary_text
        or "subprocess/CLI backend contract TODO" not in boundary_text
        or "does not claim benchmark-ready CLI provider parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate README guardrails from benchmark-ready CLI provider parity"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmeCliProviderGuardrailBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        marker_record_count=data.get("marker_record_count") if isinstance(data.get("marker_record_count"), int) else 0,
        missing_marker_count=data.get("missing_marker_count") if isinstance(data.get("missing_marker_count"), int) else 0,
        forbidden_claim_count=data.get("forbidden_claim_count") if isinstance(data.get("forbidden_claim_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_cli_provider_guardrail_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_cli_provider_guardrail_boundary(boundary)
    lines = [
        "README CLI-provider guardrail boundary",
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
) -> tuple[dict[str, Any] | None, list[ReadmeCliProviderGuardrailBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README CLI-provider guardrail boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeCliProviderGuardrailBoundaryIssue],
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
    issues: list[ReadmeCliProviderGuardrailBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeCliProviderGuardrailBoundaryIssue:
    return ReadmeCliProviderGuardrailBoundaryIssue(code, message)
