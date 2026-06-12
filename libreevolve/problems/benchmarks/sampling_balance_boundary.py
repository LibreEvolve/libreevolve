from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SAMPLING_BALANCE_BOUNDARY_SCHEMA = "libreevolve.sampling_balance_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_REPORT_SCHEMA = "libreevolve.sampling_balance_report.v1"
EXPECTED_BOUNDARY_STATUS = "local_sampling_counts_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "configured_explore_ratio",
    "parent_strategy_counts",
    "inspiration_strategy_counts",
    "per_generation_decision_counts",
    "candidate_sample_records",
    "parent_selection_metadata",
    "inspiration_selection_metadata",
    "strategy_source_counts",
    "fallback_source_pool_provenance",
    "selected_program_repetition_table",
    "island_cell_metric_lineage_descriptor_coverage",
    "score_improvement_vs_diversity_effects",
    "equal_budget_strategy_comparisons",
    "calibrated_exploration_exploitation_policy",
)
EXPECTED_MISSING_EVIDENCE = {
    "fallback_source_pool_provenance": "not_recorded_locally",
    "selected_program_repetition_table": "not_recorded_locally",
    "island_cell_metric_lineage_descriptor_coverage": "not_recorded_locally",
    "score_improvement_vs_diversity_effects": "not_recorded_locally",
    "equal_budget_strategy_comparisons": "not_recorded_locally",
    "calibrated_exploration_exploitation_policy": "not_recorded_locally",
}


@dataclass(frozen=True)
class SamplingBalanceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SamplingBalanceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[SamplingBalanceBoundaryIssue]


def sampling_balance_boundary_record() -> dict[str, Any]:
    """Return the local sampling-counts versus calibrated balance boundary."""

    return {
        "schema": SAMPLING_BALANCE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve's evolutionary database balances exploration and "
            "exploitation while maintaining diversity across the search space"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_report_status": "sampling_balance_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests include local "
            "sampling counts from runtime.history.sampling_balance_report: "
            "configured explore ratio, parent and inspiration strategy counts, "
            "per-generation decision counts, sampled candidate metadata, "
            "strategy-source counts, and metric/frontier/lineage indicators. "
            "It does not claim calibrated exploration/exploitation balance, "
            "fallback source-pool provenance, selected-program repetition "
            "tables, island/cell/metric/lineage/descriptor coverage, "
            "score-improvement versus diversity effects, equal-budget strategy "
            "comparisons, or an AlphaEvolve-grade database-balance policy."
        ),
    }


def validate_sampling_balance_boundary(
    boundary: object | str | Path | None = None,
) -> SamplingBalanceBoundaryValidation:
    data, read_issues = _load_boundary(
        sampling_balance_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SamplingBalanceBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[SamplingBalanceBoundaryIssue] = []
    if data.get("schema") != SAMPLING_BALANCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported sampling-balance boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "balances exploration and exploitation" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify exploration/exploitation balance"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("runtime_report_status") != "sampling_balance_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to local sampling-count telemetry"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "sampling-balance boundary must not claim calibrated exploration/exploitation balance"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim calibrated exploration/exploitation balance" not in boundary_text
        or "equal-budget strategy comparisons" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate local sampling counts from calibrated balance evidence"))
    return SamplingBalanceBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_sampling_balance_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_sampling_balance_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Sampling balance boundary",
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
) -> tuple[dict[str, Any] | None, list[SamplingBalanceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "sampling-balance boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[SamplingBalanceBoundaryIssue],
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
    issues: list[SamplingBalanceBoundaryIssue],
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


def _issue(code: str, message: str) -> SamplingBalanceBoundaryIssue:
    return SamplingBalanceBoundaryIssue(code, message)
