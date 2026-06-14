from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HARDWARE_RTL_EDA_EVIDENCE_BOUNDARY_SCHEMA = (
    "libreevolve.hardware_rtl_eda_evidence_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("3.3.3",)
EXPECTED_BOUNDARY_STATUS = "metadata_contract_without_real_rtl_eda_artifacts"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "systems_result_hardware_domain_gate",
    "hardware_rtl_eda_provenance_metadata_contract",
    "claim_calibration_for_hardware_result",
    "hdl_language_identity",
    "exact_rtl_module_or_arithmetic_circuit_identity",
    "source_rtl_or_verilog_artifact",
    "modified_rtl_or_verilog_artifact",
    "synthesis_or_place_and_route_toolchain_run",
    "ppa_metric_output_artifacts",
    "timing_constraint_artifacts",
    "power_area_constraint_artifacts",
    "equivalence_check_logs",
    "formal_verification_logs",
    "robust_verification_method_identity",
    "designer_validation_signoff",
    "downstream_synthesis_confirmation_artifact",
    "rtl_flow_stage_timing_evidence",
    "standard_language_trust_adoption_evidence",
    "upcoming_tpu_integration_target",
    "deployment_time_to_market_evidence",
    "artifact_hashes_and_refs",
)
EXPECTED_MISSING_EVIDENCE = {
    "exact_rtl_module_or_arithmetic_circuit_identity": "not_recorded_locally",
    "source_rtl_or_verilog_artifact": "not_recorded_locally",
    "modified_rtl_or_verilog_artifact": "not_recorded_locally",
    "synthesis_or_place_and_route_toolchain_run": "not_recorded_locally",
    "ppa_metric_output_artifacts": "not_recorded_locally",
    "timing_constraint_artifacts": "not_recorded_locally",
    "power_area_constraint_artifacts": "not_recorded_locally",
    "equivalence_check_logs": "not_recorded_locally",
    "formal_verification_logs": "not_recorded_locally",
    "robust_verification_method_identity": "not_recorded_locally",
    "designer_validation_signoff": "not_recorded_locally",
    "downstream_synthesis_confirmation_artifact": "not_recorded_locally",
    "rtl_flow_stage_timing_evidence": "not_recorded_locally",
    "standard_language_trust_adoption_evidence": "not_recorded_locally",
    "upcoming_tpu_integration_target": "not_recorded_locally",
    "deployment_time_to_market_evidence": "not_recorded_locally",
    "artifact_hashes_and_refs": "not_recorded_locally",
}


@dataclass(frozen=True)
class HardwareRtlEdaEvidenceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class HardwareRtlEdaEvidenceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[HardwareRtlEdaEvidenceBoundaryIssue]


def hardware_rtl_eda_evidence_boundary_record() -> dict[str, Any]:
    """Return the hardware RTL/EDA artifact-evidence boundary."""

    return {
        "schema": HARDWARE_RTL_EDA_EVIDENCE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 3.3.3 reports a Verilog RTL rewrite for a "
            "TPU arithmetic circuit that reduced power and area while "
            "preserving functionality; it says the final proposal passed "
            "robust verification, was validated by TPU designers, was later "
            "found by downstream synthesis tools, and was useful at the RTL "
            "stage before integration into an upcoming TPU."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "systems_result_schema": "libreevolve.systems_result_report.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can validate a hardware "
            "domain gate, hardware_rtl_eda_provenance metadata, and hardware "
            "claim-calibration records. It does not claim exact RTL module or "
            "arithmetic-circuit identity, real source or modified Verilog/RTL "
            "artifacts, synthesis or place-and-route runs, PPA output "
            "artifacts, timing/power/area constraints, equivalence-check "
            "logs, formal-verification logs, robust verification method "
            "identity, designer validation signoff, downstream synthesis "
            "confirmation artifacts, RTL-stage timing evidence, "
            "standard-language trust or adoption evidence, upcoming-TPU "
            "integration target evidence, deployment or time-to-market "
            "evidence, or complete artifact hashes and refs."
        ),
    }


def validate_hardware_rtl_eda_evidence_boundary(
    boundary: object | str | Path | None = None,
) -> HardwareRtlEdaEvidenceBoundaryValidation:
    data, read_issues = _load_boundary(
        hardware_rtl_eda_evidence_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return HardwareRtlEdaEvidenceBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[HardwareRtlEdaEvidenceBoundaryIssue] = []
    if data.get("schema") != HARDWARE_RTL_EDA_EVIDENCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported hardware RTL/EDA boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 3.3.3"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "Verilog RTL rewrite" not in source_claim
        or "robust verification" not in source_claim
        or "downstream synthesis tools" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify RTL rewrite, verification, and downstream synthesis claims"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("systems_result_schema") != "libreevolve.systems_result_report.v1":
        issues.append(_issue("invalid_systems_result_schema", "systems result schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "hardware RTL/EDA boundary must not claim artifact readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim exact RTL module" not in boundary_text
        or "formal-verification logs" not in boundary_text
        or "deployment or time-to-market evidence" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate metadata from real RTL/EDA evidence"))
    return HardwareRtlEdaEvidenceBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_hardware_rtl_eda_evidence_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_hardware_rtl_eda_evidence_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Hardware RTL/EDA evidence boundary",
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
) -> tuple[dict[str, Any] | None, list[HardwareRtlEdaEvidenceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "hardware RTL/EDA boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[HardwareRtlEdaEvidenceBoundaryIssue],
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
    issues: list[HardwareRtlEdaEvidenceBoundaryIssue],
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


def _issue(code: str, message: str) -> HardwareRtlEdaEvidenceBoundaryIssue:
    return HardwareRtlEdaEvidenceBoundaryIssue(code, message)
