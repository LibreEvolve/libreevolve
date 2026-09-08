from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any

from libreevolve.core.redaction import redact_sensitive_text

from .prompt_roles import validate_prompt_role_label


PROVIDER_CANCELLATION_POLICY_SCHEMA = "libreevolve.provider_cancellation_policy.v1"
PROVIDER_CANCELLATION_ARTIFACT_INVENTORY_SCHEMA = "libreevolve.provider_cancellation_artifact_inventory.v1"
PROVIDER_CANCELLATION_RUNTIME_READINESS_SCHEMA = "libreevolve.provider_cancellation_runtime_readiness.v1"
CANCELLATION_KINDS = frozenset({"provider_request_timeout", "ensemble_wait_deadline", "runtime_deadline", "hard_cancel"})
BUDGET_ACTIONS = frozenset({"retry", "fallback", "quarantine", "stop_run", "telemetry_only"})
ARTIFACT_KINDS = frozenset({"timeout_log", "cancellation_record", "budget_stop_record", "quarantine_record"})
RUNTIME_READINESS_FALSE_FIELDS = (
    "live_provider_sdk_cancellation",
    "timeout_driven_stop_enforcement",
    "cross_run_provider_quarantine_resume",
)
_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}")
_ROLE_PATTERN_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,125}:\*")
_SHA256_RE = re.compile(r"[0-9a-f]{64}")


@dataclass(frozen=True)
class CancellationPolicyIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CancellationPolicyValidation:
    ok: bool
    hard_cancel_ready: bool
    policy_id: str | None
    rule_count: int
    issues: list[CancellationPolicyIssue]


def validate_provider_cancellation_policy(policy: object | str | Path) -> CancellationPolicyValidation:
    """Validate provider timeout/cancellation semantics for budgeted LLM runs."""
    data, read_issues = _load_policy(policy)
    if read_issues:
        return CancellationPolicyValidation(False, False, None, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CancellationPolicyIssue] = []
    if data.get("schema") != PROVIDER_CANCELLATION_POLICY_SCHEMA:
        issues.append(CancellationPolicyIssue("invalid_schema", "unsupported cancellation policy schema"))
    policy_id = _id_field(data, "policy_id", issues)
    rules = _validate_rules(data.get("rules"), issues)
    artifact_kinds = _validate_artifacts(data.get("artifacts"), issues)
    _validate_runtime_readiness(data.get("runtime_readiness"), issues)
    _validate_rule_artifact_requirements(rules, artifact_kinds, issues)
    if data.get("hard_cancel_ready") is True and not _has_hard_cancel_stop_rule(rules):
        issues.append(CancellationPolicyIssue("missing_hard_cancel_stop_rule", "hard_cancel_ready requires a hard_cancel stop_run rule"))
    if data.get("hard_cancel_ready") is True and not _has_hard_cancel_record_rule(rules):
        issues.append(CancellationPolicyIssue("missing_hard_cancel_record_artifact", "hard_cancel_ready requires a hard_cancel stop_run rule with cancellation_record artifact evidence"))
    elif not isinstance(data.get("hard_cancel_ready"), bool):
        issues.append(CancellationPolicyIssue("invalid_hard_cancel_ready", "hard_cancel_ready must be boolean"))
    return CancellationPolicyValidation(
        ok=not issues,
        hard_cancel_ready=not issues and data.get("hard_cancel_ready") is True,
        policy_id=policy_id,
        rule_count=len(rules),
        issues=issues,
    )


