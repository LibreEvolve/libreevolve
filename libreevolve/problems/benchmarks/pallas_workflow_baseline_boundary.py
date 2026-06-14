from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PALLAS_WORKFLOW_BASELINE_BOUNDARY_SCHEMA = (
    "libreevolve.pallas_workflow_baseline_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("3.3.2",)
EXPECTED_BOUNDARY_STATUS = "pallas_runtime_without_workflow_baseline_evidence"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "kernel_shape_corpus_boundary",
    "kernel_runtime_boundary",
    "baseline_workflow_class",
    "search_autotuning_baseline_record",
    "manual_heuristic_baseline_record",
    "hybrid_expert_baseline_record",
    "autotuning_search_space",
    "autotuning_retuning_policy",
    "input_shape_change_sensitivity",
    "manual_authoring_effort",
    "manual_review_effort",
    "hardware_expertise_assumptions",
    "kernel_engineer_workflow_impact",
    "model_developer_ergonomics_impact",
    "alphaevolve_generated_heuristic_comparison",
    "baseline_comparison_artifacts",
    "workflow_interruption_evidence",
    "optimization_time_reduction_evidence",
)
EXPECTED_MISSING_EVIDENCE = {
    "baseline_workflow_class": "not_recorded_locally",
    "search_autotuning_baseline_record": "not_recorded_locally",
    "manual_heuristic_baseline_record": "not_recorded_locally",
    "hybrid_expert_baseline_record": "not_recorded_locally",
    "autotuning_search_space": "not_recorded_locally",
    "autotuning_retuning_policy": "not_recorded_locally",
    "input_shape_change_sensitivity": "not_recorded_locally",
    "manual_authoring_effort": "not_recorded_locally",
    "manual_review_effort": "not_recorded_locally",
    "hardware_expertise_assumptions": "not_recorded_locally",
    "kernel_engineer_workflow_impact": "not_recorded_locally",
    "model_developer_ergonomics_impact": "not_recorded_locally",
    "alphaevolve_generated_heuristic_comparison": "not_recorded_locally",
    "baseline_comparison_artifacts": "not_recorded_locally",
    "workflow_interruption_evidence": "not_recorded_locally",
    "optimization_time_reduction_evidence": "not_recorded_locally",
}


@dataclass(frozen=True)
class PallasWorkflowBaselineBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class PallasWorkflowBaselineBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[PallasWorkflowBaselineBoundaryIssue]


def pallas_workflow_baseline_boundary_record() -> dict[str, Any]:
    """Return the Pallas autotuning/manual-baseline workflow evidence boundary."""

    return {
        "schema": PALLAS_WORKFLOW_BASELINE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 3.3.2 contrasts Pallas search-based "
            "autotuning with manually crafted tiling heuristics: autotuning "
            "interrupts research workflows and requires retuning when input "
            "shapes change, while manual heuristic design is a major kernel "
            "engineering bottleneck requiring deep hardware expertise; "
            "AlphaEvolve is framed as automating manual tuning and improving "
            "Gemini kernel ergonomics"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "systems_result_schema": "libreevolve.systems_result_report.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve now separately tracks "
            "kernel shape-corpus/runtime evidence as a prerequisite. It does "
            "not claim baseline workflow class records, search-autotuning "
            "baseline records, manual-heuristic baseline records, hybrid expert "
            "baseline records, autotuning search-space evidence, retuning "
            "policy evidence, input-shape-change sensitivity, manual authoring "
            "or review effort, hardware-expertise assumptions, kernel engineer "
            "workflow impact, model-developer ergonomics impact, comparison of "
            "AlphaEvolve-generated heuristics against baseline workflows, "
            "baseline comparison artifacts, workflow-interruption evidence, or "
            "optimization-time reduction evidence."
        ),
    }


def validate_pallas_workflow_baseline_boundary(
    boundary: object | str | Path | None = None,
) -> PallasWorkflowBaselineBoundaryValidation:
    data, read_issues = _load_boundary(
        pallas_workflow_baseline_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return PallasWorkflowBaselineBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[PallasWorkflowBaselineBoundaryIssue] = []
    if data.get("schema") != PALLAS_WORKFLOW_BASELINE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Pallas workflow baseline boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 3.3.2"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "search-based autotuning" not in source_claim
        or "manually crafted tiling heuristics" not in source_claim
        or "retuning when input shapes change" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify autotuning, manual heuristics, and retuning burden"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("systems_result_schema") != "libreevolve.systems_result_report.v1":
        issues.append(_issue("invalid_systems_result_schema", "systems result schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Pallas workflow baseline boundary must not claim workflow automation readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim baseline workflow class records" not in boundary_text
        or "retuning policy evidence" not in boundary_text
        or "model-developer ergonomics impact" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate Pallas runtime evidence from workflow-baseline evidence"))
    return PallasWorkflowBaselineBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_pallas_workflow_baseline_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_pallas_workflow_baseline_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Pallas workflow baseline boundary",
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
) -> tuple[dict[str, Any] | None, list[PallasWorkflowBaselineBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Pallas workflow baseline boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[PallasWorkflowBaselineBoundaryIssue],
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
    issues: list[PallasWorkflowBaselineBoundaryIssue],
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


def _issue(code: str, message: str) -> PallasWorkflowBaselineBoundaryIssue:
    return PallasWorkflowBaselineBoundaryIssue(code, message)
