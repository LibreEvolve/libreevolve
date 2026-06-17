from __future__ import annotations

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
from libreevolve.problems.benchmarks.benchmark_run_contract import (
    validate_benchmark_run_contract,
)


BENCHMARK_PROVIDER_PROFILE_SCHEMA = "libreevolve.benchmark_provider_profile.v1"
SAFE_PROFILE_ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]{0,127}$")
SUPPORT_STATUSES = {
    "experimental_protocol_input_not_benchmark_evidence",
    "supported_profile_without_certified_run_evidence",
    "local_only_profile",
}


@dataclass(frozen=True)
class BenchmarkProviderProfileIssue:
    code: str
    message: str


@dataclass(frozen=True)
class BenchmarkProviderProfileValidation:
    ok: bool
    profile_id: str | None
    problem_id: str | None
    support_status: str | None
    backend_type: str | None
    model: str | None
    issues: list[BenchmarkProviderProfileIssue]


def validate_benchmark_provider_profile(
    profile_record: object | str | Path,
    *,
    root: str | Path = ".",
) -> BenchmarkProviderProfileValidation:
    """Validate a committed benchmark provider-profile hygiene artifact."""

    root_path = Path(root)
    data, read_issues = _load_mapping(profile_record, root_path)
    if read_issues:
        return BenchmarkProviderProfileValidation(False, None, None, None, None, None, read_issues)
    assert isinstance(data, dict)
    issues: list[BenchmarkProviderProfileIssue] = []

    if data.get("schema") != BENCHMARK_PROVIDER_PROFILE_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported benchmark provider-profile schema"))
    profile_id = _required_text(data, "profile_id", issues)
    if profile_id is not None and SAFE_PROFILE_ID_PATTERN.fullmatch(profile_id) is None:
        issues.append(_issue("invalid_profile_id", "profile_id must be a safe stable id"))
    problem_id = _required_text(data, "problem_id", issues)
    support_status = _required_text(data, "support_status", issues)
    if support_status is not None and support_status not in SUPPORT_STATUSES:
        issues.append(_issue("invalid_support_status", "support_status is unsupported"))
    if data.get("claim_ready") is True:
        issues.append(_issue("claim_ready_overclaim", "provider profiles must not claim benchmark readiness"))

    config_path = _validate_existing_path(data, "config_path", root_path, issues)
    contract_path = _validate_existing_path(data, "run_contract_path", root_path, issues)
    prompt_path = _validate_existing_path(data, "benchmark_goal_prompt_path", root_path, issues)

    provider_lane = _validate_provider_lane(data.get("provider_lane"), issues)
    budget = _validate_budget(data.get("budget"), issues)
    transcript_policy = _validate_transcript_policy(data.get("transcript_policy"), provider_lane, issues)
    artifact_expectations = _validate_artifact_expectations(data.get("artifact_expectations"), issues)
    result_linkage = _validate_result_linkage(data.get("result_linkage"), issues)

    config = _load_yaml_mapping(config_path, issues)
    contract = _load_json_mapping(contract_path, issues)
    prompt = _load_json_mapping(prompt_path, issues)
    _validate_against_config(config, provider_lane, budget, transcript_policy, issues)
    _validate_against_contract(contract, data, provider_lane, artifact_expectations, result_linkage, issues)
    _validate_against_prompt(prompt, data, provider_lane, result_linkage, issues)
    _validate_linked_artifacts(contract_path, prompt_path, root_path, issues)

    claim_boundary = _required_text(data, "claim_boundary", issues)
    if claim_boundary is not None:
        boundary_text = claim_boundary.lower()
        if "not benchmark evidence" not in boundary_text or "does not certify" not in boundary_text:
            issues.append(_issue("claim_boundary_overclaim", "claim_boundary must reject benchmark evidence and certification claims"))
    if SECRET_LIKE_PATTERN.search(json.dumps(data, sort_keys=True)):
        issues.append(_issue("secret_like_profile_text", "provider profile must not contain secret-like tokens"))

    return BenchmarkProviderProfileValidation(
        ok=not issues,
        profile_id=profile_id,
        problem_id=problem_id,
        support_status=support_status,
        backend_type=provider_lane.get("backend_type"),
        model=provider_lane.get("model"),
        issues=issues,
    )


