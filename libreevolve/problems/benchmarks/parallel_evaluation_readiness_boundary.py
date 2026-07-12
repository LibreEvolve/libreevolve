from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PARALLEL_EVALUATION_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_parallel_evaluation_readiness_boundary.v1"
)
PARALLEL_EVALUATION_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.parallel_evaluation_readiness_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "local_candidate_async_evaluation_partial"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "local_stage_sample_worker_fanout",
    "observed_wall_clock_compression",
    "distributed_pipeline_topology_ref",
    "hundred_compute_hour_candidate_budget",
    "generation_cadence_under_slow_feedback",
    "per_candidate_compute_hour_budget",
    "concurrent_llm_sampler_queue",
    "candidate_level_async_evaluation_queue",
    "queue_capacity_backpressure_policy",
    "distributed_evaluator_worker_nodes",
    "deterministic_async_result_merge_order",
    "concurrency_safe_shared_state_mutation",
    "randomized_initialization_shard_identity",
    "mutation_chain_depth_impact_under_slow_feedback",
    "pending_evaluation_resume_state",
    "equal_budget_parallelism_report_ref",
)
EXPECTED_IMPLEMENTED_EVIDENCE = {
    "local_stage_sample_worker_fanout": "recorded_when_configured",
    "candidate_level_async_evaluation_queue": "bounded_local_asyncio_queue",
    "queue_capacity_backpressure_policy": "recorded_in_controller_report",
    "local_candidate_evaluator_worker_nodes": "named_asyncio_workers",
    "out_of_order_completion_telemetry": "recorded_per_candidate_task",
    "deterministic_async_result_merge_order": "submission_order",
    "shared_state_mutation_policy": "serial_controller_commit_after_merge",
}
EXPECTED_MISSING_EVIDENCE = {
    "hundred_compute_hour_candidate_budget_records": "not_recorded_locally",
    "generation_cadence_under_slow_feedback_report": "not_recorded_locally",
    "per_candidate_compute_hour_budget_records": "not_recorded_locally",
    "concurrent_llm_sampler_queue": "not_recorded_locally",
    "distributed_evaluator_worker_nodes": "not_recorded_locally",
    "randomized_initialization_shard_identity": "not_recorded_locally",
    "mutation_chain_depth_impact_under_slow_feedback": "not_recorded_locally",
    "pending_evaluation_resume_state": "not_recorded_locally",
    "equal_budget_parallelism_report_links": "not_recorded_locally",
    "cross_generation_proposal_evaluation_overlap": "not_recorded_locally",
}


@dataclass(frozen=True)
class ParallelEvaluationReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ParallelEvaluationReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ParallelEvaluationReadinessBoundaryIssue]


def parallel_evaluation_readiness_boundary_record() -> dict[str, Any]:
    """Return the current AlphaEvolve parallel-evaluation boundary."""

    return {
        "schema": PARALLEL_EVALUATION_READINESS_BOUNDARY_SCHEMA,
        "runtime_report_schema": PARALLEL_EVALUATION_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve parallelizes expensive candidate evaluation and runs "
            "an asynchronous controller, LLM sampler, and evaluator-node "
            "pipeline optimized for throughput; Section 2.4 describes "
            "spending on the order of 100 compute-hours on a new solution "
            "while parallelism preserves generation cadence for consecutive "
            "mutations"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "parallel_evaluation_readiness_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "implemented_evidence": dict(EXPECTED_IMPLEMENTED_EVIDENCE),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has runtime reporting for "
            "configured local stage sample-worker fan-out, observed wall-clock "
            "compression, and distributed-pipeline topology linkage. Opt-in "
            "candidate evaluation now uses a bounded local asyncio queue, named "
            "workers, queue backpressure telemetry, out-of-order completion "
            "records, deterministic submission-order result merge and archive "
            "admission, exact in-flight duplicate coalescing, and serial shared-"
            "state commit. It does not claim AlphaEvolve-style 100-compute-hour "
            "candidate budgets, generation-cadence preservation under slow "
            "feedback, per-candidate compute-hour budgets, concurrent LLM "
            "sampler queues, distributed evaluator nodes, randomized "
            "initialization shards, cross-generation proposal/evaluation "
            "overlap, mutation-chain depth impact under slow feedback, pending-"
            "work resume, or equal-budget parallelism reports."
        ),
    }


def validate_parallel_evaluation_readiness_boundary(
    boundary: object | str | Path | None = None,
) -> ParallelEvaluationReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        parallel_evaluation_readiness_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ParallelEvaluationReadinessBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ParallelEvaluationReadinessBoundaryIssue] = []
    if data.get("schema") != PARALLEL_EVALUATION_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported parallel-evaluation boundary schema"))
    if data.get("runtime_report_schema") != PARALLEL_EVALUATION_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify parallel-evaluation readiness reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "asynchronous controller" not in source_claim
        or "100 compute-hours" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve asynchronous throughput"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "parallel_evaluation_readiness_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to parallel-evaluation readiness reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "parallel-evaluation boundary must not claim AlphaEvolve throughput readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    _validate_evidence_map(
        "implemented_evidence",
        data.get("implemented_evidence"),
        EXPECTED_IMPLEMENTED_EVIDENCE,
        issues,
    )
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim" not in boundary_text
        or "bounded local asyncio queue" not in boundary_text
        or "deterministic submission-order result merge" not in boundary_text
        or "concurrent LLM sampler queues" not in boundary_text
        or "cross-generation proposal/evaluation overlap" not in boundary_text
        or "pending-work resume" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim AlphaEvolve parallel-evaluation parity"))
    return ParallelEvaluationReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_parallel_evaluation_readiness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_parallel_evaluation_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve parallel-evaluation readiness boundary",
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
) -> tuple[dict[str, Any] | None, list[ParallelEvaluationReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "parallel-evaluation boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ParallelEvaluationReadinessBoundaryIssue],
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
    issues: list[ParallelEvaluationReadinessBoundaryIssue],
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


def _validate_evidence_map(
    field: str,
    value: object,
    expected: dict[str, str],
    issues: list[ParallelEvaluationReadinessBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue(f"invalid_{field}", f"{field} must be an object"))
        return
    if value != expected:
        issues.append(
            _issue(
                f"invalid_{field}",
                f"{field} must match the validated local async evidence map",
            )
        )


def _issue(code: str, message: str) -> ParallelEvaluationReadinessBoundaryIssue:
    return ParallelEvaluationReadinessBoundaryIssue(code, message)
