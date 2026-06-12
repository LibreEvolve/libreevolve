from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


GLOBAL_NLP_OPTIMIZATION_BOUNDARY_SCHEMA = (
    "libreevolve.global_nlp_optimization_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2601.05943"
EXPECTED_SOURCE_TITLE = (
    "Global Optimization for Combinatorial Geometry Problems Revisited in the Era of LLMs"
)
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2601.05943.pdf"
EXPECTED_SOURCE_FILE = "papers/2601.05943__Global_NLP_Optimization.pdf"
EXPECTED_SOURCE_SHA256 = (
    "9e8a50b1b9613392941341258d9e13e2ce954b87efce840b4d6c0e7bfe2ceae5"
)
EXPECTED_SOURCE_BYTES = 608432
EXPECTED_BOUNDARY_STATUS = "global_nlp_comparator_without_local_solver_harness"
EXPECTED_COMPONENT_IDS = (
    "min_max_distance_ratio_nlp",
    "distance_ratio_squared_variable_formulation",
    "circle_packing_square_model",
    "circle_packing_rectangle_perimeter_model",
    "hexagon_packing_model",
    "farkas_nonoverlap_certificate",
    "mosel_model_artifacts",
    "xpress_global_solver_runner",
    "scip_solver_runner",
    "solver_license_version_records",
    "alphaevolve_validation_code_outputs",
    "table1_distance_ratio_rows",
    "table2_circle_packing_rows",
    "table3_hexagon_packing_rows",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "direct_nlp_comparator_policy",
    "selected_benchmark_subset",
    "min_max_distance_ratio_formulations",
    "circle_packing_square_formulation",
    "circle_packing_rectangle_formulation",
    "hexagon_packing_formulation",
    "mosel_model_artifacts",
    "xpress_solver_identity_and_license",
    "scip_solver_identity_and_license",
    "solver_parameter_and_time_limit_records",
    "incumbent_bound_certificate_artifacts",
    "numerical_tolerance_and_rounding_policy",
    "alphaevolve_validation_code_records",
    "prior_literature_baseline_records",
    "alphaevolve_baseline_records",
    "table1_distance_ratio_rows",
    "table2_circle_packing_rows",
    "table3_hexagon_packing_rows",
    "solver_attribution_caveat",
    "dual_bound_detail_caveat",
    "run_seed_and_resource_records",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "direct_nlp_formulation_schema": "not_implemented_locally",
    "min_max_distance_ratio_fixture": "not_implemented_locally",
    "circle_packing_square_fixture": "not_implemented_locally",
    "circle_packing_rectangle_fixture": "not_implemented_locally",
    "hexagon_packing_fixture": "not_implemented_locally",
    "mosel_model_artifacts": "not_recorded_locally",
    "xpress_global_solver_runner": "not_implemented_locally",
    "xpress_license_and_version_records": "not_recorded_locally",
    "scip_solver_runner": "not_implemented_locally",
    "scip_10_version_records": "not_recorded_locally",
    "solver_parameter_time_limit_records": "not_recorded_locally",
    "incumbent_bound_certificate_artifacts": "not_recorded_locally",
    "numerical_tolerance_rounding_policy": "not_recorded_locally",
    "alphaevolve_validation_code_outputs": "not_recorded_locally",
    "table1_distance_ratio_reproduction": "not_recorded_locally",
    "table2_circle_packing_reproduction": "not_recorded_locally",
    "table3_hexagon_packing_reproduction": "not_recorded_locally",
    "solver_attribution_records": "not_available_in_source",
    "dual_bound_improvement_records": "not_discussed_in_source",
    "independent_checker_outputs": "not_recorded_locally",
}


@dataclass(frozen=True)
class GlobalNlpOptimizationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class GlobalNlpOptimizationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[GlobalNlpOptimizationBoundaryIssue]


def global_nlp_optimization_boundary_record() -> dict[str, Any]:
    """Return the current global-NLP comparator absence boundary."""

    return {
        "schema": GLOBAL_NLP_OPTIMIZATION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": [
            "Timo Berthold",
            "Dominik Kamp",
            "Gioni Mexi",
            "Sebastian Pokutta",
            "Imre Polik",
        ],
        "source_version": "v2",
        "source_submitted_date": "2026-01-09",
        "source_last_revised_date": "2026-01-15",
        "source_pdf_date": "2026-01-15",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by-nc-nd/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2601.05943v2",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://github.com/algorithmicsuperintelligence/openevolve",
                "status": "related_alphaevolve_implementation_reference_only",
            },
            {
                "url": "https://github.com/algorithmicsuperintelligence/openevolve/blob/main/examples/circle_packing/best_program.py",
                "status": "related_circle_packing_reference_only",
            },
            {
                "url": "https://erich-friedman.github.io/packing/",
                "status": "prior_literature_reference_only",
            },
            {
                "url": "https://erich-friedman.github.io/packing/cirRsqu/",
                "status": "prior_literature_reference_only",
            },
            {
                "url": "https://erich-friedman.github.io/packing/hexinhex/",
                "status": "prior_literature_reference_only",
            },
            {
                "url": "https://optimization-online.org/2025/11/the-scip-optimization-suite-10-0/",
                "status": "solver_reference_only",
            },
        ],
        "framework_components": [
            {
                "component_id": "min_max_distance_ratio_nlp",
                "paper_role": "model point-set min/max squared-distance ratio instances",
                "local_status": "not_implemented",
            },
            {
                "component_id": "distance_ratio_squared_variable_formulation",
                "paper_role": "choose t_min=1 or t_max=1 squared-distance normalization",
                "local_status": "not_implemented",
            },
            {
                "component_id": "circle_packing_square_model",
                "paper_role": "pack n circles into a unit square using QCP constraints",
                "local_status": "not_implemented",
            },
            {
                "component_id": "circle_packing_rectangle_perimeter_model",
                "paper_role": "pack circles into a perimeter-4 rectangle with variable width",
                "local_status": "not_implemented",
            },
            {
                "component_id": "hexagon_packing_model",
                "paper_role": "pack rotated unit regular hexagons in a containing hexagon",
                "local_status": "not_implemented",
            },
            {
                "component_id": "farkas_nonoverlap_certificate",
                "paper_role": "enforce hexagon non-overlap with Farkas multipliers",
                "local_status": "not_implemented",
            },
            {
                "component_id": "mosel_model_artifacts",
                "paper_role": "record Mosel model source/exported nonlinear models",
                "local_status": "not_recorded",
            },
            {
                "component_id": "xpress_global_solver_runner",
                "paper_role": "run commercial FICO Xpress Global on the NLP models",
                "local_status": "not_implemented",
            },
            {
                "component_id": "scip_solver_runner",
                "paper_role": "run open-source SCIP on the NLP models",
                "local_status": "not_implemented",
            },
            {
                "component_id": "solver_license_version_records",
                "paper_role": "preserve solver identity, version, license, and availability",
                "local_status": "not_recorded",
            },
            {
                "component_id": "alphaevolve_validation_code_outputs",
                "paper_role": "validate solver-produced solutions with AlphaEvolve repository code",
                "local_status": "not_recorded",
            },
            {
                "component_id": "table1_distance_ratio_rows",
                "paper_role": "record improving min-max distance-ratio rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "table2_circle_packing_rows",
                "paper_role": "record improving square/rectangle circle-packing rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "table3_hexagon_packing_rows",
                "paper_role": "record improving hexagon-packing rows",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_global_nlp_runner": "<none>",
            "current_comparator_scope": "python_primary_generic_search_not_direct_nlp_solver_baseline",
            "nlp_schema_ready": False,
            "min_max_distance_ratio_ready": False,
            "circle_packing_ready": False,
            "hexagon_packing_ready": False,
            "mosel_artifacts_ready": False,
            "xpress_runner_ready": False,
            "xpress_license_verified": False,
            "scip_runner_ready": False,
            "solver_log_artifacts_ready": False,
            "alphaevolve_validation_ready": False,
            "table_reproduction_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_result": {
            "selected_problem_families": [
                "min_max_distance_ratio",
                "circle_packing_square_or_perimeter_4_rectangle",
                "unit_hexagon_packing_in_regular_hexagon",
            ],
            "solvers": ["FICO Xpress", "SCIP"],
            "modeling_language": "Mosel",
            "distance_ratio_instance_size_min": "7 variables and 10 constraints",
            "distance_ratio_instance_size_max": "91 variables and 876 constraints",
            "table1_rows": [
                {"d": 2, "n": 16, "squared_distance_ratio": 12.88924, "previous_best": 12.88927},
                {"d": 2, "n": 21, "squared_distance_ratio": 17.77499, "previous_best": 17.776},
                {"d": 2, "n": 22, "squared_distance_ratio": 19.05398, "previous_best": 19.055},
                {"d": 2, "n": 29, "squared_distance_ratio": 25.92460, "previous_best": 25.929},
                {"d": 3, "n": 14, "squared_distance_ratio": 4.16578, "previous_best": 4.16585},
            ],
            "table2_rows": [
                {"variant": "square", "n": 32, "sum_of_radii": 2.93957, "previous_best": 2.93794},
                {"variant": "rectangle", "n": 26, "sum_of_radii": 2.63930, "previous_best": 2.638},
                {"variant": "rectangle", "n": 27, "sum_of_radii": 2.69015, "previous_best": 2.687},
            ],
            "table3_rows": [
                {"n": 11, "containing_hexagon_side": 3.92485, "previous_best": 3.93010},
                {"n": 12, "containing_hexagon_side": 3.94165, "previous_best": 3.94192},
                {"n": 14, "containing_hexagon_side": 4.26900, "previous_best": 4.27240},
                {"n": 15, "containing_hexagon_side": 4.44769, "previous_best": 4.45406},
                {"n": 16, "containing_hexagon_side": 4.52788, "previous_best": 4.53633},
            ],
            "rounding_policy": {
                "distance_ratio": "rounded up to five decimal places",
                "circle_packing": "floored to five decimal digits",
                "hexagon_packing": "ceiled to five decimal digits",
            },
            "solver_attribution": "paper does not distinguish which solver found which solution",
            "dual_bound_scope": "paper does not discuss dual-bound improvement details",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records Global NLP Optimization as a direct solver "
            "comparator for AlphaEvolve geometry benchmarks only. LibreEvolve "
            "currently does not claim NLP formulation schemas, Mosel model "
            "artifacts, Xpress or SCIP solver runners, solver license/version "
            "records, incumbent/bound/certificate artifacts, numerical tolerance "
            "policy, AlphaEvolve validation-code outputs, Table 1-3 reproduction, "
            "solver logs, or independent checker outputs."
        ),
    }


def validate_global_nlp_optimization_boundary(
    boundary: object | str | Path | None = None,
) -> GlobalNlpOptimizationBoundaryValidation:
    data, read_issues = _load_boundary(
        global_nlp_optimization_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return GlobalNlpOptimizationBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[GlobalNlpOptimizationBoundaryIssue] = []
    for field, expected in (
        ("schema", GLOBAL_NLP_OPTIMIZATION_BOUNDARY_SCHEMA),
        ("source_paper_id", EXPECTED_SOURCE_PAPER_ID),
        ("source_title", EXPECTED_SOURCE_TITLE),
        ("source_version", "v2"),
        ("source_submitted_date", "2026-01-09"),
        ("source_last_revised_date", "2026-01-15"),
        ("source_pdf_date", "2026-01-15"),
        ("source_url", EXPECTED_SOURCE_URL),
        ("source_file", EXPECTED_SOURCE_FILE),
        ("source_sha256", EXPECTED_SOURCE_SHA256),
        ("source_bytes", EXPECTED_SOURCE_BYTES),
        ("source_license", "http://creativecommons.org/licenses/by-nc-nd/4.0/"),
        ("boundary_status", EXPECTED_BOUNDARY_STATUS),
    ):
        if data.get(field) != expected:
            issues.append(
                GlobalNlpOptimizationBoundaryIssue(
                    f"{field}_mismatch",
                    f"{field} must match the cached Global NLP Optimization source evidence",
                )
            )
    if data.get("claim_ready") is not False:
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "claim_ready_overclaim",
                "Global NLP solver comparison is not claim-ready",
            )
        )
    _validate_source_links(data, issues)
    _validate_components(data, issues)
    _validate_local_evidence(data, issues)
    _validate_reported_result(data, issues)
    _validate_missing_evidence(data, issues)
    required = data.get("required_evidence_fields")
    if tuple(required or ()) != EXPECTED_REQUIRED_EVIDENCE_FIELDS:
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "required_evidence_fields_mismatch",
                "required evidence fields must remain source-specific and complete",
            )
        )
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "claim_boundary_missing",
                "claim_boundary must state that global-NLP parity is not claimed",
            )
        )
    return GlobalNlpOptimizationBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status")
        if isinstance(data.get("boundary_status"), str)
        else None,
        component_count=len(data.get("framework_components") or []),
        required_evidence_field_count=len(required or []),
        missing_evidence_count=len(data.get("missing_evidence") or {}),
        issues=issues,
    )


