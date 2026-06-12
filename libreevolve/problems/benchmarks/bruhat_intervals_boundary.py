from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BRUHAT_INTERVALS_BOUNDARY_SCHEMA = "libreevolve.bruhat_intervals_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2601.01235"
EXPECTED_SOURCE_TITLE = "Bruhat intervals that are large hypercubes"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2601.01235.pdf"
EXPECTED_SOURCE_FILE = "papers/2601.01235__Bruhat_Intervals.pdf"
EXPECTED_SOURCE_SHA256 = (
    "a5ff203da843a73bc0b6f5568be7320963e5f4f45bff11f5d2ce39ec08b0ef64"
)
EXPECTED_SOURCE_BYTES = 735975
EXPECTED_BOUNDARY_STATUS = "constructive_math_context_without_local_bruhat_hypercube_benchmark"
EXPECTED_COMPONENT_IDS = (
    "permutation_pair_candidate_schema",
    "simple_reflection_word_decoder",
    "d_invariant_evaluator",
    "bruhat_order_ehresmann_matrix",
    "bruhat_interval_witness_generator",
    "dyadic_basic_interval_checker",
    "dyadically_well_distributed_checker",
    "fundamental_block_validator",
    "complementary_block_flip_validator",
    "poset_hypercube_isomorphism_checker",
    "kazhdan_lusztig_r_polynomial_linkage",
    "cluster_algebra_consequence_rows",
    "alphaevolve_experiment_provenance",
    "public_artifact_snapshot",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "constructive_math_fixture_policy",
    "permutation_pair_schema",
    "simple_reflection_word_schema",
    "bruhat_order_definition_records",
    "ehresmann_matrix_comparison_records",
    "x_m_y_m_generator_records",
    "dyadic_basic_interval_records",
    "dyadically_well_distributed_records",
    "fundamental_block_validation_records",
    "complementary_block_flip_records",
    "poset_hypercube_isomorphism_records",
    "dimension_formula_records",
    "d_invariant_records",
    "kazhdan_lusztig_r_polynomial_records",
    "cluster_algebra_consequence_records",
    "bruhat_graph_embedding_consequence_records",
    "small_n_table_rows",
    "alphaevolve_prompt_records",
    "model_call_and_budget_records",
    "public_artifact_hashes",
    "finite_test_vs_general_proof_status",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "permutation_pair_candidate_schema": "not_implemented_locally",
    "simple_reflection_word_decoder": "not_implemented_locally",
    "d_invariant_evaluator": "not_implemented_locally",
    "bruhat_order_verifier": "not_implemented_locally",
    "ehresmann_matrix_records": "not_recorded_locally",
    "x_m_y_m_generator": "not_implemented_locally",
    "dyadic_basic_interval_checker": "not_implemented_locally",
    "dyadically_well_distributed_checker": "not_implemented_locally",
    "fundamental_block_validator": "not_implemented_locally",
    "complementary_block_flip_validator": "not_implemented_locally",
    "bruhat_interval_witness_artifacts": "not_recorded_locally",
    "poset_hypercube_isomorphism_checker": "not_implemented_locally",
    "dimension_formula_verifier": "not_implemented_locally",
    "kazhdan_lusztig_r_polynomial_linkage": "not_recorded_locally",
    "cluster_algebra_consequence_rows": "not_recorded_locally",
    "bruhat_graph_embedding_consequence_rows": "not_recorded_locally",
    "alphaevolve_prompt_and_lineage_records": "not_recorded_locally",
    "public_artifact_hashes": "not_recorded_locally",
    "independent_checker_outputs": "not_recorded_locally",
    "local_repository_or_notebook_snapshot": "not_recorded_locally",
}


@dataclass(frozen=True)
class BruhatIntervalsBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class BruhatIntervalsBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[BruhatIntervalsBoundaryIssue]


