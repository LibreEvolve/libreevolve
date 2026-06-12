from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MAP_ELITES_ILLUMINATION_BOUNDARY_SCHEMA = (
    "libreevolve.map_elites_illumination_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "1504.04909"
EXPECTED_SOURCE_TITLE = "Illuminating search spaces by mapping elites"
EXPECTED_SOURCE_FILE = "papers/1504.04909__MAP_Elites.pdf"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/1504.04909.pdf"
EXPECTED_SOURCE_SHA256 = (
    "df7344343b14893a1d79a5459c1f56db50562e246d132cd0269f5201d1455872"
)
EXPECTED_SOURCE_BYTES = 3221283
EXPECTED_BOUNDARY_STATUS = "local_3d_archive_without_full_illumination_evidence"
EXPECTED_LOCAL_ARCHIVE_SCHEMA = "libreevolve.map_elites_state.v1"
EXPECTED_DESCRIPTOR_READINESS_SCHEMA = "libreevolve.map_elites_descriptor_readiness.v1"
EXPECTED_OBJECTIVE_READINESS_SCHEMA = (
    "libreevolve.map_elites_objective_archive_readiness.v1"
)
EXPECTED_DEFAULT_DESCRIPTOR_AXES = ("performance", "complexity", "diversity")
EXPECTED_PAPER_MAP_VARIABLES = ("P", "X")
EXPECTED_PAPER_ILLUMINATION_METRICS = (
    "global_performance",
    "global_reliability",
    "precision",
    "coverage",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_digest",
    "feature_descriptor_bx_contract",
    "performance_function_fx_contract",
    "dimension_declaration_policy",
    "discretization_policy",
    "initialization_policy_records",
    "random_selection_variation_records",
    "per_cell_replacement_records",
    "p_map_export",
    "x_map_export",
    "empty_unfillable_cell_diagnostics",
    "global_performance_report",
    "global_reliability_report",
    "precision_report",
    "coverage_report",
    "feature_performance_visualization_artifacts",
    "parent_lineage_stepping_stone_report",
    "descriptor_rebin_compatibility_tests",
    "retina_experiment_schedule",
    "simulated_soft_robot_schedule",
    "real_soft_arm_schedule",
    "comparison_baseline_rows",
)
EXPECTED_MISSING_EVIDENCE = {
    "explicit_bx_feature_descriptor_contract": "not_recorded_as_paper_contract",
    "explicit_fx_performance_contract": "not_recorded_as_paper_contract",
    "user_chosen_dimension_semantics": "not_recorded_locally",
    "paper_p_and_x_map_exports": "not_recorded_locally",
    "initialization_and_variation_records": "not_recorded_locally",
    "illumination_metric_reports": "not_recorded_locally",
    "feature_performance_visualizations": "not_recorded_locally",
    "empty_unfillable_cell_diagnostics": "not_recorded_locally",
    "lineage_stepping_stone_analysis": "not_recorded_locally",
    "descriptor_rebin_tests": "not_recorded_locally",
    "retina_domain_reproduction": "not_recorded_locally",
    "simulated_soft_robot_reproduction": "not_recorded_locally",
    "real_soft_arm_reproduction": "not_recorded_locally",
    "comparison_baseline_rows": "not_recorded_locally",
}


@dataclass(frozen=True)
class MapElitesIlluminationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MapElitesIlluminationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    default_axis_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[MapElitesIlluminationBoundaryIssue]


def map_elites_illumination_boundary_record() -> dict[str, Any]:
    """Return the current MAP-Elites illumination-algorithm boundary."""

    return {
        "schema": MAP_ELITES_ILLUMINATION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_url": EXPECTED_SOURCE_URL,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_status": "local_preliminary_arxiv_pdf_cached",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "paper_algorithm_contract": {
            "feature_descriptor": "b(x)",
            "performance_function": "f(x)",
            "map_variables": list(EXPECTED_PAPER_MAP_VARIABLES),
            "initialization": "random_initialization_G_solutions",
            "selection": "random_elite_selection_from_non_empty_cells",
            "variation": "mutation_or_crossover_from_selected_elites",
            "replacement": "replace_cell_only_when_candidate_improves_cell_performance",
            "illumination_metrics": list(EXPECTED_PAPER_ILLUMINATION_METRICS),
        },
        "local_archive_evidence": {
            "implementation_file": "libreevolve/population/map_elites.py",
            "snapshot_schema": EXPECTED_LOCAL_ARCHIVE_SCHEMA,
            "descriptor_readiness_schema": EXPECTED_DESCRIPTOR_READINESS_SCHEMA,
            "objective_archive_readiness_schema": EXPECTED_OBJECTIVE_READINESS_SCHEMA,
            "default_descriptor_axes": list(EXPECTED_DEFAULT_DESCRIPTOR_AXES),
            "configurable_descriptor_axes": [
                "metric:<name>",
                "evaluation_metadata:<path>",
                "candidate_metadata:<path>",
            ],
            "cell_replacement_policy": "scalar_selection_score_with_metric_overlays",
            "diversity_policy": "current_elite_corpus_tfidf_char_ngram_distance",
            "rebin_policy": "insertion_time_coordinates_no_rebin_engine",
            "full_p_x_map_export_ready": False,
            "illumination_metrics_ready": False,
            "paper_domain_reproduction_ready": False,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has a configurable local "
            "3D MAP-Elites-style archive, descriptor readiness metadata, and "
            "objective archive readiness metadata, but does not claim full "
            "Mouret-Clune illumination-algorithm parity with explicit b(x)/f(x) "
            "contracts, P/X feature-performance map exports, illumination "
            "metrics, visualization artifacts, lineage stepping-stone analysis, "
            "or retina/soft-robot/real-arm benchmark reproduction."
        ),
    }


def validate_map_elites_illumination_boundary(
    boundary: object | str | Path | None = None,
) -> MapElitesIlluminationBoundaryValidation:
    data, read_issues = _load_boundary(
        map_elites_illumination_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MapElitesIlluminationBoundaryValidation(
            False,
            None,
            0,
            0,
            0,
            read_issues,
        )
    assert isinstance(data, dict)
    issues: list[MapElitesIlluminationBoundaryIssue] = []
    if data.get("schema") != MAP_ELITES_ILLUMINATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported MAP-Elites boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 1504.04909"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify the MAP-Elites paper"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached MAP-Elites PDF"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_sha256") != EXPECTED_SOURCE_SHA256:
        issues.append(_issue("invalid_source_sha256", "source_sha256 must match the cached PDF digest"))
    if data.get("source_bytes") != EXPECTED_SOURCE_BYTES:
        issues.append(_issue("invalid_source_bytes", "source_bytes must match the cached PDF size"))
    if data.get("source_status") != "local_preliminary_arxiv_pdf_cached":
        issues.append(_issue("invalid_source_status", "source_status must preserve the local preliminary-PDF boundary"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "MAP-Elites illumination boundary must not claim paper readiness"))
    _validate_paper_contract(data.get("paper_algorithm_contract"), issues)
    default_axis_count = _validate_local_archive_evidence(data.get("local_archive_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim illumination parity"))
    return MapElitesIlluminationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        default_axis_count=default_axis_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_map_elites_illumination_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_map_elites_illumination_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "MAP-Elites illumination boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| default_axis_count | {validation.default_axis_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[MapElitesIlluminationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "MAP-Elites illumination boundary must be a JSON object")]


def _validate_paper_contract(
    value: object,
    issues: list[MapElitesIlluminationBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_paper_algorithm_contract", "paper_algorithm_contract must be an object"))
        return
    expected = {
        "feature_descriptor": "b(x)",
        "performance_function": "f(x)",
        "map_variables": list(EXPECTED_PAPER_MAP_VARIABLES),
        "initialization": "random_initialization_G_solutions",
        "selection": "random_elite_selection_from_non_empty_cells",
        "variation": "mutation_or_crossover_from_selected_elites",
        "replacement": "replace_cell_only_when_candidate_improves_cell_performance",
        "illumination_metrics": list(EXPECTED_PAPER_ILLUMINATION_METRICS),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(
                _issue(
                    f"invalid_paper_contract_{field}",
                    f"paper_algorithm_contract.{field} must preserve the MAP-Elites paper contract",
                )
            )


def _validate_local_archive_evidence(
    value: object,
    issues: list[MapElitesIlluminationBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_archive_evidence", "local_archive_evidence must be an object"))
        return 0
    expected = {
        "implementation_file": "libreevolve/population/map_elites.py",
        "snapshot_schema": EXPECTED_LOCAL_ARCHIVE_SCHEMA,
        "descriptor_readiness_schema": EXPECTED_DESCRIPTOR_READINESS_SCHEMA,
        "objective_archive_readiness_schema": EXPECTED_OBJECTIVE_READINESS_SCHEMA,
        "cell_replacement_policy": "scalar_selection_score_with_metric_overlays",
        "diversity_policy": "current_elite_corpus_tfidf_char_ngram_distance",
        "rebin_policy": "insertion_time_coordinates_no_rebin_engine",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_local_{field}", f"local_archive_evidence.{field} has drifted"))
    axes = value.get("default_descriptor_axes")
    if axes != list(EXPECTED_DEFAULT_DESCRIPTOR_AXES):
        issues.append(_issue("invalid_default_descriptor_axes", "default_descriptor_axes must stay performance/complexity/diversity"))
        axis_count = 0
    else:
        axis_count = len(axes)
    for field in (
        "full_p_x_map_export_ready",
        "illumination_metrics_ready",
        "paper_domain_reproduction_ready",
    ):
        if value.get(field) is not False:
            issues.append(_issue(f"{field}_overclaim", f"local_archive_evidence.{field} must remain false"))
    configurable = value.get("configurable_descriptor_axes")
    if not isinstance(configurable, list) or not all(isinstance(item, str) for item in configurable):
        issues.append(_issue("invalid_configurable_descriptor_axes", "configurable_descriptor_axes must be a string list"))
    return axis_count


def _validate_required_fields(
    value: object,
    issues: list[MapElitesIlluminationBoundaryIssue],
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
    issues: list[MapElitesIlluminationBoundaryIssue],
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


def _issue(code: str, message: str) -> MapElitesIlluminationBoundaryIssue:
    return MapElitesIlluminationBoundaryIssue(code, message)
