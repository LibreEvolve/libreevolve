from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.plugins.registry import builtin_plugin_registry
from libreevolve.problems.benchmarks.roadmap_non_goal_contradiction_boundary import (
    roadmap_non_goal_contradiction_boundary_record,
)


ROADMAP_NON_GOAL_RUNTIME_METADATA_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_non_goal_runtime_metadata_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "runtime_metadata_scan_without_ci_or_promotion_gate"
)
SOURCE_NON_GOAL_BOUNDARY_INPUT = "papers/roadmap_non_goal_contradiction_boundary.json"
FORBIDDEN_RUNTIME_SUPPORT_CLAIM_PHRASES = (
    "requires a service database",
    "service database is required",
    "arbitrary-language runners are implemented",
    "arbitrary-language/build runners are implemented",
    "arbitrary-language/codebase parity is implemented",
    "build-system runners are implemented",
    "supports arbitrary-language runners",
    "paper-inspired plugins are faithful implementations",
    "built-in paper-inspired plugins faithfully implement",
    "plugins faithfully implement the papers",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stable_non_goal_ids",
    "runtime_metadata_source_inventory",
    "startup_manifest_config_scan",
    "candidate_language_policy_scan",
    "runtime_plugin_state_scan",
    "runtime_plugin_artifacts_scan",
    "builtin_plugin_registry_metadata_scan",
    "forbidden_support_claim_phrase_scan",
    "ci_non_goal_promotion_gate",
    "intentional_promotion_workflow",
    "claim_surface_remediation",
    "runtime_plugin_scope_join",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "ci_non_goal_promotion_gate": "not_recorded_locally",
    "intentional_promotion_workflow": "not_recorded_locally",
    "claim_surface_remediation": "not_recorded_locally",
    "runtime_plugin_scope_join": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


RUNTIME_SURFACE_SPECS = (
    {
        "surface_id": "startup_manifest_config_plugins",
        "path": "libreevolve/core/database.py",
        "runtime_metadata_paths": (
            "config.plugins",
            "config.candidate_language_runners",
            "config.candidate_build_systems",
            "policies.candidate_language",
        ),
        "required_safe_phrases": (
            '"plugins": config.plugins',
            '"candidate_language_runners": list(config.candidate_language_runners)',
            '"candidate_build_systems": list(config.candidate_build_systems)',
            '"arbitrary_language_runners": "unsupported"',
            '"build_system_runners": "unsupported"',
            '"declaration_scope": "manifest_metadata_only_not_executed"',
            '"language_runner_ready": False',
        ),
    },
    {
        "surface_id": "runtime_plugin_state",
        "path": "libreevolve/core/loop.py",
        "runtime_metadata_paths": (
            "runtime.plugin_state",
            "runtime.plugin_state.loaded_specs",
            "runtime.plugin_state.core_resolves_config_plugins",
        ),
        "required_safe_phrases": (
            'runtime["plugin_state"] = _runtime_plugin_state',
            '"loaded_specs": loaded_specs',
            '"paper_scope_policy": paper_scope_policy',
            '"core_resolves_config_plugins": core_resolves_config_plugins',
        ),
    },
    {
        "surface_id": "runtime_plugin_artifacts",
        "path": "libreevolve/core/loop.py",
        "runtime_metadata_paths": (
            "runtime.plugin_artifacts",
            "runtime.plugin_artifact_failures",
            "plugin.run_artifacts_metadata",
        ),
        "required_safe_phrases": (
            'runtime["plugin_artifacts"] = plugin_artifacts',
            'runtime["plugin_artifact_failures"] = plugin_artifact_failures',
            '"hook": "run_artifacts_metadata"',
            '"policy": "recorded_during_abort_finalization"',
        ),
    },
    {
        "surface_id": "builtin_plugin_registry",
        "path": "libreevolve/plugins/registry.py",
        "runtime_metadata_paths": (
            "builtin_plugin_registry.*.paper_inspiration",
            "validate_plugin_spec.paper_inspiration",
            "entry_point.paper_inspiration",
        ),
        "required_safe_phrases": (
            "paper_inspiration: str",
            '"paper_inspiration": definition.paper_inspiration',
            '"paper_inspiration": entry_point["paper_inspiration"]',
            '"external_plugin_entry_point"',
        ),
    },
)


@dataclass(frozen=True)
class RoadmapNonGoalRuntimeMetadataBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapNonGoalRuntimeMetadataBoundaryValidation:
    ok: bool
    boundary_status: str | None
    runtime_surface_count: int
    source_missing_count: int
    safe_phrase_missing_count: int
    contradiction_count: int
    missing_evidence_count: int
    issues: list[RoadmapNonGoalRuntimeMetadataBoundaryIssue]


def roadmap_non_goal_runtime_metadata_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the ROADMAP non-goal runtime metadata source scan."""

    root_path = Path(root)
    source_boundary = roadmap_non_goal_contradiction_boundary_record(root_path)
    surface_records = [
        _runtime_surface_record(root_path, spec) for spec in RUNTIME_SURFACE_SPECS
    ]
    registry_records = _builtin_plugin_registry_records()
    contradiction_records = [
        hit
        for surface in surface_records
        for hit in surface["forbidden_support_claim_hit_records"]
    ]
    safe_phrase_missing_records = [
        phrase
        for surface in surface_records
        for phrase in surface["missing_safe_phrase_records"]
    ]
    return {
        "schema": ROADMAP_NON_GOAL_RUNTIME_METADATA_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_non_goal_boundary_input": SOURCE_NON_GOAL_BOUNDARY_INPUT,
        "source_non_goal_count": source_boundary["non_goal_count"],
        "runtime_surface_count": len(surface_records),
        "runtime_surface_records": surface_records,
        "runtime_metadata_path_count": sum(
            len(record["runtime_metadata_paths"]) for record in surface_records
        ),
        "source_missing_count": sum(
            1 for record in surface_records if record["source_status"] != "present"
        ),
        "safe_phrase_missing_count": len(safe_phrase_missing_records),
        "safe_phrase_missing_records": safe_phrase_missing_records,
        "builtin_plugin_registry_count": len(registry_records),
        "builtin_plugin_registry_records": registry_records,
        "forbidden_phrase_count": len(FORBIDDEN_RUNTIME_SUPPORT_CLAIM_PHRASES),
        "contradiction_count": len(contradiction_records),
        "contradiction_records": contradiction_records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary scans source-defined runtime metadata surfaces for "
            "ROADMAP non-goal support-claim contradictions: startup manifest "
            "config fields, candidate language runner policy, runtime plugin "
            "state, runtime plugin artifact metadata, and built-in plugin "
            "registry paper-inspiration labels. It does not claim CI promotion "
            "enforcement, an intentional promotion workflow, joined "
            "runtime/plugin/docs/paper scope proof, or owner-reviewed "
            "remediation readiness."
        ),
    }


def validate_roadmap_non_goal_runtime_metadata_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapNonGoalRuntimeMetadataBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_non_goal_runtime_metadata_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapNonGoalRuntimeMetadataBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_non_goal_runtime_metadata_boundary_record(root)
    issues: list[RoadmapNonGoalRuntimeMetadataBoundaryIssue] = []
    if data.get("schema") != ROADMAP_NON_GOAL_RUNTIME_METADATA_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP non-goal runtime metadata schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "runtime metadata scan must not claim full non-goal promotion readiness"))
    for key in (
        "source_non_goal_count",
        "runtime_surface_count",
        "runtime_surface_records",
        "runtime_metadata_path_count",
        "source_missing_count",
        "safe_phrase_missing_count",
        "safe_phrase_missing_records",
        "builtin_plugin_registry_count",
        "builtin_plugin_registry_records",
        "forbidden_phrase_count",
        "contradiction_count",
        "contradiction_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current runtime metadata inputs"))
    if data.get("contradiction_count") != 0:
        issues.append(_issue("contradiction_detected", "runtime metadata source contains forbidden non-goal support claim phrases"))
    required_count = _validate_required_fields(
        data.get("required_evidence_fields"), issues
    )
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "source-defined runtime metadata surfaces" not in boundary_text
        or "does not claim CI promotion enforcement" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate runtime metadata scan from promotion readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapNonGoalRuntimeMetadataBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        runtime_surface_count=data.get("runtime_surface_count") if isinstance(data.get("runtime_surface_count"), int) else 0,
        source_missing_count=data.get("source_missing_count") if isinstance(data.get("source_missing_count"), int) else 0,
        safe_phrase_missing_count=data.get("safe_phrase_missing_count") if isinstance(data.get("safe_phrase_missing_count"), int) else 0,
        contradiction_count=data.get("contradiction_count") if isinstance(data.get("contradiction_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_non_goal_runtime_metadata_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_non_goal_runtime_metadata_boundary(boundary)
    rows = [
        ("schema_status", "ok" if validation.ok else "invalid"),
        ("boundary_status", validation.boundary_status or "unknown"),
        ("runtime_surface_count", str(validation.runtime_surface_count)),
        ("source_missing_count", str(validation.source_missing_count)),
        ("safe_phrase_missing_count", str(validation.safe_phrase_missing_count)),
        ("contradiction_count", str(validation.contradiction_count)),
        ("missing_evidence_count", str(validation.missing_evidence_count)),
    ]
    lines = ["# ROADMAP non-goal runtime metadata boundary", "", "| Field | Value |", "| --- | --- |"]
    lines.extend(f"| {name} | {value} |" for name, value in rows)
    if validation.issues:
        lines.extend(["", "## Issues"])
        lines.extend(f"- `{issue.code}`: {issue.message}" for issue in validation.issues)
    return "\n".join(lines) + "\n"


def _runtime_surface_record(root_path: Path, spec: dict[str, Any]) -> dict[str, Any]:
    relative_path = Path(spec["path"])
    path = root_path / relative_path
    if not path.exists():
        return {
            "surface_id": spec["surface_id"],
            "path": relative_path.as_posix(),
            "source_status": "missing",
            "runtime_metadata_paths": list(spec["runtime_metadata_paths"]),
            "required_safe_phrases": list(spec["required_safe_phrases"]),
            "present_safe_phrases": [],
            "missing_safe_phrase_records": [
                {
                    "surface_id": spec["surface_id"],
                    "path": relative_path.as_posix(),
                    "phrase": phrase,
                }
                for phrase in spec["required_safe_phrases"]
            ],
            "forbidden_support_claim_hit_records": [],
        }
    text = path.read_text(encoding="utf-8", errors="ignore")
    present = [phrase for phrase in spec["required_safe_phrases"] if phrase in text]
    missing = [
        {
            "surface_id": spec["surface_id"],
            "path": relative_path.as_posix(),
            "phrase": phrase,
        }
        for phrase in spec["required_safe_phrases"]
        if phrase not in text
    ]
    return {
        "surface_id": spec["surface_id"],
        "path": relative_path.as_posix(),
        "source_status": "present",
        "runtime_metadata_paths": list(spec["runtime_metadata_paths"]),
        "required_safe_phrases": list(spec["required_safe_phrases"]),
        "present_safe_phrases": present,
        "missing_safe_phrase_records": missing,
        "forbidden_support_claim_hit_records": _forbidden_phrase_hits(
            relative_path, text
        ),
    }


def _forbidden_phrase_hits(relative_path: Path, text: str) -> list[dict[str, Any]]:
    hits: list[dict[str, Any]] = []
    lowered_lines = [line.lower() for line in text.splitlines()]
    for phrase in FORBIDDEN_RUNTIME_SUPPORT_CLAIM_PHRASES:
        phrase_lower = phrase.lower()
        for line_number, line in enumerate(lowered_lines, start=1):
            column = line.find(phrase_lower)
            if column == -1:
                continue
            hits.append(
                {
                    "path": relative_path.as_posix(),
                    "line_start": line_number,
                    "phrase": phrase,
                    "column_start": column + 1,
                }
            )
    return hits


def _builtin_plugin_registry_records() -> list[dict[str, Any]]:
    return [
        {
            "label": label,
            "plugin_class": definition.plugin_class.__name__,
            "plugin_module": definition.plugin_class.__module__,
            "paper_inspiration": definition.paper_inspiration,
            "option_names": sorted(definition.option_schema),
        }
        for label, definition in sorted(builtin_plugin_registry().items())
    ]


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapNonGoalRuntimeMetadataBoundaryIssue]]:
    if isinstance(boundary, dict):
        return boundary, []
    if isinstance(boundary, (str, Path)):
        path = Path(boundary)
        try:
            return json.loads(path.read_text(encoding="utf-8")), []
        except OSError as exc:
            return None, [_issue("read_error", f"could not read boundary: {exc}")]
        except json.JSONDecodeError as exc:
            return None, [_issue("json_error", f"could not parse boundary JSON: {exc}")]
    return None, [_issue("invalid_boundary_type", "boundary must be a dict or JSON path")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapNonGoalRuntimeMetadataBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_evidence_fields", "required_evidence_fields must be a list"))
        return 0
    for field in EXPECTED_REQUIRED_EVIDENCE_FIELDS:
        if field not in value:
            issues.append(_issue("missing_required_evidence_field", f"missing required evidence field: {field}"))
    return len(value)


def _validate_missing_evidence(
    value: object,
    issues: list[RoadmapNonGoalRuntimeMetadataBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be a dict"))
        return 0
    for field, expected_status in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(field) != expected_status:
            issues.append(_issue(f"invalid_missing_evidence_{field}", f"missing_evidence[{field!r}] must be {expected_status!r}"))
    unexpected = sorted(set(value) - set(EXPECTED_MISSING_EVIDENCE))
    for field in unexpected:
        issues.append(_issue("unexpected_missing_evidence_field", f"unexpected missing evidence field: {field}"))
    return len(value)


def _issue(
    code: str,
    message: str,
) -> RoadmapNonGoalRuntimeMetadataBoundaryIssue:
    return RoadmapNonGoalRuntimeMetadataBoundaryIssue(code=code, message=message)
