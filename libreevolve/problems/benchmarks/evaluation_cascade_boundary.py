from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EVALUATION_CASCADE_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_evaluation_cascade_boundary.v1"
EVALUATION_CASCADE_RUNTIME_REPORT_SCHEMA = "libreevolve.evaluation_cascade_report.v1"
CASCADE_HYPOTHESIS_TEST_POLICY_REPORT_SCHEMA = "libreevolve.cascade_hypothesis_test_policy_report.v1"
EVALUATION_CASCADE_STAGE_EVIDENCE_SUMMARY_SCHEMA = (
    "libreevolve.evaluation_cascade_stage_evidence_summary.v1"
)
EVALUATION_CASCADE_TRANSITION_MATRIX_SCHEMA = (
    "libreevolve.evaluation_cascade_transition_matrix.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_ID = "2.4"
EXPECTED_SOURCE_SECTION_IDS = ("2.4",)
EXPECTED_BOUNDARY_STATUS = (
    "runtime_transition_and_stage_identity_without_benchmark_efficiency_evidence"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stage_id",
    "stage_role",
    "stage_evidence_summary",
    "difficulty_scale_label",
    "evaluator_test_set_identity",
    "test_set_sha256",
    "sample_count",
    "random_seed_policy",
    "promotion_rule",
    "candidate_stage_transition_id",
    "promotion_decision_reason",
    "next_stage_exposure_link",
    "transition_denominator_policy",
    "main_test_exposure_count",
    "early_prune_count",
    "per_stage_elapsed_seconds",
    "counterfactual_full_evaluation_cost",
    "observed_cost_savings",
    "claim_readiness",
)
EXPECTED_MISSING_EVIDENCE = {
    "benchmark_seed_sample_policy": (
        "runtime_sample_accounting_only_not_benchmark_policy"
    ),
    "counterfactual_full_evaluation_costs": (
        "stage_evidence_summary_records_not_recorded"
    ),
    "wall_clock_cost_savings": "stage_evidence_summary_records_not_recorded",
    "matrix_multiplication_repeated_seed_policy": "not_recorded_locally",
}


@dataclass(frozen=True)
class EvaluationCascadeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class EvaluationCascadeBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[EvaluationCascadeBoundaryIssue]


def evaluation_cascade_boundary_record() -> dict[str, Any]:
    """Return the current cascade-efficiency evidence absence boundary."""

    return {
        "schema": EVALUATION_CASCADE_BOUNDARY_SCHEMA,
        "runtime_report_schema": EVALUATION_CASCADE_RUNTIME_REPORT_SCHEMA,
        "hypothesis_test_policy_report_schema": CASCADE_HYPOTHESIS_TEST_POLICY_REPORT_SCHEMA,
        "stage_evidence_summary_schema": EVALUATION_CASCADE_STAGE_EVIDENCE_SUMMARY_SCHEMA,
        "transition_matrix_schema": EVALUATION_CASCADE_TRANSITION_MATRIX_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_id": EXPECTED_SOURCE_SECTION_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "evaluation cascades use increasingly difficult test ensembles to "
            "promote promising candidates and prune less promising candidates "
            "before larger budgets are spent; paper-ready evidence must link "
            "candidate-level promotion and prune decisions to next-stage "
            "exposure and stage-specific rules"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "evaluation_cascade_report_available_when_stages_run",
        "stage_provenance_status": (
            "optional_complete_difficulty_and_content_hashed_test_set_contract"
        ),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has runtime cascade attrition "
            "reports, stage evidence summaries, hypothesis-test policy reports, and "
            "a runtime transition matrix with promotion-decision attribution, "
            "next-stage exposure linkage, bounded candidate ids, and denominator "
            "reconciliation. Configured stages can also record strictly increasing "
            "difficulty/scale rationale and content-hashed declared-data or "
            "eval-input test-set identities. It does not claim AlphaEvolve-style "
            "cascade-efficiency evidence with benchmark seed/sample policy, "
            "counterfactual full-evaluation costs, or observed wall-clock cost "
            "savings."
        ),
    }


def validate_evaluation_cascade_boundary(
    boundary: object | str | Path | None = None,
) -> EvaluationCascadeBoundaryValidation:
    data, read_issues = _load_boundary(
        evaluation_cascade_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return EvaluationCascadeBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[EvaluationCascadeBoundaryIssue] = []
    if data.get("schema") != EVALUATION_CASCADE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported evaluation cascade boundary schema"))
    if data.get("runtime_report_schema") != EVALUATION_CASCADE_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify evaluation cascade reports"))
    if data.get("hypothesis_test_policy_report_schema") != CASCADE_HYPOTHESIS_TEST_POLICY_REPORT_SCHEMA:
        issues.append(_issue("invalid_hypothesis_policy_schema", "hypothesis policy schema must identify cascade hypothesis reports"))
    if data.get("stage_evidence_summary_schema") != EVALUATION_CASCADE_STAGE_EVIDENCE_SUMMARY_SCHEMA:
        issues.append(_issue("invalid_stage_evidence_summary_schema", "stage evidence summary schema must identify cascade stage evidence summaries"))
    if data.get("transition_matrix_schema") != EVALUATION_CASCADE_TRANSITION_MATRIX_SCHEMA:
        issues.append(_issue("invalid_transition_matrix_schema", "transition matrix schema must identify cascade transition evidence"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_id") != EXPECTED_SOURCE_SECTION_ID:
        issues.append(_issue("invalid_source_section_id", "source_section_id must be 2.4"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.4']"))
    if (
        not isinstance(data.get("source_claim"), str)
        or "increasingly difficult" not in data["source_claim"]
        or "candidate-level promotion" not in data["source_claim"]
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify increasingly difficult cascade stages"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "evaluation_cascade_report_available_when_stages_run":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to cascade runtime reports"))
    if data.get("stage_provenance_status") != "optional_complete_difficulty_and_content_hashed_test_set_contract":
        issues.append(_issue("invalid_stage_provenance_status", "stage provenance status must identify the optional complete contract"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "evaluation cascade boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "runtime transition matrix" not in boundary_text
        or "promotion-decision attribution" not in boundary_text
        or "denominator reconciliation" not in boundary_text
        or "content-hashed declared-data or eval-input test-set identities" not in boundary_text
        or "does not claim AlphaEvolve-style cascade-efficiency" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim cascade-efficiency evidence"))
    return EvaluationCascadeBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_evaluation_cascade_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_evaluation_cascade_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve evaluation cascade boundary",
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
) -> tuple[dict[str, Any] | None, list[EvaluationCascadeBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "evaluation cascade boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[EvaluationCascadeBoundaryIssue],
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
    issues: list[EvaluationCascadeBoundaryIssue],
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


def _issue(code: str, message: str) -> EvaluationCascadeBoundaryIssue:
    return EvaluationCascadeBoundaryIssue(code, message)
