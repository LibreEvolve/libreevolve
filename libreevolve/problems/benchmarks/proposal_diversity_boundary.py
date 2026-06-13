from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROPOSAL_DIVERSITY_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_proposal_diversity_boundary.v1"
PROPOSAL_DIVERSITY_RUNTIME_REPORT_SCHEMA = "libreevolve.proposal_diversity_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "exact_text_diversity_without_semantic_novelty"
EXPECTED_CURRENT_EVIDENCE_FIELDS = (
    "generated_candidate_count",
    "captured_proposal_metadata_count",
    "exact_proposal_hashes",
    "exact_idea_hashes",
    "generation_duplicate_counts",
    "proposal_batch_duplicate_counts",
    "bounded_sample_records",
    "exact_text_analysis_policy",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "runtime_report_schema",
    "exact_proposal_hashes",
    "exact_idea_hashes",
    "operator_family_labels",
    "code_distance_metrics",
    "semantic_distance_metrics",
    "task_output_distance_metrics",
    "near_duplicate_detection",
    "parent_inspiration_relation",
    "prompt_context_backend_links",
    "accepted_rejected_status_linkage",
    "novelty_contribution_scoring",
    "equal_budget_model_ablation_linkage",
    "benchmark_level_proposal_diversity_telemetry",
)
EXPECTED_MISSING_EVIDENCE = {
    "operator_family_labels": "not_recorded_locally",
    "code_distance_metrics": "not_recorded_locally",
    "semantic_distance_metrics": "not_recorded_locally",
    "task_output_distance_metrics": "not_recorded_locally",
    "near_duplicate_detection": "not_recorded_locally",
    "parent_inspiration_relation": "not_recorded_locally",
    "prompt_context_backend_links": "not_recorded_locally",
    "novelty_contribution_scoring": "not_recorded_locally",
    "equal_budget_model_ablation_linkage": "not_recorded_locally",
    "benchmark_level_proposal_diversity_telemetry": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProposalDiversityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProposalDiversityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ProposalDiversityBoundaryIssue]


def proposal_diversity_boundary_record() -> dict[str, Any]:
    """Return the current AlphaEvolve proposal-diversity evidence boundary."""

    return {
        "schema": PROPOSAL_DIVERSITY_BOUNDARY_SCHEMA,
        "runtime_report_schema": PROPOSAL_DIVERSITY_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve Section 2.3 says SOTA LLMs digest previous solutions "
            "and propose new, diverse ways to improve them, with later ablations "
            "connecting model strength to performance"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "proposal_diversity_report_available",
        "claim_ready": False,
        "current_evidence_fields": list(EXPECTED_CURRENT_EVIDENCE_FIELDS),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records exact proposal and idea hash diversity, "
            "duplicate counts by generation and proposal batch, bounded sample "
            "records, and an exact-text analysis policy. It does not claim "
            "semantic proposal diversity, near-duplicate detection, "
            "operator-family labels, code or task-output distance, novelty "
            "contribution scoring, prompt/backend attribution, or equal-budget "
            "model-ablation linkage."
        ),
    }


def validate_proposal_diversity_boundary(
    boundary: object | str | Path | None = None,
) -> ProposalDiversityBoundaryValidation:
    data, read_issues = _load_boundary(
        proposal_diversity_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ProposalDiversityBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ProposalDiversityBoundaryIssue] = []
    if data.get("schema") != PROPOSAL_DIVERSITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported proposal-diversity boundary schema"))
    if data.get("runtime_report_schema") != PROPOSAL_DIVERSITY_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify proposal-diversity reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "new, diverse ways" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve creative-generation language"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "proposal_diversity_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to proposal-diversity reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "proposal-diversity boundary must not claim semantic novelty readiness"))
    _validate_current_evidence(data.get("current_evidence_fields"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim semantic proposal diversity" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that semantic proposal diversity is not claimed"))
    return ProposalDiversityBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_proposal_diversity_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_proposal_diversity_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve proposal-diversity boundary",
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
) -> tuple[dict[str, Any] | None, list[ProposalDiversityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "proposal-diversity boundary must be a JSON object")]


def _validate_current_evidence(
    value: object,
    issues: list[ProposalDiversityBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_current_evidence_fields", "current_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_CURRENT_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_current_evidence_field", f"current evidence fields lack entries: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_current_evidence_field", f"current evidence fields have unknown entries: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_current_evidence_field", "current evidence fields must be strings"))
    return len(seen)


def _validate_required_fields(
    value: object,
    issues: list[ProposalDiversityBoundaryIssue],
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
    issues: list[ProposalDiversityBoundaryIssue],
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


def _issue(code: str, message: str) -> ProposalDiversityBoundaryIssue:
    return ProposalDiversityBoundaryIssue(code, message)
