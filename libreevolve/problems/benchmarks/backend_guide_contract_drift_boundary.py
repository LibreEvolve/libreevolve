from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BACKEND_GUIDE_CONTRACT_DRIFT_BOUNDARY_SCHEMA = (
    "libreevolve.backend_guide_contract_drift_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "backend_guide_structural_evidence_map_without_semantic_contract_proof"
)
BACKENDS_PATH = "docs/backends.md"
CONFIGURATION_PATH = "docs/configuration.md"
README_TODO_PATH = "docs/todo/readme.md"
CODE_TODO_PATH = "docs/todo/code.md"
ENSEMBLE_PATH = "libreevolve/llm/ensemble.py"
BACKEND_REGISTRY_PATH = "libreevolve/llm/backend_registry.py"
OPENAI_PATH = "libreevolve/llm/openai.py"
ANTHROPIC_PATH = "libreevolve/llm/anthropic.py"
OLLAMA_PATH = "libreevolve/llm/ollama.py"
CODEX_CLI_PATH = "libreevolve/llm/codex_cli.py"
CONFIG_PATH = "libreevolve/core/config.py"
CLI_PATH = "libreevolve/cli.py"
TEST_ENSEMBLE_PATH = "tests/llm/test_ensemble.py"
TEST_CODEX_CLI_PATH = "tests/llm/test_codex_cli.py"
TEST_CONFIG_PATH = "tests/core/test_config.py"
TEST_LOOP_PATH = "tests/core/test_loop.py"
GEMINI_BOUNDARY_PATH = "papers/gemini_provider_parity_boundary.json"
PROVIDER_PRICING_PATH = "papers/provider_pricing_boundary.json"
PROVIDER_DIAGNOSTICS_PATH = "papers/provider_diagnostics_replay_boundary.json"
PROVIDER_CANCELLATION_PATH = "papers/provider_cancellation_boundary.json"
LLM_BUDGET_PATH = "papers/llm_budget_policy_boundary.json"
BACKEND_CLI_PROVIDER_GUARDRAIL_PATH = "papers/backend_cli_provider_guardrail_boundary.json"

