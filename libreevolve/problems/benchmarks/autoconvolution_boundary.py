from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


AUTOCONVOLUTION_BOUNDARY_SCHEMA = "libreevolve.autoconvolution_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.16750"
EXPECTED_SOURCE_TITLE = "An improved example for an autoconvolution inequality"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2506.16750.pdf"
EXPECTED_SOURCE_FILE = "papers/2506.16750__Autoconvolution.pdf"
EXPECTED_SOURCE_SHA256 = (
    "74f3e1781ce06e3752142fa24b60037ae5d27e33ee188273b4a7aa20d54f1c1d"
)
EXPECTED_SOURCE_BYTES = 446393
EXPECTED_BOUNDARY_STATUS = (
    "post_alphaevolve_autoconvolution_context_without_local_witness_verifier"
)
EXPECTED_COMPONENT_IDS = (
    "step_function_witness_schema",
    "interval_575_coefficient_payload",
    "discrete_autoconvolution_checker",
    "lj_sequence_recomputation",
    "norm_objective_policy",
    "exact_fraction_result_record",
    "alphaevolve_baseline_record",
    "matolcsi_vinuesa_baseline_record",
    "simulated_annealing_search_provenance",
    "gradient_refinement_provenance",
    "github_artifact_snapshot",
    "mathematica_verification_notebook",
    "coefficient_row_order_parser",
    "support_normalization_invariance",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "post_alphaevolve_improvement_policy",
    "step_function_witness_schema",
    "interval_count_and_grid_spacing",
    "coefficient_payload_hashes",
    "convolution_integral_recomputation",
    "l2_linf_l1_norm_definitions",
    "objective_and_tolerance_policy",
    "exact_fraction_result_record",
    "decimal_result_record",
    "alphaevolve_baseline_record",
    "matolcsi_vinuesa_baseline_record",
    "simulated_annealing_provenance",
    "gradient_search_provenance",
    "translation_dilation_invariance_records",
    "support_normalization_records",
    "row_major_coefficient_order_tests",
    "github_artifact_snapshot",
    "python_checker_artifacts",
    "mathematica_verification_artifacts",
    "hpc_resource_provenance",
    "comparison_correlation_records",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "step_function_witness_schema": "not_implemented_locally",
    "interval_575_coefficient_payload": "not_recorded_locally",
    "coeffbl_artifact_hashes": "not_recorded_locally",
    "verify_notebook_snapshot": "not_recorded_locally",
    "formula_3_checker": "not_implemented_locally",
    "lj_sequence_recomputation": "not_implemented_locally",
    "l2_linf_l1_norm_recomputation": "not_implemented_locally",
    "exact_fraction_validation": "not_recorded_locally",
    "decimal_tolerance_policy": "not_recorded_locally",
    "alphaevolve_baseline_coefficients": "not_recorded_locally",
    "matolcsi_vinuesa_baseline_coefficients": "not_recorded_locally",
    "github_repository_snapshot": "not_recorded_locally",
    "initial_hpc_code_artifact": "not_recorded_locally",
    "refine_hpc_code_artifact": "not_recorded_locally",
    "f95_artifact": "not_recorded_locally",
    "simulated_annealing_trace": "not_recorded_locally",
    "gradient_refinement_trace": "not_recorded_locally",
    "ncsu_hpc_resource_record": "not_recorded_locally",
    "support_normalization_checker": "not_implemented_locally",
    "independent_checker_outputs": "not_recorded_locally",
}


@dataclass(frozen=True)
class AutoconvolutionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AutoconvolutionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AutoconvolutionBoundaryIssue]


