from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_good_first_ci_priority_gate_boundary import (
    roadmap_good_first_ci_priority_gate_boundary_record,
)
from libreevolve.problems.benchmarks.roadmap_good_first_followups_boundary import (
    GOOD_FIRST_FOLLOWUP_SPECS,
    roadmap_good_first_followups_boundary_record,
)


ROADMAP_GOOD_FIRST_VALIDATION_ARTIFACT_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_good_first_validation_artifact_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "good_first_validation_artifact_report_recorded_without_owner_signoff"
)
SOURCE_GOOD_FIRST_BOUNDARY_INPUT = "papers/roadmap_good_first_followups_boundary.json"
CI_PRIORITY_GATE_BOUNDARY_INPUT = "papers/roadmap_good_first_ci_priority_gate_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "source_good_first_priority_items",
    "validation_gate_records",
    "artifact_family_labels",
    "artifact_sidecar_refs",
    "active_todo_refs",
    "ci_priority_freshness_gate",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "owner_review_signoff": "not_recorded_locally",
}


ARTIFACT_SPECS = (
    {
        "item_id": "durable_query_indexes",
        "validation_gate": "durable database/query index tests",
        "artifact_family": "durable_database_query_index_tests",
        "sidecars": (
            "papers/todo_canonical_gap_boundary.json",
            "papers/implementation_evidence_map_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "run-local resurfacing indexes",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "durable query/report surfaces",
            },
        ),
    },
    {
        "item_id": "durable_query_indexes",
        "validation_gate": "run-artifact query/report sidecar",
        "artifact_family": "run_artifact_query_report_sidecar",
        "sidecars": (
            "papers/artifact_index_boundary.json",
            "papers/todo_canonical_gap_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "query/report surfaces",
            },
        ),
    },
    {
        "item_id": "durable_query_indexes",
        "validation_gate": "paper-manifest validation",
        "artifact_family": "paper_manifest_validation",
        "sidecars": (
            "papers/roadmap_good_first_ci_priority_gate_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "paper-manifest validators",
            },
        ),
    },
    {
        "item_id": "non_toy_benchmark_fixture",
        "validation_gate": "repeated-seed run reports",
        "artifact_family": "repeated_seed_run_reports",
        "sidecars": (
            "papers/benchmark_coverage_inventory.json",
            "papers/sorting_network_rediscovery_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "repeated-seed run reports",
            },
        ),
    },
    {
        "item_id": "non_toy_benchmark_fixture",
        "validation_gate": "target-hit-rate summaries",
        "artifact_family": "target_hit_rate_summaries",
        "sidecars": (
            "papers/benchmark_coverage_inventory.json",
            "papers/sorting_network_rediscovery_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "target-hit-rate summaries",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "target-hit-rate summaries",
            },
        ),
    },
    {
        "item_id": "non_toy_benchmark_fixture",
        "validation_gate": "benchmark hardening certification",
        "artifact_family": "benchmark_hardening_certification",
        "sidecars": (
            "papers/benchmark_fixture_readiness_boundary.json",
            "papers/benchmark_coverage_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "benchmark hardening",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "benchmark hardening",
            },
        ),
    },
    {
        "item_id": "workspace_resume_coverage",
        "validation_gate": "archive event replay restore tests",
        "artifact_family": "archive_event_replay_restore_tests",
        "sidecars": (
            "papers/archive_event_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Replay archive event logs",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "archive-event replay",
            },
        ),
    },
    {
        "item_id": "workspace_resume_coverage",
        "validation_gate": "pending-work resume tests",
        "artifact_family": "pending_work_resume_tests",
        "sidecars": (
            "papers/controller_pending_work_resume_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "pending-work controller resume state",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "controller pending-work resume",
            },
        ),
    },
    {
        "item_id": "workspace_resume_coverage",
        "validation_gate": "workspace artifact integrity report",
        "artifact_family": "workspace_artifact_integrity_report",
        "sidecars": (
            "papers/workspace_materialization_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "workspace artifact hashes",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "best-workspace artifact hashes",
            },
        ),
    },
    {
        "item_id": "feedback_calibration_reports",
        "validation_gate": "runtime feedback-calibration fixture",
        "artifact_family": "runtime_feedback_calibration_fixture",
        "sidecars": (
            "papers/feedback_calibration_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "feedback calibration reports",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "No runtime feedback-calibration fixture",
            },
        ),
    },
    {
        "item_id": "feedback_calibration_reports",
        "validation_gate": "grader ablation outputs",
        "artifact_family": "grader_ablation_outputs",
        "sidecars": (
            "papers/feedback_calibration_boundary.json",
            "papers/benchmark_coverage_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "ablation outputs",
            },
        ),
    },
    {
        "item_id": "feedback_calibration_reports",
        "validation_gate": "feedback-calibration artifact inventory",
        "artifact_family": "feedback_calibration_artifact_inventory",
        "sidecars": (
            "papers/feedback_calibration_boundary.json",
            "papers/artifact_index_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "feedback-calibration artifacts",
            },
        ),
    },
)


