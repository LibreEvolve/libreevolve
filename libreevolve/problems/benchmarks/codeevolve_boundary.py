from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CODEEVOLVE_BOUNDARY_SCHEMA = "libreevolve.codeevolve_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2510.14150"
EXPECTED_SOURCE_TITLE = (
    "CodeEvolve: an open source evolutionary coding agent for algorithmic "
    "discovery and optimization"
)
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2510.14150.pdf"
EXPECTED_SOURCE_FILE = "papers/2510.14150__CodeEvolve.pdf"
EXPECTED_SOURCE_SHA256 = (
    "8dc8c35d24e2f6bce81e9608609e10b4dac5dd7072d155d9cd5c575d47472405"
)
EXPECTED_SOURCE_BYTES = 2094810
EXPECTED_BOUNDARY_STATUS = "agentic_code_evolution_inspiration_without_codeevolve_parity"
EXPECTED_COMPONENT_IDS = (
    "islands_population",
    "prompt_solution_dual_fitness",
    "weighted_llm_ensemble",
    "search_replace_editing",
    "semantic_inspiration_crossover",
    "meta_prompting_exploration",
    "depth_targeted_refinement",
    "exploration_plateau_scheduler",
    "sandbox_runtime_memory_limits",
    "map_elites_cvt_archives",
    "benchmark_and_ablation_rows",
    "quality_cost_comparison_rows",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "science_codeevolve_release_status",
    "science_codeevolve_experiments_status",
    "islands_population_schema",
    "prompt_fitness_schema",
    "solution_fitness_schema",
    "weighted_ensemble_configuration",
    "model_cost_telemetry",
    "search_replace_operator_provenance",
    "semantic_inspiration_crossover_provenance",
    "meta_prompting_exploration_artifacts",
    "depth_refinement_ancestor_context",
    "exploration_scheduler_trace",
    "rank_based_parent_inspiration_selection",
    "elitist_migration_records",
    "sandbox_runtime_limit_evidence",
    "sandbox_memory_limit_evidence",
    "map_elites_cvt_archive_metadata",
    "alphaevolve_benchmark_rows",
    "eoh_benchmark_rows",
    "component_depth_inspiration_map_elites_topology_ablations",
    "open_framework_comparison_rows",
    "quality_cost_comparison_rows",
    "recommended_hyperparameter_rows",
)
EXPECTED_MISSING_EVIDENCE = {
    "prompt_solution_dual_fitness": "not_implemented_locally",
    "semantic_inspiration_crossover": "not_implemented_locally",
    "meta_prompting_exploration": "not_implemented_locally",
    "depth_targeted_refinement": "not_implemented_locally",
    "exploration_plateau_scheduler": "not_recorded_locally",
    "rank_based_inspiration_selection": "not_implemented_locally",
    "elitist_migration": "not_implemented_locally",
    "sandbox_runtime_memory_limits": "not_implemented_locally",
    "cvt_map_elites_archives": "not_implemented_locally",
    "alphaevolve_benchmark_rows": "not_recorded_locally",
    "eoh_benchmark_rows": "not_recorded_locally",
    "component_ablation_rows": "not_recorded_locally",
    "quality_cost_comparison_rows": "not_recorded_locally",
    "open_framework_comparison_rows": "not_recorded_locally",
    "recommended_hyperparameter_rows": "not_recorded_locally",
    "linked_experiment_artifact_status": "not_disambiguated_locally",
}


@dataclass(frozen=True)
class CodeEvolveBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CodeEvolveBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CodeEvolveBoundaryIssue]


