from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BILATERAL_TRADE_BOUNDARY_SCHEMA = "libreevolve.bilateral_trade_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2603.08679"
EXPECTED_SOURCE_TITLE = (
    "A New Lower Bound for the Random Offerer Mechanism in Bilateral Trade "
    "using AI-Guided Evolutionary Search"
)
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2603.08679.pdf"
EXPECTED_SOURCE_FILE = "papers/2603.08679__Bilateral_Trade.pdf"
EXPECTED_SOURCE_SHA256 = (
    "34d3bf9c5f424d911d4ac91cc5bf4ef88d3b4cac02b7b31c064b9c868689bfa1"
)
EXPECTED_SOURCE_BYTES = 633706
EXPECTED_BOUNDARY_STATUS = "mechanism_design_result_without_local_distribution_benchmark"
EXPECTED_COMPONENT_IDS = (
    "bilateral_trade_distribution_candidates",
    "fixed_equal_revenue_buyer_distribution",
    "evolved_seller_cdf_generator",
    "seller_distribution_witness",
    "pmf_cdf_survival_rounding_policy",
    "first_best_gft_evaluator",
    "seller_offering_gft_evaluator",
    "buyer_offering_gft_evaluator",
    "random_offerer_ratio_evaluator",
    "integer_arithmetic_precision_policy",
    "prior_counterexample_baseline_rows",
    "alternate_search_attempt_rows",
    "evolved_code_artifact",
    "independent_checker_outputs",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "mechanism_design_fixture_policy",
    "buyer_distribution_schema",
    "seller_distribution_schema",
    "cdf_survival_pmf_validation_records",
    "support_domain_records",
    "rounding_tolerance_records",
    "first_best_gft_records",
    "seller_offering_gft_records",
    "buyer_offering_gft_records",
    "random_offerer_gft_records",
    "ratio_result_rows",
    "witness_distribution_artifacts",
    "evolved_code_artifact_hashes",
    "evaluation_code_artifact_hashes",
    "prior_baseline_citation_rows",
    "fixed_buyer_policy_records",
    "evolved_seller_policy_records",
    "search_attempt_records",
    "unrounded_mixture_caveat",
    "bic_bb_ir_assumption_records",
    "independent_checker_outputs",
    "reproducibility_status",
)
EXPECTED_MISSING_EVIDENCE = {
    "bilateral_trade_candidate_schema": "not_implemented_locally",
    "fixed_buyer_distribution_fixture": "not_recorded_locally",
    "seller_distribution_witness": "not_recorded_locally",
    "seller_cdf_generator_runtime": "not_implemented_locally",
    "cdf_survival_pmf_validator": "not_implemented_locally",
    "first_best_gft_evaluator": "not_implemented_locally",
    "seller_offering_gft_evaluator": "not_implemented_locally",
    "buyer_offering_gft_evaluator": "not_implemented_locally",
    "random_offerer_ratio_evaluator": "not_implemented_locally",
    "integer_rounding_policy": "not_recorded_locally",
    "ratio_result_rows": "not_recorded_locally",
    "witness_distribution_artifacts": "not_recorded_locally",
    "evolved_code_artifact_hashes": "not_recorded_locally",
    "evaluation_code_artifact_hashes": "not_recorded_locally",
    "prior_counterexample_baseline_rows": "not_recorded_locally",
    "alternate_search_attempt_rows": "not_recorded_locally",
    "unrounded_mixture_caveat": "not_recorded_locally",
    "bic_bb_ir_assumption_records": "not_recorded_locally",
    "independent_checker_outputs": "not_recorded_locally",
    "local_repository_or_notebook_snapshot": "not_recorded_locally",
}


@dataclass(frozen=True)
class BilateralTradeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class BilateralTradeBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[BilateralTradeBoundaryIssue]


