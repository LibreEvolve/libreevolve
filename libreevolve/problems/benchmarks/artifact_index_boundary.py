from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ARTIFACT_INDEX_BOUNDARY_SCHEMA = "libreevolve.artifact_index_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_ARTIFACT_INDEX_SCHEMA = "libreevolve.artifact_index.v1"
EXPECTED_BOUNDARY_STATUS = "bounded_artifact_metadata_not_full_content_search"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "evaluator_artifact_metadata_capture",
    "artifact_path_records",
    "artifact_hash_records",
    "artifact_redaction_status",
    "skipped_artifact_records",
    "stage_attempt_sample_metadata",
    "bounded_content_excerpts",
    "runtime_artifact_index",
    "valid_artifact_program_resurfacing_source",
    "artifact_count_and_byte_summaries",
    "durable_artifact_query_table",
    "full_artifact_content_search",
    "semantic_artifact_similarity_search",
    "cross_run_artifact_index",
    "artifact_content_ranking_policy",
    "replayable_artifact_sampling_policy",
)
EXPECTED_MISSING_EVIDENCE = {
    "durable_artifact_query_table": "not_recorded_locally",
    "full_artifact_content_search": "not_recorded_locally",
    "semantic_artifact_similarity_search": "not_recorded_locally",
    "cross_run_artifact_index": "not_recorded_locally",
    "artifact_content_ranking_policy": "not_recorded_locally",
    "replayable_artifact_sampling_policy": "not_recorded_locally",
}


@dataclass(frozen=True)
class ArtifactIndexBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ArtifactIndexBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ArtifactIndexBoundaryIssue]


def artifact_index_boundary_record() -> dict[str, Any]:
    """Return the bounded artifact metadata versus full-content search boundary."""

    return {
        "schema": ARTIFACT_INDEX_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve stores generated solutions with attached evaluation "
            "results and artifacts, so artifact evidence should be reusable "
            "through the evolutionary database"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "artifact_index_schema": EXPECTED_ARTIFACT_INDEX_SCHEMA,
        "runtime_report_status": "bounded_current_run_artifact_index_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve can capture evaluator "
            "artifact metadata, artifact paths and hashes, redaction status, "
            "skipped-artifact diagnostics, stage/sample/attempt metadata, "
            "bounded content excerpts, runtime.history.artifact_index records, "
            "artifact-bearing current-run resurfacing sources, and artifact "
            "count/byte summaries. It does not claim durable artifact query "
            "tables, full artifact-content search, semantic artifact "
            "similarity search, cross-run artifact indexes, artifact-content "
            "ranking policy, or replayable artifact-driven sampling policy."
        ),
    }


def validate_artifact_index_boundary(
    boundary: object | str | Path | None = None,
) -> ArtifactIndexBoundaryValidation:
    data, read_issues = _load_boundary(
        artifact_index_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ArtifactIndexBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ArtifactIndexBoundaryIssue] = []
    if data.get("schema") != ARTIFACT_INDEX_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported artifact-index boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "attached evaluation results and artifacts" not in source_claim
        or "evolutionary database" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify reusable artifact evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("artifact_index_schema") != EXPECTED_ARTIFACT_INDEX_SCHEMA:
        issues.append(_issue("invalid_artifact_index_schema", f"artifact_index_schema must be {EXPECTED_ARTIFACT_INDEX_SCHEMA}"))
    if data.get("runtime_report_status") != "bounded_current_run_artifact_index_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to bounded current-run artifact evidence"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "artifact-index boundary must not claim durable full-content artifact search readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim durable artifact query tables" not in boundary_text
        or "full artifact-content search" not in boundary_text
        or "semantic artifact similarity search" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded artifact metadata from durable full-content search"))
    return ArtifactIndexBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_artifact_index_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_artifact_index_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Artifact index boundary",
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
) -> tuple[dict[str, Any] | None, list[ArtifactIndexBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "artifact-index boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ArtifactIndexBoundaryIssue],
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
    issues: list[ArtifactIndexBoundaryIssue],
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


def _issue(code: str, message: str) -> ArtifactIndexBoundaryIssue:
    return ArtifactIndexBoundaryIssue(code, message)
