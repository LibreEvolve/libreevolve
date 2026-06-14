from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


GEMINI_SELF_TRAINING_LOOP_BOUNDARY_SCHEMA = (
    "libreevolve.gemini_self_training_loop_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("3.3.2", "Discussion")
EXPECTED_BOUNDARY_STATUS = "pallas_deployment_without_gemini_self_training_loop"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "pallas_kernel_deployment_record",
    "kernel_runtime_boundary",
    "gemini_model_family_identity",
    "gemini_training_workload_identity",
    "alphaevolve_backend_model_family_relation",
    "optimized_pallas_kernel_id",
    "production_deployment_or_rollout_state",
    "deployment_date_or_release_window",
    "before_training_time_measurement",
    "after_training_time_measurement",
    "before_kernel_runtime_measurement",
    "after_kernel_runtime_measurement",
    "training_efficiency_delta",
    "research_velocity_evidence",
    "engineering_turnaround_evidence",
    "self_optimization_interpretation_basis",
    "causal_link_to_gemini_training_pipeline",
    "rollback_or_safety_status",
    "team_or_owner_confirmation",
)
EXPECTED_MISSING_EVIDENCE = {
    "gemini_model_family_identity": "not_recorded_locally",
    "gemini_training_workload_identity": "not_recorded_locally",
    "alphaevolve_backend_model_family_relation": "not_recorded_locally",
    "optimized_pallas_kernel_id": "not_recorded_locally",
    "production_deployment_or_rollout_state": "not_recorded_locally",
    "deployment_date_or_release_window": "not_recorded_locally",
    "before_training_time_measurement": "not_recorded_locally",
    "after_training_time_measurement": "not_recorded_locally",
    "before_kernel_runtime_measurement": "not_recorded_locally",
    "after_kernel_runtime_measurement": "not_recorded_locally",
    "training_efficiency_delta": "not_recorded_locally",
    "research_velocity_evidence": "not_recorded_locally",
    "engineering_turnaround_evidence": "not_recorded_locally",
    "self_optimization_interpretation_basis": "not_recorded_locally",
    "causal_link_to_gemini_training_pipeline": "not_recorded_locally",
    "rollback_or_safety_status": "not_recorded_locally",
    "team_or_owner_confirmation": "not_recorded_locally",
}


@dataclass(frozen=True)
class GeminiSelfTrainingLoopBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class GeminiSelfTrainingLoopBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[GeminiSelfTrainingLoopBoundaryIssue]


def gemini_self_training_loop_boundary_record() -> dict[str, Any]:
    """Return the Gemini self-training loop evidence boundary."""

    return {
        "schema": GEMINI_SELF_TRAINING_LOOP_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 3.3.2 states that the deployed Pallas tiling "
            "heuristic enhanced Gemini training efficiency and the Gemini "
            "team's research and engineering velocity; the Discussion frames "
            "this as a novel case where Gemini, through AlphaEvolve, optimized "
            "its own training process"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "systems_result_schema": "libreevolve.systems_result_report.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can separately track "
            "Pallas kernel deployment and runtime evidence as prerequisites. "
            "It does not claim Gemini model-family identity, Gemini training "
            "workload identity, AlphaEvolve backend/model-family relation, "
            "optimized Pallas kernel id, production deployment or rollout "
            "state, deployment date or release window, before/after training "
            "time measurements, before/after kernel runtime measurements, "
            "training-efficiency deltas, research-velocity evidence, "
            "engineering-turnaround evidence, a self-optimization "
            "interpretation basis, causal linkage to the Gemini training "
            "pipeline, rollback/safety status, or team/owner confirmation."
        ),
    }


def validate_gemini_self_training_loop_boundary(
    boundary: object | str | Path | None = None,
) -> GeminiSelfTrainingLoopBoundaryValidation:
    data, read_issues = _load_boundary(
        gemini_self_training_loop_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return GeminiSelfTrainingLoopBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[GeminiSelfTrainingLoopBoundaryIssue] = []
    if data.get("schema") != GEMINI_SELF_TRAINING_LOOP_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Gemini self-training loop boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 3.3.2 and Discussion"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "Gemini training efficiency" not in source_claim
        or "research and engineering velocity" not in source_claim
        or "optimized its own training process" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify Gemini training-efficiency and self-optimization claims"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("systems_result_schema") != "libreevolve.systems_result_report.v1":
        issues.append(_issue("invalid_systems_result_schema", "systems result schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Gemini self-training boundary must not claim self-optimization readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim Gemini model-family identity" not in boundary_text
        or "causal linkage to the Gemini training pipeline" not in boundary_text
        or "team/owner confirmation" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate Pallas deployment from Gemini self-training evidence"))
    return GeminiSelfTrainingLoopBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_gemini_self_training_loop_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_gemini_self_training_loop_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Gemini self-training loop boundary",
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
) -> tuple[dict[str, Any] | None, list[GeminiSelfTrainingLoopBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Gemini self-training loop boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[GeminiSelfTrainingLoopBoundaryIssue],
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
    issues: list[GeminiSelfTrainingLoopBoundaryIssue],
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


def _issue(code: str, message: str) -> GeminiSelfTrainingLoopBoundaryIssue:
    return GeminiSelfTrainingLoopBoundaryIssue(code, message)
