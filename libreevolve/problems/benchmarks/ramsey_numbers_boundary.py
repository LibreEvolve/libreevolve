from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RAMSEY_NUMBERS_BOUNDARY_SCHEMA = "libreevolve.ramsey_numbers_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2603.09172"
EXPECTED_SOURCE_TITLE = "Reinforced Generation of Combinatorial Structures: Ramsey Numbers"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2603.09172.pdf"
EXPECTED_SOURCE_FILE = "papers/2603.09172__Ramsey_Numbers.pdf"
EXPECTED_SOURCE_SHA256 = (
    "f133fe6f2b7db15fad214164359359f0e5ecbc0656b81bb6917c5c40df402ded"
)
EXPECTED_SOURCE_BYTES = 302923
EXPECTED_BOUNDARY_STATUS = "constructive_ramsey_context_without_graph_witness_parity"
EXPECTED_COMPONENT_IDS = (
    "ramsey_graph_candidates",
    "primary_and_prospect_graph_contract",
    "clique_independent_set_verifier",
    "ramsey_parameter_rows",
    "new_lower_bound_rows",
    "matched_bound_rows",
    "exact_bound_recovery_rows",
    "google_research_construction_links",
    "search_algorithm_code_links",
    "initialization_family_taxonomy",
    "prior_sota_baseline_rows",
    "graph_size_lower_bound_semantics",
    "algorithm_generated_witness_artifacts",
    "independent_checker_outputs",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "constructive_math_fixture_policy",
    "ramsey_candidate_representation",
    "run_return_contract",
    "primary_graph_witness_schema",
    "prospect_graph_schema",
    "clique_verifier_records",
    "independent_set_verifier_records",
    "ramsey_parameter_table_rows",
    "new_lower_bound_rows",
    "matched_best_known_rows",
    "exact_known_bound_recovery_rows",
    "graph_vertex_count_records",
    "implied_lower_bound_records",
    "off_by_one_semantics",
    "source_graph_artifact_hashes",
    "source_algorithm_artifact_hashes",
    "initialization_family_records",
    "prior_sota_baseline_citations",
    "search_budget_records",
    "random_seed_records",
    "algorithm_summary_audit_records",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "ramsey_candidate_schema": "not_implemented_locally",
    "ramsey_run_return_contract": "not_implemented_locally",
    "graph_witness_artifact_schema": "not_recorded_locally",
    "clique_independent_set_verifier": "not_implemented_locally",
    "ramsey_parameter_rows": "not_recorded_locally",
    "new_lower_bound_rows": "not_recorded_locally",
    "matched_best_known_rows": "not_recorded_locally",
    "exact_known_recovery_rows": "not_recorded_locally",
    "primary_graph_records": "not_recorded_locally",
    "prospect_graph_records": "not_recorded_locally",
    "source_graph_artifact_hashes": "not_recorded_locally",
    "source_algorithm_artifact_hashes": "not_recorded_locally",
    "initialization_family_taxonomy": "not_recorded_locally",
    "prior_sota_baseline_rows": "not_recorded_locally",
    "graph_size_lower_bound_semantics": "not_recorded_locally",
    "search_budget_records": "not_recorded_locally",
    "random_seed_records": "not_recorded_locally",
    "algorithm_summary_audit_records": "not_recorded_locally",
    "independent_checker_outputs": "not_recorded_locally",
    "local_google_research_artifact_snapshot": "not_recorded_locally",
}


@dataclass(frozen=True)
class RamseyNumbersBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RamseyNumbersBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[RamseyNumbersBoundaryIssue]


