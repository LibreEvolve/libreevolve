from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAP_ELITES_DESCRIPTOR_BOUNDARY_SCHEMA = "libreevolve.map_elites_descriptor_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_DESCRIPTOR_MODEL_SCHEMA = "libreevolve.map_elites_descriptor_model.v1"
EXPECTED_RUNTIME_READINESS_SCHEMA = "libreevolve.map_elites_descriptor_readiness.v1"
EXPECTED_BOUNDARY_STATUS = "insertion_time_local_descriptor_snapshots_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "descriptor_policy_axes",
    "descriptor_model_revision",
    "dynamic_diversity_reference_ids",
    "no_rebin_insertion_time_coordinate_policy",
    "per_cell_descriptor_value_snapshots",
    "restore_time_axes_and_model_validation",
    "readiness_overclaim_rejection",
    "metric_metadata_candidate_metadata_axis_options",
    "stable_task_behavior_descriptor_contract",
    "learned_descriptor_model",
    "evaluator_provided_descriptor_model",
    "descriptor_training_inputs",
    "restore_compatible_descriptor_revisioning",
    "full_archive_rebin_engine",
    "partial_archive_rebin_engine",
)
EXPECTED_MISSING_EVIDENCE = {
    "stable_task_behavior_descriptor_contract": "not_recorded_locally",
    "learned_descriptor_model": "not_recorded_locally",
    "evaluator_provided_descriptor_model": "not_recorded_locally",
    "descriptor_training_inputs": "not_recorded_locally",
    "restore_compatible_descriptor_revisioning": "not_recorded_locally",
    "full_archive_rebin_engine": "not_recorded_locally",
    "partial_archive_rebin_engine": "not_recorded_locally",
}


@dataclass(frozen=True)
class MapElitesDescriptorBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MapElitesDescriptorBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[MapElitesDescriptorBoundaryIssue]


def map_elites_descriptor_boundary_record() -> dict[str, Any]:
    """Return the MAP-Elites descriptor-model and rebin-semantics boundary."""

    return {
        "schema": MAP_ELITES_DESCRIPTOR_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve uses an evolutionary database inspired by MAP-Elites, "
            "where quality-diversity descriptors should be task-meaningful or "
            "otherwise stable enough to support archive semantics"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_descriptor_model_schema": EXPECTED_RUNTIME_DESCRIPTOR_MODEL_SCHEMA,
        "runtime_readiness_schema": EXPECTED_RUNTIME_READINESS_SCHEMA,
        "runtime_report_status": "map_elites_descriptor_model_available_in_archive_snapshots",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve MAP-Elites snapshots include "
            "descriptor policy axes, descriptor-model revision metadata, dynamic "
            "diversity reference ids, an explicit no-rebin insertion-time "
            "coordinate policy, per-cell finite descriptor-value snapshots, "
            "restore-time axes/model validation, readiness overclaim rejection, "
            "and metric/evaluation-metadata/candidate-metadata axis options. "
            "It does not claim stable task behavior "
            "descriptor contracts, learned descriptor models, evaluator-provided "
            "descriptor models, descriptor training inputs, restore-compatible "
            "descriptor revisioning, full archive rebin engines, or partial "
            "archive rebin engines."
        ),
    }


def validate_map_elites_descriptor_boundary(
    boundary: object | str | Path | None = None,
) -> MapElitesDescriptorBoundaryValidation:
    data, read_issues = _load_boundary(
        map_elites_descriptor_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MapElitesDescriptorBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MapElitesDescriptorBoundaryIssue] = []
    if data.get("schema") != MAP_ELITES_DESCRIPTOR_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported MAP-Elites descriptor boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "MAP-Elites" not in source_claim
        or "task-meaningful" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify MAP-Elites descriptor semantics"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_descriptor_model_schema") != EXPECTED_RUNTIME_DESCRIPTOR_MODEL_SCHEMA:
        issues.append(_issue("invalid_runtime_descriptor_model_schema", f"runtime_descriptor_model_schema must be {EXPECTED_RUNTIME_DESCRIPTOR_MODEL_SCHEMA}"))
    if data.get("runtime_readiness_schema") != EXPECTED_RUNTIME_READINESS_SCHEMA:
        issues.append(_issue("invalid_runtime_readiness_schema", f"runtime_readiness_schema must be {EXPECTED_RUNTIME_READINESS_SCHEMA}"))
    if data.get("runtime_report_status") != "map_elites_descriptor_model_available_in_archive_snapshots":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to archive snapshot descriptor models"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "MAP-Elites descriptor boundary must not claim stable descriptor/rebin readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim stable task behavior descriptor contracts" not in boundary_text
        or "learned descriptor models" not in boundary_text
        or "archive rebin engines" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate snapshot descriptors from stable descriptor/rebin readiness"))
    return MapElitesDescriptorBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_map_elites_descriptor_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_map_elites_descriptor_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "MAP-Elites descriptor boundary",
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
) -> tuple[dict[str, Any] | None, list[MapElitesDescriptorBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "MAP-Elites descriptor boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[MapElitesDescriptorBoundaryIssue],
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
    issues: list[MapElitesDescriptorBoundaryIssue],
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


def _issue(code: str, message: str) -> MapElitesDescriptorBoundaryIssue:
    return MapElitesDescriptorBoundaryIssue(code, message)
