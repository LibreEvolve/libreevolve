from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BENCHMARK_GOAL_PROMPT_SCHEMA = "libreevolve.benchmark_goal_prompt.v1"
SECRET_LIKE_PATTERN = re.compile(
    r"(?i)(sk-[A-Za-z0-9_-]{16,}|api[_-]?key\s*[=:]\s*[A-Za-z0-9_-]{12,})"
)


@dataclass(frozen=True)
class BenchmarkGoalPromptIssue:
    code: str
    message: str


@dataclass(frozen=True)
class BenchmarkGoalPromptValidation:
    ok: bool
    prompt_id: str | None
    prompt_character_count: int
    character_limit: int | None
    run_contract_path: str | None
    issues: list[BenchmarkGoalPromptIssue]


def validate_benchmark_goal_prompt(
    prompt_record: object | str | Path,
    *,
    root: str | Path = ".",
    run_contract: object | str | Path | None = None,
) -> BenchmarkGoalPromptValidation:
    """Validate a committed benchmark goal-prompt protocol artifact."""

    root_path = Path(root)
    data, read_issues = _load_mapping(prompt_record, root_path)
    if read_issues:
        return BenchmarkGoalPromptValidation(False, None, 0, None, None, read_issues)
    assert isinstance(data, dict)
    issues: list[BenchmarkGoalPromptIssue] = []
    if data.get("schema") != BENCHMARK_GOAL_PROMPT_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported benchmark goal-prompt schema"))

    prompt_id = data.get("prompt_id")
    if not _safe_id(prompt_id):
        issues.append(_issue("invalid_prompt_id", "prompt_id must be a stable safe id"))

    prompt = data.get("prompt")
    if not isinstance(prompt, str) or not prompt.strip():
        issues.append(_issue("invalid_prompt", "prompt must be non-empty text"))
        prompt_text = ""
    else:
        prompt_text = prompt
    prompt_count = len(prompt_text)
    if SECRET_LIKE_PATTERN.search(prompt_text):
        issues.append(_issue("secret_like_prompt_text", "prompt must not contain secret-like tokens"))

    character_limit = data.get("character_limit")
    if not isinstance(character_limit, int) or character_limit <= 0:
        issues.append(_issue("invalid_character_limit", "character_limit must be a positive integer"))
        limit_value: int | None = None
    else:
        limit_value = character_limit
        if prompt_count > character_limit:
            issues.append(_issue("prompt_exceeds_character_limit", "prompt exceeds character_limit"))

    if data.get("prompt_character_count") != prompt_count:
        issues.append(_issue("invalid_prompt_character_count", "prompt_character_count must equal len(prompt)"))

    for field_name in (
        "problem_id",
        "model",
        "backend_type",
        "auth_name",
        "run_contract_path",
        "run_name",
        "redaction_policy",
        "transcript_retention_policy",
        "review_status",
        "claim_boundary",
    ):
        value = data.get(field_name)
        if not isinstance(value, str) or not value.strip():
            issues.append(_issue(f"invalid_{field_name}", f"{field_name} must be non-empty text"))

    if "not evidence" not in str(data.get("claim_boundary", "")):
        issues.append(_issue("claim_boundary_overclaim", "claim_boundary must reject result-evidence overclaim"))
    if "no_secrets" not in str(data.get("redaction_policy", "")):
        issues.append(_issue("invalid_redaction_policy", "redaction_policy must include no_secrets"))

    contract_path = data.get("run_contract_path") if isinstance(data.get("run_contract_path"), str) else None
    contract = run_contract
    if contract is None and contract_path:
        resolved = root_path / contract_path
        if resolved.exists():
            contract = resolved
        else:
            issues.append(_issue("missing_run_contract_path", "run_contract_path does not exist under root"))
    if contract is not None:
        contract_data, contract_issues = _load_mapping(contract, root_path)
        issues.extend(
            _issue(f"run_contract_{issue.code}", issue.message)
            for issue in contract_issues
        )
        if isinstance(contract_data, dict):
            _validate_against_run_contract(data, contract_data, issues)

    return BenchmarkGoalPromptValidation(
        ok=not issues,
        prompt_id=prompt_id if isinstance(prompt_id, str) else None,
        prompt_character_count=prompt_count,
        character_limit=limit_value,
        run_contract_path=contract_path,
        issues=issues,
    )


