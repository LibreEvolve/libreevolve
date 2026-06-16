from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_non_goal_contradiction_boundary import (
    roadmap_non_goal_contradiction_boundary_record,
)


ROADMAP_NON_GOAL_DRIFT_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_non_goal_drift_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_non_goal_drift_matrix_without_full_promotion_gate"
)
SOURCE_NON_GOAL_BOUNDARY_INPUT = "papers/roadmap_non_goal_contradiction_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "runtime_metadata_scan",
    "plugin_docstring_scan",
    "full_markdown_corpus_scan",
    "ci_non_goal_promotion_gate",
    "intentional_promotion_workflow",
    "claim_surface_remediation",
    "runtime_plugin_scope_join",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "runtime_metadata_scan": "not_recorded_locally",
    "ci_non_goal_promotion_gate": "not_recorded_locally",
    "intentional_promotion_workflow": "not_recorded_locally",
    "claim_surface_remediation": "not_recorded_locally",
    "runtime_plugin_scope_join": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "runtime_metadata_scan",
        "constrained_surface": "run manifests, runtime finalization, and provider/plugin metadata",
        "current_scope": "selected ROADMAP and documentation surfaces only",
        "missing_readiness": "machine-readable scan of runtime metadata claims constrained by ROADMAP non-goals",
        "sidecars": (
            "papers/roadmap_non_goal_contradiction_boundary.json",
            "papers/status_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "runtime metadata scan",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "machine-readable evidence map",
            },
        ),
        "validation_gate": "runtime metadata contradiction scan tied to stable non-goal ids",
        "readiness_status": "documentation_surface_inventory_only",
    },
    {
        "criterion_id": "plugin_docstring_scan",
        "constrained_surface": "plugin source modules, docstrings, aliases, and paper-inspiration labels",
        "current_scope": "README, architecture, status, and ROADMAP scope wording",
        "missing_readiness": "plugin source/docstring scan proving paper-inspired plugins are not advertised as faithful implementations",
        "sidecars": (
            "papers/roadmap_plugin_extensibility_boundary.json",
            "papers/documentation_claim_inventory.json",
            "papers/roadmap_non_goal_plugin_docstring_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "plugin docstring scan",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "paper-facing classification of local plugin/retrieval/failure sections",
            },
        ),
        "validation_gate": "plugin docstring and metadata scan for faithful-implementation overclaims",
        "readiness_status": "plugin_docstring_scan_recorded_without_runtime_join",
    },
    {
        "criterion_id": "full_markdown_corpus_scan",
        "constrained_surface": "README, ROADMAP, docs, papers index, and TODO ledgers",
        "current_scope": "nine constrained documentation surfaces from the non-goal inventory",
        "missing_readiness": "exhaustive Markdown corpus scan for promoted support claims and stale non-goal wording",
        "sidecars": (
            "papers/documentation_claim_inventory.json",
            "papers/documentation_truthfulness_boundary.json",
            "papers/roadmap_non_goal_markdown_scan_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "exhaustive Markdown corpus scan",
            },
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "complete cross-document claim inventory",
            },
        ),
        "validation_gate": "whole-corpus Markdown contradiction scan with source spans",
        "readiness_status": "markdown_corpus_scan_recorded_without_runtime_join",
    },
    {
        "criterion_id": "ci_non_goal_promotion_gate",
        "constrained_surface": "CI and paper-manifest validation gates",
        "current_scope": "manifest validation of committed sidecar shape",
        "missing_readiness": "CI gate that fails when a ROADMAP non-goal is removed, completed, or promoted without evidence updates",
        "sidecars": (
            "papers/ci_workflow_coverage_boundary.json",
            "papers/roadmap_non_goal_contradiction_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "CI promotion gate",
            },
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "drift check",
            },
        ),
        "validation_gate": "CI non-goal promotion/removal gate",
        "readiness_status": "local_manifest_shape_check_only",
    },
    {
        "criterion_id": "intentional_promotion_workflow",
        "constrained_surface": "ROADMAP non-goal lifecycle and TODO evidence updates",
        "current_scope": "static current non-goal inventory",
        "missing_readiness": "workflow proving intentional promotion updates ROADMAP, README, papers, and TODO evidence",
        "sidecars": (
            "papers/todo_canonical_gap_boundary.json",
            "papers/roadmap_phase_sequence_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "intentionally promoted",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "update ROADMAP/TODO evidence",
            },
        ),
        "validation_gate": "intentional non-goal promotion workflow with evidence checklist",
        "readiness_status": "no_promotion_workflow_recorded",
    },
    {
        "criterion_id": "claim_surface_remediation",
        "constrained_surface": "contradictory claim report and TODO remediation routing",
        "current_scope": "zero exact forbidden phrase matches in selected docs",
        "missing_readiness": "remediation report that links each contradiction to an owner, TODO, and claim update",
        "sidecars": (
            "papers/todo_canonical_gap_boundary.json",
            "papers/roadmap_claim_evidence_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "contradictory support claims",
            },
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "implementation-evidence mapping for every README claim",
            },
        ),
        "validation_gate": "non-goal contradiction remediation report",
        "readiness_status": "no_claim_remediation_report",
    },
    {
        "criterion_id": "runtime_plugin_scope_join",
        "constrained_surface": "joined runtime metadata, plugin docs, paper claims, and docs claims",
        "current_scope": "independent sidecars for plugin scope, status claims, and non-goal wording",
        "missing_readiness": "joined map proving code, docs, papers, and runtime metadata agree on non-goal scope",
        "sidecars": (
            "papers/roadmap_plugin_extensibility_boundary.json",
            "papers/status_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "code/docs/paper surfaces",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "broader plugin registry gap",
            },
        ),
        "validation_gate": "runtime/plugin/docs/papers non-goal scope join",
        "readiness_status": "sidecars_are_not_joined",
    },
)