EXPECTED_GUIDE_MARKERS = (
    ("provider_lanes", "## Provider lanes"),
    ("selection_and_reward", "## Selection and reward"),
    ("openai_backend", "## OpenAI backend"),
    ("anthropic_backend", "## Anthropic backend"),
    ("ollama_backend", "## Ollama backend"),
    ("codex_cli_backend", "## Codex CLI backend"),
    ("environment_setup", "## Environment setup"),
    ("adding_new_backend", "## Adding a new backend"),
    ("practical_guidance", "## Practical guidance"),
    ("call_history_claim", "`LLMEnsemble.call_history` records normalized call telemetry"),
    ("llm_calls_replay_claim", "`load_llm_call_ledger()` validates durable `llm_calls.jsonl`"),
    ("scheduler_restore_claim", "`LLMEnsemble.restore_scheduler_state()` is the supported direct restore path"),
    ("prompt_validation_claim", "`LLMEnsemble.generate()` validates prompt payloads"),
    ("provider_metadata_claim", "built-in adapters copy safe provider usage counts"),
    ("role_backend_indices_claim", "`llm_role_backend_indices` can route a validated call role"),
    ("provider_failure_claim", "failed provider calls are recorded in ensemble telemetry"),
    ("timeout_claim", "Run-level `llm_call_timeout_sec` adds an ensemble deadline around"),
    ("openai_api_mode_claim", 'api_mode="auto"` preserves legacy routing: Chat Completions'),
    ("custom_backend_claim", "Configured custom backends use `type: custom` plus an importable"),
    ("credential_preflight_claim", "startup checks required credentials for\nOpenAI"),
    ("cli_provider_guardrail_claim", "Built-in CLI adapters: `type: codex` delegates generation"),
    ("cli_provider_limit_claim", "no run-manifest/report integration promotes Codex CLI runs"),
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("ensemble_class", ENSEMBLE_PATH, "class LLMEnsemble:"),
    ("ensemble_call_history", ENSEMBLE_PATH, "call_history"),
    ("llm_call_ledger_loader", ENSEMBLE_PATH, "def load_llm_call_ledger"),
    ("scheduler_restore", ENSEMBLE_PATH, "def restore_scheduler_state"),
    ("prompt_validation", ENSEMBLE_PATH, "LLM prompt must be non-empty text"),
    ("build_llm", ENSEMBLE_PATH, "def build_llm(config)"),
    ("custom_backend_builder", ENSEMBLE_PATH, "def build_custom_backend_from_spec"),
    ("backend_registry", BACKEND_REGISTRY_PATH, "def builtin_backend_registry"),
    ("openai_backend", OPENAI_PATH, "class OpenAIBackend"),
    ("anthropic_backend", ANTHROPIC_PATH, "class AnthropicBackend"),
    ("ollama_backend", OLLAMA_PATH, "class OllamaBackend"),
    ("codex_cli_backend", CODEX_CLI_PATH, "class CodexCLIBackend"),
    ("config_llm_role_backend_indices", CONFIG_PATH, "llm_role_backend_indices"),
    ("config_custom_backend_class_path", CONFIG_PATH, "_require_custom_backend_class_path"),
    ("cli_credential_preflight", CLI_PATH, "_preflight_llm_backends_if_needed"),
    ("ensemble_tests", TEST_ENSEMBLE_PATH, "LLMEnsemble"),
    ("codex_cli_tests", TEST_CODEX_CLI_PATH, "test_codex_backend_invokes_codex_exec_and_writes_transcript"),
    ("config_role_backend_tests", TEST_CONFIG_PATH, "test_accepts_llm_role_backend_indices"),
    ("runtime_budget_tests", TEST_LOOP_PATH, "max_llm_provider_attempts"),
    ("configuration_role_routing_note", CONFIGURATION_PATH, "llm_role_backend_indices"),
    ("readme_todo_owner", README_TODO_PATH, "Add backend-guide provider contract drift evidence."),
    ("code_todo_cli_contract", CODE_TODO_PATH, "Finish the subprocess/CLI LLM backend contract"),
    ("gemini_boundary_sidecar", GEMINI_BOUNDARY_PATH, "gemini"),
    ("provider_pricing_sidecar", PROVIDER_PRICING_PATH, "provider_pricing"),
    ("provider_diagnostics_sidecar", PROVIDER_DIAGNOSTICS_PATH, "provider_diagnostics"),
    ("provider_cancellation_sidecar", PROVIDER_CANCELLATION_PATH, "provider_cancellation"),
    ("llm_budget_sidecar", LLM_BUDGET_PATH, "llm_budget"),
    ("backend_cli_guardrail_sidecar", BACKEND_CLI_PROVIDER_GUARDRAIL_PATH, "backend_cli_provider_guardrail"),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "backend_guide_section_inventory",
    "backend_guide_provider_lane_markers",
    "backend_guide_scheduler_and_reward_markers",
    "backend_guide_call_history_and_ledger_markers",
    "backend_guide_provider_adapter_markers",
    "backend_guide_credential_and_custom_backend_markers",
    "backend_guide_cli_provider_guardrail_marker",
    "source_module_anchor_map",
    "focused_test_anchor_map",
    "sidecar_boundary_anchor_map",
    "active_todo_owner_anchor",
    "semantic_backend_claim_verifier",
    "per_constructor_field_evidence_map",
    "per_telemetry_field_evidence_map",
    "backend_docs_ci_drift_gate",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "semantic_backend_claim_verifier": "not_recorded_locally",
    "per_constructor_field_evidence_map": "not_recorded_locally",
    "per_telemetry_field_evidence_map": "not_recorded_locally",
    "backend_docs_ci_drift_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class BackendGuideContractDriftBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class BackendGuideContractDriftBoundaryValidation:
    ok: bool
    boundary_status: str | None
    guide_marker_count: int
    missing_guide_marker_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    missing_evidence_count: int
    issues: list[BackendGuideContractDriftBoundaryIssue]


def backend_guide_contract_drift_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the backend-guide structural evidence-map boundary."""

    root_path = Path(root)
    paths = {
        BACKENDS_PATH,
        CONFIGURATION_PATH,
        README_TODO_PATH,
        CODE_TODO_PATH,
        ENSEMBLE_PATH,
        BACKEND_REGISTRY_PATH,
        OPENAI_PATH,
        ANTHROPIC_PATH,
        OLLAMA_PATH,
        CODEX_CLI_PATH,
        CONFIG_PATH,
        CLI_PATH,
        TEST_ENSEMBLE_PATH,
        TEST_CODEX_CLI_PATH,
        TEST_CONFIG_PATH,
        TEST_LOOP_PATH,
        GEMINI_BOUNDARY_PATH,
        PROVIDER_PRICING_PATH,
        PROVIDER_DIAGNOSTICS_PATH,
        PROVIDER_CANCELLATION_PATH,
        LLM_BUDGET_PATH,
        BACKEND_CLI_PROVIDER_GUARDRAIL_PATH,
    }
    texts = {path: _read_text(root_path / path) for path in paths}
    guide_marker_records = [
        _marker_record(record_id, BACKENDS_PATH, texts[BACKENDS_PATH], marker)
        for record_id, marker in EXPECTED_GUIDE_MARKERS
    ]
    evidence_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_EVIDENCE_ANCHORS
    ]
    missing_guide_markers = [
        record for record in guide_marker_records if record["marker_status"] != "marker_present"
    ]
    missing_evidence_anchors = [
        record for record in evidence_anchor_records if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": BACKEND_GUIDE_CONTRACT_DRIFT_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "backend_guide_path": BACKENDS_PATH,
        "source_paths": [
            ENSEMBLE_PATH,
            BACKEND_REGISTRY_PATH,
            OPENAI_PATH,
            ANTHROPIC_PATH,
            OLLAMA_PATH,
            CONFIG_PATH,
            CLI_PATH,
        ],
        "test_paths": [TEST_ENSEMBLE_PATH, TEST_CONFIG_PATH, TEST_LOOP_PATH],
        "sidecar_paths": [
            GEMINI_BOUNDARY_PATH,
            PROVIDER_PRICING_PATH,
            PROVIDER_DIAGNOSTICS_PATH,
            PROVIDER_CANCELLATION_PATH,
            LLM_BUDGET_PATH,
            BACKEND_CLI_PROVIDER_GUARDRAIL_PATH,
        ],
        "todo_paths": [README_TODO_PATH, CODE_TODO_PATH],
        "guide_marker_count": len(guide_marker_records),
        "missing_guide_marker_count": len(missing_guide_markers),
        "missing_guide_marker_records": missing_guide_markers,
        "guide_marker_records": guide_marker_records,
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "backend_guide_contract_map_status": (
            "backend_guide_structural_evidence_map_present"
            if not missing_guide_markers and not missing_evidence_anchors
            else "backend_guide_structural_evidence_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records docs/backends.md section and claim markers "
            "for provider lanes, scheduler/reward accounting, call-history and "
            "llm_calls replay, restore, prompt validation, provider metadata, "
            "role routing, provider failures, timeouts, OpenAI API-mode policy, "
            "credential preflight, custom backends, and CLI-provider guardrails. "
            "It also records source-module, focused-test, sidecar, and active "
            "TODO anchors. It does not claim semantic backend-claim "
            "verification, a per-constructor-field evidence map, a "
            "per-telemetry-field evidence map, a backend-docs CI drift gate, or "
            "owner review signoff."
        ),
    }


def validate_backend_guide_contract_drift_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> BackendGuideContractDriftBoundaryValidation:
    data, read_issues = _load_boundary(
        backend_guide_contract_drift_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return BackendGuideContractDriftBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = backend_guide_contract_drift_boundary_record(root)
    issues: list[BackendGuideContractDriftBoundaryIssue] = []
    if data.get("schema") != BACKEND_GUIDE_CONTRACT_DRIFT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported backend-guide contract drift boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "backend-guide contract map must not claim semantic backend proof"))
    for key in (
        "backend_guide_path",
        "source_paths",
        "test_paths",
        "sidecar_paths",
        "todo_paths",
        "guide_marker_count",
        "missing_guide_marker_count",
        "missing_guide_marker_records",
        "guide_marker_records",
        "evidence_anchor_count",
        "missing_evidence_anchor_count",
        "missing_evidence_anchor_records",
        "evidence_anchor_records",
        "backend_guide_contract_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current backend-guide inputs"))
    if data.get("guide_marker_count") != len(EXPECTED_GUIDE_MARKERS):
        issues.append(_issue("invalid_guide_marker_count", "all expected backend-guide markers must be recorded"))
    if data.get("missing_guide_marker_count") != 0:
        issues.append(_issue("missing_backend_guide_marker", "backend-guide markers are incomplete"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_backend_evidence_anchor", "backend-guide evidence anchors are incomplete"))
    if data.get("backend_guide_contract_map_status") != "backend_guide_structural_evidence_map_present":
        issues.append(_issue("invalid_backend_guide_contract_map_status", "backend-guide structural evidence map must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "docs/backends.md section and claim markers" not in boundary_text
        or "source-module, focused-test, sidecar, and active TODO anchors" not in boundary_text
        or "does not claim semantic backend-claim verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate structural backend-guide evidence from semantic proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return BackendGuideContractDriftBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        guide_marker_count=data.get("guide_marker_count") if isinstance(data.get("guide_marker_count"), int) else 0,
        missing_guide_marker_count=data.get("missing_guide_marker_count") if isinstance(data.get("missing_guide_marker_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_backend_guide_contract_drift_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_backend_guide_contract_drift_boundary(boundary)
    lines = [
        "Backend guide contract drift boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| guide_marker_count | {validation.guide_marker_count} |",
        f"| missing_guide_marker_count | {validation.missing_guide_marker_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_evidence_anchor_count | {validation.missing_evidence_anchor_count} |",
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
) -> tuple[dict[str, Any] | None, list[BackendGuideContractDriftBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "backend-guide contract drift boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[BackendGuideContractDriftBoundaryIssue],
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
    issues: list[BackendGuideContractDriftBoundaryIssue],
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


def _issue(code: str, message: str) -> BackendGuideContractDriftBoundaryIssue:
    return BackendGuideContractDriftBoundaryIssue(code, message)
