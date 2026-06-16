from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_phase_sequence_boundary import (
    roadmap_phase_sequence_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_phase_dependency_graph_boundary import (
    roadmap_phase_dependency_graph_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_phase_staleness_boundary import (
    roadmap_phase_staleness_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_phase_promotion_workflow_boundary import (
    roadmap_phase_promotion_workflow_boundary_record,
)


ROADMAP_PHASE_FRESHNESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_phase_freshness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_phase_freshness_matrix_with_promotion_workflow"
)
SOURCE_PHASE_BOUNDARY_INPUT = "papers/roadmap_phase_sequence_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "dependency_graph",
    "phase_staleness_detector",
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


CRITERION_SPECS = (
    {
        "criterion_id": "dependency_graph",
        "phase_surface": "Near Term, Mid Term, and Longer Term section prerequisites",
        "current_scope": "bounded dependency graph connecting each major section to prerequisites and blocking TODOs",
        "missing_readiness": "staleness and CI freshness gates that refresh dependency edges after evidence changes",
        "sidecars": (
            "papers/roadmap_phase_sequence_boundary.json",
            "papers/todo_canonical_gap_boundary.json",
            "papers/roadmap_phase_dependency_graph_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "dependency graph",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "prerequisites, blocking TODOs",
            },
        ),
        "validation_gate": "ROADMAP phase dependency graph",
        "readiness_status": "phase_dependency_graph_recorded_without_freshness_gate",
    },
    {
        "criterion_id": "phase_staleness_detector",
        "phase_surface": "phase labels and section ordering",
        "current_scope": "bounded detector over section order, active blocker TODO refs, sidecar presence, and dependency graph status",
        "missing_readiness": "workflow, CI gate, evidence refresh report, and owner signoff that act on stale phase records",
        "sidecars": (
            "papers/roadmap_claim_evidence_boundary.json",
            "papers/documentation_claim_inventory.json",
            "papers/roadmap_phase_staleness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "stale-phase detector",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "refreshed when implementation or evidence status changes",
            },
        ),
        "validation_gate": "phase staleness detector tied to implementation and evidence status",
        "readiness_status": "phase_staleness_detector_recorded_without_workflow_gate",
    },
    {
        "criterion_id": "promotion_demotion_workflow",
        "phase_surface": "phase changes, item promotions, item demotions, and replacements",
        "current_scope": "written phase promotion/demotion workflow covering claim surfaces, sidecars, dependency graph refresh, stale phase records, and manifest gate",
        "missing_readiness": "CI gate, evidence refresh report, and owner signoff that enforce the workflow automatically",
        "sidecars": (
            "papers/roadmap_good_first_freshness_boundary.json",
            "papers/roadmap_non_goal_drift_boundary.json",
            "papers/roadmap_phase_promotion_workflow_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "promotion/demotion workflow",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "promotion criteria",
            },
        ),
        "validation_gate": "phase promotion/demotion evidence workflow",
        "readiness_status": "phase_promotion_demotion_workflow_recorded_without_ci_gate",
    },
    {
        "criterion_id": "ci_phase_freshness_gate",
        "phase_surface": "CI and paper-manifest checks for ROADMAP phase drift",
        "current_scope": "repo-root sidecar shape validation",
        "missing_readiness": "CI gate that fails stale phase labels, missing dependency edges, or incomplete promotion records",
        "sidecars": (
            "papers/ci_workflow_coverage_boundary.json",
            "papers/roadmap_phase_sequence_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "CI phase freshness gate",
            },
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "drift check",
            },
        ),
        "validation_gate": "CI phase freshness gate",
        "readiness_status": "manifest_shape_check_without_ci_phase_gate",
    },
    {
        "criterion_id": "evidence_status_refresh",
        "phase_surface": "code, papers, README, sidecars, and ROADMAP evidence status",
        "current_scope": "phase sidecar records validation-gate labels but no current evidence-state refresh",
        "missing_readiness": "freshness report that refreshes phase labels when code, papers, README, or sidecar evidence changes",
        "sidecars": (
            "papers/implementation_evidence_map_boundary.json",
            "papers/status_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "code, papers, README, or sidecar evidence changes",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "validation gates",
            },
        ),
        "validation_gate": "phase evidence-status refresh report",
        "readiness_status": "validation_labels_without_evidence_refresh",
    },
    {
        "criterion_id": "owner_review_signoff",
        "phase_surface": "owner-reviewed ROADMAP phase lifecycle decisions",
        "current_scope": "no owner-reviewed signoff record for phase labels or ordering",
        "missing_readiness": "review signoff for phase moves, deferrals, dependency changes, and scope changes",
        "sidecars": (
            "papers/todo_ledger_ownership_boundary.json",
            "papers/roadmap_readiness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "owner review signoff",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "phase labels and item ordering",
            },
        ),
        "validation_gate": "owner-reviewed phase freshness signoff",
        "readiness_status": "no_owner_review_signoff",
    },
)


@dataclass(frozen=True)
class RoadmapPhaseFreshnessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapPhaseFreshnessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    freshness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapPhaseFreshnessBoundaryIssue]


