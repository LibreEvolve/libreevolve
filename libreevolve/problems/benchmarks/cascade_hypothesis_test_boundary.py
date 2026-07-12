from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CASCADE_HYPOTHESIS_TEST_BOUNDARY_SCHEMA = (
    "libreevolve.cascade_hypothesis_test_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_ID = "2.4"
EXPECTED_SOURCE_SECTION_IDS = ("2.4",)
EXPECTED_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.cascade_hypothesis_test_policy_report.v1"
)
EXPECTED_TRANSITION_MATRIX_SCHEMA = (
    "libreevolve.evaluation_cascade_transition_matrix.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "runtime_policy_with_deterministic_matrix_calibration_without_empirical_error_rates"
)
EXPECTED_MATRIX_FIXTURE_REPORT_SCHEMA = "libreevolve.matrix_cascade_fixture_report.v1"
EXPECTED_MATRIX_FIXTURE_REPORT_REF = (
    "libreevolve/problems/benchmarks/artifacts/matrix_cascade_fixture/"
    "matrix/mm_2x2x2/cascade_fixture_report.json"
)
EXPECTED_MATRIX_EVOLUTION_FIXTURE_REPORT_SCHEMA = (
    "libreevolve.matrix_evolution_fixture_report.v1"
)
EXPECTED_MATRIX_EVOLUTION_FIXTURE_REPORT_REF = (
    "libreevolve/problems/benchmarks/artifacts/matrix_evolution_fixture/"
    "matrix/mm_2x2x2/evolution_fixture_report.json"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stage_role_inference",
    "small_scale_filter_role",
    "main_test_role",
    "deterministic_threshold_promotion_policy",
    "artifact_check_promotion_policy",
    "one_sided_lower_confidence_bound_gate",
    "retained_per_sample_observations",
    "confidence_bound_evidence",
    "p_value_evidence",
    "sequential_stopping_diagnostics",
    "error_budget_fields",
    "binomial_success_rate_gate",
    "wilson_lower_bound_evidence",
    "benchmark_calibrated_thresholds",
    "repeated_seed_benchmark_fixtures",
    "small_filter_to_main_test_linkage",
    "empirical_false_promotion_validation",
    "empirical_false_rejection_validation",
)
EXPECTED_MISSING_EVIDENCE = {
    "empirical_false_promotion_validation": "not_recorded_locally",
    "empirical_false_rejection_validation": "not_recorded_locally",
}


@dataclass(frozen=True)
class CascadeHypothesisTestBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CascadeHypothesisTestBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CascadeHypothesisTestBoundaryIssue]


def cascade_hypothesis_test_boundary_record() -> dict[str, Any]:
    """Return the cascade hypothesis-test policy versus benchmark-ready boundary."""

    return {
        "schema": CASCADE_HYPOTHESIS_TEST_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_id": EXPECTED_SOURCE_SECTION_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve describes cascades as hypothesis testing where "
            "small-scale filters promote sufficiently promising candidates "
            "toward larger main-test cases"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "transition_matrix_schema": EXPECTED_TRANSITION_MATRIX_SCHEMA,
        "matrix_fixture_report_schema": EXPECTED_MATRIX_FIXTURE_REPORT_SCHEMA,
        "matrix_fixture_report_ref": EXPECTED_MATRIX_FIXTURE_REPORT_REF,
        "matrix_fixture_status": "executed_deterministic_rank7_rank8_calibration",
        "matrix_evolution_fixture_report_schema": (
            EXPECTED_MATRIX_EVOLUTION_FIXTURE_REPORT_SCHEMA
        ),
        "matrix_evolution_fixture_report_ref": (
            EXPECTED_MATRIX_EVOLUTION_FIXTURE_REPORT_REF
        ),
        "matrix_evolution_fixture_status": (
            "executed_normal_evolve_pipeline_scripted_control"
        ),
        "runtime_report_status": "cascade_hypothesis_test_policy_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can report inferred or "
            "configured stage roles, deterministic threshold and artifact-check "
            "promotion policies, opt-in one-sided lower-confidence-bound gates "
            "with retained observations, confidence-bound and p-value evidence, "
            "sequential stopping diagnostics, configured error-budget fields, "
            "and binomial success-rate gates with Wilson lower-bound evidence. "
            "It also records runtime small-filter-to-main-test promotion linkage "
            "through a reconciled adjacent-stage transition matrix and an "
            "executed deterministic repeated-seed matrix fixture that promotes "
            "rank 7 and rejects rank 8 at a pinned threshold. A linked four-seed "
            "scripted control also runs the normal evolve pipeline and records "
            "causal parentage, budget use, and emitted cascade stages. It does "
            "not claim stochastic-search calibration or stochastic LLM discovery, "
            "empirical false-promotion "
            "validation, or empirical false-rejection validation."
        ),
    }


