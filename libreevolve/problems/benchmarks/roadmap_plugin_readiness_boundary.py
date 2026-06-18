from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_plugin_extensibility_boundary import (
    roadmap_plugin_extensibility_boundary_record,
)


ROADMAP_PLUGIN_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_plugin_readiness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_plugin_readiness_matrix_without_external_plugin_gate"
)
SOURCE_PLUGIN_BOUNDARY_INPUT = "papers/roadmap_plugin_extensibility_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "plugin_trust_boundary_matrix",
    "plugin_admission_checklist",
    "direct_constructor_value_schema_registry",
    "versioned_custom_plugin_registry",
    "artifact_lifecycle_hash_policy",
    "runtime_isolation_policy",
    "paper_scope_attribution_and_staleness",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "plugin_trust_boundary_matrix": "not_recorded_locally",
    "plugin_admission_checklist": "not_recorded_locally",
    "direct_constructor_value_schema_registry": "not_recorded_locally",
    "versioned_custom_plugin_registry": "not_recorded_locally",
    "artifact_lifecycle_hash_policy": "not_recorded_locally",
    "runtime_isolation_policy": "not_recorded_locally",
    "paper_scope_attribution_and_staleness": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "plugin_trust_boundary_matrix",
        "plugin_surface": "built-in, entry-point, direct-instance, and future custom-registry plugins",
        "current_scope": "six static plugin surfaces with trust-boundary labels",
        "missing_readiness": "matrix separating trusted in-repo code, configured entry points, live direct instances, and future custom registries",
        "sidecars": (
            "papers/roadmap_plugin_extensibility_boundary.json",
            "papers/roadmap_non_goal_drift_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "plugin trust-boundary matrix",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "runtime isolation/trust assumptions",
            },
        ),
        "validation_gate": "plugin trust-boundary matrix",
        "readiness_status": "surface_labels_without_trust_matrix",
    },
    {
        "criterion_id": "plugin_admission_checklist",
        "plugin_surface": "external plugin loading and support claims",
        "current_scope": "entry-point metadata and direct-instance policy without external admission rules",
        "missing_readiness": "checklist for admitting external plugins before support claims are allowed",
        "sidecars": (
            "papers/config_validation_boundary.json",
            "papers/validator_execution_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "plugin admission checklist",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "external plugin readiness",
            },
        ),
        "validation_gate": "external plugin admission checklist",
        "readiness_status": "no_external_plugin_admission_checklist",
    },
    {
        "criterion_id": "direct_constructor_value_schema_registry",
        "plugin_surface": "direct-instance constructor values, declared schemas, and provenance",
        "current_scope": "signature-only direct-instance policy that explicitly excludes values and arbitrary schemas",
        "missing_readiness": "registry for direct constructor value/schema evidence and allowed provenance capture",
        "sidecars": (
            "papers/documentation_claim_inventory.json",
            "papers/roadmap_operational_readiness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "direct constructor value/schema registry",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "constructor-value provenance",
            },
        ),
        "validation_gate": "direct constructor value/schema registry",
        "readiness_status": "signature_only_without_value_schema_registry",
    },
    {
        "criterion_id": "versioned_custom_plugin_registry",
        "plugin_surface": "future direct custom plugin registries and package/source identity",
        "current_scope": "entry-point distribution metadata and direct module hashes only",
        "missing_readiness": "versioned custom plugin registry with source/package identity and declared constructor policy",
        "sidecars": (
            "papers/todo_ledger_ownership_boundary.json",
            "papers/roadmap_readiness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "versioned custom plugin registry",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "future custom-registry plugins",
            },
        ),
        "validation_gate": "versioned custom plugin registry",
        "readiness_status": "not_implemented",
    },
    {
        "criterion_id": "artifact_lifecycle_hash_policy",
        "plugin_surface": "plugin artifacts, generated paper artifacts, and run bundle lifecycle",
        "current_scope": "artifact summaries and aggregate emitted-artifact hashes without plugin-owned lifecycle policy",
        "missing_readiness": "hash ownership policy for plugin artifacts across run artifacts and paper-facing artifacts",
        "sidecars": (
            "papers/artifact_index_boundary.json",
            "papers/roadmap_operational_readiness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "artifact lifecycle hash policy",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "artifact hashing",
            },
        ),
        "validation_gate": "plugin artifact lifecycle hash policy",
        "readiness_status": "artifact_summaries_without_lifecycle_policy",
    },
    {
        "criterion_id": "runtime_isolation_policy",
        "plugin_surface": "plugin hook execution, quarantine, failure policy, and runtime trust",
        "current_scope": "fatal hook policy and recorded artifact failures without configurable isolation",
        "missing_readiness": "runtime isolation policy for optional plugin hooks and external plugin failures",
        "sidecars": (
            "papers/validator_execution_boundary.json",
            "papers/documentation_truthfulness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "runtime isolation policy",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add configurable non-fatal plugin hook isolation for optional extension",
            },
        ),
        "validation_gate": "plugin runtime isolation policy",
        "readiness_status": "fatal_policy_without_external_isolation",
    },
    {
        "criterion_id": "paper_scope_attribution_and_staleness",
        "plugin_surface": "paper-inspired plugin scope, stale readiness, and cross-document overclaim prevention",
        "current_scope": "paper-inspiration labels and approximation wording without full attribution policy",
        "missing_readiness": "paper-scope attribution policy plus stale-readiness detector across README, papers, runtime metadata, and plugin docs",
        "sidecars": (
            "papers/causalevolve_boundary.json",
            "papers/deepevolve_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "paper-scope attribution policy",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "stale-readiness detector",
            },
        ),
        "validation_gate": "paper-scope attribution and stale-readiness guard",
        "readiness_status": "approximation_labels_without_policy_gate",
    },
)


