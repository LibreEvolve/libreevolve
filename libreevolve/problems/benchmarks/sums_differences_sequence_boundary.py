from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUMS_DIFFERENCES_SEQUENCE_BOUNDARY_SCHEMA = (
    "libreevolve.sums_differences_sequence_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.01896"
EXPECTED_SOURCE_TITLE = (
    "Sums and differences of sets: a further improvement over AlphaEvolve"
)
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2506.01896.pdf"
EXPECTED_SOURCE_FILE = "papers/2506.01896__Sums_and_Differences_II.pdf"
EXPECTED_SOURCE_SHA256 = (
    "3f04c75ccd850eb6e5c785e543f98d12446e9891399cc5246acae9335b4494c2"
)
EXPECTED_SOURCE_BYTES = 302747
EXPECTED_BOUNDARY_STATUS = (
    "post_alphaevolve_sums_differences_sequence_without_local_asymptotic_verifier"
)
EXPECTED_COMPONENT_IDS = (
    "sequence_u_set_construction_schema",
    "large_deviation_i_c_b_checker",
    "asymptotic_w_m_floor_rm_b_checker",
    "q_bound_derivation_checker",
    "sumset_upper_bound_checker",
    "difference_lower_bound_checker",
    "theta0_variational_formula_recomputation",
    "matlab_code_provenance_records",
    "tolerance_sweep_table_records",
    "finite_prefix_artifact_policy",
    "alphaevolve_baseline_record",
    "gerbicz_2505_baseline_record",
    "lineage_comparison_rows",
    "independent_checker_outputs",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_artifact_status",
    "alphaevolve_relation",
    "post_alphaevolve_sequence_policy",
    "sequence_u_set_construction_schema",
    "w_m_floor_rm_b_large_deviation_formula",
    "i_c_b_legendre_transform_records",
    "lemma_1_and_lemma_2_checker_outputs",
    "q_bound_derivation_records",
    "sumset_upper_bound_records",
    "difference_lower_bound_records",
    "theta0_variational_formula_records",
    "parameter_rows_b_r_a_m",
    "matlab_2024b_code_provenance",
    "tolerance_sweep_rows",
    "independent_python_or_exact_reimplementation",
    "finite_prefix_witness_artifacts",
    "convergence_and_tail_bound_checks",
    "theta_tolerance_policy",
    "alphaevolve_1_1584_baseline_record",
    "gerbicz_2505_1_173050_baseline_record",
    "prior_gyarmati_hennecart_ruzsa_baseline_record",
    "lineage_comparison_rows",
    "reproducibility_status",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "sequence_u_set_construction_schema": "not_implemented_locally",
    "large_deviation_i_c_b_checker": "not_implemented_locally",
    "asymptotic_w_checker": "not_implemented_locally",
    "lemma_1_checker": "not_implemented_locally",
    "lemma_2_checker": "not_implemented_locally",
    "q_bound_checker": "not_implemented_locally",
    "sumset_upper_bound_checker": "not_implemented_locally",
    "difference_lower_bound_checker": "not_implemented_locally",
    "theta0_recomputation": "not_implemented_locally",
    "matlab_code_extraction": "not_recorded_locally",
    "matlab_2024b_provenance": "not_recorded_locally",
    "tolerance_sweep_reproduction": "not_recorded_locally",
    "independent_python_reimplementation": "not_recorded_locally",
    "finite_prefix_artifacts": "not_recorded_locally",
    "convergence_tail_bounds": "not_recorded_locally",
    "alphaevolve_baseline": "not_recorded_locally",
    "gerbicz_2505_baseline": "not_recorded_locally",
    "prior_baseline_theta_1_14465": "not_recorded_locally",
    "lineage_comparison_rows": "not_recorded_locally",
    "independent_checker_outputs": "not_recorded_locally",
}


@dataclass(frozen=True)
class SumsDifferencesSequenceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SumsDifferencesSequenceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[SumsDifferencesSequenceBoundaryIssue]


def sums_differences_sequence_boundary_record() -> dict[str, Any]:
    """Return the current Sums and Differences II absence boundary."""

    return {
        "schema": SUMS_DIFFERENCES_SEQUENCE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": ["Fan Zheng"],
        "source_version": "v1",
        "source_submitted_date": "2025-06-02",
        "source_pdf_date": "2025-06-11",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "CC BY 4.0",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2506.01896v1",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://doi.org/10.48550/arXiv.2506.01896",
                "status": "doi_reference_only",
            },
            {
                "url": "http://creativecommons.org/licenses/by/4.0/",
                "status": "license_reference_only",
            },
            {
                "url": "https://arxiv.org/abs/2505.16105",
                "status": "gerbicz_2505_baseline_reference_only",
            },
            {
                "url": "http://bit.ly/4jkeOoX",
                "status": "alphaevolve_context_reference_only",
            },
        ],
        "framework_components": [
            {
                "component_id": "sequence_u_set_construction_schema",
                "paper_role": "represent a limiting sequence of U sets from W(m,floor(rm),B)",
                "local_status": "not_implemented",
            },
            {
                "component_id": "large_deviation_i_c_b_checker",
                "paper_role": "check Legendre-transform I(c,B) large-deviation values",
                "local_status": "not_implemented",
            },
            {
                "component_id": "asymptotic_w_m_floor_rm_b_checker",
                "paper_role": "verify asymptotic log |W(m,floor(rm),B)| / m",
                "local_status": "not_implemented",
            },
            {
                "component_id": "q_bound_derivation_checker",
                "paper_role": "check q(U) <= (2B+1)^m derivation",
                "local_status": "not_implemented",
            },
            {
                "component_id": "sumset_upper_bound_checker",
                "paper_role": "check s(U) upper bound using W(m,floor(2rm),2B)",
                "local_status": "not_implemented",
            },
            {
                "component_id": "difference_lower_bound_checker",
                "paper_role": "check d(U) lower bound from k=floor(aL) term",
                "local_status": "not_implemented",
            },
            {
                "component_id": "theta0_variational_formula_recomputation",
                "paper_role": "recompute restricted supremum over B,r,a and theta",
                "local_status": "not_implemented",
            },
            {
                "component_id": "matlab_code_provenance_records",
                "paper_role": "record MATLAB 2024b fminbnd/fminunc source-code provenance",
                "local_status": "not_recorded",
            },
            {
                "component_id": "tolerance_sweep_table_records",
                "paper_role": "record B=3..10 and 1e-4..1e-10 tolerance table",
                "local_status": "not_recorded",
            },
            {
                "component_id": "finite_prefix_artifact_policy",
                "paper_role": "separate asymptotic sequence claims from finite witness artifacts",
                "local_status": "not_recorded",
            },
            {
                "component_id": "alphaevolve_baseline_record",
                "paper_role": "compare against AlphaEvolve theta=1.1584 baseline",
                "local_status": "not_recorded",
            },
            {
                "component_id": "gerbicz_2505_baseline_record",
                "paper_role": "compare against Gerbicz theta=1.173050 finite construction",
                "local_status": "not_recorded",
            },
            {
                "component_id": "lineage_comparison_rows",
                "paper_role": "preserve prior-to-current bound lineage",
                "local_status": "not_recorded",
            },
            {
                "component_id": "independent_checker_outputs",
                "paper_role": "record independent verification of formulas and numerics",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_sums_differences_runner": "<none>",
            "current_math_scope": "appendix_b_context_not_post_alphaevolve_sequence_verifier",
            "sequence_schema_ready": False,
            "large_deviation_checker_ready": False,
            "asymptotic_w_checker_ready": False,
            "q_bound_checker_ready": False,
            "sumset_bound_checker_ready": False,
            "difference_bound_checker_ready": False,
            "theta0_recomputation_ready": False,
            "matlab_code_records_ready": False,
            "tolerance_sweep_records_ready": False,
            "finite_prefix_policy_ready": False,
            "alphaevolve_baseline_ready": False,
            "gerbicz_2505_baseline_ready": False,
            "independent_checker_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_result": {
            "alphaevolve_bound": 1.1584,
            "gerbicz_2505_bound": 1.173050,
            "paper_bound": 1.173077,
            "paper_bound_description": "theta >= 1.173077 in the limiting sequence",
            "winning_b": 5,
            "restricted_b_values": [3, 4, 5, 6, 7, 8, 9, 10],
            "restricted_r_interval": "(0.5, 2)",
            "restricted_a_interval": "(0, min(1, 1/r))",
            "tolerances": ["1e-4", "1e-6", "1e-8", "1e-10"],
            "winning_theta_minus_one": {
                "epsilon_1e_minus_4": 0.173077285664668,
                "epsilon_1e_minus_6": 0.173077279785044,
                "epsilon_1e_minus_8": 0.173077279785136,
                "epsilon_1e_minus_10": 0.173077279785136,
            },
            "table_1_theta_minus_one_by_b_at_1e_minus_10": {
                "3": 0.168700179627163,
                "4": 0.172137890014121,
                "5": 0.173077279785136,
                "6": 0.172855932676998,
                "7": 0.172060243360376,
                "8": 0.170975345189401,
                "9": 0.169749936705623,
                "10": 0.168465310634737,
            },
            "numerical_tool": "MATLAB 2024b",
            "matlab_functions": ["fminbnd", "fminunc", "logW", "logD", "sup"],
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records Sums and Differences II as "
            "post-AlphaEvolve asymptotic constructive-math context only. "
            "LibreEvolve currently does not claim a sequence-of-U construction "
            "schema, large-deviation I(c,B) checker, W(m,floor(rm),B) "
            "asymptotic checker, q/s/d bound derivation verifier, theta0 "
            "variational-formula recomputation, MATLAB-code provenance, "
            "tolerance-sweep reproduction, finite-prefix artifact policy, "
            "AlphaEvolve and Gerbicz baseline comparison rows, or independent "
            "checker outputs."
        ),
    }


def validate_sums_differences_sequence_boundary(
    boundary: object | str | Path | None = None,
) -> SumsDifferencesSequenceBoundaryValidation:
    data, read_issues = _load_boundary(
        sums_differences_sequence_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SumsDifferencesSequenceBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[SumsDifferencesSequenceBoundaryIssue] = []
    for field, expected in (
        ("schema", SUMS_DIFFERENCES_SEQUENCE_BOUNDARY_SCHEMA),
        ("source_paper_id", EXPECTED_SOURCE_PAPER_ID),
        ("source_title", EXPECTED_SOURCE_TITLE),
        ("source_version", "v1"),
        ("source_submitted_date", "2025-06-02"),
        ("source_pdf_date", "2025-06-11"),
        ("source_url", EXPECTED_SOURCE_URL),
        ("source_file", EXPECTED_SOURCE_FILE),
        ("source_sha256", EXPECTED_SOURCE_SHA256),
        ("source_bytes", EXPECTED_SOURCE_BYTES),
        ("source_license", "CC BY 4.0"),
        ("boundary_status", EXPECTED_BOUNDARY_STATUS),
    ):
        if data.get(field) != expected:
            issues.append(
                SumsDifferencesSequenceBoundaryIssue(
                    f"{field}_mismatch",
                    f"{field} must match the cached Sums and Differences II source evidence",
                )
            )
    if data.get("claim_ready") is not False:
        issues.append(
            SumsDifferencesSequenceBoundaryIssue(
                "claim_ready_overclaim",
                "Sums and Differences II asymptotic reproduction is not claim-ready",
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
            SumsDifferencesSequenceBoundaryIssue(
                "required_evidence_fields_mismatch",
                "required evidence fields must remain source-specific and complete",
            )
        )
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(
            SumsDifferencesSequenceBoundaryIssue(
                "claim_boundary_missing",
                "claim_boundary must state that asymptotic reproduction is not claimed",
            )
        )
    return SumsDifferencesSequenceBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status")
        if isinstance(data.get("boundary_status"), str)
        else None,
        component_count=len(data.get("framework_components") or []),
        required_evidence_field_count=len(required or []),
        missing_evidence_count=len(data.get("missing_evidence") or {}),
        issues=issues,
    )


def render_sums_differences_sequence_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    validation = validate_sums_differences_sequence_boundary(boundary)
    lines = [
        "# Sums and Differences II boundary",
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
) -> tuple[dict[str, Any] | None, list[SumsDifferencesSequenceBoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            return json.loads(boundary.read_text(encoding="utf-8")), []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, [
                SumsDifferencesSequenceBoundaryIssue(
                    "read_error",
                    f"Could not read Sums and Differences II boundary: {exc}",
                )
            ]
    if isinstance(boundary, str):
        if boundary.strip().startswith("{"):
            try:
                data = json.loads(boundary)
            except json.JSONDecodeError as exc:
                return None, [
                    SumsDifferencesSequenceBoundaryIssue(
                        "json_error",
                        f"Could not parse Sums and Differences II boundary: {exc}",
                    )
                ]
            if isinstance(data, dict):
                return data, []
            return None, [
                SumsDifferencesSequenceBoundaryIssue(
                    "invalid_boundary_shape",
                    "Sums and Differences II boundary JSON must be an object",
                )
            ]
        return _load_boundary(Path(boundary))
    if isinstance(boundary, dict):
        return boundary, []
    return None, [
        SumsDifferencesSequenceBoundaryIssue(
            "invalid_boundary_type",
            "Sums and Differences II boundary must be a dict, JSON string, or JSON path",
        )
    ]


def _validate_source_links(
    data: dict[str, Any], issues: list[SumsDifferencesSequenceBoundaryIssue]
) -> None:
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        issues.append(
            SumsDifferencesSequenceBoundaryIssue(
                "source_links_missing",
                "Sums and Differences II boundary must record source links",
            )
        )
        return
    expected_urls = {
        "https://arxiv.org/abs/2506.01896v1",
        "https://doi.org/10.48550/arXiv.2506.01896",
        "http://creativecommons.org/licenses/by/4.0/",
        "https://arxiv.org/abs/2505.16105",
        "http://bit.ly/4jkeOoX",
    }
    urls = {link.get("url") for link in source_links if isinstance(link, dict)}
    if urls != expected_urls:
        issues.append(
            SumsDifferencesSequenceBoundaryIssue(
                "source_links_mismatch",
                "source links must preserve Sums and Differences II references",
            )
        )
    allowed_statuses = {
        "source_version_reference_only",
        "doi_reference_only",
        "license_reference_only",
        "gerbicz_2505_baseline_reference_only",
        "alphaevolve_context_reference_only",
    }
    for link in source_links:
        status = link.get("status") if isinstance(link, dict) else None
        if status not in allowed_statuses:
            issues.append(
                SumsDifferencesSequenceBoundaryIssue(
                    "source_link_status_overclaim",
                    "Sums and Differences II links are reference-only until verifier evidence exists",
                )
            )


def _validate_components(
    data: dict[str, Any], issues: list[SumsDifferencesSequenceBoundaryIssue]
) -> None:
    components = data.get("framework_components")
    if not isinstance(components, list):
        issues.append(
            SumsDifferencesSequenceBoundaryIssue(
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
            SumsDifferencesSequenceBoundaryIssue(
                "framework_component_ids_mismatch",
                "framework component ids must match the Sums and Differences II boundary",
            )
        )
    for component in components:
        status = component.get("local_status") if isinstance(component, dict) else None
        if status not in {"not_implemented", "not_recorded"}:
            issues.append(
                SumsDifferencesSequenceBoundaryIssue(
                    "framework_component_overclaim",
                    "Sums and Differences II components must remain not_implemented/not_recorded",
                )
            )


def _validate_local_evidence(
    data: dict[str, Any], issues: list[SumsDifferencesSequenceBoundaryIssue]
) -> None:
    evidence = data.get("local_evidence")
    if not isinstance(evidence, dict):
        issues.append(
            SumsDifferencesSequenceBoundaryIssue(
                "local_evidence_missing", "local_evidence must be a dict"
            )
        )
        return
    for field in (
        "sequence_schema_ready",
        "large_deviation_checker_ready",
        "asymptotic_w_checker_ready",
        "q_bound_checker_ready",
        "sumset_bound_checker_ready",
        "difference_bound_checker_ready",
        "theta0_recomputation_ready",
        "matlab_code_records_ready",
        "tolerance_sweep_records_ready",
        "finite_prefix_policy_ready",
        "alphaevolve_baseline_ready",
        "gerbicz_2505_baseline_ready",
        "independent_checker_ready",
        "repository_runtime_verified",
    ):
        if evidence.get(field) is not False:
            issues.append(
                SumsDifferencesSequenceBoundaryIssue(
                    f"local_evidence_{field}_overclaim",
                    f"{field} must remain false until local sequence evidence exists",
                )
            )


def _validate_reported_result(
    data: dict[str, Any], issues: list[SumsDifferencesSequenceBoundaryIssue]
) -> None:
    result = data.get("reported_result")
    if not isinstance(result, dict):
        issues.append(
            SumsDifferencesSequenceBoundaryIssue(
                "reported_result_missing", "reported_result must be a dict"
            )
        )
        return
    expected = {
        "alphaevolve_bound": 1.1584,
        "gerbicz_2505_bound": 1.173050,
        "paper_bound": 1.173077,
        "winning_b": 5,
        "restricted_r_interval": "(0.5, 2)",
        "restricted_a_interval": "(0, min(1, 1/r))",
        "numerical_tool": "MATLAB 2024b",
    }
    for field, expected_value in expected.items():
        if result.get(field) != expected_value:
            issues.append(
                SumsDifferencesSequenceBoundaryIssue(
                    f"reported_result_{field}_mismatch",
                    f"reported_result.{field} must match the source-reported Sums and Differences II result",
                )
            )
    if result.get("restricted_b_values") != [3, 4, 5, 6, 7, 8, 9, 10]:
        issues.append(
            SumsDifferencesSequenceBoundaryIssue(
                "reported_result_restricted_b_values_mismatch",
                "restricted_b_values must preserve the Table 1 search range",
            )
        )
    winning = result.get("winning_theta_minus_one")
    if not isinstance(winning, dict) or winning.get("epsilon_1e_minus_10") != 0.173077279785136:
        issues.append(
            SumsDifferencesSequenceBoundaryIssue(
                "reported_result_winning_theta_minus_one_mismatch",
                "winning theta-1 values must preserve the B=5 tolerance row",
            )
        )


def _validate_missing_evidence(
    data: dict[str, Any], issues: list[SumsDifferencesSequenceBoundaryIssue]
) -> None:
    if data.get("missing_evidence") != EXPECTED_MISSING_EVIDENCE:
        issues.append(
            SumsDifferencesSequenceBoundaryIssue(
                "missing_evidence_mismatch",
                "missing evidence must match the Sums and Differences II absence boundary",
            )
        )
