from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RESTORE_CERTIFICATION_BOUNDARY_SCHEMA = "libreevolve.restore_certification_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.5", "2.6", "4")
EXPECTED_RUNTIME_RESTORE_CERTIFICATION_SCHEMA = (
    "libreevolve.full_resume_restore_certification.v1"
)
EXPECTED_RUN_ARTIFACT_BUNDLE_REPORT_SCHEMA = "libreevolve.run_artifact_bundle_report.v1"
EXPECTED_BOUNDARY_STATUS = (
    "compatible_manifest_restore_certification_without_full_replay_proof"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "runtime_restore_certification_schema",
    "runtime_run_artifact_bundle_report_schema",
    "accepted_stream_manifest_validation",
    "quarantine_stream_manifest_validation",
    "accepted_quarantine_boundary_validation",
    "show_time_restore_certification_validation",
    "cli_restore_certification_validation",
    "direct_runtime_restore_loader_validation",
    "direct_archive_restore_loader_validation",
    "provider_output_replay_exclusion",
    "pending_work_resume_exclusion",
    "artifact_payload_reconstruction_exclusion",
    "compatible_resume_surface_certification",
    "full_replay_ready_false_boundary",
    "provider_output_replay_ready_false_boundary",
    "pending_work_resume_ready_false_boundary",
    "resumed_trace_proof_ready_false_boundary",
    "cross_run_restore_replay_evidence",
    "provider_raw_payload_sidecars",
    "controller_pending_work_checkpoint",
    "artifact_payload_reconstruction_hashes",
    "independent_restore_replay_audit",
)
EXPECTED_MISSING_EVIDENCE = {
    "cross_run_restore_replay_evidence": "not_recorded_locally",
    "provider_raw_payload_sidecars": "not_recorded_locally",
    "controller_pending_work_checkpoint": "not_recorded_locally",
    "artifact_payload_reconstruction_hashes": "not_recorded_locally",
    "independent_restore_replay_audit": "not_recorded_locally",
}


@dataclass(frozen=True)
class RestoreCertificationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RestoreCertificationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[RestoreCertificationBoundaryIssue]


def restore_certification_boundary_record() -> dict[str, Any]:
    """Return the runtime restore-certification versus full replay boundary."""

    return {
        "schema": RESTORE_CERTIFICATION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve-style long-running search needs auditable restore "
            "and replay evidence that separates accepted experiment state from "
            "diagnostic quarantine rows and from provider/controller payloads "
            "that are not replayed."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_restore_certification_schema": (
            EXPECTED_RUNTIME_RESTORE_CERTIFICATION_SCHEMA
        ),
        "runtime_run_artifact_bundle_report_schema": (
            EXPECTED_RUN_ARTIFACT_BUNDLE_REPORT_SCHEMA
        ),
        "runtime_report_status": (
            "compatible_restore_surfaces_certified_with_full_replay_boundaries"
        ),
        "claim_ready": False,
        "implemented_runtime_evidence": {
            "runtime_restore_certification_schema": (
                "runtime.restore_certification uses "
                "libreevolve.full_resume_restore_certification.v1"
            ),
            "runtime_run_artifact_bundle_report_schema": (
                "runtime.run_artifact_bundle_report links accepted streams, "
                "quarantine diagnostics, non-JSONL policy, and paper artifacts"
            ),
            "accepted_stream_manifest_validation": (
                "restore/show readers validate manifest-advertised accepted streams"
            ),
            "quarantine_stream_manifest_validation": (
                "restore/show readers validate manifest-advertised quarantine streams"
            ),
            "accepted_quarantine_boundary_validation": (
                "restore certification records quarantine rows as diagnostics, "
                "not replayed state"
            ),
            "show_time_restore_certification_validation": (
                "libreevolve show rejects restore-certification overclaims"
            ),
            "cli_restore_certification_validation": (
                "CLI restore flags reject restore-certification overclaims before run"
            ),
            "direct_runtime_restore_loader_validation": (
                "direct runtime restore loaders validate the certification report"
            ),
            "direct_archive_restore_loader_validation": (
                "direct archive restore loaders validate the certification report"
            ),
            "provider_output_replay_exclusion": (
                "provider_output_replay_ready remains false"
            ),
            "pending_work_resume_exclusion": "pending_work_resume_ready remains false",
            "artifact_payload_reconstruction_exclusion": (
                "artifact payload reconstruction is outside current certification"
            ),
            "compatible_resume_surface_certification": (
                "compatible_resume_ready remains true for supported manifest surfaces"
            ),
            "full_replay_ready_false_boundary": "full_replay_ready remains false",
            "provider_output_replay_ready_false_boundary": (
                "provider_output_replay_ready remains false"
            ),
            "pending_work_resume_ready_false_boundary": (
                "pending_work_resume_ready remains false"
            ),
            "resumed_trace_proof_ready_false_boundary": (
                "resumed_trace_proof_ready remains false"
            ),
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that runtime.restore_certification validates "
            "compatible local manifest restore surfaces, run-artifact bundle "
            "report linkage, accepted-stream validation, quarantine-diagnostic "
            "validation, show-time rejection, CLI restore rejection, direct "
            "runtime restore-loader rejection, direct archive restore-loader "
            "rejection, and the explicit separation of quarantine diagnostics "
            "from accepted state. It does not claim full replay proof, provider "
            "raw-payload replay, controller pending-work checkpoint replay, "
            "artifact payload reconstruction hashes, cross-run restore/replay "
            "evidence, or independent restore/replay audit."
        ),
    }


