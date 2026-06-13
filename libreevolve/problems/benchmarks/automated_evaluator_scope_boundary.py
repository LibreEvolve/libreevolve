from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


AUTOMATED_EVALUATOR_SCOPE_BOUNDARY_SCHEMA = (
    "libreevolve.automated_evaluator_scope_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("front_matter_overview", "2.1", "2.4", "Discussion")
EXPECTED_RUNTIME_REPORT_SCHEMA = "libreevolve.automated_evaluator_scope_report.v1"
EXPECTED_BOUNDARY_STATUS = (
    "machine_gradeable_scope_without_robust_environment_fixtures"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "automated_evaluator_available",
    "deterministic_candidate_validity_owner",
    "declared_metric_score_owner",
    "llm_feedback_post_evaluator_only",
    "manual_experiment_exclusion",
    "transition_to_executable_code_required",
    "runtime_evaluation_summary",
    "problem_local_evaluator_sources",
    "configured_evaluator_stages",
    "robust_evaluator_environment_fixture",
    "manual_to_code_transition_criteria",
    "llm_only_idea_feedback_stage_contract",
    "environment_scaling_evidence",
    "automatable_domain_boundary",
    "setup_effort_or_cost_model",
    "expected_high_value_discovery_scope",
)
EXPECTED_MISSING_EVIDENCE = {
    "robust_evaluator_environment_fixture": "not_recorded_locally",
    "manual_to_code_transition_criteria": "not_recorded_locally",
    "llm_only_idea_feedback_stage_contract": "not_recorded_locally",
    "environment_scaling_evidence": "not_recorded_locally",
    "automatable_domain_boundary": "not_recorded_locally",
    "setup_effort_or_cost_model": "not_recorded_locally",
    "expected_high_value_discovery_scope": "not_recorded_locally",
}


@dataclass(frozen=True)
class AutomatedEvaluatorScopeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AutomatedEvaluatorScopeBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AutomatedEvaluatorScopeBoundaryIssue]


def automated_evaluator_scope_boundary_record() -> dict[str, Any]:
    """Return the machine-gradeable scope versus robust environment boundary."""

    return {
        "schema": AUTOMATED_EVALUATOR_SCOPE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve is optimized for problems where automated evaluators "
            "can provide machine feedback; tasks requiring manual "
            "experimentation are out of scope, and LLM-only idea feedback is "
            "a possible bridge rather than the primary setting"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_report_status": "automated_evaluator_scope_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests include "
            "runtime.history.automated_evaluator_scope_report, which labels "
            "deterministic machine evaluators as the candidate-validity owner, "
            "declared evaluator metrics as the score owner, optional LLM "
            "feedback as post-evaluator feedback rather than a primary gate, "
            "manual experiments as excluded from candidate admission, and "
            "transition to executable code as required before scoring. It does "
            "not claim robust evaluator-environment fixtures, manual-to-code "
            "transition criteria, LLM-only idea-feedback stage contracts, "
            "environment-scaling evidence, automatable-domain boundaries, "
            "setup effort/cost models, or expected high-value discovery scope."
        ),
    }


def validate_automated_evaluator_scope_boundary(
    boundary: object | str | Path | None = None,
) -> AutomatedEvaluatorScopeBoundaryValidation:
    data, read_issues = _load_boundary(
        automated_evaluator_scope_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AutomatedEvaluatorScopeBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AutomatedEvaluatorScopeBoundaryIssue] = []
    if data.get("schema") != AUTOMATED_EVALUATOR_SCOPE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported automated-evaluator scope boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be front_matter_overview, 2.1, 2.4, and Discussion"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "automated evaluators" not in source_claim
        or "manual experimentation" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify automated-evaluator scope and manual-experiment exclusion"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("runtime_report_status") != "automated_evaluator_scope_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to automated-evaluator scope telemetry"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "automated-evaluator scope boundary must not claim robust environment readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim robust evaluator-environment fixtures" not in boundary_text
        or "manual-to-code transition criteria" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate machine-gradeable local scope from robust environment readiness"))
    return AutomatedEvaluatorScopeBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_automated_evaluator_scope_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_automated_evaluator_scope_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Automated evaluator scope boundary",
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
) -> tuple[dict[str, Any] | None, list[AutomatedEvaluatorScopeBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "automated-evaluator scope boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[AutomatedEvaluatorScopeBoundaryIssue],
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
    issues: list[AutomatedEvaluatorScopeBoundaryIssue],
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


def _issue(code: str, message: str) -> AutomatedEvaluatorScopeBoundaryIssue:
    return AutomatedEvaluatorScopeBoundaryIssue(code, message)
