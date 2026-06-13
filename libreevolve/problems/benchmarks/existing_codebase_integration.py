from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EXISTING_CODEBASE_INTEGRATION_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_existing_codebase_integration_boundary.v1"
)
EXISTING_CODEBASE_RUNTIME_REPORT_SCHEMA = "libreevolve.existing_codebase_integration_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_ID = "2.1"
EXPECTED_SOURCE_SECTION_IDS = ("2.1",)
EXPECTED_BOUNDARY_STATUS = "smoke_source_setup_fixture_recorded_missing_real_upstream"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "original_codebase_id",
    "upstream_release_artifact",
    "pre_marker_source_sha256",
    "marker_added_setup_diff",
    "setup_change_counts",
    "evaluator_call_path_before_marker_insertion",
    "evaluator_call_path_after_marker_insertion",
    "copied_static_asset_source_identity",
    "codebase_scale_fixture",
    "runtime_report_linkage",
)
EXPECTED_MISSING_EVIDENCE = {
    "original_codebase_id": "smoke_fixture_id_recorded_not_external_upstream",
    "upstream_release_artifact": "local_fixture_manifest_recorded_not_external_release",
    "pre_marker_source_hashes": "smoke_fixture_hashes_recorded",
    "marker_added_setup_diff": "smoke_marker_only_diff_recorded",
    "setup_change_counts": "smoke_setup_counts_recorded",
    "evaluator_call_path_before_marker_insertion": "declared_for_smoke_fixture",
    "evaluator_call_path_after_marker_insertion": "declared_for_smoke_fixture",
    "copied_static_asset_source_identity": "smoke_static_asset_hashes_recorded",
    "codebase_scale_fixture": "smoke_fixture_recorded_not_codebase_scale",
}


@dataclass(frozen=True)
class ExistingCodebaseIntegrationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ExistingCodebaseIntegrationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ExistingCodebaseIntegrationBoundaryIssue]


def existing_codebase_integration_boundary_record() -> dict[str, Any]:
    """Return the current source-setup-level existing-codebase boundary."""

    return {
        "schema": EXISTING_CODEBASE_INTEGRATION_BOUNDARY_SCHEMA,
        "runtime_report_schema": EXISTING_CODEBASE_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_id": EXPECTED_SOURCE_SECTION_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_figures": ["Figure 2", "Figure 3"],
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": (
            "runtime_workspace_marker_inventory_and_smoke_source_setup_metadata_available"
        ),
        "claim_ready": False,
        "marker_contract": {
            "language": "python",
            "start_marker": "# EVOLVE-BLOCK-START",
            "end_marker": "# EVOLVE-BLOCK-END",
            "marker_grammar": "python_comment_exact_token_optional_manifest_safe_name",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has runtime workspace marker "
            "inventory evidence plus a checked-in smoke fixture with source-setup "
            "metadata, but does not claim AlphaEvolve-style minimal-change "
            "integration with a real external upstream codebase, codebase-scale "
            "fixture, independent setup-diff artifact, or verified evaluator-call "
            "continuity beyond the smoke fixture."
        ),
    }


def validate_existing_codebase_integration_boundary(
    boundary: object | str | Path | None = None,
) -> ExistingCodebaseIntegrationBoundaryValidation:
    data, read_issues = _load_boundary(
        existing_codebase_integration_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ExistingCodebaseIntegrationBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ExistingCodebaseIntegrationBoundaryIssue] = []
    if data.get("schema") != EXISTING_CODEBASE_INTEGRATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported existing-codebase boundary schema"))
    if data.get("runtime_report_schema") != EXISTING_CODEBASE_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify the existing-codebase runtime report"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_id") != EXPECTED_SOURCE_SECTION_ID:
        issues.append(_issue("invalid_source_section_id", "source_section_id must be 2.1"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.1']"))
    if data.get("source_figures") != ["Figure 2", "Figure 3"]:
        issues.append(_issue("invalid_source_figures", "source_figures must link Figure 2 and Figure 3"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if (
        data.get("runtime_report_status")
        != "runtime_workspace_marker_inventory_and_smoke_source_setup_metadata_available"
    ):
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to marker inventory plus smoke source-setup metadata"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "existing-codebase integration boundary must not claim paper readiness"))
    _validate_marker_contract(data.get("marker_contract"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim source-level integration"))
    return ExistingCodebaseIntegrationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_existing_codebase_integration_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_existing_codebase_integration_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve existing-codebase integration boundary",
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
) -> tuple[dict[str, Any] | None, list[ExistingCodebaseIntegrationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "existing-codebase integration boundary must be a JSON object")]


def _validate_marker_contract(
    value: object,
    issues: list[ExistingCodebaseIntegrationBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_marker_contract", "marker_contract must be an object"))
        return
    expected = existing_codebase_integration_boundary_record()["marker_contract"]
    for key, expected_value in expected.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_marker_contract_{key}", f"marker_contract.{key} must be {expected_value}"))


def _validate_required_fields(
    value: object,
    issues: list[ExistingCodebaseIntegrationBoundaryIssue],
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
    issues: list[ExistingCodebaseIntegrationBoundaryIssue],
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


def _issue(code: str, message: str) -> ExistingCodebaseIntegrationBoundaryIssue:
    return ExistingCodebaseIntegrationBoundaryIssue(code, message)
