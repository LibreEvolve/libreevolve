import json

from libreevolve.core.database import _validator_execution_policy
from libreevolve.core.evaluator import _validator_boundary_metadata
from libreevolve.core.validator_policy import (
    VALIDATOR_BOUNDARY_CONSISTENCY_FIELDS,
    VALIDATOR_BOUNDARY_CONSISTENCY_VALIDATOR,
    VALIDATOR_EXECUTION_POLICY_SCHEMA,
    validate_run_artifact_validator_boundary_consistency,
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


def test_run_artifact_validator_boundary_consistency_accepts_current_rows(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    policy = _validator_execution_policy("deny")
    boundary = _validator_boundary_metadata("deny")
    (run_dir / "manifest.json").write_text(
        json.dumps({"runtime": {"status": "completed"}, "policies": {"validator_execution": policy}}),
        encoding="utf-8",
    )
    (run_dir / "history.jsonl").write_text(
        json.dumps({"evaluation": {"metadata": {"validator_boundary": boundary}}}) + "\n",
        encoding="utf-8",
    )
    (run_dir / "failure_history.jsonl").write_text(
        json.dumps({"evaluation": {"metadata": {"validator_boundary": boundary}}}) + "\n",
        encoding="utf-8",
    )

    validation = validate_run_artifact_validator_boundary_consistency(run_dir)

    assert validation.ok is True
    assert validation.manifest_policy_present is True
    assert validation.checked_attempts == 2
    assert validation.checked_streams == ["history.jsonl", "failure_history.jsonl"]
    assert validation.issues == []


def test_run_artifact_validator_boundary_consistency_rejects_missing_boundary(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "runtime": {"status": "completed"},
                "policies": {"validator_execution": _validator_execution_policy("host")},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "history.jsonl").write_text(
        json.dumps({"evaluation": {"metadata": {}}}) + "\n",
        encoding="utf-8",
    )

    validation = validate_run_artifact_validator_boundary_consistency(run_dir)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.checked_attempts == 0
    assert "missing_validator_boundary" in codes
    assert "missing_evaluation_attempts" in codes


def test_run_artifact_validator_boundary_consistency_skips_synthetic_syntax_rows(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    boundary = _validator_boundary_metadata("host")
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "runtime": {"status": "completed"},
                "policies": {"validator_execution": _validator_execution_policy("host")},
            }
        ),
        encoding="utf-8",
    )
    rows = [
        {"evaluation": {"metadata": {"validator_boundary": boundary}}},
        {
            "evaluation": {
                "error": "syntax_error",
                "metadata": {
                    "syntax_errors": [{"path": "candidate.py", "message": "invalid syntax"}],
                    "synthetic_metrics": {"policy": "declared_metric_penalty"},
                },
            }
        },
    ]
    (run_dir / "history.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )

    validation = validate_run_artifact_validator_boundary_consistency(run_dir)

    assert validation.ok is True
    assert validation.checked_attempts == 1
    assert validation.issues == []


def test_run_artifact_validator_boundary_consistency_skips_legacy_syntax_rows(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    boundary = _validator_boundary_metadata("host")
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "runtime": {"status": "completed"},
                "policies": {"validator_execution": _validator_execution_policy("host")},
            }
        ),
        encoding="utf-8",
    )
    rows = [
        {"evaluation": {"metadata": {"validator_boundary": boundary}}},
        {
            "evaluation": {
                "error": "syntax_error",
                "stages": [
                    {
                        "name": "syntax",
                        "passed": False,
                        "score": -0.2,
                        "error": "candidate.py: SyntaxError",
                    }
                ],
            }
        },
    ]
    (run_dir / "history.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows),
        encoding="utf-8",
    )

    validation = validate_run_artifact_validator_boundary_consistency(run_dir)

    assert validation.ok is True
    assert validation.checked_attempts == 1
    assert validation.issues == []


def test_run_artifact_validator_boundary_consistency_skips_pre_validator_diff_rows(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    boundary = _validator_boundary_metadata("host")
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "runtime": {"status": "completed"},
                "policies": {"validator_execution": _validator_execution_policy("host")},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "history.jsonl").write_text(
        json.dumps({"evaluation": {"metadata": {"validator_boundary": boundary}}}) + "\n",
        encoding="utf-8",
    )
    (run_dir / "failure_history.jsonl").write_text(
        json.dumps(
            {
                "error": "unknown_diff_error",
                "diff_error": "seed.py:no_valid_changes",
                "evaluation": {
                    "error": "unknown_diff_error",
                    "stages": [
                        {
                            "name": "diff",
                            "passed": False,
                            "score": -0.4,
                            "error": "unknown_diff_error",
                        }
                    ],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    validation = validate_run_artifact_validator_boundary_consistency(run_dir)

    assert validation.ok is True
    assert validation.checked_attempts == 1
    assert validation.issues == []


def test_run_artifact_validator_boundary_consistency_skips_llm_mutation_failures(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    boundary = _validator_boundary_metadata("host")
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "runtime": {"status": "completed"},
                "policies": {"validator_execution": _validator_execution_policy("host")},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "history.jsonl").write_text(
        json.dumps({"evaluation": {"metadata": {"validator_boundary": boundary}}}) + "\n",
        encoding="utf-8",
    )
    (run_dir / "failure_history.jsonl").write_text(
        json.dumps(
            {
                "error": "llm_mutation_failed",
                "diff_error": "llm_mutation_failed",
                "evaluation": {
                    "error": "llm_mutation_failed",
                    "stages": [],
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    validation = validate_run_artifact_validator_boundary_consistency(run_dir)

    assert validation.ok is True
    assert validation.checked_attempts == 1
    assert validation.issues == []


def test_run_artifact_validator_boundary_consistency_rejects_mismatched_failure_row(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "runtime": {"status": "completed"},
                "policies": {"validator_execution": _validator_execution_policy("deny")},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "history.jsonl").write_text(
        json.dumps(
            {
                "evaluation": {
                    "metadata": {"validator_boundary": _validator_boundary_metadata("deny")}
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (run_dir / "failure_history.jsonl").write_text(
        json.dumps(
            {
                "evaluation": {
                    "metadata": {"validator_boundary": _validator_boundary_metadata("host")}
                }
            }
        )
        + "\n",
        encoding="utf-8",
    )

    validation = validate_run_artifact_validator_boundary_consistency(run_dir)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.checked_attempts == 2
    assert "boundary_network_policy_mismatch" in codes
    assert any(
        issue.stream == "failure_history.jsonl" and issue.line_number == 1
        for issue in validation.issues
    )


def test_run_artifact_validator_boundary_consistency_rejects_manifest_backed_legacy_rows(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()
    (run_dir / "manifest.json").write_text(
        json.dumps(
            {
                "runtime": {"status": "completed"},
                "policies": {"validator_execution": _validator_execution_policy("host")},
            }
        ),
        encoding="utf-8",
    )
    (run_dir / "history.jsonl").write_text(json.dumps({"fitness": 1.0}) + "\n", encoding="utf-8")

    validation = validate_run_artifact_validator_boundary_consistency(run_dir)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_evaluation" in codes
    assert "missing_evaluation_attempts" in codes


def test_run_artifact_validator_boundary_consistency_skips_history_only_legacy_runs(tmp_path):
    run_dir = tmp_path / "run"
    run_dir.mkdir()

    validation = validate_run_artifact_validator_boundary_consistency(run_dir)

    assert validation.ok is False
    assert validation.manifest_policy_present is False
    assert validation.issues[0].code == "invalid_manifest_json"
