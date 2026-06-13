from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROVIDER_DIAGNOSTICS_REPLAY_BOUNDARY_SCHEMA = (
    "libreevolve.provider_diagnostics_replay_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.2", "2.3", "2.4", "4")
EXPECTED_BOUNDARY_STATUS = "bounded_scalar_diagnostics_without_raw_provider_replay"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "provider_usage_metadata",
    "provider_request_response_ids",
    "finish_reason_metadata",
    "adapter_retry_metadata",
    "provider_failure_category",
    "provider_status_code",
    "bounded_provider_diagnostics",
    "backend_defaults_metadata",
    "retained_call_history_window",
    "diagnostics_summary_schema",
    "records_hash",
    "raw_payload_replay_overclaim_checks",
    "remote_provider_defaults_overclaim_checks",
    "backend_default_count_checks",
    "raw_provider_payload_sidecars",
    "provider_output_replay",
    "complete_provider_call_replay",
    "account_model_default_capture",
)
EXPECTED_MISSING_EVIDENCE = {
    "raw_provider_payload_sidecars": "not_recorded_locally",
    "provider_output_replay": "not_recorded_locally",
    "complete_provider_call_replay": "not_recorded_locally",
    "account_model_default_capture": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProviderDiagnosticsReplayBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProviderDiagnosticsReplayBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ProviderDiagnosticsReplayBoundaryIssue]


def provider_diagnostics_replay_boundary_record() -> dict[str, Any]:
    """Return the bounded diagnostics versus raw provider replay boundary."""

    return {
        "schema": PROVIDER_DIAGNOSTICS_REPLAY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve-scale provider-call evidence should identify model "
            "calls that produced proposals, LLM feedback, and meta-prompt "
            "evolution without confusing retained diagnostics with replayable "
            "raw provider outputs; local critique-role diagnostics are extra "
            "runtime telemetry rather than a detailed paper-method surface"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "diagnostics_schema": "libreevolve.llm_provider_diagnostics.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has provider usage "
            "metadata, request/response ids, finish reasons, adapter retry "
            "metadata, provider failure categories, provider status codes, "
            "bounded provider diagnostics, backend defaults metadata, retained "
            "call-history windows, provider-diagnostics summary schema, "
            "records hashes, raw-payload replay overclaim checks, remote "
            "provider-default overclaim checks, and backend-default count "
            "checks. It does not claim raw provider-payload sidecars, provider "
            "output replay, complete provider-call replay, or account/model "
            "default capture."
        ),
    }


def validate_provider_diagnostics_replay_boundary(
    boundary: object | str | Path | None = None,
) -> ProviderDiagnosticsReplayBoundaryValidation:
    data, read_issues = _load_boundary(
        provider_diagnostics_replay_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ProviderDiagnosticsReplayBoundaryValidation(
            False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[ProviderDiagnosticsReplayBoundaryIssue] = []
    if data.get("schema") != PROVIDER_DIAGNOSTICS_REPLAY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported provider diagnostics replay boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.2, 2.3, 2.4, and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "retained diagnostics" not in source_claim
        or "replayable raw provider outputs" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must separate retained diagnostics from replayable raw provider outputs"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("diagnostics_schema") != "libreevolve.llm_provider_diagnostics.v1":
        issues.append(_issue("invalid_diagnostics_schema", "diagnostics_schema must identify runtime provider diagnostics summaries"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "provider diagnostics replay boundary must not claim raw provider replay readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim raw provider-payload sidecars" not in boundary_text
        or "provider output replay" not in boundary_text
        or "complete provider-call replay" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded diagnostics from raw provider replay"))
    return ProviderDiagnosticsReplayBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_provider_diagnostics_replay_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_provider_diagnostics_replay_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Provider diagnostics replay boundary",
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
) -> tuple[dict[str, Any] | None, list[ProviderDiagnosticsReplayBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "provider diagnostics replay boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ProviderDiagnosticsReplayBoundaryIssue],
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
    issues: list[ProviderDiagnosticsReplayBoundaryIssue],
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


def _issue(code: str, message: str) -> ProviderDiagnosticsReplayBoundaryIssue:
    return ProviderDiagnosticsReplayBoundaryIssue(code, message)
