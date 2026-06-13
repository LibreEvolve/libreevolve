from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EVALUATOR_ORACLE_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_evaluator_oracle_boundary.v1"
EVALUATOR_ORACLE_RUNTIME_REGISTRY_SCHEMA = "libreevolve.evaluator_oracle_registry.v1"
EVALUATOR_ORACLE_DISAGREEMENT_OUTCOMES_SCHEMA = (
    "libreevolve.evaluator_oracle_disagreement_outcomes.v1"
)
EVALUATOR_ORACLE_SOURCE_EVIDENCE_SCHEMA = (
    "libreevolve.evaluator_oracle_source_evidence.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_ID = "2.4"
EXPECTED_SOURCE_SECTION_IDS = ("2.4",)
EXPECTED_BOUNDARY_STATUS = "local_arbitration_without_independent_oracle_evidence"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "evaluator_id",
    "oracle_type",
    "authority",
    "input_schema",
    "output_schema",
    "metric_ownership",
    "oracle_source_ref",
    "oracle_source_hash",
    "independent_evidence_flag",
    "reference_or_statistical_oracle_id",
    "benchmark_sufficiency_label",
    "disagreement_case_id",
    "disagreement_resolution",
    "database_admission_effect",
    "score_reporting_effect",
    "prompt_feedback_effect",
    "cross_run_oracle_table_ref",
)
EXPECTED_MISSING_EVIDENCE = {
    "independent_reference_oracle_records": "not_recorded_locally",
    "statistical_oracle_records": "not_recorded_locally",
    "benchmark_sufficiency_evidence": (
        "local_source_refs_and_hashes_recorded_not_benchmark_sufficiency_proof"
    ),
    "independent_disagreement_outcomes": "not_recorded_locally",
    "database_admission_effect_records": "not_recorded_locally",
    "score_reporting_effect_records": "not_recorded_locally",
    "cross_run_oracle_table": "not_recorded_locally",
}


@dataclass(frozen=True)
class EvaluatorOracleBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class EvaluatorOracleBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[EvaluatorOracleBoundaryIssue]


def evaluator_oracle_boundary_record() -> dict[str, Any]:
    """Return the current independent evaluator-oracle evidence absence boundary."""

    return {
        "schema": EVALUATOR_ORACLE_BOUNDARY_SCHEMA,
        "runtime_registry_schema": EVALUATOR_ORACLE_RUNTIME_REGISTRY_SCHEMA,
        "disagreement_outcomes_schema": EVALUATOR_ORACLE_DISAGREEMENT_OUTCOMES_SCHEMA,
        "source_evidence_schema": EVALUATOR_ORACLE_SOURCE_EVIDENCE_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_id": EXPECTED_SOURCE_SECTION_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve improves candidates by continuously receiving feedback "
            "from one or more evaluators, with optional cascades and generated "
            "feedback layered around the user-provided evaluation function"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "evaluator_oracle_registry_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has local evaluator/cascade/"
            "feedback arbitration metadata plus local oracle source refs and "
            "hashes when available, but does not claim AlphaEvolve-style "
            "independent evaluator-oracle evidence with reference or statistical "
            "oracles, benchmark sufficiency proof, independent disagreement "
            "outcomes affecting validity, score reporting, database admission, "
            "or cross-run oracle tables."
        ),
    }


def validate_evaluator_oracle_boundary(
    boundary: object | str | Path | None = None,
) -> EvaluatorOracleBoundaryValidation:
    data, read_issues = _load_boundary(evaluator_oracle_boundary_record() if boundary is None else boundary)
    if read_issues:
        return EvaluatorOracleBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[EvaluatorOracleBoundaryIssue] = []
    if data.get("schema") != EVALUATOR_ORACLE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported evaluator-oracle boundary schema"))
    if data.get("runtime_registry_schema") != EVALUATOR_ORACLE_RUNTIME_REGISTRY_SCHEMA:
        issues.append(_issue("invalid_runtime_registry_schema", "runtime registry schema must identify evaluator-oracle registries"))
    if data.get("disagreement_outcomes_schema") != EVALUATOR_ORACLE_DISAGREEMENT_OUTCOMES_SCHEMA:
        issues.append(_issue("invalid_disagreement_outcomes_schema", "disagreement outcomes schema must identify evaluator-oracle disagreement reports"))
    if data.get("source_evidence_schema") != EVALUATOR_ORACLE_SOURCE_EVIDENCE_SCHEMA:
        issues.append(_issue("invalid_source_evidence_schema", "source evidence schema must identify evaluator-oracle source evidence reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_id") != EXPECTED_SOURCE_SECTION_ID:
        issues.append(_issue("invalid_source_section_id", "source_section_id must be 2.4"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.4']"))
    if not isinstance(data.get("source_claim"), str) or "one or more evaluators" not in data["source_claim"]:
        issues.append(_issue("invalid_source_claim", "source_claim must identify feedback from one or more evaluators"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "evaluator_oracle_registry_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to evaluator-oracle registry evidence"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "evaluator-oracle boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim independent evaluator-oracle evidence"))
    return EvaluatorOracleBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_evaluator_oracle_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_evaluator_oracle_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve evaluator-oracle boundary",
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
) -> tuple[dict[str, Any] | None, list[EvaluatorOracleBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "evaluator-oracle boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[EvaluatorOracleBoundaryIssue],
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
    issues: list[EvaluatorOracleBoundaryIssue],
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


def _issue(code: str, message: str) -> EvaluatorOracleBoundaryIssue:
    return EvaluatorOracleBoundaryIssue(code, message)
