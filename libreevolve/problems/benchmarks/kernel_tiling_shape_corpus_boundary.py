from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


KERNEL_TILING_SHAPE_CORPUS_BOUNDARY_SCHEMA = (
    "libreevolve.kernel_tiling_shape_corpus_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("3.3.2",)
EXPECTED_BOUNDARY_STATUS = "generic_kernel_gates_without_pallas_shape_corpus"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "kernel_domain_gate_records",
    "claim_calibration_records",
    "application_provenance_records",
    "certification_reference",
    "collected_input_shape_corpus",
    "shape_corpus_source_provenance",
    "deterministic_train_eval_split",
    "train_shape_set_hash",
    "eval_shape_set_hash",
    "real_accelerator_runtime_artifacts",
    "pallas_kernel_source_identity",
    "expert_baseline_tiling_heuristic",
    "tiling_parameter_output_constraints",
    "tiling_only_candidate_boundary",
    "unchanged_kernel_math_evidence",
    "correctness_by_construction_scope",
    "speedup_metric_denominator",
    "training_time_reduction_linkage",
    "deployment_readiness_record",
    "shape_corpus_runtime_join",
)
EXPECTED_MISSING_EVIDENCE = {
    "collected_input_shape_corpus": "not_recorded_locally",
    "shape_corpus_source_provenance": "not_recorded_locally",
    "deterministic_train_eval_split": "not_recorded_locally",
    "train_shape_set_hash": "not_recorded_locally",
    "eval_shape_set_hash": "not_recorded_locally",
    "real_accelerator_runtime_artifacts": "not_recorded_locally",
    "pallas_kernel_source_identity": "not_recorded_locally",
    "expert_baseline_tiling_heuristic": "not_recorded_locally",
    "tiling_parameter_output_constraints": "not_recorded_locally",
    "tiling_only_candidate_boundary": "not_recorded_locally",
    "unchanged_kernel_math_evidence": "not_recorded_locally",
    "correctness_by_construction_scope": "not_recorded_locally",
    "speedup_metric_denominator": "not_recorded_locally",
    "training_time_reduction_linkage": "not_recorded_locally",
    "deployment_readiness_record": "not_recorded_locally",
    "shape_corpus_runtime_join": "not_recorded_locally",
}


@dataclass(frozen=True)
class KernelTilingShapeCorpusBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class KernelTilingShapeCorpusBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[KernelTilingShapeCorpusBoundaryIssue]


def kernel_tiling_shape_corpus_boundary_record() -> dict[str, Any]:
    """Return the Pallas kernel shape-corpus and runtime evidence boundary."""

    return {
        "schema": KERNEL_TILING_SHAPE_CORPUS_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 3.3.2 optimized Pallas matrix-multiplication "
            "tiling heuristics by collecting realistic input shapes, splitting "
            "them into optimization and held-out evaluation sets, measuring "
            "runtime on real TPU accelerators, comparing against expert "
            "tiling heuristics, and preserving correctness by construction "
            "because the evolved code changes tiling strategy rather than the "
            "underlying mathematical operation"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "systems_result_schema": "libreevolve.systems_result_report.v1",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has generic kernel-domain "
            "gate records, claim-calibration records, application provenance, "
            "and certification references. It does not claim collected input "
            "shape corpora, shape-corpus source provenance, deterministic "
            "train/eval splits, train or eval shape-set hashes, real "
            "accelerator runtime artifacts, Pallas kernel source identity, "
            "expert baseline tiling heuristics, tiling-parameter output "
            "constraints, tiling-only candidate boundaries, unchanged kernel "
            "math evidence, correctness-by-construction scope, speedup "
            "denominator evidence, training-time reduction linkage, deployment "
            "readiness, or shape-corpus-to-runtime joins."
        ),
    }


def validate_kernel_tiling_shape_corpus_boundary(
    boundary: object | str | Path | None = None,
) -> KernelTilingShapeCorpusBoundaryValidation:
    data, read_issues = _load_boundary(
        kernel_tiling_shape_corpus_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return KernelTilingShapeCorpusBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[KernelTilingShapeCorpusBoundaryIssue] = []
    if data.get("schema") != KERNEL_TILING_SHAPE_CORPUS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported kernel tiling shape-corpus boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 3.3.2"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "realistic input shapes" not in source_claim
        or "real TPU accelerators" not in source_claim
        or "correctness by construction" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify input shapes, real TPU runtime, and correctness by construction"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("systems_result_schema") != "libreevolve.systems_result_report.v1":
        issues.append(_issue("invalid_systems_result_schema", "systems result schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "kernel tiling shape-corpus boundary must not claim Pallas parity readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim collected input shape corpora" not in boundary_text
        or "real accelerator runtime artifacts" not in boundary_text
        or "shape-corpus-to-runtime joins" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate generic kernel gates from Pallas shape-corpus/runtime evidence"))
    return KernelTilingShapeCorpusBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_kernel_tiling_shape_corpus_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_kernel_tiling_shape_corpus_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Kernel tiling shape-corpus boundary",
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
) -> tuple[dict[str, Any] | None, list[KernelTilingShapeCorpusBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "kernel tiling shape-corpus boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[KernelTilingShapeCorpusBoundaryIssue],
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
    issues: list[KernelTilingShapeCorpusBoundaryIssue],
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


def _issue(code: str, message: str) -> KernelTilingShapeCorpusBoundaryIssue:
    return KernelTilingShapeCorpusBoundaryIssue(code, message)