def autoconvolution_boundary_record() -> dict[str, Any]:
    """Return the current post-AlphaEvolve autoconvolution absence boundary."""

    return {
        "schema": AUTOCONVOLUTION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": ["Christopher Boyer", "Zane Kun Li"],
        "source_version": "v2",
        "source_submitted_date": "2025-06-20",
        "source_last_revised_date": "2025-08-10",
        "source_pdf_date": "2025-08-10",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2506.16750v2",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://github.com/zkli-math/autoconvolutionHolder",
                "status": "public_artifact_reference_only",
            },
            {
                "url": "https://github.com/google-deepmind/alphaevolve_results/blob/main/mathematical_results.ipynb",
                "status": "alphaevolve_baseline_reference_only",
            },
            {
                "url": "https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/",
                "status": "alphaevolve_context_reference_only",
            },
            {
                "url": "https://mathoverflow.net/q/60087",
                "status": "problem_context_reference_only",
            },
        ],
        "framework_components": [
            {
                "component_id": "step_function_witness_schema",
                "paper_role": "represent nonnegative step-function witnesses",
                "local_status": "not_implemented",
            },
            {
                "component_id": "interval_575_coefficient_payload",
                "paper_role": "store the 575 row-major integer coefficients",
                "local_status": "not_recorded",
            },
            {
                "component_id": "discrete_autoconvolution_checker",
                "paper_role": "evaluate formula (3) for coefficient lists",
                "local_status": "not_implemented",
            },
            {
                "component_id": "lj_sequence_recomputation",
                "paper_role": "recompute L_j convolution samples from coefficients",
                "local_status": "not_implemented",
            },
            {
                "component_id": "norm_objective_policy",
                "paper_role": "define L2, Linf, L1 and objective/tolerance policy",
                "local_status": "not_recorded",
            },
            {
                "component_id": "exact_fraction_result_record",
                "paper_role": "verify the exact rational lower-bound certificate",
                "local_status": "not_recorded",
            },
            {
                "component_id": "alphaevolve_baseline_record",
                "paper_role": "compare against the 50-interval AlphaEvolve witness",
                "local_status": "not_recorded",
            },
            {
                "component_id": "matolcsi_vinuesa_baseline_record",
                "paper_role": "compare against the 20-step Matolcsi-Vinuesa witness",
                "local_status": "not_recorded",
            },
            {
                "component_id": "simulated_annealing_search_provenance",
                "paper_role": "record coarse and refined simulated-annealing stages",
                "local_status": "not_recorded",
            },
            {
                "component_id": "gradient_refinement_provenance",
                "paper_role": "record gradient-based refinement and upscaling stages",
                "local_status": "not_recorded",
            },
            {
                "component_id": "github_artifact_snapshot",
                "paper_role": "snapshot public Python coefficient/search artifacts",
                "local_status": "not_recorded",
            },
            {
                "component_id": "mathematica_verification_notebook",
                "paper_role": "snapshot Verify.nb coefficient checks",
                "local_status": "not_recorded",
            },
            {
                "component_id": "coefficient_row_order_parser",
                "paper_role": "parse Appendix A coefficients by row, not column",
                "local_status": "not_implemented",
            },
            {
                "component_id": "support_normalization_invariance",
                "paper_role": "track translation/dilation invariance and support normalization",
                "local_status": "not_implemented",
            },
        ],
        "local_evidence": {
            "current_autoconvolution_runner": "<none>",
            "current_math_scope": "appendix_b_alphaevolve_context_not_post_alphaevolve_575_interval_witness",
            "witness_schema_ready": False,
            "coefficient_payload_ready": False,
            "formula3_checker_ready": False,
            "norm_recomputation_ready": False,
            "exact_fraction_ready": False,
            "alphaevolve_baseline_ready": False,
            "matolcsi_vinuesa_baseline_ready": False,
            "search_provenance_ready": False,
            "github_snapshot_ready": False,
            "verify_notebook_ready": False,
            "support_normalization_ready": False,
            "independent_checker_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_result": {
            "interval_count": 575,
            "alphaevolve_interval_count": 50,
            "matolcsi_vinuesa_interval_count": 20,
            "lower_bound_decimal": 0.901564,
            "exact_fraction": (
                "96086089410408840289339769 / "
                "106577013451431545242354944"
            ),
            "alphaevolve_bound_reported": 0.8962,
            "alphaevolve_formula3_recomputed": 0.89628,
            "matolcsi_vinuesa_recomputed": 0.889226,
            "found_before_alphaevolve_awareness": "November 2024",
            "search_methods": ["simulated annealing", "gradient based methods"],
            "coefficient_scaling_factor": "2^24",
            "support_interval_for_comparison": "[-1/4, 1/4]",
            "coefficient_table_order": "row_major",
            "mv_vs_bl_autoconvolution_correlation": 0.996342,
            "alphaevolve_vs_bl_autoconvolution_correlation": 0.848466,
            "public_artifacts": [
                "Inital HPC code.py",
                "Refine HPC code.py",
                "f95.py",
                "coeffBL.txt",
                "Verify.nb",
            ],
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the post-AlphaEvolve autoconvolution paper as "
            "constructive math context only. LibreEvolve currently does not "
            "claim a 575-interval witness schema, coefficient payload hashes, "
            "formula (3) recomputation, L2/Linf/L1 norm checks, exact-rational "
            "verification, AlphaEvolve or Matolcsi-Vinuesa baseline records, "
            "simulated-annealing or gradient-search provenance, public GitHub "
            "artifact snapshots, Mathematica verification notebook evidence, "
            "support-normalization checks, or independent checker outputs."
        ),
    }


