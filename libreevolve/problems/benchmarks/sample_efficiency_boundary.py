from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SAMPLE_EFFICIENCY_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_sample_efficiency_boundary.v1"
SAMPLE_EFFICIENCY_RUNTIME_REPORT_SCHEMA = "libreevolve.sample_efficiency_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "single_run_counts_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "run_id",
    "problem_id",
    "target_metric",
    "target_threshold",
    "llm_sample_count",
    "generated_candidate_count",
    "evaluated_candidate_count",
    "valid_candidate_count",
    "admitted_candidate_count",
    "retained_elite_count",
    "best_score_by_sample",
    "target_hit_sample_index",
    "thousands_scale_budget_curve_ref",
    "repeated_sampling_baseline_ref",
    "model_size_comparison_ref",
    "equal_budget_comparator_ref",
)
EXPECTED_MISSING_EVIDENCE = {
    "target_threshold_records": "not_recorded_locally",
    "target_hit_sample_index": "not_recorded_locally",
    "thousands_scale_budget_curves": "not_recorded_locally",
    "repeated_sampling_comparator_runs": "not_recorded_locally",
    "small_vs_strong_model_sample_curves": "not_recorded_locally",
    "cross_run_sample_efficiency_table": "not_recorded_locally",
    "funsearch_millions_vs_alphaevolve_thousands_reproduction": "not_recorded_locally",
}


@dataclass(frozen=True)
class SampleEfficiencyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SampleEfficiencyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[SampleEfficiencyBoundaryIssue]


def sample_efficiency_boundary_record() -> dict[str, Any]:
    """Return the current absence boundary for AlphaEvolve-style sample efficiency."""

    return {
        "schema": SAMPLE_EFFICIENCY_BOUNDARY_SCHEMA,
        "runtime_report_schema": SAMPLE_EFFICIENCY_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve-style sample efficiency contrasts thousands-scale LLM "
            "samples against larger repeated-sampling or weaker-model budgets"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "single_run_sample_efficiency_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has single-run generated, "
            "evaluated, valid, admitted, retained-elite, sampling-eligible, "
            "logical-sample, and bounded best-score counts, but does not claim "
            "AlphaEvolve-style target-hit sample-efficiency, thousands-scale "
            "proposal curves, repeated-sampling comparisons, model-size "
            "comparisons, or FunSearch-versus-AlphaEvolve budget reproduction."
        ),
    }


def validate_sample_efficiency_boundary(
    boundary: object | str | Path | None = None,
) -> SampleEfficiencyBoundaryValidation:
    data, read_issues = _load_boundary(
        sample_efficiency_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SampleEfficiencyBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[SampleEfficiencyBoundaryIssue] = []
    if data.get("schema") != SAMPLE_EFFICIENCY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported sample-efficiency boundary schema"))
    if data.get("runtime_report_schema") != SAMPLE_EFFICIENCY_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify sample-efficiency reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "thousands-scale" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify thousands-scale sample efficiency"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "single_run_sample_efficiency_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to single-run sample-efficiency reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "sample-efficiency boundary must not claim AlphaEvolve-scale efficiency readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim benchmark-level sample efficiency"))
    return SampleEfficiencyBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_sample_efficiency_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_sample_efficiency_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve sample-efficiency boundary",
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
) -> tuple[dict[str, Any] | None, list[SampleEfficiencyBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "sample-efficiency boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[SampleEfficiencyBoundaryIssue],
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
    issues: list[SampleEfficiencyBoundaryIssue],
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


def _issue(code: str, message: str) -> SampleEfficiencyBoundaryIssue:
    return SampleEfficiencyBoundaryIssue(code, message)
