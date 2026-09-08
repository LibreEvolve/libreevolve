from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.core.jsonl import (
    StrictJsonlError,
    iter_strict_jsonl_objects,
    load_strict_json_object,
)

VALIDATOR_EXECUTION_POLICY_SCHEMA = "libreevolve.validator_execution_policy.v1"
VALIDATOR_FILESYSTEM_CAPABILITIES_SCHEMA = (
    "libreevolve.validator_filesystem_capabilities.v1"
)
VALIDATOR_RESOURCE_LIMIT_POLICY_SCHEMA = (
    "libreevolve.validator_resource_limit_policy.v1"
)
VALIDATOR_NETWORK_POLICIES = {"host", "deny"}
VALIDATOR_BOUNDARY_CONSISTENCY_VALIDATOR = (
    "validate_validator_boundary_consistency.v1"
)
VALIDATOR_BOUNDARY_CONSISTENCY_FIELDS = (
    "policy",
    "execution",
    "security_sandbox",
    "container",
    "filesystem_capability_model",
    "filesystem_capabilities",
    "network_policy",
    "network_egress",
    "network_denial",
    "network_denial_scope",
    "resource_limits",
    "resource_limit_policy",
    "secret_boundary",
)
RUN_ARTIFACT_VALIDATOR_BOUNDARY_CONSISTENCY_SCHEMA = (
    "libreevolve.run_artifact_validator_boundary_consistency.v1"
)
RUN_ARTIFACT_VALIDATOR_BOUNDARY_STREAMS = (
    "history.jsonl",
    "failure_history.jsonl",
)


@dataclass(frozen=True)
class ValidatorPolicyIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ValidatorPolicyValidation:
    ok: bool
    local_boundary_ready: bool
    sandbox_ready: bool
    network_policy: str | None
    issues: list[ValidatorPolicyIssue]


@dataclass(frozen=True)
class ValidatorBoundaryConsistencyValidation:
    ok: bool
    local_boundary_ready: bool
    sandbox_ready: bool
    network_policy: str | None
    compared_fields: list[str]
    issues: list[ValidatorPolicyIssue]


@dataclass(frozen=True)
class ValidatorBoundaryArtifactIssue:
    code: str
    message: str
    stream: str | None = None
    line_number: int | None = None


@dataclass(frozen=True)
class ValidatorBoundaryArtifactValidation:
    ok: bool
    schema: str
    manifest_policy_present: bool
    checked_attempts: int
    checked_streams: list[str]
    issues: list[ValidatorBoundaryArtifactIssue]


def validate_validator_execution_policy(
    policy: object | str | Path,
) -> ValidatorPolicyValidation:
    """Validate the manifest-visible validator execution boundary record."""
    data, read_issues = _load_policy(policy)
    if read_issues:
        return ValidatorPolicyValidation(False, False, False, None, read_issues)
    assert isinstance(data, dict)
    issues: list[ValidatorPolicyIssue] = []
    _expect(data, "schema", VALIDATOR_EXECUTION_POLICY_SCHEMA, issues)
    _expect(data, "policy", "local_subprocess_boundary_v1", issues)
    _expect(data, "execution", "temporary_local_subprocess", issues)
    _expect(data, "security_sandbox", "unsupported", issues)
    _expect(data, "container", "unsupported", issues)
    _expect(
        data,
        "filesystem_capability_model",
        "candidate_root_plus_declared_problem_files",
        issues,
    )
    _validate_filesystem_scope(data.get("filesystem_scope"), issues)
    _validate_filesystem_capabilities(data.get("filesystem_capabilities"), issues)
    network_policy = _validate_network(data, issues)
    _validate_resource_limits(data.get("resource_limits"), issues)
    _validate_resource_limit_policy(data.get("resource_limit_policy"), issues)
    _expect(data, "startup_manifest_only", True, issues)
    _expect(data, "per_evaluation_metadata", "evaluation.metadata.validator_boundary", issues)
    _expect(
        data,
        "boundary_consistency_validator",
        VALIDATOR_BOUNDARY_CONSISTENCY_VALIDATOR,
        issues,
    )
    fields = data.get("boundary_consistency_fields")
    if list(VALIDATOR_BOUNDARY_CONSISTENCY_FIELDS) != fields:
        issues.append(
            ValidatorPolicyIssue(
                "invalid_boundary_consistency_fields",
                "boundary_consistency_fields must name the shared policy/boundary fields",
            )
        )
    if not isinstance(data.get("remaining_gap"), str) or not data["remaining_gap"].strip():
        issues.append(
            ValidatorPolicyIssue(
                "invalid_remaining_gap",
                "validator policy must describe unsupported enforcement gaps",
            )
        )
    sandbox_ready = (
        data.get("security_sandbox") != "unsupported"
        and data.get("container") != "unsupported"
        and not _resource_policy_declares_unsupported(data.get("resource_limit_policy"))
    )
    return ValidatorPolicyValidation(
        ok=not issues,
        local_boundary_ready=not issues,
        sandbox_ready=not issues and sandbox_ready,
        network_policy=network_policy,
        issues=issues,
    )


