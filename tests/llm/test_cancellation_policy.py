import hashlib
import json

import pytest

from libreevolve.llm.cancellation_policy import (
    PROVIDER_CANCELLATION_ARTIFACT_INVENTORY_SCHEMA,
    PROVIDER_CANCELLATION_POLICY_SCHEMA,
    PROVIDER_CANCELLATION_RUNTIME_READINESS_SCHEMA,
    provider_cancellation_artifact_inventory,
    render_provider_cancellation_summary,
    validate_provider_cancellation_policy,
)


def _valid_policy() -> dict:
    return {
        "schema": PROVIDER_CANCELLATION_POLICY_SCHEMA,
        "policy_id": "default_llm_timeout_policy",
        "hard_cancel_ready": True,
        "runtime_readiness": {
            "schema": PROVIDER_CANCELLATION_RUNTIME_READINESS_SCHEMA,
            "live_provider_sdk_cancellation": False,
            "timeout_driven_stop_enforcement": False,
            "cross_run_provider_quarantine_resume": False,
            "remaining_gap": [
                "live_provider_sdk_cancellation",
                "timeout_driven_stop_enforcement",
                "cross_run_provider_quarantine_resume",
            ],
        },
        "rules": [
            {
                "id": "provider_request_timeout_mutation",
                "kind": "provider_request_timeout",
                "role": "mutation",
                "budget_actions": ["retry", "fallback"],
                "artifact_required": True,
                "artifact_kinds": ["timeout_log"],
                "description": "Provider SDK request timeout can retry or fall back.",
            },
            {
                "id": "ensemble_wait_deadline_feedback",
                "kind": "ensemble_wait_deadline",
                "role": "feedback:*",
                "budget_actions": ["retry", "fallback", "quarantine"],
                "artifact_required": True,
                "artifact_kinds": ["timeout_log"],
                "description": "Local ensemble wait deadline creates structured timeout evidence.",
            },
            {
                "id": "hard_cancel_stop",
                "kind": "hard_cancel",
                "role": "*",
                "budget_actions": ["stop_run"],
                "artifact_required": True,
                "artifact_kinds": ["cancellation_record"],
                "description": "Hard cancellation stops the run and records the cancellation artifact.",
            },
        ],
        "artifacts": [
            {
                "kind": "timeout_log",
                "path": "llm/calls.jsonl",
                "sha256": "b" * 64,
                "bytes": 4096,
            },
            {
                "kind": "cancellation_record",
                "path": "llm/cancellation/default_policy.json",
                "sha256": "a" * 64,
                "bytes": 2048,
            }
        ],
    }


def test_provider_cancellation_policy_validates_hard_cancel_ready_policy():
    validation = validate_provider_cancellation_policy(_valid_policy())

    assert validation.ok is True
    assert validation.hard_cancel_ready is True
    assert validation.policy_id == "default_llm_timeout_policy"
    assert validation.rule_count == 3
    assert validation.issues == []


def test_provider_cancellation_policy_loads_json_file(tmp_path):
    path = tmp_path / "cancellation_policy.json"
    path.write_text(json.dumps(_valid_policy()), encoding="utf-8")

    validation = validate_provider_cancellation_policy(path)

    assert validation.ok is True
    assert validation.hard_cancel_ready is True


