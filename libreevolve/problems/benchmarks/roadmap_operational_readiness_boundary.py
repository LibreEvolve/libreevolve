from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_operational_maturity_boundary import (
    roadmap_operational_maturity_boundary_record,
)


ROADMAP_OPERATIONAL_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_operational_readiness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_operational_readiness_matrix_without_global_maturity_gate"
)
SOURCE_OPERATIONAL_BOUNDARY_INPUT = "papers/roadmap_operational_maturity_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "global_acceptance_threshold",
    "unified_generated_artifact_lifecycle_inventory",
    "semantic_docs_verification",
    "signed_release_provenance",
    "cross_platform_ci_policy",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "global_acceptance_threshold": "not_recorded_locally",
    "unified_generated_artifact_lifecycle_inventory": "not_recorded_locally",
    "semantic_docs_verification": "not_recorded_locally",
    "signed_release_provenance": "not_recorded_locally",
    "cross_platform_ci_policy": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "global_acceptance_threshold",
        "maturity_surface": "section-level operational criteria and global maturity decision",
        "current_scope": "six section-level criteria with risk classes and acceptance-gate labels",
        "missing_readiness": "global threshold that defines when operational maturity can be claimed",
        "sidecars": (
            "papers/roadmap_operational_maturity_boundary.json",
            "papers/roadmap_readiness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "global acceptance threshold",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "full checklist is satisfied",
            },
        ),
        "validation_gate": "global operational-maturity acceptance threshold",
        "readiness_status": "criteria_map_without_threshold",
    },
    {
        "criterion_id": "unified_generated_artifact_lifecycle_inventory",
        "maturity_surface": "runtime artifacts, generated paper artifacts, overwrite policy, and schema ownership",
        "current_scope": "run-artifact lifecycle gaps are documented in separate code and papers TODOs",
        "missing_readiness": "single lifecycle inventory for manifest, history, best workspace, evaluator artifacts, plugin artifacts, prompt tables, and paper_artifacts",
        "sidecars": (
            "papers/documentation_claim_inventory.json",
            "papers/artifact_index_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "unified generated-artifact lifecycle inventory",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Bring generated `paper_artifacts/` directories under the run-artifact",
            },
        ),
        "validation_gate": "unified generated-artifact lifecycle inventory",
        "readiness_status": "distributed_lifecycle_todos_only",
    },
    {
        "criterion_id": "semantic_docs_verification",
        "maturity_surface": "README, ROADMAP, docs, papers index, status, and completed TODO claims",
        "current_scope": "structural documentation inventories and bounded claim sidecars",
        "missing_readiness": "semantic verifier that proves operational-maturity claims match implementation evidence",
        "sidecars": (
            "papers/documentation_truthfulness_boundary.json",
            "papers/documentation_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "semantic docs verification",
            },
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "semantic claim verifier",
            },
        ),
        "validation_gate": "semantic documentation verification gate",
        "readiness_status": "structural_docs_inventory_without_semantic_verifier",
    },
    {
        "criterion_id": "signed_release_provenance",
        "maturity_surface": "release artifacts, package metadata, source hygiene, and install verification",
        "current_scope": "release reproducibility boundary and code TODOs without signed provenance",
        "missing_readiness": "signed release provenance and install-from-wheel/index verification",
        "sidecars": (
            "papers/release_artifact_reproducibility_boundary.json",
            "papers/config_validation_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "signed release provenance",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add release artifact and install-from-wheel verification.",
            },
        ),
        "validation_gate": "signed release provenance gate",
        "readiness_status": "unsigned_release_reproducibility_boundary_only",
    },
    {
        "criterion_id": "cross_platform_ci_policy",
        "maturity_surface": "GitHub Actions, local validation, integration tests, paper/docs checks, and branch policy",
        "current_scope": "path-scoped CI workflow coverage boundary plus local validation commands",
        "missing_readiness": "cross-platform CI policy covering code, docs, papers, release, integration, and local-PDF gates",
        "sidecars": (
            "papers/ci_workflow_coverage_boundary.json",
            "papers/provider_diagnostics_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "cross-platform CI policy",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track CI workflow coverage separately from local validation commands.",
            },
        ),
        "validation_gate": "cross-platform CI policy gate",
        "readiness_status": "path_scoped_ci_without_cross_platform_policy",
    },
    {
        "criterion_id": "owner_review_signoff",
        "maturity_surface": "owner-reviewed operational readiness decision and release/policy exceptions",
        "current_scope": "no owner-reviewed maturity signoff record",
        "missing_readiness": "owner signoff preventing one green release or CI boundary from being mistaken for maturity",
        "sidecars": (
            "papers/todo_ledger_ownership_boundary.json",
            "papers/roadmap_operational_maturity_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "owner signoff preventing",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "operationally mature",
            },
        ),
        "validation_gate": "owner-reviewed operational-readiness signoff",
        "readiness_status": "no_owner_review_signoff",
    },
)


