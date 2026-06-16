from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_OPERATIONAL_MATURITY_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_operational_maturity_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_operational_maturity_criteria_without_acceptance_threshold"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "criteria_records",
    "roadmap_section_presence",
    "current_sidecar_refs",
    "active_todo_refs",
    "risk_classification",
    "acceptance_threshold",
    "unified_run_artifact_lifecycle_inventory",
    "semantic_docs_verification",
    "signed_release_provenance",
    "ci_cross_platform_policy",
)
EXPECTED_MISSING_EVIDENCE = {
    "acceptance_threshold": "not_recorded_locally",
    "unified_run_artifact_lifecycle_inventory": "not_recorded_locally",
    "semantic_docs_verification": "not_recorded_locally",
    "signed_release_provenance": "not_recorded_locally",
    "ci_cross_platform_policy": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_ROADMAP_HEADING = "### 10. Operational maturity"


CRITERION_SPECS = (
    {
        "criterion_id": "config_validation",
        "risk_class": "provider_and_plugin_configuration",
        "roadmap_required_phrase": "Extend current config validation beyond",
        "current_sidecars": ("papers/config_validation_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "missing plugin-specific config schemas, provider/model compatibility",
            },
        ),
        "acceptance_gate": "plugin/provider config schema and live compatibility policy",
    },
    {
        "criterion_id": "strict_jsonl_diagnostics",
        "risk_class": "artifact_integrity",
        "roadmap_required_phrase": "Extend strict finite JSONL coverage and diagnostics",
        "current_sidecars": ("papers/documentation_claim_inventory.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add schema-level coverage for invalid/quarantine run streams.",
            },
        ),
        "acceptance_gate": "all accepted and quarantine streams have schema ownership",
    },
    {
        "criterion_id": "run_inspection",
        "risk_class": "observability_and_replay",
        "roadmap_required_phrase": "Improve run inspection beyond the current",
        "current_sidecars": ("papers/whole_run_source_workspace_integrity_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Add whole-run source/workspace integrity reports for run inspection.",
            },
        ),
        "acceptance_gate": "whole-run query, replay, and source/workspace inspection coverage",
    },
    {
        "criterion_id": "release_provenance",
        "risk_class": "packaging_and_distribution",
        "roadmap_required_phrase": "Extend current `pyproject.toml` metadata",
        "current_sidecars": ("papers/release_artifact_reproducibility_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add release artifact and install-from-wheel verification.",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add untracked-source hygiene to release artifact provenance.",
            },
        ),
        "acceptance_gate": "signed release provenance and index verification",
    },
    {
        "criterion_id": "ci_workflow_coverage",
        "risk_class": "automation_policy",
        "roadmap_required_phrase": "Extend the current path-scoped GitHub Actions workflow",
        "current_sidecars": ("papers/ci_workflow_coverage_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Expand GitHub Actions workflow coverage beyond path-scoped",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track CI workflow coverage separately from local validation commands.",
            },
        ),
        "acceptance_gate": "cross-platform paper/docs/release/integration CI policy",
    },
    {
        "criterion_id": "run_artifact_lifecycle",
        "risk_class": "run_bundle_lifecycle",
        "roadmap_required_phrase": "durable query views over run artifacts",
        "current_sidecars": ("papers/documentation_claim_inventory.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Bring generated `paper_artifacts/` directories under the run-artifact",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add schema-level coverage for non-JSONL run artifacts.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Paper-facing generated-artifact lifecycle evidence is still incomplete",
            },
        ),
        "acceptance_gate": "unified lifecycle inventory for runtime and paper artifacts",
    },
)


@dataclass(frozen=True)
class RoadmapOperationalMaturityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapOperationalMaturityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    criterion_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapOperationalMaturityBoundaryIssue]


def roadmap_operational_maturity_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP operational-maturity criteria map."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    records = [_criterion_record(root_path, roadmap_text, spec) for spec in CRITERION_SPECS]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_OPERATIONAL_MATURITY_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "roadmap_heading": EXPECTED_ROADMAP_HEADING,
        "roadmap_heading_present": _contains_phrase(roadmap_text, EXPECTED_ROADMAP_HEADING),
        "criterion_count": len(records),
        "active_todo_ref_count": active_todo_ref_count,
        "criteria_records": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a section-level operational-maturity "
            "criteria map for validation, packaging, observability, "
            "reproducibility, CI, release, and run-artifact lifecycle evidence. "
            "It does not claim a global acceptance threshold, unified run "
            "artifact lifecycle inventory, semantic documentation verification, "
            "signed release provenance, cross-platform CI policy, or owner "
            "review signoff."
        ),
    }


def validate_roadmap_operational_maturity_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapOperationalMaturityBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_operational_maturity_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapOperationalMaturityBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_operational_maturity_boundary_record(root)
    issues: list[RoadmapOperationalMaturityBoundaryIssue] = []
    if data.get("schema") != ROADMAP_OPERATIONAL_MATURITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP operational maturity boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP operational maturity boundary must not claim maturity readiness"))
    for key in (
        "roadmap_heading",
        "roadmap_heading_present",
        "criterion_count",
        "active_todo_ref_count",
        "criteria_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP/TODO inputs"))
    if data.get("roadmap_heading_present") is not True:
        issues.append(_issue("missing_roadmap_heading", "operational maturity heading was not found"))
    if data.get("criterion_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_criterion_count", "criterion count changed"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a global acceptance threshold" not in boundary_text
        or "unified run artifact lifecycle inventory" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded criteria from maturity readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapOperationalMaturityBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        criterion_count=data.get("criterion_count") if isinstance(data.get("criterion_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_operational_maturity_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_operational_maturity_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP operational maturity boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| criterion_count | {validation.criterion_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _criterion_record(
    root: Path,
    roadmap_text: str,
    spec: dict[str, Any],
) -> dict[str, Any]:
    todo_refs = [_todo_ref_record(root, todo_ref) for todo_ref in spec["active_todos"]]
    sidecar_refs = [
        {
            "path": path,
            "exists": (root / path).exists(),
        }
        for path in spec["current_sidecars"]
    ]
    return {
        "criterion_id": spec["criterion_id"],
        "risk_class": spec["risk_class"],
        "roadmap_required_phrase": spec["roadmap_required_phrase"],
        "roadmap_phrase_present": _contains_phrase(roadmap_text, spec["roadmap_required_phrase"]),
        "current_sidecar_refs": sidecar_refs,
        "active_todo_refs": todo_refs,
        "active_todo_ref_count": len(todo_refs),
        "acceptance_gate": spec["acceptance_gate"],
        "readiness_status": "not_operationally_mature",
    }


def _todo_ref_record(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": spec["required_phrase"],
        "required_phrase_present": _contains_phrase(text, spec["required_phrase"]),
        "active_marker_present": "- [ ]" in text,
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
) -> tuple[dict[str, Any] | None, list[RoadmapOperationalMaturityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP operational maturity boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapOperationalMaturityBoundaryIssue],
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
    issues: list[RoadmapOperationalMaturityBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapOperationalMaturityBoundaryIssue:
    return RoadmapOperationalMaturityBoundaryIssue(code=code, message=message)
