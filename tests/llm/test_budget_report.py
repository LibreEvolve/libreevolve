import json
import hashlib

from libreevolve.llm.budget_report import (
    LLM_BUDGET_RESUME_ARTIFACT_INVENTORY_SCHEMA,
    LLM_BUDGET_REPORT_POLICY,
    LLM_BUDGET_REPORT_SCHEMA,
    LLM_BUDGET_REPORT_STATUS,
    llm_budget_resume_artifact_inventory,
    render_llm_budget_summary,
    validate_llm_budget_evidence_bundle,
    validate_llm_budget_report,
)


def _role_budget(role: str) -> dict:
    return {
        "role": role,
        "logical_call_limit": 10,
        "retry_attempt_limit": 4,
        "adapter_attempt_limit": 12,
        "token_limit": 1000,
        "cost_limit_usd": 2.5,
        "wall_clock_limit_seconds": 60.0,
    }


def _role_usage(role: str) -> dict:
    return {
        "role": role,
        "logical_calls": 3,
        "retry_attempts": 1,
        "adapter_attempt_count": 4,
        "total_tokens": 300,
        "cost_usd": 0.25,
        "wall_clock_seconds": 12.0,
        "adapter_attempts": [
            {
                "backend": f"{role}_backend",
                "provider_max_retries": 2,
                "attempts": 2,
            }
        ],
    }


def _valid_report() -> dict:
    return {
        "schema": LLM_BUDGET_REPORT_SCHEMA,
        "status": LLM_BUDGET_REPORT_STATUS,
        "policy": LLM_BUDGET_REPORT_POLICY,
        "run_id": "run_2026_06_04",
        "paper_budget_ready": True,
        "role_scheduler_scope": "shared",
        "role_budgets": [_role_budget("mutation"), _role_budget("critique"), _role_budget("feedback")],
        "role_usage": [_role_usage("mutation"), _role_usage("critique"), _role_usage("feedback")],
        "resume_state": {
            "persisted": True,
            "restored": False,
            "state_sha256": "a" * 64,
        },
    }


def _write_resume_artifacts(report: dict, root) -> None:
    artifacts = []
    for kind, path in (
        ("runtime_budget_snapshot", "resume/runtime-budget.json"),
        ("controller_budget_events", "resume/controller-budget-events.jsonl"),
    ):
        raw = f"{kind} evidence".encode("utf-8")
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(raw)
        artifacts.append(
            {
                "kind": kind,
                "path": path,
                "sha256": hashlib.sha256(raw).hexdigest(),
                "bytes": len(raw),
            }
        )
    report["resume_state"]["artifacts"] = artifacts


def test_llm_budget_report_validates_paper_budget_ready_record():
    validation = validate_llm_budget_report(_valid_report())

    assert validation.ok is True
    assert validation.paper_budget_ready is True
    assert validation.run_id == "run_2026_06_04"
    assert validation.role_count == 3
    assert validation.issues == []


def test_llm_budget_report_rejects_invalid_status_and_policy():
    report = _valid_report()
    report["status"] = "audit_snapshot"
    report["policy"] = "runtime_observed_usage_not_budget_enforced"

    validation = validate_llm_budget_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_status" in codes
    assert "invalid_policy" in codes


def test_llm_budget_report_rejects_invalid_role_scheduler_scope():
    report = _valid_report()
    report["role_scheduler_scope"] = "global"

    validation = validate_llm_budget_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "invalid_role_scheduler_scope" in codes


def test_llm_budget_report_loads_json_file(tmp_path):
    path = tmp_path / "llm_budget.json"
    path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    validation = validate_llm_budget_report(path)

    assert validation.ok is True
    assert validation.paper_budget_ready is True


def test_llm_budget_resume_artifact_inventory_verifies_declared_files(tmp_path):
    report = _valid_report()
    _write_resume_artifacts(report, tmp_path)

    inventory = llm_budget_resume_artifact_inventory(report, tmp_path)

    assert inventory["schema"] == LLM_BUDGET_RESUME_ARTIFACT_INVENTORY_SCHEMA
    assert inventory["report_schema"] == LLM_BUDGET_REPORT_SCHEMA
    assert inventory["run_id"] == "run_2026_06_04"
    assert inventory["resume_state_sha256"] == "a" * 64
    assert inventory["artifact_root_policy"] == (
        "safe_relative_resume_artifact_paths_under_artifact_root"
    )
    assert inventory["ok"] is True
    assert inventory["artifact_count"] == 2
    assert inventory["verified_count"] == 2
    assert inventory["missing_count"] == 0
    assert inventory["mismatch_count"] == 0
    assert inventory["invalid_count"] == 0
    assert len(inventory["records_sha256"]) == 64
    assert {record["status"] for record in inventory["artifacts"]} == {"verified"}


def test_llm_budget_evidence_bundle_validates_report_and_inventory(tmp_path):
    report = _valid_report()
    _write_resume_artifacts(report, tmp_path)
    inventory = llm_budget_resume_artifact_inventory(report, tmp_path)

    validation = validate_llm_budget_evidence_bundle(report, inventory)

    assert validation.ok is True
    assert validation.run_id == "run_2026_06_04"
    assert validation.report_ok is True
    assert validation.inventory_ok is True
    assert validation.paper_budget_ready is True
    assert validation.issues == []


