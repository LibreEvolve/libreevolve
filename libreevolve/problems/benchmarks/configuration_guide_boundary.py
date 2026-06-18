from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIGURATION_GUIDE_BOUNDARY_SCHEMA = "libreevolve.configuration_guide_boundary.v1"
EXPECTED_BOUNDARY_STATUS = "configuration_guide_static_inventory_with_llm_budget_cli_markers_resolved"
CONFIGURATION_DOC_PATH = "docs/configuration.md"
CONFIG_SOURCE_PATH = "libreevolve/core/config.py"
CLI_SOURCE_PATH = "libreevolve/cli.py"
AGENTS_TEST_PATH = "tests/test_agents_docs.py"
STATUS_PATH = "docs/status.md"
PAPERS_README_PATH = "papers/README.md"
README_TODO_PATH = "docs/todo/readme.md"

EXPECTED_CONFIGURATION_DOC_MARKERS = (
    ("config_precedence", "Configuration is assembled from three sources"),
    ("config_defaults_anchor", "Config` defaults in [`libreevolve/core/config.py`]"),
    ("problem_config_yaml_anchor", "optional problem-local `config.yaml`"),
    ("cli_override_anchor", "CLI overrides from [`libreevolve/cli.py`]"),
    ("post_cli_validation", "validated once after CLI overrides are\napplied"),
    ("config_source_provenance", "`manifest.provenance.config`"),
    ("dotenv_override", "`.env` is loaded by the `run` command during run setup with `override=True`"),
    ("dotenv_provenance", "`manifest.provenance.dotenv`"),
    ("validator_env_allowlist", "`validator_env_allowlist`"),
    ("validator_network_policy", "`validator_network_policy` (`host`)"),
    ("max_llm_provider_attempts", "`max_llm_provider_attempts` (`null`)"),
    ("llm_role_budget_maps", "`llm_role_provider_attempt_limits` (`{}`)"),
    ("prompt_max_estimated_tokens", "`prompt_max_estimated_tokens` (`None`)"),
    ("runtime_llm_accounting_boundary", "`runtime.llm_accounting` with policy\n`audit_summary_not_budget_enforced`"),
    ("runtime_budget_stop_policy", "`runtime.budget` snapshot"),
    ("cli_overrides_heading", "## CLI overrides"),
    ("backend_spec_format", "## Backend spec format"),
    ("provider_capability_lookup", "`policies.provider_capability_lookup`"),
    ("openai_api_mode_policy", "`policies.openai_api_mode.records[]`"),
    ("environment_variables_heading", "## Environment variables"),
    ("known_caveats_heading", "## Known caveats"),
)
EXPECTED_CLI_OPTION_MARKERS = (
    "--max-generations",
    "--max-evaluations",
    "--max-evaluator-seconds",
    "--max-runtime-seconds",
    "--proposals-per-generation",
    "--max-llm-calls",
    "--max-llm-provider-attempts",
    "--max-llm-tokens",
    "--max-llm-cost-microusd",
    "--max-llm-seconds",
    "--plugins",
    "--backends",
    "--seed",
    "--mutation-mode",
    "--reasoning-effort",
    "--llm-max-retries",
    "--llm-max-call-attempts",
    "--llm-fallback",
    "--no-llm-fallback",
    "--llm-max-response-chars",
    "--llm-call-history-max",
    "--llm-call-timeout-sec",
    "--prompt-max-chars",
    "--prompt-max-estimated-tokens",
    "--explore-ratio",
    "--parent-selection-strategy",
    "--inspiration-strategy",
    "--run-name",
    "--restore-runtime-from-manifest",
    "--restore-rng-from-manifest",
    "--restore-llm-scheduler-from-manifest",
    "--restore-archive-cursor-from-manifest",
    "--restore-archive-from-manifest",
    "--restore-budget-from-manifest",
    "--overwrite",
)
EXPECTED_CONFIG_SOURCE_MARKERS = (
    ("config_class", "class Config:"),
    ("max_generations_field", "max_generations:"),
    ("validator_env_allowlist_field", "validator_env_allowlist: list[str]"),
    ("validator_network_policy_field", 'validator_network_policy: str = "host"'),
    ("max_llm_provider_attempts_field", "max_llm_provider_attempts: int | None = None"),
    ("max_llm_seconds_field", "max_llm_seconds:"),
    ("llm_role_provider_attempt_limits_field", "llm_role_provider_attempt_limits: dict[str, int]"),
    ("prompt_max_estimated_tokens_field", "prompt_max_estimated_tokens: int | None = None"),
    ("backends_field", "backends:"),
    ("seed_field", "seed:"),
)
EXPECTED_CLI_SOURCE_MARKERS = (
    ("click_max_generations", '@click.option("--max-generations"'),
    ("click_max_llm_provider_attempts", '@click.option("--max-llm-provider-attempts"'),
    ("click_max_llm_seconds", '@click.option("--max-llm-seconds"'),
    ("click_backends", '@click.option("--backends"'),
    ("click_restore_budget", '"--restore-budget-from-manifest"'),
    ("click_overwrite", '@click.option("--overwrite"'),
    ("dotenv_loader", "load_dotenv"),
    ("config_builder", "_build_config"),
)
EXPECTED_TEST_AND_DOC_ANCHORS = (
    ("agents_sampling_strategy_test", AGENTS_TEST_PATH, "test_configuration_docs_track_sampling_strategy_fields"),
    ("agents_archive_cleanup_test", AGENTS_TEST_PATH, "test_configuration_docs_track_archive_event_cleanup_stream"),
    ("status_config_validation_boundary", STATUS_PATH, "Configuration validation is local effective-config validation"),
    ("papers_config_validation_sidecar", PAPERS_README_PATH, "papers/config_validation_boundary.json"),
    ("papers_provider_capability_scope", PAPERS_README_PATH, "capability lookup"),
    ("active_todo_owner", README_TODO_PATH, "Add configuration-guide field and override drift evidence."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "configuration_doc_precedence_markers",
    "configuration_doc_env_and_validator_markers",
    "configuration_doc_budget_and_retention_markers",
    "configuration_doc_cli_override_markers",
    "configuration_doc_backend_provider_markers",
    "config_source_field_anchors",
    "cli_source_option_anchors",
    "focused_agent_doc_tests",
    "status_and_paper_sidecar_anchors",
    "active_todo_owner_anchor",
    "complete_config_field_default_map",
    "complete_cli_option_to_config_map",
    "yaml_key_validation_semantic_map",
    "manifest_provenance_field_map",
    "restore_capability_semantic_map",
    "configuration_docs_ci_drift_gate",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "complete_config_field_default_map": "not_recorded_locally",
    "complete_cli_option_to_config_map": "not_recorded_locally",
    "yaml_key_validation_semantic_map": "not_recorded_locally",
    "manifest_provenance_field_map": "not_recorded_locally",
    "restore_capability_semantic_map": "not_recorded_locally",
    "configuration_docs_ci_drift_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_RESOLVED_EVIDENCE = {
    "llm_budget_cli_option_markers": "recorded_in_docs_configuration_cli_overrides",
    "runtime_llm_accounting_stop_policy_routing": "recorded_with_runtime_budget_snapshot",
}


@dataclass(frozen=True)
class ConfigurationGuideBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ConfigurationGuideBoundaryValidation:
    ok: bool
    boundary_status: str | None
    configuration_marker_count: int
    cli_option_marker_count: int
    config_source_anchor_count: int
    cli_source_anchor_count: int
    test_and_doc_anchor_count: int
    missing_cli_option_count: int
    missing_marker_count: int
    missing_evidence_count: int
    issues: list[ConfigurationGuideBoundaryIssue]


def configuration_guide_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return a static inventory for the configuration guide contract."""

    root_path = Path(root)
    texts = {
        path: _read_text(root_path / path)
        for path in (
            CONFIGURATION_DOC_PATH,
            CONFIG_SOURCE_PATH,
            CLI_SOURCE_PATH,
            AGENTS_TEST_PATH,
            STATUS_PATH,
            PAPERS_README_PATH,
            README_TODO_PATH,
        )
    }
    configuration_records = [
        _marker_record(record_id, CONFIGURATION_DOC_PATH, texts[CONFIGURATION_DOC_PATH], marker)
        for record_id, marker in EXPECTED_CONFIGURATION_DOC_MARKERS
    ]
    cli_option_records = [
        _marker_record(f"cli_option_{marker.lstrip('-').replace('-', '_')}", CONFIGURATION_DOC_PATH, texts[CONFIGURATION_DOC_PATH], marker)
        for marker in EXPECTED_CLI_OPTION_MARKERS
    ]
    missing_cli_option_records = [
        record
        for record in cli_option_records
        if record["marker_status"] != "marker_present"
    ]
    config_source_records = [
        _marker_record(record_id, CONFIG_SOURCE_PATH, texts[CONFIG_SOURCE_PATH], marker)
        for record_id, marker in EXPECTED_CONFIG_SOURCE_MARKERS
    ]
    cli_source_records = [
        _marker_record(record_id, CLI_SOURCE_PATH, texts[CLI_SOURCE_PATH], marker)
        for record_id, marker in EXPECTED_CLI_SOURCE_MARKERS
    ]
    test_and_doc_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_TEST_AND_DOC_ANCHORS
    ]
    all_records = (
        configuration_records
        + config_source_records
        + cli_source_records
        + test_and_doc_anchor_records
    )
    missing_records = [
        record for record in all_records if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": CONFIGURATION_GUIDE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "configuration_doc_path": CONFIGURATION_DOC_PATH,
        "config_source_path": CONFIG_SOURCE_PATH,
        "cli_source_path": CLI_SOURCE_PATH,
        "configuration_marker_count": len(configuration_records),
        "configuration_marker_records": configuration_records,
        "cli_option_marker_count": len(cli_option_records),
        "cli_option_marker_records": cli_option_records,
        "missing_cli_option_count": len(missing_cli_option_records),
        "missing_cli_option_records": missing_cli_option_records,
        "config_source_anchor_count": len(config_source_records),
        "config_source_anchor_records": config_source_records,
        "cli_source_anchor_count": len(cli_source_records),
        "cli_source_anchor_records": cli_source_records,
        "test_and_doc_anchor_count": len(test_and_doc_anchor_records),
        "test_and_doc_anchor_records": test_and_doc_anchor_records,
        "missing_marker_count": len(missing_records),
        "missing_marker_records": missing_records,
        "resolved_evidence": dict(EXPECTED_RESOLVED_EVIDENCE),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records static docs/configuration.md markers for "
            "configuration precedence, config.yaml provenance, .env behavior, "
            "validator environment/network policy, representative Config "
            "fields, CLI override markers, backend/provider capability policy, "
            "OpenAI API-mode policy, focused agent-doc tests, status/paper "
            "sidecar anchors, active TODO ownership, resolved "
            "configuration-guide CLI-option records for the current run "
            "command surface, and resolved runtime.llm_accounting wording "
            "that routes live stop enforcement to runtime.budget. It does "
            "not claim a "
            "complete field/default map, complete CLI option-to-config map, "
            "YAML validation semantic map, manifest provenance field map, "
            "restore capability semantic map, CI configuration-doc drift gate, "
            "or owner review signoff."
        ),
    }


def validate_configuration_guide_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ConfigurationGuideBoundaryValidation:
    data, read_issues = _load_boundary(
        configuration_guide_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ConfigurationGuideBoundaryValidation(False, None, 0, 0, 0, 0, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = configuration_guide_boundary_record(root)
    issues: list[ConfigurationGuideBoundaryIssue] = []
    if data.get("schema") != CONFIGURATION_GUIDE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported configuration guide boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "configuration guide boundary must not claim semantic configuration parity"))
    for key in (
        "configuration_doc_path",
        "config_source_path",
        "cli_source_path",
        "configuration_marker_count",
        "configuration_marker_records",
        "cli_option_marker_count",
        "cli_option_marker_records",
        "missing_cli_option_count",
        "missing_cli_option_records",
        "config_source_anchor_count",
        "config_source_anchor_records",
        "cli_source_anchor_count",
        "cli_source_anchor_records",
        "test_and_doc_anchor_count",
        "test_and_doc_anchor_records",
        "missing_marker_count",
        "missing_marker_records",
        "resolved_evidence",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current configuration guide inputs"))
    if data.get("missing_cli_option_count") != 0:
        issues.append(_issue("invalid_missing_cli_option_count", "configuration guide should not record missing expected CLI option markers"))
    if data.get("missing_marker_count") != 0:
        issues.append(_issue("missing_configuration_guide_marker", "configuration guide evidence anchors are incomplete"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "static docs/configuration.md markers" not in boundary_text
        or "resolved configuration-guide CLI-option records" not in boundary_text
        or "routes live stop enforcement to runtime.budget" not in boundary_text
        or "does not claim a complete field/default map" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate static configuration-guide markers from semantic drift proof"))
    return ConfigurationGuideBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        configuration_marker_count=data.get("configuration_marker_count") if isinstance(data.get("configuration_marker_count"), int) else 0,
        cli_option_marker_count=data.get("cli_option_marker_count") if isinstance(data.get("cli_option_marker_count"), int) else 0,
        config_source_anchor_count=data.get("config_source_anchor_count") if isinstance(data.get("config_source_anchor_count"), int) else 0,
        cli_source_anchor_count=data.get("cli_source_anchor_count") if isinstance(data.get("cli_source_anchor_count"), int) else 0,
        test_and_doc_anchor_count=data.get("test_and_doc_anchor_count") if isinstance(data.get("test_and_doc_anchor_count"), int) else 0,
        missing_cli_option_count=data.get("missing_cli_option_count") if isinstance(data.get("missing_cli_option_count"), int) else 0,
        missing_marker_count=data.get("missing_marker_count") if isinstance(data.get("missing_marker_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_configuration_guide_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_configuration_guide_boundary(boundary)
    lines = [
        "Configuration guide boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| configuration_marker_count | {validation.configuration_marker_count} |",
        f"| cli_option_marker_count | {validation.cli_option_marker_count} |",
        f"| config_source_anchor_count | {validation.config_source_anchor_count} |",
        f"| cli_source_anchor_count | {validation.cli_source_anchor_count} |",
        f"| test_and_doc_anchor_count | {validation.test_and_doc_anchor_count} |",
        f"| missing_cli_option_count | {validation.missing_cli_option_count} |",
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
) -> tuple[dict[str, Any] | None, list[ConfigurationGuideBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "configuration guide boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ConfigurationGuideBoundaryIssue],
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
    issues: list[ConfigurationGuideBoundaryIssue],
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


def _issue(code: str, message: str) -> ConfigurationGuideBoundaryIssue:
    return ConfigurationGuideBoundaryIssue(code, message)
