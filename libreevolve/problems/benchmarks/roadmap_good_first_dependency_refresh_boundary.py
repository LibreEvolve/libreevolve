from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_good_first_followups_boundary import (
    GOOD_FIRST_FOLLOWUP_SPECS,
    roadmap_good_first_followups_boundary_record,
)


ROADMAP_GOOD_FIRST_DEPENDENCY_REFRESH_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_good_first_dependency_refresh_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "good_first_dependency_state_refresh_recorded_with_priority_score_model"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_good_first_priority_items",
    "active_dependency_todo_refs",
    "current_blocker_labels",
    "dependency_refresh_records",
    "validation_gate_expectations",
    "stale_priority_detector",
    "calibrated_priority_score_model",
    "ci_priority_freshness_gate",
    "validation_artifact_refresh",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "ci_priority_freshness_gate": "not_recorded_locally",
    "validation_artifact_refresh": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
SOURCE_GOOD_FIRST_BOUNDARY_INPUT = "papers/roadmap_good_first_followups_boundary.json"


@dataclass(frozen=True)
class RoadmapGoodFirstDependencyRefreshBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapGoodFirstDependencyRefreshBoundaryValidation:
    ok: bool
    boundary_status: str | None
    dependency_record_count: int
    active_dependency_ref_count: int
    stale_dependency_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapGoodFirstDependencyRefreshBoundaryIssue]


