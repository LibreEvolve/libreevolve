from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_distributed_pipeline_topology_boundary.v1"
)
DISTRIBUTED_PIPELINE_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.distributed_pipeline_topology_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.6",)
EXPECTED_BOUNDARY_STATUS = "single_process_synchronous_topology"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "asyncio_runtime_identity",
    "controller_node_identity",
    "program_database_node_identity",
    "llm_sampler_node_identity",
    "evaluation_node_identity",
    "queue_count",
    "blocking_dependency_edges",
    "dispatch_policy",
    "throughput_budget_linkage",
    "pending_work_checkpoint",
    "async_topology_claim_readiness",
)
EXPECTED_MISSING_EVIDENCE = {
    "python_asyncio_runtime": "not_recorded_locally",
    "async_controller_queues": "not_recorded_locally",
    "queue_capacity_records": "not_recorded_locally",
    "nonblocking_dependency_graph": "not_recorded_locally",
    "distributed_llm_sampler_worker_nodes": "not_recorded_locally",
    "distributed_evaluator_worker_nodes": "not_recorded_locally",
    "throughput_dispatch_telemetry": "not_recorded_locally",
    "pending_work_checkpoint_state": "not_recorded_locally",
}


@dataclass(frozen=True)
class DistributedPipelineTopologyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class DistributedPipelineTopologyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[DistributedPipelineTopologyBoundaryIssue]


def distributed_pipeline_topology_boundary_record() -> dict[str, Any]:
    """Return the current AlphaEvolve distributed-pipeline topology boundary."""

    return {
        "schema": DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_SCHEMA,
        "runtime_report_schema": DISTRIBUTED_PIPELINE_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 2.6 describes a Python asyncio asynchronous controller, "
            "LLM-sampler, and evaluator-node pipeline optimized for throughput "
            "with computations that can block on unfinished dependencies"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "distributed_pipeline_topology_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has a runtime topology "
            "report for the current local controller, program database, "
            "configured LLM sampler nodes, evaluator nodes, zero queues, "
            "blocking dependency edges, synchronous dispatch, runtime-budget "
            "linkage, and unsupported pending-work checkpoints, but does not "
            "claim AlphaEvolve-style Python asyncio runtime identity, async "
            "controller queues, queue capacities, nonblocking dependency "
            "graphs, distributed sampler/evaluator worker nodes, throughput "
            "dispatch telemetry, or pending-work checkpoint state."
        ),
    }


def validate_distributed_pipeline_topology_boundary(
    boundary: object | str | Path | None = None,
) -> DistributedPipelineTopologyBoundaryValidation:
    data, read_issues = _load_boundary(
        distributed_pipeline_topology_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return DistributedPipelineTopologyBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[DistributedPipelineTopologyBoundaryIssue] = []
    if data.get("schema") != DISTRIBUTED_PIPELINE_TOPOLOGY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported distributed-pipeline topology boundary schema"))
    if data.get("runtime_report_schema") != DISTRIBUTED_PIPELINE_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify distributed-pipeline topology reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.6']"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "asynchronous controller" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve asynchronous topology"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "distributed_pipeline_topology_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to distributed-pipeline topology reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "distributed-pipeline topology boundary must not claim AlphaEvolve topology readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim AlphaEvolve topology parity"))
    return DistributedPipelineTopologyBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_distributed_pipeline_topology_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_distributed_pipeline_topology_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve distributed-pipeline topology boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[DistributedPipelineTopologyBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "distributed-pipeline topology boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[DistributedPipelineTopologyBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_evidence_field", f"missing required evidence fields: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_evidence_field", f"unknown required evidence fields: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_evidence_field", "required evidence fields must be strings"))
    return len(seen)


def _validate_missing_evidence(
    value: object,
    issues: list[DistributedPipelineTopologyBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_missing_evidence_key", f"missing_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_missing_evidence_key", f"missing_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> DistributedPipelineTopologyBoundaryIssue:
    return DistributedPipelineTopologyBoundaryIssue(code, message)