def validate_restore_certification_boundary(
    boundary: object | str | Path | None = None,
) -> RestoreCertificationBoundaryValidation:
    data, read_issues = _load_boundary(
        restore_certification_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return RestoreCertificationBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[RestoreCertificationBoundaryIssue] = []
    if data.get("schema") != RESTORE_CERTIFICATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported restore certification boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.5, 2.6, and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "accepted experiment state" not in source_claim
        or "diagnostic quarantine rows" not in source_claim
        or "provider/controller payloads" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify accepted state, quarantine diagnostics, and provider/controller payload boundaries"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_restore_certification_schema") != EXPECTED_RUNTIME_RESTORE_CERTIFICATION_SCHEMA:
        issues.append(_issue("invalid_runtime_restore_certification_schema", f"runtime restore certification schema must be {EXPECTED_RUNTIME_RESTORE_CERTIFICATION_SCHEMA}"))
    if data.get("runtime_run_artifact_bundle_report_schema") != EXPECTED_RUN_ARTIFACT_BUNDLE_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_run_artifact_bundle_report_schema", f"run artifact bundle report schema must be {EXPECTED_RUN_ARTIFACT_BUNDLE_REPORT_SCHEMA}"))
    if data.get("runtime_report_status") != "compatible_restore_surfaces_certified_with_full_replay_boundaries":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to compatible restore surfaces"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "restore certification boundary must not claim full replay readiness"))
    implemented_count = _validate_implemented_runtime_evidence(
        data.get("implemented_runtime_evidence"), issues
    )
    if implemented_count != 17:
        issues.append(_issue("invalid_implemented_runtime_evidence_count", "implemented runtime evidence count must be 17"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "explicit separation of quarantine diagnostics from accepted state" not in boundary_text
        or "does not claim full replay proof" not in boundary_text
        or "independent restore/replay audit" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate compatible restore certification from full replay proof"))
    return RestoreCertificationBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_restore_certification_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_restore_certification_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Restore certification boundary",
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
) -> tuple[dict[str, Any] | None, list[RestoreCertificationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "restore certification boundary must be a JSON object")]


def _validate_implemented_runtime_evidence(
    value: object,
    issues: list[RestoreCertificationBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_implemented_runtime_evidence", "implemented_runtime_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_REQUIRED_EVIDENCE_FIELDS) - set(EXPECTED_MISSING_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_implemented_runtime_evidence", f"implemented_runtime_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_implemented_runtime_evidence", f"implemented_runtime_evidence has unknown keys: {', '.join(extra)}"))
    for key, evidence_status in value.items():
        if not isinstance(key, str) or not isinstance(evidence_status, str) or not evidence_status:
            issues.append(_issue("invalid_implemented_runtime_evidence_entry", "implemented runtime evidence entries must be non-empty text"))
            break
    return len(actual_keys)


def _validate_required_fields(
    value: object,
    issues: list[RestoreCertificationBoundaryIssue],
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
    issues: list[RestoreCertificationBoundaryIssue],
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


def _issue(code: str, message: str) -> RestoreCertificationBoundaryIssue:
    return RestoreCertificationBoundaryIssue(code, message)
