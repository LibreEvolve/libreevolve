from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.llm.ensemble import LLM_PROVIDER_DIAGNOSTICS_SCHEMA

LLM_PROVIDER_DIAGNOSTICS_POLICY = (
    "bounded_retained_call_history_provider_diagnostics"
)
_EXPECTED_STATUS = "snapshot"
_EXPECTED_SOURCE = "LLMEnsemble.call_history"
_HEX_64 = re.compile(r"^[0-9a-f]{64}$")
_REQUIRED_LIMITATIONS = {
    "retained_call_history_window_only",
    "provider_response_error_text_retention_follows_configured_modes",
    "bounded_scalar_provider_diagnostics_not_full_raw_provider_payloads",
    "configured_cost_estimates_not_live_provider_pricing",
}
_TOTAL_COUNT_FIELDS = (
    "call_count",
    "usage_record_count",
    "provider_response_retention_record_count",
    "provider_response_hash_count",
    "provider_response_text_retained_count",
    "provider_response_stored_chars",
    "provider_response_redacted_count",
    "provider_response_truncated_count",
    "provider_error_retention_record_count",
    "provider_error_hash_count",
    "provider_error_text_retained_count",
    "provider_error_stored_chars",
    "provider_error_redacted_count",
    "provider_error_truncated_count",
    "provider_diagnostics_record_count",
    "provider_diagnostic_item_count",
    "provider_diagnostic_omitted_item_count",
    "cost_estimate_count",
    "cost_not_estimated_count",
    "configured_pricing_estimate_count",
    "live_pricing_record_count",
    "backend_defaults_record_count",
)
_BACKEND_COUNT_FIELDS = (
    "calls",
    "successes",
    "failures",
    "usage_record_count",
    "provider_response_retention_record_count",
    "provider_response_hash_count",
    "provider_response_text_retained_count",
    "provider_response_stored_chars",
    "provider_response_redacted_count",
    "provider_response_truncated_count",
    "provider_error_retention_record_count",
    "provider_error_hash_count",
    "provider_error_text_retained_count",
    "provider_error_stored_chars",
    "provider_error_redacted_count",
    "provider_error_truncated_count",
    "provider_diagnostics_record_count",
    "provider_diagnostic_item_count",
    "provider_diagnostic_omitted_item_count",
    "cost_estimate_count",
    "cost_not_estimated_count",
    "configured_pricing_estimate_count",
    "live_pricing_record_count",
    "backend_defaults_record_count",
)
_COUNTER_FIELDS = (
    "provider_response_retention_modes",
    "provider_response_retention_policies",
    "provider_error_retention_modes",
    "provider_error_retention_policies",
    "diagnostic_keys",
    "cost_status_reasons",
    "backend_default_api_modes",
)
_RAW_PAYLOAD_FIELDS = (
    "raw_provider_payloads",
    "full_provider_payloads",
    "provider_native_payloads",
    "raw_payload_replay",
)


@dataclass(frozen=True)
class LLMProviderDiagnosticsIssue:
    code: str
    message: str


@dataclass(frozen=True)
class LLMProviderDiagnosticsValidation:
    ok: bool
    snapshot_ready: bool
    live_pricing_ready: bool
    raw_payload_replay_ready: bool
    backend_count: int
    issues: list[LLMProviderDiagnosticsIssue]


