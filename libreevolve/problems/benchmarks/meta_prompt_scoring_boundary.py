from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


META_PROMPT_SCORING_BOUNDARY_SCHEMA = (
    "libreevolve.meta_prompt_scoring_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.2",)
EXPECTED_BOUNDARY_STATUS = (
    "child_score_prompt_rewards_without_calibrated_lineage_attribution"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "prompt_reward_mode_absolute",
    "prompt_reward_mode_improvement",
    "finite_prompt_reward_bounds",
    "normalized_prompt_reward_metadata",
    "prompt_reward_policy_replay_compatibility",
    "ucb_style_prompt_arm_selection",
    "bounded_meta_prompt_performance_evidence",
    "prompt_history_reward_events",
    "latest_candidate_prompt_reward",
    "score_composition_prompt_reward_input",
    "calibrated_prompt_reward_signal",
    "prompt_lineage_ablation_report",
    "prompt_policy_effect_attribution",
    "parent_program_noise_control",
    "evaluator_noise_control",
    "equal_budget_prompt_policy_comparison",
)
EXPECTED_MISSING_EVIDENCE = {
    "calibrated_prompt_reward_signal": "not_recorded_locally",
    "prompt_lineage_ablation_report": "not_recorded_locally",
    "prompt_policy_effect_attribution": "not_recorded_locally",
    "parent_program_noise_control": "not_recorded_locally",
    "evaluator_noise_control": "not_recorded_locally",
    "equal_budget_prompt_policy_comparison": "not_recorded_locally",
}


@dataclass(frozen=True)
class MetaPromptScoringBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MetaPromptScoringBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[MetaPromptScoringBoundaryIssue]


def meta_prompt_scoring_boundary_record() -> dict[str, Any]:
    """Return the meta-prompt reward accounting versus calibrated scoring boundary."""

    return {
        "schema": META_PROMPT_SCORING_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve co-evolves prompt instructions and context; prompt "
            "updates should be justified by calibrated evidence that separates "
            "prompt-policy effects from program, parent, and evaluator noise"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_surfaces": {
            "prompt_database": "PromptDatabase",
            "prompt_history": "prompt_history.jsonl",
            "reward_metadata_key": "last_prompt_reward",
            "meta_prompt_request_builder": "_build_meta_prompt_mutation_request",
        },
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve supports absolute and "
            "improvement prompt reward modes, finite prompt reward bounds, "
            "normalized prompt reward metadata, prompt reward policy replay "
            "compatibility checks, UCB-style prompt-arm selection, bounded "
            "meta-prompt performance evidence, prompt-history reward events, "
            "latest-candidate prompt reward evidence, and score-composition "
            "inputs to prompt rewards. It does not claim calibrated prompt "
            "reward signals, prompt-lineage ablation reports, prompt-policy "
            "effect attribution, parent-program noise controls, evaluator "
            "noise controls, or equal-budget prompt-policy comparisons."
        ),
    }


def validate_meta_prompt_scoring_boundary(
    boundary: object | str | Path | None = None,
) -> MetaPromptScoringBoundaryValidation:
    data, read_issues = _load_boundary(
        meta_prompt_scoring_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MetaPromptScoringBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MetaPromptScoringBoundaryIssue] = []
    if data.get("schema") != META_PROMPT_SCORING_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported meta-prompt scoring boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.2"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "co-evolves prompt instructions" not in source_claim
        or "evaluator noise" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify prompt co-evolution and attribution noise"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    _validate_runtime_surfaces(data.get("runtime_surfaces"), issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "meta-prompt scoring boundary must not claim calibrated attribution readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim calibrated prompt reward signals" not in boundary_text
        or "prompt-lineage ablation reports" not in boundary_text
        or "equal-budget prompt-policy comparisons" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate child-score rewards from calibrated prompt attribution"))
    return MetaPromptScoringBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_meta_prompt_scoring_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_meta_prompt_scoring_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Meta-prompt scoring boundary",
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
) -> tuple[dict[str, Any] | None, list[MetaPromptScoringBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "meta-prompt scoring boundary must be a JSON object")]


def _validate_runtime_surfaces(
    value: object,
    issues: list[MetaPromptScoringBoundaryIssue],
) -> None:
    expected = {
        "prompt_database": "PromptDatabase",
        "prompt_history": "prompt_history.jsonl",
        "reward_metadata_key": "last_prompt_reward",
        "meta_prompt_request_builder": "_build_meta_prompt_mutation_request",
    }
    if value != expected:
        issues.append(_issue("invalid_runtime_surfaces", "runtime_surfaces must identify current prompt reward surfaces"))


def _validate_required_fields(
    value: object,
    issues: list[MetaPromptScoringBoundaryIssue],
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
    issues: list[MetaPromptScoringBoundaryIssue],
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


def _issue(code: str, message: str) -> MetaPromptScoringBoundaryIssue:
    return MetaPromptScoringBoundaryIssue(code, message)
