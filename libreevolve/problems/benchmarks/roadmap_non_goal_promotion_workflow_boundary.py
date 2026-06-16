from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_NON_GOAL_PROMOTION_WORKFLOW_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_non_goal_promotion_workflow_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "intentional_promotion_workflow_recorded_without_remediation_or_signoff"
)
EXPECTED_WORKFLOW_DOC = "docs/roadmap-non-goal-promotion-workflow.md"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "workflow_doc",
    "stable_non_goal_id_update",
    "roadmap_update",
    "readme_update",
    "papers_index_update",
    "status_update",
    "todo_active_update",
    "todo_completed_update",
    "non_goal_sidecar_refresh",
    "paper_manifest_gate",
    "claim_surface_remediation",
    "runtime_plugin_scope_join",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "claim_surface_remediation": "not_recorded_locally",
    "runtime_plugin_scope_join": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_WORKFLOW_PHRASES = {
    "promotion_scope": "removed, completed, or intentionally promoted",
    "stable_non_goal_id": "stable non-goal id record",
    "same_pull_request": "same pull request",
    "not_valid_if_only_prose": "not valid if it only changes prose",
    "contradiction_routing": "Contradictory support claims must be routed",
    "manifest_gate": "py -3.12 -m libreevolve.tools.paper_manifest --root . --require-local-pdfs --json",
    "owner_signoff_boundary": "not an owner review signoff record",
}
EXPECTED_CLAIM_SURFACES = (
    "ROADMAP.md",
    "README.md",
    "papers/README.md",
    "docs/status.md",
    "docs/todo/roadmap.md",
    "docs/todo/Completed/roadmap.md",
)
EXPECTED_SIDECARS = (
    "papers/roadmap_non_goal_contradiction_boundary.json",
    "papers/roadmap_non_goal_drift_boundary.json",
    "papers/roadmap_non_goal_ci_promotion_gate_boundary.json",
    "papers/roadmap_non_goal_markdown_scan_boundary.json",
    "papers/roadmap_non_goal_plugin_docstring_boundary.json",
    "papers/roadmap_non_goal_runtime_metadata_boundary.json",
)


@dataclass(frozen=True)
class RoadmapNonGoalPromotionWorkflowBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapNonGoalPromotionWorkflowBoundaryValidation:
    ok: bool
    boundary_status: str | None
    workflow_phrase_count: int
    claim_surface_count: int
    sidecar_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapNonGoalPromotionWorkflowBoundaryIssue]


