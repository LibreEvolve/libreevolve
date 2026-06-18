from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROGRAMMATIC_REPRESENTATION_BOUNDARY_SCHEMA = (
    "libreevolve.programmatic_representation_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.programmatic_representation_boundary_report.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "executable_code_representation_with_measured_claim_gap_matrix"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "executable_code_workspace_candidate_representation",
    "natural_language_proposal_metadata_context_only",
    "declared_evaluator_metric_criteria",
    "deterministic_evaluator_validity_gate",
    "llm_feedback_post_evaluator_only",
    "hypothesis_to_code_transition_required",
    "sample_candidate_representation_records",
    "runtime_generation_count_scope",
    "representation_claim_gap_matrix",
    "hallucination_risk_measurement",
    "long_horizon_step_count_evidence",
    "natural_language_hypothesis_stage_contract",
    "natural_language_to_programmatic_bridge_status",
    "proposal_quality_or_truth_model",
    "combined_ai_coscientist_workflow_evidence",
)
EXPECTED_MISSING_EVIDENCE = {
    "hallucination_risk_measurement": "not_recorded_locally",
    "long_horizon_step_count_evidence": "not_recorded_locally",
    "natural_language_hypothesis_stage_contract": "not_recorded_locally",
    "natural_language_to_programmatic_bridge_status": "not_recorded_locally",
    "proposal_quality_or_truth_model": "not_recorded_locally",
    "combined_ai_coscientist_workflow_evidence": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProgrammaticRepresentationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProgrammaticRepresentationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ProgrammaticRepresentationBoundaryIssue]


def programmatic_representation_boundary_record() -> dict[str, Any]:
    """Return the code/programmatic-evaluation versus natural-language boundary."""

    return {
        "schema": PROGRAMMATIC_REPRESENTATION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve contrasts code candidates with programmatic "
            "evaluation functions against AI Co-Scientist-style "
            "natural-language hypotheses and natural-language evaluation "
            "criteria"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_report_status": "programmatic_representation_boundary_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests include "
            "runtime.history.programmatic_representation_boundary_report, "
            "which labels generated candidates as executable code workspaces, "
            "proposal idea/rationale/hypothesis text as natural-language "
            "context metadata rather than candidate representation, declared "
            "evaluator metrics and deterministic evaluator validity as "
            "programmatic criteria, optional LLM feedback as post-evaluator, "
            "hypothesis-to-code transition as required, and a representation "
            "claim gap matrix for structural evidence versus measured claims. "
            "It does not claim hallucination-risk measurement, long-horizon "
            "step-count evidence, a natural-language hypothesis-stage contract, a "
            "natural-language-to-programmatic bridge, proposal-quality truth "
            "models, or combined AI-Co-Scientist workflow evidence."
        ),
    }


def validate_programmatic_representation_boundary(
    boundary: object | str | Path | None = None,
) -> ProgrammaticRepresentationBoundaryValidation:
    data, read_issues = _load_boundary(
        programmatic_representation_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return ProgrammaticRepresentationBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ProgrammaticRepresentationBoundaryIssue] = []
    if data.get("schema") != PROGRAMMATIC_REPRESENTATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported programmatic-representation boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "code candidates" not in source_claim
        or "natural-language hypotheses" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify code candidates versus natural-language hypotheses"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("runtime_report_status") != "programmatic_representation_boundary_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to programmatic-representation boundary telemetry"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "programmatic-representation boundary must not claim hallucination or bridge readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "representation claim gap matrix" not in boundary_text
        or "does not claim hallucination-risk measurement" not in boundary_text
        or "natural-language-to-programmatic bridge" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate structural representation evidence from hallucination and bridge claims"))
    return ProgrammaticRepresentationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_programmatic_representation_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_programmatic_representation_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Programmatic representation boundary",
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
) -> tuple[dict[str, Any] | None, list[ProgrammaticRepresentationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "programmatic-representation boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ProgrammaticRepresentationBoundaryIssue],
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
    issues: list[ProgrammaticRepresentationBoundaryIssue],
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


def _issue(code: str, message: str) -> ProgrammaticRepresentationBoundaryIssue:
    return ProgrammaticRepresentationBoundaryIssue(code, message)
