from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


GIGAEVO_FRAMEWORK_BOUNDARY_SCHEMA = "libreevolve.gigaevo_framework_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2511.17592"
EXPECTED_SOURCE_TITLE = (
    "GigaEvo: An Open Source Optimization Framework Powered by LLMs and "
    "Evolution Algorithms"
)
EXPECTED_SOURCE_URL = "https://arxiv.org/pdf/2511.17592.pdf"
EXPECTED_SOURCE_FILE = "papers/2511.17592__GigaEvo.pdf"
EXPECTED_SOURCE_SHA256 = (
    "9a14bf06a1323e63bf53234e79e44c41e1e78e0dc2f90578d74b928efd067113"
)
EXPECTED_SOURCE_BYTES = 1393166
EXPECTED_BOUNDARY_STATUS = "framework_inspiration_without_gigaevo_runtime_parity"
EXPECTED_COMPONENT_IDS = (
    "redis_program_storage",
    "asyncio_dag_engine",
    "map_elites_evolution",
    "langgraph_mutation_operator",
    "insight_generation",
    "bidirectional_lineage",
    "hydra_configuration",
    "benchmark_reproduction",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_license_and_repository_status",
    "redis_program_lifecycle_schema",
    "optimistic_concurrency_records",
    "asyncio_dag_node_edge_schema",
    "dag_stage_output_records",
    "stage_caching_and_skip_telemetry",
    "concurrent_unit_runtime_telemetry",
    "hydra_component_configuration_mapping",
    "gigaevo_problem_layout_adapter",
    "insight_generation_artifacts",
    "ancestor_descendant_lineage_artifacts",
    "langgraph_mutation_operator_provenance",
    "diff_rewrite_mutation_mode_evidence",
    "map_elites_island_compatibility_report",
    "benchmark_reproduction_rows",
    "dual_github_source_disambiguation",
)
EXPECTED_MISSING_EVIDENCE = {
    "redis_program_lifecycle_database": "not_implemented_locally",
    "asyncio_dag_execution_engine": "not_implemented_locally",
    "optimistic_concurrency_control": "not_implemented_locally",
    "dag_stage_caching_and_skipping": "not_recorded_locally",
    "concurrent_units": "not_implemented_locally",
    "hydra_component_mapping": "not_recorded_locally",
    "gigaevo_problem_layout_adapter": "not_implemented_locally",
    "insight_stage_artifacts": "not_recorded_locally",
    "bidirectional_lineage_analysis": "not_recorded_locally",
    "langgraph_mutation_operator": "not_implemented_locally",
    "benchmark_reproduction_rows": "not_recorded_locally",
    "dual_github_source_status": "not_disambiguated",
}


@dataclass(frozen=True)
class GigaEvoBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class GigaEvoBoundaryValidation:
    ok: bool
    boundary_status: str | None
    component_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[GigaEvoBoundaryIssue]


def gigaevo_framework_boundary_record() -> dict[str, Any]:
    """Return the current GigaEvo framework-parity absence boundary."""

    return {
        "schema": GIGAEVO_FRAMEWORK_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_title": EXPECTED_SOURCE_TITLE,
        "source_version": "v1",
        "source_submitted_date": "2025-11-17",
        "source_url": EXPECTED_SOURCE_URL,
        "source_file": EXPECTED_SOURCE_FILE,
        "source_sha256": EXPECTED_SOURCE_SHA256,
        "source_bytes": EXPECTED_SOURCE_BYTES,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_links": [
            {
                "url": "https://github.com/AIRI-Institute/gigaevo-core",
                "status": "linked_in_paper_source_status_not_disambiguated",
            },
            {
                "url": "https://github.com/FusionBrainLab/gigaevo-core",
                "status": "linked_in_paper_source_status_not_disambiguated",
            },
        ],
        "framework_components": [
            {
                "component_id": "redis_program_storage",
                "paper_role": "Redis-backed Program records with lifecycle state and optimistic counters",
                "local_status": "not_implemented",
            },
            {
                "component_id": "asyncio_dag_engine",
                "paper_role": "async DAG execution with dependencies, caching, and skip behavior",
                "local_status": "not_implemented",
            },
            {
                "component_id": "map_elites_evolution",
                "paper_role": "quality-diversity evolution backbone",
                "local_status": "partial_local_map_elites_not_gigaevo_runtime",
            },
            {
                "component_id": "langgraph_mutation_operator",
                "paper_role": "LangGraph mutation and agentic pipeline operator",
                "local_status": "not_implemented",
            },
            {
                "component_id": "insight_generation",
                "paper_role": "generated insights used by later stages",
                "local_status": "not_implemented",
            },
            {
                "component_id": "bidirectional_lineage",
                "paper_role": "ancestor and descendant lineage analysis",
                "local_status": "not_implemented",
            },
            {
                "component_id": "hydra_configuration",
                "paper_role": "componentized Hydra configuration and problem layout",
                "local_status": "not_mapped",
            },
            {
                "component_id": "benchmark_reproduction",
                "paper_role": "Heilbronn, circle packing, kissing, bin packing, and Jigsaw rows",
                "local_status": "not_recorded",
            },
        ],
        "local_evidence": {
            "program_database_scope": "small_local_log_archive_not_lifecycle_database",
            "current_mutation_modes": ["diff", "full_rewrite"],
            "current_map_elites_scope": "local_archive_without_gigaevo_runtime_parity",
            "redis_required": False,
            "asyncio_dag_ready": False,
            "concurrent_units_ready": False,
            "insight_stage_ready": False,
            "benchmark_reproduction_ready": False,
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records GigaEvo as framework inspiration only. It "
            "does not claim Redis lifecycle storage, asyncio DAG execution, "
            "concurrent units, Hydra component parity, LangGraph mutation, "
            "insight or bidirectional-lineage stages, source-repository "
            "disambiguation, or GigaEvo benchmark reproduction."
        ),
    }


