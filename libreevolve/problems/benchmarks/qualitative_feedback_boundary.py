from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


QUALITATIVE_FEEDBACK_BOUNDARY_SCHEMA = (
    "libreevolve.qualitative_feedback_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_ID = "2.4"
EXPECTED_POLICY_REPORT_SCHEMA = "libreevolve.qualitative_feedback_policy_report.v1"
EXPECTED_PROMPT_AUDIT_SCHEMA = (
    "libreevolve.qualitative_feedback_prompt_history_audit_report.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "declared_qualitative_policy_without_executed_calibration"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "configured_llm_feedback_graders",
    "qualitative_criterion_metadata",
    "criterion_description",
    "evaluator_gap_rationale",
    "rubric_or_prompt_hashes",
    "score_or_discard_intent",
    "metric_linkage",
    "calibration_report_id_metadata",
    "bounded_qualitative_policy_records",
    "observed_feedback_record_counts",
    "prompt_history_feedback_joins",
    "executed_calibration_task_suite",
    "criterion_quality_ablation",
    "hard_to_code_property_fixture",
    "independent_feedback_quality_validation",
)
EXPECTED_MISSING_EVIDENCE = {
    "executed_calibration_task_suite": "not_recorded_locally",
    "criterion_quality_ablation": "not_recorded_locally",
    "hard_to_code_property_fixture": "not_recorded_locally",
    "independent_feedback_quality_validation": "not_recorded_locally",
}


@dataclass(frozen=True)
class QualitativeFeedbackBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class QualitativeFeedbackBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[QualitativeFeedbackBoundaryIssue]


def qualitative_feedback_boundary_record() -> dict[str, Any]:
    """Return the qualitative LLM-feedback provenance versus calibration boundary."""

    return {
        "schema": QUALITATIVE_FEEDBACK_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_id": EXPECTED_SOURCE_SECTION_ID,
        "source_claim": (
            "AlphaEvolve can use LLM-generated feedback to grade properties "
            "that are difficult to capture precisely in the evaluator, such "
            "as simplicity, and can use those grades as scores or discard gates"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "policy_report_schema": EXPECTED_POLICY_REPORT_SCHEMA,
        "prompt_history_audit_schema": EXPECTED_PROMPT_AUDIT_SCHEMA,
        "runtime_report_status": "qualitative_feedback_policy_reports_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can declare configured LLM "
            "feedback graders, qualitative criterion metadata, criterion "
            "descriptions, evaluator-gap rationales, rubric or prompt hashes, "
            "score-or-discard intent, metric linkage, calibration-report-id "
            "metadata, bounded qualitative policy records, observed feedback "
            "record counts, and prompt-history feedback joins. It does not "
            "claim executed calibration task suites, criterion-quality "
            "ablations, hard-to-code property fixtures, or independent "
            "feedback-quality validation."
        ),
    }


def validate_qualitative_feedback_boundary(
    boundary: object | str | Path | None = None,
) -> QualitativeFeedbackBoundaryValidation:
    data, read_issues = _load_boundary(
        qualitative_feedback_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return QualitativeFeedbackBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[QualitativeFeedbackBoundaryIssue] = []
    if data.get("schema") != QUALITATIVE_FEEDBACK_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported qualitative feedback boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_id") != EXPECTED_SOURCE_SECTION_ID:
        issues.append(_issue("invalid_source_section_id", "source_section_id must be 2.4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "difficult to capture precisely" not in source_claim
        or "discard gates" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify qualitative feedback score/discard use"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("policy_report_schema") != EXPECTED_POLICY_REPORT_SCHEMA:
        issues.append(_issue("invalid_policy_report_schema", f"policy_report_schema must be {EXPECTED_POLICY_REPORT_SCHEMA}"))
    if data.get("prompt_history_audit_schema") != EXPECTED_PROMPT_AUDIT_SCHEMA:
        issues.append(_issue("invalid_prompt_history_audit_schema", f"prompt_history_audit_schema must be {EXPECTED_PROMPT_AUDIT_SCHEMA}"))
    if data.get("runtime_report_status") != "qualitative_feedback_policy_reports_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to qualitative policy reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "qualitative feedback boundary must not claim executed calibration readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim executed calibration task suites" not in boundary_text
        or "criterion-quality ablations" not in boundary_text
        or "independent feedback-quality validation" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate declared qualitative policy from calibration evidence"))
    return QualitativeFeedbackBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_qualitative_feedback_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_qualitative_feedback_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Qualitative feedback boundary",
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
) -> tuple[dict[str, Any] | None, list[QualitativeFeedbackBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "qualitative feedback boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[QualitativeFeedbackBoundaryIssue],
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
    issues: list[QualitativeFeedbackBoundaryIssue],
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


def _issue(code: str, message: str) -> QualitativeFeedbackBoundaryIssue:
    return QualitativeFeedbackBoundaryIssue(code, message)
