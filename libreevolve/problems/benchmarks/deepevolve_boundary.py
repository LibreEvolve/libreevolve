from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEEPEVOLVE_BOUNDARY_SCHEMA = "libreevolve.deepevolve_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2510.06056"
EXPECTED_SOURCE_TITLE = "Scientific Algorithm Discovery by Augmenting AlphaEvolve with Deep Research"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2510.06056.pdf"
EXPECTED_SOURCE_FILE = "papers/2510.06056__DeepEvolve.pdf"
EXPECTED_SOURCE_SHA256 = (
    "e2f578c3b7979eb72857b1545b244405cf0fa8792bab82645e58c97cf3681f86"
)
EXPECTED_SOURCE_BYTES = 2681978
EXPECTED_BOUNDARY_STATUS = "retrieval_context_inspiration_without_deepevolve_loop_parity"
EXPECTED_COMPONENT_IDS = (
    "problem_algorithm_instruction_input",
    "textualization_function",
    "plan_search_write_research_loop",
    "retrieved_source_provenance",
    "proposal_pseudocode_schema",
    "cross_file_code_editing",
    "reflection_checkpoints",
    "execution_debugging_agent",
    "score_zero_fallback",
    "evolutionary_database",
    "island_candidate_selection",
    "map_elites_inspiration_sampling",
    "benchmark_task_rows",
    "performance_runtime_debug_ablation_rows",
    "qualitative_judge_rows",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "problem_input_schema",
    "evaluation_data_and_function_records",
    "textualization_function_records",
    "user_instruction_records",
    "algorithm_description_records",
    "plan_step_question_records",
    "search_step_source_records",
    "write_step_proposal_records",
    "proposal_pseudocode_records",
    "cross_file_delimiter_records",
    "code_localization_records",
    "code_patch_records",
    "reflection_checkpoint_records",
    "debugging_attempt_records",
    "execution_feedback_records",
    "score_zero_fallback_records",
    "evolutionary_database_records",
    "island_sampling_records",
    "map_elites_inspiration_records",
    "table1_task_metric_rows",
    "table2_performance_runtime_rows",
    "table3_debugging_success_rows",
    "figure3_judge_score_rows",
    "table4_deep_research_ablation_rows",
    "appendix_c_query_hyperparameter_rows",
    "thirty_minute_single_gpu_budget_evidence",
    "local_deepevolve_runtime_artifacts",
)
EXPECTED_MISSING_EVIDENCE = {
    "six_module_workflow_trace": "not_implemented_locally",
    "problem_algorithm_instruction_input_schema": "not_recorded_locally",
    "textualization_function": "not_implemented_locally",
    "plan_search_write_research_loop": "not_implemented_locally",
    "retrieved_source_provenance_as_deepevolve_research": "partial_bounded_retrieval_only",
    "proposal_pseudocode_schema": "not_recorded_locally",
    "cross_file_code_editing": "not_implemented_locally",
    "reflection_checkpoints": "not_implemented_locally",
    "execution_debugging_agent": "not_implemented_locally",
    "score_zero_fallback": "not_implemented_locally",
    "evolutionary_database": "partial_current_run_database_not_deepevolve",
    "island_candidate_selection": "partial_local_islands_not_deepevolve_trace",
    "map_elites_inspiration_sampling": "partial_local_archive_not_deepevolve_inspiration",
    "nine_task_benchmark_rows": "not_recorded_locally",
    "table2_performance_runtime_rows": "not_recorded_locally",
    "table3_debugging_success_rows": "not_recorded_locally",
    "figure3_qualitative_judge_rows": "not_recorded_locally",
    "table4_deep_research_ablation_rows": "not_recorded_locally",
    "appendix_c_query_hyperparameter_rows": "not_recorded_locally",
    "repository_runtime_verification": "not_verified_locally",
}


@dataclass(frozen=True)
class DeepEvolveBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class DeepEvolveBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[DeepEvolveBoundaryIssue]


