from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


COMBINATORICS_BERCZY_BOUNDARY_SCHEMA = "libreevolve.combinatorics_berczy_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2603.06692"
EXPECTED_SOURCE_TITLE = (
    "Evolving Local Corrections for Global Constructions in Combinatorics"
)
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2603.06692.pdf"
EXPECTED_SOURCE_FILE = "papers/2603.06692__Combinatorics_Berczy.pdf"
EXPECTED_SOURCE_SHA256 = (
    "86e39ec4ae7e93dd88e1e44a0c8484c890be682ffb5396a4edb079103a68fb6f"
)
EXPECTED_SOURCE_BYTES = 813934
EXPECTED_BOUNDARY_STATUS = (
    "reported_combinatorics_experiments_without_local_harness_parity"
)
EXPECTED_COMPONENT_IDS = (
    "bipartite_graph_reconstruction_harness",
    "planar_graph_reconstruction_harness",
    "alon_tarsi_latin_square_involution_harness",
    "rota_basis_linear_matroid_harness",
    "candidate_certificate_representations",
    "local_correction_policy_api",
    "symmetry_scramble_worst_case_evaluation",
    "hard_negative_replay_buffers",
    "evolved_code_block_artifacts",
    "gemini_experiment_summary_artifacts",
    "reported_metric_tables",
    "conjecture_rows",
    "independent_verifier_outputs",
    "source_code_repository_snapshot",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "constructive_combinatorics_fixture_policy",
    "graph_deck_candidate_schema",
    "bipartite_matrix_deck_schema",
    "planar_graph_deck_schema",
    "latin_square_candidate_schema",
    "latin_trade_involution_schema",
    "rota_basis_matroid_instance_schema",
    "local_exchange_policy_schema",
    "symmetry_scramble_seed_records",
    "worst_case_aggregate_records",
    "hard_negative_replay_records",
    "bipartite_result_rows",
    "planar_result_rows",
    "alon_tarsi_result_rows",
    "rota_basis_result_rows",
    "evolved_block_source_hashes",
    "gemini_summary_hashes",
    "experiment_run_ids",
    "search_duration_records",
    "independent_verifier_outputs",
    "counterexample_or_loophole_audit_records",
    "proof_status_boundary",
)
EXPECTED_MISSING_EVIDENCE = {
    "bipartite_graph_reconstruction_harness": "not_implemented_locally",
    "planar_graph_reconstruction_harness": "not_implemented_locally",
    "alon_tarsi_involution_harness": "not_implemented_locally",
    "rota_basis_exchange_harness": "not_implemented_locally",
    "graph_deck_candidate_schema": "not_recorded_locally",
    "latin_square_candidate_schema": "not_recorded_locally",
    "rota_basis_matroid_instance_schema": "not_recorded_locally",
    "local_correction_policy_api": "not_implemented_locally",
    "symmetry_scramble_seed_records": "not_recorded_locally",
    "worst_case_aggregate_records": "not_recorded_locally",
    "hard_negative_replay_records": "not_recorded_locally",
    "bipartite_result_rows": "not_recorded_locally",
    "planar_result_rows": "not_recorded_locally",
    "alon_tarsi_result_rows": "not_recorded_locally",
    "rota_basis_result_rows": "not_recorded_locally",
    "evolved_block_source_hashes": "not_recorded_locally",
    "gemini_summary_hashes": "not_recorded_locally",
    "experiment_run_ids": "not_recorded_locally",
    "independent_verifier_outputs": "not_recorded_locally",
    "source_code_repository_snapshot": "not_recorded_locally",
}


@dataclass(frozen=True)
class CombinatoricsBerczyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CombinatoricsBerczyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CombinatoricsBerczyBoundaryIssue]


def combinatorics_berczy_boundary_record() -> dict[str, Any]:
    """Return the current Berczy combinatorics experiment absence boundary."""

    return {
        "schema": COMBINATORICS_BERCZY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": ["Gergely Berczi"],
        "source_version": "v1",
        "source_submitted_date": "2026-03-04",
        "source_last_revised_date": "2026-03-04",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2603.06692v1",
                "status": "source_version_reference_only",
            }
        ],
        "framework_components": [
            {
                "component_id": "bipartite_graph_reconstruction_harness",
                "paper_role": "deck-based bipartite matrix reconstruction benchmark",
                "local_status": "not_implemented",
            },
            {
                "component_id": "planar_graph_reconstruction_harness",
                "paper_role": "planar graph reconstruction benchmark with exact deck equality",
                "local_status": "not_implemented",
            },
            {
                "component_id": "alon_tarsi_latin_square_involution_harness",
                "paper_role": "Latin-square sign-flipping involution experiments",
                "local_status": "not_implemented",
            },
            {
                "component_id": "rota_basis_linear_matroid_harness",
                "paper_role": "Rota basis local-exchange policy experiments over F2",
                "local_status": "not_implemented",
            },
            {
                "component_id": "candidate_certificate_representations",
                "paper_role": "graphs, Latin squares, and basis-grid certificate objects",
                "local_status": "not_recorded",
            },
            {
                "component_id": "local_correction_policy_api",
                "paper_role": "evolved policies propose small correcting steps",
                "local_status": "not_implemented",
            },
            {
                "component_id": "symmetry_scramble_worst_case_evaluation",
                "paper_role": "random relabeling/isotopy scrambles with worst-case aggregation",
                "local_status": "not_recorded",
            },
            {
                "component_id": "hard_negative_replay_buffers",
                "paper_role": "persistent buffers of failed cases replayed in later generations",
                "local_status": "not_recorded",
            },
            {
                "component_id": "evolved_code_block_artifacts",
                "paper_role": "appendix evolve-block code excerpts and final policies",
                "local_status": "not_recorded",
            },
            {
                "component_id": "gemini_experiment_summary_artifacts",
                "paper_role": "Gemini-generated AlphaEvolve run summaries",
                "local_status": "not_recorded",
            },
            {
                "component_id": "reported_metric_tables",
                "paper_role": "Tables 1-6 and graph-reconstruction success rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "conjecture_rows",
                "paper_role": "Conjectures 4-11 extracted from experiment outcomes",
                "local_status": "not_recorded",
            },
            {
                "component_id": "independent_verifier_outputs",
                "paper_role": "local reruns or independent checks of reported algorithms",
                "local_status": "not_recorded",
            },
            {
                "component_id": "source_code_repository_snapshot",
                "paper_role": "external repository or notebook snapshot for harnesses and runs",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_combinatorics_runner": "<none>",
            "current_candidate_scope": "python_primary_generic_workspace_not_berczy_combinatorics_api",
            "bipartite_harness_ready": False,
            "planar_harness_ready": False,
            "alon_tarsi_harness_ready": False,
            "rota_basis_harness_ready": False,
            "candidate_schema_ready": False,
            "symmetry_scramble_records_ready": False,
            "hard_negative_replay_ready": False,
            "reported_metric_rows_ready": False,
            "evolved_block_artifacts_ready": False,
            "gemini_summary_artifacts_ready": False,
            "independent_verifier_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_results": [
            "bipartite matrix reconstruction: 1420/1420 successful reconstructions after about two days",
            "planar graph reconstruction: 896/896 successful reconstructions with worst-of-5 scrambles",
            "Alon-Tarsi Experiment 1: validity and involution rates 1.00 for n in {8,10,12,14,26}",
            "Alon-Tarsi Experiment 3: flip rate 1.00 for n in {10,12,14,26} and 0.98 for n=8",
            "Rota Basis Experiment A rank 5: overall success rate 1.00",
            "Rota Basis Experiment B rank 7: overall success rate 1.00",
            "Rota Basis Experiment C ranks {5,7,9,11,13}: overall success rate 1.00",
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the Berczy combinatorics paper as "
            "AlphaEvolve-assisted experimental-math context only. LibreEvolve "
            "currently does not claim bipartite or planar graph-reconstruction "
            "harnesses, Alon-Tarsi Latin-square involution harnesses, Rota-basis "
            "linear-matroid exchange harnesses, candidate certificate schemas, "
            "symmetry-scramble records, hard-negative replay buffers, evolved "
            "code-block artifact hashes, Gemini summary artifacts, reported "
            "metric rows, conjecture/proof-status ledgers, repository snapshots, "
            "or independent verifier outputs."
        ),
    }


def validate_combinatorics_berczy_boundary(
    boundary: object | str | Path | None = None,
) -> CombinatoricsBerczyBoundaryValidation:
    data, read_issues = _load_boundary(
        combinatorics_berczy_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CombinatoricsBerczyBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CombinatoricsBerczyBoundaryIssue] = []
    if data.get("schema") != COMBINATORICS_BERCZY_BOUNDARY_SCHEMA:
        issues.append(
            CombinatoricsBerczyBoundaryIssue(
                "schema_mismatch",
                "Berczy boundary schema must match the committed contract",
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
                CombinatoricsBerczyBoundaryIssue(
                    f"{field}_mismatch",
                    f"{field} must match the local cached Berczy source evidence",
                )
            )
    if data.get("claim_ready") is not False:
        issues.append(
            CombinatoricsBerczyBoundaryIssue(
                "claim_ready_overclaim",
                "Berczy combinatorics benchmark parity is not claim-ready",
            )
        )
    _validate_source_links(data, issues)
    _validate_components(data, issues)
    _validate_local_evidence(data, issues)
    _validate_missing_evidence(data, issues)
    required = data.get("required_evidence_fields")
    if tuple(required or ()) != EXPECTED_REQUIRED_EVIDENCE_FIELDS:
        issues.append(
            CombinatoricsBerczyBoundaryIssue(
                "required_evidence_fields_mismatch",
                "required evidence fields must remain source-specific and complete",
            )
        )
    return CombinatoricsBerczyBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status")
        if isinstance(data.get("boundary_status"), str)
        else None,
        component_count=len(data.get("framework_components") or []),
        required_evidence_field_count=len(required or []),
        missing_evidence_count=len(data.get("missing_evidence") or {}),
        issues=issues,
    )


def render_combinatorics_berczy_boundary_summary(boundary: object | str | Path | None = None) -> str:
    validation = validate_combinatorics_berczy_boundary(boundary)
    rows = [
        ("schema_status", "ok" if validation.ok else "invalid"),
        ("boundary_status", validation.boundary_status or "<missing>"),
        ("component_count", str(validation.component_count)),
        ("required_evidence_field_count", str(validation.required_evidence_field_count)),
        ("missing_evidence_count", str(validation.missing_evidence_count)),
    ]
    lines = ["# Combinatorics Berczy boundary", "", "| field | value |", "| --- | --- |"]
    lines.extend(f"| {field} | {value} |" for field, value in rows)
    if validation.issues:
        lines.extend(["", "## Issues"])
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object,
) -> tuple[dict[str, Any] | None, list[CombinatoricsBerczyBoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            return json.loads(boundary.read_text(encoding="utf-8")), []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, [
                CombinatoricsBerczyBoundaryIssue(
                    "read_error", f"Could not read Berczy boundary: {exc}"
                )
            ]
    if isinstance(boundary, str):
        return _load_boundary(Path(boundary))
    if isinstance(boundary, dict):
        return boundary, []
    return None, [
        CombinatoricsBerczyBoundaryIssue(
            "invalid_boundary_type", "Berczy boundary must be a dict or JSON path"
        )
    ]


def _validate_source_links(
    data: dict[str, Any], issues: list[CombinatoricsBerczyBoundaryIssue]
) -> None:
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        issues.append(
            CombinatoricsBerczyBoundaryIssue(
                "source_links_missing", "Berczy boundary must record source links"
            )
        )
        return
    for link in source_links:
        status = link.get("status") if isinstance(link, dict) else None
        if status != "source_version_reference_only":
            issues.append(
                CombinatoricsBerczyBoundaryIssue(
                    "source_link_status_overclaim",
                    "Berczy source links are reference-only until local source snapshots exist",
                )
            )


def _validate_components(
    data: dict[str, Any], issues: list[CombinatoricsBerczyBoundaryIssue]
) -> None:
    components = data.get("framework_components")
    if not isinstance(components, list):
        issues.append(
            CombinatoricsBerczyBoundaryIssue(
                "framework_components_missing", "framework components must be a list"
            )
        )
        return
    ids = tuple(component.get("component_id") for component in components if isinstance(component, dict))
    if ids != EXPECTED_COMPONENT_IDS:
        issues.append(
            CombinatoricsBerczyBoundaryIssue(
                "framework_component_ids_mismatch",
                "framework component ids must match the Berczy evidence boundary",
            )
        )
    for component in components:
        status = component.get("local_status") if isinstance(component, dict) else None
        if status not in {"not_implemented", "not_recorded"}:
            issues.append(
                CombinatoricsBerczyBoundaryIssue(
                    "framework_component_overclaim",
                    "Berczy components must remain not_implemented/not_recorded",
                )
            )


def _validate_local_evidence(
    data: dict[str, Any], issues: list[CombinatoricsBerczyBoundaryIssue]
) -> None:
    evidence = data.get("local_evidence")
    if not isinstance(evidence, dict):
        issues.append(
            CombinatoricsBerczyBoundaryIssue(
                "local_evidence_missing", "local evidence must be a dict"
            )
        )
        return
    for field in (
        "bipartite_harness_ready",
        "planar_harness_ready",
        "alon_tarsi_harness_ready",
        "rota_basis_harness_ready",
        "candidate_schema_ready",
        "independent_verifier_ready",
        "repository_runtime_verified",
    ):
        if evidence.get(field) is not False:
            issues.append(
                CombinatoricsBerczyBoundaryIssue(
                    f"local_evidence_{field}_overclaim",
                    f"{field} must remain false until local Berczy parity evidence exists",
                )
            )


def _validate_missing_evidence(
    data: dict[str, Any], issues: list[CombinatoricsBerczyBoundaryIssue]
) -> None:
    missing = data.get("missing_evidence")
    if missing != EXPECTED_MISSING_EVIDENCE:
        issues.append(
            CombinatoricsBerczyBoundaryIssue(
                "missing_evidence_mismatch",
                "missing evidence must match the Berczy absence boundary",
            )
        )
