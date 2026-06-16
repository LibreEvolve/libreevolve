from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_good_first_followups_boundary import (
    roadmap_good_first_followups_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_good_first_dependency_refresh_boundary import (
    roadmap_good_first_dependency_refresh_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_good_first_stale_priority_boundary import (
    roadmap_good_first_stale_priority_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_good_first_priority_score_boundary import (
    roadmap_good_first_priority_score_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_good_first_ci_priority_gate_boundary import (
    roadmap_good_first_ci_priority_gate_boundary_record,
)


ROADMAP_GOOD_FIRST_FRESHNESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_good_first_freshness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_good_first_freshness_matrix_with_ci_priority_gate_without_artifact_signoff"
)
SOURCE_GOOD_FIRST_BOUNDARY_INPUT = "papers/roadmap_good_first_followups_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "dependency_state_refresh",
    "stale_priority_detector",
    "calibrated_priority_score_model",
    "ci_priority_freshness_gate",
    "validation_artifact_refresh",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "validation_artifact_refresh": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "dependency_state_refresh",
        "freshness_surface": "active implementation TODO state and blocking prerequisites",
        "current_scope": "dependency-state refresh records for the four current good-first items",
        "missing_readiness": "validation-artifact freshness tied to refreshed dependency state and the priority score model",
        "sidecars": (
            "papers/roadmap_good_first_followups_boundary.json",
            "papers/roadmap_good_first_dependency_refresh_boundary.json",
            "papers/todo_canonical_gap_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "live active TODO dependency refs",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "current blocker labels",
            },
        ),
        "validation_gate": "dependency-state refresh report for every good-first item",
        "readiness_status": "dependency_state_refresh_recorded_with_ci_priority_gate",
    },
    {
        "criterion_id": "stale_priority_detector",
        "freshness_surface": "ROADMAP Good First Follow-Ups section ordering",
        "current_scope": "bounded stale-priority detector joined to dependency refresh records",
        "missing_readiness": "validation-artifact freshness that promotes or demotes priorities after broader evidence changes",
        "sidecars": (
            "papers/roadmap_claim_evidence_boundary.json",
            "papers/documentation_claim_inventory.json",
            "papers/roadmap_good_first_stale_priority_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "stale-priority detector",
            },
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "drift check",
            },
        ),
        "validation_gate": "stale-priority detector tied to ROADMAP and dependency refresh drift",
        "readiness_status": "stale_priority_detector_recorded_with_ci_priority_gate",
    },
    {
        "criterion_id": "calibrated_priority_score_model",
        "freshness_surface": "priority ordering rationale and AlphaEvolve-gap impact",
        "current_scope": "bounded deterministic score model combining dependency readiness, stale-priority state, validation gates, and AlphaEvolve impact",
        "missing_readiness": "validation-artifact freshness that enforces the score model after broader evidence changes",
        "sidecars": (
            "papers/roadmap_readiness_boundary.json",
            "papers/implementation_evidence_map_boundary.json",
            "papers/roadmap_good_first_priority_score_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "bounded deterministic priority score model",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "AlphaEvolve-facing behavior has been classified",
            },
        ),
        "validation_gate": "priority score model with recorded inputs and weights",
        "readiness_status": "priority_score_model_recorded_with_ci_priority_gate",
    },
    {
        "criterion_id": "ci_priority_freshness_gate",
        "freshness_surface": "CI and manifest checks for priority drift",
        "current_scope": "paper-manifest sidecar validation plus docs/paper/boundary workflow gate",
        "missing_readiness": "validation-artifact freshness and owner signoff after CI gate execution",
        "sidecars": (
            "papers/ci_workflow_coverage_boundary.json",
            "papers/roadmap_good_first_followups_boundary.json",
            "papers/roadmap_good_first_ci_priority_gate_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "CI freshness gate",
            },
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "drift evidence",
            },
        ),
        "validation_gate": "CI priority freshness gate",
        "readiness_status": "ci_priority_freshness_gate_recorded_without_artifact_signoff",
    },
    {
        "criterion_id": "validation_artifact_refresh",
        "freshness_surface": "expected validation artifacts for each good-first item",
        "current_scope": "static validation-gate labels in the bounded priority map",
        "missing_readiness": "artifact freshness proof for durable indexes, benchmark fixture, resume coverage, and calibration reports",
        "sidecars": (
            "papers/benchmark_coverage_inventory.json",
            "papers/roadmap_source_span_coverage_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "expected validation artifacts",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "runtime feedback-calibration fixture",
            },
        ),
        "validation_gate": "per-item validation-artifact freshness report",
        "readiness_status": "validation_gate_labels_without_artifact_freshness",
    },
    {
        "criterion_id": "owner_review_signoff",
        "freshness_surface": "human review of priority promotions, demotions, and replacements",
        "current_scope": "no review record for the good-first ordering",
        "missing_readiness": "owner signoff when priority items change, become complete, or are displaced by stronger AlphaEvolve gaps",
        "sidecars": (
            "papers/todo_ledger_ownership_boundary.json",
            "papers/roadmap_phase_sequence_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "owner review signoff",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "dependencies or implementation states change",
            },
        ),
        "validation_gate": "owner-reviewed good-first freshness signoff",
        "readiness_status": "no_owner_review_signoff",
    },
)


