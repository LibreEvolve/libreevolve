from __future__ import annotations

import json
import hashlib
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .provider_retry import MAX_PROVIDER_MAX_RETRIES
from .prompt_roles import validate_prompt_role_label


LLM_BUDGET_REPORT_SCHEMA = "libreevolve.llm_budget_report.v1"
LLM_BUDGET_REPORT_STATUS = "cooperative_enforcement_snapshot"
LLM_BUDGET_REPORT_POLICY = "runtime_cooperative_budget_enforcement_v1"
LLM_BUDGET_RESUME_ARTIFACT_INVENTORY_SCHEMA = (
    "libreevolve.llm_budget_resume_artifact_inventory.v1"
)
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


@dataclass(frozen=True)
class LLMBudgetEvidenceBundleValidation:
    ok: bool
    run_id: str | None
    report_ok: bool
    inventory_ok: bool
    paper_budget_ready: bool
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
    if data.get("status") != LLM_BUDGET_REPORT_STATUS:
        issues.append(LLMBudgetIssue("invalid_status", "unsupported LLM budget report status"))
    if data.get("policy") != LLM_BUDGET_REPORT_POLICY:
        issues.append(LLMBudgetIssue("invalid_policy", "unsupported LLM budget report policy"))
    run_id = _id_field(data, "run_id", issues)
    _validate_role_scheduler_scope(data.get("role_scheduler_scope"), issues)
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


def validate_llm_budget_evidence_bundle(
    report: object | str | Path,
    inventory: object,
) -> LLMBudgetEvidenceBundleValidation:
    """Validate an LLM budget report together with its resume artifact inventory."""
    data, read_issues = _load_report(report)
    if read_issues:
        return LLMBudgetEvidenceBundleValidation(
            ok=False,
            run_id=None,
            report_ok=False,
            inventory_ok=False,
            paper_budget_ready=False,
            issues=read_issues,
        )
    assert isinstance(data, dict)
    issues: list[LLMBudgetIssue] = []
    report_validation = validate_llm_budget_report(data)
    issues.extend(report_validation.issues)
    inventory_ok = _validate_llm_budget_inventory(
        inventory,
        data,
        report_validation.run_id,
        issues,
    )
    return LLMBudgetEvidenceBundleValidation(
        ok=not issues,
        run_id=report_validation.run_id,
        report_ok=report_validation.ok,
        inventory_ok=inventory_ok,
        paper_budget_ready=report_validation.paper_budget_ready and inventory_ok and not issues,
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
        f"| role_scheduler_scope | {report.get('role_scheduler_scope', '<missing>')} |",
        f"| role_count | {validation.role_count} |",
        f"| usage_count | {len(report.get('role_usage', [])) if isinstance(report.get('role_usage'), list) else 0} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def llm_budget_resume_artifact_inventory(
    report: object | str | Path,
    artifact_root: str | Path,
) -> dict[str, Any]:
    """Verify LLM budget resume-state artifact references under a root."""
    data, read_issues = _load_report(report)
    root = Path(artifact_root)
    records: list[dict[str, Any]] = []
    issues = [
        {"code": issue.code, "message": issue.message}
        for issue in read_issues
    ]
    resume_state = data.get("resume_state") if isinstance(data, dict) else None
    if isinstance(resume_state, dict):
        artifacts = resume_state.get("artifacts")
        if isinstance(artifacts, list):
            records = [
                _llm_budget_resume_artifact_inventory_record(artifact, root)
                for artifact in artifacts
            ]
        else:
            issues.append(
                {
                    "code": "invalid_resume_artifacts",
                    "message": "resume_state.artifacts must be a non-empty list",
                }
            )
    elif data is not None:
        issues.append(
            {
                "code": "invalid_resume_state",
                "message": "resume_state must be an object",
            }
        )
    verified_count = sum(1 for record in records if record["status"] == "verified")
    missing_count = sum(1 for record in records if record["status"] == "missing_file")
    mismatch_count = sum(
        1
        for record in records
        if record["status"] in {"hash_mismatch", "bytes_mismatch"}
    )
    invalid_count = sum(
        1
        for record in records
        if record["status"] in {"invalid_artifact", "unsafe_path", "read_error"}
    )
    if not records and data is not None and not issues:
        issues.append(
            {
                "code": "empty_resume_artifact_inventory",
                "message": "no LLM budget resume artifact records were available to verify",
            }
        )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return {
        "schema": LLM_BUDGET_RESUME_ARTIFACT_INVENTORY_SCHEMA,
        "report_schema": data.get("schema") if isinstance(data, dict) else None,
        "run_id": data.get("run_id") if isinstance(data, dict) else None,
        "resume_state_sha256": (
            resume_state.get("state_sha256") if isinstance(resume_state, dict) else None
        ),
        "artifact_root_policy": "safe_relative_resume_artifact_paths_under_artifact_root",
        "artifact_root_name": root.name,
        "artifact_count": len(records),
        "verified_count": verified_count,
        "missing_count": missing_count,
        "mismatch_count": mismatch_count,
        "invalid_count": invalid_count,
        "records_sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest(),
        "ok": (
            not issues
            and bool(records)
            and verified_count == len(records)
            and missing_count == 0
            and mismatch_count == 0
            and invalid_count == 0
        ),
        "issues": issues,
        "artifacts": records,
    }


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