def render_global_nlp_optimization_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    validation = validate_global_nlp_optimization_boundary(boundary)
    lines = [
        "# Global NLP Optimization boundary",
        "",
        "| field | value |",
        "| --- | --- |",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<missing>'} |",
        f"| component_count | {validation.component_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "## Issues"])
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object,
) -> tuple[dict[str, Any] | None, list[GlobalNlpOptimizationBoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            return json.loads(boundary.read_text(encoding="utf-8")), []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, [
                GlobalNlpOptimizationBoundaryIssue(
                    "read_error",
                    f"Could not read Global NLP Optimization boundary: {exc}",
                )
            ]
    if isinstance(boundary, str):
        if boundary.strip().startswith("{"):
            try:
                data = json.loads(boundary)
            except json.JSONDecodeError as exc:
                return None, [
                    GlobalNlpOptimizationBoundaryIssue(
                        "json_error",
                        f"Could not parse Global NLP Optimization boundary: {exc}",
                    )
                ]
            if isinstance(data, dict):
                return data, []
            return None, [
                GlobalNlpOptimizationBoundaryIssue(
                    "invalid_boundary_shape",
                    "Global NLP Optimization boundary JSON must be an object",
                )
            ]
        return _load_boundary(Path(boundary))
    if isinstance(boundary, dict):
        return boundary, []
    return None, [
        GlobalNlpOptimizationBoundaryIssue(
            "invalid_boundary_type",
            "Global NLP Optimization boundary must be a dict, JSON string, or JSON path",
        )
    ]


def _validate_source_links(
    data: dict[str, Any], issues: list[GlobalNlpOptimizationBoundaryIssue]
) -> None:
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "source_links_missing",
                "Global NLP Optimization boundary must record source and artifact links",
            )
        )
        return
    expected_urls = {
        "https://arxiv.org/abs/2601.05943v2",
        "https://github.com/algorithmicsuperintelligence/openevolve",
        "https://github.com/algorithmicsuperintelligence/openevolve/blob/main/examples/circle_packing/best_program.py",
        "https://erich-friedman.github.io/packing/",
        "https://erich-friedman.github.io/packing/cirRsqu/",
        "https://erich-friedman.github.io/packing/hexinhex/",
        "https://optimization-online.org/2025/11/the-scip-optimization-suite-10-0/",
    }
    urls = {link.get("url") for link in source_links if isinstance(link, dict)}
    if urls != expected_urls:
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "source_links_mismatch",
                "source links must preserve Global NLP Optimization paper references",
            )
        )
    allowed_statuses = {
        "source_version_reference_only",
        "related_alphaevolve_implementation_reference_only",
        "related_circle_packing_reference_only",
        "prior_literature_reference_only",
        "solver_reference_only",
    }
    for link in source_links:
        status = link.get("status") if isinstance(link, dict) else None
        if status not in allowed_statuses:
            issues.append(
                GlobalNlpOptimizationBoundaryIssue(
                    "source_link_status_overclaim",
                    "Global NLP Optimization links are reference-only until local solver evidence exists",
                )
            )


