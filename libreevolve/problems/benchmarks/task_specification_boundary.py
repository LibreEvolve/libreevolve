from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TASK_SPECIFICATION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_task_specification_boundary.v1"
)
TASK_SPECIFICATION_BUNDLE_SCHEMA = (
    "libreevolve.alphaevolve_task_specification_bundle.v1"
)
TASK_SPECIFICATION_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.task_spec_artifact_resolution_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "runtime_artifact_resolution_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "startup_task_spec_bundle_recorded",
    "task_specification_json_artifact_recorded",
    "initial_programs_manifest_linked",
    "evaluation_code_manifest_linked",
    "prompt_template_manifest_linked",
    "llm_ensemble_manifest_linked",
    "background_knowledge_manifest_linked",
    "objective_metrics_manifest_linked",
    "runtime_artifact_resolution_report_recorded",
    "candidate_prompt_evaluator_rows_joined",
    "evolvable_component_span_ids_when_marked",
    "embedded_score_field_causality_when_supported",
    "external_validator_score_causality",
    "arbitrary_language_build_runner_specs",
    "user_authored_standalone_task_spec",
    "full_alphaevolve_task_spec_parity",
)
EXPECTED_MISSING_EVIDENCE = {
    "external_validator_score_causality": "not_recorded_locally",
    "arbitrary_language_build_runner_specs": "not_recorded_locally",
    "user_authored_standalone_task_spec": "not_recorded_locally",
    "full_alphaevolve_task_spec_parity": "not_recorded_locally",
}


@dataclass(frozen=True)
class TaskSpecificationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class TaskSpecificationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[TaskSpecificationBoundaryIssue]


def task_specification_boundary_record() -> dict[str, Any]:
    """Return the paper-facing task-specification boundary."""

    return {
        "schema": TASK_SPECIFICATION_BOUNDARY_SCHEMA,
        "task_specification_bundle_schema": TASK_SPECIFICATION_BUNDLE_SCHEMA,
        "runtime_report_schema": TASK_SPECIFICATION_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve Section 2.1 and Figure 2 frame the task "
            "specification as user-provided initial program components, "
            "evaluation code, prompt template and configuration, LLM choices, "
            "and optional background knowledge before the evolutionary loop"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "task_spec_artifact_resolution_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve emits a startup task-spec "
            "bundle, a standalone task_specification.json artifact, and a "
            "runtime artifact-resolution report that links task-spec fields to "
            "manifest paths, candidate history, prompt history, evaluator "
            "rows, LLM calls, controller-budget rows, best exports, marked "
            "evolvable spans, and supported embedded score-field causality. It "
            "does not claim external-validator score causality, arbitrary "
            "language or build-runner task specs, user-authored standalone "
            "task-spec parity, or full AlphaEvolve task-spec parity."
        ),
    }


def validate_task_specification_boundary(
    boundary: object | str | Path | None = None,
) -> TaskSpecificationBoundaryValidation:
    data, read_issues = _load_boundary(
        task_specification_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return TaskSpecificationBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[TaskSpecificationBoundaryIssue] = []
    if data.get("schema") != TASK_SPECIFICATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported task-specification boundary schema"))
    if data.get("task_specification_bundle_schema") != TASK_SPECIFICATION_BUNDLE_SCHEMA:
        issues.append(_issue("invalid_task_specification_bundle_schema", "task-specification bundle schema is unsupported"))
    if data.get("runtime_report_schema") != TASK_SPECIFICATION_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify task-spec artifact-resolution reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "Figure 2" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve task-specification evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "task_spec_artifact_resolution_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to task-spec artifact-resolution reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "task-specification boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim external-validator score causality" not in boundary_text
        or "full AlphaEvolve task-spec parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that current task-spec artifacts are not full AlphaEvolve parity"))
    return TaskSpecificationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_task_specification_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_task_specification_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve task-specification boundary",
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
) -> tuple[dict[str, Any] | None, list[TaskSpecificationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "task-specification boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[TaskSpecificationBoundaryIssue],
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
    issues: list[TaskSpecificationBoundaryIssue],
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


def _issue(code: str, message: str) -> TaskSpecificationBoundaryIssue:
    return TaskSpecificationBoundaryIssue(code, message)
