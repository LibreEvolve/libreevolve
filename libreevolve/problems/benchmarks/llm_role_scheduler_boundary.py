from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LLM_ROLE_SCHEDULER_BOUNDARY_SCHEMA = "libreevolve.llm_role_scheduler_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.1", "2.6")
EXPECTED_BOUNDARY_STATUS = (
    "role_scoped_local_ucb_without_calibrated_experiment_policy"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "configured_role_backend_indices",
    "backend_metadata_role_matching",
    "configured_reward_accounted_roles",
    "feedback_grader_reward_wiring",
    "per_role_logical_call_limits",
    "role_provider_attempt_limits",
    "role_token_limits",
    "role_configured_cost_limits",
    "role_latency_limits",
    "scheduler_policy_telemetry",
    "reward_accounted_vs_telemetry_only_status",
    "role_selection_state_owner",
    "opt_in_role_scoped_selection",
    "role_specific_backend_pool_policy",
    "role_specific_exploration_parameters",
    "role_reward_normalization_report",
    "role_outcome_attribution_dataset",
    "async_role_work_queue_policy",
    "cross_role_interference_analysis",
    "role_scheduler_state_snapshots",
    "scheduler_state_restore_validation",
    "runtime_llm_accounting_summary",
    "llm_budget_report_role_budgets",
    "calibrated_role_reward_policy",
    "experiment_owned_quota_policy",
    "fast_strong_model_mix_report",
    "resume_replay_experiment_report",
    "role_specific_budget_behavior_report",
)
EXPECTED_MISSING_EVIDENCE = {
    "role_specific_backend_pool_policy": "not_recorded_locally",
    "role_specific_exploration_parameters": "global_ucb_coefficient_only",
    "role_reward_normalization_report": "not_recorded_locally",
    "role_outcome_attribution_dataset": "not_recorded_locally",
    "async_role_work_queue_policy": "not_recorded_locally",
    "cross_role_interference_analysis": "not_recorded_locally",
    "calibrated_role_reward_policy": "not_recorded_locally",
    "experiment_owned_quota_policy": "not_recorded_locally",
    "fast_strong_model_mix_report": "not_recorded_locally",
    "resume_replay_experiment_report": "not_recorded_locally",
    "role_specific_budget_behavior_report": "not_recorded_locally",
}


@dataclass(frozen=True)
class LLMRoleSchedulerBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class LLMRoleSchedulerBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[LLMRoleSchedulerBoundaryIssue]


def llm_role_scheduler_boundary_record() -> dict[str, Any]:
    """Return the role-scoped scheduler evidence versus experiment policy boundary."""

    return {
        "schema": LLM_ROLE_SCHEDULER_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve orchestrates multiple LLM work classes such as "
            "proposal generation, critique, feedback, and prompt improvement "
            "with separately meaningful scheduling and reward behavior"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "scheduler_state_schema": "libreevolve.llm_ensemble_scheduler_state.v1",
        "llm_budget_report_schema": "libreevolve.llm_budget_report.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has configured role-backend "
            "indices, backend metadata role matching, configured reward-accounted "
            "roles, feedback-grader reward wiring, per-role logical call limits, "
            "role provider-attempt, token, configured-cost, and latency limits, "
            "scheduler-policy telemetry, reward-accounted versus telemetry-only "
            "status, role selection state-owner telemetry, opt-in role-scoped "
            "local UCB selection, role scheduler state snapshots, scheduler-state "
            "restore validation, runtime LLM accounting summaries, and LLM budget "
            "report role budgets. It does not claim role-specific backend-pool "
            "policy, role-specific exploration parameters, role reward "
            "normalization reports, role outcome-attribution datasets, async "
            "role work queues, cross-role interference analysis, calibrated role "
            "reward policy, experiment-owned quota policy, fast/strong model-mix "
            "reports, resume replay experiment reports, or role-specific budget "
            "behavior reports."
        ),
    }


def validate_llm_role_scheduler_boundary(
    boundary: object | str | Path | None = None,
) -> LLMRoleSchedulerBoundaryValidation:
    data, read_issues = _load_boundary(
        llm_role_scheduler_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return LLMRoleSchedulerBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[LLMRoleSchedulerBoundaryIssue] = []
    if data.get("schema") != LLM_ROLE_SCHEDULER_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported LLM role scheduler boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.1 and 2.6"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "multiple LLM work classes" not in source_claim
        or "reward behavior" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify role-specific scheduling and reward behavior"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    _validate_schema_field(data, "scheduler_state_schema", "libreevolve.llm_ensemble_scheduler_state.v1", issues)
    _validate_schema_field(data, "llm_budget_report_schema", "libreevolve.llm_budget_report.v1", issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "LLM role scheduler boundary must not claim calibrated AlphaEvolve scheduler readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim role-specific backend-pool policy" not in boundary_text
        or "role-specific exploration parameters" not in boundary_text
        or "role reward normalization reports" not in boundary_text
        or "role outcome-attribution datasets" not in boundary_text
        or "async role work queues" not in boundary_text
        or "cross-role interference analysis" not in boundary_text
        or "calibrated role reward policy" not in boundary_text
        or "fast/strong model-mix reports" not in boundary_text
        or "role-specific budget behavior reports" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate local role-scoped UCB evidence from calibrated experiment policy"))
    return LLMRoleSchedulerBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_llm_role_scheduler_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_llm_role_scheduler_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "LLM role scheduler boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[LLMRoleSchedulerBoundaryIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(boundary).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "LLM role scheduler boundary must be a JSON object")]


def _validate_schema_field(
    data: dict[str, Any],
    field: str,
    expected: str,
    issues: list[LLMRoleSchedulerBoundaryIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(_issue(f"invalid_{field}", f"{field} must be {expected}"))


def _validate_required_fields(
    value: object,
    issues: list[LLMRoleSchedulerBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_evidence_field", f"missing required evidence fields: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_evidence_field", f"unknown required evidence fields: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[LLMRoleSchedulerBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> LLMRoleSchedulerBoundaryIssue:
    return LLMRoleSchedulerBoundaryIssue(code, message)
