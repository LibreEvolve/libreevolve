import json

from libreevolve.llm.budget_report import (
    LLM_BUDGET_REPORT_SCHEMA,
    render_llm_budget_summary,
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
        "run_id": "run_2026_06_04",
        "paper_budget_ready": True,
        "role_budgets": [_role_budget("mutation"), _role_budget("critique"), _role_budget("feedback")],
        "role_usage": [_role_usage("mutation"), _role_usage("critique"), _role_usage("feedback")],
        "resume_state": {
            "persisted": True,
            "restored": False,
            "state_sha256": "a" * 64,
        },
    }


def test_llm_budget_report_validates_paper_budget_ready_record():
    validation = validate_llm_budget_report(_valid_report())

    assert validation.ok is True
    assert validation.paper_budget_ready is True
    assert validation.run_id == "run_2026_06_04"
    assert validation.role_count == 3
    assert validation.issues == []


def test_llm_budget_report_loads_json_file(tmp_path):
    path = tmp_path / "llm_budget.json"
    path.write_text(json.dumps(_valid_report()), encoding="utf-8")

    validation = validate_llm_budget_report(path)

    assert validation.ok is True
    assert validation.paper_budget_ready is True


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
