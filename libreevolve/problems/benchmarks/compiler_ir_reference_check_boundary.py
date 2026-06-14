from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


COMPILER_IR_REFERENCE_CHECK_BOUNDARY_SCHEMA = (
    "libreevolve.compiler_ir_reference_check_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("3.3.4",)
EXPECTED_BOUNDARY_STATUS = "metadata_contract_without_real_ir_reference_check_artifacts"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "systems_result_compiler_domain_gate",
    "reference_correctness_gate",
    "compiler_ir_provenance_metadata_contract",
    "ir_origin_and_editability_boundary",
    "compiler_generated_baseline_provenance",
    "reference_implementation_artifact",
    "randomized_input_generator_artifact",
    "candidate_edit_sequence_artifact",
    "per_edit_reference_check_outputs",
    "randomized_input_seed_and_coverage_records",
    "numerical_tolerance_policy_artifact",
    "failure_policy_or_rollback_records",
    "kernel_pre_postprocessing_attribution",
    "edit_artifact_refs",
    "final_expert_all_input_confirmation",
    "expert_or_owner_signoff_file",
)
EXPECTED_MISSING_EVIDENCE = {
    "reference_implementation_artifact": "not_recorded_locally",
    "randomized_input_generator_artifact": "not_recorded_locally",
    "candidate_edit_sequence_artifact": "not_recorded_locally",
    "per_edit_reference_check_outputs": "not_recorded_locally",
    "randomized_input_seed_and_coverage_records": "not_recorded_locally",
    "numerical_tolerance_policy_artifact": "not_recorded_locally",
    "failure_policy_or_rollback_records": "not_recorded_locally",
    "kernel_pre_postprocessing_attribution": "not_recorded_locally",
    "edit_artifact_refs": "not_recorded_locally",
    "final_expert_all_input_confirmation": "not_recorded_locally",
    "expert_or_owner_signoff_file": "not_recorded_locally",
}


@dataclass(frozen=True)
class CompilerIrReferenceCheckBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CompilerIrReferenceCheckBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CompilerIrReferenceCheckBoundaryIssue]


def compiler_ir_reference_check_boundary_record() -> dict[str, Any]:
    """Return the compiler IR reference-check artifact boundary."""

    return {
        "schema": COMPILER_IR_REFERENCE_CHECK_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 3.3.4 says it optimized XLA-generated IR "
            "for FlashAttention and surrounding input/output processing; each "
            "modification was checked against unmodified reference code on "
            "randomized inputs, and the final version was confirmed by human "
            "experts for all possible inputs."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "systems_result_schema": "libreevolve.systems_result_report.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can validate a compiler "
            "domain gate, a final reference-correctness gate, and "
            "compiler_ir_provenance metadata for IR origin, editability, "
            "baseline provenance, reference hashes, randomized input-generator "
            "hashes, tolerance policy, final-expert scope, per-edit reference "
            "check metadata, and artifact refs. It does not claim real "
            "reference implementation artifacts, randomized input-generator "
            "artifacts, candidate edit sequence artifacts, per-edit reference "
            "check outputs, randomized input seed or coverage records, "
            "tolerance/failure-policy artifacts, kernel/pre/postprocessing "
            "attribution artifacts, edit artifact refs, final expert all-input "
            "confirmation files, or expert/owner signoff files."
        ),
    }


def validate_compiler_ir_reference_check_boundary(
    boundary: object | str | Path | None = None,
) -> CompilerIrReferenceCheckBoundaryValidation:
    data, read_issues = _load_boundary(
        compiler_ir_reference_check_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CompilerIrReferenceCheckBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CompilerIrReferenceCheckBoundaryIssue] = []
    if data.get("schema") != COMPILER_IR_REFERENCE_CHECK_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported compiler IR reference-check boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 3.3.4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "XLA-generated IR" not in source_claim
        or "randomized inputs" not in source_claim
        or "all possible inputs" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify XLA IR, randomized-input, and all-input expert-confirmation claims"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("systems_result_schema") != "libreevolve.systems_result_report.v1":
        issues.append(_issue("invalid_systems_result_schema", "systems result schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "compiler IR reference-check boundary must not claim artifact readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim real reference implementation artifacts" not in boundary_text
        or "per-edit reference check outputs" not in boundary_text
        or "final expert all-input confirmation files" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate compiler IR metadata from real reference-check artifacts"))
    return CompilerIrReferenceCheckBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_compiler_ir_reference_check_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_compiler_ir_reference_check_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Compiler IR reference-check boundary",
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
) -> tuple[dict[str, Any] | None, list[CompilerIrReferenceCheckBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "compiler IR reference-check boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[CompilerIrReferenceCheckBoundaryIssue],
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
    issues: list[CompilerIrReferenceCheckBoundaryIssue],
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


def _issue(code: str, message: str) -> CompilerIrReferenceCheckBoundaryIssue:
    return CompilerIrReferenceCheckBoundaryIssue(code, message)
