from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


IMPROVEVOLVE_BOUNDARY_SCHEMA = "libreevolve.improvevolve_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2602.10233"
EXPECTED_SOURCE_TITLE = (
    "ImprovEvolve: Ask AlphaEvolve to Improve the Input Solution and Then "
    "Improvise"
)
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2602.10233.pdf"
EXPECTED_SOURCE_FILE = "papers/2602.10233__ImprovEvolve.pdf"
EXPECTED_SOURCE_SHA256 = (
    "8123f1b19d9ba6c891e642be28b1bd4395fff549131d2e45b619dfd28ddfe57a"
)
EXPECTED_SOURCE_BYTES = 10158341
EXPECTED_BOUNDARY_STATUS = "modular_prompting_inspiration_without_improvevolve_parity"
EXPECTED_COMPONENT_IDS = (
    "class_interface_schema",
    "interface_enforcement",
    "stage_a_initialization",
    "stage_b_basin_hopping",
    "perturbation_schedule",
    "monotonic_acceptance",
    "incumbent_improvement_records",
    "gigaevo_outer_backbone",
    "model_provider_provenance",
    "human_edited_variants",
    "hex_aci2_benchmark_rows",
    "ablation_and_budget_rows",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_rights_status",
    "improvevolve_specific_code_status",
    "generate_config_improve_perturb_interface_schema",
    "interface_enforcement_records",
    "stage_a_initial_program_records",
    "stage_b_validation_runner_records",
    "seed_count_records",
    "basin_hopping_round_records",
    "perturbation_schedule_records",
    "monotonic_acceptance_proofs",
    "incumbent_and_improvement_delta_artifacts",
    "gigaevo_backbone_compatibility",
    "model_provider_provenance",
    "human_edit_variant_attribution",
    "hex_benchmark_rows",
    "aci2_benchmark_rows",
    "hyperparameter_table_rows",
    "generalization_table_rows",
    "stage_ablation_rows",
    "cpu_gpu_wall_clock_budget_rows",
    "static_modular_plugin_separation_evidence",
)
EXPECTED_MISSING_EVIDENCE = {
    "class_interface_enforcement": "not_implemented_locally",
    "stage_a_runner": "not_implemented_locally",
    "stage_b_basin_hopping_runner": "not_implemented_locally",
    "perturbation_schedule": "not_recorded_locally",
    "monotonic_acceptance": "not_recorded_locally",
    "incumbent_improvement_records": "not_recorded_locally",
    "gigaevo_outer_backbone": "not_implemented_locally",
    "model_provider_provenance": "not_recorded_locally",
    "human_edited_variant_provenance": "not_recorded_locally",
    "hex_benchmark_rows": "not_recorded_locally",
    "aci2_benchmark_rows": "not_recorded_locally",
    "hyperparameter_rows": "not_recorded_locally",
    "generalization_rows": "not_recorded_locally",
    "stage_ablation_rows": "not_recorded_locally",
    "compute_budget_rows": "not_recorded_locally",
    "improvevolve_specific_code_url": "not_found_in_extracted_links",
}


@dataclass(frozen=True)
class ImprovEvolveBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ImprovEvolveBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ImprovEvolveBoundaryIssue]


def improvevolve_boundary_record() -> dict[str, Any]:
    """Return the current ImprovEvolve execution-parity absence boundary."""

    return {
        "schema": IMPROVEVOLVE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_version": "v1",
        "source_submitted_date": "2026-02-10",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by/4.0/",
        "rights_note": "CC-BY metadata with KDD 2026/ACM front-matter rights language",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://github.com/FusionBrainLab/gigaevo-core",
                "status": "related_gigaevo_backbone_not_improvevolve_runtime",
            },
            {
                "url": "<no_improvevolve_specific_code_url_extracted>",
                "status": "not_found_in_extracted_links",
            },
        ],
        "framework_components": [
            {
                "component_id": "class_interface_schema",
                "paper_role": "generate_config(seed), improve(x), and perturb(x, sigma) methods",
                "local_status": "static_prompt_description_only",
            },
            {
                "component_id": "interface_enforcement",
                "paper_role": "validated execution of the modular class interface",
                "local_status": "not_implemented",
            },
            {
                "component_id": "stage_a_initialization",
                "paper_role": "multi-seed initialization and initial-program generation",
                "local_status": "not_implemented",
            },
            {
                "component_id": "stage_b_basin_hopping",
                "paper_role": "basin-hopping validation loop",
                "local_status": "not_implemented",
            },
            {
                "component_id": "perturbation_schedule",
                "paper_role": "scheduled sigma perturbation intensity",
                "local_status": "not_recorded",
            },
            {
                "component_id": "monotonic_acceptance",
                "paper_role": "acceptance policy and incremental improvement tracking",
                "local_status": "not_recorded",
            },
            {
                "component_id": "incumbent_improvement_records",
                "paper_role": "inner-loop incumbent and improvement-delta artifacts",
                "local_status": "not_recorded",
            },
            {
                "component_id": "gigaevo_outer_backbone",
                "paper_role": "GigaEvo outer MAP-Elites evolution backbone",
                "local_status": "not_implemented",
            },
            {
                "component_id": "model_provider_provenance",
                "paper_role": "Gemini and OpenRouter model/provider provenance",
                "local_status": "not_recorded",
            },
            {
                "component_id": "human_edited_variants",
                "paper_role": "ImprovEvolve+E human-edit attribution",
                "local_status": "not_recorded",
            },
            {
                "component_id": "hex_aci2_benchmark_rows",
                "paper_role": "HEX and ACI2 benchmark/baseline/result rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "ablation_and_budget_rows",
                "paper_role": "stage ablations, hyperparameters, and compute budgets",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "current_plugin": "libreevolve/plugins/modular.py",
            "current_scope": "static_prompt_guidance_only_not_execution",
            "described_operations": ["generate_config", "improve", "perturb"],
            "operation_selected": "static_modular_guidance",
            "interface_enforced": False,
            "operation_executed": False,
            "basin_hopping_ready": False,
            "gigaevo_backbone_ready": False,
            "benchmark_rows_ready": False,
            "human_edit_provenance_ready": False,
            "budget_rows_ready": False,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records ImprovEvolve as modular-search inspiration "
            "only. It does not claim enforced generate_config/improve/perturb "
            "interfaces, Stage A or Stage B execution, basin hopping, "
            "perturbation scheduling, monotonic acceptance, GigaEvo outer-loop "
            "parity, model/provider provenance, human-edited variant "
            "attribution, HEX/ACI2 benchmark rows, ablations, or compute "
            "budget reproduction. LibreEvolve's current modular plugin is "
            "static prompt guidance, not ImprovEvolve execution."
        ),
    }