def ramsey_numbers_boundary_record() -> dict[str, Any]:
    """Return the current Ramsey-number discovery absence boundary."""

    return {
        "schema": RAMSEY_NUMBERS_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": [
            "Ansh Nagda",
            "Prabhakar Raghavan",
            "Abhradeep Thakurta",
        ],
        "source_version": "v5",
        "source_submitted_date": "2026-03-10",
        "source_last_revised_date": "2026-04-21",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2603.09172v5",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://github.com/google-research/google-research/tree/master/ramsey_number_bounds/improved_bounds",
                "status": "source_repository_reference_only_not_local_snapshot",
            },
            {
                "url": "https://github.com/google-research/google-research/tree/master/ramsey_number_bounds/code",
                "status": "source_repository_reference_only_not_local_snapshot",
            },
        ],
        "framework_components": [
            {
                "component_id": "ramsey_graph_candidates",
                "paper_role": "candidate programs generate Ramsey graph witnesses",
                "local_status": "not_implemented",
            },
            {
                "component_id": "primary_and_prospect_graph_contract",
                "paper_role": "program run() returns primary graph G1 and larger prospect graph G2",
                "local_status": "not_implemented",
            },
            {
                "component_id": "clique_independent_set_verifier",
                "paper_role": "verify absence of r-cliques and s-independent sets",
                "local_status": "not_implemented",
            },
            {
                "component_id": "ramsey_parameter_rows",
                "paper_role": "R(r,s) table rows for small Ramsey numbers",
                "local_status": "not_recorded",
            },
            {
                "component_id": "new_lower_bound_rows",
                "paper_role": "nine improved lower-bound rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "matched_bound_rows",
                "paper_role": "matched best-known lower-bound rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "exact_bound_recovery_rows",
                "paper_role": "recovered exact known lower-bound rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "google_research_construction_links",
                "paper_role": "public graph construction repository links",
                "local_status": "not_recorded",
            },
            {
                "component_id": "search_algorithm_code_links",
                "paper_role": "public AlphaEvolve-discovered search code repository links",
                "local_status": "not_recorded",
            },
            {
                "component_id": "initialization_family_taxonomy",
                "paper_role": "random/stochastic, algebraic, cyclic, and hybrid initialization families",
                "local_status": "not_recorded",
            },
            {
                "component_id": "prior_sota_baseline_rows",
                "paper_role": "prior lower-bound citation and graph-size rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "graph_size_lower_bound_semantics",
                "paper_role": "graph with n vertices proves R(r,s) >= n + 1",
                "local_status": "not_recorded",
            },
            {
                "component_id": "algorithm_generated_witness_artifacts",
                "paper_role": "generated search algorithms and witness graph artifacts",
                "local_status": "not_recorded",
            },
            {
                "component_id": "independent_checker_outputs",
                "paper_role": "independent verification of witness graph constraints",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_ramsey_runner": "<none>",
            "current_candidate_scope": "python_primary_generic_workspace_not_ramsey_graph_witness_api",
            "ramsey_candidate_schema_ready": False,
            "run_return_contract_ready": False,
            "graph_verifier_ready": False,
            "parameter_rows_ready": False,
            "new_lower_bound_rows_ready": False,
            "matched_bound_rows_ready": False,
            "exact_recovery_rows_ready": False,
            "source_artifact_snapshot_ready": False,
            "algorithm_summary_audit_ready": False,
            "independent_checker_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_improvements": [
            "R(3,13): 60 to 61",
            "R(3,18): 99 to 100",
            "R(4,13): 138 to 139",
            "R(4,14): 147 to 148",
            "R(4,15): 158 to 159",
            "R(4,16): 170 to 174",
            "R(4,18): 205 to 209",
            "R(4,19): 213 to 219",
            "R(4,20): 234 to 237",
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records Ramsey Numbers as AlphaEvolve constructive "
            "combinatorics context only. LibreEvolve currently does not claim "
            "Ramsey graph candidate schemas, run() primary/prospect graph "
            "contracts, clique/independent-set verifiers, new or matched "
            "lower-bound rows, exact-known-bound recovery evidence, graph "
            "artifact hashes, source algorithm artifact hashes, initialization "
            "family records, graph-size-to-Ramsey-lower-bound semantics, or "
            "independent checker outputs."
        ),
    }


def validate_ramsey_numbers_boundary(
    boundary: object | str | Path | None = None,
) -> RamseyNumbersBoundaryValidation:
    data, read_issues = _load_boundary(
        ramsey_numbers_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return RamseyNumbersBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[RamseyNumbersBoundaryIssue] = []
    if data.get("schema") != RAMSEY_NUMBERS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Ramsey Numbers boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2603.09172"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify Ramsey Numbers"))
    if data.get("source_version") != "v5":
        issues.append(_issue("invalid_source_version", "source_version must be v5"))
    if data.get("source_submitted_date") != "2026-03-10":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2026-03-10"))
    if data.get("source_last_revised_date") != "2026-04-21":
        issues.append(_issue("invalid_source_last_revised_date", "source_last_revised_date must be 2026-04-21"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached PDF"))
    if data.get("source_sha256") != EXPECTED_SOURCE_SHA256:
        issues.append(_issue("invalid_source_sha256", "source_sha256 must match the cached PDF digest"))
    if data.get("source_bytes") != EXPECTED_SOURCE_BYTES:
        issues.append(_issue("invalid_source_bytes", "source_bytes must match the cached PDF size"))
    if data.get("source_license") != "http://creativecommons.org/licenses/by/4.0/":
        issues.append(_issue("invalid_source_license", "source_license must match the cached PDF metadata"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Ramsey Numbers boundary must not claim graph-witness parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    _validate_reported_improvements(data.get("reported_improvements"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that Ramsey graph parity is not claimed"))
    return RamseyNumbersBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_ramsey_numbers_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_ramsey_numbers_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Ramsey Numbers boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| component_count | {validation.component_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RamseyNumbersBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Ramsey Numbers boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[RamseyNumbersBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    expected_urls = {
        "https://arxiv.org/abs/2603.09172v5",
        "https://github.com/google-research/google-research/tree/master/ramsey_number_bounds/improved_bounds",
        "https://github.com/google-research/google-research/tree/master/ramsey_number_bounds/code",
    }
    if urls != expected_urls:
        issues.append(_issue("source_link_mismatch", "source_links must preserve Ramsey source status"))
    allowed_statuses = {
        "source_version_reference_only",
        "source_repository_reference_only_not_local_snapshot",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") not in allowed_statuses:
            issues.append(_issue("source_link_status_overclaim", "source link status must not claim local Ramsey runtime"))


def _validate_framework_components(value: object, issues: list[RamseyNumbersBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the Ramsey component set"))
    allowed_statuses = {"not_implemented", "not_recorded"}
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS and item.get("local_status") not in allowed_statuses:
            issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim Ramsey parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[RamseyNumbersBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "current_ramsey_runner": "<none>",
        "current_candidate_scope": "python_primary_generic_workspace_not_ramsey_graph_witness_api",
        "ramsey_candidate_schema_ready": False,
        "run_return_contract_ready": False,
        "graph_verifier_ready": False,
        "parameter_rows_ready": False,
        "new_lower_bound_rows_ready": False,
        "matched_bound_rows_ready": False,
        "exact_recovery_rows_ready": False,
        "source_artifact_snapshot_ready": False,
        "algorithm_summary_audit_ready": False,
        "independent_checker_ready": False,
        "repository_runtime_verified": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current Ramsey boundary"))


def _validate_reported_improvements(value: object, issues: list[RamseyNumbersBoundaryIssue]) -> None:
    expected = [
        "R(3,13): 60 to 61",
        "R(3,18): 99 to 100",
        "R(4,13): 138 to 139",
        "R(4,14): 147 to 148",
        "R(4,15): 158 to 159",
        "R(4,16): 170 to 174",
        "R(4,18): 205 to 209",
        "R(4,19): 213 to 219",
        "R(4,20): 234 to 237",
    ]
    if value != expected:
        issues.append(_issue("reported_improvement_mismatch", "reported_improvements must preserve Ramsey result labels"))


def _validate_required_fields(
    value: object,
    issues: list[RamseyNumbersBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve Ramsey evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[RamseyNumbersBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve Ramsey artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> RamseyNumbersBoundaryIssue:
    return RamseyNumbersBoundaryIssue(code, message)
