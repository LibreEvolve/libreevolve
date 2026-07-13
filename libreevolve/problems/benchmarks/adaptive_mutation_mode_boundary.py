from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ADAPTIVE_MUTATION_MODE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_adaptive_mutation_mode_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.3",)
EXPECTED_BOUNDARY_STATUS = "adaptive_candidate_shape_selection_partial"
EXPECTED_SUPPORTED_MODES = ("diff", "full")
EXPECTED_SUPPORTING_SURFACES = (
    "config_mutation_mode",
    "cli_mutation_mode",
    "prompt_mutation_mode_fields",
    "diff_parser",
    "full_replacement_parser",
    "mutation_mode_history_metadata",
    "adaptive_mutation_mode_runtime_report",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "run_wide_configured_mode",
    "per_candidate_mode_selection",
    "candidate_size_thresholds",
    "workspace_shape_thresholds",
    "task_shape_policy",
    "parent_failure_history_policy",
    "parser_fallback_policy",
    "critique_fallback_policy",
    "prompt_metadata",
    "selection_reason_telemetry",
    "large_codebase_diff_selection_test",
    "short_code_full_selection_test",
    "mixed_mode_run_history",
    "paper_visible_selection_report",
)
EXPECTED_MISSING_EVIDENCE = {
    "benchmark_calibrated_thresholds": "not_recorded_locally",
    "semantic_complete_rewrite_appropriateness": "not_recorded_locally",
    "response_quality_aware_mode_policy": "not_recorded_locally",
    "equal_budget_diff_full_adaptive_ablation": "not_recorded_locally",
}
EXPECTED_IMPLEMENTED_EVIDENCE = {
    "per_candidate_mode_selection": "recorded_in_candidate_history",
    "candidate_size_thresholds": "configured_and_recorded",
    "workspace_shape_thresholds": "file_char_and_evolve_block_counts_recorded",
    "task_shape_policy": "explicit_auto_diff_or_full_preference",
    "parent_failure_history_policy": "threshold_mode_switch_recorded",
    "parser_fallback_policy": "opposite_mode_response_format_fallback_recorded",
    "critique_fallback_policy": "selected_mode_validation_with_parser_fallback",
    "prompt_metadata": "selected_mode_and_policy_recorded",
    "selection_reason_telemetry": "runtime_report_counts_and_sample_records",
    "large_codebase_diff_selection_test": "executable_regression",
    "short_code_full_selection_test": "executable_regression",
    "mixed_mode_run_history": "runtime_reported_when_observed",
    "paper_visible_selection_report": "runtime_history_adaptive_mutation_mode_report",
}


@dataclass(frozen=True)
class AdaptiveMutationModeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AdaptiveMutationModeBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AdaptiveMutationModeBoundaryIssue]


def adaptive_mutation_mode_boundary_record() -> dict[str, Any]:
    """Return the current adaptive mutation-output mode boundary."""

    return {
        "schema": ADAPTIVE_MUTATION_MODE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 2.3 requests SEARCH/REPLACE diffs for larger "
            "codebases and full-code output for very short code or complete "
            "rewrite cases"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "supported_modes": list(EXPECTED_SUPPORTED_MODES),
        "supporting_surfaces": list(EXPECTED_SUPPORTING_SURFACES),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "implemented_evidence": dict(EXPECTED_IMPLEMENTED_EVIDENCE),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records configured run-wide diff/full modes plus an "
            "adaptive per-candidate policy using workspace size, file and evolve-"
            "block shape, explicit task preference, parent-mode failure history, "
            "response-format parser fallback, selected-mode critique validation, "
            "prompt/history metadata, mixed-mode telemetry, and executable short-"
            "full/large-diff tests. It does not claim benchmark-calibrated "
            "thresholds, semantic proof that a complete rewrite is appropriate, "
            "response-quality-aware selection, or an equal-budget adaptive "
            "ablation."
        ),
    }


def validate_adaptive_mutation_mode_boundary(
    boundary: object | str | Path | None = None,
) -> AdaptiveMutationModeBoundaryValidation:
    data, read_issues = _load_boundary(
        adaptive_mutation_mode_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AdaptiveMutationModeBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AdaptiveMutationModeBoundaryIssue] = []
    if data.get("schema") != ADAPTIVE_MUTATION_MODE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported adaptive mutation-mode boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.3']"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "SEARCH/REPLACE diffs" not in source_claim or "full-code output" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify diff and full-code output selection"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "adaptive mutation-mode boundary must not claim full AlphaEvolve parity"))
    _validate_list_field(
        data.get("supported_modes"),
        set(EXPECTED_SUPPORTED_MODES),
        "supported_modes",
        issues,
    )
    _validate_list_field(
        data.get("supporting_surfaces"),
        set(EXPECTED_SUPPORTING_SURFACES),
        "supporting_surfaces",
        issues,
    )
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    _validate_evidence_map(
        data.get("implemented_evidence"),
        EXPECTED_IMPLEMENTED_EVIDENCE,
        "implemented_evidence",
        issues,
    )
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "adaptive per-candidate policy" not in boundary_text
        or "does not claim benchmark-calibrated" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must scope local adaptive selection and remaining parity gaps"))
    return AdaptiveMutationModeBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_adaptive_mutation_mode_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_adaptive_mutation_mode_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve adaptive mutation-mode boundary",
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
) -> tuple[dict[str, Any] | None, list[AdaptiveMutationModeBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "adaptive mutation-mode boundary must be a JSON object")]


def _validate_list_field(
    value: object,
    expected: set[str],
    field: str,
    issues: list[AdaptiveMutationModeBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue(f"invalid_{field}", f"{field} must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue(f"missing_{field}", f"{field} lacks entries: {', '.join(missing)}"))
    if extra:
        issues.append(_issue(f"extra_{field}", f"{field} has unknown entries: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue(f"invalid_{field}_entry", f"{field} entries must be strings"))
    return len(seen)


def _validate_required_fields(
    value: object,
    issues: list[AdaptiveMutationModeBoundaryIssue],
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
    issues: list[AdaptiveMutationModeBoundaryIssue],
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


def _validate_evidence_map(
    value: object,
    expected: dict[str, str],
    field: str,
    issues: list[AdaptiveMutationModeBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue(f"invalid_{field}", f"{field} must be an object"))
        return
    if value != expected:
        issues.append(_issue(f"invalid_{field}", f"{field} must match implemented evidence"))


def _issue(code: str, message: str) -> AdaptiveMutationModeBoundaryIssue:
    return AdaptiveMutationModeBoundaryIssue(code, message)
