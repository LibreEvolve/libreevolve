from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROVIDER_CAPABILITY_LOOKUP_POLICY_SCHEMA = (
    "libreevolve.provider_capability_lookup_policy.v1"
)
PROVIDER_CAPABILITY_LOOKUP_POLICY = "local_static_validation_no_live_provider_lookup"
_REQUIRED_LOCAL_VALIDATION = {
    "backend_type_and_supported_key_schema",
    "manifest_safe_model_identifier",
    "manifest_safe_client_context_fields",
}
_OPENAI_LOCAL_VALIDATION = {
    "openai_api_mode_enum_and_reasoning_effort_route",
    "openai_model_family_reasoning_effort_static_compatibility",
}


@dataclass(frozen=True)
class ProviderCapabilityIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProviderCapabilityValidation:
    ok: bool
    static_lookup_ready: bool
    live_lookup_ready: bool
    record_count: int
    issues: list[ProviderCapabilityIssue]


def validate_provider_capability_lookup_policy(
    policy: object | str | Path,
) -> ProviderCapabilityValidation:
    """Validate the manifest-visible provider capability lookup boundary."""
    data, read_issues = _load_policy(policy)
    if read_issues:
        return ProviderCapabilityValidation(False, False, False, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ProviderCapabilityIssue] = []
    _expect(data, "schema", PROVIDER_CAPABILITY_LOOKUP_POLICY_SCHEMA, issues)
    _expect(data, "policy", PROVIDER_CAPABILITY_LOOKUP_POLICY, issues)
    _expect(data, "live_lookup", "unsupported", issues)
    _expect(data, "offline_operation", "supported", issues)
    _expect(data, "network_calls_before_run", "none_for_capability_discovery", issues)
    _expect(data, "provider_model_registry", "not_queried", issues)
    _expect(data, "provider_service_api_version", "not_queried", issues)
    _expect(data, "provider_account_availability", "not_checked", issues)
    records = _validate_records(data.get("records"), issues)
    if not isinstance(data.get("remaining_gap"), str) or not data["remaining_gap"].strip():
        issues.append(
            ProviderCapabilityIssue(
                "invalid_remaining_gap",
                "provider capability policy must describe live lookup gaps",
            )
        )
    return ProviderCapabilityValidation(
        ok=not issues,
        static_lookup_ready=not issues,
        live_lookup_ready=False,
        record_count=len(records),
        issues=issues,
    )


def _load_policy(
    policy: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ProviderCapabilityIssue]]:
    if isinstance(policy, dict):
        return dict(policy), []
    if isinstance(policy, (str, Path)):
        path = Path(policy)
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
        except OSError as exc:
            return None, [
                ProviderCapabilityIssue(
                    "read_error",
                    f"failed to read provider capability policy: {exc}",
                )
            ]
        except json.JSONDecodeError as exc:
            return None, [
                ProviderCapabilityIssue(
                    "invalid_json",
                    f"invalid provider capability policy JSON: {exc.msg}",
                )
            ]
        if isinstance(loaded, dict):
            return loaded, []
    return None, [
        ProviderCapabilityIssue(
            "invalid_shape",
            "provider capability policy must be a JSON object",
        )
    ]


def _validate_records(
    value: object,
    issues: list[ProviderCapabilityIssue],
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        issues.append(
            ProviderCapabilityIssue(
                "invalid_records",
                "provider capability records must be a non-empty list",
            )
        )
        return []
    records: list[dict[str, Any]] = []
    seen_indices: set[int] = set()
    for item in value:
        if not isinstance(item, dict):
            issues.append(
                ProviderCapabilityIssue(
                    "invalid_record",
                    "provider capability record must be an object",
                )
            )
            continue
        records.append(item)
        index = item.get("backend_index")
        if isinstance(index, bool) or not isinstance(index, int) or index < 0:
            issues.append(
                ProviderCapabilityIssue(
                    "invalid_backend_index",
                    "backend_index must be a non-negative integer",
                )
            )
        elif index in seen_indices:
            issues.append(
                ProviderCapabilityIssue(
                    "duplicate_backend_index",
                    "provider capability backend_index values must be unique",
                )
            )
        else:
            seen_indices.add(index)
        _validate_record(item, issues)
    return records


def _validate_record(
    record: dict[str, Any],
    issues: list[ProviderCapabilityIssue],
) -> None:
    provider = record.get("provider")
    if not isinstance(provider, str) or not provider:
        issues.append(
            ProviderCapabilityIssue(
                "invalid_provider",
                "provider capability record requires provider",
            )
        )
    if not isinstance(record.get("model"), str) or not record["model"]:
        issues.append(
            ProviderCapabilityIssue(
                "invalid_model",
                "provider capability record requires a model string",
            )
        )
    for field in (
        "live_model_registry_lookup",
        "provider_service_api_version_lookup",
        "provider_account_availability_check",
    ):
        if record.get(field) is not False:
            issues.append(
                ProviderCapabilityIssue(
                    f"invalid_{field}",
                    f"{field} must be false for static-only lookup",
                )
            )
    if record.get("offline_compatible") is not True:
        issues.append(
            ProviderCapabilityIssue(
                "invalid_offline_compatible",
                "offline_compatible must be true",
            )
        )
    local_validation = record.get("local_validation")
    if not isinstance(local_validation, list) or not all(
        isinstance(item, str) and item for item in local_validation
    ):
        issues.append(
            ProviderCapabilityIssue(
                "invalid_local_validation",
                "local_validation must be a non-empty string list",
            )
        )
        return
    local_set = set(local_validation)
    missing = _REQUIRED_LOCAL_VALIDATION - local_set
    if missing:
        issues.append(
            ProviderCapabilityIssue(
                "missing_required_local_validation",
                "provider capability records must include core local checks",
            )
        )
    if provider == "openai":
        if not _OPENAI_LOCAL_VALIDATION <= local_set:
            issues.append(
                ProviderCapabilityIssue(
                    "missing_openai_local_validation",
                    "OpenAI records must include static API-mode compatibility checks",
                )
            )
        if record.get("api_mode_policy_ref") != "policies.openai_api_mode":
            issues.append(
                ProviderCapabilityIssue(
                    "invalid_openai_api_mode_policy_ref",
                    "OpenAI records must reference policies.openai_api_mode",
                )
            )


def _expect(
    data: dict[str, Any],
    field: str,
    expected: object,
    issues: list[ProviderCapabilityIssue],
) -> None:
    if data.get(field) != expected:
        issues.append(
            ProviderCapabilityIssue(
                f"invalid_{field}",
                f"{field} must be {expected!r}",
            )
        )
