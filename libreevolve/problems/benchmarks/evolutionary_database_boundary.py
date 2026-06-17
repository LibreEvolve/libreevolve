from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


EVOLUTIONARY_DATABASE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_evolutionary_database_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "current_run_resurfacing_without_durable_database"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "accepted_history_jsonl",
    "failure_history_jsonl",
    "archive_events_jsonl",
    "archive_state_snapshot",
    "resurfacing_index_summary",
    "metric_resurfacing_queries",
    "lineage_resurfacing_queries",
    "descriptor_resurfacing_queries",
    "novelty_resurfacing_queries",
    "feedback_resurfacing_queries",
    "program_output_resurfacing_queries",
    "artifact_index_summary",
    "hypothesis_index_summary",
    "failure_index_summary",
    "durable_cross_run_query_store",
    "schema_versioned_database_migrations",
    "semantic_retrieval_indexes",
    "replayable_sampling_policy",
    "cross_run_failure_memory",
    "learned_novelty_model",
)
EXPECTED_MISSING_EVIDENCE = {
    "durable_cross_run_query_store": "not_recorded_locally",
    "schema_versioned_database_migrations": "not_recorded_locally",
    "semantic_retrieval_indexes": "not_recorded_locally",
    "replayable_sampling_policy": "not_recorded_locally",
    "cross_run_failure_memory": "not_recorded_locally",
    "learned_novelty_model": "not_recorded_locally",
}


@dataclass(frozen=True)
class EvolutionaryDatabaseBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class EvolutionaryDatabaseBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[EvolutionaryDatabaseBoundaryIssue]


def evolutionary_database_boundary_record() -> dict[str, Any]:
    """Return the current-run resurfacing versus durable database boundary."""

    return {
        "schema": EVOLUTIONARY_DATABASE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve's evolutionary database resurfaces previously "
            "explored programs while balancing quality, diversity, feedback, "
            "and lineage across the search process"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "implemented_runtime_evidence": {
            "accepted_history_jsonl": "current_run_append_only_stream",
            "failure_history_jsonl": "current_run_append_only_stream",
            "archive_events_jsonl": "current_run_append_only_stream",
            "archive_state_snapshot": "manifest_current_state_snapshot",
            "resurfacing_index_summary": "bounded_current_history_rank_fusion",
            "metric_resurfacing_queries": "bounded_current_run_snapshots",
            "lineage_resurfacing_queries": "bounded_current_run_snapshots",
            "descriptor_resurfacing_queries": "bounded_current_run_snapshots",
            "novelty_resurfacing_queries": "bounded_current_run_snapshots",
            "feedback_resurfacing_queries": "bounded_current_run_snapshots",
            "program_output_resurfacing_queries": "exact_current_run_output_lookup",
            "artifact_index_summary": "bounded_current_run_artifact_metadata",
            "hypothesis_index_summary": "bounded_current_run_proposal_metadata",
            "failure_index_summary": "bounded_current_run_failure_fingerprints",
        },
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has append-only current-run "
            "history streams, manifest archive snapshots, bounded rank-fusion "
            "resurfacing summaries, and defensive current-run query snapshots by "
            "metric, lineage, descriptor, novelty, feedback, artifact, hypothesis, "
            "failure, and exact program output evidence. It does not claim a "
            "durable cross-run query store, schema-versioned database migrations, "
            "semantic retrieval indexes, replayable sampling policies, cross-run "
            "failure memory, learned novelty models, or AlphaEvolve-grade "
            "evolutionary database parity."
        ),
    }


def validate_evolutionary_database_boundary(
    boundary: object | str | Path | None = None,
) -> EvolutionaryDatabaseBoundaryValidation:
    data, read_issues = _load_boundary(
        evolutionary_database_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return EvolutionaryDatabaseBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[EvolutionaryDatabaseBoundaryIssue] = []
    if data.get("schema") != EVOLUTIONARY_DATABASE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported evolutionary-database boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "evolutionary database resurfaces" not in source_claim
        or "quality, diversity, feedback, and lineage" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify evolutionary database resurfacing scope"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "evolutionary-database boundary must not claim AlphaEvolve-grade database parity"))
    implemented_count = _validate_implemented_runtime_evidence(
        data.get("implemented_runtime_evidence"), issues
    )
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    if implemented_count != 14:
        issues.append(_issue("invalid_implemented_runtime_evidence_count", "implemented runtime evidence count must be 14"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a durable cross-run query store" not in boundary_text
        or "schema-versioned database migrations" not in boundary_text
        or "AlphaEvolve-grade evolutionary database parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate current-run resurfacing from durable database parity"))
    return EvolutionaryDatabaseBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_evolutionary_database_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_evolutionary_database_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Evolutionary database boundary",
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
) -> tuple[dict[str, Any] | None, list[EvolutionaryDatabaseBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "evolutionary-database boundary must be a JSON object")]


def _validate_implemented_runtime_evidence(
    value: object,
    issues: list[EvolutionaryDatabaseBoundaryIssue],
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
    issues: list[EvolutionaryDatabaseBoundaryIssue],
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
    issues: list[EvolutionaryDatabaseBoundaryIssue],
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


def _issue(code: str, message: str) -> EvolutionaryDatabaseBoundaryIssue:
    return EvolutionaryDatabaseBoundaryIssue(code, message)