def deepevolve_boundary_record() -> dict[str, Any]:
    """Return the current DeepEvolve loop-parity absence boundary."""

    return {
        "schema": DEEPEVOLVE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": ["Gang Liu", "Yihan Zhu", "Jie Chen", "Meng Jiang"],
        "source_version": "v1",
        "source_submitted_date": "2025-10-07",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2510.06056v1",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://github.com/liugangcode/deepevolve",
                "status": "paper_link_resolves_not_verified_as_local_runtime",
            },
        ],
        "framework_components": [
            {
                "component_id": "problem_algorithm_instruction_input",
                "paper_role": "problem, initial algorithm, and user instructions as the update context",
                "local_status": "partial_problem_config_not_deepevolve_input_schema",
            },
            {
                "component_id": "textualization_function",
                "paper_role": "tau(P) and tau(f) textualization for problem and algorithm descriptions",
                "local_status": "not_implemented",
            },
            {
                "component_id": "plan_search_write_research_loop",
                "paper_role": "planning questions, online search, and proposal writing before coding",
                "local_status": "not_implemented",
            },
            {
                "component_id": "retrieved_source_provenance",
                "paper_role": "online research source evidence used to form proposals",
                "local_status": "partial_bounded_plugin_retrieval_only",
            },
            {
                "component_id": "proposal_pseudocode_schema",
                "paper_role": "research proposals with pseudo-code for implementation",
                "local_status": "not_recorded",
            },
            {
                "component_id": "cross_file_code_editing",
                "paper_role": "coding agent parses multi-file codebases and edits localized regions",
                "local_status": "not_implemented",
            },
            {
                "component_id": "reflection_checkpoints",
                "paper_role": "research and coding reflection checkpoints",
                "local_status": "not_implemented",
            },
            {
                "component_id": "execution_debugging_agent",
                "paper_role": "automatic debugging agent using execution feedback",
                "local_status": "not_implemented",
            },
            {
                "component_id": "score_zero_fallback",
                "paper_role": "assign score zero after exhausted debugging attempts",
                "local_status": "not_implemented",
            },
            {
                "component_id": "evolutionary_database",
                "paper_role": "long-term algorithm memory for next and inspiration sampling",
                "local_status": "partial_current_run_database_not_deepevolve",
            },
            {
                "component_id": "island_candidate_selection",
                "paper_role": "island-based candidate pool for next sampling",
                "local_status": "partial_local_islands_not_deepevolve_trace",
            },
            {
                "component_id": "map_elites_inspiration_sampling",
                "paper_role": "MAP-Elites nearby algorithms used as inspirations",
                "local_status": "partial_local_map_elites_not_deepevolve_inspiration",
            },
            {
                "component_id": "benchmark_task_rows",
                "paper_role": "nine task, domain, data-type, and metric rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "performance_runtime_debug_ablation_rows",
                "paper_role": "Table 2 performance/runtime, Table 3 debugging, and Table 4 ablation rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "qualitative_judge_rows",
                "paper_role": "Figure 3 originality, future-potential, and code-difficulty judge rows",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_plugin": "libreevolve/plugins/deep_research.py",
            "current_scope": "bounded_retrieval_context_not_deepevolve_loop",
            "retrieval_context_ready": True,
            "bounded_source_metadata_ready": True,
            "plan_search_write_loop_ready": False,
            "proposal_pseudocode_ready": False,
            "cross_file_coding_ready": False,
            "reflection_ready": False,
            "debugging_agent_ready": False,
            "score_zero_fallback_ready": False,
            "deepevolve_database_ready": False,
            "benchmark_rows_ready": False,
            "ablation_rows_ready": False,
            "repository_runtime_verified": False,
        },
        "benchmark_tasks": [
            "Molecular Prediction",
            "Molecular Translation",
            "Circle Packing",
            "Burgers' Equation",
            "Parkinson's Disease",
            "Nuclei Image",
            "Open Vaccine",
            "Polymer Prediction",
            "USP P2P",
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records DeepEvolve as retrieval/debug-loop inspiration "
            "only. LibreEvolve's current DeepResearch plugin is bounded retrieval "
            "context with provenance; it does not claim DeepEvolve's six-module "
            "plan/search/write/code/evaluation/evolutionary-selection loop, "
            "proposal pseudo-code, cross-file coding, reflection checkpoints, "
            "automatic debugging agent, score-zero fallback, DeepEvolve database "
            "semantics, nine-task benchmark rows, qualitative judge records, "
            "or deep-research ablation parity."
        ),
    }


