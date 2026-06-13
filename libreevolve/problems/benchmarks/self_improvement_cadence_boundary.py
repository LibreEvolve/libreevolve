from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SELF_IMPROVEMENT_CADENCE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_self_improvement_cadence_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("Discussion",)
EXPECTED_LOCAL_PDF_PAGE = 21
EXPECTED_BOUNDARY_STATUS = "cadence_environment_roi_not_recorded"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "self_improvement_loop_id",
    "source_optimization_identity",
    "affected_next_version_component",
    "start_end_dates_or_elapsed_months",
    "moderate_gain_calibration",
    "compounding_improvement_timeline",
    "environment_setup_cost",
    "environment_maintenance_cost",
    "robust_evaluator_environment_identity",
    "expected_discovery_value",
    "realized_discovery_value",
    "environment_expansion_decision_record",
    "gating_assumptions",
    "claim_to_artifact_certification_row",
)
EXPECTED_MISSING_EVIDENCE = {
    "self_improvement_loop_id": "not_recorded_locally",
    "source_optimization_identity": "not_recorded_locally",
    "affected_next_version_component": "not_recorded_locally",
    "start_end_dates_or_elapsed_months": "not_recorded_locally",
    "moderate_gain_calibration": "not_recorded_locally",
    "compounding_improvement_timeline": "not_recorded_locally",
    "environment_setup_cost": "not_recorded_locally",
    "environment_maintenance_cost": "not_recorded_locally",
    "robust_evaluator_environment_identity": "not_recorded_locally",
    "expected_discovery_value": "not_recorded_locally",
    "realized_discovery_value": "not_recorded_locally",
    "environment_expansion_decision_record": "not_recorded_locally",
    "gating_assumptions": "not_recorded_locally",
    "claim_to_artifact_certification_row": "not_recorded_locally",
}


@dataclass(frozen=True)
class SelfImprovementCadenceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SelfImprovementCadenceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[SelfImprovementCadenceBoundaryIssue]


def self_improvement_cadence_boundary_record() -> dict[str, Any]:
    """Return the current self-improvement cadence/environment ROI boundary."""

    return {
        "schema": SELF_IMPROVEMENT_CADENCE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "local_pdf_page": EXPECTED_LOCAL_PDF_PAGE,
        "source_claim": (
            "AlphaEvolve's Discussion says self-improvement gains can be "
            "moderate, next-version feedback loops can take months, and those "
            "improvements can make robust-evaluator environments more valuable"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve does not claim "
            "AlphaEvolve-style months-scale self-improvement loop cadence, "
            "moderate-gain calibration, compounding next-version improvement "
            "timelines, robust-evaluator environment setup or maintenance cost "
            "models, expected-versus-realized discovery value, environment "
            "expansion decisions, gating assumptions, or paper-facing "
            "certification rows for feedback-loop economics."
        ),
    }


def validate_self_improvement_cadence_boundary(
    boundary: object | str | Path | None = None,
) -> SelfImprovementCadenceBoundaryValidation:
    data, read_issues = _load_boundary(
        self_improvement_cadence_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SelfImprovementCadenceBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[SelfImprovementCadenceBoundaryIssue] = []
    if data.get("schema") != SELF_IMPROVEMENT_CADENCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported self-improvement cadence boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['Discussion']"))
    if data.get("local_pdf_page") != EXPECTED_LOCAL_PDF_PAGE:
        issues.append(_issue("invalid_local_pdf_page", "local_pdf_page must be 21"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "months" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify months-scale feedback-loop context"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "self-improvement cadence boundary must not claim readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim" not in boundary_text
        or "months-scale" not in boundary_text
        or "expected-versus-realized discovery value" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must keep cadence and environment ROI claims absent"))
    return SelfImprovementCadenceBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_self_improvement_cadence_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_self_improvement_cadence_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve self-improvement cadence boundary",
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
) -> tuple[dict[str, Any] | None, list[SelfImprovementCadenceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "self-improvement cadence boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[SelfImprovementCadenceBoundaryIssue],
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
    issues: list[SelfImprovementCadenceBoundaryIssue],
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


def _issue(code: str, message: str) -> SelfImprovementCadenceBoundaryIssue:
    return SelfImprovementCadenceBoundaryIssue(code, message)
