from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EMBEDDED_EVALUATOR_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_embedded_evaluator_entrypoint_boundary.v1"
)
EMBEDDED_EVALUATOR_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.embedded_evaluator_entrypoint_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_ID = "2.1"
EXPECTED_SOURCE_SECTION_IDS = ("2.1", "2.3")
EXPECTED_SOURCE_FIGURE_IDS = ("Figure 3",)
EXPECTED_BOUNDARY_STATUS = "embedded_entrypoint_without_full_figure3_parity"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "candidate_primary_file",
    "evaluate_signature",
    "eval_inputs_schema",
    "evolved_block_span_id",
    "skeleton_invocation_trace",
    "score_field_name",
    "returned_metric_name",
    "score_to_block_link",
    "callable_isolation_policy",
    "workspace_dependency_policy",
    "build_isolation_policy",
    "external_validator_score_linkage",
    "figure3_prompt_exhibit_ref",
    "figure3_response_exhibit_ref",
)
EXPECTED_MISSING_EVIDENCE = {
    "build_isolation_policy": "not_recorded_locally",
    "non_static_score_field_causality": "not_recorded_locally",
    "external_validator_score_linkage": (
        "stage_metric_visibility_recorded_causal_linkage_not_recorded"
    ),
    "figure3_prompt_and_response_exhibits": "not_recorded_locally",
}


@dataclass(frozen=True)
class EmbeddedEvaluatorBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class EmbeddedEvaluatorBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[EmbeddedEvaluatorBoundaryIssue]


def embedded_evaluator_boundary_record() -> dict[str, Any]:
    """Return the current Figure 3 embedded-evaluator parity absence boundary."""

    return {
        "schema": EMBEDDED_EVALUATOR_BOUNDARY_SCHEMA,
        "runtime_report_schema": EMBEDDED_EVALUATOR_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_id": EXPECTED_SOURCE_SECTION_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_figure_ids": list(EXPECTED_SOURCE_FIGURE_IDS),
        "source_claim": (
            "AlphaEvolve Figure 3 shows a candidate codebase skeleton exposing "
            "evaluate(eval_inputs) -> dict[str, float], with evaluators invoking "
            "that function to score the modified program"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "embedded_evaluator_entrypoint_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has opt-in candidate-owned "
            "evaluate(eval_inputs) runtime evidence and static score-field "
            "attribution for supported embedded returns, plus a runtime-enforced "
            "materialized-candidate workspace dependency policy for local reads "
            "and imports, and external-validator stage metric visibility without "
            "causal score linkage, but does not claim full AlphaEvolve Figure 3 "
            "evaluator parity with build isolation, non-static or "
            "external-validator causal score linkage, or prompt/response exhibit "
            "artifacts."
        ),
    }


def validate_embedded_evaluator_boundary(
    boundary: object | str | Path | None = None,
) -> EmbeddedEvaluatorBoundaryValidation:
    data, read_issues = _load_boundary(
        embedded_evaluator_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return EmbeddedEvaluatorBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[EmbeddedEvaluatorBoundaryIssue] = []
    if data.get("schema") != EMBEDDED_EVALUATOR_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported embedded evaluator boundary schema"))
    if data.get("runtime_report_schema") != EMBEDDED_EVALUATOR_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify embedded evaluator reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_id") != EXPECTED_SOURCE_SECTION_ID:
        issues.append(_issue("invalid_source_section_id", "source_section_id must be 2.1"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.1', '2.3']"))
    if data.get("source_figure_ids") != list(EXPECTED_SOURCE_FIGURE_IDS):
        issues.append(_issue("invalid_source_figure_ids", "source_figure_ids must be ['Figure 3']"))
    if not isinstance(data.get("source_claim"), str) or "evaluate(eval_inputs)" not in data["source_claim"]:
        issues.append(_issue("invalid_source_claim", "source_claim must identify evaluate(eval_inputs)"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "embedded_evaluator_entrypoint_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to embedded evaluator reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "embedded evaluator boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim full Figure 3 evaluator parity"))
    return EmbeddedEvaluatorBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_embedded_evaluator_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_embedded_evaluator_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve embedded evaluator boundary",
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
) -> tuple[dict[str, Any] | None, list[EmbeddedEvaluatorBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "embedded evaluator boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[EmbeddedEvaluatorBoundaryIssue],
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
    issues: list[EmbeddedEvaluatorBoundaryIssue],
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


def _issue(code: str, message: str) -> EmbeddedEvaluatorBoundaryIssue:
    return EmbeddedEvaluatorBoundaryIssue(code, message)
