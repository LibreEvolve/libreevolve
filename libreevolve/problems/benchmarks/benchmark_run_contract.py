from __future__ import annotations

import importlib.util
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from libreevolve.problems.benchmarks.benchmark_goal_prompt import (
    SECRET_LIKE_PATTERN,
    validate_benchmark_goal_prompt,
)


BENCHMARK_RUN_CONTRACT_SCHEMA_SUFFIX = "_run_contract.v1"
SAFE_CONTRACT_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")


@dataclass(frozen=True)
class BenchmarkRunContractIssue:
    code: str
    message: str


@dataclass(frozen=True)
class BenchmarkRunContractValidation:
    ok: bool
    schema: str | None
    problem_id: str | None
    run_name: str | None
    expected_artifact_count: int
    manifest_assertion_count: int
    issues: list[BenchmarkRunContractIssue]


def validate_benchmark_run_contract(
    contract_record: object | str | Path,
    *,
    root: str | Path = ".",
) -> BenchmarkRunContractValidation:
    """Validate a reusable clean-checkout benchmark run-contract artifact."""

    root_path = Path(root)
    data, read_issues = _load_mapping(contract_record, root_path)
    if read_issues:
        return BenchmarkRunContractValidation(
            False,
            None,
            None,
            None,
            0,
            0,
            read_issues,
        )
    assert isinstance(data, dict)
    issues: list[BenchmarkRunContractIssue] = []

    schema = data.get("schema")
    if not (
        isinstance(schema, str)
        and schema.startswith("libreevolve.")
        and schema.endswith(BENCHMARK_RUN_CONTRACT_SCHEMA_SUFFIX)
    ):
        issues.append(_issue("invalid_schema", "schema must be a libreevolve benchmark run-contract schema"))

    problem_id = _required_text(data, "problem_id", issues)
    if problem_id is not None and not SAFE_CONTRACT_ID_PATTERN.fullmatch(problem_id):
        issues.append(_issue("invalid_problem_id", "problem_id must be a safe stable id"))

    status = _required_text(data, "status", issues)
    if status is not None and "not_certified" not in status:
        issues.append(_issue("status_overclaim", "status must preserve the non-certified boundary"))

    path_fields = {
        "problem_path": "directory",
        "config_path": "file",
        "seed_path": "file",
        "validator_path": "file",
        "goal_prompt_path": "file",
    }
    resolved_paths: dict[str, Path] = {}
    for field_name, expected_kind in path_fields.items():
        raw_path = _required_text(data, field_name, issues)
        if raw_path is None:
            continue
        path = root_path / raw_path
        resolved_paths[field_name] = path
        if expected_kind == "directory" and not path.is_dir():
            issues.append(_issue(f"missing_{field_name}", f"{field_name} must point to an existing directory"))
        if expected_kind == "file" and not path.is_file():
            issues.append(_issue(f"missing_{field_name}", f"{field_name} must point to an existing file"))

    command = _validate_command(data.get("command"), data, issues)
    run_name = _command_value(command, "--run-name") if command is not None else None
    auth_setup = _validate_auth_setup(data.get("auth_setup"), issues)
    _validate_config_matches_auth(resolved_paths.get("config_path"), auth_setup, issues)
    _validate_validator_budget(
        data.get("validator_budget"),
        resolved_paths.get("validator_path"),
        issues,
    )
    _validate_goal_prompt(data, resolved_paths.get("goal_prompt_path"), root_path, issues)

    expected_artifacts = _validate_string_list(
        data.get("expected_artifacts"),
        "expected_artifacts",
        issues,
        minimum=3,
    )
    for required_artifact in ("manifest.json", "task_specification.json", "best.py"):
        if required_artifact not in expected_artifacts:
            issues.append(
                _issue(
                    f"missing_expected_artifact_{required_artifact.replace('.', '_')}",
                    f"expected_artifacts must include {required_artifact}",
                )
            )
    if auth_setup.get("backend_type") == "codex" and not any(
        "transcript" in artifact for artifact in expected_artifacts
    ):
        issues.append(
            _issue(
                "missing_codex_transcript_artifact",
                "Codex benchmark contracts must name transcript artifacts",
            )
        )

    manifest_assertions = _validate_string_list(
        data.get("manifest_assertions"),
        "manifest_assertions",
        issues,
        minimum=3,
    )
    _validate_manifest_assertions(manifest_assertions, data, auth_setup, issues)
    _validate_string_list(data.get("skip_or_failure_modes"), "skip_or_failure_modes", issues, minimum=1)
    post_run_bundle = _validate_string_list(
        data.get("post_run_evidence_bundle"),
        "post_run_evidence_bundle",
        issues,
        minimum=3,
    )
    if "manifest.json" not in post_run_bundle:
        issues.append(_issue("missing_post_run_manifest", "post_run_evidence_bundle must include manifest.json"))

    claim_boundary = _required_text(data, "claim_boundary", issues)
    if claim_boundary is not None and "does not certify" not in claim_boundary:
        issues.append(_issue("claim_boundary_overclaim", "claim_boundary must reject certification overclaim"))
    contract_text = json.dumps(data, sort_keys=True)
    if SECRET_LIKE_PATTERN.search(contract_text):
        issues.append(_issue("secret_like_contract_text", "run contract must not contain secret-like tokens"))

    return BenchmarkRunContractValidation(
        ok=not issues,
        schema=schema if isinstance(schema, str) else None,
        problem_id=problem_id,
        run_name=run_name,
        expected_artifact_count=len(expected_artifacts),
        manifest_assertion_count=len(manifest_assertions),
        issues=issues,
    )


