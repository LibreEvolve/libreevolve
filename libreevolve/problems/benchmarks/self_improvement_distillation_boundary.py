from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SELF_IMPROVEMENT_DISTILLATION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_self_improvement_distillation_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("Discussion",)
EXPECTED_LOCAL_PDF_PAGE = 21
EXPECTED_BOUNDARY_STATUS = "discussion_context_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "optimized_component_identity",
    "optimization_objective",
    "before_after_runtime_or_cost_metrics",
    "candidate_to_libreevolve_execution_path_provenance",
    "deployment_or_adoption_status",
    "rollback_safety_review",
    "production_or_self_hosted_runtime_evidence",
    "base_llm_uplift_target_identity",
    "distillation_dataset_provenance",
    "distillation_training_run",
    "student_model_evaluation_artifacts",
    "feedback_loop_cadence_record",
    "environment_roi_record",
    "claim_to_artifact_certification_row",
)
EXPECTED_MISSING_EVIDENCE = {
    "optimized_component_identity": "not_recorded_locally",
    "optimization_objective": "not_recorded_locally",
    "before_after_runtime_or_cost_metrics": "not_recorded_locally",
    "candidate_to_libreevolve_execution_path_provenance": "not_recorded_locally",
    "deployment_or_adoption_status": "not_recorded_locally",
    "rollback_safety_review": "not_recorded_locally",
    "production_or_self_hosted_runtime_evidence": "not_recorded_locally",
    "base_llm_uplift_target_identity": "not_recorded_locally",
    "distillation_dataset_provenance": "not_recorded_locally",
    "distillation_training_run": "not_recorded_locally",
    "student_model_evaluation_artifacts": "not_recorded_locally",
    "feedback_loop_cadence_record": "not_recorded_locally",
    "environment_roi_record": "not_recorded_locally",
    "claim_to_artifact_certification_row": "not_recorded_locally",
}


@dataclass(frozen=True)
class SelfImprovementDistillationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SelfImprovementDistillationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[SelfImprovementDistillationBoundaryIssue]


def self_improvement_distillation_boundary_record() -> dict[str, Any]:
    """Return the current self-improvement/distillation absence boundary."""

    return {
        "schema": SELF_IMPROVEMENT_DISTILLATION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "local_pdf_page": EXPECTED_LOCAL_PDF_PAGE,
        "source_claim": (
            "AlphaEvolve's Discussion describes practical discoveries that can "
            "improve its own infrastructure and future base LLMs, and mentions "
            "distilling AlphaEvolve-augmented performance into next-generation "
            "base models"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "non_evidence_boundaries": {
            "ttt_rl_grpo_data_jsonl": (
                "bounded prompt/response/reward export; not online RL, "
                "base-model distillation, or student-model evaluation"
            ),
            "provider_budget_reports": (
                "runtime-cost telemetry; not an evolved improvement to "
                "LibreEvolve's own execution path"
            ),
            "systems_result_schemas": (
                "paper-result metadata contracts; not deployment/adoption or "
                "rollback evidence for self-improving infrastructure"
            ),
        },
        "claim_boundary": (
            "This boundary records AlphaEvolve self-improvement and "
            "distillation as Discussion context only. LibreEvolve does not "
            "claim evolved optimization of its own runtime/provider/evaluator/"
            "compiler/benchmark infrastructure, measured before/after "
            "execution-path improvement, deployment or adoption status, "
            "rollback/safety review, production or self-hosted runtime "
            "evidence, base-LLM uplift, distillation dataset provenance, "
            "distillation training runs, student-model evaluation artifacts, "
            "feedback-loop cadence, environment ROI, or paper-facing "
            "certification rows for those claims."
        ),
    }


def validate_self_improvement_distillation_boundary(
    boundary: object | str | Path | None = None,
) -> SelfImprovementDistillationBoundaryValidation:
    data, read_issues = _load_boundary(
        self_improvement_distillation_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SelfImprovementDistillationBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[SelfImprovementDistillationBoundaryIssue] = []
    if data.get("schema") != SELF_IMPROVEMENT_DISTILLATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported self-improvement/distillation boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['Discussion']"))
    if data.get("local_pdf_page") != EXPECTED_LOCAL_PDF_PAGE:
        issues.append(_issue("invalid_local_pdf_page", "local_pdf_page must be 21"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "distilling" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify Discussion distillation context"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "self-improvement/distillation boundary must not claim readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    _validate_non_evidence_boundaries(data.get("non_evidence_boundaries"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "Discussion context only" not in boundary_text
        or "does not claim evolved optimization" not in boundary_text
        or "distillation training runs" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must keep self-improvement and distillation claims absent"))
    return SelfImprovementDistillationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_self_improvement_distillation_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_self_improvement_distillation_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve self-improvement/distillation boundary",
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
) -> tuple[dict[str, Any] | None, list[SelfImprovementDistillationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "self-improvement/distillation boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[SelfImprovementDistillationBoundaryIssue],
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
    issues: list[SelfImprovementDistillationBoundaryIssue],
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


def _validate_non_evidence_boundaries(
    value: object,
    issues: list[SelfImprovementDistillationBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_non_evidence_boundaries", "non_evidence_boundaries must be an object"))
        return
    for key in ("ttt_rl_grpo_data_jsonl", "provider_budget_reports", "systems_result_schemas"):
        text = value.get(key)
        if not isinstance(text, str) or "not" not in text:
            issues.append(_issue(f"invalid_non_evidence_boundary_{key}", f"non_evidence_boundaries.{key} must state non-evidence scope"))


def _issue(code: str, message: str) -> SelfImprovementDistillationBoundaryIssue:
    return SelfImprovementDistillationBoundaryIssue(code, message)