def test_llm_budget_evidence_bundle_rejects_tampered_inventory(tmp_path):
    report = _valid_report()
    _write_resume_artifacts(report, tmp_path)
    inventory = llm_budget_resume_artifact_inventory(report, tmp_path)
    inventory["run_id"] = "other_run"
    inventory["ok"] = False
    inventory["missing_count"] = 1

    validation = validate_llm_budget_evidence_bundle(report, inventory)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.report_ok is True
    assert validation.inventory_ok is False
    assert validation.paper_budget_ready is False
    assert "inventory_not_ok" in codes
    assert "inventory_run_id_mismatch" in codes
    assert "inventory_missing_count_mismatch" in codes
    assert "inventory_missing_count_nonzero" in codes


def test_llm_budget_resume_artifact_inventory_reports_bad_references(tmp_path):
    report = _valid_report()
    bad_path = tmp_path / "resume" / "runtime-budget.json"
    bad_path.parent.mkdir(parents=True, exist_ok=True)
    bad_path.write_text("wrong", encoding="utf-8")
    report["resume_state"]["artifacts"] = [
        {
            "kind": "runtime_budget_snapshot",
            "path": "resume/runtime-budget.json",
            "sha256": "b" * 64,
            "bytes": 999,
        },
        {
            "kind": "controller_budget_events",
            "path": "resume/missing-events.jsonl",
            "sha256": "c" * 64,
            "bytes": 10,
        },
        {
            "kind": "provider_replay",
            "path": "../escape-provider.json",
            "sha256": "d" * 64,
            "bytes": 10,
        },
    ]

    inventory = llm_budget_resume_artifact_inventory(report, tmp_path)
    records = {artifact["kind"]: artifact for artifact in inventory["artifacts"]}

    assert inventory["ok"] is False
    assert inventory["mismatch_count"] == 1
    assert inventory["missing_count"] == 1
    assert inventory["invalid_count"] == 1
    assert records["runtime_budget_snapshot"]["status"] == "hash_mismatch"
    assert "resume_artifact_hash_mismatch" in records["runtime_budget_snapshot"][
        "issues"
    ]
    assert "resume_artifact_bytes_mismatch" in records["runtime_budget_snapshot"][
        "issues"
    ]
    assert records["controller_budget_events"]["status"] == "missing_file"
    assert records["provider_replay"]["status"] == "unsafe_path"


def test_llm_budget_report_rejects_usage_over_limits():
    report = _valid_report()
    report["role_usage"][0]["logical_calls"] = 11
    report["role_usage"][0]["retry_attempts"] = 5
    report["role_usage"][0]["adapter_attempt_count"] = 13
    report["role_usage"][0]["total_tokens"] = 1001
    report["role_usage"][0]["cost_usd"] = 2.6
    report["role_usage"][0]["wall_clock_seconds"] = 61.0

    validation = validate_llm_budget_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "logical_calls_exceeds_limit" in codes
    assert "retry_attempts_exceeds_limit" in codes
    assert "adapter_attempt_count_exceeds_limit" in codes
    assert "total_tokens_exceeds_limit" in codes
    assert "cost_usd_exceeds_limit" in codes
    assert "wall_clock_seconds_exceeds_limit" in codes


def test_llm_budget_report_rejects_provider_attempts_over_internal_retry_limit():
    report = _valid_report()
    report["role_usage"][0]["adapter_attempts"][0]["provider_max_retries"] = 2
    report["role_usage"][0]["adapter_attempts"][0]["attempts"] = 4

    validation = validate_llm_budget_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "provider_attempts_exceed_retry_limit" in codes


def test_paper_ready_requires_core_roles_limits_and_persisted_resume_state():
    report = _valid_report()
    report["role_budgets"] = [_role_budget("mutation")]
    report["role_usage"] = [_role_usage("mutation")]
    report["role_budgets"][0].pop("token_limit")
    report["resume_state"] = {"persisted": False, "restored": False}

    validation = validate_llm_budget_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert "missing_paper_budget_role" in codes
    assert "missing_paper_usage_role" in codes
    assert "missing_paper_budget_limit" in codes
    assert "missing_persisted_retry_budget_state" in codes


def test_llm_budget_report_rejects_restored_without_persisted_resume_state():
    report = _valid_report()
    report["paper_budget_ready"] = False
    report["resume_state"] = {
        "persisted": False,
        "restored": True,
    }

    validation = validate_llm_budget_report(report)
    codes = {issue.code for issue in validation.issues}

    assert validation.ok is False
    assert validation.paper_budget_ready is False
    assert "invalid_resume_restored_without_persisted" in codes


def test_llm_budget_summary_renders_readiness():
    summary = render_llm_budget_summary(_valid_report())

    assert "LLM budget report: run_2026_06_04" in summary
    assert "| schema_status | ok |" in summary
    assert "| paper_budget_ready | yes |" in summary
    assert "| role_count | 3 |" in summary
    assert "| usage_count | 3 |" in summary