@dataclass(frozen=True)
class RoadmapGoodFirstValidationArtifactBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapGoodFirstValidationArtifactBoundaryValidation:
    ok: bool
    boundary_status: str | None
    validation_artifact_record_count: int
    stale_validation_artifact_record_count: int
    missing_evidence_count: int
    issues: list[RoadmapGoodFirstValidationArtifactBoundaryIssue]


def roadmap_good_first_validation_artifact_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the Good First expected validation-artifact freshness report."""

    root_path = Path(root)
    source_boundary = roadmap_good_first_followups_boundary_record(root_path)
    ci_gate = roadmap_good_first_ci_priority_gate_boundary_record(root_path)
    ci_gate_status = _ci_gate_status_for_validation_artifact(ci_gate)
    records = [
        _artifact_record(root_path, index + 1, spec)
        for index, spec in enumerate(ARTIFACT_SPECS)
    ]
    stale_records = [
        record
        for record in records
        if record["artifact_freshness_status"] != "artifact_freshness_anchor_recorded"
    ]
    artifact_families = sorted({record["artifact_family"] for record in records})
    return {
        "schema": ROADMAP_GOOD_FIRST_VALIDATION_ARTIFACT_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_good_first_boundary_input": SOURCE_GOOD_FIRST_BOUNDARY_INPUT,
        "source_priority_item_count": source_boundary["priority_item_count"],
        "source_validation_gate_count": sum(
            len(record["validation_gates"])
            for record in source_boundary["priority_records"]
        ),
        "ci_priority_gate_boundary_input": CI_PRIORITY_GATE_BOUNDARY_INPUT,
        "ci_priority_gate_status": ci_gate_status,
        "validation_artifact_record_count": len(records),
        "stale_validation_artifact_record_count": len(stale_records),
        "stale_validation_artifact_records": stale_records,
        "artifact_family_labels": artifact_families,
        "validation_artifact_records": records,
        "validation_artifact_report_status": (
            "validation_artifact_freshness_report_current"
            if not stale_records
            else "validation_artifact_freshness_report_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records expected validation artifacts for the four "
            "ROADMAP Good First Follow-Ups by joining each validation gate to "
            "artifact-family labels, committed sidecar refs, active TODO "
            "anchors, and the CI priority freshness gate. It does not claim "
            "that the underlying implementations are complete or owner review "
            "signoff is recorded."
        ),
    }


def validate_roadmap_good_first_validation_artifact_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapGoodFirstValidationArtifactBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_good_first_validation_artifact_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapGoodFirstValidationArtifactBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_good_first_validation_artifact_boundary_record(root)
    issues: list[RoadmapGoodFirstValidationArtifactBoundaryIssue] = []
    if data.get("schema") != ROADMAP_GOOD_FIRST_VALIDATION_ARTIFACT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported Good First validation-artifact schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "validation-artifact report must not claim owner signoff or implementation readiness"))
    for key in (
        "source_good_first_boundary_input",
        "source_priority_item_count",
        "source_validation_gate_count",
        "ci_priority_gate_boundary_input",
        "ci_priority_gate_status",
        "validation_artifact_record_count",
        "stale_validation_artifact_record_count",
        "stale_validation_artifact_records",
        "artifact_family_labels",
        "validation_artifact_records",
        "validation_artifact_report_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current validation-artifact inputs"))
    if data.get("stale_validation_artifact_record_count") != 0:
        issues.append(_issue("stale_validation_artifact_record", "validation artifact refs must have live sidecar and TODO anchors"))
    if data.get("validation_artifact_report_status") != "validation_artifact_freshness_report_current":
        issues.append(_issue("invalid_validation_artifact_report_status", "validation artifact report must be current"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "expected validation artifacts" not in boundary_text
        or "CI priority freshness gate" not in boundary_text
        or "does not claim that the underlying implementations are complete" not in boundary_text
        or "owner review signoff is recorded" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate artifact inventory from implementation and signoff readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapGoodFirstValidationArtifactBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        validation_artifact_record_count=(
            data.get("validation_artifact_record_count")
            if isinstance(data.get("validation_artifact_record_count"), int)
            else 0
        ),
        stale_validation_artifact_record_count=(
            data.get("stale_validation_artifact_record_count")
            if isinstance(data.get("stale_validation_artifact_record_count"), int)
            else 0
        ),
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_good_first_validation_artifact_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_good_first_validation_artifact_boundary(boundary)
    lines = [
        "ROADMAP Good First validation-artifact boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| validation_artifact_record_count | {validation.validation_artifact_record_count} |",
        f"| stale_validation_artifact_record_count | {validation.stale_validation_artifact_record_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _artifact_record(root: Path, ordinal: int, spec: dict[str, Any]) -> dict[str, Any]:
    item_id = spec["item_id"]
    source_spec = _source_spec(item_id)
    sidecar_refs = [_sidecar_ref(root, path) for path in spec["sidecars"]]
    todo_refs = [_active_todo_ref(root, todo) for todo in spec["active_todos"]]
    validation_gate_present = spec["validation_gate"] in source_spec["validation_gates"]
    stale_reasons: list[str] = []
    if not validation_gate_present:
        stale_reasons.append("validation_gate_missing_from_priority_map")
    if any(not ref["exists"] for ref in sidecar_refs):
        stale_reasons.append("sidecar_ref_missing")
    if any(not ref["required_phrase_present"] for ref in todo_refs):
        stale_reasons.append("active_todo_anchor_missing")
    return {
        "record_ordinal": ordinal,
        "item_id": item_id,
        "validation_gate": spec["validation_gate"],
        "validation_gate_present": validation_gate_present,
        "artifact_family": spec["artifact_family"],
        "sidecar_refs": sidecar_refs,
        "active_todo_refs": todo_refs,
        "artifact_freshness_status": (
            "artifact_freshness_anchor_recorded"
            if not stale_reasons
            else "artifact_freshness_anchor_stale_or_missing"
        ),
        "stale_reasons": stale_reasons,
    }


def _ci_gate_status_for_validation_artifact(ci_gate: dict[str, Any]) -> str:
    missing_records = ci_gate.get("missing_gate_records")
    if not isinstance(missing_records, list):
        return "good_first_priority_freshness_gate_incomplete"
    tolerated_self_missing = {
        "papers/roadmap_good_first_validation_artifact_boundary.json"
    }
    unexpected_missing = [
        record
        for record in missing_records
        if not (
            isinstance(record, dict)
            and record.get("gate_kind") == "committed_sidecar"
            and record.get("path") in tolerated_self_missing
        )
    ]
    if not unexpected_missing:
        return "good_first_priority_freshness_gate_present"
    status = ci_gate.get("ci_gate_status")
    return status if isinstance(status, str) else "good_first_priority_freshness_gate_incomplete"


def _source_spec(item_id: str) -> dict[str, Any]:
    for spec in GOOD_FIRST_FOLLOWUP_SPECS:
        if spec["item_id"] == item_id:
            return spec
    return {"validation_gates": ()}


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
) -> tuple[dict[str, Any] | None, list[RoadmapGoodFirstValidationArtifactBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "Good First validation-artifact boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapGoodFirstValidationArtifactBoundaryIssue],
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
    issues: list[RoadmapGoodFirstValidationArtifactBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapGoodFirstValidationArtifactBoundaryIssue:
    return RoadmapGoodFirstValidationArtifactBoundaryIssue(code=code, message=message)
