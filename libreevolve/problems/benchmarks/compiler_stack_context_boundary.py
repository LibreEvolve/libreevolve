from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


COMPILER_STACK_CONTEXT_BOUNDARY_SCHEMA = (
    "libreevolve.compiler_stack_context_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("3.3.4",)
EXPECTED_BOUNDARY_STATUS = "metadata_contract_without_real_flashattention_stack_artifacts"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "systems_result_compiler_domain_gate",
    "compiler_stack_provenance_metadata_contract",
    "compiler_ir_reference_check_prerequisite_boundary",
    "workload_model_configuration_record",
    "flashattention_kernel_identity",
    "pallas_kernel_source_artifact",
    "jax_preprocessing_wrapper_artifact",
    "jax_postprocessing_wrapper_artifact",
    "xla_lowering_stage_record",
    "hardware_target_record",
    "lowered_ir_artifact",
    "optimization_decision_category_evidence",
    "memory_access_orchestration_evidence",
    "computation_scheduling_evidence",
    "stack_artifact_refs",
)
EXPECTED_MISSING_EVIDENCE = {
    "workload_model_configuration_record": "not_recorded_locally",
    "flashattention_kernel_identity": "not_recorded_locally",
    "pallas_kernel_source_artifact": "not_recorded_locally",
    "jax_preprocessing_wrapper_artifact": "not_recorded_locally",
    "jax_postprocessing_wrapper_artifact": "not_recorded_locally",
    "xla_lowering_stage_record": "not_recorded_locally",
    "hardware_target_record": "not_recorded_locally",
    "lowered_ir_artifact": "not_recorded_locally",
    "optimization_decision_category_evidence": "not_recorded_locally",
    "memory_access_orchestration_evidence": "not_recorded_locally",
    "computation_scheduling_evidence": "not_recorded_locally",
    "stack_artifact_refs": "not_recorded_locally",
}


@dataclass(frozen=True)
class CompilerStackContextBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CompilerStackContextBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CompilerStackContextBoundaryIssue]


def compiler_stack_context_boundary_record() -> dict[str, Any]:
    """Return the FlashAttention compiler-stack context artifact boundary."""

    return {
        "schema": COMPILER_STACK_CONTEXT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 3.3.4 places the optimized "
            "compiler-generated FlashAttention code inside a Pallas/JAX/XLA "
            "stack for a high-impact GPU inference configuration, with "
            "optimization targeting memory-access orchestration or computation "
            "scheduling."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "systems_result_schema": "libreevolve.systems_result_report.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can validate "
            "compiler_stack_provenance metadata for workload/model "
            "configuration, FlashAttention/Pallas kernel identity, JAX "
            "pre/postprocessing boundaries, XLA lowering stage, hardware "
            "target, lowered-IR hash, optimization decision category, and "
            "artifact refs. It does not claim real workload/model "
            "configuration records, FlashAttention kernel artifacts, Pallas "
            "kernel source artifacts, JAX preprocessing wrapper artifacts, "
            "JAX postprocessing wrapper artifacts, XLA lowering-stage records, "
            "hardware-target records, lowered-IR artifacts, optimization "
            "decision evidence, memory-access orchestration evidence, "
            "computation-scheduling evidence, or complete stack artifact refs."
        ),
    }


def validate_compiler_stack_context_boundary(
    boundary: object | str | Path | None = None,
) -> CompilerStackContextBoundaryValidation:
    data, read_issues = _load_boundary(
        compiler_stack_context_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CompilerStackContextBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CompilerStackContextBoundaryIssue] = []
    if data.get("schema") != COMPILER_STACK_CONTEXT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported compiler stack context boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 3.3.4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "FlashAttention" not in source_claim
        or "Pallas/JAX/XLA" not in source_claim
        or "memory-access orchestration or computation scheduling" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify FlashAttention stack and decision-category claims"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("systems_result_schema") != "libreevolve.systems_result_report.v1":
        issues.append(_issue("invalid_systems_result_schema", "systems result schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "compiler stack context boundary must not claim artifact readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim real workload/model configuration records" not in boundary_text
        or "lowered-IR artifacts" not in boundary_text
        or "memory-access orchestration evidence" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate compiler-stack metadata from real stack artifacts"))
    return CompilerStackContextBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_compiler_stack_context_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_compiler_stack_context_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Compiler stack context boundary",
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
) -> tuple[dict[str, Any] | None, list[CompilerStackContextBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "compiler stack context boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[CompilerStackContextBoundaryIssue],
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
    issues: list[CompilerStackContextBoundaryIssue],
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


def _issue(code: str, message: str) -> CompilerStackContextBoundaryIssue:
    return CompilerStackContextBoundaryIssue(code, message)
