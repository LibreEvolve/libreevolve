from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_phase_dependency_graph_boundary import (
    roadmap_phase_dependency_graph_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_phase_sequence_boundary import (
    PHASE_SECTION_SPECS,
    roadmap_phase_sequence_boundary_record,
)


ROADMAP_PHASE_STALENESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_phase_staleness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_phase_staleness_detector_with_promotion_workflow"
)
SOURCE_PHASE_BOUNDARY_INPUT = "papers/roadmap_phase_sequence_boundary.json"
SOURCE_DEPENDENCY_GRAPH_INPUT = "papers/roadmap_phase_dependency_graph_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_phase_sequence",
    "phase_dependency_graph",
    "section_order_check",
    "heading_presence_check",
    "active_blocking_todo_ref_check",
    "section_sidecar_presence_check",
    "dependency_edge_staleness_check",
    "stale_phase_records",
    "promotion_demotion_workflow",
    "ci_phase_freshness_gate",
    "evidence_status_refresh",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "ci_phase_freshness_gate": "not_recorded_locally",
    "evidence_status_refresh": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class RoadmapPhaseStalenessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapPhaseStalenessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    phase_record_count: int
    stale_phase_record_count: int
    dependency_edge_count: int
    missing_evidence_count: int
    issues: list[RoadmapPhaseStalenessBoundaryIssue]