def _validate_llm_budget_inventory(
    inventory: object,
    report: dict[str, Any],
    run_id: str | None,
    issues: list[LLMBudgetIssue],
) -> bool:
    if not isinstance(inventory, dict):
        issues.append(LLMBudgetIssue("invalid_inventory", "inventory must be an object"))
        return False
    issue_count = len(issues)
    if inventory.get("schema") != LLM_BUDGET_RESUME_ARTIFACT_INVENTORY_SCHEMA:
        issues.append(LLMBudgetIssue("invalid_inventory_schema", "unsupported LLM budget inventory schema"))
    if inventory.get("ok") is not True:
        issues.append(LLMBudgetIssue("inventory_not_ok", "LLM budget inventory must verify every resume artifact"))
    if inventory.get("report_schema") != report.get("schema"):
        issues.append(LLMBudgetIssue("inventory_report_schema_mismatch", "inventory report_schema must match LLM budget report"))
    if run_id is not None and inventory.get("run_id") != run_id:
        issues.append(LLMBudgetIssue("inventory_run_id_mismatch", "inventory run_id must match LLM budget report"))
    resume_state = report.get("resume_state")
    expected_resume_hash = (
        resume_state.get("state_sha256")
        if isinstance(resume_state, dict)
        else None
    )
    if isinstance(expected_resume_hash, str) and inventory.get("resume_state_sha256") != expected_resume_hash:
        issues.append(
            LLMBudgetIssue(
                "inventory_resume_state_hash_mismatch",
                "inventory resume_state_sha256 must match LLM budget report",
            )
        )
    records = inventory.get("artifacts")
    if not isinstance(records, list) or not records:
        issues.append(LLMBudgetIssue("invalid_inventory_artifacts", "inventory artifacts must be a non-empty list"))
        records = []
    records_payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    records_sha = inventory.get("records_sha256")
    if not isinstance(records_sha, str) or _SHA256_RE.fullmatch(records_sha) is None:
        issues.append(
            LLMBudgetIssue(
                "invalid_inventory_records_hash",
                "inventory records_sha256 must be a lowercase SHA-256 hex digest",
            )
        )
    elif hashlib.sha256(records_payload.encode("utf-8")).hexdigest() != records_sha:
        issues.append(
            LLMBudgetIssue(
                "inventory_records_hash_mismatch",
                "inventory records_sha256 must match inventory artifacts",
            )
        )
    expected_counts = {
        "artifact_count": len(records),
        "verified_count": sum(
            1
            for record in records
            if isinstance(record, dict) and record.get("status") == "verified"
        ),
        "missing_count": sum(
            1
            for record in records
            if isinstance(record, dict) and record.get("status") == "missing_file"
        ),
        "mismatch_count": sum(
            1
            for record in records
            if isinstance(record, dict)
            and record.get("status") in {"hash_mismatch", "bytes_mismatch"}
        ),
        "invalid_count": sum(
            1
            for record in records
            if isinstance(record, dict)
            and record.get("status")
            in {"invalid_artifact", "unsafe_path", "read_error"}
        ),
    }
    for field, expected in expected_counts.items():
        value = inventory.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append(
                LLMBudgetIssue(
                    f"invalid_inventory_{field}",
                    f"inventory {field} must be a non-negative integer",
                )
            )
        elif value != expected:
            issues.append(
                LLMBudgetIssue(
                    f"inventory_{field}_mismatch",
                    f"inventory {field} must match inventory artifacts",
                )
            )
    if inventory.get("verified_count") != inventory.get("artifact_count"):
        issues.append(
            LLMBudgetIssue(
                "inventory_verified_count_mismatch",
                "inventory verified_count must equal artifact_count",
            )
        )
    for field in ("missing_count", "mismatch_count", "invalid_count"):
        if inventory.get(field) != 0:
            issues.append(
                LLMBudgetIssue(
                    f"inventory_{field}_nonzero",
                    f"inventory {field} must be zero for LLM budget evidence",
                )
            )
    if inventory.get("issues"):
        issues.append(LLMBudgetIssue("inventory_has_issues", "inventory issues must be empty"))
    return len(issues) == issue_count


