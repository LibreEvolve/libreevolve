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
from libreevolve.problems.benchmarks.roadmap_good_first_stale_priority_boundary import (
    roadmap_good_first_stale_priority_boundary_record,
)


ROADMAP_GOOD_FIRST_PRIORITY_SCORE_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_good_first_priority_score_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "good_first_priority_score_model_recorded_with_validation_artifact_report"
)
SOURCE_GOOD_FIRST_BOUNDARY_INPUT = "papers/roadmap_good_first_followups_boundary.json"
DEPENDENCY_REFRESH_BOUNDARY_INPUT = (
    "papers/roadmap_good_first_dependency_refresh_boundary.json"
)
STALE_PRIORITY_BOUNDARY_INPUT = "papers/roadmap_good_first_stale_priority_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_good_first_priority_items",
    "dependency_refresh_records",
    "stale_priority_detector",
    "score_feature_weights",
    "dependency_readiness_scores",
    "alphaevolve_impact_scores",
    "priority_score_records",
    "rank_mismatch_records",
    "ci_priority_freshness_gate",
    "validation_artifact_report",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "owner_review_signoff": "not_recorded_locally",
}

SCORE_FEATURE_WEIGHTS = {
    "alphaevolve_impact_score": 10,
    "dependency_readiness_score": 5,
    "live_dependency_refresh_score": 3,
    "validation_gate_count": 1,
    "stale_priority_penalty": -100,
}
DEPENDENCY_READINESS_SCORES = {
    "has_run_local_indexes_needs_durable_tables": 5,
    "sorting_network_candidates_exist_needs_run_evidence": 4,
    "archive_restore_exists_needs_full_workspace_resume_contract": 3,
    "report_contract_exists_needs_runtime_runner": 2,
}
ALPHAEVOLVE_IMPACT_SCORES = {
    "program_database_resurfacing": 5,
    "representative_benchmark_reproduction": 4,
    "resumable_evolutionary_database": 3,
    "multi_score_feedback_quality": 2,
}


@dataclass(frozen=True)
class RoadmapGoodFirstPriorityScoreBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapGoodFirstPriorityScoreBoundaryValidation:
    ok: bool
    boundary_status: str | None
    priority_item_count: int
    rank_mismatch_count: int
    missing_evidence_count: int
    issues: list[RoadmapGoodFirstPriorityScoreBoundaryIssue]


