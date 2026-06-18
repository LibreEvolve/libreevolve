from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROMPT_TEMPLATE_COMPATIBILITY_BOUNDARY_SCHEMA = (
    "libreevolve.prompt_template_compatibility_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.2", "2.3")
EXPECTED_BOUNDARY_STATUS = (
    "generic_template_validation_without_role_specific_compatibility_policy"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "known_placeholder_schema",
    "simple_placeholder_policy",
    "dry_run_formatting_validation",
    "configured_mutation_channel_semantic_policy",
    "prompt_format_fragment_validation",
    "prompt_format_marker_option_validation",
    "meta_prompt_parent_placeholder_retention",
    "prompt_program_identity",
    "template_sha256_identity",
    "duplicate_prompt_arm_identity_policy",
    "role_specific_template_compatibility_matrix",
    "mutation_runtime_role_compatibility_policy",
    "critique_prompt_template_compatibility_policy",
    "feedback_prompt_template_compatibility_policy",
    "meta_prompt_call_surface_compatibility_policy",
    "context_policy_compatibility_matrix",
    "duplicate_arm_semantic_equivalence_audit",
    "prompt_template_dedup_design",
    "human_reviewed_role_surface_fixtures",
)
EXPECTED_MISSING_EVIDENCE = {
    "role_specific_template_compatibility_matrix": "not_recorded_locally",
    "mutation_runtime_role_compatibility_policy": "not_recorded_locally",
    "critique_prompt_template_compatibility_policy": "not_recorded_locally",
    "feedback_prompt_template_compatibility_policy": "not_recorded_locally",
    "meta_prompt_call_surface_compatibility_policy": "not_recorded_locally",
    "context_policy_compatibility_matrix": "not_recorded_locally",
    "duplicate_arm_semantic_equivalence_audit": "not_recorded_locally",
    "prompt_template_dedup_design": "not_recorded_locally",
    "human_reviewed_role_surface_fixtures": "not_recorded_locally",
}


@dataclass(frozen=True)
class PromptTemplateCompatibilityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class PromptTemplateCompatibilityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[PromptTemplateCompatibilityBoundaryIssue]


def prompt_template_compatibility_boundary_record() -> dict[str, Any]:
    """Return the prompt-template validation versus role-compatibility boundary."""

    return {
        "schema": PROMPT_TEMPLATE_COMPATIBILITY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve builds prompts from task instructions, previous "
            "programs, evaluator feedback, and stochastic prompt templates; "
            "templates must remain compatible with the prompt roles and "
            "context channels that consume them"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "prompt_template_error_type": "PromptTemplateError",
        "prompt_program_log": "prompt_history.jsonl",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "duplicate_arm_policy": {
            "status": "independent_prompt_arms_preserved",
            "identity_fields": ["id", "template_sha256"],
            "semantic_deduplication": "not_performed",
        },
        "claim_boundary": (
            "This boundary records that LibreEvolve validates known simple "
            "prompt placeholders, dry-runs template formatting, validates "
            "configured AlphaEvolve-style mutation-channel requirements, "
            "checks prompt-format fragments and markers, preserves parent "
            "placeholders for evolved prompt children, records prompt-program "
            "identity, records template_sha256 identity, and intentionally "
            "preserves duplicate prompt text as independent prompt arms. It "
            "does not claim a role-specific template compatibility matrix, "
            "mutation runtime role compatibility policy, critique prompt "
            "template compatibility policy, feedback prompt template "
            "compatibility policy, meta-prompt call-surface compatibility "
            "policy, context-policy compatibility matrix, duplicate-arm "
            "semantic equivalence audit, prompt-template dedup design, or "
            "human-reviewed role-surface fixtures."
        ),
    }


def validate_prompt_template_compatibility_boundary(
    boundary: object | str | Path | None = None,
) -> PromptTemplateCompatibilityBoundaryValidation:
    data, read_issues = _load_boundary(
        prompt_template_compatibility_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return PromptTemplateCompatibilityBoundaryValidation(
            False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[PromptTemplateCompatibilityBoundaryIssue] = []
    if data.get("schema") != PROMPT_TEMPLATE_COMPATIBILITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported prompt-template compatibility boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.2 and 2.3"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "stochastic prompt templates" not in source_claim
        or "prompt roles and context channels" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify prompt templates plus role/context compatibility"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("prompt_template_error_type") != "PromptTemplateError":
        issues.append(_issue("invalid_prompt_template_error_type", "prompt_template_error_type must be PromptTemplateError"))
    if data.get("prompt_program_log") != "prompt_history.jsonl":
        issues.append(_issue("invalid_prompt_program_log", "prompt_program_log must be prompt_history.jsonl"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "prompt-template compatibility boundary must not claim role-specific compatibility readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    _validate_duplicate_arm_policy(data.get("duplicate_arm_policy"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a role-specific template compatibility matrix" not in boundary_text
        or "critique prompt template compatibility policy" not in boundary_text
        or "duplicate-arm semantic equivalence audit" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate generic validation and duplicate-arm identity from role-specific compatibility"))
    return PromptTemplateCompatibilityBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_prompt_template_compatibility_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_prompt_template_compatibility_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Prompt-template compatibility boundary",
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
) -> tuple[dict[str, Any] | None, list[PromptTemplateCompatibilityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "prompt-template compatibility boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[PromptTemplateCompatibilityBoundaryIssue],
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
    issues: list[PromptTemplateCompatibilityBoundaryIssue],
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


def _validate_duplicate_arm_policy(
    value: object,
    issues: list[PromptTemplateCompatibilityBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_duplicate_arm_policy", "duplicate_arm_policy must be an object"))
        return
    if value.get("status") != "independent_prompt_arms_preserved":
        issues.append(_issue("invalid_duplicate_arm_policy_status", "duplicate_arm_policy.status must preserve independent prompt arms"))
    if value.get("identity_fields") != ["id", "template_sha256"]:
        issues.append(_issue("invalid_duplicate_arm_identity_fields", "duplicate_arm_policy.identity_fields must be id/template_sha256"))
    if value.get("semantic_deduplication") != "not_performed":
        issues.append(_issue("invalid_duplicate_arm_semantic_deduplication", "duplicate_arm_policy.semantic_deduplication must be not_performed"))


def _issue(code: str, message: str) -> PromptTemplateCompatibilityBoundaryIssue:
    return PromptTemplateCompatibilityBoundaryIssue(code, message)