def test_provider_cancellation_artifact_inventory_verifies_declared_files(tmp_path):
    policy = _valid_policy()
    for artifact in policy["artifacts"]:
        path = tmp_path / artifact["path"]
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = f"{artifact['kind']} evidence".encode("utf-8")
        path.write_bytes(raw)
        artifact["sha256"] = hashlib.sha256(raw).hexdigest()
        artifact["bytes"] = len(raw)

    inventory = provider_cancellation_artifact_inventory(policy, tmp_path)

    assert inventory["schema"] == PROVIDER_CANCELLATION_ARTIFACT_INVENTORY_SCHEMA
    assert inventory["policy_schema"] == PROVIDER_CANCELLATION_POLICY_SCHEMA
    assert inventory["policy_id"] == "default_llm_timeout_policy"
    assert inventory["hard_cancel_ready"] is True
    assert inventory["artifact_root_policy"] == (
        "safe_relative_report_paths_under_artifact_root"
    )
    assert inventory["ok"] is True
    assert inventory["artifact_count"] == 2
    assert inventory["verified_count"] == 2
    assert inventory["missing_count"] == 0
    assert inventory["mismatch_count"] == 0
    assert inventory["invalid_count"] == 0
    assert {record["status"] for record in inventory["artifacts"]} == {
        "verified"
    }
    assert all("actual_sha256" in artifact for artifact in inventory["artifacts"])


def test_provider_cancellation_artifact_inventory_reports_missing_mismatch_and_unsafe_paths(tmp_path):
    policy = _valid_policy()
    policy["artifacts"].append(
        {
            "kind": "quarantine_record",
            "path": "../escape-quarantine.json",
            "sha256": "c" * 64,
            "bytes": 1024,
        }
    )
    first = policy["artifacts"][0]
    first_path = tmp_path / first["path"]
    first_path.parent.mkdir(parents=True, exist_ok=True)
    first_path.write_text("wrong", encoding="utf-8")
    first["sha256"] = "d" * 64
    first["bytes"] = 999
    policy["artifacts"][1]["path"] = "missing/cancellation.json"

    inventory = provider_cancellation_artifact_inventory(policy, tmp_path)
    records = {artifact["kind"]: artifact for artifact in inventory["artifacts"]}

    assert inventory["ok"] is False
    assert inventory["mismatch_count"] == 1
    assert inventory["missing_count"] == 1
    assert inventory["invalid_count"] == 1
    assert records["timeout_log"]["status"] == "hash_mismatch"
    assert "artifact_hash_mismatch" in records["timeout_log"]["issues"]
    assert "artifact_bytes_mismatch" in records["timeout_log"]["issues"]
    assert records["cancellation_record"]["status"] == "missing_file"
    assert records["quarantine_record"]["status"] == "unsafe_path"


def test_hard_cancel_ready_requires_stop_rule_with_artifact():
    policy = _valid_policy()
    policy["rules"] = policy["rules"][:-1]

    validation = validate_provider_cancellation_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.hard_cancel_ready is False
    assert "missing_hard_cancel_stop_rule" in codes


def test_hard_cancel_ready_requires_cancellation_record_artifact():
    policy = _valid_policy()
    policy["rules"][2]["artifact_kinds"] = ["timeout_log"]

    validation = validate_provider_cancellation_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.hard_cancel_ready is False
    assert "missing_hard_cancel_record_artifact" in codes


def test_artifact_required_rules_must_declare_matching_artifact_kind():
    policy = _valid_policy()
    del policy["rules"][0]["artifact_kinds"]
    policy["rules"][1]["artifact_kinds"] = ["quarantine_record"]

    validation = validate_provider_cancellation_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_rule_artifact_kinds" in codes
    assert "missing_required_artifact_kind" in codes


def test_provider_cancellation_policy_rejects_bad_rules_and_actions():
    policy = _valid_policy()
    policy["rules"][0]["kind"] = "not-a-kind"
    policy["rules"][0]["role"] = "bad role"
    policy["rules"][0]["budget_actions"] = ["retry", "not-an-action"]
    policy["rules"][0]["artifact_required"] = "yes"
    policy["rules"][0]["artifact_kinds"] = ["not-a-kind"]
    policy["rules"][0]["description"] = ""

    validation = validate_provider_cancellation_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_rule_kind" in codes
    assert "invalid_rule_role" in codes
    assert "invalid_budget_action" in codes
    assert "invalid_artifact_required" in codes
    assert "invalid_rule_artifact_kind" in codes
    assert "missing_rule_description" in codes