def validate_validator_boundary_consistency(
    policy: object | str | Path,
    boundary: object | str | Path,
) -> ValidatorBoundaryConsistencyValidation:
    """Validate that manifest policy and per-attempt boundary claims agree."""
    policy_data, policy_read_issues = _load_policy(policy)
    boundary_data, boundary_read_issues = _load_policy(boundary)
    issues = list(policy_read_issues)
    issues.extend(
        ValidatorPolicyIssue(f"boundary_{issue.code}", issue.message)
        for issue in boundary_read_issues
    )
    if policy_data is None or boundary_data is None:
        return ValidatorBoundaryConsistencyValidation(
            ok=False,
            local_boundary_ready=False,
            sandbox_ready=False,
            network_policy=None,
            compared_fields=[],
            issues=issues,
        )

    policy_validation = validate_validator_execution_policy(policy_data)
    issues.extend(policy_validation.issues)
    _validate_boundary_record(boundary_data, issues)
    for field in VALIDATOR_BOUNDARY_CONSISTENCY_FIELDS:
        if policy_data.get(field) != boundary_data.get(field):
            issues.append(
                ValidatorPolicyIssue(
                    f"boundary_{field}_mismatch",
                    f"boundary {field} must match validator execution policy",
                )
            )
    return ValidatorBoundaryConsistencyValidation(
        ok=not issues,
        local_boundary_ready=not issues,
        sandbox_ready=False,
        network_policy=policy_validation.network_policy,
        compared_fields=list(VALIDATOR_BOUNDARY_CONSISTENCY_FIELDS),
        issues=issues,
    )


def validate_run_artifact_validator_boundary_consistency(
    run_dir: str | Path,
) -> ValidatorBoundaryArtifactValidation:
    """Validate persisted evaluator-boundary evidence across a run directory."""
    root = Path(run_dir)
    issues: list[ValidatorBoundaryArtifactIssue] = []
    checked_attempts = 0
    checked_streams: list[str] = []
    manifest_path = root / "manifest.json"
    try:
        manifest = load_strict_json_object(manifest_path, source="manifest.json")
    except StrictJsonlError as exc:
        return ValidatorBoundaryArtifactValidation(
            ok=False,
            schema=RUN_ARTIFACT_VALIDATOR_BOUNDARY_CONSISTENCY_SCHEMA,
            manifest_policy_present=False,
            checked_attempts=0,
            checked_streams=[],
            issues=[
                ValidatorBoundaryArtifactIssue(
                    "invalid_manifest_json",
                    str(exc),
                )
            ],
        )
    runtime = manifest.get("runtime")
    if runtime is None:
        return ValidatorBoundaryArtifactValidation(
            ok=True,
            schema=RUN_ARTIFACT_VALIDATOR_BOUNDARY_CONSISTENCY_SCHEMA,
            manifest_policy_present=False,
            checked_attempts=0,
            checked_streams=[],
            issues=[],
        )
    policies = manifest.get("policies")
    policy = policies.get("validator_execution") if isinstance(policies, dict) else None
    if not isinstance(policy, dict):
        issues.append(
            ValidatorBoundaryArtifactIssue(
                "missing_validator_execution_policy",
                "manifest.json must include policies.validator_execution for run-boundary validation",
            )
        )
        return ValidatorBoundaryArtifactValidation(
            ok=False,
            schema=RUN_ARTIFACT_VALIDATOR_BOUNDARY_CONSISTENCY_SCHEMA,
            manifest_policy_present=False,
            checked_attempts=0,
            checked_streams=[],
            issues=issues,
        )

    policy_validation = validate_validator_execution_policy(policy)
    for issue in policy_validation.issues:
        issues.append(
            ValidatorBoundaryArtifactIssue(
                issue.code,
                issue.message,
                stream="manifest.json",
            )
        )

    for stream in RUN_ARTIFACT_VALIDATOR_BOUNDARY_STREAMS:
        path = root / stream
        if not path.exists():
            if stream == "history.jsonl":
                issues.append(
                    ValidatorBoundaryArtifactIssue(
                        "missing_history_stream",
                        "history.jsonl must exist for run-boundary validation",
                        stream=stream,
                    )
                )
            continue
        checked_streams.append(stream)
        try:
            records = iter_strict_jsonl_objects(path, stream_name=stream)
            for line_number, record in enumerate(records, start=1):
                if _validate_run_artifact_boundary_record(
                    policy,
                    record,
                    stream,
                    line_number,
                    issues,
                ):
                    checked_attempts += 1
        except StrictJsonlError as exc:
            issues.append(
                ValidatorBoundaryArtifactIssue(
                    "invalid_jsonl_stream",
                    str(exc),
                    stream=stream,
                )
            )

    if checked_attempts == 0:
        issues.append(
            ValidatorBoundaryArtifactIssue(
                "missing_evaluation_attempts",
                "run-boundary validation requires at least one persisted evaluation attempt",
            )
        )
    return ValidatorBoundaryArtifactValidation(
        ok=not issues,
        schema=RUN_ARTIFACT_VALIDATOR_BOUNDARY_CONSISTENCY_SCHEMA,
        manifest_policy_present=True,
        checked_attempts=checked_attempts,
        checked_streams=checked_streams,
        issues=issues,
    )


