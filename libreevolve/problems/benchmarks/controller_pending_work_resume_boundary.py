from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CONTROLLER_PENDING_WORK_RESUME_BOUNDARY_SCHEMA = (
    "libreevolve.controller_pending_work_resume_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.5", "2.6")
EXPECTED_BOUNDARY_STATUS = "terminal_controller_snapshot_without_pending_work_resume"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "controller_state_schema",
    "terminal_drained_controller_state",
    "pending_work_zero_count_validation",
    "controller_budget_event_stream_validation",
    "controller_state_artifact_inventory",
    "full_resume_bundle_validation_schema",
    "cli_restore_runtime_entrypoint",
    "direct_evolve_resume_entrypoint",
    "unsupported_surface_list",
    "controller_queue_checkpoint_schema",
    "queued_proposal_resume_state",
    "running_evaluation_resume_state",
    "in_flight_llm_call_resume_state",
    "pending_archive_admission_resume_state",
    "partial_generation_replay_trace",
    "async_controller_graph_checkpoint",
    "provider_output_handoff_replay",
    "end_to_end_resumed_trace_proof",
)
EXPECTED_MISSING_EVIDENCE = {
    "controller_queue_checkpoint_schema": "not_recorded_locally",
    "queued_proposal_resume_state": "not_recorded_locally",
    "running_evaluation_resume_state": "not_recorded_locally",
    "in_flight_llm_call_resume_state": "not_recorded_locally",
    "pending_archive_admission_resume_state": "not_recorded_locally",
    "partial_generation_replay_trace": "not_recorded_locally",
    "async_controller_graph_checkpoint": "not_recorded_locally",
    "provider_output_handoff_replay": "not_recorded_locally",
    "end_to_end_resumed_trace_proof": "not_recorded_locally",
}


@dataclass(frozen=True)
class ControllerPendingWorkResumeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ControllerPendingWorkResumeBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ControllerPendingWorkResumeBoundaryIssue]


def controller_pending_work_resume_boundary_record() -> dict[str, Any]:
    """Return the pending-work resume boundary for controller state."""

    return {
        "schema": CONTROLLER_PENDING_WORK_RESUME_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve's asynchronous controller and long-running island "
            "search require resume evidence for queued, running, and pending "
            "work, not only terminal drained-state snapshots."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "controller_state_schema": "libreevolve.controller_state.v1",
        "full_resume_bundle_validation_schema": (
            "libreevolve.full_resume_bundle_validation.v1"
        ),
        "runtime_report_status": "terminal_controller_state_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve writes a terminal "
            "runtime.history.controller_state snapshot for the single-process "
            "synchronous loop, validates zero queued/running/pending work at "
            "finalization, checks the controller_budget_events.jsonl stream, "
            "exposes controller-state artifact inventory, and includes the "
            "same unsupported pending-work surfaces in full-runtime restore "
            "bundle validation. It does not claim controller queue checkpoint "
            "schema support, queued proposal resume state, running evaluation "
            "resume state, in-flight LLM call resume state, pending archive "
            "admission resume state, partial-generation replay trace, async "
            "controller graph checkpoint, provider-output handoff replay, or "
            "end-to-end resumed trace proof."
        ),
    }


def validate_controller_pending_work_resume_boundary(
    boundary: object | str | Path | None = None,
) -> ControllerPendingWorkResumeBoundaryValidation:
    data, read_issues = _load_boundary(
        controller_pending_work_resume_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return ControllerPendingWorkResumeBoundaryValidation(
            False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[ControllerPendingWorkResumeBoundaryIssue] = []
    if data.get("schema") != CONTROLLER_PENDING_WORK_RESUME_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported controller pending-work resume boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.5 and 2.6"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "asynchronous controller" not in source_claim
        or "queued, running, and pending work" not in source_claim
        or "terminal drained-state snapshots" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify async controller pending-work resume"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("controller_state_schema") != "libreevolve.controller_state.v1":
        issues.append(_issue("invalid_controller_state_schema", "controller_state_schema must be linked"))
    if (
        data.get("full_resume_bundle_validation_schema")
        != "libreevolve.full_resume_bundle_validation.v1"
    ):
        issues.append(_issue("invalid_full_resume_bundle_validation_schema", "full resume bundle validation schema must be linked"))
    if data.get("runtime_report_status") != "terminal_controller_state_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to terminal controller state"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "pending-work resume boundary must not claim queue-checkpoint readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim controller queue checkpoint schema support" not in boundary_text
        or "in-flight LLM call resume state" not in boundary_text
        or "end-to-end resumed trace proof" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate terminal controller snapshots from pending-work resume"))
    return ControllerPendingWorkResumeBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_controller_pending_work_resume_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_controller_pending_work_resume_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Controller pending-work resume boundary",
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
) -> tuple[
    dict[str, Any] | None,
    list[ControllerPendingWorkResumeBoundaryIssue],
]:
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
    return None, [_issue("invalid_shape", "controller pending-work resume boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ControllerPendingWorkResumeBoundaryIssue],
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
    issues: list[ControllerPendingWorkResumeBoundaryIssue],
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


def _issue(
    code: str,
    message: str,
) -> ControllerPendingWorkResumeBoundaryIssue:
    return ControllerPendingWorkResumeBoundaryIssue(code, message)