def validate_llm_provider_diagnostics_summary(
    summary: object | str | Path,
) -> LLMProviderDiagnosticsValidation:
    """Validate the manifest-visible LLM provider diagnostics summary."""
    data, read_issues = _load_summary(summary)
    if read_issues:
        return LLMProviderDiagnosticsValidation(False, False, False, False, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[LLMProviderDiagnosticsIssue] = []
    _expect(data, "schema", LLM_PROVIDER_DIAGNOSTICS_SCHEMA, issues)
    _expect(data, "policy", LLM_PROVIDER_DIAGNOSTICS_POLICY, issues)
    _expect(data, "status", _EXPECTED_STATUS, issues)
    _expect(data, "source", _EXPECTED_SOURCE, issues)
    if not isinstance(data.get("call_history_retention"), dict):
        issues.append(
            LLMProviderDiagnosticsIssue(
                "invalid_call_history_retention",
                "call_history_retention must be an object",
            )
        )
    totals = _validate_totals(data.get("totals"), issues)
    backends = _validate_backends(data.get("backends"), issues)
    backend_count = data.get("backend_count")
    if (
        isinstance(backend_count, bool)
        or not isinstance(backend_count, int)
        or backend_count < 0
    ):
        issues.append(
            LLMProviderDiagnosticsIssue(
                "invalid_backend_count",
                "backend_count must be a non-negative integer",
            )
        )
    elif backend_count != len(backends):
        issues.append(
            LLMProviderDiagnosticsIssue(
                "backend_count_mismatch",
                "backend_count must match the backend record count",
            )
        )
    _validate_records_hash(data.get("records_sha256"), backends, issues)
    _validate_limitations(data.get("limitations"), issues)
    _validate_no_raw_payload_claims(data, issues)
    _validate_live_pricing_boundary(totals, backends, issues)
    _validate_configured_pricing_boundary(totals, backends, issues)
    if totals is not None:
        _validate_totals_match_backends(totals, backends, issues)
    return LLMProviderDiagnosticsValidation(
        ok=not issues,
        snapshot_ready=not issues,
        live_pricing_ready=False,
        raw_payload_replay_ready=False,
        backend_count=len(backends),
        issues=issues,
    )


def _load_summary(
    summary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[LLMProviderDiagnosticsIssue]]:
    if isinstance(summary, dict):
        return dict(summary), []
    if isinstance(summary, (str, Path)):
        path = Path(summary)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [
                LLMProviderDiagnosticsIssue(
                    "read_error",
                    f"failed to read provider diagnostics summary: {exc}",
                )
            ]
        except json.JSONDecodeError as exc:
            return None, [
                LLMProviderDiagnosticsIssue(
                    "invalid_json",
                    f"invalid provider diagnostics summary JSON: {exc.msg}",
                )
            ]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [
        LLMProviderDiagnosticsIssue(
            "invalid_shape",
            "provider diagnostics summary must be a JSON object",
        )
    ]


def _validate_totals(
    value: object,
    issues: list[LLMProviderDiagnosticsIssue],
) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        issues.append(
            LLMProviderDiagnosticsIssue(
                "invalid_totals",
                "totals must be an object",
            )
        )
        return None
    _validate_count_fields(value, _TOTAL_COUNT_FIELDS, "totals", issues)
    _validate_counter_fields(value, _COUNTER_FIELDS[:4], "totals", issues)
    return value


def _validate_backends(
    value: object,
    issues: list[LLMProviderDiagnosticsIssue],
) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        issues.append(
            LLMProviderDiagnosticsIssue(
                "invalid_backends",
                "backends must be a list",
            )
        )
        return []
    records: list[dict[str, Any]] = []
    for item in value:
        if not isinstance(item, dict):
            issues.append(
                LLMProviderDiagnosticsIssue(
                    "invalid_backend",
                    "each backend diagnostic record must be an object",
                )
            )
            continue
        records.append(item)
        index = item.get("backend_idx")
        if index is not None and (
            isinstance(index, bool) or not isinstance(index, int) or index < 0
        ):
            issues.append(
                LLMProviderDiagnosticsIssue(
                    "invalid_backend_idx",
                    "backend_idx must be null or a non-negative integer",
                )
            )
        for field in ("backend_name", "api_mode"):
            if not isinstance(item.get(field), str) or not item[field]:
                issues.append(
                    LLMProviderDiagnosticsIssue(
                        f"invalid_{field}",
                        f"{field} must be a non-empty string",
                    )
                )
        _validate_count_fields(item, _BACKEND_COUNT_FIELDS, "backend", issues)
        _validate_counter_fields(item, _COUNTER_FIELDS, "backend", issues)
        calls = item.get("calls")
        successes = item.get("successes")
        failures = item.get("failures")
        if all(
            isinstance(count, int) and not isinstance(count, bool)
            for count in (calls, successes, failures)
        ) and successes + failures > calls:
            issues.append(
                LLMProviderDiagnosticsIssue(
                    "backend_outcome_count_mismatch",
                    "successes plus failures cannot exceed calls",
                )
            )
    return records


def _validate_count_fields(
    data: dict[str, Any],
    fields: tuple[str, ...],
    scope: str,
    issues: list[LLMProviderDiagnosticsIssue],
) -> None:
    for field in fields:
        value = data.get(field)
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            issues.append(
                LLMProviderDiagnosticsIssue(
                    f"invalid_{scope}_{field}",
                    f"{scope}.{field} must be a non-negative integer",
                )
            )


def _validate_counter_fields(
    data: dict[str, Any],
    fields: tuple[str, ...],
    scope: str,
    issues: list[LLMProviderDiagnosticsIssue],
) -> None:
    for field in fields:
        value = data.get(field)
        if not isinstance(value, dict):
            issues.append(
                LLMProviderDiagnosticsIssue(
                    f"invalid_{scope}_{field}",
                    f"{scope}.{field} must be an object counter",
                )
            )
            continue
        for key, count in value.items():
            if not isinstance(key, str) or not key:
                issues.append(
                    LLMProviderDiagnosticsIssue(
                        f"invalid_{scope}_{field}_key",
                        f"{scope}.{field} keys must be non-empty strings",
                    )
                )
            if isinstance(count, bool) or not isinstance(count, int) or count < 0:
                issues.append(
                    LLMProviderDiagnosticsIssue(
                        f"invalid_{scope}_{field}_count",
                        f"{scope}.{field} values must be non-negative integers",
                    )
                )


def _validate_records_hash(
    value: object,
    backends: list[dict[str, Any]],
    issues: list[LLMProviderDiagnosticsIssue],
) -> None:
    if not isinstance(value, str) or not _HEX_64.match(value):
        issues.append(
            LLMProviderDiagnosticsIssue(
                "invalid_records_sha256",
                "records_sha256 must be a lowercase SHA-256 hex digest",
            )
        )
        return
    payload = json.dumps(backends, sort_keys=True, separators=(",", ":"))
    expected = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    if value != expected:
        issues.append(
            LLMProviderDiagnosticsIssue(
                "records_sha256_mismatch",
                "records_sha256 must match the backend record payload",
            )
            )


def _validate_totals_match_backends(
    totals: dict[str, Any],
    backends: list[dict[str, Any]],
    issues: list[LLMProviderDiagnosticsIssue],
) -> None:
    field_pairs = {"call_count": "calls"}
    field_pairs.update(
        {
            field: field
            for field in _TOTAL_COUNT_FIELDS
            if field != "call_count"
        }
    )
    for total_field, backend_field in field_pairs.items():
        total = totals.get(total_field)
        if isinstance(total, bool) or not isinstance(total, int):
            continue
        backend_total = 0
        comparable = True
        for item in backends:
            value = item.get(backend_field)
            if isinstance(value, bool) or not isinstance(value, int):
                comparable = False
                break
            backend_total += value
        if comparable and total != backend_total:
            issues.append(
                LLMProviderDiagnosticsIssue(
                    f"{total_field}_mismatch",
                    f"totals.{total_field} must equal summed backend {backend_field}",
                )
            )

    for field in _COUNTER_FIELDS[:4]:
        counter = totals.get(field)
        if not isinstance(counter, dict):
            continue
        backend_counter: dict[str, int] = {}
        comparable = True
        for item in backends:
            value = item.get(field)
            if not isinstance(value, dict):
                comparable = False
                break
            for key, count in value.items():
                if (
                    not isinstance(key, str)
                    or isinstance(count, bool)
                    or not isinstance(count, int)
                    or count < 0
                ):
                    comparable = False
                    break
                backend_counter[key] = backend_counter.get(key, 0) + count
            if not comparable:
                break
        if comparable and dict(sorted(counter.items())) != dict(sorted(backend_counter.items())):
            issues.append(
                LLMProviderDiagnosticsIssue(
                    f"{field}_mismatch",
                    f"totals.{field} must equal summed backend {field}",
                )
            )


def _validate_limitations(
    value: object,
    issues: list[LLMProviderDiagnosticsIssue],
) -> None:
    if not isinstance(value, list) or not all(
        isinstance(item, str) and item for item in value
    ):
        issues.append(
            LLMProviderDiagnosticsIssue(
                "invalid_limitations",
                "limitations must be a non-empty string list",
            )
        )
        return
    missing = _REQUIRED_LIMITATIONS - set(value)
    if missing:
        issues.append(
            LLMProviderDiagnosticsIssue(
                "missing_required_limitations",
                "provider diagnostics summary must state its retention limits",
            )
        )


def _validate_no_raw_payload_claims(
    data: dict[str, Any],
    issues: list[LLMProviderDiagnosticsIssue],
) -> None:
    for field in _RAW_PAYLOAD_FIELDS:
        if field in data and data[field] not in (False, None, "unsupported"):
            issues.append(
                LLMProviderDiagnosticsIssue(
                    f"invalid_{field}",
                    f"{field} must not claim raw provider payload replay",
                )
            )


def _validate_live_pricing_boundary(
    totals: dict[str, Any] | None,
    backends: list[dict[str, Any]],
    issues: list[LLMProviderDiagnosticsIssue],
) -> None:
    live_counts: list[int] = []
    if totals is not None and isinstance(totals.get("live_pricing_record_count"), int):
        live_counts.append(totals["live_pricing_record_count"])
    for item in backends:
        value = item.get("live_pricing_record_count")
        if isinstance(value, int) and not isinstance(value, bool):
            live_counts.append(value)
    if any(count > 0 for count in live_counts):
        issues.append(
            LLMProviderDiagnosticsIssue(
                "live_pricing_not_supported",
                "current diagnostics policy must not claim live pricing records",
            )
        )


def _validate_configured_pricing_boundary(
    totals: dict[str, Any] | None,
    backends: list[dict[str, Any]],
    issues: list[LLMProviderDiagnosticsIssue],
) -> None:
    records = [item for item in backends]
    if totals is not None:
        records.append(totals)
    for index, record in enumerate(records):
        scope = "totals" if record is totals else f"backend[{index}]"
        cost_count = record.get("cost_estimate_count")
        configured_count = record.get("configured_pricing_estimate_count")
        not_estimated_count = record.get("cost_not_estimated_count")
        reasons = record.get("cost_status_reasons")
        if (
            isinstance(cost_count, int)
            and not isinstance(cost_count, bool)
            and isinstance(configured_count, int)
            and not isinstance(configured_count, bool)
            and configured_count > cost_count
        ):
            issues.append(
                LLMProviderDiagnosticsIssue(
                    "configured_pricing_count_exceeds_cost_estimates",
                    f"{scope}.configured_pricing_estimate_count cannot exceed cost_estimate_count",
                )
            )
        if isinstance(reasons, dict):
            estimated_reason_count = reasons.get(
                "estimated_from_configured_rate_and_provider_total_tokens", 0
            )
            if (
                isinstance(estimated_reason_count, int)
                and not isinstance(estimated_reason_count, bool)
                and isinstance(configured_count, int)
                and not isinstance(configured_count, bool)
                and estimated_reason_count != configured_count
            ):
                issues.append(
                    LLMProviderDiagnosticsIssue(
                        "configured_pricing_reason_count_mismatch",
                        f"{scope}.cost_status_reasons estimated count must match configured pricing estimates",
                    )
                )
            if isinstance(not_estimated_count, int) and not isinstance(
                not_estimated_count, bool
            ):
                not_estimated_reasons = 0
                for reason, count in reasons.items():
                    if reason == "estimated_from_configured_rate_and_provider_total_tokens":
                        continue
                    if isinstance(count, int) and not isinstance(count, bool):
                        not_estimated_reasons += count
                if not_estimated_reasons != not_estimated_count:
                    issues.append(
                        LLMProviderDiagnosticsIssue(
                            "not_estimated_reason_count_mismatch",
                            f"{scope}.cost_status_reasons not-estimated counts must match cost_not_estimated_count",
                        )
                    )


def _expect(
    data: dict[str, Any],
    field: str,
    expected: object,
    issues: list[LLMProviderDiagnosticsIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(
            LLMProviderDiagnosticsIssue(
                f"invalid_{field}",
                f"{field} must be {expected!r}",
            )
        )