def _validate_run_artifact_boundary_record(
    policy: dict[str, Any],
    record: dict[str, Any],
    stream: str,
    line_number: int,
    issues: list[ValidatorBoundaryArtifactIssue],
) -> bool:
    evaluation = record.get("evaluation")
    if evaluation is None:
        if _is_non_validator_attempt_record(record, None):
            return False
        issues.append(
            ValidatorBoundaryArtifactIssue(
                "missing_evaluation",
                "persisted current run rows must include evaluation objects",
                stream=stream,
                line_number=line_number,
            )
        )
        return False
    if not isinstance(evaluation, dict):
        issues.append(
            ValidatorBoundaryArtifactIssue(
                "invalid_evaluation",
                "evaluation must be an object",
                stream=stream,
                line_number=line_number,
            )
        )
        return False
    if _is_non_validator_attempt_record(record, evaluation):
        return False
    metadata = evaluation.get("metadata")
    if not isinstance(metadata, dict):
        issues.append(
            ValidatorBoundaryArtifactIssue(
                "missing_evaluation_metadata",
                "evaluation.metadata must carry validator_boundary",
                stream=stream,
                line_number=line_number,
            )
        )
        return False
    boundary = metadata.get("validator_boundary")
    if not isinstance(boundary, dict):
        issues.append(
            ValidatorBoundaryArtifactIssue(
                "missing_validator_boundary",
                "evaluation.metadata.validator_boundary must be an object",
                stream=stream,
                line_number=line_number,
            )
        )
        return False
    validation = validate_validator_boundary_consistency(policy, boundary)
    for issue in validation.issues:
        issues.append(
            ValidatorBoundaryArtifactIssue(
                issue.code,
                issue.message,
                stream=stream,
                line_number=line_number,
            )
        )
    return True


def _is_non_validator_attempt_record(
    record: dict[str, Any],
    evaluation: dict[str, Any] | None,
) -> bool:
    """Return True for persisted failures that never crossed the validator boundary."""
    if evaluation is not None:
        metadata = evaluation.get("metadata")
        if isinstance(metadata, dict):
            candidate_runner_scorers = _candidate_runner_scorer_states(metadata)
            if candidate_runner_scorers:
                return not any(candidate_runner_scorers)
        if isinstance(metadata, dict) and (
            isinstance(metadata.get("syntax_errors"), list)
            or isinstance(metadata.get("synthetic_metrics"), dict)
        ):
            return True
        stages = evaluation.get("stages")
        error = evaluation.get("error")
        if isinstance(stages, list) and stages and not any(
            isinstance(stage, dict) and stage.get("name") == "validate"
            for stage in stages
        ):
            return True
        if error == "syntax_error":
            return True
        if error == "llm_mutation_failed" and stages == []:
            return True
    if record.get("error") == "llm_mutation_failed" or record.get("diff_error") == "llm_mutation_failed":
        return True
    return False


