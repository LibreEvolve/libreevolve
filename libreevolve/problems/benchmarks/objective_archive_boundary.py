from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


OBJECTIVE_ARCHIVE_BOUNDARY_SCHEMA = "libreevolve.objective_archive_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_FRONTIER_SCHEMA = "libreevolve.objective_frontier.v1"
EXPECTED_POLICY_SCHEMA = "libreevolve.map_elites_objective_archive_policy.v1"
EXPECTED_READINESS_SCHEMA = "libreevolve.map_elites_objective_archive_readiness.v1"
EXPECTED_BOUNDARY_STATUS = "bounded_retained_overlays_not_primary_pareto_archive"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "diagnostic_objective_frontier",
    "declared_normalized_metric_vectors",
    "bounded_pareto_frontier_retention",
    "metric_cell_archive_overlays",
    "metric_and_frontier_sampling_pools",
    "objective_archive_policy_snapshot",
    "objective_primary_archive_readiness_report",
    "readiness_overclaim_rejection",
    "primary_pareto_archive_replacement",
    "frontier_dominance_cell_replacement",
    "durable_cross_run_metric_database",
    "metric_target_persistence_tables",
    "llm_feedback_calibration_runner",
    "cross_run_metric_specific_optimization",
    "frontier_primary_archive_replay",
)
EXPECTED_MISSING_EVIDENCE = {
    "primary_pareto_archive_replacement": "not_recorded_locally",
    "frontier_dominance_cell_replacement": "not_recorded_locally",
    "durable_cross_run_metric_database": "not_recorded_locally",
    "metric_target_persistence_tables": "not_recorded_locally",
    "llm_feedback_calibration_runner": "not_recorded_locally",
    "cross_run_metric_specific_optimization": "not_recorded_locally",
    "frontier_primary_archive_replay": "not_recorded_locally",
}


@dataclass(frozen=True)
class ObjectiveArchiveBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ObjectiveArchiveBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ObjectiveArchiveBoundaryIssue]


def objective_archive_boundary_record() -> dict[str, Any]:
    """Return the multi-objective overlay versus primary archive boundary."""

    return {
        "schema": OBJECTIVE_ARCHIVE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve can optimize multiple user-provided scores, so "
            "multi-objective tradeoffs should be part of the durable archive "
            "policy rather than only diagnostic views"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_frontier_schema": EXPECTED_RUNTIME_FRONTIER_SCHEMA,
        "objective_archive_policy_schema": EXPECTED_POLICY_SCHEMA,
        "objective_archive_readiness_schema": EXPECTED_READINESS_SCHEMA,
        "runtime_report_status": (
            "objective_frontier_map_elites_policy_and_primary_readiness_"
            "audit_available"
        ),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests and archive "
            "snapshots include diagnostic objective frontiers, declared "
            "normalized metric vectors, bounded Pareto frontier retention, "
            "metric-cell archive overlays, metric/frontier sampling pools, "
            "objective archive policy snapshots, an objective primary archive "
            "readiness audit, and readiness overclaim rejection. It does not "
            "claim primary Pareto archive replacement, "
            "frontier-dominance cell replacement, durable cross-run metric "
            "databases, metric-target persistence tables, LLM feedback "
            "calibration runners, cross-run metric-specific optimization, or "
            "frontier primary archive replay."
        ),
    }


def validate_objective_archive_boundary(
    boundary: object | str | Path | None = None,
) -> ObjectiveArchiveBoundaryValidation:
    data, read_issues = _load_boundary(
        objective_archive_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ObjectiveArchiveBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ObjectiveArchiveBoundaryIssue] = []
    if data.get("schema") != OBJECTIVE_ARCHIVE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported objective archive boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "multiple user-provided scores" not in source_claim
        or "durable archive policy" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify multi-objective durable archive policy"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_frontier_schema") != EXPECTED_RUNTIME_FRONTIER_SCHEMA:
        issues.append(_issue("invalid_runtime_frontier_schema", f"runtime_frontier_schema must be {EXPECTED_RUNTIME_FRONTIER_SCHEMA}"))
    if data.get("objective_archive_policy_schema") != EXPECTED_POLICY_SCHEMA:
        issues.append(_issue("invalid_objective_archive_policy_schema", f"objective_archive_policy_schema must be {EXPECTED_POLICY_SCHEMA}"))
    if data.get("objective_archive_readiness_schema") != EXPECTED_READINESS_SCHEMA:
        issues.append(_issue("invalid_objective_archive_readiness_schema", f"objective_archive_readiness_schema must be {EXPECTED_READINESS_SCHEMA}"))
    allowed_report_statuses = {
        "objective_frontier_and_map_elites_policy_available",
        (
            "objective_frontier_map_elites_policy_and_primary_readiness_"
            "audit_available"
        ),
    }
    if data.get("runtime_report_status") not in allowed_report_statuses:
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to diagnostic frontier, retained overlay, and readiness-audit evidence"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "objective archive boundary must not claim primary Pareto archive readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim primary Pareto archive replacement" not in boundary_text
        or "durable cross-run metric databases" not in boundary_text
        or "frontier primary archive replay" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate retained overlays from primary multi-objective archive readiness"))
    return ObjectiveArchiveBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_objective_archive_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_objective_archive_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Objective archive boundary",
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
) -> tuple[dict[str, Any] | None, list[ObjectiveArchiveBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "objective archive boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ObjectiveArchiveBoundaryIssue],
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
    issues: list[ObjectiveArchiveBoundaryIssue],
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


def _issue(code: str, message: str) -> ObjectiveArchiveBoundaryIssue:
    return ObjectiveArchiveBoundaryIssue(code, message)
