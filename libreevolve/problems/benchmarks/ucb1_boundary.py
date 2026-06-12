from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


UCB1_BOUNDARY_SCHEMA = "libreevolve.ucb1_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "auer-cesa-bianchi-fischer-2002"
EXPECTED_SOURCE_TITLE = "Finite-time Analysis of the Multiarmed Bandit Problem"
EXPECTED_SOURCE_URL = (
    "https://web.engr.oregonstate.edu/~afern/classes/cs533/notes/ucb.pdf"
)
EXPECTED_SOURCE_FILE = (
    "papers/auer-cesa-bianchi-fischer-2002__"
    "UCB1_Finite_Time_Analysis_Multiarmed_Bandit.pdf"
)
EXPECTED_SOURCE_SHA256 = (
    "82c8a8192bdb425fbe7662c59ee85faf47f59901f1a4999a732d04db82702a5d"
)
EXPECTED_SOURCE_BYTES = 207956
EXPECTED_BOUNDARY_STATUS = (
    "ucb1_foundational_source_without_canonical_regret_scheduler_claim"
)
EXPECTED_COMPONENT_IDS = (
    "paper_source_identity",
    "bounded_reward_support_assumption",
    "conditional_mean_stationarity_assumption",
    "regret_definition_record",
    "theorem1_regret_bound_record",
    "suboptimal_pull_bound_record",
    "canonical_index_formula_record",
    "initialization_policy_record",
    "scheduler_reward_normalization_evidence",
    "backend_arm_identity_evidence",
    "explore_coefficient_mapping",
    "selected_index_trace_records",
    "variant_support_matrix",
    "throughput_depth_nonproof_status",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_mirror_status",
    "paper_title_authors_venue_year",
    "ucb1_theorem_scope",
    "arm_count_requirement",
    "reward_support_assumptions",
    "conditional_mean_stationarity_assumptions",
    "regret_definition",
    "theorem1_regret_bound_constants",
    "suboptimal_pull_bound_constants",
    "chernoff_hoeffding_confidence_term",
    "canonical_index_formula",
    "initial_arm_try_policy",
    "stable_backend_as_arm_identity_records",
    "reward_normalization_policy",
    "reward_accounting_scope_records",
    "explore_coefficient_mapping",
    "selected_arm_index_trace_rows",
    "stationary_reward_diagnostics",
    "regret_baseline_reports",
    "variant_support_matrix",
    "ucb1_tuned_no_proof_status",
    "throughput_depth_nonproof_status",
    "scheduler_documentation_boundary",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "canonical_ucb1_scheduler_claim": "not_claimed_locally",
    "bounded_reward_distribution_evidence": "not_recorded_locally",
    "conditional_mean_stationarity_evidence": "not_recorded_locally",
    "regret_definition_runtime_report": "not_implemented_locally",
    "theorem1_regret_bound_report": "not_implemented_locally",
    "suboptimal_pull_bound_report": "not_implemented_locally",
    "canonical_confidence_radius": "not_implemented_locally",
    "canonical_initialization_policy": "not_implemented_locally",
    "stable_arm_identity_audit": "not_recorded_locally",
    "reward_normalization_audit": "not_recorded_locally",
    "explore_coefficient_equivalence": "not_claimed_locally",
    "selected_index_trace_rows": "not_recorded_locally",
    "stationary_reward_diagnostics": "not_implemented_locally",
    "regret_baseline_reports": "not_implemented_locally",
    "ucb2_support": "not_implemented_locally",
    "epsilon_n_greedy_support": "not_implemented_locally",
    "ucb1_normal_support": "not_implemented_locally",
    "ucb1_tuned_support": "not_implemented_locally",
    "throughput_depth_regret_proof": "not_claimed_locally",
    "independent_checker_outputs": "not_recorded_locally",
}


@dataclass(frozen=True)
class UCB1BoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class UCB1BoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[UCB1BoundaryIssue]