def render_provider_cancellation_summary(policy: dict[str, Any]) -> str:
    validation = validate_provider_cancellation_policy(policy)
    status = "ok" if validation.ok else "invalid"
    ready = "yes" if validation.hard_cancel_ready else "no"
    lines = [
        f"Provider cancellation policy: {policy.get('policy_id', '<unknown>')}",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| hard_cancel_ready | {ready} |",
        f"| rule_count | {validation.rule_count} |",
        f"| artifact_count | {len(policy.get('artifacts', [])) if isinstance(policy.get('artifacts'), list) else 0} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def provider_cancellation_artifact_inventory(
    policy: object | str | Path,
    artifact_root: str | Path,
) -> dict[str, Any]:
    """Verify cancellation policy artifact references under a root."""
    data, read_issues = _load_policy(policy)
    root = Path(artifact_root)
    records: list[dict[str, Any]] = []
    issues = [
        {"code": issue.code, "message": issue.message}
        for issue in read_issues
    ]
    if data is not None:
        artifacts = data.get("artifacts")
        if isinstance(artifacts, list):
            for artifact in artifacts:
                records.append(_cancellation_artifact_inventory_record(artifact, root))
        else:
            issues.append(
                {
                    "code": "invalid_artifacts",
                    "message": "artifacts must be a non-empty list",
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
    if not records and data is not None:
        issues.append(
            {
                "code": "empty_artifact_inventory",
                "message": "no cancellation artifact records were available to verify",
            }
        )
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"))
    return {
        "schema": PROVIDER_CANCELLATION_ARTIFACT_INVENTORY_SCHEMA,
        "policy_schema": data.get("schema") if isinstance(data, dict) else None,
        "policy_id": data.get("policy_id") if isinstance(data, dict) else None,
        "hard_cancel_ready": data.get("hard_cancel_ready") if isinstance(data, dict) else None,
        "artifact_root_policy": "safe_relative_report_paths_under_artifact_root",
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


def _load_policy(policy: object | str | Path) -> tuple[dict[str, Any] | None, list[CancellationPolicyIssue]]:
    if isinstance(policy, dict):
        return dict(policy), []
    if isinstance(policy, (str, Path)):
        path = Path(policy)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [CancellationPolicyIssue("read_error", f"failed to read cancellation policy: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [CancellationPolicyIssue("invalid_json", f"invalid cancellation policy JSON: {exc.msg}")]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [CancellationPolicyIssue("invalid_shape", "cancellation policy must be a JSON object")]


def _cancellation_artifact_inventory_record(artifact: object, root: Path) -> dict[str, Any]:
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
        "expected_bytes": expected_bytes if isinstance(expected_bytes, int) and not isinstance(expected_bytes, bool) else None,
        "status": "verified",
        "issues": [],
    }
    path_obj = Path(path) if isinstance(path, str) else None
    if not _is_safe_relative_artifact_path(path):
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_artifact_path")
        return record
    try:
        resolved_root = root.resolve()
        resolved_path = (resolved_root / path_obj).resolve(strict=False)
    except OSError:
        record["status"] = "unsafe_path"
        record["issues"].append("invalid_artifact_path")
        return record
    if not resolved_path.is_relative_to(resolved_root):
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_outside_root")
        return record
    if _path_contains_link(resolved_root, path_obj):
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_symlink")
        return record
    if not resolved_path.exists():
        record["status"] = "missing_file"
        record["issues"].append("missing_artifact_file")
        return record
    if not resolved_path.is_file():
        record["status"] = "unsafe_path"
        record["issues"].append("artifact_path_not_file")
        return record
    try:
        raw = resolved_path.read_bytes()
    except OSError:
        record["status"] = "read_error"
        record["issues"].append("artifact_read_error")
        return record
    actual_sha = hashlib.sha256(raw).hexdigest()
    actual_bytes = len(raw)
    record["actual_sha256"] = actual_sha
    record["actual_bytes"] = actual_bytes
    if not isinstance(expected_sha, str) or _SHA256_RE.fullmatch(expected_sha) is None:
        record["status"] = "hash_mismatch"
        record["issues"].append("invalid_expected_artifact_hash")
    elif actual_sha != expected_sha:
        record["status"] = "hash_mismatch"
        record["issues"].append("artifact_hash_mismatch")
    if isinstance(expected_bytes, bool) or not isinstance(expected_bytes, int) or expected_bytes <= 0:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("invalid_expected_artifact_bytes")
    elif actual_bytes != expected_bytes:
        if record["status"] == "verified":
            record["status"] = "bytes_mismatch"
        record["issues"].append("artifact_bytes_mismatch")
    return record


def _id_field(data: dict[str, Any], field: str, issues: list[CancellationPolicyIssue]) -> str | None:
    value = data.get(field)
    if not isinstance(value, str) or _ID_RE.fullmatch(value) is None:
        issues.append(CancellationPolicyIssue(f"invalid_{field}", f"{field} must be a stable identifier"))
        return None
    return value


def _validate_rules(value: object, issues: list[CancellationPolicyIssue]) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        issues.append(CancellationPolicyIssue("invalid_rules", "rules must be a non-empty list"))
        return []
    rules: list[dict[str, Any]] = []
    seen: set[str] = set()
    for rule in value:
        if not isinstance(rule, dict):
            issues.append(CancellationPolicyIssue("invalid_rule", "rule must be an object"))
            continue
        rule_id = rule.get("id")
        if not isinstance(rule_id, str) or _ID_RE.fullmatch(rule_id) is None:
            issues.append(CancellationPolicyIssue("invalid_rule_id", "rule id must be stable"))
        elif rule_id in seen:
            issues.append(CancellationPolicyIssue("duplicate_rule_id", "rule ids must be unique"))
        else:
            seen.add(rule_id)
        if rule.get("kind") not in CANCELLATION_KINDS:
            issues.append(CancellationPolicyIssue("invalid_rule_kind", "unsupported cancellation rule kind"))
        role = rule.get("role")
        if _role_scope(role, issues) is None:
            issues.append(CancellationPolicyIssue("invalid_rule_role", "rule role must be '*', a manifest-safe role, or a manifest-safe role prefix ending in :*"))
        actions = rule.get("budget_actions")
        if not isinstance(actions, list) or not actions:
            issues.append(CancellationPolicyIssue("invalid_budget_actions", "budget_actions must be a non-empty list"))
        elif any(action not in BUDGET_ACTIONS for action in actions):
            issues.append(CancellationPolicyIssue("invalid_budget_action", "unsupported budget action"))
        if not isinstance(rule.get("artifact_required"), bool):
            issues.append(CancellationPolicyIssue("invalid_artifact_required", "artifact_required must be boolean"))
        _validate_rule_artifact_kinds(rule, issues)
        if not isinstance(rule.get("description"), str) or not rule["description"].strip():
            issues.append(CancellationPolicyIssue("missing_rule_description", "rule description is required"))
        rules.append(rule)
    return rules


def _has_hard_cancel_stop_rule(rules: list[dict[str, Any]]) -> bool:
    for rule in rules:
        actions = rule.get("budget_actions")
        if rule.get("kind") == "hard_cancel" and isinstance(actions, list) and "stop_run" in actions and rule.get("artifact_required") is True:
            return True
    return False


def _has_hard_cancel_record_rule(rules: list[dict[str, Any]]) -> bool:
    for rule in rules:
        actions = rule.get("budget_actions")
        artifact_kinds = rule.get("artifact_kinds")
        if (
            rule.get("kind") == "hard_cancel"
            and isinstance(actions, list)
            and "stop_run" in actions
            and rule.get("artifact_required") is True
            and isinstance(artifact_kinds, list)
            and "cancellation_record" in artifact_kinds
        ):
            return True
    return False


def _validate_rule_artifact_kinds(rule: dict[str, Any], issues: list[CancellationPolicyIssue]) -> None:
    value = rule.get("artifact_kinds")
    if value is None:
        if rule.get("artifact_required") is True:
            issues.append(CancellationPolicyIssue("missing_rule_artifact_kinds", "artifact_required rules must declare artifact_kinds"))
        return
    if not isinstance(value, list) or not value:
        issues.append(CancellationPolicyIssue("invalid_rule_artifact_kinds", "artifact_kinds must be a non-empty list"))
        return
    seen: set[str] = set()
    for kind in value:
        if kind not in ARTIFACT_KINDS:
            issues.append(CancellationPolicyIssue("invalid_rule_artifact_kind", "unsupported rule artifact kind"))
        elif kind in seen:
            issues.append(CancellationPolicyIssue("duplicate_rule_artifact_kind", "rule artifact_kinds must be unique"))
        else:
            seen.add(kind)


def _validate_rule_artifact_requirements(
    rules: list[dict[str, Any]],
    artifact_kinds: set[str],
    issues: list[CancellationPolicyIssue],
) -> None:
    for rule in rules:
        if rule.get("artifact_required") is not True:
            continue
        required = rule.get("artifact_kinds")
        if not isinstance(required, list):
            continue
        missing = [
            kind for kind in required
            if kind in ARTIFACT_KINDS and kind not in artifact_kinds
        ]
        if missing:
            issues.append(CancellationPolicyIssue("missing_required_artifact_kind", "artifact_required rule artifact_kinds must be present in artifacts"))


def _validate_artifacts(value: object, issues: list[CancellationPolicyIssue]) -> set[str]:
    kinds: set[str] = set()
    if not isinstance(value, list) or not value:
        issues.append(CancellationPolicyIssue("invalid_artifacts", "artifacts must be a non-empty list"))
        return kinds
    for artifact in value:
        if not isinstance(artifact, dict):
            issues.append(CancellationPolicyIssue("invalid_artifact", "artifact must be an object"))
            continue
        if artifact.get("kind") not in ARTIFACT_KINDS:
            issues.append(CancellationPolicyIssue("invalid_artifact_kind", "unsupported artifact kind"))
        else:
            kinds.add(artifact["kind"])
        _validate_file_record(artifact, "artifact", issues)
    return kinds


def _validate_runtime_readiness(
    value: object,
    issues: list[CancellationPolicyIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(
            CancellationPolicyIssue(
                "invalid_runtime_readiness",
                "runtime_readiness must be an object",
            )
        )
        return
    if value.get("schema") != PROVIDER_CANCELLATION_RUNTIME_READINESS_SCHEMA:
        issues.append(
            CancellationPolicyIssue(
                "invalid_runtime_readiness_schema",
                "runtime_readiness schema is unsupported",
            )
        )
    for field in RUNTIME_READINESS_FALSE_FIELDS:
        if value.get(field) is not False:
            issues.append(
                CancellationPolicyIssue(
                    f"{field}_overclaim",
                    f"runtime_readiness.{field} must remain false until implemented",
                )
            )
    remaining_gap = value.get("remaining_gap")
    if (
        not isinstance(remaining_gap, list)
        or not all(isinstance(item, str) and item for item in remaining_gap)
    ):
        issues.append(
            CancellationPolicyIssue(
                "invalid_runtime_readiness_remaining_gap",
                "runtime_readiness.remaining_gap must list incomplete runtime surfaces",
            )
        )


def _validate_file_record(record: dict[str, Any], prefix: str, issues: list[CancellationPolicyIssue]) -> None:
    path = record.get("path")
    if not _is_safe_relative_artifact_path(path):
        issues.append(CancellationPolicyIssue(f"invalid_{prefix}_path", f"{prefix} path must be safe and relative"))
    sha = record.get("sha256")
    if not isinstance(sha, str) or _SHA256_RE.fullmatch(sha) is None:
        issues.append(CancellationPolicyIssue(f"invalid_{prefix}_hash", f"{prefix} sha256 must be a lowercase SHA-256 hex digest"))
    byte_count = record.get("bytes")
    if isinstance(byte_count, bool) or not isinstance(byte_count, int) or byte_count <= 0:
        issues.append(CancellationPolicyIssue(f"invalid_{prefix}_bytes", f"{prefix} bytes must be a positive integer"))


def _is_safe_relative_artifact_path(path: object) -> bool:
    """Apply the artifact path grammar independently of the host OS."""
    if not isinstance(path, str) or not path:
        return False
    posix_path = PurePosixPath(path)
    windows_path = PureWindowsPath(path)
    return not (
        "\x00" in path or redact_sensitive_text(path) != path
        or posix_path.is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.root)
        or bool(windows_path.drive)
        or ".." in posix_path.parts
        or ".." in windows_path.parts
    )


def _is_link(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (is_junction is not None and is_junction())


def _path_contains_link(root: Path, relative_path: Path) -> bool:
    current = root
    for part in relative_path.parts:
        current /= part
        if _is_link(current):
            return True
    return False


def _role(value: object, issues: list[CancellationPolicyIssue]) -> str | None:
    try:
        return validate_prompt_role_label(value, field="role")
    except ValueError:
        return None


def _role_scope(value: object, issues: list[CancellationPolicyIssue]) -> str | None:
    if value == "*":
        return value
    if isinstance(value, str) and _ROLE_PATTERN_RE.fullmatch(value) is not None:
        try:
            validate_prompt_role_label(value[:-2], field="role")
        except ValueError:
            return None
        return value
    return _role(value, issues)
