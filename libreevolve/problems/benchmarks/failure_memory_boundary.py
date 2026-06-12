from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FAILURE_MEMORY_BOUNDARY_SCHEMA = "libreevolve.failure_memory_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_FAILURE_INDEX_SCHEMA = "libreevolve.failure_index.v1"
EXPECTED_FAILURE_HISTORY_SCHEMA = "libreevolve.failure_history.v1"
EXPECTED_BOUNDARY_STATUS = "run_local_failure_diagnostics_not_semantic_memory"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "failure_history_jsonl_rows",
    "strict_failure_history_loader",
    "persisted_failure_fingerprints",
    "repetition_counts",
    "changed_file_summaries",
    "file_delta_summaries",
    "evaluation_error_summaries",
    "stage_error_summaries",
    "bounded_prompt_visible_failure_memory",
    "configurable_recent_failure_filters",
    "runtime_failure_index",
    "proposal_lifecycle_failure_reuse_summary",
    "durable_cross_run_failure_table",
    "semantic_failed_proposal_retrieval",
    "learned_repetition_avoidance_policy",
    "replayable_failed_mutation_payloads",
    "failure_aware_sampling_policy",
    "cross_run_failure_index_migrations",
)
EXPECTED_MISSING_EVIDENCE = {
    "durable_cross_run_failure_table": "not_recorded_locally",
    "semantic_failed_proposal_retrieval": "not_recorded_locally",
    "learned_repetition_avoidance_policy": "not_recorded_locally",
    "replayable_failed_mutation_payloads": "not_recorded_locally",
    "failure_aware_sampling_policy": "not_recorded_locally",
    "cross_run_failure_index_migrations": "not_recorded_locally",
}


@dataclass(frozen=True)
class FailureMemoryBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class FailureMemoryBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[FailureMemoryBoundaryIssue]


def failure_memory_boundary_record() -> dict[str, Any]:
    """Return the run-local failure diagnostics versus semantic memory boundary."""

    return {
        "schema": FAILURE_MEMORY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve-style evolutionary memory should reuse failed "
            "proposal evidence through durable, searchable, and semantically "
            "meaningful memory rather than only bounded run-local diagnostics"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "failure_index_schema": EXPECTED_FAILURE_INDEX_SCHEMA,
        "failure_history_schema": EXPECTED_FAILURE_HISTORY_SCHEMA,
        "runtime_report_status": "run_local_failure_index_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve persists run-local "
            "failure_history.jsonl rows, validates them with a strict loader, "
            "stores failure fingerprints and repetition counts, summarizes "
            "changed files, file deltas, evaluation and stage errors, renders "
            "bounded prompt-visible failure memory with configurable filters, "
            "emits runtime.history.failure_index, and summarizes failure reuse "
            "in proposal lifecycle reports. It does not claim durable cross-run "
            "failure tables, semantic failed-proposal retrieval, learned "
            "repetition avoidance, replayable failed-mutation payloads, "
            "failure-aware sampling policy, or cross-run failure-index "
            "migrations."
        ),
    }


def validate_failure_memory_boundary(
    boundary: object | str | Path | None = None,
) -> FailureMemoryBoundaryValidation:
    data, read_issues = _load_boundary(
        failure_memory_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return FailureMemoryBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[FailureMemoryBoundaryIssue] = []
    if data.get("schema") != FAILURE_MEMORY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported failure-memory boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "failed proposal evidence" not in source_claim
        or "semantically meaningful memory" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify semantic failed-proposal memory"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("failure_index_schema") != EXPECTED_FAILURE_INDEX_SCHEMA:
        issues.append(_issue("invalid_failure_index_schema", f"failure_index_schema must be {EXPECTED_FAILURE_INDEX_SCHEMA}"))
    if data.get("failure_history_schema") != EXPECTED_FAILURE_HISTORY_SCHEMA:
        issues.append(_issue("invalid_failure_history_schema", f"failure_history_schema must be {EXPECTED_FAILURE_HISTORY_SCHEMA}"))
    if data.get("runtime_report_status") != "run_local_failure_index_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to run-local failure diagnostics"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "failure-memory boundary must not claim semantic failed-proposal memory readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim durable cross-run failure tables" not in boundary_text
        or "semantic failed-proposal retrieval" not in boundary_text
        or "failure-aware sampling policy" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate run-local diagnostics from semantic failed-proposal memory"))
    return FailureMemoryBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_failure_memory_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_failure_memory_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Failure memory boundary",
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
) -> tuple[dict[str, Any] | None, list[FailureMemoryBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "failure-memory boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[FailureMemoryBoundaryIssue],
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
    issues: list[FailureMemoryBoundaryIssue],
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


def _issue(code: str, message: str) -> FailureMemoryBoundaryIssue:
    return FailureMemoryBoundaryIssue(code, message)
