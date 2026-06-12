from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TTT_DISCOVER_BOUNDARY_SCHEMA = "libreevolve.ttt_discover_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2601.16175"
EXPECTED_SOURCE_TITLE = "Learning to Discover at Test Time"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2601.16175.pdf"
EXPECTED_SOURCE_FILE = "papers/2601.16175__TTT_Discover.pdf"
EXPECTED_SOURCE_SHA256 = (
    "4656ec28d800002d9a3e3f83a71c7d9032ef5f1873cd953b8808a8391ce06ec7"
)
EXPECTED_SOURCE_BYTES = 1286088
EXPECTED_BOUNDARY_STATUS = "test_time_training_context_without_local_policy_update_runtime"
EXPECTED_COMPONENT_IDS = (
    "test_time_training_policy_updates",
    "single_problem_rl_environment",
    "continuous_reward_problem_contract",
    "state_reuse_search_subroutine",
    "promising_solution_prioritization_objective",
    "tinker_training_runtime",
    "gpt_oss_120b_open_model_setup",
    "mathematics_benchmark_rows",
    "gpu_kernel_benchmark_rows",
    "atcoder_algorithm_benchmark_rows",
    "single_cell_denoising_benchmark_rows",
    "expert_or_organizer_review_records",
    "public_code_reproduction_artifacts",
    "best_of_n_baseline_comparisons",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "test_time_discovery_fixture_policy",
    "problem_description_schema",
    "candidate_state_schema",
    "continuous_reward_schema",
    "sota_baseline_records",
    "discovery_threshold_records",
    "policy_update_trace_records",
    "rl_training_runtime_records",
    "tinker_api_run_records",
    "open_model_backend_records",
    "state_reuse_records",
    "sample_budget_records",
    "best_of_n_comparator_records",
    "mathematics_result_rows",
    "gpu_kernel_result_rows",
    "atcoder_result_rows",
    "biology_result_rows",
    "expert_review_records",
    "organizer_review_records",
    "public_code_artifact_hashes",
    "cost_records",
    "independent_reproduction_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "test_time_training_policy_update_loop": "not_implemented_locally",
    "single_problem_rl_environment": "not_implemented_locally",
    "continuous_reward_problem_contract": "not_implemented_locally",
    "candidate_state_schema": "not_implemented_locally",
    "sota_baseline_records": "not_recorded_locally",
    "discovery_threshold_records": "not_recorded_locally",
    "state_reuse_search_subroutine": "not_implemented_locally",
    "sample_budget_records": "not_recorded_locally",
    "best_of_n_comparator_records": "not_recorded_locally",
    "tinker_runtime_records": "not_recorded_locally",
    "open_model_backend_records": "not_recorded_locally",
    "mathematics_result_rows": "not_recorded_locally",
    "gpu_kernel_result_rows": "not_recorded_locally",
    "atcoder_result_rows": "not_recorded_locally",
    "biology_result_rows": "not_recorded_locally",
    "expert_review_records": "not_recorded_locally",
    "public_code_artifact_hashes": "not_recorded_locally",
    "cost_records": "not_recorded_locally",
    "independent_reproduction_outputs": "not_recorded_locally",
    "local_repository_or_notebook_snapshot": "not_recorded_locally",
}


@dataclass(frozen=True)
class TTTDiscoverBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class TTTDiscoverBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[TTTDiscoverBoundaryIssue]


