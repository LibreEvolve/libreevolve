from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FAST_STRONG_MODEL_MIX_BOUNDARY_SCHEMA = (
    "libreevolve.fast_strong_model_mix_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_ID = "2.3"
EXPECTED_SOURCE_SECTION_IDS = ("2.3",)
EXPECTED_BOUNDARY_STATUS = "throughput_depth_metadata_without_experiment_report"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "throughput_depth_strategy",
    "backend_cost_metadata",
    "backend_latency_metadata",
    "backend_depth_metadata",
    "metadata_normalization_policy",
    "metadata_weights",
    "neutral_missing_metadata_defaults",
    "backend_role_lane_labels",
    "backend_model_lane_labels",
    "fast_breadth_lane_detection",
    "strong_depth_lane_detection",
    "eligible_backend_lane_trace",
    "per_call_scheduler_policy",
    "claim_ready_false_lane_evidence",
    "experiment_level_selection_traces",
    "reserved_fast_breadth_lane_policy",
    "reserved_strong_depth_lane_policy",
    "candidate_throughput_outcomes",
    "candidate_quality_depth_outcomes",
    "equal_budget_single_model_comparison",
    "equal_budget_generic_ucb_comparison",
)
EXPECTED_MISSING_EVIDENCE = {
    "experiment_level_selection_traces": "not_recorded_locally",
    "reserved_fast_breadth_lane_policy": "not_recorded_locally",
    "reserved_strong_depth_lane_policy": "not_recorded_locally",
    "candidate_throughput_outcomes": "not_recorded_locally",
    "candidate_quality_depth_outcomes": "not_recorded_locally",
    "equal_budget_single_model_comparison": "not_recorded_locally",
    "equal_budget_generic_ucb_comparison": "not_recorded_locally",
}


@dataclass(frozen=True)
class FastStrongModelMixBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class FastStrongModelMixBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[FastStrongModelMixBoundaryIssue]


def fast_strong_model_mix_boundary_record() -> dict[str, Any]:
    """Return the throughput/depth metadata versus fast/strong experiment boundary."""

    return {
        "schema": FAST_STRONG_MODEL_MIX_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_id": EXPECTED_SOURCE_SECTION_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve mixes a fast model for high-volume breadth with a "
            "stronger model for occasional deeper suggestions under a fixed "
            "compute budget"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "scheduler_policy_schema": "libreevolve.llm_scheduler_policy.v1",
        "lane_evidence_policy": "throughput_depth_backend_metadata_lane_evidence_v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has a throughput_depth "
            "strategy with backend cost, latency, and depth metadata, min/max "
            "normalization, metadata weights, neutral missing-metadata "
            "defaults, backend role/model-lane labels, fast-breadth and "
            "strong-depth lane detection, eligible-backend lane traces, "
            "per-call scheduler policy records, and explicit false "
            "claim-readiness lane evidence. It does not claim experiment-level "
            "selection traces, reserved fast-breadth lane policy, reserved "
            "strong-depth lane policy, candidate throughput outcomes, "
            "candidate quality/depth outcomes, equal-budget single-model "
            "comparison, or equal-budget generic-UCB comparison."
        ),
    }


def validate_fast_strong_model_mix_boundary(
    boundary: object | str | Path | None = None,
) -> FastStrongModelMixBoundaryValidation:
    data, read_issues = _load_boundary(
        fast_strong_model_mix_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return FastStrongModelMixBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[FastStrongModelMixBoundaryIssue] = []
    if data.get("schema") != FAST_STRONG_MODEL_MIX_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported fast/strong model-mix boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_id") != EXPECTED_SOURCE_SECTION_ID:
        issues.append(_issue("invalid_source_section_id", "source_section_id must be 2.3"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.3']"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "fast model" not in source_claim
        or "stronger model" not in source_claim
        or "fixed compute budget" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify fast/strong fixed-budget scheduling"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    _validate_schema_field(data, "scheduler_policy_schema", "libreevolve.llm_scheduler_policy.v1", issues)
    _validate_schema_field(data, "lane_evidence_policy", "throughput_depth_backend_metadata_lane_evidence_v1", issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "fast/strong model-mix boundary must not claim AlphaEvolve scheduler readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim experiment-level selection traces" not in boundary_text
        or "reserved fast-breadth lane policy" not in boundary_text
        or "equal-budget generic-UCB comparison" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate metadata traces from fast/strong experiment evidence"))
    return FastStrongModelMixBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_fast_strong_model_mix_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_fast_strong_model_mix_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Fast/strong model-mix boundary",
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
) -> tuple[dict[str, Any] | None, list[FastStrongModelMixBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "fast/strong model-mix boundary must be a JSON object")]


def _validate_schema_field(
    data: dict[str, Any],
    field: str,
    expected: str,
    issues: list[FastStrongModelMixBoundaryIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(_issue(f"invalid_{field}", f"{field} must be {expected}"))


def _validate_required_fields(
    value: object,
    issues: list[FastStrongModelMixBoundaryIssue],
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
    issues: list[FastStrongModelMixBoundaryIssue],
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


def _issue(code: str, message: str) -> FastStrongModelMixBoundaryIssue:
    return FastStrongModelMixBoundaryIssue(code, message)
