from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PRIMARY_PROMPT_ROLE_TELEMETRY_BOUNDARY_SCHEMA = (
    "libreevolve.primary_prompt_role_telemetry_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.2",)
EXPECTED_RUNTIME_REPORT_SCHEMA = "libreevolve.primary_prompt_instruction_report.v1"
EXPECTED_BOUNDARY_STATUS = (
    "hash_only_prompt_role_policy_join_without_provider_payload_parity"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "primary_prompt_instruction_report_schema",
    "mutation_call_id_join",
    "prompt_role_policy_join_count",
    "single_user_message_policy_shape",
    "configured_structured_messages_policy_shape",
    "hash_only_instruction_metadata",
    "prompt_role_policy_validation_gate",
    "provider_message_policy_boundary",
    "claim_readiness_provider_prompt_role_policy_joined",
    "provider_family_payload_shape_audit",
    "provider_specific_message_transcript",
    "all_generated_prompt_call_ledger_outer_join",
    "role_separated_provider_message_parity",
    "full_alphaevolve_primary_prompt_parity",
)
EXPECTED_MISSING_EVIDENCE = {
    "provider_family_payload_shape_audit": "not_recorded_locally",
    "provider_specific_message_transcript": "not_recorded_locally",
    "all_generated_prompt_call_ledger_outer_join": "not_recorded_locally",
    "role_separated_provider_message_parity": "not_recorded_locally",
    "full_alphaevolve_primary_prompt_parity": "not_recorded_locally",
}


@dataclass(frozen=True)
class PrimaryPromptRoleTelemetryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class PrimaryPromptRoleTelemetryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[PrimaryPromptRoleTelemetryBoundaryIssue]


def primary_prompt_role_telemetry_boundary_record() -> dict[str, Any]:
    """Return the primary-prompt prompt-role telemetry join boundary."""

    return {
        "schema": PRIMARY_PROMPT_ROLE_TELEMETRY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve primary prompts include task instructions, prior "
            "solutions, and system-level prompt instructions; provider message "
            "role placement must be attributable alongside prompt ingredients"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_join_status": "prompt_role_policy_joined_when_call_telemetry_present",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "joined_policy_shapes": {
            "single_user_message": {
                "message_roles": ["user"],
                "instruction_fields": [],
                "instruction_metadata": {},
            },
            "configured_structured_messages": {
                "message_roles": ["system", "developer", "user"],
                "instruction_fields": ["system", "developer"],
                "instruction_metadata_retention": "hash_only",
            },
        },
        "claim_boundary": (
            "This boundary records that primary-prompt instruction reports can "
            "join mutation call ids to hash-only prompt_role_policy telemetry, "
            "count prompt_role_policy joins, distinguish single-user-message "
            "and configured-structured-message policy shapes, validate joined "
            "instruction metadata hashes, and keep provider message policy "
            "readiness explicit. It does not claim provider-family payload "
            "shape audit, provider-specific message transcripts, an all-"
            "generated-prompt call-ledger outer join, role-separated provider "
            "message parity, or full AlphaEvolve primary-prompt parity."
        ),
    }


def validate_primary_prompt_role_telemetry_boundary(
    boundary: object | str | Path | None = None,
) -> PrimaryPromptRoleTelemetryBoundaryValidation:
    data, read_issues = _load_boundary(
        primary_prompt_role_telemetry_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return PrimaryPromptRoleTelemetryBoundaryValidation(
            False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[PrimaryPromptRoleTelemetryBoundaryIssue] = []
    if data.get("schema") != PRIMARY_PROMPT_ROLE_TELEMETRY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported primary-prompt role telemetry boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.2"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "system-level prompt instructions" not in source_claim
        or "provider message role placement" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify system instructions and provider role placement"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("runtime_join_status") != "prompt_role_policy_joined_when_call_telemetry_present":
        issues.append(_issue("invalid_runtime_join_status", "runtime_join_status must stay scoped to present call telemetry"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "primary-prompt role telemetry boundary must not claim provider payload parity"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    _validate_joined_policy_shapes(data.get("joined_policy_shapes"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "hash-only prompt_role_policy telemetry" not in boundary_text
        or "does not claim provider-family payload shape audit" not in boundary_text
        or "full AlphaEvolve primary-prompt parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate hash-only telemetry joins from provider payload parity"))
    return PrimaryPromptRoleTelemetryBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_primary_prompt_role_telemetry_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_primary_prompt_role_telemetry_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Primary-prompt role telemetry boundary",
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
) -> tuple[dict[str, Any] | None, list[PrimaryPromptRoleTelemetryBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "primary-prompt role telemetry boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[PrimaryPromptRoleTelemetryBoundaryIssue],
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
    issues: list[PrimaryPromptRoleTelemetryBoundaryIssue],
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


def _validate_joined_policy_shapes(
    value: object,
    issues: list[PrimaryPromptRoleTelemetryBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_joined_policy_shapes", "joined_policy_shapes must be an object"))
        return
    single = value.get("single_user_message")
    configured = value.get("configured_structured_messages")
    if not isinstance(single, dict) or single.get("message_roles") != ["user"]:
        issues.append(_issue("invalid_single_user_message_shape", "single-user policy shape must record user-only messages"))
    if not isinstance(configured, dict) or configured.get("message_roles") != ["system", "developer", "user"]:
        issues.append(_issue("invalid_configured_structured_messages_shape", "configured policy shape must record system/developer/user messages"))
    if isinstance(configured, dict) and configured.get("instruction_metadata_retention") != "hash_only":
        issues.append(_issue("invalid_instruction_metadata_retention", "configured policy shape must retain instruction metadata as hash_only"))


def _issue(code: str, message: str) -> PrimaryPromptRoleTelemetryBoundaryIssue:
    return PrimaryPromptRoleTelemetryBoundaryIssue(code, message)
