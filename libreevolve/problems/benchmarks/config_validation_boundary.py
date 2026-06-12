from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONFIG_VALIDATION_BOUNDARY_SCHEMA = "libreevolve.config_validation_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "local_effective_config_validation_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "cli_overrides_applied_before_validation",
    "config_dataclass_validation",
    "backend_spec_local_validation",
    "plugin_label_option_validation",
    "program_database_runtime_config_revalidation",
    "manifest_serialization_config_record",
    "provider_credential_presence_preflight",
    "live_provider_model_registry_validation",
    "provider_service_api_version_capture",
    "provider_account_model_availability",
    "provider_default_parameter_capture",
    "plugin_specific_schema_contracts",
)
EXPECTED_MISSING_EVIDENCE = {
    "live_provider_model_registry_validation": "not_recorded_locally",
    "provider_service_api_version_capture": "not_recorded_locally",
    "provider_account_model_availability": "not_recorded_locally",
    "provider_default_parameter_capture": "not_recorded_locally",
    "plugin_specific_schema_contracts": "partial_or_not_recorded_locally",
}


@dataclass(frozen=True)
class ConfigValidationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ConfigValidationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ConfigValidationBoundaryIssue]


def config_validation_boundary_record() -> dict[str, Any]:
    """Return the local effective-config versus live provider boundary."""

    return {
        "schema": CONFIG_VALIDATION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve-scale runs need validated experiment configuration "
            "and compatible model/provider setup before long-running search"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "local_effective_config_validation_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve validates the merged local "
            "effective Config after CLI overrides, validates built-in backend "
            "specs and plugin labels/options locally, revalidates mutable "
            "runtime Config before manifest/run-directory preparation, records "
            "the effective config in manifests, and performs credential-presence "
            "or local client-construction preflight for mutation-capable runs. "
            "It does not claim live provider/model API compatibility, live "
            "provider model-registry validation, provider service/API-version "
            "capture, account model-availability proof, provider default "
            "parameter discovery, or complete plugin-specific schema contracts."
        ),
    }


def validate_config_validation_boundary(
    boundary: object | str | Path | None = None,
) -> ConfigValidationBoundaryValidation:
    data, read_issues = _load_boundary(
        config_validation_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ConfigValidationBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ConfigValidationBoundaryIssue] = []
    if data.get("schema") != CONFIG_VALIDATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported config-validation boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "validated experiment configuration" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify validated experiment configuration"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "local_effective_config_validation_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to local effective config validation"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "config-validation boundary must not claim live provider compatibility"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim live provider/model API compatibility" not in boundary_text
        or "provider service/API-version capture" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate local config validation from live provider compatibility"))
    return ConfigValidationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_config_validation_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_config_validation_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Config validation boundary",
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
) -> tuple[dict[str, Any] | None, list[ConfigValidationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "config-validation boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ConfigValidationBoundaryIssue],
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
    issues: list[ConfigValidationBoundaryIssue],
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


def _issue(code: str, message: str) -> ConfigValidationBoundaryIssue:
    return ConfigValidationBoundaryIssue(code, message)