@dataclass(frozen=True)
class RoadmapPluginReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapPluginReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readiness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapPluginReadinessBoundaryIssue]


def roadmap_plugin_readiness_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP plugin-readiness matrix."""

    root_path = Path(root)
    source_boundary = roadmap_plugin_extensibility_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    claim_guard = [_claim_guard_record(record) for record in records]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_PLUGIN_READINESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_plugin_boundary_input": SOURCE_PLUGIN_BOUNDARY_INPUT,
        "source_surface_count": source_boundary["surface_count"],
        "source_active_todo_ref_count": source_boundary["active_todo_ref_count"],
        "source_sidecar_ref_count": source_boundary["sidecar_ref_count"],
        "source_code_ref_count": source_boundary["code_ref_count"],
        "readiness_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "readiness_criteria": records,
        "plugin_claim_guard": claim_guard,
        "plugin_claim_guard_count": len(claim_guard),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records plugin-readiness criteria tied to the "
            "bounded plugin extensibility matrix, plus a claim guard for each "
            "plugin surface. It does not claim a plugin trust-boundary matrix, "
            "plugin admission checklist, direct constructor value/schema "
            "registry, versioned custom plugin registry, artifact lifecycle "
            "hash policy, runtime isolation policy, paper-scope attribution "
            "and staleness guard, or owner review signoff."
        ),
    }


def validate_roadmap_plugin_readiness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapPluginReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_plugin_readiness_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapPluginReadinessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_plugin_readiness_boundary_record(root)
    issues: list[RoadmapPluginReadinessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_PLUGIN_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP plugin readiness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP plugin readiness boundary must not claim external-plugin readiness"))
    for key in (
        "source_plugin_boundary_input",
        "source_surface_count",
        "source_active_todo_ref_count",
        "source_sidecar_ref_count",
        "source_code_ref_count",
        "readiness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "readiness_criteria",
        "plugin_claim_guard",
        "plugin_claim_guard_count",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP plugin-readiness inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a plugin trust-boundary matrix" not in boundary_text
        or "claim guard for each plugin surface" not in boundary_text
        or "plugin admission checklist" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness matrix from external plugin support"))
    if data.get("plugin_claim_guard_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_plugin_claim_guard_count", "plugin claim guard count changed"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapPluginReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readiness_criterion_count=data.get("readiness_criterion_count") if isinstance(data.get("readiness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_plugin_readiness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_plugin_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP plugin readiness boundary",
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
        "plugin_surface": spec["plugin_surface"],
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
        "plugin_surface": record["plugin_surface"],
        "allowed_current_claim": record["current_scope"],
        "missing_before_external_plugin_claim": record["missing_readiness"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapPluginReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP plugin readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapPluginReadinessBoundaryIssue],
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
    issues: list[RoadmapPluginReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapPluginReadinessBoundaryIssue:
    return RoadmapPluginReadinessBoundaryIssue(code=code, message=message)
