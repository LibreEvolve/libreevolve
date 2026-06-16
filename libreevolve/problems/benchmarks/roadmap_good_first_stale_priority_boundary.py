from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_good_first_dependency_refresh_boundary import (
    roadmap_good_first_dependency_refresh_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_good_first_followups_boundary import (
    roadmap_good_first_followups_boundary_record,
)


ROADMAP_GOOD_FIRST_STALE_PRIORITY_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_good_first_stale_priority_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "good_first_stale_priority_detector_recorded_with_separate_score_model"
)
SOURCE_GOOD_FIRST_BOUNDARY_INPUT = "papers/roadmap_good_first_followups_boundary.json"
DEPENDENCY_REFRESH_BOUNDARY_INPUT = (
    "papers/roadmap_good_first_dependency_refresh_boundary.json"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_good_first_priority_items",
    "dependency_refresh_records",
    "ordinal_sequence_check",
    "live_dependency_ref_check",
    "blocker_label_check",
    "stale_priority_records",
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


@dataclass(frozen=True)
class RoadmapGoodFirstStalePriorityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapGoodFirstStalePriorityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    priority_item_count: int
    stale_priority_count: int
    missing_evidence_count: int
    issues: list[RoadmapGoodFirstStalePriorityBoundaryIssue]


def roadmap_good_first_stale_priority_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Good First stale-priority detector record."""

    root_path = Path(root)
    source_boundary = roadmap_good_first_followups_boundary_record(root_path)
    dependency_refresh = roadmap_good_first_dependency_refresh_boundary_record(root_path)
    dependency_by_id = {
        record["item_id"]: record
        for record in dependency_refresh["dependency_records"]
    }
    detector_records = [
        _detector_record(priority_record, dependency_by_id.get(priority_record["item_id"]))
        for priority_record in source_boundary["priority_records"]
    ]
    stale_priority_records = [
        record
        for record in detector_records
        if record["priority_detector_status"] != "priority_current"
    ]
    expected_ordinals = list(range(1, len(detector_records) + 1))
    observed_ordinals = [record["ordinal"] for record in detector_records]
    return {
        "schema": ROADMAP_GOOD_FIRST_STALE_PRIORITY_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_good_first_boundary_input": SOURCE_GOOD_FIRST_BOUNDARY_INPUT,
        "dependency_refresh_boundary_input": DEPENDENCY_REFRESH_BOUNDARY_INPUT,
        "source_priority_item_count": source_boundary["priority_item_count"],
        "dependency_refresh_record_count": dependency_refresh["dependency_record_count"],
        "ordinal_sequence_check": {
            "expected_ordinals": expected_ordinals,
            "observed_ordinals": observed_ordinals,
            "status": (
                "ordinal_sequence_current"
                if observed_ordinals == expected_ordinals
                else "ordinal_sequence_stale"
            ),
        },
        "priority_detector_status": (
            "no_stale_good_first_priorities_detected"
            if not stale_priority_records
            else "stale_good_first_priorities_detected"
        ),
        "priority_item_count": len(detector_records),
        "stale_priority_count": len(stale_priority_records),
        "stale_priority_records": stale_priority_records,
        "detector_records": detector_records,
        "detector_scope": (
            "bounded static priority-order detector joined to dependency refresh "
            "records; priority score model is recorded separately"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a bounded stale-priority detector for the "
            "current ROADMAP Good First Follow-Ups by joining the static "
            "priority map to dependency-state refresh records, ordinal order, "
            "live dependency refs, blocker labels, and ROADMAP phrase checks. "
            "It rejects stale priority records. Priority scoring is recorded "
            "separately. It does not claim CI freshness enforcement, "
            "validation-artifact freshness, or owner review signoff."
        ),
    }


def validate_roadmap_good_first_stale_priority_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapGoodFirstStalePriorityBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_good_first_stale_priority_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapGoodFirstStalePriorityBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_good_first_stale_priority_boundary_record(root)
    issues: list[RoadmapGoodFirstStalePriorityBoundaryIssue] = []
    if data.get("schema") != ROADMAP_GOOD_FIRST_STALE_PRIORITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Good First stale-priority schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "stale-priority detector must not claim priority-score readiness"))
    for key in (
        "source_good_first_boundary_input",
        "dependency_refresh_boundary_input",
        "source_priority_item_count",
        "dependency_refresh_record_count",
        "ordinal_sequence_check",
        "priority_detector_status",
        "priority_item_count",
        "stale_priority_count",
        "stale_priority_records",
        "detector_records",
        "detector_scope",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current Good First stale-priority inputs"))
    if data.get("stale_priority_count") != 0:
        issues.append(_issue("stale_priority_detected", "Good First priority order must not contain stale detector records"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "bounded stale-priority detector" not in boundary_text
        or "rejects stale priority records" not in boundary_text
        or "Priority scoring is recorded separately" not in boundary_text
        or "does not claim CI freshness enforcement" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate stale detection from score and CI gates"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapGoodFirstStalePriorityBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        priority_item_count=data.get("priority_item_count") if isinstance(data.get("priority_item_count"), int) else 0,
        stale_priority_count=data.get("stale_priority_count") if isinstance(data.get("stale_priority_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_good_first_stale_priority_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_good_first_stale_priority_boundary(boundary)
    lines = [
        "ROADMAP Good First stale-priority boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| priority_item_count | {validation.priority_item_count} |",
        f"| stale_priority_count | {validation.stale_priority_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _detector_record(
    priority_record: dict[str, Any],
    dependency_record: dict[str, Any] | None,
) -> dict[str, Any]:
    reasons: list[str] = []
    if dependency_record is None:
        reasons.append("missing_dependency_refresh_record")
        dependency_status = "missing_dependency_refresh_record"
        stale_dependency_ref_count = None
        current_blocker_label = None
        source_spec_ordinal = None
    else:
        dependency_status = dependency_record["dependency_refresh_status"]
        stale_dependency_ref_count = dependency_record["stale_dependency_ref_count"]
        current_blocker_label = dependency_record["current_blocker_label"]
        source_spec_ordinal = dependency_record["source_spec_ordinal"]
        if dependency_status != "dependency_state_refreshed":
            reasons.append("dependency_refresh_not_current")
        if stale_dependency_ref_count != 0:
            reasons.append("stale_dependency_ref")
        if dependency_record["roadmap_phrase_present"] is not True:
            reasons.append("missing_roadmap_phrase")
        if source_spec_ordinal != priority_record["ordinal"]:
            reasons.append("ordinal_mismatch")
    if priority_record["roadmap_phrase_present"] is not True:
        reasons.append("source_priority_roadmap_phrase_missing")
    return {
        "item_id": priority_record["item_id"],
        "ordinal": priority_record["ordinal"],
        "source_spec_ordinal": source_spec_ordinal,
        "dependency_refresh_status": dependency_status,
        "stale_dependency_ref_count": stale_dependency_ref_count,
        "roadmap_phrase_present": priority_record["roadmap_phrase_present"],
        "current_blocker_label": current_blocker_label,
        "priority_detector_status": (
            "priority_current" if not reasons else "stale_priority_detected"
        ),
        "stale_reasons": reasons,
    }


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapGoodFirstStalePriorityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Good First stale-priority boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapGoodFirstStalePriorityBoundaryIssue],
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
    issues: list[RoadmapGoodFirstStalePriorityBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapGoodFirstStalePriorityBoundaryIssue:
    return RoadmapGoodFirstStalePriorityBoundaryIssue(code=code, message=message)
