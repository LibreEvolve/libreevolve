from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ARCHAGENT_BOUNDARY_SCHEMA = "libreevolve.archagent_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2602.22425"
EXPECTED_SOURCE_TITLE = "ArchAgent: Agentic AI-driven Computer Architecture Discovery"
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2602.22425.pdf"
EXPECTED_SOURCE_FILE = "papers/2602.22425__ArchAgent.pdf"
EXPECTED_SOURCE_SHA256 = (
    "c074fe0dc4680dcc5f25ee48bc27815218d2735b29afcff879df0d64e340ca98"
)
EXPECTED_SOURCE_BYTES = 885845
EXPECTED_BOUNDARY_STATUS = "computer_architecture_context_without_archagent_runtime_parity"
EXPECTED_COMPONENT_IDS = (
    "cxx_cache_policy_candidates",
    "champsim_policy_h_integration",
    "alphaevolve_prompting",
    "distributed_champsim_evaluation",
    "crc_hardware_configurations",
    "workload_trace_provenance",
    "ipc_speedup_metrics",
    "policy31_single_core_spec",
    "policy31_tuned_hyperspecialization",
    "policy61_google_workloads",
    "policy62_google_workloads",
    "hardware_realizability_verification",
    "policy_ablation_rows",
    "simulator_escape_controls",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "alphaevolve_relation",
    "architecture_fixture_policy",
    "cache_policy_candidate_schema",
    "champsim_policy_h_integration_points",
    "crc_cache_core_prefetch_dram_configuration_rows",
    "workload_trace_provenance",
    "single_core_benchmark_split",
    "multi_core_benchmark_split",
    "evolution_instruction_count_protocols",
    "validation_instruction_count_protocols",
    "ipc_speedup_metric_definition",
    "lru_baseline_identity",
    "sota_policy_baseline_identities",
    "policy31_mechanism_rows",
    "policy61_mechanism_rows",
    "policy62_mechanism_rows",
    "policy_state_budget_records",
    "hardware_realizability_checker_outputs",
    "policy_ablation_records",
    "post_silicon_parameter_specialization_records",
    "simulator_escape_records",
    "write_bypass_containment_policy",
    "distributed_simulation_failure_retry_records",
    "evolution_budget_records",
    "development_time_comparison_rows",
    "champion_policy_artifact_hashes",
    "simulator_environment_hashes",
    "independent_checker_outputs",
)
EXPECTED_MISSING_EVIDENCE = {
    "cache_policy_candidate_schema": "not_implemented_locally",
    "champsim_policy_h_runner": "not_implemented_locally",
    "champsim_build_and_simulation_harness": "not_implemented_locally",
    "crc_hardware_configuration_rows": "not_recorded_locally",
    "spec06_workload_fixture": "not_implemented_locally",
    "google_workload_trace_fixture": "not_implemented_locally",
    "single_core_benchmark_rows": "not_recorded_locally",
    "multi_core_benchmark_rows": "not_recorded_locally",
    "ipc_speedup_metric_records": "not_recorded_locally",
    "evolution_validation_instruction_protocols": "not_recorded_locally",
    "policy31_artifact_and_ablation_rows": "not_recorded_locally",
    "policy31_tuned_specialization_records": "not_recorded_locally",
    "policy61_policy62_artifact_rows": "not_recorded_locally",
    "sota_baseline_ledger": "not_recorded_locally",
    "hardware_realizability_verifier": "not_implemented_locally",
    "state_budget_checker": "not_implemented_locally",
    "simulator_escape_detection": "not_implemented_locally",
    "write_bypass_containment_policy": "not_recorded_locally",
    "distributed_simulation_retry_records": "not_recorded_locally",
    "development_time_comparison_rows": "not_recorded_locally",
    "independent_checker_outputs": "not_recorded_locally",
    "dedicated_archagent_runtime_repository": "not_found_in_extracted_links",
}


@dataclass(frozen=True)
class ArchAgentBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ArchAgentBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ArchAgentBoundaryIssue]


