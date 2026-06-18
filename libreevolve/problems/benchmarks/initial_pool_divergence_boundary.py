from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


INITIAL_POOL_DIVERGENCE_BOUNDARY_SCHEMA = (
    "libreevolve.initial_pool_divergence_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_REPORT_SCHEMA = "libreevolve.initial_pool_divergence_report.v1"
EXPECTED_BOUNDARY_STATUS = "syntactic_metric_and_evaluator_output_telemetry_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "seed_pool_baseline_records",
    "generated_candidate_workspace_hashes",
    "exact_seed_workspace_match_counts",
    "bounded_primary_file_text_distance",
    "changed_component_summary",
    "numeric_metric_l1_distance",
    "generic_evaluator_output_signature_distance",
    "candidate_seed_comparison_records",
    "task_specific_functional_distance_artifacts",
    "behavior_or_output_distance_metrics",
    "substantially_different_threshold_policy",
    "benchmark_level_discovery_distance_telemetry",
    "cross_run_discovery_distance_table",
    "syntax_and_function_joint_claim_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "task_specific_functional_distance_artifacts": "not_recorded_locally",
    "behavior_or_output_distance_metrics": "not_recorded_locally",
    "substantially_different_threshold_policy": "not_recorded_locally",
    "benchmark_level_discovery_distance_telemetry": "not_recorded_locally",
    "cross_run_discovery_distance_table": "not_recorded_locally",
    "syntax_and_function_joint_claim_gate": "not_recorded_locally",
}


@dataclass(frozen=True)
class InitialPoolDivergenceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class InitialPoolDivergenceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[InitialPoolDivergenceBoundaryIssue]


def initial_pool_divergence_boundary_record() -> dict[str, Any]:
    """Return the initial-pool divergence telemetry versus discovery claim boundary."""

    return {
        "schema": INITIAL_POOL_DIVERGENCE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve says feedback-driven evolution can discover "
            "candidates substantially different from the initial candidate "
            "pool in both syntax and function"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_report_status": "initial_pool_divergence_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests include "
            "runtime.history.initial_pool_divergence_report for seed-pool "
            "baseline records, generated candidate workspace hashes, exact "
            "seed workspace match counts, bounded primary-file text distance, "
            "changed component summaries, numeric metric L1 distance, and "
            "generic bounded evaluator-output signature distance in "
            "candidate-to-seed comparison records. It does not claim "
            "task-specific functional-distance artifacts, task-specific "
            "behavior or output distance metrics, substantially-different "
            "threshold policy, benchmark-level discovery-distance telemetry, "
            "cross-run discovery-distance tables, or a syntax-and-function "
            "joint claim gate."
        ),
    }


def validate_initial_pool_divergence_boundary(
    boundary: object | str | Path | None = None,
) -> InitialPoolDivergenceBoundaryValidation:
    data, read_issues = _load_boundary(
        initial_pool_divergence_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return InitialPoolDivergenceBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[InitialPoolDivergenceBoundaryIssue] = []
    if data.get("schema") != INITIAL_POOL_DIVERGENCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported initial-pool divergence boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "substantially different" not in source_claim
        or "syntax and function" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify syntax-and-function discovery distance"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("runtime_report_status") != "initial_pool_divergence_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to initial-pool divergence telemetry"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "initial-pool divergence boundary must not claim functional discovery-distance readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim task-specific functional-distance artifacts" not in boundary_text
        or "generic bounded evaluator-output signature distance" not in boundary_text
        or "substantially-different threshold policy" not in boundary_text
        or "syntax-and-function joint claim gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate telemetry from functional discovery-distance claims"))
    return InitialPoolDivergenceBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_initial_pool_divergence_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_initial_pool_divergence_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Initial-pool divergence boundary",
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
) -> tuple[dict[str, Any] | None, list[InitialPoolDivergenceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "initial-pool divergence boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[InitialPoolDivergenceBoundaryIssue],
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
    issues: list[InitialPoolDivergenceBoundaryIssue],
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


def _issue(code: str, message: str) -> InitialPoolDivergenceBoundaryIssue:
    return InitialPoolDivergenceBoundaryIssue(code, message)
