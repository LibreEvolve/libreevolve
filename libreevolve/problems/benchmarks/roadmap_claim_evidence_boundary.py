from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_CLAIM_EVIDENCE_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_claim_evidence_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_roadmap_claim_evidence_map_without_semantic_freshness_verifier"
)
CURRENT_STATE_HEADING = "## Current State"
GOOD_FIRST_HEADING = "## Good First Follow-Ups"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "roadmap_current_state_bullet_count",
    "roadmap_good_first_item_count",
    "claim_surface_records",
    "sidecar_refs",
    "active_todo_refs",
    "per_bullet_claim_ids",
    "semantic_evidence_sufficiency",
    "freshness_checks",
    "priority_freshness_gate",
    "generated_alignment_report",
)
EXPECTED_MISSING_EVIDENCE = {
    "complete_current_state_claim_inventory": "not_recorded_locally",
    "per_bullet_code_test_runtime_evidence_map": "not_recorded_locally",
    "semantic_evidence_sufficiency_verifier": "not_recorded_locally",
    "stale_current_state_detector": "not_recorded_locally",
    "cross_document_claim_freshness_report": "not_recorded_locally",
    "generated_alignment_report": "not_recorded_locally",
    "ci_semantic_claim_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CLAIM_SURFACE_SPECS = (
    {
        "surface_id": "roadmap_scope_preamble",
        "roadmap_required_phrase": "machine-verified proof ledger",
        "current_scope": "ROADMAP declares current-state bullets are maintained planning summaries",
        "missing_readiness": "semantic proof ledger for each ROADMAP implementation phrase",
        "sidecars": (
            "papers/documentation_truthfulness_boundary.json",
            "papers/documentation_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "complete machine-readable claim inventory",
            },
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "semantic claim verifier",
            },
        ),
        "validation_gate": "semantic ROADMAP claim verifier and proof ledger",
        "readiness_status": "scope_caveat_and_top_level_claim_inventory_only",
    },
    {
        "surface_id": "current_state_bullet_inventory",
        "roadmap_required_phrase": "## Current State",
        "current_scope": "parsed current-state top-level bullet count without per-bullet claim ids",
        "missing_readiness": "claim ids and evidence links for every current-state bullet and subclaim",
        "sidecars": ("papers/documentation_claim_inventory.json",),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "per-bullet code/test/runtime",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "exhaustive implementation-evidence mapping",
            },
        ),
        "validation_gate": "current-state bullet-to-evidence map with stale detection",
        "readiness_status": "top_level_claim_inventory_without_per_bullet_semantics",
    },
    {
        "surface_id": "implementation_evidence_links",
        "roadmap_required_phrase": "code, tests, runtime artifacts, paper sidecars",
        "current_scope": "selected core AlphaEvolve anchors and documentation evidence refs",
        "missing_readiness": "per-claim code/test/runtime-artifact sufficiency checks",
        "sidecars": (
            "papers/implementation_evidence_map_boundary.json",
            "papers/status_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "generated alignment reports",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "evidence-sufficiency checks",
            },
        ),
        "validation_gate": "claim-to-implementation evidence sufficiency report",
        "readiness_status": "selected_anchor_and_structural_ref_existence_only",
    },
    {
        "surface_id": "good_first_priority_claims",
        "roadmap_required_phrase": "## Good First Follow-Ups",
        "current_scope": "four parsed good-first items, bounded static priority map, dependency refresh records, stale-priority detector, priority score model, CI freshness gate, and validation-artifact report",
        "missing_readiness": "owner review signoff",
        "sidecars": (
            "papers/roadmap_good_first_followups_boundary.json",
            "papers/roadmap_good_first_dependency_refresh_boundary.json",
            "papers/roadmap_good_first_stale_priority_boundary.json",
            "papers/roadmap_good_first_priority_score_boundary.json",
            "papers/roadmap_good_first_ci_priority_gate_boundary.json",
            "papers/roadmap_good_first_validation_artifact_boundary.json",
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
        "validation_gate": "priority freshness gate tied to dependency state",
        "readiness_status": "validation_artifact_report_recorded_without_owner_signoff",
    },
    {
        "surface_id": "cross_document_claim_sync",
        "roadmap_required_phrase": "Keep README, docs, paper index",
        "current_scope": "top-level README/ROADMAP/papers claim anchors plus status ledger structural inventory",
        "missing_readiness": "cross-document semantic freshness checks for README, ROADMAP, papers, and status ledger",
        "sidecars": (
            "papers/documentation_truthfulness_boundary.json",
            "papers/documentation_claim_inventory.json",
            "papers/status_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "implementation-evidence mapping for every README claim",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "absence-sentence freshness",
            },
        ),
        "validation_gate": "cross-document semantic freshness report",
        "readiness_status": "structural_cross_document_inventory_only",
    },
    {
        "surface_id": "alignment_report_publication",
        "roadmap_required_phrase": "full AlphaEvolve-facing claim proof",
        "current_scope": "raw TODO and weighted readiness reports without semantic completion proof",
        "missing_readiness": "generated alignment report proving each ROADMAP statement is current",
        "sidecars": (
            "papers/roadmap_readiness_boundary.json",
            "papers/todo_ledger_ownership_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "generated alignment report",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "semantic documentation-claim verification",
            },
        ),
        "validation_gate": "published generated alignment report with semantic claim freshness",
        "readiness_status": "ledger_readiness_without_semantic_alignment_report",
    },
)