@dataclass(frozen=True)
class RoadmapGoodFirstFreshnessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapGoodFirstFreshnessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    freshness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapGoodFirstFreshnessBoundaryIssue]


def roadmap_good_first_freshness_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Good First Follow-Ups freshness readiness matrix."""

    root_path = Path(root)
    source_boundary = roadmap_good_first_followups_boundary_record(root_path)
    dependency_refresh = roadmap_good_first_dependency_refresh_boundary_record(root_path)
    stale_priority = roadmap_good_first_stale_priority_boundary_record(root_path)
    priority_score = roadmap_good_first_priority_score_boundary_record(root_path)
    ci_gate = roadmap_good_first_ci_priority_gate_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_GOOD_FIRST_FRESHNESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_good_first_boundary_input": SOURCE_GOOD_FIRST_BOUNDARY_INPUT,
        "source_priority_item_count": source_boundary["priority_item_count"],
        "source_active_todo_ref_count": source_boundary["active_todo_ref_count"],
        "dependency_refresh_boundary_input": "papers/roadmap_good_first_dependency_refresh_boundary.json",
        "dependency_refresh_record_count": dependency_refresh["dependency_record_count"],
        "dependency_refresh_stale_ref_count": dependency_refresh["stale_dependency_ref_count"],
        "stale_priority_boundary_input": "papers/roadmap_good_first_stale_priority_boundary.json",
        "stale_priority_count": stale_priority["stale_priority_count"],
        "priority_detector_status": stale_priority["priority_detector_status"],
        "priority_score_boundary_input": "papers/roadmap_good_first_priority_score_boundary.json",
        "priority_score_rank_mismatch_count": priority_score["rank_mismatch_count"],
        "priority_score_order_match": priority_score["priority_order_match"],
        "ci_priority_gate_boundary_input": "papers/roadmap_good_first_ci_priority_gate_boundary.json",
        "ci_priority_gate_status": ci_gate["ci_gate_status"],
        "ci_priority_gate_missing_record_count": ci_gate["missing_gate_record_count"],
        "freshness_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "freshness_criteria": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records Good First Follow-Ups freshness readiness "
            "criteria tied to the bounded static priority map and the recorded "
            "dependency-state refresh, stale-priority detector, and priority "
            "score model, and CI priority gate boundaries. It does not claim "
            "validation-artifact freshness or owner review signoff."
        ),
    }


def validate_roadmap_good_first_freshness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapGoodFirstFreshnessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_good_first_freshness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapGoodFirstFreshnessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_good_first_freshness_boundary_record(root)
    issues: list[RoadmapGoodFirstFreshnessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_GOOD_FIRST_FRESHNESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP good-first freshness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "Good-first freshness boundary must not claim refresh-gate readiness"))
    for key in (
        "source_good_first_boundary_input",
        "source_priority_item_count",
        "source_active_todo_ref_count",
        "dependency_refresh_boundary_input",
        "dependency_refresh_record_count",
        "dependency_refresh_stale_ref_count",
        "stale_priority_boundary_input",
        "stale_priority_count",
        "priority_detector_status",
        "priority_score_boundary_input",
        "priority_score_rank_mismatch_count",
        "priority_score_order_match",
        "ci_priority_gate_boundary_input",
        "ci_priority_gate_status",
        "ci_priority_gate_missing_record_count",
        "freshness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "freshness_criteria",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current Good First Follow-Ups freshness inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "CI priority gate boundaries" not in boundary_text
        or "does not claim validation-artifact freshness" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate freshness readiness from implemented priority refresh gates"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapGoodFirstFreshnessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        freshness_criterion_count=data.get("freshness_criterion_count") if isinstance(data.get("freshness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_good_first_freshness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_good_first_freshness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP Good First Follow-Ups freshness boundary",
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
        "freshness_surface": spec["freshness_surface"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapGoodFirstFreshnessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP good-first freshness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapGoodFirstFreshnessBoundaryIssue],
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
    issues: list[RoadmapGoodFirstFreshnessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapGoodFirstFreshnessBoundaryIssue:
    return RoadmapGoodFirstFreshnessBoundaryIssue(code=code, message=message)
