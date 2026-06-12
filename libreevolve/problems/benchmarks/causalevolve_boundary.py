from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CAUSALEVOLVE_BOUNDARY_SCHEMA = "libreevolve.causalevolve_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2603.14575"
EXPECTED_SOURCE_TITLE = "CausalEvolve: Towards Open-Ended Discovery with Causal Scratchpad"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2603.14575.pdf"
EXPECTED_SOURCE_FILE = "papers/2603.14575__CausalEvolve.pdf"
EXPECTED_SOURCE_SHA256 = (
    "b3190d25d802f5b9913e4e266b7dda1b76d2211d2d4cad68e1a5d0a3d03fc4d2"
)
EXPECTED_SOURCE_BYTES = 538166
EXPECTED_BOUNDARY_STATUS = "causal_guidance_inspiration_without_causalevolve_scratchpad_parity"
EXPECTED_COMPONENT_IDS = (
    "pomdp_scm_framing",
    "causal_scratchpad_schema",
    "llm_outcome_factor_generation",
    "executable_factor_code",
    "causalplanner_interventions",
    "inspiration_sorting",
    "procedure_factor_extraction",
    "treatment_effect_estimation",
    "surprise_pattern_detection",
    "abductive_hypothesis_generation",
    "scratchpad_memory_replay",
    "benchmark_and_ablation_rows",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_code_status",
    "pomdp_scm_task_world_metadata",
    "causal_scratchpad_schema",
    "outcome_factor_prompt_records",
    "executable_factor_code_contracts",
    "deterministic_factor_metric_artifacts",
    "causalplanner_action_space",
    "causalplanner_reward_policy_tau_k",
    "inspiration_selection_records",
    "procedure_factor_extraction_artifacts",
    "approximate_treatment_effect_tables",
    "surprise_pattern_detector_outputs",
    "abductive_hypothesis_lifecycle",
    "scratchpad_memory_update_replay",
    "environment_shift_generalization_checks",
    "hadamard_autocorr_circle_aime_benchmark_rows",
    "baseline_ablation_method_rows",
    "seed_step_schedule_records",
    "grok_4_1_fast_reasoning_model_provenance",
    "appendix_d_metric_library",
    "theory_nonidentifiability_boundary",
    "local_token_pattern_plugin_separation_evidence",
)
EXPECTED_MISSING_EVIDENCE = {
    "pomdp_scm_belief_records": "not_recorded_locally",
    "causal_scratchpad_schema": "not_implemented_locally",
    "llm_outcome_factor_generation": "not_implemented_locally",
    "executable_factor_code": "not_implemented_locally",
    "causalplanner_intervention_actions": "not_implemented_locally",
    "top_factor_inspiration_sorting": "not_implemented_locally",
    "procedure_factor_extraction": "not_implemented_locally",
    "treatment_effect_estimates": "not_recorded_locally",
    "surprise_pattern_detection": "not_implemented_locally",
    "abductive_hypothesis_generation": "not_implemented_locally",
    "scratchpad_memory_replay": "not_recorded_locally",
    "environment_shift_model": "not_recorded_locally",
    "benchmark_comparison_rows": "not_recorded_locally",
    "appendix_d_metric_library": "not_implemented_locally",
    "dedicated_code_repository": "not_found_in_extracted_links",
    "theory_sample_efficiency_boundary": "not_recorded_locally",
}


@dataclass(frozen=True)
class CausalEvolveBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CausalEvolveBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CausalEvolveBoundaryIssue]


