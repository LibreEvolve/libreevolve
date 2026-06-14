from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


LLM_STOCHASTIC_REPRODUCIBILITY_BOUNDARY_SCHEMA = (
    "libreevolve.llm_stochastic_reproducibility_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.2", "2.3", "2.4", "4")
EXPECTED_BOUNDARY_STATUS = (
    "request_parameter_telemetry_without_deterministic_provider_replay"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "normalized_request_parameters",
    "prompt_hashes",
    "output_hashes",
    "backend_model_api_mode_telemetry",
    "supported_temperature_top_p_stop_telemetry",
    "supported_seed_field_telemetry",
    "provider_diagnostics_boundary",
    "provider_output_replay_boundary",
    "backend_api_mode_seed_support_matrix",
    "provider_model_revision_stability_records",
    "provider_system_fingerprint_stability_records",
    "repeated_identical_call_fixtures",
    "deterministic_output_replay_contract",
    "same_prompt_same_parameters_output_match_reports",
    "cross_provider_seed_semantics_report",
)
EXPECTED_MISSING_EVIDENCE = {
    "backend_api_mode_seed_support_matrix": "not_recorded_locally",
    "provider_model_revision_stability_records": "not_recorded_locally",
    "provider_system_fingerprint_stability_records": "not_recorded_locally",
    "repeated_identical_call_fixtures": "not_recorded_locally",
    "deterministic_output_replay_contract": "not_recorded_locally",
    "same_prompt_same_parameters_output_match_reports": "not_recorded_locally",
    "cross_provider_seed_semantics_report": "not_recorded_locally",
}


@dataclass(frozen=True)
class LlmStochasticReproducibilityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class LlmStochasticReproducibilityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[LlmStochasticReproducibilityBoundaryIssue]


def llm_stochastic_reproducibility_boundary_record() -> dict[str, Any]:
    """Return the stochastic LLM-generation reproducibility boundary."""

    return {
        "schema": LLM_STOCHASTIC_REPRODUCIBILITY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve repeated experiments and ablations depend on "
            "controlled model calls, seeds, and budgets, but request-"
            "parameter logging is not by itself proof that stochastic provider "
            "sampling behavior is replayable or deterministic."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "llm_call_ledger_schema": "libreevolve.llm_call_ledger.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve logs normalized request "
            "parameters, prompt hashes, output hashes, backend/model/API-mode "
            "telemetry, supported temperature/top-p/stop telemetry, supported "
            "seed-field telemetry, provider diagnostics boundaries, and "
            "provider-output replay boundaries. It does not claim a backend/"
            "API-mode seed-support matrix, provider model-revision stability "
            "records, provider system-fingerprint stability records, repeated "
            "identical-call fixtures, a deterministic output replay contract, "
            "same-prompt same-parameter output-match reports, or cross-provider "
            "seed-semantics reports."
        ),
    }


def validate_llm_stochastic_reproducibility_boundary(
    boundary: object | str | Path | None = None,
) -> LlmStochasticReproducibilityBoundaryValidation:
    data, read_issues = _load_boundary(
        llm_stochastic_reproducibility_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return LlmStochasticReproducibilityBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[LlmStochasticReproducibilityBoundaryIssue] = []
    if data.get("schema") != LLM_STOCHASTIC_REPRODUCIBILITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported stochastic reproducibility boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.2, 2.3, 2.4, and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "controlled model calls" not in source_claim
        or "request-parameter logging" not in source_claim
        or "replayable or deterministic" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must separate request telemetry from deterministic replay"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("llm_call_ledger_schema") != "libreevolve.llm_call_ledger.v1":
        issues.append(_issue("invalid_llm_call_ledger_schema", "llm call ledger schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "stochastic reproducibility boundary must not claim deterministic provider replay readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a backend/API-mode seed-support matrix" not in boundary_text
        or "repeated identical-call fixtures" not in boundary_text
        or "same-prompt same-parameter output-match reports" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate request telemetry from deterministic provider replay evidence"))
    return LlmStochasticReproducibilityBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_llm_stochastic_reproducibility_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_llm_stochastic_reproducibility_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "LLM stochastic reproducibility boundary",
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
) -> tuple[dict[str, Any] | None, list[LlmStochasticReproducibilityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "stochastic reproducibility boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[LlmStochasticReproducibilityBoundaryIssue],
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
    issues: list[LlmStochasticReproducibilityBoundaryIssue],
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


def _issue(code: str, message: str) -> LlmStochasticReproducibilityBoundaryIssue:
    return LlmStochasticReproducibilityBoundaryIssue(code, message)
