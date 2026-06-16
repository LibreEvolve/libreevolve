from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_PLUGIN_EXTENSIBILITY_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_plugin_extensibility_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_plugin_extensibility_matrix_without_external_plugin_readiness"
)
EXPECTED_ROADMAP_HEADING = "### 8. Plugin extensibility"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "surface_records",
    "roadmap_section_presence",
    "plugin_trust_boundary_matrix",
    "plugin_admission_checklist",
    "configuration_schema_policy",
    "package_source_identity_policy",
    "constructor_provenance_policy",
    "artifact_lifecycle_hash_policy",
    "runtime_isolation_policy",
    "paper_scope_attribution_policy",
    "stale_readiness_detector",
)
EXPECTED_MISSING_EVIDENCE = {
    "plugin_trust_boundary_matrix": "not_recorded_locally",
    "plugin_admission_checklist": "not_recorded_locally",
    "direct_constructor_value_schema_registry": "not_recorded_locally",
    "versioned_custom_plugin_registry": "not_recorded_locally",
    "artifact_lifecycle_hash_policy": "not_recorded_locally",
    "runtime_isolation_policy": "not_recorded_locally",
    "paper_scope_attribution_policy": "not_recorded_locally",
    "stale_readiness_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


SURFACE_SPECS = (
    {
        "surface_id": "builtin_plugin_catalog",
        "plugin_surface": "built_in",
        "configuration_shape": "validated scalar and path constructor options",
        "package_source_identity": "in-repo module identity and source-tree provenance",
        "constructor_provenance": "validated built-in parameters recorded for known plugin classes",
        "artifact_hashing": "plugin-provided summaries only; no unified lifecycle hash policy",
        "runtime_trust_boundary": "trusted in-repo plugin code",
        "paper_scope_attribution": "paper inspiration label scoped to approximation metadata",
        "roadmap_required_phrase": "built-in scalar/path options",
        "current_code_refs": (
            {
                "path": "libreevolve/plugins/registry.py",
                "required_phrase": "paper_inspiration=\"CausalEvolve\"",
            },
            {
                "path": "libreevolve/plugins/registry.py",
                "required_phrase": "option_schema={\"history_limit\": _POSITIVE_INT}",
            },
        ),
        "current_sidecars": (
            "papers/causalevolve_boundary.json",
            "papers/deepevolve_boundary.json",
            "papers/thetaevolve_boundary.json",
            "papers/improvevolve_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Keep built-in paper-inspired plugin behavior scoped to approximation",
            },
        ),
        "validation_gate": "built-in option schemas and approximation metadata stay explicit",
        "readiness_status": "trusted_builtin_approximation_only",
    },
    {
        "surface_id": "entry_point_plugins",
        "plugin_surface": "entry_point",
        "configuration_shape": "manifest-safe constructor options and declared constructor schemas",
        "package_source_identity": "entry-point distribution name/version plus RECORD/WHEEL metadata when available",
        "constructor_provenance": "declared option schema validation before construction",
        "artifact_hashing": "manifest-safe emitted artifact summaries without lifecycle ownership matrix",
        "runtime_trust_boundary": "configured package entry point loaded in the local process",
        "paper_scope_attribution": "configured entry-point paper-inspiration label",
        "roadmap_required_phrase": "entry-point distribution metadata",
        "current_code_refs": (
            {
                "path": "libreevolve/plugins/registry.py",
                "required_phrase": "entry_point_distribution_name_version_hash_v1",
            },
            {
                "path": "libreevolve/plugins/registry.py",
                "required_phrase": "_entry_point_constructor_option_schema",
            },
        ),
        "current_sidecars": (
            "papers/documentation_claim_inventory.json",
            "papers/artifact_index_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "richer package policy, direct custom constructor schemas",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "richer custom package policy beyond entry-point distribution records",
            },
        ),
        "validation_gate": "entry-point constructor schemas and distribution metadata remain bounded",
        "readiness_status": "entry_point_metadata_available_without_external_plugin_readiness",
    },
    {
        "surface_id": "direct_instance_plugins",
        "plugin_surface": "direct_instance",
        "configuration_shape": "constructor signature shape only",
        "package_source_identity": "module, qualname, file hash, and exposed version metadata",
        "constructor_provenance": "constructor values and arbitrary instance state explicitly excluded",
        "artifact_hashing": "plugin artifacts summarized when hooks return safe metadata",
        "runtime_trust_boundary": "trusted live object supplied by caller",
        "paper_scope_attribution": "not safely attributable without a declaration path",
        "roadmap_required_phrase": "direct-instance signature-only policy",
        "current_code_refs": (
            {
                "path": "libreevolve/core/loop.py",
                "required_phrase": "libreevolve.direct_plugin_policy.v1",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_phrase": "direct_instance_constructor_values",
            },
        ),
        "current_sidecars": (
            "papers/documentation_claim_inventory.json",
            "papers/roadmap_readiness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Extend direct custom plugin provenance beyond signature-only records.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Add remaining full-run replay, lineage, provider, and custom-plugin",
            },
        ),
        "validation_gate": "direct-plugin policy keeps constructor values and schemas false until declared",
        "readiness_status": "direct_instance_signature_only",
    },
    {
        "surface_id": "future_custom_registry",
        "plugin_surface": "custom_registry",
        "configuration_shape": "not implemented; needs versioned declaration path",
        "package_source_identity": "not implemented beyond entry-point distributions and direct module hashes",
        "constructor_provenance": "not implemented for arbitrary custom constructor values or schemas",
        "artifact_hashing": "not implemented as registry-owned lifecycle hashes",
        "runtime_trust_boundary": "not implemented as an external plugin admission policy",
        "paper_scope_attribution": "not implemented as versioned custom registry metadata",
        "roadmap_required_phrase": "versioned custom registries",
        "current_code_refs": (
            {
                "path": "libreevolve/core/loop.py",
                "required_phrase": "direct_custom_plugin_registry",
            },
        ),
        "current_sidecars": (
            "papers/todo_ledger_ownership_boundary.json",
            "papers/documentation_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "add a versioned direct custom plugin registry or",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "future custom-registry plugins",
            },
        ),
        "validation_gate": "versioned custom registry and admission checklist exist before external support claims",
        "readiness_status": "not_implemented",
    },
    {
        "surface_id": "plugin_hook_isolation",
        "plugin_surface": "runtime_hooks",
        "configuration_shape": "fatal hook policy only for current core hook execution",
        "package_source_identity": "uses loaded plugin identity records",
        "constructor_provenance": "inherits loaded spec provenance",
        "artifact_hashing": "optional artifact hook failures are recorded but not isolated by policy",
        "runtime_trust_boundary": "plugin failures abort rather than quarantine by default",
        "paper_scope_attribution": "no hook-failure isolation report proving optional extension behavior",
        "roadmap_required_phrase": "current prompt-context/configuration/artifact records",
        "current_code_refs": (
            {
                "path": "libreevolve/core/loop.py",
                "required_phrase": "fatal_run_abort",
            },
            {
                "path": "libreevolve/core/loop.py",
                "required_phrase": "plugin_artifact_failures",
            },
        ),
        "current_sidecars": (
            "papers/documentation_claim_inventory.json",
            "papers/artifact_index_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add configurable non-fatal plugin hook isolation for optional extension",
            },
        ),
        "validation_gate": "per-hook failure policy and quarantine records exist before optional-plugin robustness claims",
        "readiness_status": "fatal_policy_visible_without_nonfatal_isolation",
    },
    {
        "surface_id": "plugin_artifact_lifecycle",
        "plugin_surface": "generated_artifacts",
        "configuration_shape": "plugin artifact summaries can be emitted by hooks",
        "package_source_identity": "artifact summaries do not establish package ownership by themselves",
        "constructor_provenance": "artifact records inherit loaded spec context when present",
        "artifact_hashing": "aggregate emitted-artifact hashes exist without unified paper/plugin lifecycle inventory",
        "runtime_trust_boundary": "artifact summaries are local run metadata, not external plugin certification",
        "paper_scope_attribution": "paper-facing artifact lifecycle remains incomplete",
        "roadmap_required_phrase": "stronger artifact lifecycle hashes",
        "current_code_refs": (
            {
                "path": "libreevolve/core/loop.py",
                "required_phrase": "runtime[\"plugin_artifacts\"]",
            },
            {
                "path": "libreevolve/plugins/base.py",
                "required_phrase": "run_artifacts_metadata",
            },
        ),
        "current_sidecars": (
            "papers/artifact_index_boundary.json",
            "papers/documentation_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Paper-facing generated-artifact lifecycle evidence is still incomplete",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "artifact hashing",
            },
        ),
        "validation_gate": "unified lifecycle inventory and artifact hash ownership exist",
        "readiness_status": "summary_hashes_without_lifecycle_policy",
    },
)