def roadmap_phase_freshness_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP phase freshness readiness matrix."""

    root_path = Path(root)
    source_boundary = roadmap_phase_sequence_boundary_record(root_path)
    dependency_graph = roadmap_phase_dependency_graph_boundary_record(root_path)
    staleness = roadmap_phase_staleness_boundary_record(root_path)
    promotion_workflow = roadmap_phase_promotion_workflow_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_PHASE_FRESHNESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_phase_boundary_input": SOURCE_PHASE_BOUNDARY_INPUT,
        "source_phase_count": source_boundary["phase_count"],
        "source_section_count": source_boundary["section_count"],
        "source_section_sequence_status": source_boundary["section_sequence_status"],
        "phase_dependency_graph_boundary_input": "papers/roadmap_phase_dependency_graph_boundary.json",
        "phase_dependency_graph_status": dependency_graph["dependency_graph_status"],
        "phase_dependency_graph_edge_count": dependency_graph["edge_count"],
        "phase_dependency_graph_stale_edge_count": dependency_graph["stale_dependency_edge_count"],
        "phase_staleness_boundary_input": "papers/roadmap_phase_staleness_boundary.json",
        "phase_staleness_detector_status": staleness["phase_detector_status"],
        "phase_staleness_record_count": staleness["phase_record_count"],
        "stale_phase_record_count": staleness["stale_phase_record_count"],
        "phase_promotion_workflow_input": "papers/roadmap_phase_promotion_workflow_boundary.json",
        "phase_promotion_workflow_status": promotion_workflow["boundary_status"],
        "phase_promotion_workflow_phrase_count": promotion_workflow["workflow_phrase_count"],
        "phase_promotion_workflow_sidecar_ref_count": promotion_workflow["sidecar_ref_count"],
        "freshness_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "freshness_criteria": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records ROADMAP phase freshness readiness criteria "
            "tied to the bounded static phase sequence map and phase "
            "dependency graph plus the bounded stale-phase detector and phase "
            "promotion/demotion workflow. It does not claim a CI phase "
            "freshness gate, evidence-status refresh report, or owner review "
            "signoff."
        ),
    }


def validate_roadmap_phase_freshness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapPhaseFreshnessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_phase_freshness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapPhaseFreshnessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_phase_freshness_boundary_record(root)
    issues: list[RoadmapPhaseFreshnessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_PHASE_FRESHNESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP phase freshness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP phase freshness boundary must not claim dependency-gate readiness"))
    for key in (
        "source_phase_boundary_input",
        "source_phase_count",
        "source_section_count",
        "source_section_sequence_status",
        "phase_dependency_graph_boundary_input",
        "phase_dependency_graph_status",
        "phase_dependency_graph_edge_count",
        "phase_dependency_graph_stale_edge_count",
        "phase_staleness_boundary_input",
        "phase_staleness_detector_status",
        "phase_staleness_record_count",
        "stale_phase_record_count",
        "phase_promotion_workflow_input",
        "phase_promotion_workflow_status",
        "phase_promotion_workflow_phrase_count",
        "phase_promotion_workflow_sidecar_ref_count",
        "freshness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "freshness_criteria",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP phase freshness inputs"))
    if data.get("source_section_sequence_status") != "roadmap_major_sections_in_expected_order":
        issues.append(_issue("invalid_source_section_sequence", "source phase sequence is not currently in expected order"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "phase dependency graph" not in boundary_text
        or "bounded stale-phase detector" not in boundary_text
        or "promotion/demotion workflow" not in boundary_text
        or "CI phase freshness gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate phase freshness readiness from implemented phase refresh gates"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapPhaseFreshnessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        freshness_criterion_count=data.get("freshness_criterion_count") if isinstance(data.get("freshness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_phase_freshness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_phase_freshness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP phase freshness boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| freshness_criterion_count | {validation.freshness_criterion_count} |",
        f"| sidecar_ref_count | {validation.sidecar_ref_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _criterion_record(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "criterion_id": spec["criterion_id"],
        "phase_surface": spec["phase_surface"],
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "sidecar_refs": [_sidecar_ref(root, path) for path in spec["sidecars"]],
        "active_todo_refs": [
            _active_todo_ref(root, todo) for todo in spec["active_todos"]
        ],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _sidecar_ref(root: Path, path: str) -> dict[str, Any]:
    return {"path": path, "exists": (root / path).exists()}


def _active_todo_ref(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    required_phrase = spec["required_phrase"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": required_phrase,
        "required_phrase_present": _contains_phrase(text, required_phrase),
        "exists": (root / path).exists(),
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized_text = " ".join(text.casefold().split())
    normalized_phrase = " ".join(phrase.casefold().split())
    return normalized_phrase in normalized_text


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapPhaseFreshnessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP phase freshness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapPhaseFreshnessBoundaryIssue],
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
    issues: list[RoadmapPhaseFreshnessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapPhaseFreshnessBoundaryIssue:
    return RoadmapPhaseFreshnessBoundaryIssue(code=code, message=message)
