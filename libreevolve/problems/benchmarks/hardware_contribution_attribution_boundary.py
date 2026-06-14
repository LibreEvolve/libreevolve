from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HARDWARE_CONTRIBUTION_ATTRIBUTION_BOUNDARY_SCHEMA = (
    "libreevolve.hardware_contribution_attribution_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("3.3.3",)
EXPECTED_BOUNDARY_STATUS = "metadata_contract_without_gemini_tpu_attribution_artifacts"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "systems_result_hardware_domain_gate",
    "hardware_contribution_provenance_metadata_contract",
    "hardware_rtl_eda_prerequisite_boundary",
    "hardware_rewrite_prerequisite_boundary",
    "gemini_model_family_identity",
    "alphaevolve_run_identity",
    "producing_backend_identity",
    "reviewed_tpu_generation_identity",
    "reviewed_arithmetic_circuit_identity",
    "contribution_novelty_basis",
    "first_direct_contribution_scope",
    "integration_milestone_record",
    "integration_milestone_confirmation",
    "hardware_review_signoff_file",
    "synthesis_rediscovery_audit_artifact",
    "rediscovery_caveat_record",
    "gemini_family_confirmation",
    "alphaevolve_mediation_confirmation",
    "artifact_refs",
)
EXPECTED_MISSING_EVIDENCE = {
    "gemini_model_family_identity": "not_recorded_locally",
    "alphaevolve_run_identity": "not_recorded_locally",
    "producing_backend_identity": "not_recorded_locally",
    "reviewed_tpu_generation_identity": "not_recorded_locally",
    "reviewed_arithmetic_circuit_identity": "not_recorded_locally",
    "contribution_novelty_basis": "not_recorded_locally",
    "first_direct_contribution_scope": "not_recorded_locally",
    "integration_milestone_record": "not_recorded_locally",
    "integration_milestone_confirmation": "not_recorded_locally",
    "hardware_review_signoff_file": "not_recorded_locally",
    "synthesis_rediscovery_audit_artifact": "not_recorded_locally",
    "rediscovery_caveat_record": "not_recorded_locally",
    "gemini_family_confirmation": "not_recorded_locally",
    "alphaevolve_mediation_confirmation": "not_recorded_locally",
    "artifact_refs": "not_recorded_locally",
}


@dataclass(frozen=True)
class HardwareContributionAttributionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class HardwareContributionAttributionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[HardwareContributionAttributionBoundaryIssue]


def hardware_contribution_attribution_boundary_record() -> dict[str, Any]:
    """Return the Gemini-to-TPU hardware contribution attribution boundary."""

    return {
        "schema": HARDWARE_CONTRIBUTION_ATTRIBUTION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 3.3.3 says the hardware improvement was "
            "integrated into an upcoming TPU and represents Gemini's first "
            "direct contribution to TPU arithmetic circuits, achieved via "
            "AlphaEvolve."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "systems_result_schema": "libreevolve.systems_result_report.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can validate "
            "hardware_contribution_provenance metadata and can link it to the "
            "RTL/EDA and concrete rewrite prerequisite boundaries. It does not "
            "claim Gemini model-family identity, AlphaEvolve run identity, "
            "producing backend identity, reviewed TPU generation identity, "
            "reviewed arithmetic-circuit identity, contribution novelty or "
            "firstness review evidence, first-direct-contribution scope, "
            "integration milestone records, integration milestone "
            "confirmation, hardware review signoff files, synthesis "
            "rediscovery audit artifacts, rediscovery caveat records, Gemini "
            "family confirmation, AlphaEvolve mediation confirmation, or "
            "complete artifact refs."
        ),
    }


def validate_hardware_contribution_attribution_boundary(
    boundary: object | str | Path | None = None,
) -> HardwareContributionAttributionBoundaryValidation:
    data, read_issues = _load_boundary(
        hardware_contribution_attribution_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return HardwareContributionAttributionBoundaryValidation(
            False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[HardwareContributionAttributionBoundaryIssue] = []
    if data.get("schema") != HARDWARE_CONTRIBUTION_ATTRIBUTION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported hardware contribution attribution boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 3.3.3"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "upcoming TPU" not in source_claim
        or "first direct contribution" not in source_claim
        or "AlphaEvolve" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify upcoming TPU, first-direct-contribution, and AlphaEvolve attribution claims"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("systems_result_schema") != "libreevolve.systems_result_report.v1":
        issues.append(_issue("invalid_systems_result_schema", "systems result schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "hardware contribution attribution boundary must not claim artifact readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim Gemini model-family identity" not in boundary_text
        or "contribution novelty or firstness review evidence" not in boundary_text
        or "synthesis rediscovery audit artifacts" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate contribution metadata from Gemini-to-TPU attribution artifacts"))
    return HardwareContributionAttributionBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_hardware_contribution_attribution_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_hardware_contribution_attribution_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Hardware contribution attribution boundary",
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
) -> tuple[dict[str, Any] | None, list[HardwareContributionAttributionBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "hardware contribution attribution boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[HardwareContributionAttributionBoundaryIssue],
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
    issues: list[HardwareContributionAttributionBoundaryIssue],
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


def _issue(code: str, message: str) -> HardwareContributionAttributionBoundaryIssue:
    return HardwareContributionAttributionBoundaryIssue(code, message)