def render_benchmark_run_contract_summary(contract_record: dict[str, Any]) -> str:
    validation = validate_benchmark_run_contract(contract_record)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Benchmark run contract",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| problem_id | {validation.problem_id or '<unknown>'} |",
        f"| run_name | {validation.run_name or '<unknown>'} |",
        f"| expected_artifact_count | {validation.expected_artifact_count} |",
        f"| manifest_assertion_count | {validation.manifest_assertion_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _validate_command(
    value: object,
    data: dict[str, Any],
    issues: list[BenchmarkRunContractIssue],
) -> list[str] | None:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        issues.append(_issue("invalid_command", "command must be a non-empty string list"))
        return None
    expected_prefix = ["py", "-3.12", "-m", "libreevolve", "run"]
    if value[: len(expected_prefix)] != expected_prefix:
        issues.append(_issue("invalid_command_prefix", "command must use py -3.12 -m libreevolve run"))
    problem_path = data.get("problem_path")
    if len(value) <= len(expected_prefix) or value[len(expected_prefix)] != problem_path:
        issues.append(_issue("command_problem_path_mismatch", "command problem path must match problem_path"))
    expected_run_dir = data.get("expected_run_dir")
    run_name = _command_value(value, "--run-name")
    if isinstance(expected_run_dir, str) and run_name is not None:
        if expected_run_dir != f"runs/{run_name}":
            issues.append(_issue("expected_run_dir_mismatch", "expected_run_dir must be runs/<run-name>"))
    for numeric_flag in ("--max-generations", "--proposals-per-generation"):
        raw = _command_value(value, numeric_flag)
        if raw is None or not raw.isdigit() or int(raw) <= 0:
            issues.append(_issue(f"invalid_{numeric_flag[2:].replace('-', '_')}", f"{numeric_flag} must be a positive integer"))
    if "--overwrite" not in value:
        issues.append(_issue("missing_overwrite_flag", "clean-checkout command must include --overwrite"))
    return list(value)


