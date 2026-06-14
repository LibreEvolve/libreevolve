from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LINEAGE_REPLAY_BOUNDARY_SCHEMA = "libreevolve.lineage_replay_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.5", "2.6", "4")
EXPECTED_RUNTIME_POLICY_SCHEMA = "libreevolve.lineage_replay_policy.v1"
EXPECTED_BOUNDARY_STATUS = (
    "deterministic_loop_id_policy_without_end_to_end_lineage_replay"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "runtime_lineage_replay_policy_schema",
    "loop_created_seed_candidate_ids",
    "loop_created_generated_candidate_ids",
    "prompt_database_seed_template_ids",
    "prompt_database_mutated_template_ids",
    "ordered_llm_call_ids",
    "direct_program_uuid4_exclusion",
    "direct_prompt_program_uuid4_exclusion",
    "provider_output_non_replay_boundary",
    "runtime_rng_snapshot_linkage",
    "llm_scheduler_snapshot_linkage",
    "archive_snapshot_linkage",
    "prompt_history_replay_linkage",
    "full_resume_bundle_policy_validation",
    "provider_output_replay_in_resumed_trace",
    "controller_pending_work_lineage_state",
    "ordered_migration_lineage_replay",
    "plugin_rng_state_lineage_linkage",
    "validator_rng_state_lineage_linkage",
    "end_to_end_resumed_lineage_trace",
)
EXPECTED_MISSING_EVIDENCE = {
    "provider_output_replay_in_resumed_trace": "not_recorded_locally",
    "controller_pending_work_lineage_state": "not_recorded_locally",
    "ordered_migration_lineage_replay": "not_recorded_locally",
    "plugin_rng_state_lineage_linkage": "not_recorded_locally",
    "validator_rng_state_lineage_linkage": "not_recorded_locally",
    "end_to_end_resumed_lineage_trace": "not_recorded_locally",
}


@dataclass(frozen=True)
class LineageReplayBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class LineageReplayBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[LineageReplayBoundaryIssue]


def lineage_replay_boundary_record() -> dict[str, Any]:
    """Return the lineage replay policy boundary for AlphaEvolve parity."""

    return {
        "schema": LINEAGE_REPLAY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve compares long-running searches, ablations, and "
            "repeated seeds, so lineage replay evidence must distinguish "
            "deterministic loop-owned ids from direct UUID defaults and "
            "provider outputs that are not replayed."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_lineage_replay_policy_schema": EXPECTED_RUNTIME_POLICY_SCHEMA,
        "runtime_report_status": "lineage_replay_policy_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve runtime manifests validate "
            "runtime.lineage_replay_policy, including deterministic "
            "loop-created seed and generated candidate ids, deterministic "
            "PromptDatabase seed and mutated template ids, deterministic "
            "ordered LLM call ids, explicit exclusion of direct Program() and "
            "PromptProgram() UUID4 defaults, provider-output non-replay "
            "metadata, runtime RNG linkage, LLM scheduler linkage, archive "
            "snapshot linkage, prompt-history replay linkage, and full-resume "
            "bundle policy validation. It does not claim provider-output "
            "replay in resumed traces, controller pending-work lineage state, "
            "ordered migration lineage replay, plugin RNG state linkage, "
            "validator RNG state linkage, or end-to-end resumed lineage trace "
            "proof."
        ),
    }


def validate_lineage_replay_boundary(
    boundary: object | str | Path | None = None,
) -> LineageReplayBoundaryValidation:
    data, read_issues = _load_boundary(
        lineage_replay_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return LineageReplayBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[LineageReplayBoundaryIssue] = []
    if data.get("schema") != LINEAGE_REPLAY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported lineage replay boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.5, 2.6, and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "long-running searches" not in source_claim
        or "deterministic loop-owned ids" not in source_claim
        or "provider outputs that are not replayed" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify deterministic ids versus non-replayed provider output"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_lineage_replay_policy_schema") != EXPECTED_RUNTIME_POLICY_SCHEMA:
        issues.append(_issue("invalid_runtime_lineage_replay_policy_schema", f"runtime lineage policy schema must be {EXPECTED_RUNTIME_POLICY_SCHEMA}"))
    if data.get("runtime_report_status") != "lineage_replay_policy_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to lineage replay policy availability"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "lineage replay boundary must not claim end-to-end replay readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "direct Program() and PromptProgram() UUID4 defaults" not in boundary_text
        or "provider-output replay in resumed traces" not in boundary_text
        or "end-to-end resumed lineage trace proof" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate deterministic id policy from full lineage replay proof"))
    return LineageReplayBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_lineage_replay_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_lineage_replay_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Lineage replay boundary",
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
) -> tuple[dict[str, Any] | None, list[LineageReplayBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "lineage replay boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[LineageReplayBoundaryIssue],
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
    issues: list[LineageReplayBoundaryIssue],
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


def _issue(code: str, message: str) -> LineageReplayBoundaryIssue:
    return LineageReplayBoundaryIssue(code, message)
