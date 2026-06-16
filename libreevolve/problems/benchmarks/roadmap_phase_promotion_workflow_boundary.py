from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_PHASE_PROMOTION_WORKFLOW_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_phase_promotion_workflow_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "phase_promotion_demotion_workflow_recorded_without_ci_or_signoff"
)
EXPECTED_WORKFLOW_DOC = "docs/roadmap-phase-promotion-workflow.md"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "workflow_doc",
    "stable_phase_section_id",
    "phase_change_scope",
    "roadmap_update",
    "readme_update",
    "papers_index_update",
    "status_update",
    "todo_active_update",
    "todo_completed_update",
    "phase_dependency_graph_refresh",
    "stale_phase_record_resolution",
    "phase_sidecar_refresh",
    "paper_manifest_gate",
    "ci_phase_freshness_gate",
    "evidence_status_refresh",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "ci_phase_freshness_gate": "not_recorded_locally",
    "evidence_status_refresh": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_WORKFLOW_PHRASES = {
    "phase_change_scope": "promoted, demoted",
    "stable_phase_section_id": "stable ROADMAP phase section id",
    "same_pull_request": "same pull request",
    "dependency_graph_refresh": "phase dependency graph",
    "stale_phase_records": "stale phase records",
    "not_valid_if_only_prose": "not valid if it only changes prose",
    "unresolved_evidence_routing": "active TODO ledger",
    "manifest_gate": "py -3.12 -m libreevolve.tools.paper_manifest --root . --require-local-pdfs --json",
    "ci_refresh_signoff_boundary": "not a CI phase freshness gate",
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
    "papers/roadmap_phase_sequence_boundary.json",
    "papers/roadmap_phase_dependency_graph_boundary.json",
    "papers/roadmap_phase_staleness_boundary.json",
    "papers/roadmap_phase_freshness_boundary.json",
    "papers/roadmap_claim_evidence_boundary.json",
    "papers/documentation_claim_inventory.json",
    "papers/status_claim_inventory.json",
)


@dataclass(frozen=True)
class RoadmapPhasePromotionWorkflowBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapPhasePromotionWorkflowBoundaryValidation:
    ok: bool
    boundary_status: str | None
    workflow_phrase_count: int
    claim_surface_count: int
    sidecar_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapPhasePromotionWorkflowBoundaryIssue]


def roadmap_phase_promotion_workflow_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP phase promotion/demotion workflow."""

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
        "schema": ROADMAP_PHASE_PROMOTION_WORKFLOW_BOUNDARY_SCHEMA,
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
            "This boundary records a written ROADMAP phase promotion/demotion "
            "workflow with required updates for ROADMAP, README, papers, "
            "status, TODO ledgers, phase sidecars, dependency graph refresh, "
            "stale phase record resolution, and the paper manifest gate. It "
            "does not claim a CI phase freshness gate, evidence-status "
            "refresh report, or owner review signoff."
        ),
    }


def validate_roadmap_phase_promotion_workflow_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapPhasePromotionWorkflowBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_phase_promotion_workflow_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapPhasePromotionWorkflowBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[RoadmapPhasePromotionWorkflowBoundaryIssue] = []
    if data.get("schema") != ROADMAP_PHASE_PROMOTION_WORKFLOW_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported phase promotion workflow boundary schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "phase promotion workflow must not claim CI freshness, evidence refresh, or signoff readiness"))
    if data.get("workflow_doc") != EXPECTED_WORKFLOW_DOC or data.get("workflow_doc_exists") is not True:
        issues.append(_issue("invalid_workflow_doc", "workflow_doc must point to the committed phase promotion workflow doc"))
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
        or "written ROADMAP phase promotion/demotion workflow" not in boundary_text
        or "dependency graph refresh" not in boundary_text
        or "stale phase record resolution" not in boundary_text
        or "paper manifest gate" not in boundary_text
        or "does not claim a CI phase freshness gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate phase workflow from CI, refresh, and signoff"))
    return RoadmapPhasePromotionWorkflowBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        workflow_phrase_count=phrase_count,
        claim_surface_count=surface_count,
        sidecar_ref_count=sidecar_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_phase_promotion_workflow_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_phase_promotion_workflow_boundary(boundary)
    lines = [
        "ROADMAP phase promotion workflow boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
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
) -> tuple[dict[str, Any] | None, list[RoadmapPhasePromotionWorkflowBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "phase promotion workflow boundary must be a JSON object")]


def _validate_workflow_phrases(
    value: object,
    issues: list[RoadmapPhasePromotionWorkflowBoundaryIssue],
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
    issues: list[RoadmapPhasePromotionWorkflowBoundaryIssue],
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
    issues: list[RoadmapPhasePromotionWorkflowBoundaryIssue],
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
    issues: list[RoadmapPhasePromotionWorkflowBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapPhasePromotionWorkflowBoundaryIssue:
    return RoadmapPhasePromotionWorkflowBoundaryIssue(code, message)
