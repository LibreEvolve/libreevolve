from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.systems_results import (
    SYSTEMS_ARTIFACT_INVENTORY_SCHEMA,
    SYSTEMS_EVIDENCE_BUNDLE_SCHEMA,
    SYSTEMS_RESULT_SCHEMA,
)


SYSTEMS_RESULT_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_systems_result_readiness_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("3.3",)
EXPECTED_BOUNDARY_STATUS = "report_contract_without_real_systems_fixtures"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "systems_result_report_schema",
    "systems_result_artifact_inventory_schema",
    "systems_evidence_bundle_schema",
    "optimization_gate_records",
    "heldout_gate_records",
    "reference_correctness_gate_records",
    "passed_gate_artifact_requirements",
    "domain_specific_gate_policy",
    "claim_calibration_records",
    "application_provenance_records",
    "compiler_ir_provenance_records",
    "compiler_stack_provenance_records",
    "compiler_adoption_provenance_records",
    "hardware_rtl_eda_provenance_records",
    "hardware_rewrite_provenance_records",
    "hardware_contribution_provenance_records",
    "scheduling_formulation_records",
    "scheduling_safety_records",
    "scheduling_deployment_readiness_records",
    "real_scheduling_fixture_runs",
    "real_kernel_fixture_runs",
    "real_compiler_fixture_runs",
    "real_hardware_fixture_runs",
    "deployment_measurement_artifacts",
    "expert_confirmation_artifacts",
)
EXPECTED_MISSING_EVIDENCE = {
    "real_scheduling_fixture_runs": "not_recorded_locally",
    "real_kernel_fixture_runs": "not_recorded_locally",
    "real_compiler_fixture_runs": "not_recorded_locally",
    "real_hardware_fixture_runs": "not_recorded_locally",
    "deployment_measurement_artifacts": "not_recorded_locally",
    "expert_confirmation_artifacts": "not_recorded_locally",
    "domain_specific_result_artifacts": "not_recorded_locally",
}


@dataclass(frozen=True)
class SystemsResultReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SystemsResultReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[SystemsResultReadinessBoundaryIssue]


def systems_result_readiness_boundary_record() -> dict[str, Any]:
    """Return the current AlphaEvolve systems-result readiness boundary."""

    return {
        "schema": SYSTEMS_RESULT_READINESS_BOUNDARY_SCHEMA,
        "systems_result_schema": SYSTEMS_RESULT_SCHEMA,
        "artifact_inventory_schema": SYSTEMS_ARTIFACT_INVENTORY_SCHEMA,
        "evidence_bundle_schema": SYSTEMS_EVIDENCE_BUNDLE_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 3.3 systems-result claims used domain-specific "
            "evidence: unseen scheduling workloads, held-out kernel shapes, "
            "randomized compiler reference checks, deployment measurements, "
            "and expert confirmation"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has schemas and validators "
            "for systems result reports, artifact inventories, evidence bundles, "
            "domain-specific gate policy, claim calibration, application "
            "provenance, scheduling readiness, compiler provenance, and hardware "
            "provenance. It does not claim real scheduling, kernel, compiler, "
            "or hardware fixture runs; deployment measurement artifacts; expert "
            "confirmation artifacts; or domain-specific result artifacts."
        ),
    }


def validate_systems_result_readiness_boundary(
    boundary: object | str | Path | None = None,
) -> SystemsResultReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        systems_result_readiness_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SystemsResultReadinessBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[SystemsResultReadinessBoundaryIssue] = []
    if data.get("schema") != SYSTEMS_RESULT_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported systems-result readiness boundary schema"))
    if data.get("systems_result_schema") != SYSTEMS_RESULT_SCHEMA:
        issues.append(_issue("invalid_systems_result_schema", "systems result schema must identify report validation"))
    if data.get("artifact_inventory_schema") != SYSTEMS_ARTIFACT_INVENTORY_SCHEMA:
        issues.append(_issue("invalid_artifact_inventory_schema", "artifact inventory schema must identify systems artifact validation"))
    if data.get("evidence_bundle_schema") != SYSTEMS_EVIDENCE_BUNDLE_SCHEMA:
        issues.append(_issue("invalid_evidence_bundle_schema", "evidence bundle schema must identify systems report/inventory bundles"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['3.3']"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "Section 3.3 systems-result claims" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve systems-result evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "systems-result readiness boundary must not claim real systems-result readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim real" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim real systems evidence"))
    return SystemsResultReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_systems_result_readiness_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_systems_result_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve systems-result readiness boundary",
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
) -> tuple[dict[str, Any] | None, list[SystemsResultReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "systems-result readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[SystemsResultReadinessBoundaryIssue],
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
    issues: list[SystemsResultReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> SystemsResultReadinessBoundaryIssue:
    return SystemsResultReadinessBoundaryIssue(code, message)
