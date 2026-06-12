from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


METRIC_DIVERSE_PROMPT_BOUNDARY_SCHEMA = (
    "libreevolve.metric_diverse_prompt_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_REPORT_SCHEMA = "libreevolve.metric_diverse_inspiration_report.v1"
EXPECTED_RUNTIME_RECORD_SCHEMA = "libreevolve.metric_diverse_inspiration.v1"
EXPECTED_BENCHMARK_POLICY_SCHEMA = (
    "libreevolve.metric_diverse_prompt_benchmark_boundary.v1"
)
EXPECTED_COMPARISON_READINESS_SCHEMA = (
    "libreevolve.metric_diverse_benchmark_comparison_readiness.v1"
)
EXPECTED_BOUNDARY_STATUS = "prompt_visible_evidence_not_benchmark_policy"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "declared_metric_vectors",
    "metric_targeted_parent_inspiration_metadata",
    "prompt_context_metric_filtering",
    "prompt_visible_inspiration_ids",
    "metric_niche_labels",
    "raw_and_normalized_metric_values",
    "prompt_hash_linkage",
    "metric_diverse_inspiration_report",
    "benchmark_policy_false_readiness",
    "benchmark_comparison_false_readiness",
    "benchmark_required_metric_diverse_prompt_policy",
    "cross_run_metric_diverse_prompt_fixture",
    "scalar_only_baseline_comparison",
    "single_metric_target_baseline_comparison",
    "equal_budget_comparison_report",
    "alphaevolve_section_2_4_benchmark_readiness",
)
EXPECTED_MISSING_EVIDENCE = {
    "benchmark_required_metric_diverse_prompt_policy": "not_recorded_locally",
    "cross_run_metric_diverse_prompt_fixture": "not_recorded_locally",
    "scalar_only_baseline_comparison": "not_recorded_locally",
    "single_metric_target_baseline_comparison": "not_recorded_locally",
    "equal_budget_comparison_report": "not_recorded_locally",
    "alphaevolve_section_2_4_benchmark_readiness": "not_recorded_locally",
}


@dataclass(frozen=True)
class MetricDiversePromptBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MetricDiversePromptBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[MetricDiversePromptBoundaryIssue]


def metric_diverse_prompt_boundary_record() -> dict[str, Any]:
    """Return the metric-diverse prompt evidence versus benchmark-policy boundary."""

    return {
        "schema": METRIC_DIVERSE_PROMPT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve Section 2.4 says multiple scores can improve a "
            "primary target because prompts include programs that excel under "
            "different criteria, each representing a different definition of good"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_record_schema": EXPECTED_RUNTIME_RECORD_SCHEMA,
        "benchmark_policy_schema": EXPECTED_BENCHMARK_POLICY_SCHEMA,
        "benchmark_comparison_readiness_schema": (
            EXPECTED_COMPARISON_READINESS_SCHEMA
        ),
        "runtime_report_status": "metric_diverse_prompt_visible_evidence_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests can show "
            "prompt-visible metric-diverse inspiration evidence: declared "
            "metric vectors, metric-targeted selection metadata, prompt-context "
            "metric filtering, prompt-visible inspiration ids, metric-niche "
            "labels, raw and normalized metric values, prompt hash linkage, "
            "and metric-diverse inspiration reports with false readiness "
            "fields. It does not claim benchmark-required metric-diverse "
            "prompt policy, cross-run metric-diverse prompt fixtures, scalar "
            "only baseline comparison, single-metric target baseline "
            "comparison, equal-budget comparison reports, or AlphaEvolve "
            "Section 2.4 benchmark readiness."
        ),
    }