def bilateral_trade_boundary_record() -> dict[str, Any]:
    """Return the current bilateral-trade lower-bound absence boundary."""

    return {
        "schema": BILATERAL_TRADE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": [
            "Yang Cai",
            "Vineet Gupta",
            "Zun Li",
            "Aranyak Mehta",
        ],
        "source_version": "v1",
        "source_submitted_date": "2026-03-09",
        "source_last_revised_date": "2026-03-09",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2603.08679v1",
                "status": "source_version_reference_only",
            }
        ],
        "framework_components": [
            {
                "component_id": "bilateral_trade_distribution_candidates",
                "paper_role": "candidate programs generate buyer/seller value distributions",
                "local_status": "not_implemented",
            },
            {
                "component_id": "fixed_equal_revenue_buyer_distribution",
                "paper_role": "Discrete Equal Revenue buyer survival function is fixed",
                "local_status": "not_recorded",
            },
            {
                "component_id": "evolved_seller_cdf_generator",
                "paper_role": "get_seller_distributions() produces seller CDF witness",
                "local_status": "not_implemented",
            },
            {
                "component_id": "seller_distribution_witness",
                "paper_role": "mixture of modulated power laws over H=20000",
                "local_status": "not_recorded",
            },
            {
                "component_id": "pmf_cdf_survival_rounding_policy",
                "paper_role": "round CDF/SF/PMF values to multiples of 1e-15",
                "local_status": "not_recorded",
            },
            {
                "component_id": "first_best_gft_evaluator",
                "paper_role": "compute first-best gains from trade",
                "local_status": "not_implemented",
            },
            {
                "component_id": "seller_offering_gft_evaluator",
                "paper_role": "solve seller-offering take-it-or-leave-it prices",
                "local_status": "not_implemented",
            },
            {
                "component_id": "buyer_offering_gft_evaluator",
                "paper_role": "solve buyer-offering take-it-or-leave-it prices",
                "local_status": "not_implemented",
            },
            {
                "component_id": "random_offerer_ratio_evaluator",
                "paper_role": "average SO/BO GFT and compute FB/RO ratio",
                "local_status": "not_implemented",
            },
            {
                "component_id": "integer_arithmetic_precision_policy",
                "paper_role": "avoid floating-point artifacts in ratio computation",
                "local_status": "not_recorded",
            },
            {
                "component_id": "prior_counterexample_baseline_rows",
                "paper_role": "compare against prior approximately 2.02 lower bound",
                "local_status": "not_recorded",
            },
            {
                "component_id": "alternate_search_attempt_rows",
                "paper_role": "fixed-seller/evolved-buyer and two-sided search attempts",
                "local_status": "not_recorded",
            },
            {
                "component_id": "evolved_code_artifact",
                "paper_role": "Listing 1 seller-distribution code artifact",
                "local_status": "not_recorded",
            },
            {
                "component_id": "independent_checker_outputs",
                "paper_role": "local rerun or independent verification of ratio witness",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_bilateral_trade_runner": "<none>",
            "current_candidate_scope": "python_primary_generic_workspace_not_mechanism_design_api",
            "distribution_candidate_schema_ready": False,
            "buyer_distribution_fixture_ready": False,
            "seller_cdf_generator_ready": False,
            "gft_evaluator_ready": False,
            "random_offerer_ratio_ready": False,
            "integer_rounding_policy_ready": False,
            "witness_distribution_artifacts_ready": False,
            "evolved_code_artifacts_ready": False,
            "evaluation_code_artifacts_ready": False,
            "prior_baseline_rows_ready": False,
            "independent_checker_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_result": {
            "support_h": 20000,
            "rounding_tolerance": "1e-15",
            "buyer_distribution": "Discrete Equal Revenue survival Pr(b>=m)=1/m",
            "seller_distribution": "mixture of modulated power laws",
            "seller_weight": 0.20,
            "secondary_power_law_exponent": 4.0,
            "modulated_exponent": "0.15 + 0.05 sin(2*pi*z)",
            "first_best_gft": 1.2322,
            "seller_offering_gft": 0.3312,
            "buyer_offering_gft": 0.8565,
            "random_offerer_gft": 0.5939,
            "approximation_ratio": 2.0749,
            "prior_reported_ratio": "approximately 2.02",
            "unrounded_mixture_status": "open_in_source_paper",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the Bilateral Trade paper as AlphaEvolve "
            "mechanism-design result context only. LibreEvolve currently does "
            "not claim bilateral-trade distribution candidate schemas, fixed "
            "Discrete Equal Revenue buyer fixtures, evolved seller CDF generator "
            "runtime support, PMF/CDF/survival validation, first-best or "
            "Random-Offerer GFT evaluators, 1e-15 integer rounding policy, "
            "witness distribution artifacts, evolved/evaluation code hashes, "
            "prior-baseline rows, alternate-search attempt rows, BIC/BB/IR "
            "assumption records, unrounded-mixture caveat handling, or "
            "independent checker outputs."
        ),
    }


def validate_bilateral_trade_boundary(
    boundary: object | str | Path | None = None,
) -> BilateralTradeBoundaryValidation:
    data, read_issues = _load_boundary(
        bilateral_trade_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return BilateralTradeBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[BilateralTradeBoundaryIssue] = []
    if data.get("schema") != BILATERAL_TRADE_BOUNDARY_SCHEMA:
        issues.append(
            BilateralTradeBoundaryIssue(
                "schema_mismatch",
                "Bilateral Trade boundary schema must match the committed contract",
            )
        )
    for field, expected in (
        ("source_paper_id", EXPECTED_SOURCE_PAPER_ID),
        ("source_title", EXPECTED_SOURCE_TITLE),
        ("source_url", EXPECTED_SOURCE_URL),
        ("source_file", EXPECTED_SOURCE_FILE),
        ("source_sha256", EXPECTED_SOURCE_SHA256),
        ("source_bytes", EXPECTED_SOURCE_BYTES),
        ("boundary_status", EXPECTED_BOUNDARY_STATUS),
    ):
        if data.get(field) != expected:
            issues.append(
                BilateralTradeBoundaryIssue(
                    f"{field}_mismatch",
                    f"{field} must match the local cached Bilateral Trade source evidence",
                )
            )
    if data.get("claim_ready") is not False:
        issues.append(
            BilateralTradeBoundaryIssue(
                "claim_ready_overclaim",
                "Bilateral Trade benchmark parity is not claim-ready",
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
            BilateralTradeBoundaryIssue(
                "required_evidence_fields_mismatch",
                "required evidence fields must remain source-specific and complete",
            )
        )
    return BilateralTradeBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status")
        if isinstance(data.get("boundary_status"), str)
        else None,
        component_count=len(data.get("framework_components") or []),
        required_evidence_field_count=len(required or []),
        missing_evidence_count=len(data.get("missing_evidence") or {}),
        issues=issues,
    )


def render_bilateral_trade_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    validation = validate_bilateral_trade_boundary(boundary)
    rows = [
        ("schema_status", "ok" if validation.ok else "invalid"),
        ("boundary_status", validation.boundary_status or "<missing>"),
        ("component_count", str(validation.component_count)),
        ("required_evidence_field_count", str(validation.required_evidence_field_count)),
        ("missing_evidence_count", str(validation.missing_evidence_count)),
    ]
    lines = ["# Bilateral Trade boundary", "", "| field | value |", "| --- | --- |"]
    lines.extend(f"| {field} | {value} |" for field, value in rows)
    if validation.issues:
        lines.extend(["", "## Issues"])
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object,
) -> tuple[dict[str, Any] | None, list[BilateralTradeBoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            return json.loads(boundary.read_text(encoding="utf-8")), []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, [
                BilateralTradeBoundaryIssue(
                    "read_error", f"Could not read Bilateral Trade boundary: {exc}"
                )
            ]
    if isinstance(boundary, str):
        return _load_boundary(Path(boundary))
    if isinstance(boundary, dict):
        return boundary, []
    return None, [
        BilateralTradeBoundaryIssue(
            "invalid_boundary_type",
            "Bilateral Trade boundary must be a dict or JSON path",
        )
    ]


def _validate_source_links(
    data: dict[str, Any], issues: list[BilateralTradeBoundaryIssue]
) -> None:
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        issues.append(
            BilateralTradeBoundaryIssue(
                "source_links_missing",
                "Bilateral Trade boundary must record source links",
            )
        )
        return
    for link in source_links:
        status = link.get("status") if isinstance(link, dict) else None
        if status != "source_version_reference_only":
            issues.append(
                BilateralTradeBoundaryIssue(
                    "source_link_status_overclaim",
                    "Bilateral Trade source links are reference-only until local source snapshots exist",
                )
            )


def _validate_components(
    data: dict[str, Any], issues: list[BilateralTradeBoundaryIssue]
) -> None:
    components = data.get("framework_components")
    if not isinstance(components, list):
        issues.append(
            BilateralTradeBoundaryIssue(
                "framework_components_missing", "framework components must be a list"
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
            BilateralTradeBoundaryIssue(
                "framework_component_ids_mismatch",
                "framework component ids must match the Bilateral Trade evidence boundary",
            )
        )
    for component in components:
        status = component.get("local_status") if isinstance(component, dict) else None
        if status not in {"not_implemented", "not_recorded"}:
            issues.append(
                BilateralTradeBoundaryIssue(
                    "framework_component_overclaim",
                    "Bilateral Trade components must remain not_implemented/not_recorded",
                )
            )


def _validate_local_evidence(
    data: dict[str, Any], issues: list[BilateralTradeBoundaryIssue]
) -> None:
    evidence = data.get("local_evidence")
    if not isinstance(evidence, dict):
        issues.append(
            BilateralTradeBoundaryIssue(
                "local_evidence_missing", "local evidence must be a dict"
            )
        )
        return
    for field in (
        "distribution_candidate_schema_ready",
        "buyer_distribution_fixture_ready",
        "seller_cdf_generator_ready",
        "gft_evaluator_ready",
        "random_offerer_ratio_ready",
        "integer_rounding_policy_ready",
        "independent_checker_ready",
        "repository_runtime_verified",
    ):
        if evidence.get(field) is not False:
            issues.append(
                BilateralTradeBoundaryIssue(
                    f"local_evidence_{field}_overclaim",
                    f"{field} must remain false until local Bilateral Trade parity evidence exists",
                )
            )


def _validate_reported_result(
    data: dict[str, Any], issues: list[BilateralTradeBoundaryIssue]
) -> None:
    result = data.get("reported_result")
    if not isinstance(result, dict):
        issues.append(
            BilateralTradeBoundaryIssue(
                "reported_result_missing", "reported result must be a dict"
            )
        )
        return
    expected = {
        "support_h": 20000,
        "rounding_tolerance": "1e-15",
        "approximation_ratio": 2.0749,
        "unrounded_mixture_status": "open_in_source_paper",
    }
    for field, value in expected.items():
        if result.get(field) != value:
            issues.append(
                BilateralTradeBoundaryIssue(
                    f"reported_result_{field}_mismatch",
                    f"{field} must match the source-reported Bilateral Trade result",
                )
            )


def _validate_missing_evidence(
    data: dict[str, Any], issues: list[BilateralTradeBoundaryIssue]
) -> None:
    if data.get("missing_evidence") != EXPECTED_MISSING_EVIDENCE:
        issues.append(
            BilateralTradeBoundaryIssue(
                "missing_evidence_mismatch",
                "missing evidence must match the Bilateral Trade absence boundary",
            )
        )