def causalevolve_boundary_record() -> dict[str, Any]:
    """Return the current CausalEvolve causal-scratchpad absence boundary."""

    return {
        "schema": CAUSALEVOLVE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_version": "v2",
        "source_submitted_date": "2026-03-15",
        "source_revised_date": "2026-03-29",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by-nc-sa/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2603.14575v2",
                "status": "source_version_reference_only",
            },
            {
                "url": "<no_dedicated_causalevolve_code_repository_extracted>",
                "status": "not_found_in_extracted_links",
            },
        ],
        "framework_components": [
            {
                "component_id": "pomdp_scm_framing",
                "paper_role": "POMDP and SCM-scoped scientific discovery framing",
                "local_status": "not_recorded",
            },
            {
                "component_id": "causal_scratchpad_schema",
                "paper_role": "persistent causal scratchpad memory over factors and hypotheses",
                "local_status": "not_implemented",
            },
            {
                "component_id": "llm_outcome_factor_generation",
                "paper_role": "LLM-generated outcome-level causal factors before evolution",
                "local_status": "not_implemented",
            },
            {
                "component_id": "executable_factor_code",
                "paper_role": "executable factor-code metrics over task outputs",
                "local_status": "not_implemented",
            },
            {
                "component_id": "causalplanner_interventions",
                "paper_role": "CausalPlanner MAB over factor-direction interventions",
                "local_status": "not_implemented",
            },
            {
                "component_id": "inspiration_sorting",
                "paper_role": "top-factor direction sorts inspiration programs",
                "local_status": "not_implemented",
            },
            {
                "component_id": "procedure_factor_extraction",
                "paper_role": "procedure-level factors extracted from accumulated trials",
                "local_status": "not_implemented",
            },
            {
                "component_id": "treatment_effect_estimation",
                "paper_role": "approximate treatment-effect tables over factors",
                "local_status": "not_recorded",
            },
            {
                "component_id": "surprise_pattern_detection",
                "paper_role": "sign-inversion and quantity-shift surprise pattern detection",
                "local_status": "not_implemented",
            },
            {
                "component_id": "abductive_hypothesis_generation",
                "paper_role": "abductive reasoning that proposes new factors and hypotheses",
                "local_status": "not_implemented",
            },
            {
                "component_id": "scratchpad_memory_replay",
                "paper_role": "scratchpad memory update and replay artifacts",
                "local_status": "not_recorded",
            },
            {
                "component_id": "benchmark_and_ablation_rows",
                "paper_role": "Hadamard, autocorrelation, circle-packing, and AIME rows",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_plugin": "libreevolve/plugins/causal.py",
            "current_scope": "fixed_token_pattern_guidance_not_causal_scratchpad",
            "fixed_factor_categories": [
                "loop_structure",
                "data_types",
                "algorithm_choice",
                "constants",
                "helper_functions",
            ],
            "causal_scratchpad_ready": False,
            "llm_factor_generation_ready": False,
            "executable_factor_code_ready": False,
            "intervention_policy_ready": False,
            "procedure_factor_ready": False,
            "treatment_effect_ready": False,
            "surprise_abduction_ready": False,
            "benchmark_rows_ready": False,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records CausalEvolve as causal-guidance inspiration "
            "only. It does not claim POMDP/SCM task-world records, a causal "
            "scratchpad, LLM-generated outcome factors, executable factor "
            "code, CausalPlanner factor-direction interventions, procedure "
            "factor extraction, treatment-effect tables, surprise-pattern "
            "detection, abductive hypotheses, scratchpad replay, or benchmark "
            "comparison parity. LibreEvolve's current causal plugin is fixed "
            "token-pattern guidance, not CausalEvolve causal-scratchpad "
            "execution."
        ),
    }


def validate_causalevolve_boundary(
    boundary: object | str | Path | None = None,
) -> CausalEvolveBoundaryValidation:
    data, read_issues = _load_boundary(
        causalevolve_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CausalEvolveBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CausalEvolveBoundaryIssue] = []
    if data.get("schema") != CAUSALEVOLVE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported CausalEvolve boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2603.14575"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify CausalEvolve"))
    if data.get("source_version") != "v2":
        issues.append(_issue("invalid_source_version", "source_version must be v2"))
    if data.get("source_submitted_date") != "2026-03-15":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2026-03-15"))
    if data.get("source_revised_date") != "2026-03-29":
        issues.append(_issue("invalid_source_revised_date", "source_revised_date must be 2026-03-29"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached CausalEvolve PDF"))
    if data.get("source_sha256") != EXPECTED_SOURCE_SHA256:
        issues.append(_issue("invalid_source_sha256", "source_sha256 must match the cached PDF digest"))
    if data.get("source_bytes") != EXPECTED_SOURCE_BYTES:
        issues.append(_issue("invalid_source_bytes", "source_bytes must match the cached PDF size"))
    if data.get("source_license") != "http://creativecommons.org/licenses/by-nc-sa/4.0/":
        issues.append(_issue("invalid_source_license", "source_license must match the cached PDF metadata"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "CausalEvolve boundary must not claim causal-scratchpad parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that CausalEvolve parity is not claimed"))
    return CausalEvolveBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_causalevolve_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_causalevolve_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "CausalEvolve boundary",
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
) -> tuple[dict[str, Any] | None, list[CausalEvolveBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "CausalEvolve boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[CausalEvolveBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    expected_urls = {
        "https://arxiv.org/abs/2603.14575v2",
        "<no_dedicated_causalevolve_code_repository_extracted>",
    }
    if urls != expected_urls:
        issues.append(_issue("source_link_mismatch", "source_links must preserve CausalEvolve source status"))
    allowed_statuses = {"source_version_reference_only", "not_found_in_extracted_links"}
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") not in allowed_statuses:
            issues.append(_issue("source_link_status_overclaim", "source link status must not claim local CausalEvolve code"))


def _validate_framework_components(value: object, issues: list[CausalEvolveBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the CausalEvolve component set"))
    allowed_statuses = {"not_implemented", "not_recorded"}
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS and item.get("local_status") not in allowed_statuses:
            issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim CausalEvolve parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[CausalEvolveBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "current_plugin": "libreevolve/plugins/causal.py",
        "current_scope": "fixed_token_pattern_guidance_not_causal_scratchpad",
        "fixed_factor_categories": [
            "loop_structure",
            "data_types",
            "algorithm_choice",
            "constants",
            "helper_functions",
        ],
        "causal_scratchpad_ready": False,
        "llm_factor_generation_ready": False,
        "executable_factor_code_ready": False,
        "intervention_policy_ready": False,
        "procedure_factor_ready": False,
        "treatment_effect_ready": False,
        "surprise_abduction_ready": False,
        "benchmark_rows_ready": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current CausalEvolve boundary"))


def _validate_required_fields(
    value: object,
    issues: list[CausalEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve CausalEvolve evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[CausalEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve CausalEvolve artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> CausalEvolveBoundaryIssue:
    return CausalEvolveBoundaryIssue(code, message)