def ucb1_boundary_record() -> dict[str, Any]:
    """Return the current UCB1 source boundary for heuristic scheduler claims."""

    return {
        "schema": UCB1_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": [
            "Peter Auer",
            "Nicolo Cesa-Bianchi",
            "Paul Fischer",
        ],
        "source_venue": "Machine Learning 47:235-256",
        "source_year": 2002,
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "<not declared in cached PDF metadata>",
        "source_mirror_status": "downloaded_from_accessible_academic_mirror",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": EXPECTED_SOURCE_URL,
                "status": "download_manifest_mirror_reference_only",
            },
            {
                "url": "https://doi.org/10.1023/A:1013689704352",
                "status": "doi_reference_only",
            },
        ],
        "framework_components": [
            {
                "component_id": "paper_source_identity",
                "paper_role": "preserve cached PDF source identity and venue metadata",
                "local_status": "recorded_boundary_only",
            },
            {
                "component_id": "bounded_reward_support_assumption",
                "paper_role": "UCB1 theorem assumes rewards supported in [0,1]",
                "local_status": "not_validated",
            },
            {
                "component_id": "conditional_mean_stationarity_assumption",
                "paper_role": "requires per-arm conditional mean mu_i over plays",
                "local_status": "not_validated",
            },
            {
                "component_id": "regret_definition_record",
                "paper_role": "define regret as expected loss versus always playing best arm",
                "local_status": "not_recorded",
            },
            {
                "component_id": "theorem1_regret_bound_record",
                "paper_role": "record Theorem 1 finite-time regret constants",
                "local_status": "not_recorded",
            },
            {
                "component_id": "suboptimal_pull_bound_record",
                "paper_role": "record E[T_i(n)] <= 8 ln(n)/Delta_i^2 + 1 + pi^2/3",
                "local_status": "not_recorded",
            },
            {
                "component_id": "canonical_index_formula_record",
                "paper_role": "record empirical mean plus sqrt(2 ln t / T_i(t)) index",
                "local_status": "not_recorded",
            },
            {
                "component_id": "initialization_policy_record",
                "paper_role": "try each arm once before confidence-index selection",
                "local_status": "not_equivalent",
            },
            {
                "component_id": "scheduler_reward_normalization_evidence",
                "paper_role": "prove backend rewards satisfy UCB1 support assumptions",
                "local_status": "not_recorded",
            },
            {
                "component_id": "backend_arm_identity_evidence",
                "paper_role": "prove stable backend-as-arm identity across runs and roles",
                "local_status": "not_recorded",
            },
            {
                "component_id": "explore_coefficient_mapping",
                "paper_role": "map canonical sqrt(2) coefficient to configurable c",
                "local_status": "not_equivalent",
            },
            {
                "component_id": "selected_index_trace_records",
                "paper_role": "emit selected arm/index calculation traces",
                "local_status": "not_recorded",
            },
            {
                "component_id": "variant_support_matrix",
                "paper_role": "separate UCB2, epsilon_n-GREEDY, UCB1-NORMAL, UCB1-TUNED",
                "local_status": "not_recorded",
            },
            {
                "component_id": "throughput_depth_nonproof_status",
                "paper_role": "mark metadata-weighted routing as outside UCB1 proof scope",
                "local_status": "boundary_only",
            },
        ],
        "local_evidence": {
            "scheduler_module": "libreevolve.llm.ensemble.LLMEnsemble",
            "scheduler_docstring_scope": "heuristic_adaptation_not_canonical_ucb1",
            "default_strategy": "ucb1",
            "alternative_strategy": "throughput_depth",
            "reward_cap": 1.0,
            "negative_rewards_rejected": True,
            "untried_backend_policy": "select_untried_eligible_backends_first",
            "current_index_formula": "wins_i / counts_i + c * sqrt(log(total) / counts_i)",
            "default_explore_coeff": 1.0,
            "canonical_confidence_radius_ready": False,
            "bounded_distribution_evidence_ready": False,
            "conditional_mean_evidence_ready": False,
            "regret_report_ready": False,
            "selected_index_trace_ready": False,
            "variant_support_matrix_ready": False,
            "throughput_depth_regret_claim_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_theorem_scope": {
            "arm_count_requirement": "K > 1",
            "reward_support": "[0, 1]",
            "regret_definition": (
                "expected loss due to not always playing the best machine"
            ),
            "theorem1_regret_bound": (
                "8 * sum_i ln(n) / Delta_i + "
                "(1 + pi^2 / 3) * sum_j Delta_j"
            ),
            "suboptimal_pull_bound": (
                "E[T_i(n)] <= 8 ln(n) / Delta_i^2 + 1 + pi^2 / 3"
            ),
            "canonical_index_confidence_term": "sqrt(2 ln(t) / T_i(t))",
            "cross_machine_independence_required_for_theorems_1_to_3": False,
            "conditional_mean_assumption": (
                "E[X_i,t | X_i,1, ..., X_i,t-1] = mu_i"
            ),
            "ucb1_tuned_proven_regret_bound": False,
        },
        "variant_support": {
            "UCB1": "heuristic_local_backend_router_only",
            "UCB2": "not_implemented",
            "epsilon_n_GREEDY": "not_implemented",
            "UCB1_NORMAL": "not_implemented",
            "UCB1_TUNED": "not_implemented_no_proof_claim",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records UCB1 as foundational bandit-policy source "
            "evidence only. LibreEvolve currently does not claim canonical "
            "UCB1 finite-time regret guarantees, bounded reward-distribution "
            "evidence, conditional-mean stationarity evidence, theorem-bound "
            "reports, canonical sqrt(2 ln t / T_i(t)) index equivalence, "
            "selected-index traces, UCB2/epsilon_n-GREEDY/UCB1-NORMAL/"
            "UCB1-TUNED support, or a regret proof for throughput_depth "
            "metadata-weighted routing."
        ),
    }


