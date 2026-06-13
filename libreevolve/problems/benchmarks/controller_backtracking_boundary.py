from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONTROLLER_BACKTRACKING_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_controller_backtracking_boundary.v1"
)
HYPOTHESIS_BRANCH_RUNTIME_REPORT_SCHEMA = "libreevolve.hypothesis_branch_report.v1"
CONTROLLER_BACKTRACKING_RUNTIME_REPORT_SCHEMA = "libreevolve.controller_backtracking_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "observed_redirects_without_controller_policy"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "branch_id",
    "proposal_hash",
    "abandonment_reason",
    "unpromising_decision_rule",
    "unpromising_decision_threshold",
    "controller_branch_state_machine_ref",
    "configured_suppression_policy",
    "configured_retry_policy",
    "prompt_sampling_suppression_effect",
    "fallback_target_selection_event",
    "alternative_branch_selection_event",
    "resumed_search_candidate_id",
    "causal_replay_artifact",
    "cross_run_hypothesis_branch_table",
)
EXPECTED_MISSING_EVIDENCE = {
    "controller_owned_suppression_policy": "not_configured",
    "controller_owned_retry_policy": "not_configured",
    "unpromising_decision_rule": "not_recorded_locally",
    "unpromising_decision_thresholds": "not_recorded_locally",
    "controller_branch_state_machine": "not_recorded_locally",
    "prompt_sampling_suppression_effect": "not_recorded_locally",
    "fallback_target_decision_events": "not_recorded_locally",
    "alternative_branch_decision_events": "not_recorded_locally",
    "causal_resumed_search_replay": "not_recorded_locally",
    "cross_run_hypothesis_branch_table": "not_recorded_locally",
}


@dataclass(frozen=True)
class ControllerBacktrackingBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ControllerBacktrackingBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ControllerBacktrackingBoundaryIssue]


def controller_backtracking_boundary_record() -> dict[str, Any]:
    """Return the current controller-backtracking policy absence boundary."""

    return {
        "schema": CONTROLLER_BACKTRACKING_BOUNDARY_SCHEMA,
        "hypothesis_branch_report_schema": HYPOTHESIS_BRANCH_RUNTIME_REPORT_SCHEMA,
        "controller_backtracking_report_schema": CONTROLLER_BACKTRACKING_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "scientific/program discovery involves ideation, exploration, "
            "backtracking on unpromising hypotheses, experimentation, and "
            "validation; paper-ready evidence must show which controller rule "
            "classified a branch as unpromising and how that decision changed "
            "future sampling"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "hypothesis_branch_and_observed_redirect_reports_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has runtime evidence for "
            "abandoned-looking branches and observed redirects, but does not claim "
            "AlphaEvolve-style controller-owned backtracking policy evidence with "
            "unpromising-decision rules and thresholds, controller branch-state "
            "machines, configured suppression/retry behavior, prompt-sampling "
            "suppression effects, explicit fallback-target or alternative-branch "
            "selection events, causal resumed-search replay, or cross-run "
            "hypothesis branch tables."
        ),
    }


def validate_controller_backtracking_boundary(
    boundary: object | str | Path | None = None,
) -> ControllerBacktrackingBoundaryValidation:
    data, read_issues = _load_boundary(
        controller_backtracking_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ControllerBacktrackingBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ControllerBacktrackingBoundaryIssue] = []
    if data.get("schema") != CONTROLLER_BACKTRACKING_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported controller backtracking boundary schema"))
    if data.get("hypothesis_branch_report_schema") != HYPOTHESIS_BRANCH_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_hypothesis_branch_schema", "hypothesis branch schema must identify hypothesis branch reports"))
    if data.get("controller_backtracking_report_schema") != CONTROLLER_BACKTRACKING_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_controller_backtracking_schema", "controller backtracking schema must identify controller backtracking reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if (
        not isinstance(data.get("source_claim"), str)
        or "backtracking on unpromising hypotheses" not in data["source_claim"]
        or "future sampling" not in data["source_claim"]
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify backtracking on unpromising hypotheses"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "hypothesis_branch_and_observed_redirect_reports_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to observed redirect reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "controller backtracking boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim" not in boundary_text
        or "unpromising-decision rules and thresholds" not in boundary_text
        or "controller branch-state machines" not in boundary_text
        or "prompt-sampling suppression effects" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim controller-owned backtracking policy evidence"))
    return ControllerBacktrackingBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_controller_backtracking_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_controller_backtracking_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve controller backtracking boundary",
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
) -> tuple[dict[str, Any] | None, list[ControllerBacktrackingBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "controller backtracking boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ControllerBacktrackingBoundaryIssue],
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
    issues: list[ControllerBacktrackingBoundaryIssue],
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


def _issue(code: str, message: str) -> ControllerBacktrackingBoundaryIssue:
    return ControllerBacktrackingBoundaryIssue(code, message)
