from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

VALIDATOR_EXECUTION_POLICY_SCHEMA = "libreevolve.validator_execution_policy.v1"
VALIDATOR_FILESYSTEM_CAPABILITIES_SCHEMA = (
    "libreevolve.validator_filesystem_capabilities.v1"
)
VALIDATOR_RESOURCE_LIMIT_POLICY_SCHEMA = (
    "libreevolve.validator_resource_limit_policy.v1"
)
VALIDATOR_NETWORK_POLICIES = {"host", "deny"}


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
) -> None:
    if not isinstance(value, dict):
        issues.append(
            ValidatorPolicyIssue(
                "invalid_filesystem_capabilities",
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
                "invalid_filesystem_cwd",
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
                "invalid_declared_problem_file_capability",
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
                "invalid_host_filesystem_boundary",
                "host filesystem boundary must not overclaim OS capability enforcement",
            )
        )


def _validate_network(
    data: dict[str, Any],
    issues: list[ValidatorPolicyIssue],
) -> str | None:
    network_policy = data.get("network_policy")
    if not isinstance(network_policy, str) or network_policy not in VALIDATOR_NETWORK_POLICIES:
        issues.append(
            ValidatorPolicyIssue(
                "invalid_network_policy",
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
) -> None:
    if not isinstance(value, dict):
        issues.append(
            ValidatorPolicyIssue(
                "invalid_resource_limits",
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
) -> None:
    if not isinstance(value, dict):
        issues.append(
            ValidatorPolicyIssue(
                "invalid_resource_limit_policy",
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
                "invalid_wall_clock_limit_policy",
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
                    f"invalid_{field}_limit_policy",
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