def bruhat_intervals_boundary_record() -> dict[str, Any]:
    """Return the current Bruhat-interval hypercube absence boundary."""

    return {
        "schema": BRUHAT_INTERVALS_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": [
            "Jordan Ellenberg",
            "Nicolas Libedinsky",
            "David Plaza",
            "Jose Simental",
            "Geordie Williamson",
        ],
        "source_version": "v1",
        "source_submitted_date": "2026-01-03",
        "source_last_revised_date": "2026-01-03",
        "source_pdf_date": "2026-01-06",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2601.01235v1",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://github.com/kitft/funsearch",
                "status": "related_funsearch_reference_only",
            },
            {
                "url": "https://github.com/JSEllenberg/Bruhat-hypercubes/tree/main",
                "status": "public_artifact_reference_only",
            },
        ],
        "framework_components": [
            {
                "component_id": "permutation_pair_candidate_schema",
                "paper_role": "candidate programs emit permutation pairs in symmetric groups",
                "local_status": "not_implemented",
            },
            {
                "component_id": "simple_reflection_word_decoder",
                "paper_role": "FunSearch experiments decode lists of simple reflections into permutations",
                "local_status": "not_implemented",
            },
            {
                "component_id": "d_invariant_evaluator",
                "paper_role": "score pairs by the Kazhdan-Lusztig d-invariant",
                "local_status": "not_implemented",
            },
            {
                "component_id": "bruhat_order_ehresmann_matrix",
                "paper_role": "compare permutations with Ehresmann matrix inequalities",
                "local_status": "not_implemented",
            },
            {
                "component_id": "bruhat_interval_witness_generator",
                "paper_role": "generate x_m and y_m bit-reversal affine endpoints",
                "local_status": "not_implemented",
            },
            {
                "component_id": "dyadic_basic_interval_checker",
                "paper_role": "check basic intervals in [2^m] and exact-one block conditions",
                "local_status": "not_implemented",
            },
            {
                "component_id": "dyadically_well_distributed_checker",
                "paper_role": "recognize D_m vertices by digitwise distribution",
                "local_status": "not_implemented",
            },
            {
                "component_id": "fundamental_block_validator",
                "paper_role": "verify each fundamental block has exactly one permutation-matrix entry",
                "local_status": "not_implemented",
            },
            {
                "component_id": "complementary_block_flip_validator",
                "paper_role": "verify complementary-block flips and length changes",
                "local_status": "not_implemented",
            },
            {
                "component_id": "poset_hypercube_isomorphism_checker",
                "paper_role": "validate phi: D_m -> S_2^C_m as a poset isomorphism",
                "local_status": "not_implemented",
            },
            {
                "component_id": "kazhdan_lusztig_r_polynomial_linkage",
                "paper_role": "connect interval dimension to R-polynomial coefficient bounds",
                "local_status": "not_recorded",
            },
            {
                "component_id": "cluster_algebra_consequence_rows",
                "paper_role": "record frozen-variable lower-bound consequences",
                "local_status": "not_recorded",
            },
            {
                "component_id": "alphaevolve_experiment_provenance",
                "paper_role": "record AlphaEvolve prompt, model calls, program counts, and cost",
                "local_status": "not_recorded",
            },
            {
                "component_id": "public_artifact_snapshot",
                "paper_role": "snapshot the public program, output, and prompt repository",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_bruhat_runner": "<none>",
            "current_candidate_scope": "python_primary_generic_workspace_not_bruhat_interval_api",
            "permutation_pair_schema_ready": False,
            "simple_reflection_decoder_ready": False,
            "d_invariant_evaluator_ready": False,
            "bruhat_order_verifier_ready": False,
            "ehresmann_matrix_records_ready": False,
            "x_y_generator_ready": False,
            "dyadic_checker_ready": False,
            "hypercube_isomorphism_ready": False,
            "dimension_formula_ready": False,
            "alphaevolve_provenance_ready": False,
            "public_artifact_snapshot_ready": False,
            "independent_checker_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_result": {
            "group_family": "S_{2^m}",
            "main_interval": "D_m = [x_m, y_m]",
            "vertex_characterization": "dyadically well-distributed permutations",
            "hypercube_dimension": "m * 2^(m-1)",
            "upper_bound_context": "within a constant factor of m * 2^m",
            "alpha_recurrence": "alpha(2n) = 2 alpha(n) + n",
            "tested_power_formula": "alpha(2^m) = m * 2^(m-1)",
            "alphaevolve_program_count": "3000-5000",
            "alphaevolve_models": "Gemini 2.5 Flash and Gemini 2.5 Pro",
            "alphaevolve_estimated_cost_usd": 70,
            "funsearch_estimated_cost_usd": 10,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records Bruhat Intervals as AlphaEvolve-discovered "
            "constructive math context only. LibreEvolve currently does not "
            "claim permutation-pair candidate schemas, simple-reflection "
            "decoding, d-invariant evaluation, Bruhat order or Ehresmann "
            "matrix verification, x_m/y_m witness generation, dyadic interval "
            "checks, dyadically well-distributed permutation checks, "
            "fundamental/complementary block validators, poset-hypercube "
            "isomorphism checks, Kazhdan-Lusztig R-polynomial linkage rows, "
            "cluster-algebra or Bruhat-graph consequence records, "
            "AlphaEvolve prompt/model/budget provenance, public artifact "
            "hashes, or independent checker outputs."
        ),
    }


def validate_bruhat_intervals_boundary(
    boundary: object | str | Path | None = None,
) -> BruhatIntervalsBoundaryValidation:
    data, read_issues = _load_boundary(
        bruhat_intervals_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return BruhatIntervalsBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[BruhatIntervalsBoundaryIssue] = []
    for field, expected in (
        ("schema", BRUHAT_INTERVALS_BOUNDARY_SCHEMA),
        ("source_paper_id", EXPECTED_SOURCE_PAPER_ID),
        ("source_title", EXPECTED_SOURCE_TITLE),
        ("source_version", "v1"),
        ("source_submitted_date", "2026-01-03"),
        ("source_last_revised_date", "2026-01-03"),
        ("source_pdf_date", "2026-01-06"),
        ("source_url", EXPECTED_SOURCE_URL),
        ("source_file", EXPECTED_SOURCE_FILE),
        ("source_sha256", EXPECTED_SOURCE_SHA256),
        ("source_bytes", EXPECTED_SOURCE_BYTES),
        ("source_license", "http://arxiv.org/licenses/nonexclusive-distrib/1.0/"),
        ("boundary_status", EXPECTED_BOUNDARY_STATUS),
    ):
        if data.get(field) != expected:
            issues.append(
                BruhatIntervalsBoundaryIssue(
                    f"{field}_mismatch",
                    f"{field} must match the cached Bruhat Intervals source evidence",
                )
            )
    if data.get("claim_ready") is not False:
        issues.append(
            BruhatIntervalsBoundaryIssue(
                "claim_ready_overclaim",
                "Bruhat Intervals benchmark parity is not claim-ready",
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
            BruhatIntervalsBoundaryIssue(
                "required_evidence_fields_mismatch",
                "required evidence fields must remain source-specific and complete",
            )
        )
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(
            BruhatIntervalsBoundaryIssue(
                "claim_boundary_missing",
                "claim_boundary must state that Bruhat parity is not claimed",
            )
        )
    return BruhatIntervalsBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status")
        if isinstance(data.get("boundary_status"), str)
        else None,
        component_count=len(data.get("framework_components") or []),
        required_evidence_field_count=len(required or []),
        missing_evidence_count=len(data.get("missing_evidence") or {}),
        issues=issues,
    )


def render_bruhat_intervals_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    validation = validate_bruhat_intervals_boundary(boundary)
    lines = [
        "# Bruhat Intervals boundary",
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
) -> tuple[dict[str, Any] | None, list[BruhatIntervalsBoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            return json.loads(boundary.read_text(encoding="utf-8")), []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, [
                BruhatIntervalsBoundaryIssue(
                    "read_error", f"Could not read Bruhat Intervals boundary: {exc}"
                )
            ]
    if isinstance(boundary, str):
        if boundary.strip().startswith("{"):
            try:
                data = json.loads(boundary)
            except json.JSONDecodeError as exc:
                return None, [
                    BruhatIntervalsBoundaryIssue(
                        "json_error", f"Could not parse Bruhat Intervals boundary: {exc}"
                    )
                ]
            if isinstance(data, dict):
                return data, []
            return None, [
                BruhatIntervalsBoundaryIssue(
                    "invalid_boundary_shape",
                    "Bruhat Intervals boundary JSON must be an object",
                )
            ]
        return _load_boundary(Path(boundary))
    if isinstance(boundary, dict):
        return boundary, []
    return None, [
        BruhatIntervalsBoundaryIssue(
            "invalid_boundary_type",
            "Bruhat Intervals boundary must be a dict, JSON string, or JSON path",
        )
    ]


def _validate_source_links(
    data: dict[str, Any], issues: list[BruhatIntervalsBoundaryIssue]
) -> None:
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        issues.append(
            BruhatIntervalsBoundaryIssue(
                "source_links_missing",
                "Bruhat Intervals boundary must record source and artifact links",
            )
        )
        return
    expected_urls = {
        "https://arxiv.org/abs/2601.01235v1",
        "https://github.com/kitft/funsearch",
        "https://github.com/JSEllenberg/Bruhat-hypercubes/tree/main",
    }
    urls = {link.get("url") for link in source_links if isinstance(link, dict)}
    if urls != expected_urls:
        issues.append(
            BruhatIntervalsBoundaryIssue(
                "source_links_mismatch",
                "source links must preserve Bruhat Intervals paper and artifact references",
            )
        )
    allowed_statuses = {
        "source_version_reference_only",
        "related_funsearch_reference_only",
        "public_artifact_reference_only",
    }
    for link in source_links:
        status = link.get("status") if isinstance(link, dict) else None
        if status not in allowed_statuses:
            issues.append(
                BruhatIntervalsBoundaryIssue(
                    "source_link_status_overclaim",
                    "Bruhat Intervals links are reference-only until local snapshots and checker evidence exist",
                )
            )


def _validate_components(
    data: dict[str, Any], issues: list[BruhatIntervalsBoundaryIssue]
) -> None:
    components = data.get("framework_components")
    if not isinstance(components, list):
        issues.append(
            BruhatIntervalsBoundaryIssue(
                "framework_components_missing",
                "framework_components must be a list",
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
            BruhatIntervalsBoundaryIssue(
                "framework_component_ids_mismatch",
                "framework component ids must match the Bruhat Intervals evidence boundary",
            )
        )
    for component in components:
        status = component.get("local_status") if isinstance(component, dict) else None
        if status not in {"not_implemented", "not_recorded"}:
            issues.append(
                BruhatIntervalsBoundaryIssue(
                    "framework_component_overclaim",
                    "Bruhat Intervals components must remain not_implemented/not_recorded",
                )
            )


def _validate_local_evidence(
    data: dict[str, Any], issues: list[BruhatIntervalsBoundaryIssue]
) -> None:
    evidence = data.get("local_evidence")
    if not isinstance(evidence, dict):
        issues.append(
            BruhatIntervalsBoundaryIssue(
                "local_evidence_missing", "local_evidence must be a dict"
            )
        )
        return
    for field in (
        "permutation_pair_schema_ready",
        "simple_reflection_decoder_ready",
        "d_invariant_evaluator_ready",
        "bruhat_order_verifier_ready",
        "ehresmann_matrix_records_ready",
        "x_y_generator_ready",
        "dyadic_checker_ready",
        "hypercube_isomorphism_ready",
        "dimension_formula_ready",
        "alphaevolve_provenance_ready",
        "public_artifact_snapshot_ready",
        "independent_checker_ready",
        "repository_runtime_verified",
    ):
        if evidence.get(field) is not False:
            issues.append(
                BruhatIntervalsBoundaryIssue(
                    f"local_evidence_{field}_overclaim",
                    f"{field} must remain false until local Bruhat Intervals evidence exists",
                )
            )


def _validate_reported_result(
    data: dict[str, Any], issues: list[BruhatIntervalsBoundaryIssue]
) -> None:
    result = data.get("reported_result")
    if not isinstance(result, dict):
        issues.append(
            BruhatIntervalsBoundaryIssue(
                "reported_result_missing", "reported_result must be a dict"
            )
        )
        return
    expected = {
        "group_family": "S_{2^m}",
        "main_interval": "D_m = [x_m, y_m]",
        "hypercube_dimension": "m * 2^(m-1)",
        "alpha_recurrence": "alpha(2n) = 2 alpha(n) + n",
        "tested_power_formula": "alpha(2^m) = m * 2^(m-1)",
        "alphaevolve_program_count": "3000-5000",
        "alphaevolve_models": "Gemini 2.5 Flash and Gemini 2.5 Pro",
        "alphaevolve_estimated_cost_usd": 70,
    }
    for field, expected_value in expected.items():
        if result.get(field) != expected_value:
            issues.append(
                BruhatIntervalsBoundaryIssue(
                    f"reported_result_{field}_mismatch",
                    f"reported_result.{field} must match the source-reported Bruhat Intervals result",
                )
            )


def _validate_missing_evidence(
    data: dict[str, Any], issues: list[BruhatIntervalsBoundaryIssue]
) -> None:
    if data.get("missing_evidence") != EXPECTED_MISSING_EVIDENCE:
        issues.append(
            BruhatIntervalsBoundaryIssue(
                "missing_evidence_mismatch",
                "missing evidence must match the Bruhat Intervals absence boundary",
            )
        )
