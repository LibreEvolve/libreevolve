from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_PHASE_SEQUENCE_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_phase_sequence_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_phase_sequence_map_with_phase_lifecycle_workflow"
)
EXPECTED_PHASE_ORDER = ("near_term", "mid_term", "longer_term")
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "phase_headings",
    "major_section_sequence",
    "active_blocking_todo_refs",
    "validation_gate_labels",
    "promotion_criteria",
    "dependency_graph_boundary",
    "phase_staleness_detector",
    "promotion_demotion_workflow",
    "ci_phase_freshness_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "ci_phase_freshness_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


PHASE_SECTION_SPECS = (
    {
        "section_id": "candidate_workspace_fidelity",
        "phase": "near_term",
        "ordinal": 1,
        "heading": "### 1. Finish candidate workspace fidelity",
        "blocking_todo": "Add ROADMAP candidate-workspace fidelity readiness criteria.",
        "validation_gate": "candidate workspace fidelity readiness criteria",
        "promotion_criterion": "language/build/workspace fidelity blockers are evidence-mapped",
    },
    {
        "section_id": "multi_objective_search",
        "phase": "near_term",
        "ordinal": 2,
        "heading": "### 2. Strengthen multi-objective search",
        "blocking_todo": "Add ROADMAP multi-objective search readiness criteria.",
        "validation_gate": "multi-objective archive/search readiness criteria",
        "promotion_criterion": "archive objective policy blockers are evidence-mapped",
    },
    {
        "section_id": "evaluation_cascades",
        "phase": "near_term",
        "ordinal": 3,
        "heading": "### 3. Expand evaluation cascades",
        "blocking_todo": "Add ROADMAP evaluation-cascade readiness criteria.",
        "validation_gate": "evaluation cascade readiness criteria",
        "promotion_criterion": "cascade/oracle/statistical gate blockers are evidence-mapped",
    },
    {
        "section_id": "prompt_context",
        "phase": "near_term",
        "ordinal": 4,
        "heading": "### 4. Prompt and context work",
        "blocking_todo": "Add ROADMAP prompt/context-system readiness criteria.",
        "validation_gate": "prompt/context readiness criteria",
        "promotion_criterion": "prompt packing, retrieval, and context blockers are evidence-mapped",
    },
    {
        "section_id": "documentation_truthfulness",
        "phase": "near_term",
        "ordinal": 5,
        "heading": "### 5. Documentation truthfulness",
        "blocking_todo": "Add semantic evidence mapping for ROADMAP current-state and priority",
        "validation_gate": "semantic documentation claim evidence map",
        "promotion_criterion": "README/ROADMAP/papers semantic verification gaps are evidence-mapped",
    },
    {
        "section_id": "async_resumable_runtime",
        "phase": "mid_term",
        "ordinal": 6,
        "heading": "### 6. Async and resumable runtime",
        "blocking_todo": "Add ROADMAP async/resumable-runtime readiness criteria.",
        "validation_gate": "async/resumable runtime readiness criteria",
        "promotion_criterion": "async queue and pending-work restore blockers are evidence-mapped",
    },
    {
        "section_id": "backend_scheduling_and_critique",
        "phase": "mid_term",
        "ordinal": 7,
        "heading": "### 7. Backend scheduling and critique",
        "blocking_todo": "Add ROADMAP backend-scheduling and critique readiness criteria.",
        "validation_gate": "backend scheduling and critique readiness criteria",
        "promotion_criterion": "role scheduler and critique calibration blockers are evidence-mapped",
    },
    {
        "section_id": "plugin_extensibility",
        "phase": "mid_term",
        "ordinal": 8,
        "heading": "### 8. Plugin extensibility",
        "blocking_todo": "Add ROADMAP plugin-extensibility readiness criteria.",
        "validation_gate": "plugin extensibility readiness criteria",
        "promotion_criterion": "plugin package/schema/provenance blockers are evidence-mapped",
    },
    {
        "section_id": "representative_benchmarks",
        "phase": "longer_term",
        "ordinal": 9,
        "heading": "### 9. Representative benchmarks",
        "blocking_todo": "Add ROADMAP representative-benchmark portfolio readiness criteria.",
        "validation_gate": "representative benchmark portfolio readiness criteria",
        "promotion_criterion": "benchmark portfolio and certification blockers are evidence-mapped",
    },
    {
        "section_id": "operational_maturity",
        "phase": "longer_term",
        "ordinal": 10,
        "heading": "### 10. Operational maturity",
        "blocking_todo": "Add ROADMAP operational-maturity acceptance criteria.",
        "validation_gate": "operational maturity acceptance criteria",
        "promotion_criterion": "release, CI, run-artifact, and observability blockers are evidence-mapped",
    },
)


