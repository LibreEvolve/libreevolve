from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.core.artifact_schema import run_artifact_schema


NON_JSONL_ARTIFACT_BOUNDARY_SCHEMA = "libreevolve.non_jsonl_artifact_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.5", "2.6", "4")
EXPECTED_BOUNDARY_STATUS = (
    "schema_checked_non_jsonl_artifacts_without_payload_replay_certification"
)
EXPECTED_RUNTIME_SCHEMA_POINTER = "artifact_schema.non_jsonl_artifacts"
EXPECTED_ARTIFACT_NAMES = (
    "best.py",
    "best_workspace",
    "evaluator_artifacts",
    "manifest.json",
    "paper_artifacts",
    "plugin_artifacts",
    "task_specification.json",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "runtime_schema_pointer",
    "declared_artifact_names",
    "artifact_kind_policy",
    "presence_condition_policy",
    "writer_owner_policy",
    "reader_owner_policy",
    "hash_policy",
    "runtime_pointer_location",
    "lifecycle_status",
    "generated_inventory_linkage",
    "implementation_anchor_linkage",
    "documentation_anchor_linkage",
    "behavior_test_anchor_linkage",
    "show_policy_validation",
    "restore_policy_validation",
    "paper_artifact_subpath_schema",
    "full_restored_run_payload_replay",
    "artifact_payload_carry_forward",
    "cross_run_payload_reconstruction",
    "independent_bundle_audit",
    "paper_artifact_replay_certification",
)
EXPECTED_MISSING_EVIDENCE = {
    "full_restored_run_payload_replay": "not_recorded_locally",
    "artifact_payload_carry_forward": "not_recorded_locally",
    "cross_run_payload_reconstruction": "not_recorded_locally",
    "independent_bundle_audit": "not_recorded_locally",
    "paper_artifact_replay_certification": "not_recorded_locally",
}


@dataclass(frozen=True)
class NonJsonlArtifactBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class NonJsonlArtifactBoundaryValidation:
    ok: bool
    boundary_status: str | None
    artifact_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[NonJsonlArtifactBoundaryIssue]


def non_jsonl_artifact_boundary_record() -> dict[str, Any]:
    """Return the non-JSONL artifact schema versus replay-proof boundary."""

    schema = run_artifact_schema()
    non_jsonl_artifacts = schema["non_jsonl_artifacts"]
    inventory = schema["generated_artifact_inventory"]
    return {
        "schema": NON_JSONL_ARTIFACT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve-style long-running experiment directories need "
            "standalone JSON files, exported source files, workspaces, and "
            "artifact directories to be discoverable as part of the run bundle "
            "without confusing schema/hash policy checks with full replay "
            "or artifact payload reconstruction proof."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_schema_pointer": EXPECTED_RUNTIME_SCHEMA_POINTER,
        "claim_ready": False,
        "artifact_names": sorted(non_jsonl_artifacts),
        "non_jsonl_artifacts": non_jsonl_artifacts,
        "generated_inventory_records": {
            name: {
                "artifact_kind": inventory[name]["artifact_kind"],
                "schema_pointer": inventory[name]["schema_pointer"],
                "cleanup_managed": inventory[name]["cleanup_managed"],
                "runtime_pointer_location": inventory[name][
                    "runtime_pointer_location"
                ],
                "restore_show_handling": inventory[name]["restore_show_handling"],
                "implementation_anchor_groups": sorted(
                    inventory[name]["implementation_anchors"]
                ),
                "behavior_test_anchor_groups": sorted(
                    inventory[name]["behavior_test_anchors"]
                ),
                "documentation_anchor_count": len(
                    inventory[name]["documentation_anchors"]
                ),
            }
            for name in sorted(non_jsonl_artifacts)
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the runtime manifest schema for non-JSONL "
            "run artifacts, including path, kind, presence condition, writer "
            "owner, reader owner, hash policy, lifecycle status, runtime "
            "pointer location, generated inventory linkage, implementation "
            "anchors, documentation anchors, behavior-test anchors, show and "
            "restore policy validation, and the paper_artifacts subpath schema. "
            "It does not claim full restored-run payload replay, artifact "
            "payload carry-forward, cross-run payload reconstruction, "
            "independent bundle audit, or paper_artifacts replay certification."
        ),
    }


def validate_non_jsonl_artifact_boundary(
    boundary: object | str | Path | None = None,
) -> NonJsonlArtifactBoundaryValidation:
    data, read_issues = _load_boundary(
        non_jsonl_artifact_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return NonJsonlArtifactBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[NonJsonlArtifactBoundaryIssue] = []
    expected = non_jsonl_artifact_boundary_record()
    if data.get("schema") != NON_JSONL_ARTIFACT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported non-JSONL artifact boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.5, 2.6, and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "standalone JSON files" not in source_claim
        or "artifact directories" not in source_claim
        or "payload reconstruction proof" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify non-JSONL bundle and payload reconstruction scope"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_schema_pointer") != EXPECTED_RUNTIME_SCHEMA_POINTER:
        issues.append(_issue("invalid_runtime_schema_pointer", f"runtime schema pointer must be {EXPECTED_RUNTIME_SCHEMA_POINTER}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "non-JSONL artifact boundary must not claim full replay readiness"))
    artifact_names = data.get("artifact_names")
    if artifact_names != list(EXPECTED_ARTIFACT_NAMES):
        issues.append(_issue("invalid_artifact_names", "non-JSONL artifact names drifted from run_artifact_schema"))
    artifact_count = _validate_artifacts(data.get("non_jsonl_artifacts"), expected, issues)
    _validate_inventory(data.get("generated_inventory_records"), expected, issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "runtime manifest schema for non-JSONL run artifacts" not in boundary_text
        or "does not claim full restored-run payload replay" not in boundary_text
        or "paper_artifacts replay certification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate non-JSONL schema evidence from payload replay proof"))
    return NonJsonlArtifactBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        artifact_count=artifact_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_non_jsonl_artifact_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_non_jsonl_artifact_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Non-JSONL artifact boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| artifact_count | {validation.artifact_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[NonJsonlArtifactBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "non-JSONL artifact boundary must be a JSON object")]


def _validate_artifacts(
    value: object,
    expected: dict[str, Any],
    issues: list[NonJsonlArtifactBoundaryIssue],
) -> int:
    expected_artifacts = expected["non_jsonl_artifacts"]
    if value != expected_artifacts:
        issues.append(_issue("invalid_non_jsonl_artifacts", "non_jsonl_artifacts drifted from run_artifact_schema"))
    return len(value) if isinstance(value, dict) else 0


def _validate_inventory(
    value: object,
    expected: dict[str, Any],
    issues: list[NonJsonlArtifactBoundaryIssue],
) -> int:
    expected_inventory = expected["generated_inventory_records"]
    if value != expected_inventory:
        issues.append(_issue("invalid_generated_inventory_records", "generated inventory records drifted from run_artifact_schema"))
    return len(value) if isinstance(value, dict) else 0


def _validate_required_fields(
    value: object,
    issues: list[NonJsonlArtifactBoundaryIssue],
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
    issues: list[NonJsonlArtifactBoundaryIssue],
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


def _issue(code: str, message: str) -> NonJsonlArtifactBoundaryIssue:
    return NonJsonlArtifactBoundaryIssue(code, message)
