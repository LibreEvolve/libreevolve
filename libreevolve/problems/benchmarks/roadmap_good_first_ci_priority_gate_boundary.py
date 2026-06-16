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
from libreevolve.problems.benchmarks.roadmap_good_first_priority_score_boundary import (
    roadmap_good_first_priority_score_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_good_first_stale_priority_boundary import (
    roadmap_good_first_stale_priority_boundary_record,
)


ROADMAP_GOOD_FIRST_CI_PRIORITY_GATE_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_good_first_ci_priority_gate_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "good_first_ci_priority_freshness_gate_recorded_without_artifact_signoff"
)
WORKFLOW_PATH = ".github/workflows/tests.yml"
PAPER_MANIFEST_PATH = "libreevolve/tools/paper_manifest.py"
REQUIRED_SIDECARS = (
    "papers/roadmap_good_first_followups_boundary.json",
    "papers/roadmap_good_first_dependency_refresh_boundary.json",
    "papers/roadmap_good_first_stale_priority_boundary.json",
    "papers/roadmap_good_first_priority_score_boundary.json",
    "papers/roadmap_good_first_freshness_boundary.json",
)
REQUIRED_MANIFEST_MARKERS = (
    "_validate_roadmap_good_first_followups_boundary",
    "_validate_roadmap_good_first_dependency_refresh_boundary",
    "_validate_roadmap_good_first_stale_priority_boundary",
    "_validate_roadmap_good_first_priority_score_boundary",
    "_validate_roadmap_good_first_freshness_boundary",
)
REQUIRED_WORKFLOW_MARKERS = (
    "python -m libreevolve.tools.paper_manifest --root .",
    "test_*boundary.py",
)
EXPECTED_FRESHNESS_CRITERION_COUNT = 6
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_good_first_priority_items",
    "dependency_refresh_records",
    "stale_priority_detector",
    "priority_score_model",
    "freshness_matrix",
    "paper_manifest_gate",
    "boundary_test_workflow_gate",
    "validation_artifact_refresh",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "validation_artifact_refresh": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class RoadmapGoodFirstCiPriorityGateBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapGoodFirstCiPriorityGateBoundaryValidation:
    ok: bool
    boundary_status: str | None
    gate_record_count: int
    missing_gate_record_count: int
    missing_evidence_count: int
    issues: list[RoadmapGoodFirstCiPriorityGateBoundaryIssue]


def roadmap_good_first_ci_priority_gate_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded Good First CI priority freshness gate record."""

    root_path = Path(root)
    followups = roadmap_good_first_followups_boundary_record(root_path)
    dependency = roadmap_good_first_dependency_refresh_boundary_record(root_path)
    stale = roadmap_good_first_stale_priority_boundary_record(root_path)
    score = roadmap_good_first_priority_score_boundary_record(root_path)
    manifest_text = _read_text(root_path / PAPER_MANIFEST_PATH)
    workflow_text = _read_text(root_path / WORKFLOW_PATH)
    sidecar_records = [_sidecar_record(root_path, path) for path in REQUIRED_SIDECARS]
    manifest_records = [
        _marker_record("paper_manifest_gate", PAPER_MANIFEST_PATH, manifest_text, marker)
        for marker in REQUIRED_MANIFEST_MARKERS
    ]
    workflow_records = [
        _marker_record("boundary_test_workflow_gate", WORKFLOW_PATH, workflow_text, marker)
        for marker in REQUIRED_WORKFLOW_MARKERS
    ]
    gate_records = sidecar_records + manifest_records + workflow_records
    missing_gate_records = [
        record
        for record in gate_records
        if record["gate_status"] != "gate_marker_present"
    ]
    return {
        "schema": ROADMAP_GOOD_FIRST_CI_PRIORITY_GATE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "workflow_path": WORKFLOW_PATH,
        "paper_manifest_path": PAPER_MANIFEST_PATH,
        "source_priority_item_count": followups["priority_item_count"],
        "dependency_refresh_record_count": dependency["dependency_record_count"],
        "stale_priority_count": stale["stale_priority_count"],
        "priority_score_order_match": score["priority_order_match"],
        "priority_score_rank_mismatch_count": score["rank_mismatch_count"],
        "freshness_criterion_count": EXPECTED_FRESHNESS_CRITERION_COUNT,
        "gate_record_count": len(gate_records),
        "missing_gate_record_count": len(missing_gate_records),
        "missing_gate_records": missing_gate_records,
        "gate_records": gate_records,
        "ci_gate_status": (
            "good_first_priority_freshness_gate_present"
            if not missing_gate_records
            else "good_first_priority_freshness_gate_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a bounded Good First priority freshness gate "
            "through committed sidecars, paper-manifest validation, and the "
            "existing docs/paper/boundary GitHub Actions workflow. It does not "
            "claim per-item validation-artifact freshness or owner review "
            "signoff."
        ),
    }


def validate_roadmap_good_first_ci_priority_gate_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapGoodFirstCiPriorityGateBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_good_first_ci_priority_gate_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapGoodFirstCiPriorityGateBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_good_first_ci_priority_gate_boundary_record(root)
    issues: list[RoadmapGoodFirstCiPriorityGateBoundaryIssue] = []
    if data.get("schema") != ROADMAP_GOOD_FIRST_CI_PRIORITY_GATE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Good First CI priority gate schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "CI priority gate must not claim artifact or signoff readiness"))
    for key in (
        "workflow_path",
        "paper_manifest_path",
        "source_priority_item_count",
        "dependency_refresh_record_count",
        "stale_priority_count",
        "priority_score_order_match",
        "priority_score_rank_mismatch_count",
        "freshness_criterion_count",
        "gate_record_count",
        "missing_gate_record_count",
        "missing_gate_records",
        "gate_records",
        "ci_gate_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current Good First CI gate inputs"))
    if data.get("missing_gate_record_count") != 0:
        issues.append(_issue("missing_gate_record", "Good First priority freshness gate has missing sidecar, manifest, or workflow markers"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "paper-manifest validation" not in boundary_text
        or "GitHub Actions workflow" not in boundary_text
        or "does not claim per-item validation-artifact freshness" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate CI priority gate from artifact freshness and signoff"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapGoodFirstCiPriorityGateBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        gate_record_count=data.get("gate_record_count") if isinstance(data.get("gate_record_count"), int) else 0,
        missing_gate_record_count=data.get("missing_gate_record_count") if isinstance(data.get("missing_gate_record_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_good_first_ci_priority_gate_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_good_first_ci_priority_gate_boundary(boundary)
    lines = [
        "ROADMAP Good First CI priority gate boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| gate_record_count | {validation.gate_record_count} |",
        f"| missing_gate_record_count | {validation.missing_gate_record_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _sidecar_record(root: Path, path: str) -> dict[str, Any]:
    return {
        "gate_kind": "committed_sidecar",
        "path": path,
        "required_marker": path,
        "gate_status": "gate_marker_present" if (root / path).exists() else "gate_marker_missing",
    }


def _marker_record(kind: str, path: str, text: str, marker: str) -> dict[str, Any]:
    return {
        "gate_kind": kind,
        "path": path,
        "required_marker": marker,
        "gate_status": "gate_marker_present" if marker in text else "gate_marker_missing",
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapGoodFirstCiPriorityGateBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Good First CI priority gate boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapGoodFirstCiPriorityGateBoundaryIssue],
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
    issues: list[RoadmapGoodFirstCiPriorityGateBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapGoodFirstCiPriorityGateBoundaryIssue:
    return RoadmapGoodFirstCiPriorityGateBoundaryIssue(code=code, message=message)