@dataclass(frozen=True)
class RoadmapPluginExtensibilityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapPluginExtensibilityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    surface_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapPluginExtensibilityBoundaryIssue]


def roadmap_plugin_extensibility_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP plugin-extensibility readiness matrix."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    records = [_surface_record(root_path, roadmap_text, spec) for spec in SURFACE_SPECS]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["current_sidecar_refs"]) for record in records)
    code_ref_count = sum(len(record["current_code_refs"]) for record in records)
    return {
        "schema": ROADMAP_PLUGIN_EXTENSIBILITY_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "roadmap_heading": EXPECTED_ROADMAP_HEADING,
        "roadmap_heading_present": _contains_phrase(roadmap_text, EXPECTED_ROADMAP_HEADING),
        "surface_count": len(records),
        "active_todo_ref_count": active_todo_ref_count,
        "sidecar_ref_count": sidecar_ref_count,
        "code_ref_count": code_ref_count,
        "surface_records": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a ROADMAP-level plugin-extensibility matrix "
            "for built-in, entry-point, direct-instance, future custom-registry, "
            "hook-isolation, and plugin-artifact lifecycle surfaces. It does "
            "not claim a plugin trust-boundary matrix, plugin admission "
            "checklist, direct constructor value/schema registry, versioned "
            "custom registry, artifact lifecycle hash policy, runtime isolation "
            "policy, paper-scope attribution policy, stale-readiness detector, "
            "or owner review signoff."
        ),
    }