def render_benchmark_goal_prompt_summary(prompt_record: dict[str, Any]) -> str:
    validation = validate_benchmark_goal_prompt(prompt_record)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Benchmark goal prompt",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| prompt_id | {validation.prompt_id or '<unknown>'} |",
        f"| prompt_character_count | {validation.prompt_character_count} |",
        f"| character_limit | {validation.character_limit or '<unknown>'} |",
        f"| run_contract_path | {validation.run_contract_path or '<unknown>'} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _validate_against_run_contract(
    data: dict[str, Any],
    contract: dict[str, Any],
    issues: list[BenchmarkGoalPromptIssue],
) -> None:
    auth_setup = contract.get("auth_setup")
    if not isinstance(auth_setup, dict):
        issues.append(_issue("invalid_run_contract_auth_setup", "run contract auth_setup must be an object"))
        auth_setup = {}
    comparisons = {
        "problem_id": contract.get("problem_id"),
        "model": auth_setup.get("model"),
        "backend_type": auth_setup.get("backend_type"),
        "auth_name": auth_setup.get("auth_name"),
    }
    for field_name, expected in comparisons.items():
        if data.get(field_name) != expected:
            issues.append(_issue(f"mismatched_{field_name}", f"{field_name} must match run contract"))
    command = contract.get("command")
    if isinstance(command, list) and "--run-name" in command:
        index = command.index("--run-name")
        expected_run_name = command[index + 1] if index + 1 < len(command) else None
        if data.get("run_name") != expected_run_name:
            issues.append(_issue("mismatched_run_name", "run_name must match run contract command"))
    elif data.get("run_name") != contract.get("expected_run_dir"):
        issues.append(_issue("missing_run_contract_run_name", "run contract must expose a run name"))
    goal_prompt_path = contract.get("goal_prompt_path")
    if not isinstance(goal_prompt_path, str) or not goal_prompt_path.endswith(
        "/benchmark_goal_prompt.json"
    ):
        issues.append(_issue("invalid_run_contract_goal_prompt_path", "goal_prompt_path must reference the prompt artifact"))
    provenance = contract.get("goal_prompt_provenance")
    if not isinstance(provenance, dict):
        issues.append(_issue("missing_run_contract_goal_prompt_provenance", "run contract must record goal_prompt_provenance"))
        return
    provenance_checks = {
        "schema": data.get("schema"),
        "prompt_id": data.get("prompt_id"),
        "path": goal_prompt_path,
        "prompt_character_count": data.get("prompt_character_count"),
    }
    for field_name, expected in provenance_checks.items():
        if provenance.get(field_name) != expected:
            issues.append(
                _issue(
                    f"mismatched_goal_prompt_provenance_{field_name}",
                    f"goal_prompt_provenance.{field_name} must match the prompt artifact",
                )
            )
    if provenance.get("status") != "required_for_cited_run_evidence_emitted_by_runtime":
        issues.append(
            _issue(
                "invalid_goal_prompt_provenance_status",
                "goal_prompt_provenance.status must preserve the runtime-emitted boundary",
            )
        )
    if provenance.get("manifest_pointer") != "runtime.benchmark_goal_prompt.prompt_id":
        issues.append(
            _issue(
                "invalid_goal_prompt_manifest_pointer",
                "goal_prompt_provenance.manifest_pointer must name the runtime prompt-id field",
            )
        )


def _load_mapping(
    value: object | str | Path,
    root_path: Path,
) -> tuple[dict[str, Any] | None, list[BenchmarkGoalPromptIssue]]:
    if isinstance(value, dict):
        return dict(value), []
    try:
        if isinstance(value, str) and value.strip().startswith("{"):
            loaded = json.loads(value)
        else:
            path = Path(value)
            if not path.is_absolute():
                path = root_path / path
            loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return None, [_issue("unreadable_record", f"record could not be loaded: {exc}")]
    if not isinstance(loaded, dict):
        return None, [_issue("invalid_shape", "record must be a JSON object")]
    return loaded, []


def _safe_id(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,127}", value) is not None


def _issue(code: str, message: str) -> BenchmarkGoalPromptIssue:
    return BenchmarkGoalPromptIssue(code, message)
