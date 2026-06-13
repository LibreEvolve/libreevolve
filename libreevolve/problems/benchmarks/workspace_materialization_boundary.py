from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


WORKSPACE_MATERIALIZATION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_workspace_materialization_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.1", "Table 1")
EXPECTED_BOUNDARY_STATUS = "local_file_workspace_diagnostics_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "candidate_materialization_error_reason_contract",
    "bounded_materialization_error_paths",
    "casefold_collision_diagnostics",
    "recursive_link_preflight",
    "static_source_copy_hash_checks",
    "static_source_copy_portable_identity",
    "bulk_directory_operation_diagnostics",
    "generated_dependency_graph_diagnostics",
    "language_build_runner_artifact_diagnostics",
    "remote_or_container_mount_diagnostics",
    "stable_reason_path_contract_for_future_surfaces",
    "paper_facing_invalid_workspace_fixture_rows",
)
EXPECTED_MISSING_EVIDENCE = {
    "static_source_copy_portable_identity": "local_path_label_only",
    "bulk_directory_operation_diagnostics": "not_supported",
    "generated_dependency_graph_diagnostics": "not_recorded_locally",
    "language_build_runner_artifact_diagnostics": "not_recorded_locally",
    "remote_or_container_mount_diagnostics": "not_recorded_locally",
    "paper_facing_invalid_workspace_fixture_rows": "not_recorded_locally",
}


@dataclass(frozen=True)
class WorkspaceMaterializationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class WorkspaceMaterializationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[WorkspaceMaterializationBoundaryIssue]


def workspace_materialization_boundary_record() -> dict[str, Any]:
    """Return the paper-facing workspace materialization diagnostics boundary."""

    return {
        "schema": WORKSPACE_MATERIALIZATION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve evolves task-defined program artifacts and Table 1 "
            "contrasts entire-code-file/codebase evolution with narrower code "
            "generation systems, so invalid generated workspaces need stable, "
            "inspectable diagnostics as the workspace surface expands"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records LibreEvolve's current local file-workspace "
            "materialization diagnostics: typed CandidateMaterializationError "
            "reasons, bounded paths, casefold collision diagnostics, recursive "
            "link preflight, and static source-copy byte/hash checks. It does "
            "not claim portable static source-copy identity, bulk directory "
            "operation diagnostics, generated dependency graph diagnostics, "
            "language/build-runner artifact diagnostics, remote or container "
            "mount diagnostics, paper-facing invalid-workspace fixture rows, or "
            "a proven stable reason/path contract for future topology surfaces."
        ),
    }


def validate_workspace_materialization_boundary(
    boundary: object | str | Path | None = None,
) -> WorkspaceMaterializationBoundaryValidation:
    data, read_issues = _load_boundary(
        workspace_materialization_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return WorkspaceMaterializationBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[WorkspaceMaterializationBoundaryIssue] = []
    if data.get("schema") != WORKSPACE_MATERIALIZATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported workspace materialization boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.1', 'Table 1']"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "task-defined program artifacts" not in source_claim
        or "Table 1" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify workspace/codebase materialization evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "workspace materialization boundary must not claim future-surface readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim portable static source-copy identity" not in boundary_text
        or "bulk directory operation diagnostics" not in boundary_text
        or "language/build-runner artifact diagnostics" not in boundary_text
        or "stable reason/path contract for future topology surfaces" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate local diagnostics from future topology parity"))
    return WorkspaceMaterializationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_workspace_materialization_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_workspace_materialization_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve workspace materialization boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[WorkspaceMaterializationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "workspace materialization boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[WorkspaceMaterializationBoundaryIssue],
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
    issues: list[WorkspaceMaterializationBoundaryIssue],
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


def _issue(code: str, message: str) -> WorkspaceMaterializationBoundaryIssue:
    return WorkspaceMaterializationBoundaryIssue(code, message)
