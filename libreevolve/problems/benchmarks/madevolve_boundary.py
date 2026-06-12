from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MADEVOLVE_BOUNDARY_SCHEMA = "libreevolve.madevolve_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2602.15951"
EXPECTED_SOURCE_TITLE = (
    "MadEvolve: Evolutionary Optimization of Cosmological Algorithms with "
    "Large Language Models"
)
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2602.15951.pdf"
EXPECTED_SOURCE_FILE = "papers/2602.15951__MadEvolve.pdf"
EXPECTED_SOURCE_SHA256 = (
    "ec47332c9b20ca391b8aedb6b8696c42aad20c976906d1e43f13490163daea19"
)
EXPECTED_SOURCE_BYTES = 1165170
EXPECTED_BOUNDARY_STATUS = "domain_evolution_inspiration_without_madevolve_parity"
EXPECTED_COMPONENT_IDS = (
    "framework_application_split",
    "free_parameter_tracking",
    "inner_parameter_optimization",
    "autodiff_adam_optimizer",
    "optimized_source_injection",
    "domain_task_adapters",
    "hybrid_population_management",
    "llm_scheduler_and_model_stats",
    "diff_full_synthesis_mutations",
    "generated_innovation_reports",
    "cosmology_benchmark_rows",
    "reward_hacking_and_generalization_controls",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_public_code_status",
    "madevolve_org_status",
    "framework_repository_status",
    "cosmology_application_repository_status",
    "framework_application_split",
    "parameter_declaration_schema",
    "free_parameter_meaning_records",
    "parent_child_parameter_diff_records",
    "parameter_count_limit_policy",
    "one_shot_grid_latin_hypercube_bayesian_records",
    "autodiff_adam_optimizer_records",
    "jax_vmad_operator_compatibility",
    "optimized_value_source_injection_provenance",
    "inner_outer_budget_accounting",
    "bao_iterative_bao_task_fixtures",
    "twentyone_cm_task_fixtures",
    "tsz_ldl_task_fixtures",
    "training_validation_test_split_provenance",
    "compute_environment_records",
    "success_improvement_statistics",
    "model_contribution_statistics",
    "lineage_comparative_synthesis_report_artifacts",
    "reward_hacking_diagnostics",
    "over_parameterization_controls",
    "mode_collapse_diagnostics",
    "hosted_report_artifact_checks",
)
EXPECTED_MISSING_EVIDENCE = {
    "madevolve_framework_runtime": "not_implemented_locally",
    "madevolve_cosmology_application_runtime": "not_implemented_locally",
    "free_parameter_tracking": "not_implemented_locally",
    "parameter_meaning_records": "not_recorded_locally",
    "child_parent_parameter_diffs": "not_recorded_locally",
    "budgeted_inner_optimizer": "not_implemented_locally",
    "autodiff_adam_optimizer": "not_implemented_locally",
    "jax_vmad_differentiability_contract": "not_implemented_locally",
    "optimized_value_source_injection": "not_implemented_locally",
    "bao_task_adapter": "not_implemented_locally",
    "twentyone_cm_task_adapter": "not_implemented_locally",
    "tsz_ldl_task_adapter": "not_implemented_locally",
    "generated_innovation_reports": "not_implemented_locally",
    "table1_benchmark_rows": "not_recorded_locally",
    "table2_run_statistics": "not_recorded_locally",
    "table3_model_contribution_statistics": "not_recorded_locally",
    "reward_hacking_controls": "not_recorded_locally",
    "hosted_report_artifacts": "not_verified_locally",
}


@dataclass(frozen=True)
class MadEvolveBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MadEvolveBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[MadEvolveBoundaryIssue]