def validate_autoconvolution_boundary(
    boundary: object | str | Path | None = None,
) -> AutoconvolutionBoundaryValidation:
    data, read_issues = _load_boundary(
        autoconvolution_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return AutoconvolutionBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[AutoconvolutionBoundaryIssue] = []
    for field, expected in (
        ("schema", AUTOCONVOLUTION_BOUNDARY_SCHEMA),
        ("source_paper_id", EXPECTED_SOURCE_PAPER_ID),
        ("source_title", EXPECTED_SOURCE_TITLE),
        ("source_version", "v2"),
        ("source_submitted_date", "2025-06-20"),
        ("source_last_revised_date", "2025-08-10"),
        ("source_pdf_date", "2025-08-10"),
        ("source_url", EXPECTED_SOURCE_URL),
        ("source_file", EXPECTED_SOURCE_FILE),
        ("source_sha256", EXPECTED_SOURCE_SHA256),
        ("source_bytes", EXPECTED_SOURCE_BYTES),
        ("source_license", "http://arxiv.org/licenses/nonexclusive-distrib/1.0/"),
        ("boundary_status", EXPECTED_BOUNDARY_STATUS),
    ):
        if data.get(field) != expected:
            issues.append(
                AutoconvolutionBoundaryIssue(
                    f"{field}_mismatch",
                    f"{field} must match the cached Autoconvolution source evidence",
                )
            )
    if data.get("claim_ready") is not False:
        issues.append(
            AutoconvolutionBoundaryIssue(
                "claim_ready_overclaim",
                "Post-AlphaEvolve autoconvolution reproduction is not claim-ready",
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
            AutoconvolutionBoundaryIssue(
                "required_evidence_fields_mismatch",
                "required evidence fields must remain source-specific and complete",
            )
        )
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(
            AutoconvolutionBoundaryIssue(
                "claim_boundary_missing",
                "claim_boundary must state that autoconvolution reproduction is not claimed",
            )
        )
    return AutoconvolutionBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status")
        if isinstance(data.get("boundary_status"), str)
        else None,
        component_count=len(data.get("framework_components") or []),
        required_evidence_field_count=len(required or []),
        missing_evidence_count=len(data.get("missing_evidence") or {}),
        issues=issues,
    )


def render_autoconvolution_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    validation = validate_autoconvolution_boundary(boundary)
    lines = [
        "# Autoconvolution boundary",
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
) -> tuple[dict[str, Any] | None, list[AutoconvolutionBoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            return json.loads(boundary.read_text(encoding="utf-8")), []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, [
                AutoconvolutionBoundaryIssue(
                    "read_error", f"Could not read Autoconvolution boundary: {exc}"
                )
            ]
    if isinstance(boundary, str):
        if boundary.strip().startswith("{"):
            try:
                data = json.loads(boundary)
            except json.JSONDecodeError as exc:
                return None, [
                    AutoconvolutionBoundaryIssue(
                        "json_error",
                        f"Could not parse Autoconvolution boundary: {exc}",
                    )
                ]
            if isinstance(data, dict):
                return data, []
            return None, [
                AutoconvolutionBoundaryIssue(
                    "invalid_boundary_shape",
                    "Autoconvolution boundary JSON must be an object",
                )
            ]
        return _load_boundary(Path(boundary))
    if isinstance(boundary, dict):
        return boundary, []
    return None, [
        AutoconvolutionBoundaryIssue(
            "invalid_boundary_type",
            "Autoconvolution boundary must be a dict, JSON string, or JSON path",
        )
    ]


def _validate_source_links(
    data: dict[str, Any], issues: list[AutoconvolutionBoundaryIssue]
) -> None:
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        issues.append(
            AutoconvolutionBoundaryIssue(
                "source_links_missing",
                "Autoconvolution boundary must record source and artifact links",
            )
        )
        return
    expected_urls = {
        "https://arxiv.org/abs/2506.16750v2",
        "https://github.com/zkli-math/autoconvolutionHolder",
        "https://github.com/google-deepmind/alphaevolve_results/blob/main/mathematical_results.ipynb",
        "https://deepmind.google/discover/blog/alphaevolve-a-gemini-powered-coding-agent-for-designing-advanced-algorithms/",
        "https://mathoverflow.net/q/60087",
    }
    urls = {link.get("url") for link in source_links if isinstance(link, dict)}
    if urls != expected_urls:
        issues.append(
            AutoconvolutionBoundaryIssue(
                "source_links_mismatch",
                "source links must preserve Autoconvolution paper and artifact references",
            )
        )
    allowed_statuses = {
        "source_version_reference_only",
        "public_artifact_reference_only",
        "alphaevolve_baseline_reference_only",
        "alphaevolve_context_reference_only",
        "problem_context_reference_only",
    }
    for link in source_links:
        status = link.get("status") if isinstance(link, dict) else None
        if status not in allowed_statuses:
            issues.append(
                AutoconvolutionBoundaryIssue(
                    "source_link_status_overclaim",
                    "Autoconvolution links are reference-only until local verifier evidence exists",
                )
            )


def _validate_components(
    data: dict[str, Any], issues: list[AutoconvolutionBoundaryIssue]
) -> None:
    components = data.get("framework_components")
    if not isinstance(components, list):
        issues.append(
            AutoconvolutionBoundaryIssue(
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
            AutoconvolutionBoundaryIssue(
                "framework_component_ids_mismatch",
                "framework component ids must match the Autoconvolution evidence boundary",
            )
        )
    for component in components:
        status = component.get("local_status") if isinstance(component, dict) else None
        if status not in {"not_implemented", "not_recorded"}:
            issues.append(
                AutoconvolutionBoundaryIssue(
                    "framework_component_overclaim",
                    "Autoconvolution components must remain not_implemented/not_recorded",
                )
            )


def _validate_local_evidence(
    data: dict[str, Any], issues: list[AutoconvolutionBoundaryIssue]
) -> None:
    evidence = data.get("local_evidence")
    if not isinstance(evidence, dict):
        issues.append(
            AutoconvolutionBoundaryIssue(
                "local_evidence_missing", "local_evidence must be a dict"
            )
        )
        return
    for field in (
        "witness_schema_ready",
        "coefficient_payload_ready",
        "formula3_checker_ready",
        "norm_recomputation_ready",
        "exact_fraction_ready",
        "alphaevolve_baseline_ready",
        "matolcsi_vinuesa_baseline_ready",
        "search_provenance_ready",
        "github_snapshot_ready",
        "verify_notebook_ready",
        "support_normalization_ready",
        "independent_checker_ready",
        "repository_runtime_verified",
    ):
        if evidence.get(field) is not False:
            issues.append(
                AutoconvolutionBoundaryIssue(
                    f"local_evidence_{field}_overclaim",
                    f"{field} must remain false until local Autoconvolution evidence exists",
                )
            )


def _validate_reported_result(
    data: dict[str, Any], issues: list[AutoconvolutionBoundaryIssue]
) -> None:
    result = data.get("reported_result")
    if not isinstance(result, dict):
        issues.append(
            AutoconvolutionBoundaryIssue(
                "reported_result_missing", "reported_result must be a dict"
            )
        )
        return
    expected = {
        "interval_count": 575,
        "alphaevolve_interval_count": 50,
        "matolcsi_vinuesa_interval_count": 20,
        "lower_bound_decimal": 0.901564,
        "alphaevolve_bound_reported": 0.8962,
        "alphaevolve_formula3_recomputed": 0.89628,
        "matolcsi_vinuesa_recomputed": 0.889226,
        "coefficient_scaling_factor": "2^24",
        "support_interval_for_comparison": "[-1/4, 1/4]",
        "coefficient_table_order": "row_major",
    }
    for field, expected_value in expected.items():
        if result.get(field) != expected_value:
            issues.append(
                AutoconvolutionBoundaryIssue(
                    f"reported_result_{field}_mismatch",
                    f"reported_result.{field} must match the source-reported Autoconvolution result",
                )
            )
    artifacts = result.get("public_artifacts")
    if not isinstance(artifacts, list) or len(artifacts) != 5:
        issues.append(
            AutoconvolutionBoundaryIssue(
                "reported_result_public_artifacts_mismatch",
                "public_artifacts must retain the five named repository artifacts",
            )
        )


def _validate_missing_evidence(
    data: dict[str, Any], issues: list[AutoconvolutionBoundaryIssue]
) -> None:
    if data.get("missing_evidence") != EXPECTED_MISSING_EVIDENCE:
        issues.append(
            AutoconvolutionBoundaryIssue(
                "missing_evidence_mismatch",
                "missing evidence must match the Autoconvolution absence boundary",
            )
        )
