from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_phase_sequence_boundary import (
    PHASE_SECTION_SPECS,
    roadmap_phase_sequence_boundary_record,
)


ROADMAP_PHASE_DEPENDENCY_GRAPH_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_phase_dependency_graph_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_phase_dependency_graph_recorded_with_ci_freshness_gate"
)
SOURCE_PHASE_BOUNDARY_INPUT = "papers/roadmap_phase_sequence_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_phase_sequence",
    "phase_dependency_nodes",
    "phase_dependency_edges",
    "section_sidecar_refs",
    "active_blocking_todo_refs",
    "phase_staleness_detector",
    "promotion_demotion_workflow",
    "ci_phase_freshness_gate",
    "evidence_status_refresh",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "evidence_status_refresh": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


SECTION_EVIDENCE_SIDECARS = {
    "candidate_workspace_fidelity": (
        "papers/roadmap_candidate_workspace_fidelity_boundary.json",
        "papers/roadmap_candidate_workspace_readiness_boundary.json",
    ),
    "multi_objective_search": (
        "papers/roadmap_multi_objective_search_boundary.json",
        "papers/roadmap_multi_objective_readiness_boundary.json",
    ),
    "evaluation_cascades": (
        "papers/roadmap_evaluation_cascade_boundary.json",
        "papers/roadmap_evaluation_cascade_readiness_boundary.json",
    ),
    "prompt_context": (
        "papers/roadmap_prompt_context_system_boundary.json",
        "papers/roadmap_prompt_context_readiness_boundary.json",
    ),
    "documentation_truthfulness": (
        "papers/documentation_truthfulness_boundary.json",
        "papers/roadmap_claim_evidence_boundary.json",
    ),
    "async_resumable_runtime": (
        "papers/roadmap_async_resumable_runtime_boundary.json",
        "papers/roadmap_async_runtime_readiness_boundary.json",
    ),
    "backend_scheduling_and_critique": (
        "papers/roadmap_backend_scheduling_critique_boundary.json",
        "papers/roadmap_backend_control_plane_readiness_boundary.json",
    ),
    "plugin_extensibility": (
        "papers/roadmap_plugin_extensibility_boundary.json",
        "papers/roadmap_plugin_readiness_boundary.json",
    ),
    "representative_benchmarks": (
        "papers/roadmap_representative_benchmark_portfolio_boundary.json",
        "papers/roadmap_benchmark_portfolio_readiness_boundary.json",
    ),
    "operational_maturity": (
        "papers/roadmap_operational_maturity_boundary.json",
        "papers/roadmap_operational_readiness_boundary.json",
    ),
}

DEPENDENCY_EDGE_SPECS = (
    {
        "section_id": "multi_objective_search",
        "depends_on": ("candidate_workspace_fidelity",),
        "dependency_reason": "multi-objective archive evidence depends on faithful candidate workspace records",
    },
    {
        "section_id": "evaluation_cascades",
        "depends_on": ("candidate_workspace_fidelity",),
        "dependency_reason": "cascade evidence depends on candidate materialization and validator boundaries",
    },
    {
        "section_id": "prompt_context",
        "depends_on": ("candidate_workspace_fidelity", "evaluation_cascades"),
        "dependency_reason": "prompt/context evidence depends on candidate context and evaluator feedback surfaces",
    },
    {
        "section_id": "documentation_truthfulness",
        "depends_on": (
            "candidate_workspace_fidelity",
            "multi_objective_search",
            "evaluation_cascades",
            "prompt_context",
        ),
        "dependency_reason": "documentation truthfulness depends on current evidence for the major Near Term claims",
    },
    {
        "section_id": "async_resumable_runtime",
        "depends_on": ("candidate_workspace_fidelity", "evaluation_cascades"),
        "dependency_reason": "async resume proof depends on candidate workspace and evaluator/admission state",
    },
    {
        "section_id": "backend_scheduling_and_critique",
        "depends_on": ("prompt_context", "evaluation_cascades"),
        "dependency_reason": "scheduler and critique readiness depends on prompt roles and evaluator feedback contracts",
    },
    {
        "section_id": "plugin_extensibility",
        "depends_on": ("candidate_workspace_fidelity", "evaluation_cascades"),
        "dependency_reason": "plugin lifecycle evidence depends on candidate artifacts and evaluator/plugin scoring boundaries",
    },
    {
        "section_id": "representative_benchmarks",
        "depends_on": (
            "candidate_workspace_fidelity",
            "multi_objective_search",
            "evaluation_cascades",
        ),
        "dependency_reason": "representative benchmarks need candidate, search, and cascade evidence before portfolio claims",
    },
    {
        "section_id": "operational_maturity",
        "depends_on": (
            "documentation_truthfulness",
            "async_resumable_runtime",
            "backend_scheduling_and_critique",
            "plugin_extensibility",
            "representative_benchmarks",
        ),
        "dependency_reason": "operational maturity depends on documented, runtime, backend, plugin, and benchmark readiness",
    },
)


