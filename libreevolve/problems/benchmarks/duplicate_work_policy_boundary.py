from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DUPLICATE_WORK_POLICY_BOUNDARY_SCHEMA = (
    "libreevolve.duplicate_work_policy_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_REPORT_SCHEMA = "libreevolve.duplicate_work_policy_report.v1"
EXPECTED_BOUNDARY_STATUS = "run_local_cache_with_durable_output_signature_index"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "deterministic_workspace_hash_grouping",
    "duplicate_workspace_group_counts",
    "run_local_evaluation_cache_stores",
    "run_local_evaluation_cache_hits",
    "candidate_evaluation_cache_hit_events",
    "evaluator_budget_non_consumption_for_cache_hits",
    "candidate_metadata_cache_status",
    "durable_exact_workspace_index_export",
    "bounded_output_signature_index_export",
    "duplicate_work_cache_index_jsonl",
    "cross_run_workspace_hash_lookup",
    "durable_evaluation_cache_storage",
    "resume_spanning_cache_replay",
    "cache_invalidation_or_migration_policy",
    "stochastic_re_evaluation_policy",
    "semantic_near_duplicate_detection",
    "source_aware_cache_index",
    "alphaevolve_grade_fixed_budget_memory_claim_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "cross_run_workspace_hash_lookup": "not_recorded_locally",
    "durable_evaluation_cache_storage": "not_recorded_locally",
    "resume_spanning_cache_replay": "not_recorded_locally",
    "cache_invalidation_or_migration_policy": "not_recorded_locally",
    "stochastic_re_evaluation_policy": "not_recorded_locally",
    "semantic_near_duplicate_detection": "not_recorded_locally",
    "source_aware_cache_index": "not_recorded_locally",
    "alphaevolve_grade_fixed_budget_memory_claim_gate": "not_recorded_locally",
}


@dataclass(frozen=True)
class DuplicateWorkPolicyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class DuplicateWorkPolicyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[DuplicateWorkPolicyBoundaryIssue]


def duplicate_work_policy_boundary_record() -> dict[str, Any]:
    """Return the duplicate-work cache versus durable memory boundary."""

    return {
        "schema": DUPLICATE_WORK_POLICY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve's evolutionary database stores generated programs "
            "with scores and program outputs so previously explored programs "
            "can be resurfaced under fixed search budgets"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_report_status": "duplicate_work_policy_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests include "
            "runtime.history.duplicate_work_policy_report for deterministic "
            "workspace-hash grouping, duplicate workspace group counts, "
            "run-local evaluation cache stores and hits, cache-hit controller "
            "events, evaluator-budget non-consumption for cache hits, and "
            "candidate metadata cache status, plus durable exact-workspace "
            "rows with bounded evaluator-output signature hashes in "
            "duplicate_work_cache_index.jsonl for audit and cross-run "
            "concatenation. It does not claim cross-run workspace hash lookup, "
            "durable evaluation cache storage, resume-spanning cache replay, "
            "cache invalidation or migration policy, stochastic re-evaluation "
            "policy, semantic near-duplicate detection, source-aware cache "
            "indexes, raw output replay, or an AlphaEvolve-grade fixed-budget "
            "memory claim gate."
        ),
    }


def validate_duplicate_work_policy_boundary(
    boundary: object | str | Path | None = None,
) -> DuplicateWorkPolicyBoundaryValidation:
    data, read_issues = _load_boundary(
        duplicate_work_policy_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return DuplicateWorkPolicyBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[DuplicateWorkPolicyBoundaryIssue] = []
    if data.get("schema") != DUPLICATE_WORK_POLICY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported duplicate-work policy boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "previously explored programs" not in source_claim
        or "fixed search budgets" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify fixed-budget memory over previously explored programs"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("runtime_report_status") != "duplicate_work_policy_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to duplicate-work diagnostics"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "duplicate-work policy boundary must not claim durable memory readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "duplicate_work_cache_index.jsonl" not in boundary_text
        or "bounded evaluator-output signature hashes" not in boundary_text
        or "does not claim cross-run workspace hash lookup" not in boundary_text
        or "semantic near-duplicate detection" not in boundary_text
        or "AlphaEvolve-grade fixed-budget memory claim gate" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate run-local cache evidence from durable duplicate-work memory"))
    return DuplicateWorkPolicyBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_duplicate_work_policy_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_duplicate_work_policy_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Duplicate-work policy boundary",
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
) -> tuple[dict[str, Any] | None, list[DuplicateWorkPolicyBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "duplicate-work policy boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[DuplicateWorkPolicyBoundaryIssue],
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
    issues: list[DuplicateWorkPolicyBoundaryIssue],
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


def _issue(code: str, message: str) -> DuplicateWorkPolicyBoundaryIssue:
    return DuplicateWorkPolicyBoundaryIssue(code, message)
