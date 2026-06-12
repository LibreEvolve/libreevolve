from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


REPEATED_SAMPLING_BASELINE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_repeated_sampling_baseline_boundary.v1"
)
REPEATED_SAMPLING_RUNTIME_REPORT_SCHEMA = "libreevolve.repeated_sampling_baseline_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "runtime_absence_boundary_only"
EXPECTED_REQUIRED_COMPARATOR_CONTROLS = (
    "same_initial_program_prompt_history",
    "fixed_model_and_backend",
    "fixed_prompt_template",
    "fixed_seed_and_candidate_count",
    "same_evaluator_configuration",
    "disabled_archive_admission_feedback",
    "disabled_parent_selection",
    "disabled_inspiration_resurfacing",
    "disabled_failure_feedback",
    "disabled_meta_prompt_updates",
    "linked_evolutionary_comparator_run",
)
EXPECTED_MISSING_EVIDENCE = {
    "controlled_repeated_sampling_runner": "not_recorded_locally",
    "fixed_prompt_model_seed_evaluator_contract": "not_recorded_locally",
    "budget_parity_validation": "not_recorded_locally",
    "target_progress_curve_linkage": "not_recorded_locally",
    "evolutionary_comparator_run_linkage": "not_recorded_locally",
    "same_initial_program_prompt_history_proof": "not_recorded_locally",
    "archive_feedback_disabled_proof": "not_recorded_locally",
}


@dataclass(frozen=True)
class RepeatedSamplingBaselineBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RepeatedSamplingBaselineBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_control_count: int
    missing_evidence_count: int
    issues: list[RepeatedSamplingBaselineBoundaryIssue]


def repeated_sampling_baseline_boundary_record() -> dict[str, Any]:
    """Return the current absence boundary for repeated-sampling comparator evidence."""

    return {
        "schema": REPEATED_SAMPLING_BASELINE_BOUNDARY_SCHEMA,
        "runtime_report_schema": REPEATED_SAMPLING_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve is framed as test-time compute that improves over "
            "repeated base-model sampling through machine feedback and "
            "evolutionary search"
        ),
        "paper_variant": "No evolution",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "repeated_sampling_baseline_absence_report_available",
        "claim_ready": False,
        "required_comparator_controls": list(EXPECTED_REQUIRED_COMPARATOR_CONTROLS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has a runtime absence "
            "report for the No evolution repeated-sampling comparator, but "
            "does not claim an executable controlled repeated-sampling runner, "
            "fixed prompt/model/seed/evaluator parity, budget parity, target "
            "progress curves, disabled evolutionary-feedback proof, or linked "
            "evolutionary comparator runs."
        ),
    }


def validate_repeated_sampling_baseline_boundary(
    boundary: object | str | Path | None = None,
) -> RepeatedSamplingBaselineBoundaryValidation:
    data, read_issues = _load_boundary(
        repeated_sampling_baseline_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return RepeatedSamplingBaselineBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[RepeatedSamplingBaselineBoundaryIssue] = []
    if data.get("schema") != REPEATED_SAMPLING_BASELINE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported repeated-sampling boundary schema"))
    if data.get("runtime_report_schema") != REPEATED_SAMPLING_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify repeated-sampling reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "repeated base-model sampling" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify repeated base-model sampling"))
    if data.get("paper_variant") != "No evolution":
        issues.append(_issue("invalid_paper_variant", "paper_variant must be No evolution"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "repeated_sampling_baseline_absence_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to the absence report"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "repeated-sampling boundary must not claim comparator readiness"))
    required_count = _validate_required_controls(data.get("required_comparator_controls"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim a controlled comparator"))
    return RepeatedSamplingBaselineBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_control_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_repeated_sampling_baseline_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_repeated_sampling_baseline_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve repeated-sampling baseline boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_control_count | {validation.required_control_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RepeatedSamplingBaselineBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "repeated-sampling boundary must be a JSON object")]


def _validate_required_controls(
    value: object,
    issues: list[RepeatedSamplingBaselineBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_comparator_controls", "required_comparator_controls must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_COMPARATOR_CONTROLS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_comparator_control", f"missing required comparator controls: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_comparator_control", f"unknown required comparator controls: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_comparator_control", "required comparator controls must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[RepeatedSamplingBaselineBoundaryIssue],
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


def _issue(code: str, message: str) -> RepeatedSamplingBaselineBoundaryIssue:
    return RepeatedSamplingBaselineBoundaryIssue(code, message)