def _validate_components(
    data: dict[str, Any], issues: list[GlobalNlpOptimizationBoundaryIssue]
) -> None:
    components = data.get("framework_components")
    if not isinstance(components, list):
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "framework_components_missing", "framework_components must be a list"
            )
        )
        return
    ids = tuple(
        component.get("component_id")
        for component in components
        if isinstance(component, dict)
    )
    if ids != EXPECTED_COMPONENT_IDS:
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "framework_component_ids_mismatch",
                "framework component ids must match the Global NLP Optimization boundary",
            )
        )
    for component in components:
        status = component.get("local_status") if isinstance(component, dict) else None
        if status not in {"not_implemented", "not_recorded"}:
            issues.append(
                GlobalNlpOptimizationBoundaryIssue(
                    "framework_component_overclaim",
                    "Global NLP Optimization components must remain not_implemented/not_recorded",
                )
            )


def _validate_local_evidence(
    data: dict[str, Any], issues: list[GlobalNlpOptimizationBoundaryIssue]
) -> None:
    evidence = data.get("local_evidence")
    if not isinstance(evidence, dict):
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "local_evidence_missing", "local_evidence must be a dict"
            )
        )
        return
    for field in (
        "nlp_schema_ready",
        "min_max_distance_ratio_ready",
        "circle_packing_ready",
        "hexagon_packing_ready",
        "mosel_artifacts_ready",
        "xpress_runner_ready",
        "xpress_license_verified",
        "scip_runner_ready",
        "solver_log_artifacts_ready",
        "alphaevolve_validation_ready",
        "table_reproduction_ready",
        "repository_runtime_verified",
    ):
        if evidence.get(field) is not False:
            issues.append(
                GlobalNlpOptimizationBoundaryIssue(
                    f"local_evidence_{field}_overclaim",
                    f"{field} must remain false until local global-NLP evidence exists",
                )
            )