def validate_cascade_hypothesis_test_boundary(
    boundary: object | str | Path | None = None,
) -> CascadeHypothesisTestBoundaryValidation:
    data, read_issues = _load_boundary(
        cascade_hypothesis_test_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CascadeHypothesisTestBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CascadeHypothesisTestBoundaryIssue] = []
    if data.get("schema") != CASCADE_HYPOTHESIS_TEST_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported cascade hypothesis-test boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_id") != EXPECTED_SOURCE_SECTION_ID:
        issues.append(_issue("invalid_source_section_id", "source_section_id must be 2.4"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.4']"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "hypothesis testing" not in source_claim
        or "main-test cases" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify hypothesis-testing cascade promotion"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("transition_matrix_schema") != EXPECTED_TRANSITION_MATRIX_SCHEMA:
        issues.append(_issue("invalid_transition_matrix_schema", f"transition_matrix_schema must be {EXPECTED_TRANSITION_MATRIX_SCHEMA}"))
    if data.get("matrix_fixture_report_schema") != EXPECTED_MATRIX_FIXTURE_REPORT_SCHEMA:
        issues.append(_issue("invalid_matrix_fixture_report_schema", f"matrix_fixture_report_schema must be {EXPECTED_MATRIX_FIXTURE_REPORT_SCHEMA}"))
    if data.get("matrix_fixture_report_ref") != EXPECTED_MATRIX_FIXTURE_REPORT_REF:
        issues.append(_issue("invalid_matrix_fixture_report_ref", "matrix_fixture_report_ref must identify the checked fixture report"))
    if data.get("matrix_fixture_status") != "executed_deterministic_rank7_rank8_calibration":
        issues.append(_issue("invalid_matrix_fixture_status", "matrix_fixture_status must identify the executed rank-7/rank-8 calibration"))
    if data.get("matrix_evolution_fixture_report_schema") != EXPECTED_MATRIX_EVOLUTION_FIXTURE_REPORT_SCHEMA:
        issues.append(_issue("invalid_matrix_evolution_fixture_report_schema", "matrix_evolution_fixture_report_schema linkage is invalid"))
    if data.get("matrix_evolution_fixture_report_ref") != EXPECTED_MATRIX_EVOLUTION_FIXTURE_REPORT_REF:
        issues.append(_issue("invalid_matrix_evolution_fixture_report_ref", "matrix_evolution_fixture_report_ref must identify the checked fixture report"))
    if data.get("matrix_evolution_fixture_status") != "executed_normal_evolve_pipeline_scripted_control":
        issues.append(_issue("invalid_matrix_evolution_fixture_status", "matrix_evolution_fixture_status must identify the scripted normal-pipeline control"))
    if data.get("runtime_report_status") != "cascade_hypothesis_test_policy_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to cascade hypothesis-test policy evidence"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "cascade hypothesis-test boundary must not claim benchmark-calibrated readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "runtime small-filter-to-main-test promotion linkage" not in boundary_text
        or "executed deterministic repeated-seed matrix fixture" not in boundary_text
        or "normal evolve pipeline" not in boundary_text
        or "stochastic LLM discovery" not in boundary_text
        or "does not claim stochastic-search calibration" not in boundary_text
        or "empirical false-promotion validation" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate runtime gates from benchmark-calibrated cascade evidence"))
    return CascadeHypothesisTestBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_cascade_hypothesis_test_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_cascade_hypothesis_test_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Cascade hypothesis-test boundary",
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
) -> tuple[dict[str, Any] | None, list[CascadeHypothesisTestBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "cascade hypothesis-test boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[CascadeHypothesisTestBoundaryIssue],
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
    issues: list[CascadeHypothesisTestBoundaryIssue],
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


def _issue(code: str, message: str) -> CascadeHypothesisTestBoundaryIssue:
    return CascadeHypothesisTestBoundaryIssue(code, message)
