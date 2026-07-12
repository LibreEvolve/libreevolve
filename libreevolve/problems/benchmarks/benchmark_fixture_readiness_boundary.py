from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BENCHMARK_FIXTURE_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_benchmark_fixture_readiness_boundary.v1"
)
BENCHMARK_FIXTURE_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.benchmark_fixture_readiness_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "smoke_scope_with_deterministic_matrix_calibration_only"
EXPECTED_MATRIX_FIXTURE_REPORT_SCHEMA = "libreevolve.matrix_cascade_fixture_report.v1"
EXPECTED_MATRIX_FIXTURE_REPORT_REF = (
    "libreevolve/problems/benchmarks/artifacts/matrix_cascade_fixture/"
    "matrix/mm_2x2x2/cascade_fixture_report.json"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "example_scope_record_present",
    "scope_registry_valid",
    "not_smoke_only_claim",
    "alphaevolve_comparable_scope",
    "reviewed_formulation_metadata",
    "background_knowledge_refs",
    "task_spec_target_identity",
    "benchmark_hardening_refs",
    "repeated_seed_protocol",
    "sota_or_target_baseline_values",
    "fixture_emitted_result_artifacts",
    "anti_gaming_negative_fixtures_passed",
    "benchmark_fixture_readiness",
    "alphaevolve_paper_claim_fixture",
)
EXPECTED_MISSING_EVIDENCE = {
    "non_smoke_benchmark_scope_record": "not_recorded_locally",
    "alphaevolve_comparable_scope_record": "not_recorded_locally",
    "anti_gaming_negative_fixtures_passed": "not_recorded_locally",
    "paper_claim_ready_benchmark_fixture": "not_recorded_locally",
}


@dataclass(frozen=True)
class BenchmarkFixtureReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class BenchmarkFixtureReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[BenchmarkFixtureReadinessBoundaryIssue]


def benchmark_fixture_readiness_boundary_record() -> dict[str, Any]:
    """Return the current AlphaEvolve benchmark-fixture readiness boundary."""

    return {
        "schema": BENCHMARK_FIXTURE_READINESS_BOUNDARY_SCHEMA,
        "runtime_report_schema": BENCHMARK_FIXTURE_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve paper-facing benchmark claims require scoped fixtures, "
            "expert formulation, task targets, repeated-seed evidence, "
            "baseline values, emitted result artifacts, and anti-gaming checks"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "matrix_fixture_report_schema": EXPECTED_MATRIX_FIXTURE_REPORT_SCHEMA,
        "matrix_fixture_report_ref": EXPECTED_MATRIX_FIXTURE_REPORT_REF,
        "matrix_fixture_status": "executed_rank7_rank8_known_control_calibration",
        "runtime_report_status": "benchmark_fixture_readiness_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has runtime readiness "
            "telemetry for example-scope registry linkage, smoke fixture scope, "
            "formulation/review metadata, task-spec identity, and benchmark "
            "hardening references when present. A checked four-seed matrix "
            "fixture records known rank-7/rank-8 baselines and emitted traces, "
            "but does not claim non-smoke AlphaEvolve-comparable fixture scope, "
            "search-derived repeated-seed results, anti-gaming negative-fixture "
            "checks for a full benchmark, or paper-claim-ready benchmark fixtures."
        ),
    }


def validate_benchmark_fixture_readiness_boundary(
    boundary: object | str | Path | None = None,
) -> BenchmarkFixtureReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        benchmark_fixture_readiness_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return BenchmarkFixtureReadinessBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[BenchmarkFixtureReadinessBoundaryIssue] = []
    if data.get("schema") != BENCHMARK_FIXTURE_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported benchmark-fixture readiness boundary schema"))
    if data.get("runtime_report_schema") != BENCHMARK_FIXTURE_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify benchmark-fixture readiness reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("matrix_fixture_report_schema") != EXPECTED_MATRIX_FIXTURE_REPORT_SCHEMA:
        issues.append(_issue("invalid_matrix_fixture_report_schema", "matrix fixture report schema linkage is invalid"))
    if data.get("matrix_fixture_report_ref") != EXPECTED_MATRIX_FIXTURE_REPORT_REF:
        issues.append(_issue("invalid_matrix_fixture_report_ref", "matrix fixture report ref must identify the checked report"))
    if data.get("matrix_fixture_status") != "executed_rank7_rank8_known_control_calibration":
        issues.append(_issue("invalid_matrix_fixture_status", "matrix fixture status must identify known-control calibration"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "benchmark claims" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve benchmark-claim evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "benchmark_fixture_readiness_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to benchmark-fixture readiness reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "benchmark-fixture readiness boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "checked four-seed matrix fixture" not in boundary_text
        or "does not claim" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim benchmark readiness"))
    return BenchmarkFixtureReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_benchmark_fixture_readiness_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_benchmark_fixture_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve benchmark-fixture readiness boundary",
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
) -> tuple[dict[str, Any] | None, list[BenchmarkFixtureReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "benchmark-fixture readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[BenchmarkFixtureReadinessBoundaryIssue],
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
    issues: list[BenchmarkFixtureReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> BenchmarkFixtureReadinessBoundaryIssue:
    return BenchmarkFixtureReadinessBoundaryIssue(code, message)