def madevolve_boundary_record() -> dict[str, Any]:
    """Return the current MadEvolve domain-evolution absence boundary."""

    return {
        "schema": MADEVOLVE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_version": "v1",
        "source_submitted_date": "2026-02-17",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://arxiv.org/licenses/nonexclusive-distrib/1.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://madevolve.org",
                "status": "linked_in_paper_not_verified_as_local_artifact",
            },
            {
                "url": "https://github.com/tianyi-stack/MadEvolve",
                "status": "linked_in_paper_not_verified_as_local_framework_runtime",
            },
            {
                "url": "https://github.com/tianyi-stack/MadEvolve-Cosmo",
                "status": "linked_in_paper_not_verified_as_local_application_runtime",
            },
        ],
        "framework_components": [
            {
                "component_id": "framework_application_split",
                "paper_role": "separate MadEvolve framework and cosmology application repositories",
                "local_status": "not_recorded",
            },
            {
                "component_id": "free_parameter_tracking",
                "paper_role": "free-parameter detection, meanings, and parameter-set diffs",
                "local_status": "not_implemented",
            },
            {
                "component_id": "inner_parameter_optimization",
                "paper_role": "greedy one-shot and derivative-free parameter tuning",
                "local_status": "not_implemented",
            },
            {
                "component_id": "autodiff_adam_optimizer",
                "paper_role": "autodiff/Adam optimization for JAX or vmad-compatible programs",
                "local_status": "not_implemented",
            },
            {
                "component_id": "optimized_source_injection",
                "paper_role": "optimized free-parameter values injected back into source",
                "local_status": "not_implemented",
            },
            {
                "component_id": "domain_task_adapters",
                "paper_role": "BAO, iterative BAO, 21cm, and tSZ/LDL cosmology task adapters",
                "local_status": "not_implemented",
            },
            {
                "component_id": "hybrid_population_management",
                "paper_role": "hybrid MAP-Elites/island/elite population management",
                "local_status": "partial_local_islands_not_madevolve_runtime",
            },
            {
                "component_id": "llm_scheduler_and_model_stats",
                "paper_role": "UCB model routing and per-model contribution statistics",
                "local_status": "partial_local_heuristic_scheduler_not_madevolve_stats",
            },
            {
                "component_id": "diff_full_synthesis_mutations",
                "paper_role": "diff, full, and synthesis mutation modes",
                "local_status": "partial_local_diff_full_no_synthesis_claim",
            },
            {
                "component_id": "generated_innovation_reports",
                "paper_role": "lineage, comparative analysis, and synthesis report generator",
                "local_status": "not_implemented",
            },
            {
                "component_id": "cosmology_benchmark_rows",
                "paper_role": "BAO, iterative BAO, 21cm, and tSZ result/statistics rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "reward_hacking_and_generalization_controls",
                "paper_role": "reward-hacking, over-parameterization, and mode-collapse diagnostics",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_scope": "background_domain_evolution_inspiration_only",
            "generic_evolution_surfaces_present": True,
            "free_parameter_tracking_ready": False,
            "inner_optimizer_ready": False,
            "jax_vmad_contract_ready": False,
            "optimized_source_injection_ready": False,
            "cosmology_adapters_ready": False,
            "innovation_report_ready": False,
            "benchmark_statistics_ready": False,
            "reward_hacking_controls_ready": False,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records MadEvolve as domain-evolution inspiration "
            "only. It does not claim free-parameter tracking, nested "
            "parameter optimization, autodiff/Adam or JAX/vmad compatibility, "
            "optimized-value source injection, BAO/21cm/tSZ task adapters, "
            "generated innovation reports, run/model-contribution statistics, "
            "reward-hacking controls, or hosted report reproduction."
        ),
    }


def validate_madevolve_boundary(
    boundary: object | str | Path | None = None,
) -> MadEvolveBoundaryValidation:
    data, read_issues = _load_boundary(
        madevolve_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MadEvolveBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MadEvolveBoundaryIssue] = []
    if data.get("schema") != MADEVOLVE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported MadEvolve boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2602.15951"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify MadEvolve"))
    if data.get("source_version") != "v1":
        issues.append(_issue("invalid_source_version", "source_version must be v1"))
    if data.get("source_submitted_date") != "2026-02-17":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2026-02-17"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached MadEvolve PDF"))
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
        issues.append(_issue("claim_ready_overclaim", "MadEvolve boundary must not claim domain-evolution parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that MadEvolve parity is not claimed"))
    return MadEvolveBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_madevolve_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_madevolve_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "MadEvolve boundary",
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
) -> tuple[dict[str, Any] | None, list[MadEvolveBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "MadEvolve boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[MadEvolveBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    expected_urls = {
        "https://madevolve.org",
        "https://github.com/tianyi-stack/MadEvolve",
        "https://github.com/tianyi-stack/MadEvolve-Cosmo",
    }
    if urls != expected_urls:
        issues.append(_issue("source_link_mismatch", "source_links must preserve MadEvolve public source URLs"))
    allowed_statuses = {
        "linked_in_paper_not_verified_as_local_artifact",
        "linked_in_paper_not_verified_as_local_framework_runtime",
        "linked_in_paper_not_verified_as_local_application_runtime",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") not in allowed_statuses:
            issues.append(_issue("source_link_status_overclaim", "source link status must not claim local MadEvolve runtime evidence"))


def _validate_framework_components(value: object, issues: list[MadEvolveBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the MadEvolve component set"))
    allowed_statuses = {
        "not_implemented",
        "not_recorded",
        "partial_local_islands_not_madevolve_runtime",
        "partial_local_heuristic_scheduler_not_madevolve_stats",
        "partial_local_diff_full_no_synthesis_claim",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS and item.get("local_status") not in allowed_statuses:
            issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim MadEvolve parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[MadEvolveBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "current_scope": "background_domain_evolution_inspiration_only",
        "generic_evolution_surfaces_present": True,
        "free_parameter_tracking_ready": False,
        "inner_optimizer_ready": False,
        "jax_vmad_contract_ready": False,
        "optimized_source_injection_ready": False,
        "cosmology_adapters_ready": False,
        "innovation_report_ready": False,
        "benchmark_statistics_ready": False,
        "reward_hacking_controls_ready": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current MadEvolve boundary"))


def _validate_required_fields(
    value: object,
    issues: list[MadEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve MadEvolve evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[MadEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve MadEvolve artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> MadEvolveBoundaryIssue:
    return MadEvolveBoundaryIssue(code, message)