def validate_deepevolve_boundary(
    boundary: object | str | Path | None = None,
) -> DeepEvolveBoundaryValidation:
    data, read_issues = _load_boundary(
        deepevolve_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return DeepEvolveBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[DeepEvolveBoundaryIssue] = []
    if data.get("schema") != DEEPEVOLVE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported DeepEvolve boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2510.06056"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify DeepEvolve"))
    if data.get("source_authors") != ["Gang Liu", "Yihan Zhu", "Jie Chen", "Meng Jiang"]:
        issues.append(_issue("invalid_source_authors", "source_authors must match the cached PDF metadata"))
    if data.get("source_version") != "v1":
        issues.append(_issue("invalid_source_version", "source_version must be v1"))
    if data.get("source_submitted_date") != "2025-10-07":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2025-10-07"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached DeepEvolve PDF"))
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
        issues.append(_issue("claim_ready_overclaim", "DeepEvolve boundary must not claim loop parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    _validate_benchmark_tasks(data.get("benchmark_tasks"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that DeepEvolve parity is not claimed"))
    return DeepEvolveBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_deepevolve_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_deepevolve_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "DeepEvolve boundary",
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
) -> tuple[dict[str, Any] | None, list[DeepEvolveBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "DeepEvolve boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[DeepEvolveBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    expected_urls = {
        "https://arxiv.org/abs/2510.06056v1",
        "https://github.com/liugangcode/deepevolve",
    }
    if urls != expected_urls:
        issues.append(_issue("source_link_mismatch", "source_links must preserve DeepEvolve source status"))
    allowed_statuses = {
        "source_version_reference_only",
        "paper_link_resolves_not_verified_as_local_runtime",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") not in allowed_statuses:
            issues.append(_issue("source_link_status_overclaim", "source link status must not claim local DeepEvolve runtime"))


def _validate_framework_components(value: object, issues: list[DeepEvolveBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the DeepEvolve component set"))
    allowed_statuses = {
        "partial_problem_config_not_deepevolve_input_schema",
        "not_implemented",
        "partial_bounded_plugin_retrieval_only",
        "not_recorded",
        "partial_current_run_database_not_deepevolve",
        "partial_local_islands_not_deepevolve_trace",
        "partial_local_map_elites_not_deepevolve_inspiration",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS and item.get("local_status") not in allowed_statuses:
            issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim DeepEvolve parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[DeepEvolveBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "current_plugin": "libreevolve/plugins/deep_research.py",
        "current_scope": "bounded_retrieval_context_not_deepevolve_loop",
        "retrieval_context_ready": True,
        "bounded_source_metadata_ready": True,
        "plan_search_write_loop_ready": False,
        "proposal_pseudocode_ready": False,
        "cross_file_coding_ready": False,
        "reflection_ready": False,
        "debugging_agent_ready": False,
        "score_zero_fallback_ready": False,
        "deepevolve_database_ready": False,
        "benchmark_rows_ready": False,
        "ablation_rows_ready": False,
        "repository_runtime_verified": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current DeepEvolve boundary"))


def _validate_benchmark_tasks(value: object, issues: list[DeepEvolveBoundaryIssue]) -> None:
    expected = [
        "Molecular Prediction",
        "Molecular Translation",
        "Circle Packing",
        "Burgers' Equation",
        "Parkinson's Disease",
        "Nuclei Image",
        "Open Vaccine",
        "Polymer Prediction",
        "USP P2P",
    ]
    if value != expected:
        issues.append(_issue("benchmark_task_mismatch", "benchmark_tasks must preserve the nine DeepEvolve task labels"))


def _validate_required_fields(
    value: object,
    issues: list[DeepEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve DeepEvolve evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[DeepEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve DeepEvolve artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> DeepEvolveBoundaryIssue:
    return DeepEvolveBoundaryIssue(code, message)