def codeevolve_boundary_record() -> dict[str, Any]:
    """Return the current CodeEvolve framework-parity absence boundary."""

    return {
        "schema": CODEEVOLVE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_version": "v4",
        "source_submitted_date": "2026-03-12",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://github.com/inter-co/science-codeevolve",
                "status": "linked_in_paper_not_verified_as_local_runtime",
            },
            {
                "url": "https://github.com/inter-co/science-codeevolve-experiments",
                "status": "linked_in_paper_not_verified_as_local_experiment_artifacts",
            },
        ],
        "framework_components": [
            {
                "component_id": "islands_population",
                "paper_role": "islands-based genetic algorithm and population orchestration",
                "local_status": "partial_local_islands_not_codeevolve_runtime",
            },
            {
                "component_id": "prompt_solution_dual_fitness",
                "paper_role": "separate solution fitness and prompt fitness over prompt-generated solutions",
                "local_status": "not_implemented",
            },
            {
                "component_id": "weighted_llm_ensemble",
                "paper_role": "weighted LLM ensemble with model-cost reporting",
                "local_status": "partial_local_ensemble_not_codeevolve_cost_report",
            },
            {
                "component_id": "search_replace_editing",
                "paper_role": "SEARCH/REPLACE code edits",
                "local_status": "partial_local_diff_operator_only",
            },
            {
                "component_id": "semantic_inspiration_crossover",
                "paper_role": "inspiration solutions passed to the LLM as semantic crossover",
                "local_status": "not_implemented",
            },
            {
                "component_id": "meta_prompting_exploration",
                "paper_role": "MetaPromptingLLM exploration branch",
                "local_status": "not_implemented",
            },
            {
                "component_id": "depth_targeted_refinement",
                "paper_role": "targeted refinement using nearest ancestors and depth context",
                "local_status": "not_implemented",
            },
            {
                "component_id": "exploration_plateau_scheduler",
                "paper_role": "exploration-rate scheduling including plateau behavior",
                "local_status": "not_recorded",
            },
            {
                "component_id": "sandbox_runtime_memory_limits",
                "paper_role": "sandboxed evaluation with runtime and memory limits",
                "local_status": "not_implemented",
            },
            {
                "component_id": "map_elites_cvt_archives",
                "paper_role": "MAP-Elites and CVT-MAP-Elites archive variants",
                "local_status": "partial_local_map_elites_no_cvt_parity",
            },
            {
                "component_id": "benchmark_and_ablation_rows",
                "paper_role": "AlphaEvolve/EoH benchmark rows and component ablations",
                "local_status": "not_recorded",
            },
            {
                "component_id": "quality_cost_comparison_rows",
                "paper_role": "Qwen3-Coder-30B versus GEMINI-2.5 quality-cost rows",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_mutation_modes": ["diff", "full_rewrite"],
            "current_parent_selection_scope": "local_prompt_program_and_archive_sampling_not_codeevolve_algorithm",
            "current_archive_scope": "local_map_elites_without_cvt_codeevolve_parity",
            "prompt_solution_dual_fitness_ready": False,
            "semantic_crossover_ready": False,
            "meta_prompting_ready": False,
            "depth_refinement_ready": False,
            "exploration_scheduler_ready": False,
            "sandbox_runtime_memory_ready": False,
            "benchmark_cost_rows_ready": False,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records CodeEvolve as agentic code-evolution "
            "inspiration only. It does not claim CodeEvolve prompt/solution "
            "dual fitness, semantic inspiration crossover, meta-prompting "
            "exploration, depth-targeted refinement, plateau scheduling, "
            "sandbox runtime or memory limits, CVT-MAP-Elites parity, "
            "benchmark reproduction, ablation rows, or quality-cost "
            "comparisons."
        ),
    }


def validate_codeevolve_boundary(
    boundary: object | str | Path | None = None,
) -> CodeEvolveBoundaryValidation:
    data, read_issues = _load_boundary(
        codeevolve_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CodeEvolveBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CodeEvolveBoundaryIssue] = []
    if data.get("schema") != CODEEVOLVE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported CodeEvolve boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2510.14150"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify CodeEvolve"))
    if data.get("source_version") != "v4":
        issues.append(_issue("invalid_source_version", "source_version must be v4"))
    if data.get("source_submitted_date") != "2026-03-12":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2026-03-12"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached CodeEvolve PDF"))
    if data.get("source_sha256") != EXPECTED_SOURCE_SHA256:
        issues.append(_issue("invalid_source_sha256", "source_sha256 must match the cached PDF digest"))
    if data.get("source_bytes") != EXPECTED_SOURCE_BYTES:
        issues.append(_issue("invalid_source_bytes", "source_bytes must match the cached PDF size"))
    if data.get("source_license") != "http://arxiv.org/licenses/nonexclusive-distrib/1.0/":
        issues.append(_issue("invalid_source_license", "source_license must match the cached PDF metadata"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "CodeEvolve boundary must not claim framework parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that CodeEvolve parity is not claimed"))
    return CodeEvolveBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_codeevolve_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_codeevolve_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "CodeEvolve boundary",
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
) -> tuple[dict[str, Any] | None, list[CodeEvolveBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "CodeEvolve boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[CodeEvolveBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    expected_urls = {
        "https://github.com/inter-co/science-codeevolve",
        "https://github.com/inter-co/science-codeevolve-experiments",
    }
    if urls != expected_urls:
        issues.append(_issue("source_link_mismatch", "source_links must preserve both CodeEvolve GitHub URLs"))
    allowed_statuses = {
        "linked_in_paper_not_verified_as_local_runtime",
        "linked_in_paper_not_verified_as_local_experiment_artifacts",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") not in allowed_statuses:
            issues.append(_issue("source_link_status_overclaim", "source link status must remain unverified as local runtime evidence"))


def _validate_framework_components(value: object, issues: list[CodeEvolveBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the CodeEvolve component set"))
    allowed_statuses = {
        "not_implemented",
        "not_recorded",
        "partial_local_islands_not_codeevolve_runtime",
        "partial_local_ensemble_not_codeevolve_cost_report",
        "partial_local_diff_operator_only",
        "partial_local_map_elites_no_cvt_parity",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS and item.get("local_status") not in allowed_statuses:
            issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim CodeEvolve parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[CodeEvolveBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "current_mutation_modes": ["diff", "full_rewrite"],
        "current_parent_selection_scope": "local_prompt_program_and_archive_sampling_not_codeevolve_algorithm",
        "current_archive_scope": "local_map_elites_without_cvt_codeevolve_parity",
        "prompt_solution_dual_fitness_ready": False,
        "semantic_crossover_ready": False,
        "meta_prompting_ready": False,
        "depth_refinement_ready": False,
        "exploration_scheduler_ready": False,
        "sandbox_runtime_memory_ready": False,
        "benchmark_cost_rows_ready": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current CodeEvolve boundary"))


def _validate_required_fields(
    value: object,
    issues: list[CodeEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve CodeEvolve evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[CodeEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve CodeEvolve artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> CodeEvolveBoundaryIssue:
    return CodeEvolveBoundaryIssue(code, message)