@dataclass(frozen=True)
class RoadmapPhaseDependencyGraphBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapPhaseDependencyGraphBoundaryValidation:
    ok: bool
    boundary_status: str | None
    node_count: int
    edge_count: int
    stale_dependency_edge_count: int
    missing_evidence_count: int
    issues: list[RoadmapPhaseDependencyGraphBoundaryIssue]


def roadmap_phase_dependency_graph_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP phase dependency graph."""

    root_path = Path(root)
    source_boundary = roadmap_phase_sequence_boundary_record(root_path)
    source_records = {
        record["section_id"]: record
        for record in source_boundary["section_records"]
    }
    node_records = [
        _node_record(root_path, source_records[spec["section_id"]])
        for spec in PHASE_SECTION_SPECS
    ]
    edge_records = [
        _edge_record(edge, source_records)
        for edge in DEPENDENCY_EDGE_SPECS
    ]
    stale_edges = [
        edge
        for edge in edge_records
        if edge["dependency_edge_status"] != "dependency_edge_current"
    ]
    return {
        "schema": ROADMAP_PHASE_DEPENDENCY_GRAPH_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_phase_boundary_input": SOURCE_PHASE_BOUNDARY_INPUT,
        "source_phase_count": source_boundary["phase_count"],
        "source_section_count": source_boundary["section_count"],
        "source_section_sequence_status": source_boundary["section_sequence_status"],
        "node_count": len(node_records),
        "edge_count": sum(len(edge["depends_on"]) for edge in edge_records),
        "dependency_record_count": len(edge_records),
        "stale_dependency_edge_count": len(stale_edges),
        "stale_dependency_edges": stale_edges,
        "phase_dependency_nodes": node_records,
        "phase_dependency_edges": edge_records,
        "dependency_graph_status": (
            "phase_dependency_graph_recorded"
            if not stale_edges
            else "phase_dependency_graph_stale_or_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a bounded ROADMAP phase dependency graph "
            "for the ten major sections by linking each section to source "
            "phase-sequence records, section evidence sidecars, active blocker "
            "TODO refs, and prerequisite section edges. It does not claim a "
            "evidence-status refresh report or owner review signoff. The "
            "bounded stale-phase detector, phase promotion/demotion workflow, "
            "and CI phase freshness gate are recorded separately."
        ),
    }


def validate_roadmap_phase_dependency_graph_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapPhaseDependencyGraphBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_phase_dependency_graph_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapPhaseDependencyGraphBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_phase_dependency_graph_boundary_record(root)
    issues: list[RoadmapPhaseDependencyGraphBoundaryIssue] = []
    if data.get("schema") != ROADMAP_PHASE_DEPENDENCY_GRAPH_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP phase dependency graph schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "phase dependency graph must not claim freshness-gate readiness"))
    for key in (
        "source_phase_boundary_input",
        "source_phase_count",
        "source_section_count",
        "source_section_sequence_status",
        "node_count",
        "edge_count",
        "dependency_record_count",
        "stale_dependency_edge_count",
        "stale_dependency_edges",
        "phase_dependency_nodes",
        "phase_dependency_edges",
        "dependency_graph_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current phase dependency inputs"))
    if data.get("source_section_sequence_status") != "roadmap_major_sections_in_expected_order":
        issues.append(_issue("invalid_source_section_sequence", "source phase sequence must be current"))
    if data.get("stale_dependency_edge_count") != 0:
        issues.append(_issue("stale_dependency_edge", "phase dependency graph must not contain stale edges"))
    if data.get("dependency_graph_status") != "phase_dependency_graph_recorded":
        issues.append(_issue("invalid_dependency_graph_status", "dependency graph status must be recorded"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "bounded ROADMAP phase dependency graph" not in boundary_text
        or "prerequisite section edges" not in boundary_text
        or "CI phase freshness gate are recorded separately" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate dependency graph from phase freshness gates"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapPhaseDependencyGraphBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        node_count=data.get("node_count") if isinstance(data.get("node_count"), int) else 0,
        edge_count=data.get("edge_count") if isinstance(data.get("edge_count"), int) else 0,
        stale_dependency_edge_count=(
            data.get("stale_dependency_edge_count")
            if isinstance(data.get("stale_dependency_edge_count"), int)
            else 0
        ),
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_phase_dependency_graph_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_phase_dependency_graph_boundary(boundary)
    lines = [
        "ROADMAP phase dependency graph boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| node_count | {validation.node_count} |",
        f"| edge_count | {validation.edge_count} |",
        f"| stale_dependency_edge_count | {validation.stale_dependency_edge_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _node_record(root: Path, source_record: dict[str, Any]) -> dict[str, Any]:
    section_id = source_record["section_id"]
    return {
        "section_id": section_id,
        "phase": source_record["phase"],
        "ordinal": source_record["ordinal"],
        "roadmap_heading": source_record["roadmap_heading"],
        "roadmap_heading_present": source_record["roadmap_heading_present"],
        "blocking_todo_phrase": source_record["blocking_todo_phrase"],
        "blocking_todo_present": source_record["blocking_todo_present"],
        "validation_gate": source_record["validation_gate"],
        "promotion_criterion": source_record["promotion_criterion"],
        "section_sidecar_refs": [
            {"path": path, "exists": (root / path).exists()}
            for path in SECTION_EVIDENCE_SIDECARS[section_id]
        ],
        "node_status": (
            "phase_dependency_node_current"
            if source_record["roadmap_heading_present"]
            and source_record["blocking_todo_present"]
            and all((root / path).exists() for path in SECTION_EVIDENCE_SIDECARS[section_id])
            else "phase_dependency_node_stale_or_incomplete"
        ),
    }


def _edge_record(
    spec: dict[str, Any],
    source_records: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    section_id = spec["section_id"]
    depends_on = list(spec["depends_on"])
    stale_reasons: list[str] = []
    if section_id not in source_records:
        stale_reasons.append("missing_section_node")
    for dependency_id in depends_on:
        if dependency_id not in source_records:
            stale_reasons.append(f"missing_dependency_node:{dependency_id}")
            continue
        if source_records[dependency_id]["ordinal"] >= source_records[section_id]["ordinal"]:
            stale_reasons.append(f"dependency_not_before_section:{dependency_id}")
    return {
        "section_id": section_id,
        "depends_on": depends_on,
        "dependency_reason": spec["dependency_reason"],
        "dependency_edge_status": (
            "dependency_edge_current"
            if not stale_reasons
            else "dependency_edge_stale_or_incomplete"
        ),
        "stale_reasons": stale_reasons,
    }


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapPhaseDependencyGraphBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP phase dependency graph boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapPhaseDependencyGraphBoundaryIssue],
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
    issues: list[RoadmapPhaseDependencyGraphBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapPhaseDependencyGraphBoundaryIssue:
    return RoadmapPhaseDependencyGraphBoundaryIssue(code=code, message=message)