def validate_improvevolve_boundary(
    boundary: object | str | Path | None = None,
) -> ImprovEvolveBoundaryValidation:
    data, read_issues = _load_boundary(
        improvevolve_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ImprovEvolveBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ImprovEvolveBoundaryIssue] = []
    if data.get("schema") != IMPROVEVOLVE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ImprovEvolve boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2602.10233"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify ImprovEvolve"))
    if data.get("source_version") != "v1":
        issues.append(_issue("invalid_source_version", "source_version must be v1"))
    if data.get("source_submitted_date") != "2026-02-10":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2026-02-10"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached ImprovEvolve PDF"))
    if data.get("source_sha256") != EXPECTED_SOURCE_SHA256:
        issues.append(_issue("invalid_source_sha256", "source_sha256 must match the cached PDF digest"))
    if data.get("source_bytes") != EXPECTED_SOURCE_BYTES:
        issues.append(_issue("invalid_source_bytes", "source_bytes must match the cached PDF size"))
    if data.get("source_license") != "http://creativecommons.org/licenses/by/4.0/":
        issues.append(_issue("invalid_source_license", "source_license must match the cached PDF metadata"))
    if "ACM" not in str(data.get("rights_note", "")):
        issues.append(_issue("invalid_rights_note", "rights_note must preserve ACM front-matter caveat"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ImprovEvolve boundary must not claim execution parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that ImprovEvolve parity is not claimed"))
    return ImprovEvolveBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_improvevolve_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_improvevolve_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ImprovEvolve boundary",
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
) -> tuple[dict[str, Any] | None, list[ImprovEvolveBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ImprovEvolve boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[ImprovEvolveBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    expected_urls = {
        "https://github.com/FusionBrainLab/gigaevo-core",
        "<no_improvevolve_specific_code_url_extracted>",
    }
    if urls != expected_urls:
        issues.append(_issue("source_link_mismatch", "source_links must preserve ImprovEvolve link status"))
    allowed_statuses = {
        "related_gigaevo_backbone_not_improvevolve_runtime",
        "not_found_in_extracted_links",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") not in allowed_statuses:
            issues.append(_issue("source_link_status_overclaim", "source link status must not claim ImprovEvolve runtime code"))


def _validate_framework_components(value: object, issues: list[ImprovEvolveBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the ImprovEvolve component set"))
    allowed_statuses = {
        "static_prompt_description_only",
        "not_implemented",
        "not_recorded",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS and item.get("local_status") not in allowed_statuses:
            issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim ImprovEvolve parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[ImprovEvolveBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "current_plugin": "libreevolve/plugins/modular.py",
        "current_scope": "static_prompt_guidance_only_not_execution",
        "described_operations": ["generate_config", "improve", "perturb"],
        "operation_selected": "static_modular_guidance",
        "interface_enforced": False,
        "operation_executed": False,
        "basin_hopping_ready": False,
        "gigaevo_backbone_ready": False,
        "benchmark_rows_ready": False,
        "human_edit_provenance_ready": False,
        "budget_rows_ready": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current ImprovEvolve boundary"))


def _validate_required_fields(
    value: object,
    issues: list[ImprovEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve ImprovEvolve evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[ImprovEvolveBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve ImprovEvolve artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> ImprovEvolveBoundaryIssue:
    return ImprovEvolveBoundaryIssue(code, message)