@dataclass(frozen=True)
class RoadmapOperationalReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapOperationalReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readiness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapOperationalReadinessBoundaryIssue]


def roadmap_operational_readiness_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP operational-readiness maturity matrix."""

    root_path = Path(root)
    source_boundary = roadmap_operational_maturity_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    claim_guard = [_claim_guard_record(record) for record in records]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_OPERATIONAL_READINESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_operational_boundary_input": SOURCE_OPERATIONAL_BOUNDARY_INPUT,
        "source_criterion_count": source_boundary["criterion_count"],
        "source_active_todo_ref_count": source_boundary["active_todo_ref_count"],
        "readiness_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "readiness_criteria": records,
        "operational_claim_guard": claim_guard,
        "operational_claim_guard_count": len(claim_guard),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records operational-readiness criteria tied to the "
            "bounded operational-maturity criteria map, plus a claim guard for "
            "each maturity surface. It does not claim a global acceptance "
            "threshold, unified generated-artifact lifecycle inventory, "
            "semantic documentation verification, signed release provenance, "
            "cross-platform CI policy, or owner review signoff."
        ),
    }


def validate_roadmap_operational_readiness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapOperationalReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_operational_readiness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapOperationalReadinessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_operational_readiness_boundary_record(root)
    issues: list[RoadmapOperationalReadinessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_OPERATIONAL_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP operational readiness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP operational readiness boundary must not claim maturity-gate readiness"))
    for key in (
        "source_operational_boundary_input",
        "source_criterion_count",
        "source_active_todo_ref_count",
        "readiness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "readiness_criteria",
        "operational_claim_guard",
        "operational_claim_guard_count",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP operational-readiness inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a global acceptance threshold" not in boundary_text
        or "claim guard for each maturity surface" not in boundary_text
        or "cross-platform CI policy" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness matrix from implemented operational-maturity gate"))
    if data.get("operational_claim_guard_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_operational_claim_guard_count", "operational claim guard count changed"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapOperationalReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readiness_criterion_count=data.get("readiness_criterion_count") if isinstance(data.get("readiness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_operational_readiness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_operational_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP operational readiness boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| readiness_criterion_count | {validation.readiness_criterion_count} |",
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
        "maturity_surface": spec["maturity_surface"],
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "sidecar_refs": [_sidecar_ref(root, path) for path in spec["sidecars"]],
        "active_todo_refs": [
            _active_todo_ref(root, todo) for todo in spec["active_todos"]
        ],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _claim_guard_record(record: dict[str, Any]) -> dict[str, str]:
    return {
        "criterion_id": record["criterion_id"],
        "maturity_surface": record["maturity_surface"],
        "allowed_current_claim": record["current_scope"],
        "missing_before_maturity_claim": record["missing_readiness"],
        "validation_gate": record["validation_gate"],
        "readiness_status": record["readiness_status"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapOperationalReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP operational readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapOperationalReadinessBoundaryIssue],
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
    issues: list[RoadmapOperationalReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapOperationalReadinessBoundaryIssue:
    return RoadmapOperationalReadinessBoundaryIssue(code=code, message=message)