def validate_roadmap_plugin_extensibility_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapPluginExtensibilityBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_plugin_extensibility_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapPluginExtensibilityBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_plugin_extensibility_boundary_record(root)
    issues: list[RoadmapPluginExtensibilityBoundaryIssue] = []
    if data.get("schema") != ROADMAP_PLUGIN_EXTENSIBILITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP plugin extensibility boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP plugin extensibility boundary must not claim external plugin readiness"))
    for key in (
        "roadmap_heading",
        "roadmap_heading_present",
        "surface_count",
        "active_todo_ref_count",
        "sidecar_ref_count",
        "code_ref_count",
        "surface_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP/TODO/code inputs"))
    if data.get("roadmap_heading_present") is not True:
        issues.append(_issue("missing_roadmap_heading", "plugin extensibility heading was not found"))
    if data.get("surface_count") != len(SURFACE_SPECS):
        issues.append(_issue("invalid_surface_count", "plugin surface count changed"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a plugin trust-boundary matrix" not in boundary_text
        or "direct constructor value/schema registry" not in boundary_text
        or "runtime isolation policy" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded matrix from external plugin readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapPluginExtensibilityBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        surface_count=data.get("surface_count") if isinstance(data.get("surface_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_plugin_extensibility_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_plugin_extensibility_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP plugin extensibility boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| surface_count | {validation.surface_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _surface_record(root: Path, roadmap_text: str, spec: dict[str, Any]) -> dict[str, Any]:
    code_refs = [_local_ref_record(root, ref) for ref in spec["current_code_refs"]]
    todo_refs = [_local_ref_record(root, ref) for ref in spec["active_todos"]]
    sidecar_refs = [{"path": path, "exists": (root / path).exists()} for path in spec["current_sidecars"]]
    return {
        "surface_id": spec["surface_id"],
        "plugin_surface": spec["plugin_surface"],
        "configuration_shape": spec["configuration_shape"],
        "package_source_identity": spec["package_source_identity"],
        "constructor_provenance": spec["constructor_provenance"],
        "artifact_hashing": spec["artifact_hashing"],
        "runtime_trust_boundary": spec["runtime_trust_boundary"],
        "paper_scope_attribution": spec["paper_scope_attribution"],
        "roadmap_required_phrase": spec["roadmap_required_phrase"],
        "roadmap_phrase_present": _contains_phrase(roadmap_text, spec["roadmap_required_phrase"]),
        "current_code_refs": code_refs,
        "current_sidecar_refs": sidecar_refs,
        "active_todo_refs": todo_refs,
        "active_todo_ref_count": len(todo_refs),
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
) -> tuple[dict[str, Any] | None, list[RoadmapPluginExtensibilityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP plugin extensibility boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapPluginExtensibilityBoundaryIssue],
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
    issues: list[RoadmapPluginExtensibilityBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapPluginExtensibilityBoundaryIssue:
    return RoadmapPluginExtensibilityBoundaryIssue(code=code, message=message)