def roadmap_phase_staleness_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP phase staleness detector record."""

    root_path = Path(root)
    sequence_boundary = roadmap_phase_sequence_boundary_record(root_path)
    dependency_graph = roadmap_phase_dependency_graph_boundary_record(root_path)
    sequence_by_id = {
        record["section_id"]: record
        for record in sequence_boundary["section_records"]
    }
    graph_nodes_by_id = {
        node["section_id"]: node
        for node in dependency_graph["phase_dependency_nodes"]
    }
    graph_edges_by_id = {
        edge["section_id"]: edge
        for edge in dependency_graph["phase_dependency_edges"]
    }
    detector_records = [
        _detector_record(
            sequence_by_id.get(spec["section_id"]),
            graph_nodes_by_id.get(spec["section_id"]),
            graph_edges_by_id.get(spec["section_id"]),
            sequence_boundary,
            dependency_graph,
        )
        for spec in PHASE_SECTION_SPECS
    ]
    stale_phase_records = [
        record
        for record in detector_records
        if record["phase_detector_status"] != "phase_current"
    ]
    expected_ordinals = list(range(1, len(detector_records) + 1))
    observed_ordinals = [
        record["ordinal"]
        for record in detector_records
        if isinstance(record["ordinal"], int)
    ]
    return {
        "schema": ROADMAP_PHASE_STALENESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_phase_boundary_input": SOURCE_PHASE_BOUNDARY_INPUT,
        "source_dependency_graph_input": SOURCE_DEPENDENCY_GRAPH_INPUT,
        "source_phase_count": sequence_boundary["phase_count"],
        "source_section_count": sequence_boundary["section_count"],
        "source_section_sequence_status": sequence_boundary["section_sequence_status"],
        "dependency_graph_status": dependency_graph["dependency_graph_status"],
        "dependency_edge_count": dependency_graph["edge_count"],
        "dependency_graph_stale_edge_count": dependency_graph["stale_dependency_edge_count"],
        "phase_detector_status": (
            "no_stale_phase_records_detected"
            if not stale_phase_records
            else "stale_phase_records_detected"
        ),
        "phase_record_count": len(detector_records),
        "stale_phase_record_count": len(stale_phase_records),
        "stale_phase_records": stale_phase_records,
        "detector_records": detector_records,
        "ordinal_sequence_check": {
            "expected_ordinals": expected_ordinals,
            "observed_ordinals": observed_ordinals,
            "status": (
                "phase_ordinals_current"
                if observed_ordinals == expected_ordinals
                else "phase_ordinals_stale"
            ),
        },
        "detector_scope": (
            "bounded static phase-staleness detector joined to current "
            "ROADMAP heading order, active blocker TODO refs, committed "
            "section sidecars, and dependency graph edge status"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a bounded stale-phase detector for the "
            "current ROADMAP Near Term, Mid Term, and Longer Term sections by "
            "joining the phase sequence map, phase dependency graph, active "
            "blocker TODO refs, section sidecar presence, and dependency edge "
            "status. It rejects stale phase records. The phase "
            "promotion/demotion workflow is recorded separately. CI phase "
            "freshness gating, evidence-status refresh reporting, and owner "
            "review signoff remain missing."
        ),
    }


def validate_roadmap_phase_staleness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapPhaseStalenessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_phase_staleness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapPhaseStalenessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_phase_staleness_boundary_record(root)
    issues: list[RoadmapPhaseStalenessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_PHASE_STALENESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP phase staleness schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "phase staleness detector must not claim workflow or CI freshness readiness"))
    for key in (
        "source_phase_boundary_input",
        "source_dependency_graph_input",
        "source_phase_count",
        "source_section_count",
        "source_section_sequence_status",
        "dependency_graph_status",
        "dependency_edge_count",
        "dependency_graph_stale_edge_count",
        "phase_detector_status",
        "phase_record_count",
        "stale_phase_record_count",
        "stale_phase_records",
        "detector_records",
        "ordinal_sequence_check",
        "detector_scope",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current phase staleness inputs"))
    if data.get("source_section_sequence_status") != "roadmap_major_sections_in_expected_order":
        issues.append(_issue("invalid_source_section_sequence", "source phase sequence must be current"))
    if data.get("dependency_graph_status") != "phase_dependency_graph_recorded":
        issues.append(_issue("invalid_dependency_graph_status", "dependency graph must be current before phase staleness can pass"))
    if data.get("stale_phase_record_count") != 0:
        issues.append(_issue("stale_phase_record_detected", "phase detector must not contain stale phase records"))
    if data.get("phase_detector_status") != "no_stale_phase_records_detected":
        issues.append(_issue("invalid_phase_detector_status", "phase detector status must report no stale phase records"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "bounded stale-phase detector" not in boundary_text
        or "rejects stale phase records" not in boundary_text
        or "phase promotion/demotion workflow is recorded separately" not in boundary_text
        or "CI phase freshness gating" not in boundary_text
        or "owner review signoff" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate stale detection from workflow, CI, refresh, and owner signoff"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapPhaseStalenessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        phase_record_count=data.get("phase_record_count") if isinstance(data.get("phase_record_count"), int) else 0,
        stale_phase_record_count=(
            data.get("stale_phase_record_count")
            if isinstance(data.get("stale_phase_record_count"), int)
            else 0
        ),
        dependency_edge_count=data.get("dependency_edge_count") if isinstance(data.get("dependency_edge_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_phase_staleness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_phase_staleness_boundary(boundary)
    lines = [
        "ROADMAP phase staleness boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| phase_record_count | {validation.phase_record_count} |",
        f"| dependency_edge_count | {validation.dependency_edge_count} |",
        f"| stale_phase_record_count | {validation.stale_phase_record_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _detector_record(
    sequence_record: dict[str, Any] | None,
    graph_node: dict[str, Any] | None,
    graph_edge: dict[str, Any] | None,
    sequence_boundary: dict[str, Any],
    dependency_graph: dict[str, Any],
) -> dict[str, Any]:
    section_id = (
        sequence_record["section_id"]
        if sequence_record is not None
        else graph_node["section_id"]
        if graph_node is not None
        else "<missing>"
    )
    reasons: list[str] = []
    if sequence_boundary["section_sequence_status"] != "roadmap_major_sections_in_expected_order":
        reasons.append("source_phase_sequence_stale")
    if dependency_graph["dependency_graph_status"] != "phase_dependency_graph_recorded":
        reasons.append("dependency_graph_stale")
    if sequence_record is None:
        reasons.append("missing_sequence_record")
    if graph_node is None:
        reasons.append("missing_dependency_graph_node")
    if sequence_record is not None:
        if sequence_record["roadmap_heading_present"] is not True:
            reasons.append("roadmap_heading_missing")
        if sequence_record["blocking_todo_present"] is not True:
            reasons.append("active_blocking_todo_missing")
    if graph_node is not None:
        if graph_node["node_status"] != "phase_dependency_node_current":
            reasons.append("dependency_graph_node_stale")
        if not all(sidecar["exists"] for sidecar in graph_node["section_sidecar_refs"]):
            reasons.append("section_sidecar_missing")
    if graph_edge is not None and graph_edge["dependency_edge_status"] != "dependency_edge_current":
        reasons.append("dependency_edge_stale")
    if graph_node is not None and sequence_record is not None:
        for key in ("phase", "ordinal", "roadmap_heading", "blocking_todo_phrase"):
            if graph_node.get(key) != sequence_record.get(key):
                reasons.append(f"sequence_graph_{key}_mismatch")
    return {
        "section_id": section_id,
        "phase": sequence_record.get("phase") if sequence_record is not None else None,
        "ordinal": sequence_record.get("ordinal") if sequence_record is not None else None,
        "roadmap_heading_present": (
            sequence_record.get("roadmap_heading_present")
            if sequence_record is not None
            else False
        ),
        "blocking_todo_present": (
            sequence_record.get("blocking_todo_present")
            if sequence_record is not None
            else False
        ),
        "dependency_node_status": (
            graph_node.get("node_status")
            if graph_node is not None
            else "missing_dependency_graph_node"
        ),
        "dependency_edge_status": (
            graph_edge.get("dependency_edge_status")
            if graph_edge is not None
            else "root_or_no_explicit_dependency_edge"
        ),
        "sidecar_ref_count": (
            len(graph_node["section_sidecar_refs"])
            if graph_node is not None
            else 0
        ),
        "missing_sidecar_ref_count": (
            sum(1 for sidecar in graph_node["section_sidecar_refs"] if not sidecar["exists"])
            if graph_node is not None
            else 0
        ),
        "phase_detector_status": (
            "phase_current" if not reasons else "stale_phase_detected"
        ),
        "stale_reasons": reasons,
    }


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapPhaseStalenessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP phase staleness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapPhaseStalenessBoundaryIssue],
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
    issues: list[RoadmapPhaseStalenessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapPhaseStalenessBoundaryIssue:
    return RoadmapPhaseStalenessBoundaryIssue(code=code, message=message)
