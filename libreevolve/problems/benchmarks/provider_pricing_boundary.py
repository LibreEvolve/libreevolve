from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROVIDER_PRICING_BOUNDARY_SCHEMA = "libreevolve.provider_pricing_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.6", "4")
EXPECTED_BOUNDARY_STATUS = "configured_cost_estimates_without_live_provider_pricing"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "backend_cost_usd_per_million_tokens",
    "provider_usage_total_tokens",
    "per_call_cost_estimate",
    "cost_estimate_status",
    "runtime_configured_cost_accounting",
    "llm_budget_report_configured_cost",
    "provider_diagnostics_summary",
    "pricing_readiness_schema",
    "configured_pricing_aggregate_checks",
    "cost_status_reason_checks",
    "remote_default_rate_overclaim_checks",
    "backend_default_count_checks",
    "raw_payload_replay_overclaim_checks",
    "live_provider_pricing",
    "provider_default_rate_capture",
    "account_model_specific_pricing",
    "raw_provider_payload_replay",
)
EXPECTED_MISSING_EVIDENCE = {
    "live_provider_pricing": "not_recorded_locally",
    "provider_default_rate_capture": "not_recorded_locally",
    "account_model_specific_pricing": "not_recorded_locally",
    "raw_provider_payload_replay": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProviderPricingBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProviderPricingBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ProviderPricingBoundaryIssue]


def provider_pricing_boundary_record() -> dict[str, Any]:
    """Return the configured-cost versus live-pricing boundary."""

    return {
        "schema": PROVIDER_PRICING_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve-scale LLM scheduling and budget reports need "
            "reproducible cost evidence for the model calls that produced "
            "proposals and feedback"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "pricing_readiness_schema": "libreevolve.llm_provider_pricing_readiness.v1",
        "diagnostics_schema": "libreevolve.llm_provider_diagnostics.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has configured "
            "cost_usd_per_million_tokens backend metadata, provider usage "
            "total_tokens, per-call configured cost_estimate records, "
            "cost_estimate_status records, runtime configured-cost accounting, "
            "LLM budget report configured-cost totals, provider diagnostics "
            "summaries, pricing-readiness false fields, configured-pricing "
            "aggregate checks, cost-status reason checks, remote default-rate "
            "overclaim checks, backend-default count checks, and raw-payload "
            "replay overclaim checks. It does not claim live provider pricing, "
            "provider default-rate capture, account/model-specific pricing, or "
            "raw provider-payload replay."
        ),
    }


def validate_provider_pricing_boundary(
    boundary: object | str | Path | None = None,
) -> ProviderPricingBoundaryValidation:
    data, read_issues = _load_boundary(
        provider_pricing_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ProviderPricingBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ProviderPricingBoundaryIssue] = []
    if data.get("schema") != PROVIDER_PRICING_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported provider pricing boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.6 and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "reproducible cost evidence" not in source_claim
        or "proposals and feedback" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify reproducible model-call cost evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    _validate_schema_field(data, "pricing_readiness_schema", "libreevolve.llm_provider_pricing_readiness.v1", issues)
    _validate_schema_field(data, "diagnostics_schema", "libreevolve.llm_provider_diagnostics.v1", issues)
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "provider pricing boundary must not claim live pricing readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim live provider pricing" not in boundary_text
        or "provider default-rate capture" not in boundary_text
        or "raw provider-payload replay" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate configured estimates from live pricing and raw replay"))
    return ProviderPricingBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_provider_pricing_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_provider_pricing_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Provider pricing boundary",
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
) -> tuple[dict[str, Any] | None, list[ProviderPricingBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "provider pricing boundary must be a JSON object")]


def _validate_schema_field(
    data: dict[str, Any],
    field: str,
    expected: str,
    issues: list[ProviderPricingBoundaryIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(_issue(f"invalid_{field}", f"{field} must be {expected}"))


def _validate_required_fields(
    value: object,
    issues: list[ProviderPricingBoundaryIssue],
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
    issues: list[ProviderPricingBoundaryIssue],
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


def _issue(code: str, message: str) -> ProviderPricingBoundaryIssue:
    return ProviderPricingBoundaryIssue(code, message)