def roadmap_good_first_priority_score_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Good First priority score model record."""

    root_path = Path(root)
    source_boundary = roadmap_good_first_followups_boundary_record(root_path)
    dependency_refresh = roadmap_good_first_dependency_refresh_boundary_record(root_path)
    stale_priority = roadmap_good_first_stale_priority_boundary_record(root_path)
    dependency_by_id = {
        record["item_id"]: record
        for record in dependency_refresh["dependency_records"]
    }
    stale_by_id = {
        record["item_id"]: record
        for record in stale_priority["detector_records"]
    }
    score_records = [
        _score_record(
            priority_record,
            dependency_by_id.get(priority_record["item_id"]),
            stale_by_id.get(priority_record["item_id"]),
        )
        for priority_record in source_boundary["priority_records"]
    ]
    ranked_records = sorted(
        score_records,
        key=lambda record: (-record["priority_score"], record["ordinal"]),
    )
    ranked_item_ids = [record["item_id"] for record in ranked_records]
    roadmap_priority_item_ids = [
        record["item_id"] for record in source_boundary["priority_records"]
    ]
    rank_mismatch_records = [
        {
            "expected_rank": index + 1,
            "roadmap_item_id": roadmap_item_ids,
            "score_model_item_id": score_model_item_id,
        }
        for index, (roadmap_item_ids, score_model_item_id) in enumerate(
            zip(roadmap_priority_item_ids, ranked_item_ids)
        )
        if roadmap_item_ids != score_model_item_id
    ]
    return {
        "schema": ROADMAP_GOOD_FIRST_PRIORITY_SCORE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_good_first_boundary_input": SOURCE_GOOD_FIRST_BOUNDARY_INPUT,
        "dependency_refresh_boundary_input": DEPENDENCY_REFRESH_BOUNDARY_INPUT,
        "stale_priority_boundary_input": STALE_PRIORITY_BOUNDARY_INPUT,
        "source_priority_item_count": source_boundary["priority_item_count"],
        "dependency_refresh_record_count": dependency_refresh["dependency_record_count"],
        "stale_priority_count": stale_priority["stale_priority_count"],
        "score_model_features": list(SCORE_FEATURE_WEIGHTS),
        "score_feature_weights": dict(SCORE_FEATURE_WEIGHTS),
        "dependency_readiness_scores": dict(DEPENDENCY_READINESS_SCORES),
        "alphaevolve_impact_scores": dict(ALPHAEVOLVE_IMPACT_SCORES),
        "priority_item_count": len(score_records),
        "score_records": score_records,
        "ranked_item_ids": ranked_item_ids,
        "roadmap_priority_item_ids": roadmap_priority_item_ids,
        "priority_order_match": not rank_mismatch_records,
        "rank_mismatch_count": len(rank_mismatch_records),
        "rank_mismatch_records": rank_mismatch_records,
        "score_model_scope": (
            "bounded deterministic priority score model using recorded "
            "dependency readiness, AlphaEvolve impact, validation gates, "
            "dependency refresh, and stale-priority detector state"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a bounded deterministic priority score "
            "model for the current ROADMAP Good First Follow-Ups, including "
            "feature weights, score inputs, ranked item ids, and rank mismatch "
            "checks. CI freshness gating and validation-artifact reporting are "
            "recorded separately. It does not claim owner review signoff."
        ),
    }


def validate_roadmap_good_first_priority_score_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapGoodFirstPriorityScoreBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_good_first_priority_score_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapGoodFirstPriorityScoreBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_good_first_priority_score_boundary_record(root)
    issues: list[RoadmapGoodFirstPriorityScoreBoundaryIssue] = []
    if data.get("schema") != ROADMAP_GOOD_FIRST_PRIORITY_SCORE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Good First priority score schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "priority score boundary must not claim CI freshness readiness"))
    for key in (
        "source_good_first_boundary_input",
        "dependency_refresh_boundary_input",
        "stale_priority_boundary_input",
        "source_priority_item_count",
        "dependency_refresh_record_count",
        "stale_priority_count",
        "score_model_features",
        "score_feature_weights",
        "dependency_readiness_scores",
        "alphaevolve_impact_scores",
        "priority_item_count",
        "score_records",
        "ranked_item_ids",
        "roadmap_priority_item_ids",
        "priority_order_match",
        "rank_mismatch_count",
        "rank_mismatch_records",
        "score_model_scope",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current Good First priority score inputs"))
    if data.get("priority_order_match") is not True:
        issues.append(_issue("priority_order_mismatch", "score-ranked item ids must match the ROADMAP Good First order"))
    if data.get("rank_mismatch_count") != 0:
        issues.append(_issue("rank_mismatch_detected", "priority score model detected ROADMAP order drift"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "bounded deterministic priority score model" not in boundary_text
        or "rank mismatch checks" not in boundary_text
        or "CI freshness gating and validation-artifact reporting are recorded separately" not in boundary_text
        or "does not claim owner review signoff" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate priority scoring from CI and signoff readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapGoodFirstPriorityScoreBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        priority_item_count=data.get("priority_item_count") if isinstance(data.get("priority_item_count"), int) else 0,
        rank_mismatch_count=data.get("rank_mismatch_count") if isinstance(data.get("rank_mismatch_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_good_first_priority_score_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_good_first_priority_score_boundary(boundary)
    lines = [
        "ROADMAP Good First priority score boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| priority_item_count | {validation.priority_item_count} |",
        f"| rank_mismatch_count | {validation.rank_mismatch_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _score_record(
    priority_record: dict[str, Any],
    dependency_record: dict[str, Any] | None,
    stale_record: dict[str, Any] | None,
) -> dict[str, Any]:
    dependency_readiness = priority_record["dependency_readiness"]
    alphaevolve_impact = priority_record["alphaevolve_impact"]
    dependency_readiness_score = DEPENDENCY_READINESS_SCORES.get(
        dependency_readiness,
        0,
    )
    alphaevolve_impact_score = ALPHAEVOLVE_IMPACT_SCORES.get(
        alphaevolve_impact,
        0,
    )
    live_dependency_refresh_score = (
        1
        if dependency_record is not None
        and dependency_record["dependency_refresh_status"] == "dependency_state_refreshed"
        else 0
    )
    stale_priority_penalty = (
        0
        if stale_record is not None
        and stale_record["priority_detector_status"] == "priority_current"
        else 1
    )
    validation_gate_count = len(priority_record["validation_gates"])
    priority_score = (
        alphaevolve_impact_score * SCORE_FEATURE_WEIGHTS["alphaevolve_impact_score"]
        + dependency_readiness_score * SCORE_FEATURE_WEIGHTS["dependency_readiness_score"]
        + live_dependency_refresh_score * SCORE_FEATURE_WEIGHTS["live_dependency_refresh_score"]
        + validation_gate_count * SCORE_FEATURE_WEIGHTS["validation_gate_count"]
        + stale_priority_penalty * SCORE_FEATURE_WEIGHTS["stale_priority_penalty"]
    )
    return {
        "item_id": priority_record["item_id"],
        "ordinal": priority_record["ordinal"],
        "dependency_readiness": dependency_readiness,
        "dependency_readiness_score": dependency_readiness_score,
        "alphaevolve_impact": alphaevolve_impact,
        "alphaevolve_impact_score": alphaevolve_impact_score,
        "live_dependency_refresh_score": live_dependency_refresh_score,
        "validation_gate_count": validation_gate_count,
        "stale_priority_penalty": stale_priority_penalty,
        "priority_score": priority_score,
        "score_status": "priority_score_recorded",
    }


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapGoodFirstPriorityScoreBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Good First priority score boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapGoodFirstPriorityScoreBoundaryIssue],
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
    issues: list[RoadmapGoodFirstPriorityScoreBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapGoodFirstPriorityScoreBoundaryIssue:
    return RoadmapGoodFirstPriorityScoreBoundaryIssue(code=code, message=message)