def validate_ucb1_boundary(
    boundary: object | str | Path | None = None,
) -> UCB1BoundaryValidation:
    data, read_issues = _load_boundary(ucb1_boundary_record() if boundary is None else boundary)
    if read_issues:
        return UCB1BoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[UCB1BoundaryIssue] = []
    for field, expected in (
        ("schema", UCB1_BOUNDARY_SCHEMA),
        ("source_paper_id", EXPECTED_SOURCE_PAPER_ID),
        ("source_title", EXPECTED_SOURCE_TITLE),
        ("source_year", 2002),
        ("source_url", EXPECTED_SOURCE_URL),
        ("source_file", EXPECTED_SOURCE_FILE),
        ("source_sha256", EXPECTED_SOURCE_SHA256),
        ("source_bytes", EXPECTED_SOURCE_BYTES),
        ("source_license", "<not declared in cached PDF metadata>"),
        ("source_mirror_status", "downloaded_from_accessible_academic_mirror"),
        ("boundary_status", EXPECTED_BOUNDARY_STATUS),
    ):
        if data.get(field) != expected:
            issues.append(
                UCB1BoundaryIssue(
                    f"{field}_mismatch",
                    f"{field} must match the cached UCB1 source evidence",
                )
            )
    if data.get("claim_ready") is not False:
        issues.append(
            UCB1BoundaryIssue(
                "claim_ready_overclaim",
                "LibreEvolve UCB-style routing is not canonical-regret claim-ready",
            )
        )
    _validate_source_links(data, issues)
    _validate_components(data, issues)
    _validate_local_evidence(data, issues)
    _validate_theorem_scope(data, issues)
    _validate_variant_support(data, issues)
    _validate_missing_evidence(data, issues)
    required = data.get("required_evidence_fields")
    if tuple(required or ()) != EXPECTED_REQUIRED_EVIDENCE_FIELDS:
        issues.append(
            UCB1BoundaryIssue(
                "required_evidence_fields_mismatch",
                "required evidence fields must remain source-specific and complete",
            )
        )
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim canonical" not in boundary_text:
        issues.append(
            UCB1BoundaryIssue(
                "claim_boundary_missing",
                "claim_boundary must state canonical UCB1 regret is not claimed",
            )
        )
    return UCB1BoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status")
        if isinstance(data.get("boundary_status"), str)
        else None,
        component_count=len(data.get("framework_components") or []),
        required_evidence_field_count=len(required or []),
        missing_evidence_count=len(data.get("missing_evidence") or {}),
        issues=issues,
    )