def _llm_budget_resume_artifact_inventory_record(
    artifact: object,
    root: Path,
) -> dict[str, Any]:
    if not isinstance(artifact, dict):
        return {
            "kind": "unknown",
            "path": "",
            "status": "invalid_artifact",
            "issues": ["invalid_artifact"],
        }
    kind = artifact.get("kind")
    path = artifact.get("path")
    expected_sha = artifact.get("sha256")
    expected_bytes = artifact.get("bytes")
    record: dict[str, Any] = {
        "kind": kind if isinstance(kind, str) else "unknown",
        "path": path if isinstance(path, str) else "",
        "expected_sha256": expected_sha if isinstance(expected_sha, str) else "",
        "expected_bytes": (
            expected_bytes
            if isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool)
            else None
        ),
        "status": "verified",
        "issues": [],
    }
    path_obj = Path(path) if isinstance(path, str) else None
    if (
        path_obj is None
        or not path
        or path_obj.is_absolute()
        or path.startswith(("/", "\\"))
        or ".." in path_obj.parts
    ):
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_resume_artifact_path")
        return record
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / path_obj).resolve(strict=False)
    except OSError:
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_resume_artifact_path")
        return record
    if not resolved_path.is_relative_to(resolved_root):
        record["status"] = "unsafe_path"
        record["issues"].append("resume_artifact_path_outside_root")
        return record
    if not resolved_path.exists():
        record["status"] = "missing_file"
        record["issues"].append("missing_resume_artifact_file")
        return record
    if not resolved_path.is_file() or resolved_path.is_symlink():
        record["status"] = "unsafe_path"
        record["issues"].append("resume_artifact_path_not_regular_file")
        return record
    try:
        raw = resolved_path.read_bytes()
    except OSError:
        record["status"] = "read_error"
        record["issues"].append("resume_artifact_read_error")
        return record
    actual_sha = hashlib.sha256(raw).hexdigest()
    record["actual_sha256"] = actual_sha
    record["actual_bytes"] = len(raw)
    if not isinstance(expected_sha, str) or _SHA256_RE.fullmatch(expected_sha) is None:
        record["status"] = "hash_mismatch"
        record["issues"].append("invalid_expected_resume_artifact_hash")
    elif actual_sha != expected_sha:
        record["status"] = "hash_mismatch"
        record["issues"].append("resume_artifact_hash_mismatch")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("invalid_expected_resume_artifact_bytes")
    elif len(raw) != expected_bytes:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("resume_artifact_bytes_mismatch")
    return record


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


def _validate_role_scheduler_scope(value: object, issues: list[LLMBudgetIssue]) -> None:
    if value not in {"shared", "role_scoped"}:
        issues.append(
            LLMBudgetIssue(
                "invalid_role_scheduler_scope",
                "role_scheduler_scope must be 'shared' or 'role_scoped'",
            )
        )


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