def ttt_discover_boundary_record() -> dict[str, Any]:
    """Return the current TTT-Discover absence boundary."""

    return {
        "schema": TTT_DISCOVER_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": [
            "Mert Yuksekgonul",
            "Daniel Koceja",
            "Xinhao Li",
            "Federico Bianchi",
            "Jed McCaleb",
            "Xiaolong Wang",
            "Jan Kautz",
            "Yejin Choi",
            "James Zou",
            "Carlos Guestrin",
            "Yu Sun",
        ],
        "source_version": "v2",
        "source_submitted_date": "2026-01-22",
        "source_last_revised_date": "2026-02-05",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2601.16175v2",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://github.com/test-time-training/discover",
                "status": "public_code_reference_only",
            },
            {
                "url": "https://test-time-training.github.io/discover",
                "status": "project_page_reference_only",
            },
            {
                "url": "https://github.com/test-time-training/discover/blob/main/results/mathematics/Results.ipynb",
                "status": "result_artifact_reference_only",
            },
            {
                "url": "https://github.com/test-time-training/discover/blob/main/results/kernel-engineering/",
                "status": "result_artifact_reference_only",
            },
            {
                "url": "https://github.com/test-time-training/discover/blob/main/results/algorithm-design/",
                "status": "result_artifact_reference_only",
            },
            {
                "url": "https://github.com/test-time-training/discover/blob/main/results/denoising/",
                "status": "result_artifact_reference_only",
            },
            {
                "url": "https://atcoder.jp/contests/ahc039/submissions/72633477",
                "status": "official_submission_reference_only",
            },
            {
                "url": "https://atcoder.jp/contests/ahc058/submissions/72633508",
                "status": "official_submission_reference_only",
            },
        ],
        "framework_components": [
            {
                "component_id": "test_time_training_policy_updates",
                "paper_role": "Algorithm 1 updates policy weights theta_i after each scored attempt",
                "local_status": "not_implemented",
            },
            {
                "component_id": "single_problem_rl_environment",
                "paper_role": "one test problem induces reward and transition functions",
                "local_status": "not_implemented",
            },
            {
                "component_id": "continuous_reward_problem_contract",
                "paper_role": "candidate states receive continuous rewards and validity failures score zero",
                "local_status": "not_implemented",
            },
            {
                "component_id": "state_reuse_search_subroutine",
                "paper_role": "PUCT/state reuse samples prior states and context from the attempt buffer",
                "local_status": "not_implemented",
            },
            {
                "component_id": "promising_solution_prioritization_objective",
                "paper_role": "adaptive entropic objective prioritizes maximum-discovery outcomes",
                "local_status": "not_implemented",
            },
            {
                "component_id": "tinker_training_runtime",
                "paper_role": "test-time training runs through the Tinker API",
                "local_status": "not_recorded",
            },
            {
                "component_id": "gpt_oss_120b_open_model_setup",
                "paper_role": "OpenAI gpt-oss-120b with LoRA rank 32 and rollout/training settings",
                "local_status": "not_recorded",
            },
            {
                "component_id": "mathematics_benchmark_rows",
                "paper_role": "Erdos minimum overlap, autocorrelation, and circle-packing result rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "gpu_kernel_benchmark_rows",
                "paper_role": "GPUMode TriMul and MLA Decode kernel-engineering result rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "atcoder_algorithm_benchmark_rows",
                "paper_role": "AHC039 and AHC058 algorithm-engineering official-submission rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "single_cell_denoising_benchmark_rows",
                "paper_role": "OpenProblems-style single-cell denoising rows and constraints",
                "local_status": "not_recorded",
            },
            {
                "component_id": "expert_or_organizer_review_records",
                "paper_role": "human expert or competition-organizer reviews of generated solutions",
                "local_status": "not_recorded",
            },
            {
                "component_id": "public_code_reproduction_artifacts",
                "paper_role": "public result notebooks, code folders, and artifact hashes",
                "local_status": "not_recorded",
            },
            {
                "component_id": "best_of_n_baseline_comparisons",
                "paper_role": "Best-of-25600 and OpenEvolve comparisons at matched sampling budget",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_ttt_discover_runner": "<none>",
            "current_candidate_scope": "python_primary_generic_workspace_not_mutable_llm_policy_runtime",
            "policy_update_loop_ready": False,
            "single_problem_rl_environment_ready": False,
            "continuous_reward_contract_ready": False,
            "state_reuse_ready": False,
            "sample_budget_records_ready": False,
            "benchmark_rows_ready": False,
            "expert_review_records_ready": False,
            "public_code_snapshot_ready": False,
            "tinker_runtime_verified": False,
            "open_model_backend_verified": False,
            "independent_reproduction_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_method": {
            "algorithm": "Test-Time Training to Discover",
            "training_steps": 50,
            "rollouts_per_step": 512,
            "baseline_sampling_budget": "Best-of-25600",
            "model": "OpenAI gpt-oss-120b",
            "runtime_api": "Tinker",
            "lora_rank": 32,
            "reuse_method": "PUCT",
            "objective": "adaptive entropic utility with KL penalty",
            "cost_claim": "few hundred dollars per problem",
        },
        "reported_results": [
            "Erdos minimum overlap improved to 0.380876",
            "First autocorrelation inequality improved to 1.50287",
            "TriMul A100 runtime reported as 2198.2 microseconds",
            "TriMul H100 runtime reported as 1161.2 microseconds",
            "AHC039 score reported as 567062",
            "AHC058 score reported as 848414228",
            "single-cell denoising score reported as 0.71 in headline table",
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records TTT-Discover as test-time discovery context "
            "only. LibreEvolve currently does not claim test-time policy weight "
            "updates, a single-problem RL environment, continuous-reward problem "
            "contracts, PUCT state-reuse traces, adaptive entropic training "
            "objective execution, Tinker training-run evidence, gpt-oss-120b "
            "LoRA backend records, matched Best-of-N or OpenEvolve comparator "
            "rows, mathematics/kernel/AtCoder/biology benchmark result rows, "
            "expert or organizer review records, public-code artifact hashes, "
            "cost records, or independent reproduction outputs."
        ),
    }


def validate_ttt_discover_boundary(
    boundary: object | str | Path | None = None,
) -> TTTDiscoverBoundaryValidation:
    data, read_issues = _load_boundary(
        ttt_discover_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return TTTDiscoverBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[TTTDiscoverBoundaryIssue] = []
    for field, expected in (
        ("schema", TTT_DISCOVER_BOUNDARY_SCHEMA),
        ("source_paper_id", EXPECTED_SOURCE_PAPER_ID),
        ("source_title", EXPECTED_SOURCE_TITLE),
        ("source_version", "v2"),
        ("source_submitted_date", "2026-01-22"),
        ("source_last_revised_date", "2026-02-05"),
        ("source_url", EXPECTED_SOURCE_URL),
        ("source_file", EXPECTED_SOURCE_FILE),
        ("source_sha256", EXPECTED_SOURCE_SHA256),
        ("source_bytes", EXPECTED_SOURCE_BYTES),
        ("source_license", "http://creativecommons.org/licenses/by/4.0/"),
        ("boundary_status", EXPECTED_BOUNDARY_STATUS),
    ):
        if data.get(field) != expected:
            issues.append(
                TTTDiscoverBoundaryIssue(
                    f"{field}_mismatch",
                    f"{field} must match the cached TTT-Discover source evidence",
                )
            )
    if data.get("claim_ready") is not False:
        issues.append(
            TTTDiscoverBoundaryIssue(
                "claim_ready_overclaim",
                "TTT-Discover runtime parity is not claim-ready",
            )
        )
    _validate_source_links(data, issues)
    _validate_components(data, issues)
    _validate_local_evidence(data, issues)
    _validate_reported_method(data, issues)
    _validate_reported_results(data, issues)
    _validate_missing_evidence(data, issues)
    required = data.get("required_evidence_fields")
    if tuple(required or ()) != EXPECTED_REQUIRED_EVIDENCE_FIELDS:
        issues.append(
            TTTDiscoverBoundaryIssue(
                "required_evidence_fields_mismatch",
                "required evidence fields must remain source-specific and complete",
            )
        )
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(
            TTTDiscoverBoundaryIssue(
                "claim_boundary_missing",
                "claim_boundary must state that TTT-Discover parity is not claimed",
            )
        )
    return TTTDiscoverBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status")
        if isinstance(data.get("boundary_status"), str)
        else None,
        component_count=len(data.get("framework_components") or []),
        required_evidence_field_count=len(required or []),
        missing_evidence_count=len(data.get("missing_evidence") or {}),
        issues=issues,
    )


def render_ttt_discover_boundary_summary(
    boundary: object | str | Path | None = None,
) -> str:
    validation = validate_ttt_discover_boundary(boundary)
    lines = [
        "# TTT-Discover boundary",
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
) -> tuple[dict[str, Any] | None, list[TTTDiscoverBoundaryIssue]]:
    if isinstance(boundary, Path):
        try:
            return json.loads(boundary.read_text(encoding="utf-8")), []
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            return None, [
                TTTDiscoverBoundaryIssue(
                    "read_error", f"Could not read TTT-Discover boundary: {exc}"
                )
            ]
    if isinstance(boundary, str):
        if boundary.strip().startswith("{"):
            try:
                data = json.loads(boundary)
            except json.JSONDecodeError as exc:
                return None, [
                    TTTDiscoverBoundaryIssue(
                        "json_error", f"Could not parse TTT-Discover boundary: {exc}"
                    )
                ]
            if isinstance(data, dict):
                return data, []
            return None, [
                TTTDiscoverBoundaryIssue(
                    "invalid_boundary_shape",
                    "TTT-Discover boundary JSON must be an object",
                )
            ]
        return _load_boundary(Path(boundary))
    if isinstance(boundary, dict):
        return boundary, []
    return None, [
        TTTDiscoverBoundaryIssue(
            "invalid_boundary_type",
            "TTT-Discover boundary must be a dict, JSON string, or JSON path",
        )
    ]


def _validate_source_links(
    data: dict[str, Any], issues: list[TTTDiscoverBoundaryIssue]
) -> None:
    source_links = data.get("source_links")
    if not isinstance(source_links, list) or not source_links:
        issues.append(
            TTTDiscoverBoundaryIssue(
                "source_links_missing",
                "TTT-Discover boundary must record source and result links",
            )
        )
        return
    expected_urls = {
        "https://arxiv.org/abs/2601.16175v2",
        "https://github.com/test-time-training/discover",
        "https://test-time-training.github.io/discover",
        "https://github.com/test-time-training/discover/blob/main/results/mathematics/Results.ipynb",
        "https://github.com/test-time-training/discover/blob/main/results/kernel-engineering/",
        "https://github.com/test-time-training/discover/blob/main/results/algorithm-design/",
        "https://github.com/test-time-training/discover/blob/main/results/denoising/",
        "https://atcoder.jp/contests/ahc039/submissions/72633477",
        "https://atcoder.jp/contests/ahc058/submissions/72633508",
    }
    urls = {link.get("url") for link in source_links if isinstance(link, dict)}
    if urls != expected_urls:
        issues.append(
            TTTDiscoverBoundaryIssue(
                "source_links_mismatch",
                "source links must preserve TTT-Discover paper, code, and result references",
            )
        )
    allowed_statuses = {
        "source_version_reference_only",
        "public_code_reference_only",
        "project_page_reference_only",
        "result_artifact_reference_only",
        "official_submission_reference_only",
    }
    for link in source_links:
        status = link.get("status") if isinstance(link, dict) else None
        if status not in allowed_statuses:
            issues.append(
                TTTDiscoverBoundaryIssue(
                    "source_link_status_overclaim",
                    "TTT-Discover links are reference-only until local snapshots and reproduction evidence exist",
                )
            )


def _validate_components(
    data: dict[str, Any], issues: list[TTTDiscoverBoundaryIssue]
) -> None:
    components = data.get("framework_components")
    if not isinstance(components, list):
        issues.append(
            TTTDiscoverBoundaryIssue(
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
            TTTDiscoverBoundaryIssue(
                "framework_component_ids_mismatch",
                "framework component ids must match the TTT-Discover evidence boundary",
            )
        )
    for component in components:
        status = component.get("local_status") if isinstance(component, dict) else None
        if status not in {"not_implemented", "not_recorded"}:
            issues.append(
                TTTDiscoverBoundaryIssue(
                    "framework_component_overclaim",
                    "TTT-Discover components must remain not_implemented/not_recorded",
                )
            )


def _validate_local_evidence(
    data: dict[str, Any], issues: list[TTTDiscoverBoundaryIssue]
) -> None:
    evidence = data.get("local_evidence")
    if not isinstance(evidence, dict):
        issues.append(
            TTTDiscoverBoundaryIssue(
                "local_evidence_missing", "local_evidence must be a dict"
            )
        )
        return
    for field in (
        "policy_update_loop_ready",
        "single_problem_rl_environment_ready",
        "continuous_reward_contract_ready",
        "state_reuse_ready",
        "sample_budget_records_ready",
        "benchmark_rows_ready",
        "expert_review_records_ready",
        "public_code_snapshot_ready",
        "tinker_runtime_verified",
        "open_model_backend_verified",
        "independent_reproduction_ready",
        "repository_runtime_verified",
    ):
        if evidence.get(field) is not False:
            issues.append(
                TTTDiscoverBoundaryIssue(
                    f"local_evidence_{field}_overclaim",
                    f"{field} must remain false until local TTT-Discover parity evidence exists",
                )
            )


def _validate_reported_method(
    data: dict[str, Any], issues: list[TTTDiscoverBoundaryIssue]
) -> None:
    method = data.get("reported_method")
    if not isinstance(method, dict):
        issues.append(
            TTTDiscoverBoundaryIssue(
                "reported_method_missing", "reported_method must be a dict"
            )
        )
        return
    expected = {
        "algorithm": "Test-Time Training to Discover",
        "training_steps": 50,
        "rollouts_per_step": 512,
        "baseline_sampling_budget": "Best-of-25600",
        "model": "OpenAI gpt-oss-120b",
        "runtime_api": "Tinker",
        "lora_rank": 32,
        "reuse_method": "PUCT",
        "objective": "adaptive entropic utility with KL penalty",
        "cost_claim": "few hundred dollars per problem",
    }
    for field, expected_value in expected.items():
        if method.get(field) != expected_value:
            issues.append(
                TTTDiscoverBoundaryIssue(
                    f"reported_method_{field}_mismatch",
                    f"reported_method.{field} must match the source-reported TTT-Discover method",
                )
            )


def _validate_reported_results(
    data: dict[str, Any], issues: list[TTTDiscoverBoundaryIssue]
) -> None:
    expected = [
        "Erdos minimum overlap improved to 0.380876",
        "First autocorrelation inequality improved to 1.50287",
        "TriMul A100 runtime reported as 2198.2 microseconds",
        "TriMul H100 runtime reported as 1161.2 microseconds",
        "AHC039 score reported as 567062",
        "AHC058 score reported as 848414228",
        "single-cell denoising score reported as 0.71 in headline table",
    ]
    if data.get("reported_results") != expected:
        issues.append(
            TTTDiscoverBoundaryIssue(
                "reported_results_mismatch",
                "reported_results must preserve source-reported TTT-Discover result labels",
            )
        )


def _validate_missing_evidence(
    data: dict[str, Any], issues: list[TTTDiscoverBoundaryIssue]
) -> None:
    missing = data.get("missing_evidence")
    if missing != EXPECTED_MISSING_EVIDENCE:
        issues.append(
            TTTDiscoverBoundaryIssue(
                "missing_evidence_mismatch",
                "missing evidence must match the TTT-Discover absence boundary",
            )
        )