def render_benchmark_provider_profile_summary(profile_record: dict[str, Any]) -> str:
    validation = validate_benchmark_provider_profile(profile_record)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Benchmark provider profile",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| profile_id | {validation.profile_id or '<unknown>'} |",
        f"| problem_id | {validation.problem_id or '<unknown>'} |",
        f"| support_status | {validation.support_status or '<unknown>'} |",
        f"| backend_type | {validation.backend_type or '<unknown>'} |",
        f"| model | {validation.model or '<unknown>'} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _validate_provider_lane(
    value: object,
    issues: list[BenchmarkProviderProfileIssue],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_provider_lane", "provider_lane must be an object"))
        return {}
    for field in (
        "backend_type",
        "model",
        "auth_name",
        "auth_source_policy",
        "provider_readiness",
    ):
        _required_text(value, field, issues, prefix="provider_lane")
    for field in ("supported_in_ci", "local_auth_required"):
        if not isinstance(value.get(field), bool):
            issues.append(_issue(f"invalid_provider_lane_{field}", f"provider_lane.{field} must be boolean"))
    if value.get("backend_type") == "codex":
        if value.get("provider_readiness") != "requires_local_authenticated_codex_cli":
            issues.append(_issue("invalid_codex_provider_readiness", "Codex profiles must require local authenticated Codex CLI"))
        if value.get("supported_in_ci") is not False:
            issues.append(_issue("codex_ci_overclaim", "Codex current-auth profiles must not claim CI support"))
        if value.get("local_auth_required") is not True:
            issues.append(_issue("codex_auth_requirement_missing", "Codex profiles must require local auth"))
    return dict(value)


def _validate_budget(value: object, issues: list[BenchmarkProviderProfileIssue]) -> dict[str, Any]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_budget", "budget must be an object"))
        return {}
    for field in ("max_generations", "proposals_per_generation", "max_tokens", "timeout_sec"):
        if not isinstance(value.get(field), int) or isinstance(value.get(field), bool) or value[field] <= 0:
            issues.append(_issue(f"invalid_budget_{field}", f"budget.{field} must be a positive integer"))
    if not isinstance(value.get("reasoning_effort"), str) or not value["reasoning_effort"]:
        issues.append(_issue("invalid_budget_reasoning_effort", "budget.reasoning_effort must be non-empty text"))
    return dict(value)


