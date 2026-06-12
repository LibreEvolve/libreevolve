from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXPENSIVE_EVALUATION_BUDGET_BOUNDARY_SCHEMA = (
    "libreevolve.expensive_evaluation_budget_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.4", "2.6", "4")
EXPECTED_BOUNDARY_STATUS = "local_cooperative_budgets_without_compute_hour_runtime"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "max_generation_limit",
    "max_evaluations_limit",
    "max_evaluator_seconds_limit",
    "max_runtime_seconds_limit",
    "logical_llm_call_limit",
    "provider_attempt_limit",
    "provider_token_limit",
    "configured_provider_cost_limit",
    "retained_llm_latency_limit",
    "stage_sample_retry_timeout_counters",
    "stage_sample_and_stage_wall_clock_limits",
    "runtime_budget_snapshots",
    "controller_budget_event_replay",
    "llm_budget_report",
    "full_runtime_restore_budget_preapply",
    "per_candidate_compute_hour_accounting",
    "worker_or_accelerator_lease_accounting",
    "async_queue_budget_accounting",
    "queued_running_completed_long_evaluation_state",
    "partial_expensive_evaluation_checkpoint_resume",
    "wall_clock_vs_compute_hour_compression",
    "equal_budget_benchmark_execution_report",
)
EXPECTED_MISSING_EVIDENCE = {
    "per_candidate_compute_hour_accounting": "not_recorded_locally",
    "worker_or_accelerator_lease_accounting": "not_recorded_locally",
    "async_queue_budget_accounting": "not_recorded_locally",
    "queued_running_completed_long_evaluation_state": "not_recorded_locally",
    "partial_expensive_evaluation_checkpoint_resume": "not_recorded_locally",
    "wall_clock_vs_compute_hour_compression": "not_recorded_locally",
    "equal_budget_benchmark_execution_report": "not_recorded_locally",
}


@dataclass(frozen=True)
class ExpensiveEvaluationBudgetBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ExpensiveEvaluationBudgetBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ExpensiveEvaluationBudgetBoundaryIssue]


def expensive_evaluation_budget_boundary_record() -> dict[str, Any]:
    """Return the local budget counters versus compute-hour runtime boundary."""

    return {
        "schema": EXPENSIVE_EVALUATION_BUDGET_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve can spend long parallelized evaluation budgets, "
            "including roughly hundred-compute-hour solutions, while tracking "
            "overall compute budget and ablation performance by budget fraction"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_budget_schema": "libreevolve.run_budget.v1",
        "controller_budget_event_schema": "libreevolve.controller_budget_event.v1",
        "llm_budget_report_schema": "libreevolve.llm_budget_report.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has local cooperative "
            "budget controls for generations, evaluations, evaluator seconds, "
            "wall-clock runtime, logical LLM calls, provider attempts, provider "
            "tokens, configured provider cost, retained LLM latency, staged "
            "sample/retry/timeout counters, stage/sample wall-clock limits, "
            "runtime budget snapshots, controller budget-event replay, LLM "
            "budget reports, and full-runtime restore budget pre-application. "
            "It does not claim per-candidate compute-hour accounting, worker "
            "or accelerator lease accounting, async queue budget accounting, "
            "queued/running/completed long-evaluation state, partial expensive "
            "evaluation checkpoint/resume, wall-clock versus compute-hour "
            "compression, or equal-budget benchmark execution reports."
        ),
    }


def validate_expensive_evaluation_budget_boundary(
    boundary: object | str | Path | None = None,
) -> ExpensiveEvaluationBudgetBoundaryValidation:
    data, read_issues = _load_boundary(
        expensive_evaluation_budget_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return ExpensiveEvaluationBudgetBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ExpensiveEvaluationBudgetBoundaryIssue] = []
    if data.get("schema") != EXPENSIVE_EVALUATION_BUDGET_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported expensive-evaluation budget boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.4, 2.6, and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "compute-hour" not in source_claim
        or "budget fraction" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify compute-hour and budget-fraction evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    _validate_schema_field(data, "runtime_budget_schema", "libreevolve.run_budget.v1", issues)
    _validate_schema_field(data, "controller_budget_event_schema", "libreevolve.controller_budget_event.v1", issues)
    _validate_schema_field(data, "llm_budget_report_schema", "libreevolve.llm_budget_report.v1", issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "expensive-evaluation budget boundary must not claim compute-hour runtime readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim per-candidate compute-hour accounting" not in boundary_text
        or "worker or accelerator lease accounting" not in boundary_text
        or "equal-budget benchmark execution reports" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate local cooperative budgets from compute-hour runtime evidence"))
    return ExpensiveEvaluationBudgetBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_expensive_evaluation_budget_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_expensive_evaluation_budget_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Expensive evaluation budget boundary",
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
) -> tuple[dict[str, Any] | None, list[ExpensiveEvaluationBudgetBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "expensive-evaluation budget boundary must be a JSON object")]


def _validate_schema_field(
    data: dict[str, Any],
    field: str,
    expected: str,
    issues: list[ExpensiveEvaluationBudgetBoundaryIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(_issue(f"invalid_{field}", f"{field} must be {expected}"))


def _validate_required_fields(
    value: object,
    issues: list[ExpensiveEvaluationBudgetBoundaryIssue],
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
    issues: list[ExpensiveEvaluationBudgetBoundaryIssue],
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


def _issue(code: str, message: str) -> ExpensiveEvaluationBudgetBoundaryIssue:
    return ExpensiveEvaluationBudgetBoundaryIssue(code, message)