def _validate_reported_result(
    data: dict[str, Any], issues: list[GlobalNlpOptimizationBoundaryIssue]
) -> None:
    result = data.get("reported_result")
    if not isinstance(result, dict):
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "reported_result_missing", "reported_result must be a dict"
            )
        )
        return
    expected = {
        "solvers": ["FICO Xpress", "SCIP"],
        "modeling_language": "Mosel",
        "distance_ratio_instance_size_min": "7 variables and 10 constraints",
        "distance_ratio_instance_size_max": "91 variables and 876 constraints",
        "solver_attribution": "paper does not distinguish which solver found which solution",
        "dual_bound_scope": "paper does not discuss dual-bound improvement details",
    }
    for field, expected_value in expected.items():
        if result.get(field) != expected_value:
            issues.append(
                GlobalNlpOptimizationBoundaryIssue(
                    f"reported_result_{field}_mismatch",
                    f"reported_result.{field} must match the source-reported global-NLP result",
                )
            )
    if len(result.get("table1_rows") or []) != 5:
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "reported_result_table1_rows_mismatch",
                "Table 1 must retain five distance-ratio rows",
            )
        )
    if len(result.get("table2_rows") or []) != 3:
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "reported_result_table2_rows_mismatch",
                "Table 2 must retain three circle-packing rows",
            )
        )
    if len(result.get("table3_rows") or []) != 5:
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "reported_result_table3_rows_mismatch",
                "Table 3 must retain five hexagon-packing rows",
            )
        )


def _validate_missing_evidence(
    data: dict[str, Any], issues: list[GlobalNlpOptimizationBoundaryIssue]
) -> None:
    if data.get("missing_evidence") != EXPECTED_MISSING_EVIDENCE:
        issues.append(
            GlobalNlpOptimizationBoundaryIssue(
                "missing_evidence_mismatch",
                "missing evidence must match the Global NLP Optimization absence boundary",
            )
        )
