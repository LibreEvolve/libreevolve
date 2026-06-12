from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SUMS_DIFFERENCES_BOUNDARY_SCHEMA = "libreevolve.sums_differences_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2505.16105"
EXPECTED_SOURCE_TITLE = "Sums and differences of sets (improvement over AlphaEvolve)"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2505.16105.pdf"
EXPECTED_SOURCE_FILE = "papers/2505.16105__Sums_and_Differences.pdf"
EXPECTED_SOURCE_SHA256 = (
    "90d63d13afd7b8e15ceac25a4cef3f6b1c974a12a7893e80bd18e3ef4e16e1e8"
)
EXPECTED_SOURCE_BYTES = 95450
EXPECTED_BOUNDARY_STATUS = "post_alphaevolve_sums_differences_without_local_huge_set_verifier"
EXPECTED_COMPONENT_IDS = (
    "u_set_construction_schema",
    "w_m_l_b_formula_records",
    "base_2b_plus_1_encoding_checker",
    "sumset_cardinality_checker",
    "difference_set_cardinality_checker",
    "max_element_q_value_checker",
    "theta_formula_recomputation",
    "gmp_exact_arithmetic_records",
    "small_parameter_search_record",
    "large_parameter_exact_record",
    "alphaevolve_baseline_record",
    "exact_value_artifact_snapshot",
    "huge_set_compression_policy",
    "independent_checker_outputs",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_artifact_status",
    "alphaevolve_relation",
    "post_alphaevolve_improvement_policy",
    "u_set_construction_schema",
    "w_m_l_b_inclusion_exclusion_formula",
    "base_2b_plus_1_injective_encoding_checks",
    "huge_set_compression_metadata",
    "parameter_rows",
    "sumset_cardinality_records",
    "difference_set_cardinality_records",
    "max_element_and_q_value_records",
    "set_size_records",
    "theta_formula_records",
    "theta_tolerance_policy",
    "exact_computed_value_payload_hashes",
    "gmp_arithmetic_provenance",
    "floating_point_search_records",
    "integer_confirmation_records",
    "alphaevolve_54265_integer_baseline_record",
    "prior_gyarmati_hennecart_ruzsa_baseline_record",
    "bitly_artifact_resolution_records",
    "reproducibility_status",
    "lineage_comparison_rows",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "u_set_construction_schema": "not_implemented_locally",
    "w_m_l_b_formula_checker": "not_implemented_locally",
    "base_2b_plus_1_encoding_checker": "not_implemented_locally",
    "sumset_cardinality_checker": "not_implemented_locally",
    "difference_set_cardinality_checker": "not_implemented_locally",
    "max_element_q_value_checker": "not_implemented_locally",
    "theta_formula_recomputation": "not_implemented_locally",
    "huge_set_compression_artifact": "not_recorded_locally",
    "gmp_exact_arithmetic_records": "not_recorded_locally",
    "floating_point_search_records": "not_recorded_locally",
    "small_parameter_exact_record": "not_recorded_locally",
    "large_parameter_exact_record": "not_recorded_locally",
    "exact_value_artifact_payload": "not_recorded_locally",
    "bitly_artifact_resolution": "not_recorded_locally",
    "alphaevolve_54265_integer_baseline": "not_recorded_locally",
    "prior_baseline_theta_1_14465": "not_recorded_locally",
    "set_cardinality_payload_hashes": "not_recorded_locally",
    "lineage_comparison_rows": "not_recorded_locally",
    "tolerance_policy": "not_recorded_locally",
    "independent_checker_outputs": "not_recorded_locally",
}


@dataclass(frozen=True)
class SumsDifferencesBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SumsDifferencesBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[SumsDifferencesBoundaryIssue]


