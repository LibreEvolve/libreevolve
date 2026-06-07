import json

from libreevolve.core.database import _validator_execution_policy
from libreevolve.core.evaluator import _validator_boundary_metadata
from libreevolve.core.validator_policy import (
    VALIDATOR_BOUNDARY_CONSISTENCY_FIELDS,
    VALIDATOR_BOUNDARY_CONSISTENCY_VALIDATOR,
    VALIDATOR_EXECUTION_POLICY_SCHEMA,
    validate_validator_boundary_consistency,
    validate_validator_execution_policy,
)


def test_validator_execution_policy_validates_manifest_record():
    policy = _validator_execution_policy("deny")

    validation = validate_validator_execution_policy(policy)

    assert validation.ok is True
    assert validation.local_boundary_ready is True
    assert validation.sandbox_ready is False
    assert validation.network_policy == "deny"
    assert validation.issues == []
    assert policy["schema"] == VALIDATOR_EXECUTION_POLICY_SCHEMA
    assert policy["boundary_consistency_validator"] == (
        VALIDATOR_BOUNDARY_CONSISTENCY_VALIDATOR
    )
    assert policy["boundary_consistency_fields"] == list(
        VALIDATOR_BOUNDARY_CONSISTENCY_FIELDS
    )


def test_validator_execution_policy_loads_json_file(tmp_path):
    path = tmp_path / "validator-policy.json"
    path.write_text(json.dumps(_validator_execution_policy("host")), encoding="utf-8")

    validation = validate_validator_execution_policy(path)

    assert validation.ok is True
    assert validation.local_boundary_ready is True
    assert validation.network_policy == "host"


def test_validator_execution_policy_rejects_sandbox_and_resource_overclaims():
    policy = _validator_execution_policy("host")
    policy["security_sandbox"] = "docker"
    policy["container"] = "docker"
    policy["filesystem_scope"]["host_filesystem_sandbox"] = "supported"
    policy["filesystem_capabilities"]["host_filesystem"] = {
        "os_sandbox": "supported",
        "ambient_access_possible": False,
        "undeclared_host_paths": "denied",
    }
    policy["resource_limits"]["memory"] = "1GiB"
    policy["resource_limit_policy"]["memory"] = {
        "supported": True,
        "quota": "1GiB",
    }

    validation = validate_validator_execution_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.sandbox_ready is False
    assert "invalid_security_sandbox" in codes
    assert "invalid_container" in codes
    assert "invalid_host_filesystem_sandbox" in codes
    assert "invalid_host_filesystem_boundary" in codes
    assert "invalid_memory" in codes
    assert "invalid_memory_limit_policy" in codes


def test_validator_execution_policy_rejects_network_boundary_mismatch():
    policy = _validator_execution_policy("deny")
    policy["network_egress"] = "host_inherited_not_sandboxed"
    policy["network_denial"] = "unsupported"
    policy["network_denial_scope"] = "kernel_firewall"

    validation = validate_validator_execution_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.network_policy == "deny"
    assert "invalid_network_egress" in codes
    assert "invalid_network_denial" in codes
    assert "invalid_network_denial_scope" in codes


def test_validator_execution_policy_rejects_missing_structured_records():
    policy = _validator_execution_policy("host")
    policy.pop("filesystem_capabilities")
    policy.pop("resource_limit_policy")
    policy["startup_manifest_only"] = False
    policy["per_evaluation_metadata"] = "missing"

    validation = validate_validator_execution_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_filesystem_capabilities" in codes
    assert "invalid_resource_limit_policy" in codes
    assert "invalid_startup_manifest_only" in codes
    assert "invalid_per_evaluation_metadata" in codes


def test_validator_boundary_consistency_accepts_matching_attempt_boundary():
    policy = _validator_execution_policy("deny")
    boundary = _validator_boundary_metadata("deny")

    validation = validate_validator_boundary_consistency(policy, boundary)

    assert validation.ok is True
    assert validation.local_boundary_ready is True
    assert validation.sandbox_ready is False
    assert validation.network_policy == "deny"
    assert validation.compared_fields == list(VALIDATOR_BOUNDARY_CONSISTENCY_FIELDS)
    assert validation.issues == []


def test_validator_boundary_consistency_rejects_mismatched_attempt_boundary():
    policy = _validator_execution_policy("deny")
    boundary = _validator_boundary_metadata("host")
    boundary["filesystem_capabilities"]["host_filesystem"] = {
        "os_sandbox": "supported",
        "ambient_access_possible": False,
        "undeclared_host_paths": "denied",
    }
    boundary["resource_limit_policy"]["cpu"] = {
        "supported": True,
        "quota": "1 core",
    }

    validation = validate_validator_boundary_consistency(policy, boundary)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.local_boundary_ready is False
    assert validation.sandbox_ready is False
    assert validation.network_policy == "deny"
    assert "boundary_network_policy_mismatch" in codes
    assert "boundary_network_egress_mismatch" in codes
    assert "boundary_network_denial_mismatch" in codes
    assert "boundary_filesystem_capabilities_mismatch" in codes
    assert "boundary_invalid_host_filesystem_boundary" in codes
    assert "boundary_resource_limit_policy_mismatch" in codes
    assert "boundary_invalid_cpu_limit_policy" in codes
