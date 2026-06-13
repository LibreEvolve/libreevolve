from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FEEDBACK_CALIBRATION_BOUNDARY_SCHEMA = (
    "libreevolve.feedback_calibration_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_ID = "2.4"
EXPECTED_SOURCE_SECTION_IDS = ("2.4",)
EXPECTED_BOUNDARY_STATUS = "report_contract_without_executed_calibration_fixtures"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "feedback_calibration_report_schema",
    "feedback_calibration_artifact_inventory_schema",
    "grader_declarations",
    "task_suite_declarations",
    "criterion_quality_fields",
    "safe_artifact_reference_validation",
    "summary_renderer",
    "schema_validation_tests",
    "runtime_calibration_runner",
    "executed_task_suite_results",
    "grader_ablation_results",
    "independent_feedback_quality_validation",
)
EXPECTED_MISSING_EVIDENCE = {
    "runtime_calibration_runner": "not_recorded_locally",
    "executed_task_suite_results": "not_recorded_locally",
    "grader_ablation_results": "not_recorded_locally",
    "independent_feedback_quality_validation": "not_recorded_locally",
}


@dataclass(frozen=True)
class FeedbackCalibrationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class FeedbackCalibrationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[FeedbackCalibrationBoundaryIssue]


def feedback_calibration_boundary_record() -> dict[str, Any]:
    """Return the feedback-calibration contract versus executed-fixture boundary."""

    return {
        "schema": FEEDBACK_CALIBRATION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_id": EXPECTED_SOURCE_SECTION_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve-style LLM feedback graders need calibration evidence "
            "from real reviewer or task suites before their qualitative scores "
            "can be treated as validated evaluator feedback"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "feedback_calibration_report_schema": "libreevolve.llm_feedback_calibration.v1",
        "artifact_inventory_schema": (
            "libreevolve.llm_feedback_calibration_artifact_inventory.v1"
        ),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has an LLM feedback "
            "calibration report schema, an artifact-inventory schema, grader "
            "declarations, task-suite declarations, criterion-quality fields, "
            "safe artifact-reference validation, a summary renderer, and "
            "schema validation tests. It does not claim a runtime calibration "
            "runner, executed task-suite results, grader ablation results, or "
            "independent feedback-quality validation."
        ),
    }


def validate_feedback_calibration_boundary(
    boundary: object | str | Path | None = None,
) -> FeedbackCalibrationBoundaryValidation:
    data, read_issues = _load_boundary(
        feedback_calibration_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return FeedbackCalibrationBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[FeedbackCalibrationBoundaryIssue] = []
    if data.get("schema") != FEEDBACK_CALIBRATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported feedback calibration boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_id") != EXPECTED_SOURCE_SECTION_ID:
        issues.append(_issue("invalid_source_section_id", "source_section_id must be 2.4"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.4']"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "calibration evidence" not in source_claim
        or "validated evaluator feedback" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify calibration evidence for validated feedback"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    _validate_schema_field(data, "feedback_calibration_report_schema", "libreevolve.llm_feedback_calibration.v1", issues)
    _validate_schema_field(data, "artifact_inventory_schema", "libreevolve.llm_feedback_calibration_artifact_inventory.v1", issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "feedback calibration boundary must not claim executed calibration readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a runtime calibration runner" not in boundary_text
        or "executed task-suite results" not in boundary_text
        or "independent feedback-quality validation" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate report contracts from executed calibration evidence"))
    return FeedbackCalibrationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_feedback_calibration_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_feedback_calibration_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Feedback calibration boundary",
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
) -> tuple[dict[str, Any] | None, list[FeedbackCalibrationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "feedback calibration boundary must be a JSON object")]


def _validate_schema_field(
    data: dict[str, Any],
    field: str,
    expected: str,
    issues: list[FeedbackCalibrationBoundaryIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(_issue(f"invalid_{field}", f"{field} must be {expected}"))


def _validate_required_fields(
    value: object,
    issues: list[FeedbackCalibrationBoundaryIssue],
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
    issues: list[FeedbackCalibrationBoundaryIssue],
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


def _issue(code: str, message: str) -> FeedbackCalibrationBoundaryIssue:
    return FeedbackCalibrationBoundaryIssue(code, message)