def _validate_auth_setup(
    value: object,
    issues: list[BenchmarkRunContractIssue],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_auth_setup", "auth_setup must be an object"))
        return {}
    for field_name in ("backend_type", "model", "auth_name", "expected_auth_source", "secret_policy"):
        _required_text(value, field_name, issues, prefix="auth_setup")
    for field_name in ("requires_local_codex_cli", "requires_authenticated_codex_session"):
        if not isinstance(value.get(field_name), bool):
            issues.append(_issue(f"invalid_auth_setup_{field_name}", f"auth_setup.{field_name} must be boolean"))
    secret_policy = value.get("secret_policy")
    if isinstance(secret_policy, str) and ("do_not_commit" not in secret_policy or "api_keys" not in secret_policy):
        issues.append(_issue("invalid_auth_setup_secret_policy", "auth_setup.secret_policy must reject committed secrets"))
    return dict(value)


def _validate_config_matches_auth(
    config_path: Path | None,
    auth_setup: dict[str, Any],
    issues: list[BenchmarkRunContractIssue],
) -> None:
    if config_path is None or not config_path.is_file():
        return
    try:
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        issues.append(_issue("unreadable_config", f"config could not be loaded: {exc}"))
        return
    backends = config.get("backends") if isinstance(config, dict) else None
    if not isinstance(backends, list) or not backends or not isinstance(backends[0], dict):
        issues.append(_issue("invalid_config_backends", "config must define at least one backend"))
        return
    backend = backends[0]
    comparisons = {
        "type": auth_setup.get("backend_type"),
        "model": auth_setup.get("model"),
        "auth_name": auth_setup.get("auth_name"),
    }
    for config_field, expected in comparisons.items():
        if backend.get(config_field) != expected:
            issues.append(_issue(f"config_{config_field}_mismatch", f"config backend {config_field} must match auth_setup"))
    if backend.get("sandbox") != "read-only":
        issues.append(_issue("config_sandbox_not_read_only", "benchmark config backend sandbox must be read-only"))


def _validate_validator_budget(
    value: object,
    validator_path: Path | None,
    issues: list[BenchmarkRunContractIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_validator_budget", "validator_budget must be an object"))
        return
    for field_name in ("wire_count", "binary_inputs_checked", "seed_comparators", "target_comparators", "max_comparators"):
        if not isinstance(value.get(field_name), int) or isinstance(value.get(field_name), bool) or value[field_name] <= 0:
            issues.append(_issue(f"invalid_validator_budget_{field_name}", f"validator_budget.{field_name} must be a positive integer"))
    if not isinstance(value.get("target_metric"), str) or not value["target_metric"]:
        issues.append(_issue("invalid_validator_budget_target_metric", "validator_budget.target_metric must be non-empty text"))
    constants = _load_validator_constants(validator_path)
    for field_name, constant_name in (
        ("wire_count", "WIRE_COUNT"),
        ("binary_inputs_checked", "TOTAL_BINARY_INPUTS"),
        ("target_comparators", "TARGET_COMPARATORS"),
        ("max_comparators", "MAX_COMPARATORS"),
    ):
        expected = constants.get(constant_name)
        if expected is not None and value.get(field_name) != expected:
            issues.append(_issue(f"validator_budget_{field_name}_mismatch", f"validator_budget.{field_name} must match {constant_name}"))


def _validate_goal_prompt(
    data: dict[str, Any],
    goal_prompt_path: Path | None,
    root_path: Path,
    issues: list[BenchmarkRunContractIssue],
) -> None:
    if goal_prompt_path is None or not goal_prompt_path.is_file():
        return
    validation = validate_benchmark_goal_prompt(
        goal_prompt_path,
        root=root_path,
        run_contract=data,
    )
    issues.extend(
        _issue(f"goal_prompt_{issue.code}", issue.message)
        for issue in validation.issues
    )
    provenance = data.get("goal_prompt_provenance")
    if not isinstance(provenance, dict):
        issues.append(_issue("missing_goal_prompt_provenance", "goal_prompt_provenance must be an object"))
        return
    required_manifest_assertions = [
        f"runtime.benchmark_goal_prompt.prompt_id is {provenance.get('prompt_id')}",
        f"runtime.benchmark_goal_prompt.path is {data.get('goal_prompt_path')}",
        f"runtime.benchmark_goal_prompt.prompt_character_count is {provenance.get('prompt_character_count')}",
    ]
    manifest_assertions = data.get("manifest_assertions")
    if isinstance(manifest_assertions, list):
        for assertion in required_manifest_assertions:
            if assertion not in manifest_assertions:
                issues.append(_issue("missing_goal_prompt_manifest_assertion", "manifest_assertions must include benchmark goal-prompt provenance checks"))


def _validate_manifest_assertions(
    assertions: list[str],
    data: dict[str, Any],
    auth_setup: dict[str, Any],
    issues: list[BenchmarkRunContractIssue],
) -> None:
    expected = {
        f"config.problem_name is {_command_value(data.get('command'), '--run-name')}",
        f"config.backends[0].type is {auth_setup.get('backend_type')}",
        f"config.backends[0].model is {auth_setup.get('model')}",
        f"config.backends[0].auth_name is {auth_setup.get('auth_name')}",
        f"problem.name is {data.get('problem_id')}",
    }
    missing = sorted(item for item in expected if item not in assertions)
    if missing:
        issues.append(_issue("missing_manifest_assertions", "manifest_assertions missing required checks"))


def _load_validator_constants(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    module_name = f"_libreevolve_benchmark_contract_{path.stem}_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        return {}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {
        name: getattr(module, name)
        for name in ("WIRE_COUNT", "TOTAL_BINARY_INPUTS", "TARGET_COMPARATORS", "MAX_COMPARATORS")
        if hasattr(module, name)
    }


def _validate_string_list(
    value: object,
    field_name: str,
    issues: list[BenchmarkRunContractIssue],
    *,
    minimum: int,
) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        issues.append(_issue(f"invalid_{field_name}", f"{field_name} must be a string list"))
        return []
    if len(value) < minimum:
        issues.append(_issue(f"too_few_{field_name}", f"{field_name} must include at least {minimum} entries"))
    return list(value)


def _required_text(
    data: dict[str, Any],
    field_name: str,
    issues: list[BenchmarkRunContractIssue],
    *,
    prefix: str | None = None,
) -> str | None:
    value = data.get(field_name)
    label = f"{prefix}.{field_name}" if prefix else field_name
    code = f"invalid_{prefix}_{field_name}" if prefix else f"invalid_{field_name}"
    if not isinstance(value, str) or not value.strip():
        issues.append(_issue(code, f"{label} must be non-empty text"))
        return None
    return value


def _command_value(command: object, flag: str) -> str | None:
    if not isinstance(command, list) or flag not in command:
        return None
    index = command.index(flag)
    if index + 1 >= len(command):
        return None
    value = command[index + 1]
    return value if isinstance(value, str) else None


def _load_mapping(
    value: object | str | Path,
    root_path: Path,
) -> tuple[dict[str, Any] | None, list[BenchmarkRunContractIssue]]:
    if isinstance(value, dict):
        return dict(value), []
    try:
        if isinstance(value, str) and value.strip().startswith("{"):
            loaded = json.loads(value)
        else:
            path = Path(value)
            if not path.is_absolute():
                path = root_path / path
            loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return None, [_issue("unreadable_record", f"record could not be loaded: {exc}")]
    if not isinstance(loaded, dict):
        return None, [_issue("invalid_shape", "record must be a JSON object")]
    return loaded, []


def _issue(code: str, message: str) -> BenchmarkRunContractIssue:
    return BenchmarkRunContractIssue(code, message)
