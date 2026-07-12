from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


GEMINI_PROVIDER_PARITY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_gemini_provider_parity_boundary.v1"
)
GEMINI_PROVIDER_RUNTIME_REPORT_SCHEMA = "libreevolve.gemini_provider_parity_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "first_class_adapter_without_live_alphaevolve_model_parity"
EXPECTED_PROVIDER_REQUIREMENT = "gemini_flash_and_gemini_pro"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "built_in_google_gemini_adapter",
    "gemini_credential_preflight",
    "gemini_client_context_config",
    "gemini_request_parameter_mapping",
    "provider_native_usage_telemetry",
    "provider_native_default_telemetry",
    "provider_native_error_diagnostics",
    "generate_content_completion_contract",
    "provider_capability_lookup",
    "gemini_model_registry_snapshot",
    "gemini_flash_lane_identity",
    "gemini_pro_lane_identity",
    "scheduler_flash_pro_lane_integration",
    "account_model_availability_check",
    "paper_level_substitution_contract",
    "substitution_equivalence_justification",
    "credential_safe_live_flash_pro_smoke",
    "original_gemini_2_0_model_availability",
)
EXPECTED_MISSING_EVIDENCE = {
    "built_in_google_gemini_adapter": "recorded_locally",
    "gemini_credential_preflight": "recorded_locally",
    "gemini_client_context_config": "recorded_locally",
    "gemini_request_parameter_mapping": "recorded_locally",
    "provider_native_usage_telemetry": "recorded_locally",
    "provider_native_default_telemetry": "recorded_locally",
    "provider_native_error_diagnostics": "recorded_locally",
    "generate_content_completion_contract": "recorded_locally",
    "provider_capability_lookup": "not_recorded_locally",
    "gemini_model_registry_snapshot": "not_recorded_locally",
    "gemini_flash_lane_identity": "recorded_locally",
    "gemini_pro_lane_identity": "recorded_locally",
    "scheduler_flash_pro_lane_integration": "recorded_config_contract_without_live_pair_run",
    "account_model_availability_check": "not_recorded_locally",
    "paper_level_substitution_contract": "not_recorded_locally",
    "substitution_equivalence_justification": "not_recorded_locally",
    "credential_safe_live_flash_pro_smoke": "not_recorded_locally",
    "original_gemini_2_0_model_availability": "not_recorded_locally",
}


@dataclass(frozen=True)
class GeminiProviderParityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class GeminiProviderParityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[GeminiProviderParityBoundaryIssue]


def gemini_provider_parity_boundary_record() -> dict[str, Any]:
    """Return the current absence boundary for AlphaEvolve Gemini provider parity."""

    return {
        "schema": GEMINI_PROVIDER_PARITY_BOUNDARY_SCHEMA,
        "runtime_report_schema": GEMINI_PROVIDER_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "alphaevolve_provider_requirement": EXPECTED_PROVIDER_REQUIREMENT,
        "source_claim": (
            "AlphaEvolve's published model mix used Gemini 2.0 Flash and "
            "Gemini 2.0 Pro, so provider parity needs a first-class "
            "Google/Gemini surface or explicit paper-level substitution"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "gemini_provider_partial_readiness_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a first-class Google Gen AI SDK adapter for "
            "the Gemini Developer API, environment credential preflight, API-"
            "version client context, GenerateContent request mapping, prompt-"
            "role system instructions, bounded retry/default/usage/error "
            "telemetry, strict completion-state handling, Flash/Pro lane "
            "classification, and generic scheduler configuration. It does not "
            "claim live Gemini 2.0 Flash/Pro availability, a credential-safe "
            "live pair run, provider capability lookup, model-registry "
            "snapshots, account/model availability checks, calibrated "
            "AlphaEvolve Flash/Pro scheduling, a paper-level substitution "
            "contract, or substitution-equivalence justification."
        ),
    }


def validate_gemini_provider_parity_boundary(
    boundary: object | str | Path | None = None,
) -> GeminiProviderParityBoundaryValidation:
    data, read_issues = _load_boundary(
        gemini_provider_parity_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return GeminiProviderParityBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[GeminiProviderParityBoundaryIssue] = []
    if data.get("schema") != GEMINI_PROVIDER_PARITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Gemini provider parity boundary schema"))
    if data.get("runtime_report_schema") != GEMINI_PROVIDER_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify Gemini provider parity reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("alphaevolve_provider_requirement") != EXPECTED_PROVIDER_REQUIREMENT:
        issues.append(_issue("invalid_provider_requirement", "provider requirement must identify Gemini Flash and Pro"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "Gemini 2.0 Flash" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify Gemini 2.0 Flash/Pro use"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "gemini_provider_partial_readiness_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to partial provider readiness"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Gemini provider boundary must not claim provider parity readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim" not in boundary_text
        or "first-class Google Gen AI SDK adapter" not in boundary_text
        or "live Gemini 2.0 Flash/Pro availability" not in boundary_text
        or "model-registry snapshots" not in boundary_text
        or "calibrated AlphaEvolve Flash/Pro scheduling" not in boundary_text
        or "substitution-equivalence justification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim provider parity"))
    return GeminiProviderParityBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_gemini_provider_parity_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_gemini_provider_parity_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve Gemini provider parity boundary",
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
) -> tuple[dict[str, Any] | None, list[GeminiProviderParityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Gemini provider parity boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[GeminiProviderParityBoundaryIssue],
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
    issues: list[GeminiProviderParityBoundaryIssue],
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
    return sum(value != "recorded_locally" for value in value.values())


def _issue(code: str, message: str) -> GeminiProviderParityBoundaryIssue:
    return GeminiProviderParityBoundaryIssue(code, message)