@dataclass(frozen=True)
class RoadmapPhaseSequenceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapPhaseSequenceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    phase_count: int
    section_count: int
    missing_evidence_count: int
    issues: list[RoadmapPhaseSequenceBoundaryIssue]


def roadmap_phase_sequence_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP phase and sequencing map."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    todo_text = _read_text(root_path / "docs" / "todo" / "roadmap.md")
    records = [
        _section_record(roadmap_text, todo_text, spec)
        for spec in PHASE_SECTION_SPECS
    ]
    phase_counts = {
        phase: sum(1 for record in records if record["phase"] == phase)
        for phase in EXPECTED_PHASE_ORDER
    }
    line_numbers = [
        record["roadmap_heading_line"]
        for record in records
        if isinstance(record["roadmap_heading_line"], int)
    ]
    return {
        "schema": ROADMAP_PHASE_SEQUENCE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "phase_order": list(EXPECTED_PHASE_ORDER),
        "phase_count": len(EXPECTED_PHASE_ORDER),
        "phase_section_counts": phase_counts,
        "section_count": len(records),
        "section_records": records,
        "section_sequence_status": (
            "roadmap_major_sections_in_expected_order"
            if line_numbers == sorted(line_numbers) and len(line_numbers) == len(records)
            else "roadmap_major_sections_missing_or_reordered"
        ),
        "active_blocking_todo_ref_count": sum(
            1 for record in records if record["blocking_todo_present"]
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the current ROADMAP Near Term, Mid Term, "
            "and Longer Term section sequence with active blocker TODO refs, "
            "validation gate labels, and promotion criteria. It does not claim "
            "a CI phase freshness gate or owner review signoff. The bounded "
            "dependency graph, stale-phase detector, and phase "
            "promotion/demotion workflow are recorded separately."
        ),
    }


def validate_roadmap_phase_sequence_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapPhaseSequenceBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_phase_sequence_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapPhaseSequenceBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_phase_sequence_boundary_record(root)
    issues: list[RoadmapPhaseSequenceBoundaryIssue] = []
    if data.get("schema") != ROADMAP_PHASE_SEQUENCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP phase sequence boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP phase sequence boundary must not claim full sequencing freshness readiness"))
    for key in (
        "phase_order",
        "phase_count",
        "phase_section_counts",
        "section_count",
        "section_records",
        "section_sequence_status",
        "active_blocking_todo_ref_count",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP/TODO inputs"))
    if data.get("section_sequence_status") != "roadmap_major_sections_in_expected_order":
        issues.append(_issue("invalid_section_sequence", "ROADMAP major sections are missing or out of expected order"))
    if data.get("active_blocking_todo_ref_count") != len(PHASE_SECTION_SPECS):
        issues.append(_issue("missing_blocking_todo_ref", "not every phase section has an active blocking TODO ref"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "phase promotion/demotion workflow are recorded separately" not in boundary_text
        or "CI phase freshness gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded phase map from full sequencing freshness proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapPhaseSequenceBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        phase_count=data.get("phase_count") if isinstance(data.get("phase_count"), int) else 0,
        section_count=data.get("section_count") if isinstance(data.get("section_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_phase_sequence_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_phase_sequence_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP phase sequence boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| phase_count | {validation.phase_count} |",
        f"| section_count | {validation.section_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _section_record(
    roadmap_text: str,
    todo_text: str,
    spec: dict[str, Any],
) -> dict[str, Any]:
    heading = spec["heading"]
    line = _line_number_for_phrase(roadmap_text, heading)
    return {
        "section_id": spec["section_id"],
        "phase": spec["phase"],
        "ordinal": spec["ordinal"],
        "roadmap_heading": heading,
        "roadmap_heading_present": line is not None,
        "roadmap_heading_line": line,
        "blocking_todo_phrase": spec["blocking_todo"],
        "blocking_todo_present": _contains_phrase(todo_text, spec["blocking_todo"]),
        "validation_gate": spec["validation_gate"],
        "promotion_criterion": spec["promotion_criterion"],
        "sequencing_status": "bounded_static_phase_assignment",
    }


def _line_number_for_phrase(text: str, phrase: str) -> int | None:
    normalized_phrase = " ".join(phrase.casefold().split())
    for index, line in enumerate(text.splitlines(), start=1):
        if normalized_phrase in " ".join(line.casefold().split()):
            return index
    return None


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
) -> tuple[dict[str, Any] | None, list[RoadmapPhaseSequenceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP phase sequence boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapPhaseSequenceBoundaryIssue],
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
    issues: list[RoadmapPhaseSequenceBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapPhaseSequenceBoundaryIssue:
    return RoadmapPhaseSequenceBoundaryIssue(code=code, message=message)
