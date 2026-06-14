from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FIGURE6_SCHEDULING_EXHIBIT_BOUNDARY_SCHEMA = (
    "libreevolve.figure6_scheduling_exhibit_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("Figure 6", "3.3.1")
EXPECTED_BOUNDARY_STATUS = "required_exhibit_contract_without_artifacts"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stable_exhibit_id",
    "scheduling_benchmark_candidate_link",
    "exact_heuristic_source_artifact",
    "heuristic_source_sha256",
    "figure6_code_identity_map",
    "residual_feature_definitions",
    "cpu_memory_unit_definitions",
    "residual_grid_artifact",
    "heatmap_data_artifact",
    "heatmap_rendering_parameters",
    "rendered_heatmap_artifact_hash",
    "baseline_production_heuristic_identity",
    "simulator_feedback_report_link",
    "heldout_recent_workload_report_link",
    "deployment_measurement_report_link",
    "resource_recovery_denominator_window",
    "claim_calibration_record",
    "ranking_only_safety_linkage",
    "scheduling_formulation_linkage",
    "deployment_readiness_linkage",
)
EXPECTED_MISSING_EVIDENCE = {
    "stable_exhibit_id": "not_recorded_locally",
    "scheduling_benchmark_candidate_link": "not_recorded_locally",
    "exact_heuristic_source_artifact": "not_recorded_locally",
    "heuristic_source_sha256": "not_recorded_locally",
    "figure6_code_identity_map": "not_recorded_locally",
    "residual_feature_definitions": "not_recorded_locally",
    "cpu_memory_unit_definitions": "not_recorded_locally",
    "residual_grid_artifact": "not_recorded_locally",
    "heatmap_data_artifact": "not_recorded_locally",
    "heatmap_rendering_parameters": "not_recorded_locally",
    "rendered_heatmap_artifact_hash": "not_recorded_locally",
    "baseline_production_heuristic_identity": "not_recorded_locally",
    "simulator_feedback_report_link": "not_recorded_locally",
    "heldout_recent_workload_report_link": "not_recorded_locally",
    "deployment_measurement_report_link": "not_recorded_locally",
    "resource_recovery_denominator_window": "not_recorded_locally",
    "claim_calibration_record": "not_recorded_locally",
    "ranking_only_safety_linkage": "not_recorded_locally",
    "scheduling_formulation_linkage": "not_recorded_locally",
    "deployment_readiness_linkage": "not_recorded_locally",
}


@dataclass(frozen=True)
class Figure6SchedulingExhibitBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class Figure6SchedulingExhibitBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[Figure6SchedulingExhibitBoundaryIssue]


def figure6_scheduling_exhibit_boundary_record() -> dict[str, Any]:
    """Return the Figure 6 scheduling exhibit provenance boundary."""

    return {
        "schema": FIGURE6_SCHEDULING_EXHIBIT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Figure 6 presents the Borg scheduling heuristic "
            "alpha_evolve_score(required, free), CPU/memory residual heatmap "
            "evidence, and Section 3.3.1 connects that heuristic to simulator "
            "feedback, unseen workload measurements, deployment, and about "
            "0.7% fleet-wide compute resource recovery"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "systems_readiness_boundary_schema": (
            "libreevolve.alphaevolve_systems_result_readiness_boundary.v1"
        ),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the required Figure 6 scheduling-exhibit "
            "contract only. It does not claim a stable exhibit row, scheduling "
            "benchmark or candidate linkage, exact heuristic source artifact, "
            "source hash, Figure 6 code identity map, residual feature/unit "
            "definitions, residual-grid data, heatmap data, rendering "
            "parameters, rendered heatmap hashes, baseline production heuristic "
            "identity, simulator feedback report links, held-out recent "
            "workload report links, deployment measurement report links, "
            "resource-recovery denominator/window evidence, claim calibration, "
            "ranking-only safety linkage, scheduling formulation linkage, or "
            "deployment-readiness linkage."
        ),
    }


def validate_figure6_scheduling_exhibit_boundary(
    boundary: object | str | Path | None = None,
) -> Figure6SchedulingExhibitBoundaryValidation:
    data, read_issues = _load_boundary(
        figure6_scheduling_exhibit_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return Figure6SchedulingExhibitBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[Figure6SchedulingExhibitBoundaryIssue] = []
    if data.get("schema") != FIGURE6_SCHEDULING_EXHIBIT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Figure 6 scheduling exhibit boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be Figure 6 and 3.3.1"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "alpha_evolve_score(required, free)" not in source_claim
        or "0.7% fleet-wide compute resource recovery" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify Figure 6 heuristic and resource-recovery claim"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if (
        data.get("systems_readiness_boundary_schema")
        != "libreevolve.alphaevolve_systems_result_readiness_boundary.v1"
    ):
        issues.append(_issue("invalid_systems_readiness_boundary_schema", "systems readiness boundary schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Figure 6 scheduling exhibit boundary must not claim artifact readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a stable exhibit row" not in boundary_text
        or "rendered heatmap hashes" not in boundary_text
        or "deployment-readiness linkage" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate the required contract from Figure 6 exhibit artifacts"))
    return Figure6SchedulingExhibitBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_figure6_scheduling_exhibit_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_figure6_scheduling_exhibit_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Figure 6 scheduling exhibit boundary",
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
) -> tuple[dict[str, Any] | None, list[Figure6SchedulingExhibitBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Figure 6 scheduling exhibit boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[Figure6SchedulingExhibitBoundaryIssue],
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
    issues: list[Figure6SchedulingExhibitBoundaryIssue],
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


def _issue(code: str, message: str) -> Figure6SchedulingExhibitBoundaryIssue:
    return Figure6SchedulingExhibitBoundaryIssue(code, message)