def sums_differences_boundary_record() -> dict[str, Any]:
    """Return the current post-AlphaEvolve sums/differences absence boundary."""

    return {
        "schema": SUMS_DIFFERENCES_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": ["Robert Gerbicz"],
        "source_version": "v1",
        "source_submitted_date": "2025-05-22",
        "source_pdf_date": "2025-05-22",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "<not declared in cached PDF metadata>",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2505.16105v1",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://bit.ly/43mWCVC",
                "status": "exact_value_artifact_reference_only",
            },
            {
                "url": "https://gmplib.org/",
                "status": "arithmetic_library_reference_only",
            },
            {
                "url": "http://bit.ly/4jkeOoX",
                "status": "alphaevolve_context_reference_only",
            },
            {
                "url": "https://gyarmatikati.web.elte.hu/publ/sumdiffv.pdf",
                "status": "prior_literature_reference_only",
            },
        ],
        "framework_components": [
            {
                "component_id": "u_set_construction_schema",
                "paper_role": "represent U(m,L,B) as integer images of bounded-coordinate vectors",
                "local_status": "not_implemented",
            },
            {
                "component_id": "w_m_l_b_formula_records",
                "paper_role": "record inclusion-exclusion formula for |W(m,L,B)|",
                "local_status": "not_recorded",
            },
            {
                "component_id": "base_2b_plus_1_encoding_checker",
                "paper_role": "check injective encoding on W+W and W-W",
                "local_status": "not_implemented",
            },
            {
                "component_id": "sumset_cardinality_checker",
                "paper_role": "verify s(U)=|U+U| via W(m,2L,2B)",
                "local_status": "not_implemented",
            },
            {
                "component_id": "difference_set_cardinality_checker",
                "paper_role": "verify d(U)=|U-U| with positive-coordinate split",
                "local_status": "not_implemented",
            },
            {
                "component_id": "max_element_q_value_checker",
                "paper_role": "recompute q(U)=2 max(U)+1 using greedy largest-coordinate fill",
                "local_status": "not_implemented",
            },
            {
                "component_id": "theta_formula_recomputation",
                "paper_role": "recompute theta from d(U), s(U), and q(U)",
                "local_status": "not_implemented",
            },
            {
                "component_id": "gmp_exact_arithmetic_records",
                "paper_role": "record exact GMP integer arithmetic confirmation",
                "local_status": "not_recorded",
            },
            {
                "component_id": "small_parameter_search_record",
                "paper_role": "record m=80,L=64,B=5 small exact result",
                "local_status": "not_recorded",
            },
            {
                "component_id": "large_parameter_exact_record",
                "paper_role": "record m=81411,L=65536,B=5 exact result",
                "local_status": "not_recorded",
            },
            {
                "component_id": "alphaevolve_baseline_record",
                "paper_role": "compare against AlphaEvolve 54265-integer theta=1.1584 baseline",
                "local_status": "not_recorded",
            },
            {
                "component_id": "exact_value_artifact_snapshot",
                "paper_role": "snapshot bit.ly exact computed values and code artifact",
                "local_status": "not_recorded",
            },
            {
                "component_id": "huge_set_compression_policy",
                "paper_role": "avoid materializing U with more than 10^43546 elements",
                "local_status": "not_recorded",
            },
            {
                "component_id": "independent_checker_outputs",
                "paper_role": "record independent verification of formulas and values",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_sums_differences_runner": "<none>",
            "current_math_scope": "appendix_b_context_not_post_alphaevolve_huge_set_verifier",
            "u_set_schema_ready": False,
            "w_formula_checker_ready": False,
            "encoding_checker_ready": False,
            "sumset_checker_ready": False,
            "difference_set_checker_ready": False,
            "q_value_checker_ready": False,
            "theta_recomputation_ready": False,
            "gmp_records_ready": False,
            "exact_value_artifact_ready": False,
            "alphaevolve_baseline_ready": False,
            "huge_set_compression_ready": False,
            "independent_checker_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_result": {
            "prior_bound": 1.14465,
            "alphaevolve_bound": 1.1584,
            "alphaevolve_integer_count": 54265,
            "paper_bound": 1.173050,
            "large_u_size_lower_description": "more than 10^43546 elements",
            "small_search_parameters": {"m": 80, "L": 64, "B": 5, "theta": 1.162997},
            "large_exact_parameters": {"m": 81411, "L": 65536, "B": 5},
            "large_exact_runtime": "approximately 15 hours",
            "rounded_large_values": {
                "size_u": "6.314107319 * 10^43546",
                "sumset_s_u": "3.208492702 * 10^61228",
                "difference_d_u": "6.587554451 * 10^75899",
                "q_u": "6.605282799 * 10^84780",
            },
            "example_parameters": {"m": 4, "L": 8, "B": 3},
            "example_values": {"size_u": 221, "sumset_s_u": 2075, "difference_d_u": 2307, "q_u": 2381, "theta": 1.013631},
            "search_range": "1 <= m <= 128, L = 64, 1 <= B <= 7",
            "arithmetic_library": "GMP",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the post-AlphaEvolve sums-and-differences "
            "paper as constructive math context only. LibreEvolve currently "
            "does not claim an explicit U-set construction schema, W(m,L,B) "
            "formula checker, base-(2B+1) encoding verifier, sumset or "
            "difference-set cardinality checker, max-element/q-value verifier, "
            "theta recomputation, exact GMP arithmetic records, bit.ly exact "
            "artifact snapshot, AlphaEvolve 54265-integer baseline evidence, "
            "huge-set compression artifacts, or independent checker outputs."
        ),
    }


def validate_sums_differences_boundary(
    boundary: object | str | Path | None = None,
) -> SumsDifferencesBoundaryValidation:
    data, read_issues = _load_boundary(
        sums_differences_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SumsDifferencesBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[SumsDifferencesBoundaryIssue] = []
    for field, expected in (
        ("schema", SUMS_DIFFERENCES_BOUNDARY_SCHEMA),
        ("source_paper_id", EXPECTED_SOURCE_PAPER_ID),
        ("source_title", EXPECTED_SOURCE_TITLE),
        ("source_version", "v1"),
        ("source_submitted_date", "2025-05-22"),
        ("source_pdf_date", "2025-05-22"),
        ("source_url", EXPECTED_SOURCE_URL),
        ("source_file", EXPECTED_SOURCE_FILE),
        ("source_sha256", EXPECTED_SOURCE_SHA256),
        ("source_bytes", EXPECTED_SOURCE_BYTES),
        ("source_license", "<not declared in cached PDF metadata>"),
        ("boundary_status", EXPECTED_BOUNDARY_STATUS),
    ):
        if data.get(field) != expected:
            issues.append(
                SumsDifferencesBoundaryIssue(
                    f"{field}_mismatch",
                    f"{field} must match the cached Sums and Differences source evidence",
                )
            )
    if data.get("claim_ready") is not False:
        issues.append(
            SumsDifferencesBoundaryIssue(
                "claim_ready_overclaim",
                "Sums and Differences huge-set reproduction is not claim-ready",
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
            SumsDifferencesBoundaryIssue(
                "required_evidence_fields_mismatch",
                "required evidence fields must remain source-specific and complete",
            )
        )
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(
            SumsDifferencesBoundaryIssue(
                "claim_boundary_missing",
                "claim_boundary must state that huge-set reproduction is not claimed",
            )
        )
    return SumsDifferencesBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status")
        if isinstance(data.get("boundary_status"), str)
        else None,
        component_count=len(data.get("framework_components") or []),
        required_evidence_field_count=len(required or []),
        missing_evidence_count=len(data.get("missing_evidence") or {}),
        issues=issues,
    )


def render_sums_differences_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    validation = validate_sums_differences_boundary(boundary)
    lines = [
        "# Sums and Differences boundary",
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
) -> tuple[dict[str, Any] | None, list[SumsDifferencesBoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            return json.loads(boundary.read_text(encoding="utf-8")), []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, [
                SumsDifferencesBoundaryIssue(
                    "read_error", f"Could not read Sums and Differences boundary: {exc}"
                )
            ]
    if isinstance(boundary, str):
        if boundary.strip().startswith("{"):
            try:
                data = json.loads(boundary)
            except json.JSONDecodeError as exc:
                return None, [
                    SumsDifferencesBoundaryIssue(
                        "json_error",
                        f"Could not parse Sums and Differences boundary: {exc}",
                    )
                ]
            if isinstance(data, dict):
                return data, []
            return None, [
                SumsDifferencesBoundaryIssue(
                    "invalid_boundary_shape",
                    "Sums and Differences boundary JSON must be an object",
                )
            ]
        return _load_boundary(Path(boundary))
    if isinstance(boundary, dict):
        return boundary, []
    return None, [
        SumsDifferencesBoundaryIssue(
            "invalid_boundary_type",
            "Sums and Differences boundary must be a dict, JSON string, or JSON path",
        )
    ]


def _validate_source_links(
    data: dict[str, Any], issues: list[SumsDifferencesBoundaryIssue]
) -> None:
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        issues.append(
            SumsDifferencesBoundaryIssue(
                "source_links_missing",
                "Sums and Differences boundary must record source and artifact links",
            )
        )
        return
    expected_urls = {
        "https://arxiv.org/abs/2505.16105v1",
        "https://bit.ly/43mWCVC",
        "https://gmplib.org/",
        "http://bit.ly/4jkeOoX",
        "https://gyarmatikati.web.elte.hu/publ/sumdiffv.pdf",
    }
    urls = {link.get("url") for link in source_links if isinstance(link, dict)}
    if urls != expected_urls:
        issues.append(
            SumsDifferencesBoundaryIssue(
                "source_links_mismatch",
                "source links must preserve Sums and Differences references",
            )
        )
    allowed_statuses = {
        "source_version_reference_only",
        "exact_value_artifact_reference_only",
        "arithmetic_library_reference_only",
        "alphaevolve_context_reference_only",
        "prior_literature_reference_only",
    }
    for link in source_links:
        status = link.get("status") if isinstance(link, dict) else None
        if status not in allowed_statuses:
            issues.append(
                SumsDifferencesBoundaryIssue(
                    "source_link_status_overclaim",
                    "Sums and Differences links are reference-only until local verifier evidence exists",
                )
            )


def _validate_components(
    data: dict[str, Any], issues: list[SumsDifferencesBoundaryIssue]
) -> None:
    components = data.get("framework_components")
    if not isinstance(components, list):
        issues.append(
            SumsDifferencesBoundaryIssue(
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
            SumsDifferencesBoundaryIssue(
                "framework_component_ids_mismatch",
                "framework component ids must match the Sums and Differences evidence boundary",
            )
        )
    for component in components:
        status = component.get("local_status") if isinstance(component, dict) else None
        if status not in {"not_implemented", "not_recorded"}:
            issues.append(
                SumsDifferencesBoundaryIssue(
                    "framework_component_overclaim",
                    "Sums and Differences components must remain not_implemented/not_recorded",
                )
            )


def _validate_local_evidence(
    data: dict[str, Any], issues: list[SumsDifferencesBoundaryIssue]
) -> None:
    evidence = data.get("local_evidence")
    if not isinstance(evidence, dict):
        issues.append(
            SumsDifferencesBoundaryIssue(
                "local_evidence_missing", "local_evidence must be a dict"
            )
        )
        return
    for field in (
        "u_set_schema_ready",
        "w_formula_checker_ready",
        "encoding_checker_ready",
        "sumset_checker_ready",
        "difference_set_checker_ready",
        "q_value_checker_ready",
        "theta_recomputation_ready",
        "gmp_records_ready",
        "exact_value_artifact_ready",
        "alphaevolve_baseline_ready",
        "huge_set_compression_ready",
        "independent_checker_ready",
        "repository_runtime_verified",
    ):
        if evidence.get(field) is not False:
            issues.append(
                SumsDifferencesBoundaryIssue(
                    f"local_evidence_{field}_overclaim",
                    f"{field} must remain false until local Sums and Differences evidence exists",
                )
            )


def _validate_reported_result(
    data: dict[str, Any], issues: list[SumsDifferencesBoundaryIssue]
) -> None:
    result = data.get("reported_result")
    if not isinstance(result, dict):
        issues.append(
            SumsDifferencesBoundaryIssue(
                "reported_result_missing", "reported_result must be a dict"
            )
        )
        return
    expected = {
        "prior_bound": 1.14465,
        "alphaevolve_bound": 1.1584,
        "alphaevolve_integer_count": 54265,
        "paper_bound": 1.173050,
        "large_u_size_lower_description": "more than 10^43546 elements",
        "large_exact_runtime": "approximately 15 hours",
        "search_range": "1 <= m <= 128, L = 64, 1 <= B <= 7",
        "arithmetic_library": "GMP",
    }
    for field, expected_value in expected.items():
        if result.get(field) != expected_value:
            issues.append(
                SumsDifferencesBoundaryIssue(
                    f"reported_result_{field}_mismatch",
                    f"reported_result.{field} must match the source-reported Sums and Differences result",
                )
            )
    large = result.get("large_exact_parameters")
    if large != {"m": 81411, "L": 65536, "B": 5}:
        issues.append(
            SumsDifferencesBoundaryIssue(
                "reported_result_large_parameters_mismatch",
                "large_exact_parameters must retain m=81411,L=65536,B=5",
            )
        )


def _validate_missing_evidence(
    data: dict[str, Any], issues: list[SumsDifferencesBoundaryIssue]
) -> None:
    if data.get("missing_evidence") != EXPECTED_MISSING_EVIDENCE:
        issues.append(
            SumsDifferencesBoundaryIssue(
                "missing_evidence_mismatch",
                "missing evidence must match the Sums and Differences absence boundary",
            )
        )
