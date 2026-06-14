from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


HARDWARE_REWRITE_ARTIFACT_BOUNDARY_SCHEMA = (
    "libreevolve.hardware_rewrite_artifact_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("3.3.3",)
EXPECTED_BOUNDARY_STATUS = "metadata_contract_without_concrete_rewrite_artifacts"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "systems_result_hardware_domain_gate",
    "hardware_rewrite_provenance_metadata_contract",
    "hardware_rtl_eda_prerequisite_boundary",
    "exact_tpu_arithmetic_circuit_identity",
    "matrix_multiplication_unit_context",
    "source_verilog_artifact",
    "modified_verilog_artifact",
    "rewrite_diff_or_ast_artifact",
    "changed_span_artifacts",
    "removed_bit_or_signal_inventory",
    "semantic_rewrite_category_label",
    "rewrite_rationale",
    "source_modified_diff_hashes",
    "per_removed_bit_ppa_linkage",
    "per_removed_bit_verification_linkage",
    "ppa_delta_artifacts",
    "functional_verification_outputs",
    "component_review_or_owner_signoff",
    "artifact_refs",
)
EXPECTED_MISSING_EVIDENCE = {
    "exact_tpu_arithmetic_circuit_identity": "not_recorded_locally",
    "matrix_multiplication_unit_context": "not_recorded_locally",
    "source_verilog_artifact": "not_recorded_locally",
    "modified_verilog_artifact": "not_recorded_locally",
    "rewrite_diff_or_ast_artifact": "not_recorded_locally",
    "changed_span_artifacts": "not_recorded_locally",
    "removed_bit_or_signal_inventory": "not_recorded_locally",
    "semantic_rewrite_category_label": "not_recorded_locally",
    "rewrite_rationale": "not_recorded_locally",
    "source_modified_diff_hashes": "not_recorded_locally",
    "per_removed_bit_ppa_linkage": "not_recorded_locally",
    "per_removed_bit_verification_linkage": "not_recorded_locally",
    "ppa_delta_artifacts": "not_recorded_locally",
    "functional_verification_outputs": "not_recorded_locally",
    "component_review_or_owner_signoff": "not_recorded_locally",
    "artifact_refs": "not_recorded_locally",
}


@dataclass(frozen=True)
class HardwareRewriteArtifactBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class HardwareRewriteArtifactBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[HardwareRewriteArtifactBoundaryIssue]


def hardware_rewrite_artifact_boundary_record() -> dict[str, Any]:
    """Return the TPU arithmetic-circuit rewrite artifact boundary."""

    return {
        "schema": HARDWARE_REWRITE_ARTIFACT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 3.3.3 says the hardware result was a simple "
            "rewrite in an already highly optimized Verilog implementation "
            "of a key TPU arithmetic circuit in the matrix multiplication "
            "unit; the rewrite removed unnecessary bits while reducing power "
            "and area."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "systems_result_schema": "libreevolve.systems_result_report.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can validate "
            "hardware_rewrite_provenance metadata and can link it to the "
            "hardware RTL/EDA evidence boundary. It does not claim an exact "
            "TPU arithmetic-circuit identity, matrix-multiplication-unit "
            "context, real source or modified Verilog files, rewrite diff or "
            "AST artifact, changed-span artifacts, removed-bit or signal "
            "inventory, semantic rewrite category evidence, rewrite rationale "
            "evidence, source/modified/diff hashes backed by artifacts, "
            "per-removed-bit PPA linkage, per-removed-bit verification "
            "linkage, PPA delta artifacts, functional verification outputs, "
            "component review or owner signoff, or complete artifact refs."
        ),
    }


def validate_hardware_rewrite_artifact_boundary(
    boundary: object | str | Path | None = None,
) -> HardwareRewriteArtifactBoundaryValidation:
    data, read_issues = _load_boundary(
        hardware_rewrite_artifact_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return HardwareRewriteArtifactBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[HardwareRewriteArtifactBoundaryIssue] = []
    if data.get("schema") != HARDWARE_REWRITE_ARTIFACT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported hardware rewrite boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 3.3.3"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "Verilog implementation" not in source_claim
        or "matrix multiplication unit" not in source_claim
        or "removed unnecessary bits" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify Verilog, matrix-unit, and removed-bit claims"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("systems_result_schema") != "libreevolve.systems_result_report.v1":
        issues.append(_issue("invalid_systems_result_schema", "systems result schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "hardware rewrite boundary must not claim artifact readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim an exact TPU arithmetic-circuit identity" not in boundary_text
        or "removed-bit or signal inventory" not in boundary_text
        or "functional verification outputs" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate metadata from concrete rewrite artifacts"))
    return HardwareRewriteArtifactBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_hardware_rewrite_artifact_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_hardware_rewrite_artifact_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Hardware rewrite artifact boundary",
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
) -> tuple[dict[str, Any] | None, list[HardwareRewriteArtifactBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "hardware rewrite boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[HardwareRewriteArtifactBoundaryIssue],
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
    issues: list[HardwareRewriteArtifactBoundaryIssue],
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


def _issue(code: str, message: str) -> HardwareRewriteArtifactBoundaryIssue:
    return HardwareRewriteArtifactBoundaryIssue(code, message)