def _candidate_runner_scorer_states(value: object) -> list[bool]:
    states: list[bool] = []
    if isinstance(value, dict):
        candidate_runner = value.get("candidate_runner")
        if (
            isinstance(candidate_runner, dict)
            and candidate_runner.get("schema")
            == "libreevolve.candidate_runner_execution.v1"
        ):
            states.append(candidate_runner.get("scorer_process_started") is True)
        for key, item in value.items():
            if key != "candidate_runner":
                states.extend(_candidate_runner_scorer_states(item))
    elif isinstance(value, list):
        for item in value:
            states.extend(_candidate_runner_scorer_states(item))
    return states


def _load_policy(
    policy: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ValidatorPolicyIssue]]:
    if isinstance(policy, dict):
        return dict(policy), []
    if isinstance(policy, (str, Path)):
        path = Path(policy)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [
                ValidatorPolicyIssue(
                    "read_error",
                    f"failed to read validator execution policy: {exc}",
                )
            ]
        except json.JSONDecodeError as exc:
            return None, [
                ValidatorPolicyIssue(
                    "invalid_json",
                    f"invalid validator execution policy JSON: {exc.msg}",
                )
            ]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [
        ValidatorPolicyIssue(
            "invalid_shape",
            "validator execution policy must be a JSON object",
        )
    ]


def _validate_boundary_record(
    boundary: dict[str, Any],
    issues: list[ValidatorPolicyIssue],
) -> None:
    _expect_boundary(boundary, "policy", "local_subprocess_boundary_v1", issues)
    _expect_boundary(boundary, "execution", "temporary_local_subprocess", issues)
    _expect_boundary(boundary, "security_sandbox", "unsupported", issues)
    _expect_boundary(boundary, "container", "unsupported", issues)
    _expect_boundary(
        boundary,
        "filesystem_capability_model",
        "candidate_root_plus_declared_problem_files",
        issues,
    )
    _validate_filesystem_capabilities(
        boundary.get("filesystem_capabilities"),
        issues,
        code_prefix="boundary_",
    )
    _validate_network(boundary, issues, code_prefix="boundary_")
    _validate_resource_limits(
        boundary.get("resource_limits"),
        issues,
        code_prefix="boundary_",
    )
    _validate_resource_limit_policy(
        boundary.get("resource_limit_policy"),
        issues,
        code_prefix="boundary_",
    )
    _expect_boundary(
        boundary,
        "secret_boundary",
        "minimal_environment_allowlist_with_redacted_diagnostics",
        issues,
    )