def _validate_transcript_policy(
    value: object,
    provider_lane: dict[str, Any],
    issues: list[BenchmarkProviderProfileIssue],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_transcript_policy", "transcript_policy must be an object"))
        return {}
    for field in ("transcript_dir", "retention_policy", "redaction_policy"):
        _required_text(value, field, issues, prefix="transcript_policy")
    if not isinstance(value.get("raw_transcripts_committed"), bool):
        issues.append(_issue("invalid_transcript_policy_raw_transcripts_committed", "raw_transcripts_committed must be boolean"))
    if provider_lane.get("backend_type") == "codex" and "codex" not in str(value.get("transcript_dir", "")):
        issues.append(_issue("invalid_codex_transcript_dir", "Codex transcript_dir should identify Codex transcripts"))
    if "no_secrets" not in str(value.get("redaction_policy", "")):
        issues.append(_issue("invalid_transcript_redaction_policy", "redaction_policy must include no_secrets"))
    if value.get("raw_transcripts_committed") is not False:
        issues.append(_issue("raw_transcript_commit_overclaim", "raw transcripts must not be committed by default"))
    return dict(value)


def _validate_artifact_expectations(
    value: object,
    issues: list[BenchmarkProviderProfileIssue],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_artifact_expectations", "artifact_expectations must be an object"))
        return {}
    for field in ("run_name", "expected_run_dir"):
        _required_text(value, field, issues, prefix="artifact_expectations")
    artifacts = value.get("expected_artifacts")
    if not isinstance(artifacts, list) or not all(isinstance(item, str) and item for item in artifacts):
        issues.append(_issue("invalid_artifact_expectations_expected_artifacts", "expected_artifacts must be a string list"))
    else:
        for required in ("manifest.json", "evaluator_results.jsonl", "best.py"):
            if required not in artifacts:
                issues.append(_issue(f"missing_expected_artifact_{required.replace('.', '_')}", f"expected_artifacts must include {required}"))
        if not any("transcript" in artifact for artifact in artifacts):
            issues.append(_issue("missing_transcript_artifact_expectation", "expected_artifacts must include transcript evidence"))
    return dict(value)


def _validate_result_linkage(
    value: object,
    issues: list[BenchmarkProviderProfileIssue],
) -> dict[str, Any]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_result_linkage", "result_linkage must be an object"))
        return {}
    for field in ("prompt_id", "target_metric", "target_condition", "certification_status"):
        _required_text(value, field, issues, prefix="result_linkage")
    if not isinstance(value.get("validated_run_artifacts_committed"), bool):
        issues.append(_issue("invalid_result_linkage_validated_run_artifacts_committed", "validated_run_artifacts_committed must be boolean"))
    if value.get("validated_run_artifacts_committed") is not False:
        issues.append(_issue("run_artifact_evidence_overclaim", "profile must not claim committed run artifacts until evidence exists"))
    if value.get("certification_status") != "not_certified":
        issues.append(_issue("certification_status_overclaim", "certification_status must remain not_certified"))
    return dict(value)


def _validate_against_config(
    config: dict[str, Any] | None,
    provider_lane: dict[str, Any],
    budget: dict[str, Any],
    transcript_policy: dict[str, Any],
    issues: list[BenchmarkProviderProfileIssue],
) -> None:
    if config is None:
        return
    backends = config.get("backends")
    if not isinstance(backends, list) or not backends or not isinstance(backends[0], dict):
        issues.append(_issue("invalid_config_backends", "config must define one backend"))
        return
    backend = backends[0]
    comparisons = {
        "type": provider_lane.get("backend_type"),
        "model": provider_lane.get("model"),
        "auth_name": provider_lane.get("auth_name"),
        "max_tokens": budget.get("max_tokens"),
        "timeout_sec": budget.get("timeout_sec"),
        "reasoning_effort": budget.get("reasoning_effort"),
        "transcript_dir": transcript_policy.get("transcript_dir"),
    }
    for field, expected in comparisons.items():
        if backend.get(field) != expected:
            issues.append(_issue(f"config_{field}_mismatch", f"config backend {field} must match provider profile"))
    if backend.get("sandbox") != "read-only":
        issues.append(_issue("config_sandbox_not_read_only", "benchmark provider profile requires read-only sandbox"))


def _validate_against_contract(
    contract: dict[str, Any] | None,
    data: dict[str, Any],
    provider_lane: dict[str, Any],
    artifact_expectations: dict[str, Any],
    result_linkage: dict[str, Any],
    issues: list[BenchmarkProviderProfileIssue],
) -> None:
    if contract is None:
        return
    auth_setup = contract.get("auth_setup") if isinstance(contract.get("auth_setup"), dict) else {}
    for field, expected in (
        ("problem_id", data.get("problem_id")),
        ("backend_type", provider_lane.get("backend_type")),
        ("model", provider_lane.get("model")),
        ("auth_name", provider_lane.get("auth_name")),
    ):
        actual = contract.get(field) if field == "problem_id" else auth_setup.get(field)
        if actual != expected:
            issues.append(_issue(f"contract_{field}_mismatch", f"run contract {field} must match provider profile"))
    if contract.get("expected_run_dir") != artifact_expectations.get("expected_run_dir"):
        issues.append(_issue("contract_expected_run_dir_mismatch", "run contract expected_run_dir must match provider profile"))
    if contract.get("expected_artifacts") != artifact_expectations.get("expected_artifacts"):
        issues.append(_issue("contract_expected_artifacts_mismatch", "run contract expected_artifacts must match provider profile"))
    provenance = contract.get("goal_prompt_provenance")
    if not isinstance(provenance, dict) or provenance.get("prompt_id") != result_linkage.get("prompt_id"):
        issues.append(_issue("contract_prompt_id_mismatch", "run contract prompt id must match result_linkage.prompt_id"))


def _validate_against_prompt(
    prompt: dict[str, Any] | None,
    data: dict[str, Any],
    provider_lane: dict[str, Any],
    result_linkage: dict[str, Any],
    issues: list[BenchmarkProviderProfileIssue],
) -> None:
    if prompt is None:
        return
    for field, expected in (
        ("problem_id", data.get("problem_id")),
        ("model", provider_lane.get("model")),
        ("backend_type", provider_lane.get("backend_type")),
        ("auth_name", provider_lane.get("auth_name")),
        ("prompt_id", result_linkage.get("prompt_id")),
    ):
        if prompt.get(field) != expected:
            issues.append(_issue(f"prompt_{field}_mismatch", f"benchmark goal prompt {field} must match provider profile"))


def _validate_linked_artifacts(
    contract_path: Path | None,
    prompt_path: Path | None,
    root_path: Path,
    issues: list[BenchmarkProviderProfileIssue],
) -> None:
    if contract_path is not None and contract_path.is_file():
        validation = validate_benchmark_run_contract(contract_path, root=root_path)
        issues.extend(_issue(f"run_contract_{issue.code}", issue.message) for issue in validation.issues)
    if prompt_path is not None and prompt_path.is_file():
        validation = validate_benchmark_goal_prompt(prompt_path, root=root_path)
        issues.extend(_issue(f"goal_prompt_{issue.code}", issue.message) for issue in validation.issues)


def _validate_existing_path(
    data: dict[str, Any],
    field: str,
    root_path: Path,
    issues: list[BenchmarkProviderProfileIssue],
) -> Path | None:
    value = _required_text(data, field, issues)
    if value is None:
        return None
    path = root_path / value
    if not path.is_file():
        issues.append(_issue(f"missing_{field}", f"{field} must point to a committed file"))
    return path


def _load_json_mapping(path: Path | None, issues: list[BenchmarkProviderProfileIssue]) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        issues.append(_issue("unreadable_linked_json", f"linked JSON could not be loaded: {exc}"))
        return None
    if not isinstance(loaded, dict):
        issues.append(_issue("invalid_linked_json", "linked JSON must be an object"))
        return None
    return loaded


def _load_yaml_mapping(path: Path | None, issues: list[BenchmarkProviderProfileIssue]) -> dict[str, Any] | None:
    if path is None or not path.is_file():
        return None
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        issues.append(_issue("unreadable_linked_yaml", f"linked YAML could not be loaded: {exc}"))
        return None
    if not isinstance(loaded, dict):
        issues.append(_issue("invalid_linked_yaml", "linked YAML must be an object"))
        return None
    return loaded


def _required_text(
    data: dict[str, Any],
    field: str,
    issues: list[BenchmarkProviderProfileIssue],
    *,
    prefix: str | None = None,
) -> str | None:
    value = data.get(field)
    label = f"{prefix}.{field}" if prefix else field
    code = f"invalid_{prefix}_{field}" if prefix else f"invalid_{field}"
    if not isinstance(value, str) or not value.strip():
        issues.append(_issue(code, f"{label} must be non-empty text"))
        return None
    return value


def _load_mapping(
    value: object | str | Path,
    root_path: Path,
) -> tuple[dict[str, Any] | None, list[BenchmarkProviderProfileIssue]]:
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


def _issue(code: str, message: str) -> BenchmarkProviderProfileIssue:
    return BenchmarkProviderProfileIssue(code, message)