@dataclass(frozen=True)
class RoadmapNonGoalDriftBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapNonGoalDriftBoundaryValidation:
    ok: bool
    boundary_status: str | None
    criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapNonGoalDriftBoundaryIssue]


def roadmap_non_goal_drift_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP non-goal drift/promotion readiness matrix."""

    root_path = Path(root)
    non_goal_boundary = roadmap_non_goal_contradiction_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_NON_GOAL_DRIFT_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_non_goal_boundary_input": SOURCE_NON_GOAL_BOUNDARY_INPUT,
        "source_non_goal_count": non_goal_boundary["non_goal_count"],
        "source_constrained_surface_count": non_goal_boundary["constrained_surface_count"],
        "source_contradiction_count": non_goal_boundary["contradiction_count"],
        "criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "readiness_criteria": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a non-goal drift and promotion readiness "
            "matrix tied to the bounded ROADMAP non-goal contradiction "
            "inventory. The Markdown corpus and plugin docstring scans are "
            "recorded separately, but this boundary does not claim runtime "
            "metadata scanning, CI promotion enforcement, an intentional "
            "promotion workflow, or owner-reviewed remediation readiness."
        ),
    }


def validate_roadmap_non_goal_drift_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapNonGoalDriftBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_non_goal_drift_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapNonGoalDriftBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_non_goal_drift_boundary_record(root)
    issues: list[RoadmapNonGoalDriftBoundaryIssue] = []
    if data.get("schema") != ROADMAP_NON_GOAL_DRIFT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP non-goal drift boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP non-goal drift boundary must not claim promotion-gate readiness"))
    for key in (
        "source_non_goal_boundary_input",
        "source_non_goal_count",
        "source_constrained_surface_count",
        "source_contradiction_count",
        "criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "readiness_criteria",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP non-goal readiness inputs"))
    if data.get("source_contradiction_count") != 0:
        issues.append(_issue("source_contradiction_detected", "source non-goal boundary must not include active contradictions"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "Markdown corpus and plugin docstring scans are recorded separately" not in boundary_text
        or "does not claim runtime metadata scanning" not in boundary_text
        or "CI promotion enforcement" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness matrix from full drift/promotion enforcement"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapNonGoalDriftBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        criterion_count=data.get("criterion_count") if isinstance(data.get("criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_non_goal_drift_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_non_goal_drift_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP non-goal drift boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| criterion_count | {validation.criterion_count} |",
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
        "constrained_surface": spec["constrained_surface"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapNonGoalDriftBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP non-goal drift boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapNonGoalDriftBoundaryIssue],
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
    issues: list[RoadmapNonGoalDriftBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapNonGoalDriftBoundaryIssue:
    return RoadmapNonGoalDriftBoundaryIssue(code=code, message=message)