def _expect(
    data: dict[str, Any],
    field: str,
    expected: object,
    issues: list[ValidatorPolicyIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(
            ValidatorPolicyIssue(
                f"invalid_{field}",
                f"{field} must be {expected!r}",
            )
        )


def _expect_boundary(
    data: dict[str, Any],
    field: str,
    expected: object,
    issues: list[ValidatorPolicyIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(
            ValidatorPolicyIssue(
                f"invalid_boundary_{field}",
                f"boundary {field} must be {expected!r}",
            )
        )


def _validate_filesystem_scope(
    value: object,
    issues: list[ValidatorPolicyIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(
            ValidatorPolicyIssue(
                "invalid_filesystem_scope",
                "filesystem_scope must be an object",
            )
        )
        return
    _expect(value, "cwd", "materialized_candidate_root", issues)
    _expect(value, "candidate_files", "materialized_under_temporary_candidate_root", issues)
    _expect(value, "host_filesystem_sandbox", "unsupported", issues)


def _validate_filesystem_capabilities(
    value: object,
    issues: list[ValidatorPolicyIssue],
    *,
    code_prefix: str = "",
) -> None:
    if not isinstance(value, dict):
        issues.append(
            ValidatorPolicyIssue(
                f"{code_prefix}invalid_filesystem_capabilities",
                "filesystem_capabilities must be an object",
            )
        )
        return
    _expect(value, "schema", VALIDATOR_FILESYSTEM_CAPABILITIES_SCHEMA, issues)
    _expect(value, "policy", "candidate_root_plus_declared_problem_files", issues)
    _expect(value, "enforcement", "python_runner_problem_local_provenance_checks", issues)
    cwd = value.get("cwd")
    if not isinstance(cwd, dict) or not all(
        cwd.get(field) is True for field in ("read", "write", "execute")
    ):
        issues.append(
            ValidatorPolicyIssue(
                f"{code_prefix}invalid_filesystem_cwd",
                "cwd capability must allow read/write/execute in candidate root",
            )
        )
    declared = value.get("declared_problem_files")
    if not isinstance(declared, dict) or not (
        declared.get("read") is True
        and declared.get("write") is False
        and declared.get("execute") is True
    ):
        issues.append(
            ValidatorPolicyIssue(
                f"{code_prefix}invalid_declared_problem_file_capability",
                "declared problem files must be read/execute and no-write",
            )
        )
    host = value.get("host_filesystem")
    if not isinstance(host, dict) or not (
        host.get("os_sandbox") == "unsupported"
        and host.get("ambient_access_possible") is True
        and host.get("undeclared_host_paths") == "not_capability_enforced"
    ):
        issues.append(
            ValidatorPolicyIssue(
                f"{code_prefix}invalid_host_filesystem_boundary",
                "host filesystem boundary must not overclaim OS capability enforcement",
            )
        )


def _validate_network(
    data: dict[str, Any],
    issues: list[ValidatorPolicyIssue],
    *,
    code_prefix: str = "",
) -> str | None:
    network_policy = data.get("network_policy")
    if not isinstance(network_policy, str) or network_policy not in VALIDATOR_NETWORK_POLICIES:
        issues.append(
            ValidatorPolicyIssue(
                f"{code_prefix}invalid_network_policy",
                "network_policy must be host or deny",
            )
        )
        return None
    expected = (
        {
            "network_egress": "python_socket_denied_not_os_sandbox",
            "network_denial": "python_socket_monkeypatch",
        }
        if network_policy == "deny"
        else {
            "network_egress": "host_inherited_not_sandboxed",
            "network_denial": "unsupported",
        }
    )
    for field, expected_value in expected.items():
        _expect(data, field, expected_value, issues)
    _expect(
        data,
        "network_denial_scope",
        "python_socket_api_only_not_kernel_or_container",
        issues,
    )
    return network_policy


def _validate_resource_limits(
    value: object,
    issues: list[ValidatorPolicyIssue],
    *,
    code_prefix: str = "",
) -> None:
    if not isinstance(value, dict):
        issues.append(
            ValidatorPolicyIssue(
                f"{code_prefix}invalid_resource_limits",
                "resource_limits must be an object",
            )
        )
        return
    _expect(value, "wall_clock_timeout", "configured_stage_or_sample_timeout", issues)
    for field in ("cpu", "memory", "gpu", "disk", "process_count"):
        _expect(value, field, "unsupported", issues)


def _validate_resource_limit_policy(
    value: object,
    issues: list[ValidatorPolicyIssue],
    *,
    code_prefix: str = "",
) -> None:
    if not isinstance(value, dict):
        issues.append(
            ValidatorPolicyIssue(
                f"{code_prefix}invalid_resource_limit_policy",
                "resource_limit_policy must be an object",
            )
        )
        return
    _expect(value, "schema", VALIDATOR_RESOURCE_LIMIT_POLICY_SCHEMA, issues)
    _expect(value, "policy", "wall_clock_timeout_only", issues)
    _expect(value, "enforcement", "local_subprocess_timeout_cleanup", issues)
    wall = value.get("wall_clock_timeout")
    if not isinstance(wall, dict) or wall.get("supported") is not True:
        issues.append(
            ValidatorPolicyIssue(
                f"{code_prefix}invalid_wall_clock_limit_policy",
                "wall_clock_timeout must be the only supported quota",
            )
        )
    for field in ("cpu", "memory", "gpu", "disk", "process_count"):
        quota = value.get(field)
        if not isinstance(quota, dict) or not (
            quota.get("supported") is False and quota.get("quota") == "unsupported"
        ):
            issues.append(
                ValidatorPolicyIssue(
                    f"{code_prefix}invalid_{field}_limit_policy",
                    f"{field} limits must be declared unsupported",
                )
            )
    _expect(value, "container_runtime_limits", "unsupported", issues)


def _resource_policy_declares_unsupported(value: object) -> bool:
    if not isinstance(value, dict):
        return True
    return any(
        isinstance(value.get(field), dict) and value[field].get("supported") is False
        for field in ("cpu", "memory", "gpu", "disk", "process_count")
    ) or value.get("container_runtime_limits") == "unsupported"
