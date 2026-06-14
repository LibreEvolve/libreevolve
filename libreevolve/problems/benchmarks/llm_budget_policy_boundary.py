from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LLM_BUDGET_POLICY_BOUNDARY_SCHEMA = "libreevolve.llm_budget_policy_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.2", "2.4", "2.6", "4")
EXPECTED_BOUNDARY_STATUS = (
    "cooperative_llm_budget_snapshots_without_async_pending_work_accounting"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "llm_budget_report_schema",
    "runtime_cooperative_budget_policy",
    "role_scheduler_scope_metadata",
    "logical_call_usage",
    "retry_attempt_usage",
    "adapter_attempt_usage",
    "provider_token_usage",
    "configured_cost_usage",
    "retained_latency_usage",
    "controller_budget_event_replay",
    "full_runtime_restore_budget_preapply",
    "resume_artifact_inventory",
    "async_role_work_queue_budget_accounting",
    "queued_running_pending_work_budget_state",
    "hard_provider_cancellation_budget_state",
    "provider_output_replay_for_budget_resume",
    "accelerator_worker_lease_budget_accounting",
    "experiment_owned_quota_policy",
)
EXPECTED_MISSING_EVIDENCE = {
    "async_role_work_queue_budget_accounting": "not_recorded_locally",
    "queued_running_pending_work_budget_state": "not_recorded_locally",
    "hard_provider_cancellation_budget_state": "not_recorded_locally",
    "provider_output_replay_for_budget_resume": "not_recorded_locally",
    "accelerator_worker_lease_budget_accounting": "not_recorded_locally",
    "experiment_owned_quota_policy": "not_recorded_locally",
}


@dataclass(frozen=True)
class LlmBudgetPolicyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class LlmBudgetPolicyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[LlmBudgetPolicyBoundaryIssue]


def llm_budget_policy_boundary_record() -> dict[str, Any]:
    """Return the LLM budget policy evidence boundary."""

    return {
        "schema": LLM_BUDGET_POLICY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve tracks model-call budgets, evaluation budgets, and "
            "fixed-budget ablations while operating an asynchronous search "
            "pipeline, so role-level LLM budget evidence must stay separate "
            "from queued or pending async work that has not been implemented."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "llm_budget_report_schema": "libreevolve.llm_budget_report.v1",
        "llm_budget_resume_inventory_schema": (
            "libreevolve.llm_budget_resume_artifact_inventory.v1"
        ),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has cooperative "
            "llm_budget_report snapshots, runtime cooperative budget policy, "
            "role scheduler scope metadata, logical-call usage, retry-attempt "
            "usage, adapter-attempt usage, provider-token usage, configured "
            "cost usage, retained latency usage, controller budget-event "
            "replay, full-runtime restore budget pre-application, and resume "
            "artifact inventory checks. It does not claim async role work "
            "queue budget accounting, queued/running/pending-work budget "
            "state, hard provider cancellation budget state, provider-output "
            "replay for budget resume, accelerator or worker lease budget "
            "accounting, or experiment-owned quota policy."
        ),
    }


def validate_llm_budget_policy_boundary(
    boundary: object | str | Path | None = None,
) -> LlmBudgetPolicyBoundaryValidation:
    data, read_issues = _load_boundary(
        llm_budget_policy_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return LlmBudgetPolicyBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[LlmBudgetPolicyBoundaryIssue] = []
    if data.get("schema") != LLM_BUDGET_POLICY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported LLM budget policy boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.2, 2.4, 2.6, and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "model-call budgets" not in source_claim
        or "asynchronous search pipeline" not in source_claim
        or "queued or pending async work" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify model-call budgets and pending async work"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("llm_budget_report_schema") != "libreevolve.llm_budget_report.v1":
        issues.append(_issue("invalid_llm_budget_report_schema", "llm budget report schema must be linked"))
    if (
        data.get("llm_budget_resume_inventory_schema")
        != "libreevolve.llm_budget_resume_artifact_inventory.v1"
    ):
        issues.append(_issue("invalid_llm_budget_resume_inventory_schema", "LLM budget resume inventory schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "LLM budget policy boundary must not claim async budget readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim async role work queue budget accounting" not in boundary_text
        or "queued/running/pending-work budget state" not in boundary_text
        or "provider-output replay for budget resume" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate cooperative LLM budget snapshots from async pending-work accounting"))
    return LlmBudgetPolicyBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_llm_budget_policy_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_llm_budget_policy_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "LLM budget policy boundary",
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
) -> tuple[dict[str, Any] | None, list[LlmBudgetPolicyBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "LLM budget policy boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[LlmBudgetPolicyBoundaryIssue],
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
    issues: list[LlmBudgetPolicyBoundaryIssue],
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


def _issue(code: str, message: str) -> LlmBudgetPolicyBoundaryIssue:
    return LlmBudgetPolicyBoundaryIssue(code, message)