@dataclass(frozen=True)
class RoadmapClaimEvidenceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapClaimEvidenceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_surface_count: int
    current_state_bullet_count: int
    good_first_item_count: int
    missing_evidence_count: int
    issues: list[RoadmapClaimEvidenceBoundaryIssue]


def roadmap_claim_evidence_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP current-state and priority claim evidence map."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    current_state_section = _section_text(roadmap_text, CURRENT_STATE_HEADING)
    good_first_section = _section_text(roadmap_text, GOOD_FIRST_HEADING)
    records = [_claim_surface_record(root_path, roadmap_text, spec) for spec in CLAIM_SURFACE_SPECS]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    current_state_bullet_count = _top_level_bullet_count(current_state_section)
    good_first_item_count = _numbered_item_count(good_first_section)
    return {
        "schema": ROADMAP_CLAIM_EVIDENCE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "current_state_heading_present": _contains_phrase(roadmap_text, CURRENT_STATE_HEADING),
        "good_first_heading_present": _contains_phrase(roadmap_text, GOOD_FIRST_HEADING),
        "roadmap_current_state_bullet_count": current_state_bullet_count,
        "roadmap_good_first_item_count": good_first_item_count,
        "claim_surface_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "claim_surface_records": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a ROADMAP-specific current-state and "
            "priority claim evidence map with parsed current-state bullet and "
            "good-first item counts, linked sidecars, active TODO anchors, and "
            "validation-gate labels. It does not claim complete per-bullet "
            "claim ids, per-bullet code/test/runtime evidence maps, semantic "
            "evidence sufficiency verification, stale current-state detection, "
            "cross-document claim freshness, a generated alignment report, a "
            "CI semantic claim gate, or owner review signoff."
        ),
    }


def validate_roadmap_claim_evidence_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapClaimEvidenceBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_claim_evidence_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapClaimEvidenceBoundaryValidation(False, None, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = roadmap_claim_evidence_boundary_record(root)
    issues: list[RoadmapClaimEvidenceBoundaryIssue] = []
    if data.get("schema") != ROADMAP_CLAIM_EVIDENCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP claim evidence boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP claim evidence boundary must not claim semantic readiness"))
    for key in (
        "current_state_heading_present",
        "good_first_heading_present",
        "roadmap_current_state_bullet_count",
        "roadmap_good_first_item_count",
        "claim_surface_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "claim_surface_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP/TODO inputs"))
    if data.get("current_state_heading_present") is not True:
        issues.append(_issue("missing_current_state_heading", "ROADMAP Current State heading was not found"))
    if data.get("good_first_heading_present") is not True:
        issues.append(_issue("missing_good_first_heading", "ROADMAP Good First Follow-Ups heading was not found"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim complete per-bullet claim ids" not in boundary_text
        or "semantic evidence sufficiency verification" not in boundary_text
        or "generated alignment report" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded evidence mapping from semantic verification"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapClaimEvidenceBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        claim_surface_count=data.get("claim_surface_count") if isinstance(data.get("claim_surface_count"), int) else 0,
        current_state_bullet_count=(
            data.get("roadmap_current_state_bullet_count")
            if isinstance(data.get("roadmap_current_state_bullet_count"), int)
            else 0
        ),
        good_first_item_count=(
            data.get("roadmap_good_first_item_count")
            if isinstance(data.get("roadmap_good_first_item_count"), int)
            else 0
        ),
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_claim_evidence_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_claim_evidence_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP claim evidence boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| claim_surface_count | {validation.claim_surface_count} |",
        f"| current_state_bullet_count | {validation.current_state_bullet_count} |",
        f"| good_first_item_count | {validation.good_first_item_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _claim_surface_record(root: Path, roadmap_text: str, spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "surface_id": spec["surface_id"],
        "roadmap_required_phrase": spec["roadmap_required_phrase"],
        "roadmap_phrase_present": _contains_phrase(roadmap_text, spec["roadmap_required_phrase"]),
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "sidecar_refs": [
            {"path": path, "exists": (root / path).exists()}
            for path in spec["sidecars"]
        ],
        "active_todo_refs": [_local_ref_record(root, todo_ref) for todo_ref in spec["active_todos"]],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _local_ref_record(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": spec["required_phrase"],
        "required_phrase_present": _contains_phrase(text, spec["required_phrase"]),
        "exists": (root / path).exists(),
    }


def _section_text(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    try:
        start = next(index for index, line in enumerate(lines) if line.strip() == heading)
    except StopIteration:
        return ""
    body: list[str] = []
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        body.append(line)
    return "\n".join(body)


def _top_level_bullet_count(section: str) -> int:
    return sum(1 for line in section.splitlines() if line.startswith("- "))


def _numbered_item_count(section: str) -> int:
    return sum(1 for line in section.splitlines() if re.match(r"^\d+\.\s+", line))


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
) -> tuple[dict[str, Any] | None, list[RoadmapClaimEvidenceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP claim evidence boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapClaimEvidenceBoundaryIssue],
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
    issues: list[RoadmapClaimEvidenceBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapClaimEvidenceBoundaryIssue:
    return RoadmapClaimEvidenceBoundaryIssue(code=code, message=message)
