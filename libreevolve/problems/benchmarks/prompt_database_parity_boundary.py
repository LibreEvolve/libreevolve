from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROMPT_DATABASE_PARITY_BOUNDARY_SCHEMA = (
    "libreevolve.prompt_database_parity_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.2",)
EXPECTED_BOUNDARY_STATUS = (
    "local_prompt_arm_history_without_solution_database_equivalent_archive"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "prompt_history_jsonl",
    "prompt_history_invalid_jsonl",
    "deterministic_seed_prompt_ids",
    "deterministic_mutated_prompt_ids",
    "prompt_template_sha256_identity",
    "prompt_context_policy_sha256_identity",
    "append_only_add_score_penalty_events",
    "prompt_history_replay",
    "parent_lineage_ids",
    "duplicate_prompt_arm_identity_policy",
    "ucb_style_prompt_arm_selection",
    "prompt_reward_metadata",
    "meta_prompt_template_context_policy_mutation",
    "prompt_side_archive_retention_policy",
    "prompt_descriptor_objective_indexes",
    "prompt_archive_event_stream",
    "prompt_migration_rebin_semantics",
    "prompt_async_controller_resume_state",
    "prompt_database_benchmark_evidence",
)
EXPECTED_MISSING_EVIDENCE = {
    "prompt_side_archive_retention_policy": "not_recorded_locally",
    "prompt_descriptor_objective_indexes": "not_recorded_locally",
    "prompt_archive_event_stream": "not_recorded_locally",
    "prompt_migration_rebin_semantics": "not_recorded_locally",
    "prompt_async_controller_resume_state": "not_recorded_locally",
    "prompt_database_benchmark_evidence": "not_recorded_locally",
}


@dataclass(frozen=True)
class PromptDatabaseParityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class PromptDatabaseParityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[PromptDatabaseParityBoundaryIssue]


def prompt_database_parity_boundary_record() -> dict[str, Any]:
    """Return the PromptDatabase versus solution-database-equivalent boundary."""

    return {
        "schema": PROMPT_DATABASE_PARITY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve co-evolves prompt instructions in a separate database "
            "analogous to the solution-program database; local prompt storage "
            "must not be described as equivalent without archive lifecycle "
            "and benchmark evidence"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_surfaces": {
            "prompt_database_class": "PromptDatabase",
            "prompt_program_class": "PromptProgram",
            "history_stream": "prompt_history.jsonl",
            "quarantine_stream": "prompt_history_invalid.jsonl",
            "selection_policy": "untried_then_ucb_style_mean_reward_plus_exploration",
        },
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve's PromptDatabase has "
            "prompt_history.jsonl, prompt_history_invalid.jsonl, deterministic "
            "seed and mutated prompt ids, template_sha256 identity, "
            "context-policy sha256 identity, append-only add/score/penalty "
            "events, prompt-history replay, parent lineage ids, duplicate-arm "
            "identity policy, UCB-style prompt-arm selection, prompt reward "
            "metadata, and optional meta-prompt template/context-policy "
            "mutation. It does not claim prompt-side archive retention policy, "
            "prompt descriptor/objective indexes, prompt archive-event streams, "
            "prompt migration/rebin semantics, prompt async/controller resume "
            "state, or prompt-database benchmark evidence."
        ),
    }


def validate_prompt_database_parity_boundary(
    boundary: object | str | Path | None = None,
) -> PromptDatabaseParityBoundaryValidation:
    data, read_issues = _load_boundary(
        prompt_database_parity_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return PromptDatabaseParityBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[PromptDatabaseParityBoundaryIssue] = []
    if data.get("schema") != PROMPT_DATABASE_PARITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported prompt-database parity boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.2"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "separate database" not in source_claim
        or "solution-program database" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify separate prompt database and solution-program analogy"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    _validate_runtime_surfaces(data.get("runtime_surfaces"), issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "prompt-database parity boundary must not claim solution-database-equivalent readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim prompt-side archive retention policy" not in boundary_text
        or "prompt descriptor/objective indexes" not in boundary_text
        or "prompt-database benchmark evidence" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate local prompt-arm history from prompt-database parity"))
    return PromptDatabaseParityBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_prompt_database_parity_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_prompt_database_parity_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "PromptDatabase parity boundary",
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
) -> tuple[dict[str, Any] | None, list[PromptDatabaseParityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "prompt-database parity boundary must be a JSON object")]


def _validate_runtime_surfaces(
    value: object,
    issues: list[PromptDatabaseParityBoundaryIssue],
) -> None:
    expected = {
        "prompt_database_class": "PromptDatabase",
        "prompt_program_class": "PromptProgram",
        "history_stream": "prompt_history.jsonl",
        "quarantine_stream": "prompt_history_invalid.jsonl",
        "selection_policy": "untried_then_ucb_style_mean_reward_plus_exploration",
    }
    if value != expected:
        issues.append(_issue("invalid_runtime_surfaces", "runtime_surfaces must identify current PromptDatabase surfaces"))


def _validate_required_fields(
    value: object,
    issues: list[PromptDatabaseParityBoundaryIssue],
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
    issues: list[PromptDatabaseParityBoundaryIssue],
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


def _issue(code: str, message: str) -> PromptDatabaseParityBoundaryIssue:
    return PromptDatabaseParityBoundaryIssue(code, message)
