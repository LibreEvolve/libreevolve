from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROVIDER_CANCELLATION_BOUNDARY_SCHEMA = (
    "libreevolve.provider_cancellation_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.4", "2.6")
EXPECTED_BOUNDARY_STATUS = "policy_and_audit_without_live_hard_cancellation"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "provider_request_timeout_rules",
    "ensemble_wait_deadline_rules",
    "runtime_deadline_rules",
    "declared_hard_cancellation_rules",
    "role_scoped_budget_actions",
    "artifact_kind_requirements",
    "cancellation_record_artifact_gate",
    "hashed_artifact_inventory",
    "runtime_readiness_false_fields",
    "provider_cancellation_observations",
    "timeout_failure_call_records",
    "cancellation_record_ledger_replay",
    "role_backend_quarantine_observations",
    "provider_failure_policy_summary",
    "live_provider_sdk_cancellation",
    "in_flight_cancellation_handles",
    "timeout_driven_stop_enforcement",
    "cross_run_provider_quarantine_resume",
    "richer_role_specific_timeout_artifacts",
    "provider_output_raw_payload_replay",
)
EXPECTED_MISSING_EVIDENCE = {
    "live_provider_sdk_cancellation": "not_recorded_locally",
    "in_flight_cancellation_handles": "not_recorded_locally",
    "timeout_driven_stop_enforcement": "not_recorded_locally",
    "cross_run_provider_quarantine_resume": "not_recorded_locally",
    "richer_role_specific_timeout_artifacts": "not_recorded_locally",
    "provider_output_raw_payload_replay": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProviderCancellationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProviderCancellationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ProviderCancellationBoundaryIssue]


def provider_cancellation_boundary_record() -> dict[str, Any]:
    """Return the provider cancellation policy versus live cancellation boundary."""

    return {
        "schema": PROVIDER_CANCELLATION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve-style long budgeted searches need provider calls, "
            "timeouts, retries, and cancellation behavior to be attributable "
            "to the controller's compute budget"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "policy_schema": "libreevolve.provider_cancellation_policy.v1",
        "artifact_inventory_schema": (
            "libreevolve.provider_cancellation_artifact_inventory.v1"
        ),
        "runtime_readiness_schema": (
            "libreevolve.provider_cancellation_runtime_readiness.v1"
        ),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has validated provider "
            "request timeout rules, ensemble wait deadline rules, runtime "
            "deadline rules, declared hard-cancellation rules, role-scoped "
            "budget actions, artifact-kind requirements, a cancellation-record "
            "artifact gate, hashed artifact inventory checks, runtime readiness "
            "false fields, provider-cancellation observations, timeout failure "
            "call records, cancellation-record ledger replay, role/backend "
            "quarantine observations, and provider failure-policy summaries. "
            "It does not claim live provider SDK cancellation, in-flight "
            "cancellation handles, timeout-driven stop enforcement, cross-run "
            "provider quarantine resume, richer role-specific timeout artifacts, "
            "or provider-output raw-payload replay."
        ),
    }


def validate_provider_cancellation_boundary(
    boundary: object | str | Path | None = None,
) -> ProviderCancellationBoundaryValidation:
    data, read_issues = _load_boundary(
        provider_cancellation_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ProviderCancellationBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ProviderCancellationBoundaryIssue] = []
    if data.get("schema") != PROVIDER_CANCELLATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported provider cancellation boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.4 and 2.6"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "provider calls" not in source_claim
        or "cancellation behavior" not in source_claim
        or "compute budget" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify provider cancellation and compute-budget attribution"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    _validate_schema_field(data, "policy_schema", "libreevolve.provider_cancellation_policy.v1", issues)
    _validate_schema_field(data, "artifact_inventory_schema", "libreevolve.provider_cancellation_artifact_inventory.v1", issues)
    _validate_schema_field(data, "runtime_readiness_schema", "libreevolve.provider_cancellation_runtime_readiness.v1", issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "provider cancellation boundary must not claim live hard-cancellation readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim live provider SDK cancellation" not in boundary_text
        or "timeout-driven stop enforcement" not in boundary_text
        or "provider-output raw-payload replay" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate policy evidence from live cancellation readiness"))
    return ProviderCancellationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_provider_cancellation_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_provider_cancellation_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Provider cancellation boundary",
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
) -> tuple[dict[str, Any] | None, list[ProviderCancellationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "provider cancellation boundary must be a JSON object")]


def _validate_schema_field(
    data: dict[str, Any],
    field: str,
    expected: str,
    issues: list[ProviderCancellationBoundaryIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(_issue(f"invalid_{field}", f"{field} must be {expected}"))


def _validate_required_fields(
    value: object,
    issues: list[ProviderCancellationBoundaryIssue],
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
    issues: list[ProviderCancellationBoundaryIssue],
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


def _issue(code: str, message: str) -> ProviderCancellationBoundaryIssue:
    return ProviderCancellationBoundaryIssue(code, message)
