from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FIGURE7_PALLAS_TILING_EXHIBIT_BOUNDARY_SCHEMA = (
    "libreevolve.figure7_pallas_tiling_exhibit_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("Figure 7", "3.3.2")
EXPECTED_BOUNDARY_STATUS = "required_exhibit_contract_without_artifacts"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stable_exhibit_id",
    "kernel_benchmark_candidate_link",
    "matrix_product_definition",
    "matrix_dimension_definitions",
    "tile_parameter_schema",
    "pallas_kernel_identity",
    "accelerator_shape_context",
    "memory_capacity_context",
    "fused_operation_context",
    "compiler_intricacy_context",
    "shape_corpus_report_link",
    "runtime_measurement_report_link",
    "diagram_source_data_artifact",
    "diagram_rendering_parameters",
    "rendered_diagram_artifact_hash",
    "baseline_tiling_heuristic_identity",
    "tiling_only_correctness_boundary_link",
    "train_eval_split_linkage",
    "claim_calibration_record",
    "systems_readiness_linkage",
)
EXPECTED_MISSING_EVIDENCE = {
    "stable_exhibit_id": "not_recorded_locally",
    "kernel_benchmark_candidate_link": "not_recorded_locally",
    "matrix_product_definition": "not_recorded_locally",
    "matrix_dimension_definitions": "not_recorded_locally",
    "tile_parameter_schema": "not_recorded_locally",
    "pallas_kernel_identity": "not_recorded_locally",
    "accelerator_shape_context": "not_recorded_locally",
    "memory_capacity_context": "not_recorded_locally",
    "fused_operation_context": "not_recorded_locally",
    "compiler_intricacy_context": "not_recorded_locally",
    "shape_corpus_report_link": "not_recorded_locally",
    "runtime_measurement_report_link": "not_recorded_locally",
    "diagram_source_data_artifact": "not_recorded_locally",
    "diagram_rendering_parameters": "not_recorded_locally",
    "rendered_diagram_artifact_hash": "not_recorded_locally",
    "baseline_tiling_heuristic_identity": "not_recorded_locally",
    "tiling_only_correctness_boundary_link": "not_recorded_locally",
    "train_eval_split_linkage": "not_recorded_locally",
    "claim_calibration_record": "not_recorded_locally",
    "systems_readiness_linkage": "not_recorded_locally",
}


@dataclass(frozen=True)
class Figure7PallasTilingExhibitBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class Figure7PallasTilingExhibitBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[Figure7PallasTilingExhibitBoundaryIssue]


def figure7_pallas_tiling_exhibit_boundary_record() -> dict[str, Any]:
    """Return the Figure 7 Pallas tiling-problem exhibit provenance boundary."""

    return {
        "schema": FIGURE7_PALLAS_TILING_EXHIBIT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Figure 7 visualizes the Pallas tiling heuristic "
            "problem for matrix product A B = C with dimensions M, N, and P; "
            "Section 3.3.2 says the heuristic chooses tile sizes while "
            "accounting for accelerator optimal shapes, memory capacity, "
            "fused operations, and compiler intricacies"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "systems_readiness_boundary_schema": (
            "libreevolve.alphaevolve_systems_result_readiness_boundary.v1"
        ),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the required Figure 7 Pallas tiling exhibit "
            "contract only. It does not claim a stable exhibit row, kernel "
            "benchmark or candidate linkage, matrix product definition, matrix "
            "dimension definitions, tile-parameter schema, Pallas kernel "
            "identity, accelerator shape context, memory capacity context, "
            "fused-operation context, compiler-intricacy context, shape-corpus "
            "report links, runtime measurement report links, diagram source "
            "data, diagram rendering parameters, rendered diagram hashes, "
            "baseline tiling heuristic identity, tiling-only correctness "
            "boundary linkage, train/eval split linkage, claim calibration, "
            "or systems-readiness linkage."
        ),
    }


def validate_figure7_pallas_tiling_exhibit_boundary(
    boundary: object | str | Path | None = None,
) -> Figure7PallasTilingExhibitBoundaryValidation:
    data, read_issues = _load_boundary(
        figure7_pallas_tiling_exhibit_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return Figure7PallasTilingExhibitBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[Figure7PallasTilingExhibitBoundaryIssue] = []
    if data.get("schema") != FIGURE7_PALLAS_TILING_EXHIBIT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Figure 7 Pallas tiling exhibit boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be Figure 7 and 3.3.2"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "A B = C" not in source_claim
        or "dimensions M, N, and P" not in source_claim
        or "tile sizes" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify Figure 7 matrix tiling problem"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if (
        data.get("systems_readiness_boundary_schema")
        != "libreevolve.alphaevolve_systems_result_readiness_boundary.v1"
    ):
        issues.append(_issue("invalid_systems_readiness_boundary_schema", "systems readiness boundary schema must be linked"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Figure 7 Pallas tiling exhibit boundary must not claim artifact readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a stable exhibit row" not in boundary_text
        or "rendered diagram hashes" not in boundary_text
        or "systems-readiness linkage" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate the required contract from Figure 7 exhibit artifacts"))
    return Figure7PallasTilingExhibitBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_figure7_pallas_tiling_exhibit_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_figure7_pallas_tiling_exhibit_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Figure 7 Pallas tiling exhibit boundary",
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
) -> tuple[dict[str, Any] | None, list[Figure7PallasTilingExhibitBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Figure 7 Pallas tiling exhibit boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[Figure7PallasTilingExhibitBoundaryIssue],
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
    issues: list[Figure7PallasTilingExhibitBoundaryIssue],
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


def _issue(code: str, message: str) -> Figure7PallasTilingExhibitBoundaryIssue:
    return Figure7PallasTilingExhibitBoundaryIssue(code, message)
