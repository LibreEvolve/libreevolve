from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


WHOLE_RUN_SOURCE_WORKSPACE_INTEGRITY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_whole_run_source_workspace_integrity_boundary.v1"
)
WHOLE_RUN_SOURCE_WORKSPACE_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.whole_run_source_workspace_integrity_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "bounded_retained_program_integrity_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "retained_program_workspace_hashes",
    "primary_file_coherence",
    "source_payload_shape",
    "static_file_reference_counts",
    "startup_provenance_summary",
    "selected_runtime_artifact_hashes",
    "whole_run_cli_query_surface",
    "full_source_payload_replay",
    "cross_run_workspace_dedup_index",
    "static_file_content_replay",
    "selected_and_unselected_source_diff_views",
)
EXPECTED_MISSING_EVIDENCE = {
    "durable_whole_run_query_surface": "not_recorded_locally",
    "full_source_payload_replay_artifacts": "not_recorded_locally",
    "cross_run_workspace_dedup_index": "not_recorded_locally",
    "static_file_content_replay_or_external_blob_store": "not_recorded_locally",
    "selected_and_unselected_candidate_source_diff_views": "not_recorded_locally",
}


@dataclass(frozen=True)
class WholeRunSourceWorkspaceIntegrityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class WholeRunSourceWorkspaceIntegrityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[WholeRunSourceWorkspaceIntegrityBoundaryIssue]


def whole_run_source_workspace_integrity_boundary_record() -> dict[str, Any]:
    """Return the current whole-run source/workspace integrity boundary."""

    return {
        "schema": WHOLE_RUN_SOURCE_WORKSPACE_INTEGRITY_BOUNDARY_SCHEMA,
        "runtime_report_schema": WHOLE_RUN_SOURCE_WORKSPACE_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve-scale runs need auditable generated-program database "
            "evidence across retained candidates, not only selected best-code "
            "display or compact manifest summaries"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "whole_run_source_workspace_integrity_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has a runtime report for "
            "retained-program workspace hashes, primary-file coherence, source "
            "payload shape, static-file reference counts, startup provenance "
            "presence, and selected runtime artifact file/tree hashes, but "
            "does not claim a durable whole-run query surface, full raw source "
            "payload replay artifacts, cross-run workspace deduplication index, "
            "static-file content replay, or selected/unselected candidate "
            "source-diff views."
        ),
    }


def validate_whole_run_source_workspace_integrity_boundary(
    boundary: object | str | Path | None = None,
) -> WholeRunSourceWorkspaceIntegrityBoundaryValidation:
    data, read_issues = _load_boundary(
        whole_run_source_workspace_integrity_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return WholeRunSourceWorkspaceIntegrityBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[WholeRunSourceWorkspaceIntegrityBoundaryIssue] = []
    if data.get("schema") != WHOLE_RUN_SOURCE_WORKSPACE_INTEGRITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported whole-run integrity boundary schema"))
    if data.get("runtime_report_schema") != WHOLE_RUN_SOURCE_WORKSPACE_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify whole-run integrity reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "generated-program database" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify generated-program database evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "whole_run_source_workspace_integrity_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to whole-run integrity reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "whole-run integrity boundary must not claim generated-program database readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim whole-run database parity"))
    return WholeRunSourceWorkspaceIntegrityBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_whole_run_source_workspace_integrity_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_whole_run_source_workspace_integrity_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve whole-run source/workspace integrity boundary",
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
) -> tuple[dict[str, Any] | None, list[WholeRunSourceWorkspaceIntegrityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "whole-run integrity boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[WholeRunSourceWorkspaceIntegrityBoundaryIssue],
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
    issues: list[WholeRunSourceWorkspaceIntegrityBoundaryIssue],
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


def _issue(code: str, message: str) -> WholeRunSourceWorkspaceIntegrityBoundaryIssue:
    return WholeRunSourceWorkspaceIntegrityBoundaryIssue(code, message)