def archagent_boundary_record() -> dict[str, Any]:
    """Return the current ArchAgent computer-architecture absence boundary."""

    return {
        "schema": ARCHAGENT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_authors": [
            "Raghav Gupta",
            "Akanksha Jain",
            "Abraham Gonzalez",
            "Alexander Novikov",
            "Po-Sen Huang",
            "Matej Balog",
            "Marvin Eisenberger",
            "Sergey Shirobokov",
            "Ngan Vu",
            "Martin Dixon",
            "Borivoje Nikolic",
            "Parthasarathy Ranganathan",
            "Sagar Karandikar",
        ],
        "source_version": "v1",
        "source_submitted_date": "2026-02-25",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "source_license": "http://creativecommons.org/licenses/by/4.0/",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://arxiv.org/abs/2602.22425v1",
                "status": "source_version_reference_only",
            },
            {
                "url": "https://console.cloud.google.com/storage/browser/external-traces-v2",
                "status": "workload_reference_only_not_local_fixture",
            },
            {
                "url": "https://crc2.ece.tamu.edu/?page_id=53",
                "status": "crc_reference_only_not_local_fixture",
            },
            {
                "url": "<no_dedicated_archagent_code_repository_extracted>",
                "status": "not_found_in_extracted_links",
            },
        ],
        "framework_components": [
            {
                "component_id": "cxx_cache_policy_candidates",
                "paper_role": "generated C++ cache replacement policy logic",
                "local_status": "not_implemented",
            },
            {
                "component_id": "champsim_policy_h_integration",
                "paper_role": "candidate insertion into ChampSim policy.h",
                "local_status": "not_implemented",
            },
            {
                "component_id": "alphaevolve_prompting",
                "paper_role": "architecture-agent prompts with prior policies and constraints",
                "local_status": "not_recorded",
            },
            {
                "component_id": "distributed_champsim_evaluation",
                "paper_role": "parallel ChampSim compile/run/evaluate cluster",
                "local_status": "not_implemented",
            },
            {
                "component_id": "crc_hardware_configurations",
                "paper_role": "CRC-style cache/core/prefetch/DRAM configuration rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "workload_trace_provenance",
                "paper_role": "SPEC06 and Google Workload Trace provenance",
                "local_status": "not_recorded",
            },
            {
                "component_id": "ipc_speedup_metrics",
                "paper_role": "IPC speedup normalized to LRU",
                "local_status": "not_recorded",
            },
            {
                "component_id": "policy31_single_core_spec",
                "paper_role": "Policy31 SPEC06 single-core discovery and validation rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "policy31_tuned_hyperspecialization",
                "paper_role": "post-silicon runtime-parameter specialization rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "policy61_google_workloads",
                "paper_role": "Policy61 Google Workload Trace multi-core rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "policy62_google_workloads",
                "paper_role": "Policy62 Google Workload Trace multi-core rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "hardware_realizability_verification",
                "paper_role": "state-budget, line-count, and hardware-realizability checks",
                "local_status": "not_implemented",
            },
            {
                "component_id": "policy_ablation_rows",
                "paper_role": "Policy31 mechanism ablation and explanation rows",
                "local_status": "not_recorded",
            },
            {
                "component_id": "simulator_escape_controls",
                "paper_role": "Policy12 write-bypass simulator-escape detection and containment",
                "local_status": "not_implemented",
            },
        ],
        "local_evidence": {
            "current_architecture_simulator": "<none>",
            "current_candidate_language_scope": "python_primary_text_workspace_not_champsim_cxx_policy",
            "cache_policy_candidate_ready": False,
            "champsim_runner_ready": False,
            "workload_trace_fixture_ready": False,
            "crc_configuration_rows_ready": False,
            "ipc_metric_rows_ready": False,
            "single_core_results_ready": False,
            "multi_core_results_ready": False,
            "post_silicon_specialization_ready": False,
            "hardware_realizability_checker_ready": False,
            "simulator_escape_checker_ready": False,
            "repository_runtime_verified": False,
        },
        "reported_tasks": [
            "SPEC06 single-core cache replacement policy discovery",
            "Google Workload Traces multi-core cache replacement policy discovery",
            "post-silicon runtime-parameter hyperspecialization",
            "hardware-realizability and state-budget verification",
            "simulator-escape detection for write-bypass behavior",
        ],
        "reported_policies": [
            "Policy31",
            "Policy31-Tuned",
            "Policy61",
            "Policy62",
            "Policy12 simulator-escape case",
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records ArchAgent as AlphaEvolve computer-architecture "
            "application context only. LibreEvolve currently does not claim "
            "generated C++ cache replacement policies, ChampSim policy.h "
            "integration, CRC-style hardware configuration rows, SPEC06 or "
            "Google Workload Trace fixtures, IPC-over-LRU benchmark rows, "
            "Policy31/Policy31-Tuned/Policy61/Policy62 artifacts, "
            "hardware-realizability or 48 KB state-budget verification, "
            "post-silicon hyperspecialization records, distributed simulation "
            "reliability records, or Policy12 write-bypass simulator-escape "
            "detection evidence."
        ),
    }