def validate_metric_diverse_prompt_boundary(
    boundary: object | str | Path | None = None,
) -> MetricDiversePromptBoundaryValidation:
    data, read_issues = _load_boundary(
        metric_diverse_prompt_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MetricDiversePromptBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MetricDiversePromptBoundaryIssue] = []
    if data.get("schema") != METRIC_DIVERSE_PROMPT_BOUNDARY_SCHEMA:
        issues.append(
            _issue("invalid_schema", "unsupported metric-diverse prompt boundary schema")
        )
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(
            _issue("invalid_source_paper_id", "source_paper_id must be 2506.13131")
        )
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "multiple scores can improve" not in source_claim
        or "different definition of good" not in source_claim
    ):
        issues.append(
            _issue(
                "invalid_source_claim",
                "source_claim must identify AlphaEvolve Section 2.4 multi-score prompt evidence",
            )
        )
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(
            _issue(
                "invalid_boundary_status",
                f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}",
            )
        )
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(
            _issue(
                "invalid_runtime_report_schema",
                f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}",
            )
        )
    if data.get("runtime_record_schema") != EXPECTED_RUNTIME_RECORD_SCHEMA:
        issues.append(
            _issue(
                "invalid_runtime_record_schema",
                f"runtime_record_schema must be {EXPECTED_RUNTIME_RECORD_SCHEMA}",
            )
        )
    if data.get("benchmark_policy_schema") != EXPECTED_BENCHMARK_POLICY_SCHEMA:
        issues.append(
            _issue(
                "invalid_benchmark_policy_schema",
                f"benchmark_policy_schema must be {EXPECTED_BENCHMARK_POLICY_SCHEMA}",
            )
        )
    if (
        data.get("benchmark_comparison_readiness_schema")
        != EXPECTED_COMPARISON_READINESS_SCHEMA
    ):
        issues.append(
            _issue(
                "invalid_benchmark_comparison_readiness_schema",
                "benchmark_comparison_readiness_schema must match runtime readiness schema",
            )
        )
    if (
        data.get("runtime_report_status")
        != "metric_diverse_prompt_visible_evidence_available"
    ):
        issues.append(
            _issue(
                "invalid_runtime_report_status",
                "runtime report status must stay scoped to prompt-visible evidence",
            )
        )
    if data.get("claim_ready") is not False:
        issues.append(
            _issue(
                "claim_ready_overclaim",
                "metric-diverse prompt boundary must not claim benchmark readiness",
            )
        )
    required_count = _validate_required_fields(
        data.get("required_evidence_fields"),
        issues,
    )
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim benchmark-required metric-diverse prompt policy"
        not in boundary_text
        or "equal-budget comparison reports" not in boundary_text
        or "AlphaEvolve Section 2.4 benchmark readiness" not in boundary_text
    ):
        issues.append(
            _issue(
                "missing_claim_boundary",
                "claim_boundary must separate prompt-visible evidence from benchmark policy readiness",
            )
        )
    return MetricDiversePromptBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_metric_diverse_prompt_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_metric_diverse_prompt_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Metric-diverse prompt boundary",
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
) -> tuple[dict[str, Any] | None, list[MetricDiversePromptBoundaryIssue]]:
    if isinstance(boundary, dict):
        return dict(boundary), []
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [
                _issue("invalid_json", f"boundary JSON is invalid: {exc}")
            ]
    else:
        try:
            data = json.loads(Path(boundary).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [
                _issue("unreadable_boundary", f"boundary could not be loaded: {exc}")
            ]
    if isinstance(data, dict):
        return data, []
    return None, [
        _issue("invalid_shape", "metric-diverse prompt boundary must be a JSON object")
    ]


def _validate_required_fields(
    value: object,
    issues: list[MetricDiversePromptBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(
            _issue(
                "invalid_required_evidence_fields",
                "required_evidence_fields must be a list",
            )
        )
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(
            _issue(
                "missing_required_evidence_field",
                f"missing required evidence fields: {', '.join(missing)}",
            )
        )
    if extra:
        issues.append(
            _issue(
                "extra_required_evidence_field",
                f"unknown required evidence fields: {', '.join(extra)}",
            )
        )
    if len(seen) != len(value):
        issues.append(
            _issue(
                "invalid_required_evidence_field",
                "required evidence fields must be strings",
            )
        )
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[MetricDiversePromptBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(
            _issue("invalid_missing_evidence", "missing_evidence must be an object")
        )
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(
            _issue(
                "missing_missing_evidence_key",
                f"missing_evidence lacks keys: {', '.join(missing)}",
            )
        )
    if extra:
        issues.append(
            _issue(
                "extra_missing_evidence_key",
                f"missing_evidence has unknown keys: {', '.join(extra)}",
            )
        )
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(
                _issue(
                    f"invalid_missing_evidence_{key}",
                    f"missing_evidence.{key} must be {expected_value}",
                )
            )
    return len(actual_keys)


def _issue(code: str, message: str) -> MetricDiversePromptBoundaryIssue:
    return MetricDiversePromptBoundaryIssue(code, message)
