from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .provider_retry import MAX_PROVIDER_MAX_RETRIES
from .prompt_roles import validate_prompt_role_label


LLM_BUDGET_REPORT_SCHEMA = "libreevolve.llm_budget_report.v1"
REQUIRED_PAPER_ROLES = frozenset({"mutation", "critique", "feedback"})
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class LLMBudgetIssue:
    code: str
    message: str


@dataclass(frozen=True)
class LLMBudgetValidation:
    ok: bool
    paper_budget_ready: bool
    run_id: str | None
    role_count: int
    issues: list[LLMBudgetIssue]


def validate_llm_budget_report(report: object | str | Path) -> LLMBudgetValidation:
    """Validate paper-facing LLM role/retry/budget accounting metadata."""
    data, read_issues = _load_report(report)
    if read_issues:
        return LLMBudgetValidation(False, False, None, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[LLMBudgetIssue] = []
    if data.get("schema") != LLM_BUDGET_REPORT_SCHEMA:
        issues.append(LLMBudgetIssue("invalid_schema", "unsupported LLM budget report schema"))
    run_id = _id_field(data, "run_id", issues)
    budgets = _validate_role_budgets(data.get("role_budgets"), issues)
    usage = _validate_role_usage(data.get("role_usage"), budgets, issues)
    _validate_resume_state(data.get("resume_state"), issues)
    _validate_paper_ready(data.get("paper_budget_ready"), budgets, usage, data.get("resume_state"), issues)
    return LLMBudgetValidation(
        ok=not issues,
        paper_budget_ready=not issues and data.get("paper_budget_ready") is True,
        run_id=run_id,
        role_count=len(budgets),
        issues=issues,
    )


def render_llm_budget_summary(report: dict[str, Any]) -> str:
    validation = validate_llm_budget_report(report)
    status = "ok" if validation.ok else "invalid"
    ready = "yes" if validation.paper_budget_ready else "no"
    lines = [
        f"LLM budget report: {report.get('run_id', '<unknown>')}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| paper_budget_ready | {ready} |",
        f"| role_count | {validation.role_count} |",
        f"| usage_count | {len(report.get('role_usage', [])) if isinstance(report.get('role_usage'), list) else 0} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_report(report: object | str | Path) -> tuple[dict[str, Any] | None, list[LLMBudgetIssue]]:
    if isinstance(report, dict):
        return dict(report), []
    if isinstance(report, (str, Path)):
        path = Path(report)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [LLMBudgetIssue("read_error", f"failed to read LLM budget report: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [LLMBudgetIssue("invalid_json", f"invalid LLM budget JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [LLMBudgetIssue("invalid_shape", "LLM budget report must be a JSON object")]


def _id_field(data: dict[str, Any], field: str, issues: list[LLMBudgetIssue]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        issues.append(LLMBudgetIssue(f"invalid_{field}", f"{field} must be a stable identifier"))
        return None
    return value


def _validate_role_budgets(value: object, issues: list[LLMBudgetIssue]) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list) or not value:
        issues.append(LLMBudgetIssue("invalid_role_budgets", "role_budgets must be a non-empty list"))
        return {}
    budgets: dict[str, dict[str, Any]] = {}
    for item in value:
        if not isinstance(item, dict):
            issues.append(LLMBudgetIssue("invalid_role_budget", "role budget must be an object"))
            continue
        role = _role(item.get("role"), "role_budget_role", issues)
        if role is None:
            continue
        if role in budgets:
            issues.append(LLMBudgetIssue("duplicate_role_budget", "role budgets must be unique"))
        budgets[role] = item
        for field in ("logical_call_limit", "retry_attempt_limit", "adapter_attempt_limit"):
            _nonnegative_int(item.get(field), f"invalid_{field}", field, issues)
        for field in ("token_limit", "cost_limit_usd", "wall_clock_limit_seconds"):
            if field in item and item[field] is not None:
                _positive_number(item[field], f"invalid_{field}", field, issues)
    return budgets


def _validate_role_usage(
    value: object,
    budgets: dict[str, dict[str, Any]],
    issues: list[LLMBudgetIssue],
) -> dict[str, dict[str, Any]]:
    if not isinstance(value, list) or not value:
        issues.append(LLMBudgetIssue("invalid_role_usage", "role_usage must be a non-empty list"))
        return {}
    usage_by_role: dict[str, dict[str, Any]] = {}
    for item in value:
        if not isinstance(item, dict):
            issues.append(LLMBudgetIssue("invalid_role_usage_record", "role usage must be an object"))
            continue
        role = _role(item.get("role"), "role_usage_role", issues)
        if role is None:
            continue
        if role not in budgets:
            issues.append(LLMBudgetIssue("usage_without_budget", "role usage must have a matching role budget"))
            continue
        if role in usage_by_role:
            issues.append(LLMBudgetIssue("duplicate_role_usage", "role usage records must be unique"))
        usage_by_role[role] = item
        _usage_limits(role, item, budgets[role], issues)
        _validate_adapter_attempts(item.get("adapter_attempts"), issues)
    return usage_by_role


def _usage_limits(role: str, usage: dict[str, Any], budget: dict[str, Any], issues: list[LLMBudgetIssue]) -> None:
    pairs = (
        ("logical_calls", "logical_call_limit"),
        ("retry_attempts", "retry_attempt_limit"),
        ("adapter_attempt_count", "adapter_attempt_limit"),
    )
    for used_field, limit_field in pairs:
        used = _nonnegative_int(usage.get(used_field), f"invalid_{used_field}", used_field, issues)
        limit = budget.get(limit_field)
        if used is not None and isinstance(limit, int) and used > limit:
            issues.append(LLMBudgetIssue(f"{used_field}_exceeds_limit", f"{role} {used_field} exceeds {limit_field}"))
    numeric_pairs = (
        ("total_tokens", "token_limit"),
        ("cost_usd", "cost_limit_usd"),
        ("wall_clock_seconds", "wall_clock_limit_seconds"),
    )
    for used_field, limit_field in numeric_pairs:
        used = _nonnegative_number(usage.get(used_field), f"invalid_{used_field}", used_field, issues)
        limit = budget.get(limit_field)
        if used is not None and isinstance(limit, (int, float)) and used > float(limit):
            issues.append(LLMBudgetIssue(f"{used_field}_exceeds_limit", f"{role} {used_field} exceeds {limit_field}"))


def _validate_adapter_attempts(value: object, issues: list[LLMBudgetIssue]) -> None:
    if not isinstance(value, list):
        issues.append(LLMBudgetIssue("invalid_adapter_attempts", "adapter_attempts must be a list"))
        return
    for attempt in value:
        if not isinstance(attempt, dict):
            issues.append(LLMBudgetIssue("invalid_adapter_attempt", "adapter attempt must be an object"))
            continue
        if not isinstance(attempt.get("backend"), str) or not attempt["backend"].strip():
            issues.append(LLMBudgetIssue("invalid_adapter_backend", "adapter attempt backend is required"))
        max_retries = _nonnegative_int(attempt.get("provider_max_retries"), "invalid_provider_max_retries", "provider_max_retries", issues)
        attempts = _nonnegative_int(attempt.get("attempts"), "invalid_provider_attempts", "attempts", issues)
        if max_retries is not None and max_retries > MAX_PROVIDER_MAX_RETRIES:
            issues.append(LLMBudgetIssue("provider_max_retries_exceeds_cap", "provider_max_retries exceeds configured cap"))
        if max_retries is not None and attempts is not None and attempts > max_retries + 1:
            issues.append(LLMBudgetIssue("provider_attempts_exceed_retry_limit", "provider attempts exceed provider_max_retries + 1"))


def _validate_resume_state(value: object, issues: list[LLMBudgetIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(LLMBudgetIssue("invalid_resume_state", "resume_state must be an object"))
        return
    for field in ("persisted", "restored"):
        if not isinstance(value.get(field), bool):
            issues.append(LLMBudgetIssue(f"invalid_resume_{field}", f"resume_state.{field} must be boolean"))
    if value.get("restored") is True and value.get("persisted") is not True:
        issues.append(LLMBudgetIssue("invalid_resume_restored_without_persisted", "resume_state.restored requires persisted retry-budget state"))
    sha = value.get("state_sha256")
    if value.get("persisted") is True and (not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None):
        issues.append(LLMBudgetIssue("invalid_resume_state_hash", "persisted resume state requires lowercase SHA-256 hash"))


def _validate_paper_ready(
    value: object,
    budgets: dict[str, dict[str, Any]],
    usage: dict[str, dict[str, Any]],
    resume_state: object,
    issues: list[LLMBudgetIssue],
) -> None:
    if not isinstance(value, bool):
        issues.append(LLMBudgetIssue("invalid_paper_budget_ready", "paper_budget_ready must be boolean"))
        return
    if value is not True:
        return
    missing_roles = REQUIRED_PAPER_ROLES - set(budgets)
    if missing_roles:
        issues.append(LLMBudgetIssue("missing_paper_budget_role", "paper-ready budgets require mutation, critique, and feedback roles"))
    missing_usage = REQUIRED_PAPER_ROLES - set(usage)
    if missing_usage:
        issues.append(LLMBudgetIssue("missing_paper_usage_role", "paper-ready usage requires mutation, critique, and feedback roles"))
    for role in REQUIRED_PAPER_ROLES & set(budgets):
        budget = budgets[role]
        for field in ("token_limit", "cost_limit_usd", "wall_clock_limit_seconds"):
            if field not in budget or budget[field] is None:
                issues.append(LLMBudgetIssue("missing_paper_budget_limit", "paper-ready role budgets require token, cost, and wall-clock limits"))
    if not isinstance(resume_state, dict) or resume_state.get("persisted") is not True:
        issues.append(LLMBudgetIssue("missing_persisted_retry_budget_state", "paper-ready budgets require persisted resume state"))


def _role(value: object, code: str, issues: list[LLMBudgetIssue]) -> str | None:
    try:
        return validate_prompt_role_label(value, field="role")
    except ValueError:
        issues.append(LLMBudgetIssue(code, "role must be a manifest-safe label"))
        return None


def _nonnegative_int(value: object, code: str, label: str, issues: list[LLMBudgetIssue]) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        issues.append(LLMBudgetIssue(code, f"{label} must be a non-negative integer"))
        return None
    return value


def _positive_number(value: object, code: str, label: str, issues: list[LLMBudgetIssue]) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or float(value) <= 0:
        issues.append(LLMBudgetIssue(code, f"{label} must be a positive finite number"))
        return None
    return float(value)


def _nonnegative_number(value: object, code: str, label: str, issues: list[LLMBudgetIssue]) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)) or float(value) < 0:
        issues.append(LLMBudgetIssue(code, f"{label} must be a non-negative finite number"))
        return None
    return float(value)