def test_provider_cancellation_policy_accepts_safe_role_prefix_pattern():
    policy = _valid_policy()
    policy["rules"][0]["role"] = "feedback:*"

    validation = validate_provider_cancellation_policy(policy)

    assert validation.ok is True


def test_provider_cancellation_policy_rejects_runtime_readiness_overclaims():
    policy = _valid_policy()
    policy["runtime_readiness"]["live_provider_sdk_cancellation"] = True
    policy["runtime_readiness"]["timeout_driven_stop_enforcement"] = True
    policy["runtime_readiness"]["cross_run_provider_quarantine_resume"] = True

    validation = validate_provider_cancellation_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "live_provider_sdk_cancellation_overclaim" in codes
    assert "timeout_driven_stop_enforcement_overclaim" in codes
    assert "cross_run_provider_quarantine_resume_overclaim" in codes


@pytest.mark.parametrize(
    "path",
    [
        "C:/secret.json",
        r"C:\secret.json",
        r"\\server\share\secret.json",
        "nested/../secret.json",
        r"nested\..\secret.json",
        "nul\x00artifact.json",
    ],
)
def test_provider_cancellation_policy_rejects_unsafe_artifacts(path):
    policy = _valid_policy()
    policy["artifacts"][0].update({"path": path, "sha256": "bad", "bytes": 0})

    validation = validate_provider_cancellation_policy(policy)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_artifact_path" in codes
    assert "invalid_artifact_hash" in codes
    assert "invalid_artifact_bytes" in codes


def test_provider_cancellation_artifact_inventory_rejects_in_root_symlink(tmp_path):
    target = tmp_path / "target.json"
    target.write_text("cancellation evidence", encoding="utf-8")
    link = tmp_path / "linked.json"
    try:
        link.symlink_to(target)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"symlink creation is unavailable: {exc}")

    policy = _valid_policy()
    raw = target.read_bytes()
    policy["artifacts"][0].update(
        {
            "path": "linked.json",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        }
    )

    record = provider_cancellation_artifact_inventory(policy, tmp_path)["artifacts"][0]

    assert record["status"] == "unsafe_path"
    assert record["issues"] == ["artifact_path_symlink"]


def test_provider_cancellation_artifact_inventory_rejects_nul_path_without_crashing(tmp_path):
    policy = _valid_policy()
    policy["artifacts"][0]["path"] = "nul\x00artifact.json"

    record = provider_cancellation_artifact_inventory(policy, tmp_path)["artifacts"][0]

    assert record["status"] == "unsafe_path"
    assert record["issues"] == ["invalid_artifact_path"]


def test_provider_cancellation_artifact_inventory_rejects_symlink_ancestor(tmp_path):
    actual_dir = tmp_path / "actual"
    actual_dir.mkdir()
    actual_file = actual_dir / "artifact.json"
    actual_file.write_text("cancellation evidence", encoding="utf-8")
    linked_dir = tmp_path / "linked"
    try:
        linked_dir.symlink_to(actual_dir, target_is_directory=True)
    except (OSError, NotImplementedError) as exc:
        pytest.skip(f"directory symlink creation is unavailable: {exc}")

    policy = _valid_policy()
    raw = actual_file.read_bytes()
    policy["artifacts"][0].update(
        {
            "path": "linked/artifact.json",
            "sha256": hashlib.sha256(raw).hexdigest(),
            "bytes": len(raw),
        }
    )

    record = provider_cancellation_artifact_inventory(policy, tmp_path)["artifacts"][0]

    assert record["status"] == "unsafe_path"
    assert record["issues"] == ["artifact_path_symlink"]


def test_provider_cancellation_summary_renders_readiness():
    summary = render_provider_cancellation_summary(_valid_policy())

    assert "Provider cancellation policy: default_llm_timeout_policy" in summary
    assert "| schema_status | ok |" in summary
    assert "| hard_cancel_ready | yes |" in summary
    assert "| rule_count | 3 |" in summary
    assert "| artifact_count | 2 |" in summary