def validate_gigaevo_framework_boundary(
    boundary: object | str | Path | None = None,
) -> GigaEvoBoundaryValidation:
    data, read_issues = _load_boundary(
        gigaevo_framework_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return GigaEvoBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[GigaEvoBoundaryIssue] = []
    if data.get("schema") != GIGAEVO_FRAMEWORK_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported GigaEvo boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2511.17592"))
    if data.get("source_title") != EXPECTED_SOURCE_TITLE:
        issues.append(_issue("invalid_source_title", "source_title must identify GigaEvo"))
    if data.get("source_version") != "v1":
        issues.append(_issue("invalid_source_version", "source_version must be v1"))
    if data.get("source_submitted_date") != "2025-11-17":
        issues.append(_issue("invalid_source_submitted_date", "source_submitted_date must be 2025-11-17"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must identify the arXiv PDF"))
    if data.get("source_file") != EXPECTED_SOURCE_FILE:
        issues.append(_issue("invalid_source_file", "source_file must identify the cached GigaEvo PDF"))
    if data.get("source_sha256") != EXPECTED_SOURCE_SHA256:
        issues.append(_issue("invalid_source_sha256", "source_sha256 must match the cached PDF digest"))
    if data.get("source_bytes") != EXPECTED_SOURCE_BYTES:
        issues.append(_issue("invalid_source_bytes", "source_bytes must match the cached PDF size"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "GigaEvo boundary must not claim framework parity"))
    _validate_source_links(data.get("source_links"), issues)
    component_count = _validate_framework_components(data.get("framework_components"), issues)
    _validate_local_evidence(data.get("local_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that framework parity is not claimed"))
    return GigaEvoBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        component_count=component_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_gigaevo_framework_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_gigaevo_framework_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "GigaEvo framework boundary",
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
) -> tuple[dict[str, Any] | None, list[GigaEvoBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "GigaEvo boundary must be a JSON object")]


def _validate_source_links(value: object, issues: list[GigaEvoBoundaryIssue]) -> None:
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_links", "source_links must be a list"))
        return
    urls = {item.get("url") for item in value if isinstance(item, dict)}
    expected_urls = {
        "https://github.com/AIRI-Institute/gigaevo-core",
        "https://github.com/FusionBrainLab/gigaevo-core",
    }
    if urls != expected_urls:
        issues.append(_issue("source_link_mismatch", "source_links must preserve both GigaEvo GitHub URLs"))
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_source_link", "source link records must be objects"))
            continue
        if item.get("status") != "linked_in_paper_source_status_not_disambiguated":
            issues.append(_issue("source_link_status_overclaim", "source link status must remain not disambiguated"))


def _validate_framework_components(value: object, issues: list[GigaEvoBoundaryIssue]) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_framework_components", "framework_components must be a list"))
        return 0
    ids = [item.get("component_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_COMPONENT_IDS:
        issues.append(_issue("framework_component_id_mismatch", "framework_components must preserve the GigaEvo component set"))
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_framework_component", "framework component records must be objects"))
            continue
        if item.get("component_id") in EXPECTED_COMPONENT_IDS:
            local_status = item.get("local_status")
            if local_status not in {"not_implemented", "not_mapped", "not_recorded", "partial_local_map_elites_not_gigaevo_runtime"}:
                issues.append(_issue("framework_component_overclaim", "framework component local_status must not claim GigaEvo parity"))
    return len(value)


def _validate_local_evidence(value: object, issues: list[GigaEvoBoundaryIssue]) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_local_evidence", "local_evidence must be an object"))
        return
    expected = {
        "program_database_scope": "small_local_log_archive_not_lifecycle_database",
        "current_mutation_modes": ["diff", "full_rewrite"],
        "current_map_elites_scope": "local_archive_without_gigaevo_runtime_parity",
        "redis_required": False,
        "asyncio_dag_ready": False,
        "concurrent_units_ready": False,
        "insight_stage_ready": False,
        "benchmark_reproduction_ready": False,
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            suffix = "overclaim" if expected_value is False else "mismatch"
            issues.append(_issue(f"local_evidence_{field}_{suffix}", f"local_evidence.{field} must preserve current GigaEvo boundary"))


def _validate_required_fields(
    value: object,
    issues: list[GigaEvoBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    if seen != expected:
        issues.append(_issue("required_evidence_field_mismatch", "required_evidence_fields must preserve GigaEvo framework evidence gates"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[GigaEvoBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    if set(value) != set(EXPECTED_MISSING_EVIDENCE):
        issues.append(_issue("missing_evidence_key_mismatch", "missing_evidence must preserve GigaEvo artifact-gap keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(value)


def _issue(code: str, message: str) -> GigaEvoBoundaryIssue:
    return GigaEvoBoundaryIssue(code, message)