def validate_archagent_boundary(
    boundary: object | str | Path | None = None,
) -> ArchAgentBoundaryValidation:
    data, read_issues = _load_boundary(
        archagent_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ArchAgentBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ArchAgentBoundaryIssue] = []
    if data.get("schema") != ARCHAGENT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ArchAgent boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2602.22425"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify ArchAgent"))
    if data.get("source_version") != "v1":
        issues.append(_issue("invalid_source_version", "source_version must be v1"))
    if data.get("source_submitted_date") != "2026-02-25":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2026-02-25"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached ArchAgent PDF"))
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
        issues.append(_issue("claim_ready_overclaim", "ArchAgent boundary must not claim architecture runtime parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    _validate_reported_tasks(data.get("reported_tasks"), issues)
    _validate_reported_policies(data.get("reported_policies"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that ArchAgent parity is not claimed"))
    return ArchAgentBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_archagent_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_archagent_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ArchAgent boundary",
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
) -> tuple[dict[str, Any] | None, list[ArchAgentBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ArchAgent boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[ArchAgentBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    expected_urls = {
        "https://arxiv.org/abs/2602.22425v1",
        "https://console.cloud.google.com/storage/browser/external-traces-v2",
        "https://crc2.ece.tamu.edu/?page_id=53",
        "<no_dedicated_archagent_code_repository_extracted>",
    }
    if urls != expected_urls:
        issues.append(_issue("source_link_mismatch", "source_links must preserve ArchAgent source status"))
    allowed_statuses = {
        "source_version_reference_only",
        "workload_reference_only_not_local_fixture",
        "crc_reference_only_not_local_fixture",
        "not_found_in_extracted_links",
    }
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") not in allowed_statuses:
            issues.append(_issue("source_link_status_overclaim", "source link status must not claim local ArchAgent runtime"))


def _validate_framework_components(value: object, issues: list[ArchAgentBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the ArchAgent component set"))
    allowed_statuses = {"not_implemented", "not_recorded"}
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS and item.get("local_status") not in allowed_statuses:
            issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim ArchAgent parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[ArchAgentBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "current_architecture_simulator": "<none>",
        "current_candidate_language_scope": "python_primary_text_workspace_not_champsim_cxx_policy",
        "cache_policy_candidate_ready": False,
        "champsim_runner_ready": False,
        "workload_trace_fixture_ready": False,
        "crc_configuration_rows_ready": False,
        "ipc_metric_rows_ready": False,
        "single_core_results_ready": False,
        "multi_core_results_ready": False,
        "post_silicon_specialization_ready": False,
        "hardware_realizability_checker_ready": False,
        "simulator_escape_checker_ready": False,
        "repository_runtime_verified": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current ArchAgent boundary"))


def _validate_reported_tasks(value: object, issues: list[ArchAgentBoundaryIssue]) -> None:
    expected = [
        "SPEC06 single-core cache replacement policy discovery",
        "Google Workload Traces multi-core cache replacement policy discovery",
        "post-silicon runtime-parameter hyperspecialization",
        "hardware-realizability and state-budget verification",
        "simulator-escape detection for write-bypass behavior",
    ]
    if value != expected:
        issues.append(_issue("reported_task_mismatch", "reported_tasks must preserve ArchAgent task labels"))


def _validate_reported_policies(value: object, issues: list[ArchAgentBoundaryIssue]) -> None:
    expected = [
        "Policy31",
        "Policy31-Tuned",
        "Policy61",
        "Policy62",
        "Policy12 simulator-escape case",
    ]
    if value != expected:
        issues.append(_issue("reported_policy_mismatch", "reported_policies must preserve ArchAgent policy labels"))


def _validate_required_fields(
    value: object,
    issues: list[ArchAgentBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve ArchAgent evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[ArchAgentBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve ArchAgent artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> ArchAgentBoundaryIssue:
    return ArchAgentBoundaryIssue(code, message)