def render_ucb1_boundary_summary(boundary: object | str | Path | None = None) -> str:
    validation = validate_ucb1_boundary(boundary)
    lines = [
        "# UCB1 boundary",
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
) -> tuple[dict[str, Any] | None, list[UCB1BoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            return json.loads(boundary.read_text(encoding="utf-8")), []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, [
                UCB1BoundaryIssue("read_error", f"Could not read UCB1 boundary: {exc}")
            ]
    if isinstance(boundary, str):
        if boundary.strip().startswith("{"):
            try:
                data = json.loads(boundary)
            except json.JSONDecodeError as exc:
                return None, [
                    UCB1BoundaryIssue(
                        "json_error", f"Could not parse UCB1 boundary: {exc}"
                    )
                ]
            if isinstance(data, dict):
                return data, []
            return None, [
                UCB1BoundaryIssue(
                    "invalid_boundary_shape", "UCB1 boundary JSON must be an object"
                )
            ]
        return _load_boundary(Path(boundary))
    if isinstance(boundary, dict):
        return boundary, []
    return None, [
        UCB1BoundaryIssue(
            "invalid_boundary_type",
            "UCB1 boundary must be a dict, JSON string, or JSON path",
        )
    ]


def _validate_source_links(data: dict[str, Any], issues: list[UCB1BoundaryIssue]) -> None:
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        issues.append(UCB1BoundaryIssue("source_links_missing", "source_links must be a list"))
        return
    expected_urls = {
        EXPECTED_SOURCE_URL,
        "https://doi.org/10.1023/A:1013689704352",
    }
    urls = {link.get("url") for link in source_links if isinstance(link, dict)}
    if urls != expected_urls:
        issues.append(
            UCB1BoundaryIssue(
                "source_links_mismatch", "source links must preserve UCB1 references"
            )
        )
    allowed_statuses = {
        "download_manifest_mirror_reference_only",
        "doi_reference_only",
    }
    for link in source_links:
        status = link.get("status") if isinstance(link, dict) else None
        if status not in allowed_statuses:
            issues.append(
                UCB1BoundaryIssue(
                    "source_link_status_overclaim",
                    "UCB1 source links are reference-only until source rights are expanded",
                )
            )


def _validate_components(data: dict[str, Any], issues: list[UCB1BoundaryIssue]) -> None:
    components = data.get("framework_components")
    if not isinstance(components, list):
        issues.append(
            UCB1BoundaryIssue("framework_components_missing", "framework_components must be a list")
        )
        return
    ids = tuple(
        component.get("component_id")
        for component in components
        if isinstance(component, dict)
    )
    if ids != EXPECTED_COMPONENT_IDS:
        issues.append(
            UCB1BoundaryIssue(
                "framework_component_ids_mismatch",
                "framework component ids must match the UCB1 evidence boundary",
            )
        )
    allowed = {"recorded_boundary_only", "not_validated", "not_recorded", "not_equivalent", "boundary_only"}
    for component in components:
        status = component.get("local_status") if isinstance(component, dict) else None
        if status not in allowed:
            issues.append(
                UCB1BoundaryIssue(
                    "framework_component_overclaim",
                    "UCB1 components must remain boundary-only, not-recorded, or not-validated",
                )
            )


def _validate_local_evidence(data: dict[str, Any], issues: list[UCB1BoundaryIssue]) -> None:
    evidence = data.get("local_evidence")
    if not isinstance(evidence, dict):
        issues.append(UCB1BoundaryIssue("local_evidence_missing", "local_evidence must be a dict"))
        return
    expected = {
        "scheduler_module": "libreevolve.llm.ensemble.LLMEnsemble",
        "scheduler_docstring_scope": "heuristic_adaptation_not_canonical_ucb1",
        "default_strategy": "ucb1",
        "alternative_strategy": "throughput_depth",
        "reward_cap": 1.0,
        "negative_rewards_rejected": True,
        "untried_backend_policy": "select_untried_eligible_backends_first",
        "current_index_formula": "wins_i / counts_i + c * sqrt(log(total) / counts_i)",
        "default_explore_coeff": 1.0,
    }
    for field, expected_value in expected.items():
        if evidence.get(field) != expected_value:
            issues.append(
                UCB1BoundaryIssue(
                    f"local_evidence_{field}_mismatch",
                    f"local_evidence.{field} must match scheduler boundary facts",
                )
            )
    for field in (
        "canonical_confidence_radius_ready",
        "bounded_distribution_evidence_ready",
        "conditional_mean_evidence_ready",
        "regret_report_ready",
        "selected_index_trace_ready",
        "variant_support_matrix_ready",
        "throughput_depth_regret_claim_ready",
        "repository_runtime_verified",
    ):
        if evidence.get(field) is not False:
            issues.append(
                UCB1BoundaryIssue(
                    f"local_evidence_{field}_overclaim",
                    f"{field} must remain false until canonical UCB1 evidence exists",
                )
            )


def _validate_theorem_scope(data: dict[str, Any], issues: list[UCB1BoundaryIssue]) -> None:
    theorem = data.get("reported_theorem_scope")
    if not isinstance(theorem, dict):
        issues.append(
            UCB1BoundaryIssue("reported_theorem_scope_missing", "reported_theorem_scope must be a dict")
        )
        return
    expected = {
        "arm_count_requirement": "K > 1",
        "reward_support": "[0, 1]",
        "canonical_index_confidence_term": "sqrt(2 ln(t) / T_i(t))",
        "cross_machine_independence_required_for_theorems_1_to_3": False,
        "ucb1_tuned_proven_regret_bound": False,
    }
    for field, expected_value in expected.items():
        if theorem.get(field) != expected_value:
            issues.append(
                UCB1BoundaryIssue(
                    f"reported_theorem_scope_{field}_mismatch",
                    f"reported_theorem_scope.{field} must match UCB1 source scope",
                )
            )


def _validate_variant_support(data: dict[str, Any], issues: list[UCB1BoundaryIssue]) -> None:
    expected = {
        "UCB1": "heuristic_local_backend_router_only",
        "UCB2": "not_implemented",
        "epsilon_n_GREEDY": "not_implemented",
        "UCB1_NORMAL": "not_implemented",
        "UCB1_TUNED": "not_implemented_no_proof_claim",
    }
    if data.get("variant_support") != expected:
        issues.append(
            UCB1BoundaryIssue(
                "variant_support_mismatch",
                "variant support must preserve unsupported UCB1-family variants",
            )
        )


def _validate_missing_evidence(data: dict[str, Any], issues: list[UCB1BoundaryIssue]) -> None:
    if data.get("missing_evidence") != EXPECTED_MISSING_EVIDENCE:
        issues.append(
            UCB1BoundaryIssue(
                "missing_evidence_mismatch",
                "missing evidence must match the UCB1 heuristic-scheduler boundary",
            )
        )