def roadmap_good_first_dependency_refresh_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the Good First Follow-Ups dependency-state refresh record."""

    root_path = Path(root)
    source_boundary = roadmap_good_first_followups_boundary_record(root_path)
    records = [
        _dependency_record(root_path, priority_record)
        for priority_record in source_boundary["priority_records"]
    ]
    stale_ref_records = [
        ref
        for record in records
        for ref in record["dependency_todo_refs"]
        if ref["dependency_ref_status"] != "live_active_dependency_ref"
    ]
    return {
        "schema": ROADMAP_GOOD_FIRST_DEPENDENCY_REFRESH_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_good_first_boundary_input": SOURCE_GOOD_FIRST_BOUNDARY_INPUT,
        "source_priority_item_count": source_boundary["priority_item_count"],
        "dependency_record_count": len(records),
        "active_dependency_ref_count": sum(
            len(record["dependency_todo_refs"]) for record in records
        ),
        "stale_dependency_ref_count": len(stale_ref_records),
        "stale_dependency_ref_records": stale_ref_records,
        "dependency_records": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary refreshes the current dependency state for the four "
            "ROADMAP Good First Follow-Ups by rechecking their active TODO "
            "dependency refs, current blocker labels, validation gate "
            "expectations, and AlphaEvolve impact labels. It rejects stale or "
            "missing dependency refs. Stale-priority detection is recorded "
            "separately and priority scoring is recorded separately. It does "
            "not claim CI freshness enforcement, validation-artifact "
            "freshness, or owner review signoff."
        ),
    }


def validate_roadmap_good_first_dependency_refresh_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapGoodFirstDependencyRefreshBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_good_first_dependency_refresh_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapGoodFirstDependencyRefreshBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_good_first_dependency_refresh_boundary_record(root)
    issues: list[RoadmapGoodFirstDependencyRefreshBoundaryIssue] = []
    if data.get("schema") != ROADMAP_GOOD_FIRST_DEPENDENCY_REFRESH_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Good First dependency refresh schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "dependency refresh must not claim priority freshness readiness"))
    for key in (
        "source_good_first_boundary_input",
        "source_priority_item_count",
        "dependency_record_count",
        "active_dependency_ref_count",
        "stale_dependency_ref_count",
        "stale_dependency_ref_records",
        "dependency_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current Good First dependency inputs"))
    if data.get("stale_dependency_ref_count") != 0:
        issues.append(_issue("stale_dependency_ref_detected", "Good First dependency refs must point to live active TODO blocks"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "refreshes the current dependency state" not in boundary_text
        or "rejects stale or missing dependency refs" not in boundary_text
        or "Stale-priority detection is recorded separately" not in boundary_text
        or "priority scoring is recorded separately" not in boundary_text
        or "does not claim CI freshness enforcement" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate dependency refresh from priority freshness gates"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapGoodFirstDependencyRefreshBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        dependency_record_count=data.get("dependency_record_count") if isinstance(data.get("dependency_record_count"), int) else 0,
        active_dependency_ref_count=data.get("active_dependency_ref_count") if isinstance(data.get("active_dependency_ref_count"), int) else 0,
        stale_dependency_ref_count=data.get("stale_dependency_ref_count") if isinstance(data.get("stale_dependency_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_good_first_dependency_refresh_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_good_first_dependency_refresh_boundary(boundary)
    rows = [
        ("schema_status", "ok" if validation.ok else "invalid"),
        ("boundary_status", validation.boundary_status or "unknown"),
        ("dependency_record_count", str(validation.dependency_record_count)),
        ("active_dependency_ref_count", str(validation.active_dependency_ref_count)),
        ("stale_dependency_ref_count", str(validation.stale_dependency_ref_count)),
        ("missing_evidence_count", str(validation.missing_evidence_count)),
    ]
    lines = [
        "# ROADMAP Good First dependency refresh boundary",
        "",
        "| Field | Value |",
        "| --- | --- |",
    ]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    if validation.issues:
        lines.extend(["", "## Issues"])
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in validation.issues)
    return "\n".join(lines) + "\n"


def _dependency_record(
    root: Path,
    priority_record: dict[str, Any],
) -> dict[str, Any]:
    spec = _spec_by_id(priority_record["item_id"])
    dependency_refs = [
        _dependency_ref_record(root, ref, priority_record["item_id"])
        for ref in priority_record["active_todo_refs"]
    ]
    stale_refs = [
        ref
        for ref in dependency_refs
        if ref["dependency_ref_status"] != "live_active_dependency_ref"
    ]
    validation_gates = list(priority_record["validation_gates"])
    return {
        "item_id": priority_record["item_id"],
        "ordinal": priority_record["ordinal"],
        "dependency_readiness": priority_record["dependency_readiness"],
        "current_blocker_label": _current_blocker_label(priority_record["dependency_readiness"]),
        "alphaevolve_impact": priority_record["alphaevolve_impact"],
        "priority_rationale": priority_record["priority_rationale"],
        "dependency_todo_refs": dependency_refs,
        "dependency_todo_ref_count": len(dependency_refs),
        "stale_dependency_ref_count": len(stale_refs),
        "validation_gates": validation_gates,
        "validation_gate_count": len(validation_gates),
        "roadmap_required_phrase": priority_record["roadmap_required_phrase"],
        "roadmap_phrase_present": priority_record["roadmap_phrase_present"],
        "source_spec_ordinal": spec["ordinal"],
        "dependency_refresh_status": (
            "dependency_state_refreshed"
            if not stale_refs and priority_record["roadmap_phrase_present"]
            else "dependency_state_stale_or_incomplete"
        ),
    }


def _dependency_ref_record(
    root: Path,
    ref: dict[str, Any],
    item_id: str,
) -> dict[str, Any]:
    path_text = ref["path"]
    text = _read_text(root / path_text)
    required_phrase = ref["required_phrase"]
    phrase_present = _contains_phrase(text, required_phrase)
    active_marker_present = _active_block_contains_phrase(text, required_phrase)
    return {
        "item_id": item_id,
        "path": path_text,
        "required_phrase": required_phrase,
        "required_phrase_present": phrase_present,
        "active_marker_present": active_marker_present,
        "dependency_ref_status": (
            "live_active_dependency_ref"
            if phrase_present and active_marker_present
            else "missing_or_completed_dependency_ref"
        ),
    }


def _current_blocker_label(dependency_readiness: str) -> str:
    if "_needs_" not in dependency_readiness:
        return "current_blocker_unspecified"
    return dependency_readiness.split("_needs_", 1)[1]


def _spec_by_id(item_id: str) -> dict[str, Any]:
    for spec in GOOD_FIRST_FOLLOWUP_SPECS:
        if spec["item_id"] == item_id:
            return spec
    return {"ordinal": None}


def _active_block_contains_phrase(text: str, phrase: str) -> bool:
    normalized_phrase = " ".join(phrase.casefold().split())
    current_block: list[str] = []
    for line in text.splitlines():
        if line.startswith("- ["):
            if current_block and _block_matches(current_block, normalized_phrase):
                return True
            current_block = [line] if line.startswith("- [ ]") else []
            continue
        if current_block:
            current_block.append(line)
    return bool(current_block and _block_matches(current_block, normalized_phrase))


def _block_matches(lines: list[str], normalized_phrase: str) -> bool:
    normalized_block = " ".join("\n".join(lines).casefold().split())
    return normalized_phrase in normalized_block


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
) -> tuple[dict[str, Any] | None, list[RoadmapGoodFirstDependencyRefreshBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Good First dependency refresh boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapGoodFirstDependencyRefreshBoundaryIssue],
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
    issues: list[RoadmapGoodFirstDependencyRefreshBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    if expected_keys - actual_keys:
        issues.append(_issue("missing_missing_evidence_key", "missing_evidence lacks expected keys"))
    if actual_keys - expected_keys:
        issues.append(_issue("extra_missing_evidence_key", "missing_evidence includes unknown keys"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> RoadmapGoodFirstDependencyRefreshBoundaryIssue:
    return RoadmapGoodFirstDependencyRefreshBoundaryIssue(code, message)