def roadmap_non_goal_promotion_workflow_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded intentional ROADMAP non-goal promotion workflow."""

    root_path = Path(root)
    workflow_path = root_path / EXPECTED_WORKFLOW_DOC
    workflow_text = _read_text(workflow_path)
    workflow_phrases = {
        name: {
            "phrase": phrase,
            "present": phrase in workflow_text,
        }
        for name, phrase in EXPECTED_WORKFLOW_PHRASES.items()
    }
    claim_surfaces = [
        {
            "path": path,
            "exists": (root_path / path).is_file(),
            "listed_in_workflow": f"`{path}`" in workflow_text,
        }
        for path in EXPECTED_CLAIM_SURFACES
    ]
    sidecar_refs = [
        {
            "path": path,
            "exists": (root_path / path).is_file(),
            "listed_in_workflow": f"`{path}`" in workflow_text,
        }
        for path in EXPECTED_SIDECARS
    ]
    return {
        "schema": ROADMAP_NON_GOAL_PROMOTION_WORKFLOW_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "workflow_doc": EXPECTED_WORKFLOW_DOC,
        "workflow_doc_exists": workflow_path.is_file(),
        "workflow_phrase_count": len(workflow_phrases),
        "workflow_phrases": workflow_phrases,
        "claim_surface_count": len(claim_surfaces),
        "claim_surfaces": claim_surfaces,
        "sidecar_ref_count": len(sidecar_refs),
        "sidecar_refs": sidecar_refs,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a written intentional ROADMAP non-goal "
            "promotion workflow with required updates for ROADMAP, README, "
            "papers, status, TODO ledgers, non-goal sidecars, and the paper "
            "manifest gate. It does not claim a contradiction-remediation "
            "report, joined runtime/plugin/docs/paper scope proof, or owner "
            "review signoff."
        ),
    }


def validate_roadmap_non_goal_promotion_workflow_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapNonGoalPromotionWorkflowBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_non_goal_promotion_workflow_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapNonGoalPromotionWorkflowBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[RoadmapNonGoalPromotionWorkflowBoundaryIssue] = []
    if data.get("schema") != ROADMAP_NON_GOAL_PROMOTION_WORKFLOW_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported promotion workflow boundary schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "promotion workflow boundary must not claim full non-goal lifecycle readiness"))
    if data.get("workflow_doc") != EXPECTED_WORKFLOW_DOC or data.get("workflow_doc_exists") is not True:
        issues.append(_issue("invalid_workflow_doc", "workflow_doc must point to the committed workflow doc"))

    phrase_count = _validate_workflow_phrases(data.get("workflow_phrases"), issues)
    surface_count = _validate_path_records(
        data.get("claim_surfaces"),
        EXPECTED_CLAIM_SURFACES,
        "claim_surfaces",
        issues,
    )
    sidecar_count = _validate_path_records(
        data.get("sidecar_refs"),
        EXPECTED_SIDECARS,
        "sidecar_refs",
        issues,
    )
    _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "written intentional ROADMAP non-goal promotion workflow" not in boundary_text
        or "non-goal sidecars" not in boundary_text
        or "paper manifest gate" not in boundary_text
        or "does not claim a contradiction-remediation report" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate promotion workflow from remediation, scope join, and signoff"))
    return RoadmapNonGoalPromotionWorkflowBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        workflow_phrase_count=phrase_count,
        claim_surface_count=surface_count,
        sidecar_ref_count=sidecar_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_non_goal_promotion_workflow_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_non_goal_promotion_workflow_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP non-goal promotion workflow boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| workflow_phrase_count | {validation.workflow_phrase_count} |",
        f"| claim_surface_count | {validation.claim_surface_count} |",
        f"| sidecar_ref_count | {validation.sidecar_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapNonGoalPromotionWorkflowBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "promotion workflow boundary must be a JSON object")]


def _validate_workflow_phrases(
    value: object,
    issues: list[RoadmapNonGoalPromotionWorkflowBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_workflow_phrases", "workflow_phrases must be an object"))
        return 0
    expected_keys = set(EXPECTED_WORKFLOW_PHRASES)
    actual_keys = set(value)
    if expected_keys - actual_keys:
        issues.append(_issue("missing_workflow_phrase", "workflow phrase records are incomplete"))
    if actual_keys - expected_keys:
        issues.append(_issue("extra_workflow_phrase", "workflow phrase records include unknown keys"))
    for name, phrase in EXPECTED_WORKFLOW_PHRASES.items():
        record = value.get(name)
        if (
            not isinstance(record, dict)
            or record.get("phrase") != phrase
            or record.get("present") is not True
        ):
            issues.append(_issue(f"invalid_workflow_phrase_{name}", f"workflow phrase {name} must be present"))
    return len(actual_keys)


def _validate_path_records(
    value: object,
    expected_paths: tuple[str, ...],
    field: str,
    issues: list[RoadmapNonGoalPromotionWorkflowBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue(f"invalid_{field}", f"{field} must be a list"))
        return 0
    records = {item.get("path"): item for item in value if isinstance(item, dict)}
    expected = set(expected_paths)
    actual = set(path for path in records if isinstance(path, str))
    if expected - actual:
        issues.append(_issue(f"missing_{field}", f"{field} lacks expected paths"))
    if actual - expected:
        issues.append(_issue(f"extra_{field}", f"{field} includes unknown paths"))
    for path in expected_paths:
        record = records.get(path, {})
        if record.get("exists") is not True or record.get("listed_in_workflow") is not True:
            issues.append(_issue(f"invalid_{field}_path", f"{path} must exist and be listed in the workflow"))
    if len(records) != len(value):
        issues.append(_issue(f"invalid_{field}_record", f"{field} records must be objects"))
    return len(actual)


def _validate_required_fields(
    value: object,
    issues: list[RoadmapNonGoalPromotionWorkflowBoundaryIssue],
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
    issues: list[RoadmapNonGoalPromotionWorkflowBoundaryIssue],
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


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _issue(code: str, message: str) -> RoadmapNonGoalPromotionWorkflowBoundaryIssue:
    return RoadmapNonGoalPromotionWorkflowBoundaryIssue(code, message)
