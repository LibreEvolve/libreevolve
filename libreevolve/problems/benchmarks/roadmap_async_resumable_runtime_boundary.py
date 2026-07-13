from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_ASYNC_RESUMABLE_RUNTIME_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_async_resumable_runtime_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_async_resumable_runtime_matrix_without_full_replay_readiness"
)
EXPECTED_ROADMAP_HEADING = "### 6. Async and resumable runtime"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "criterion_records",
    "roadmap_section_presence",
    "async_state_inventory",
    "replay_resume_acceptance_checklist",
    "controller_queue_checkpoint_policy",
    "llm_sampler_task_policy",
    "evaluator_worker_state_policy",
    "deterministic_merge_admission_policy",
    "archive_event_replay_policy",
    "rng_lineage_provider_replay_policy",
    "budget_resume_policy",
    "environment_replay_policy",
    "resumed_trace_proof",
    "stale_readiness_detector",
)
EXPECTED_MISSING_EVIDENCE = {
    "async_state_inventory": "not_recorded_locally",
    "replay_resume_acceptance_checklist": "not_recorded_locally",
    "controller_queue_checkpoints": "not_recorded_locally",
    "llm_sampler_task_state": "not_recorded_locally",
    "evaluator_worker_pending_state": "not_recorded_locally",
    "deterministic_async_merge_admission_replay": "not_recorded_locally",
    "ordered_migration_restore_engine": "not_recorded_locally",
    "provider_output_replay": "not_recorded_locally",
    "plugin_rng_replay": "not_recorded_locally",
    "async_budget_accounting": "not_recorded_locally",
    "external_environment_replay": "not_recorded_locally",
    "end_to_end_resumed_trace_proof": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "distributed_pipeline_topology",
        "runtime_surface": "controller, LLM sampler, evaluation-node topology",
        "current_scope": "local sampler and candidate-evaluation asyncio queues with named workers and deterministic merge/admission",
        "missing_readiness": "distributed evaluators, full wait telemetry, cross-generation overlap, and pending-work checkpoints",
        "roadmap_required_phrase": "runtime.history.distributed_pipeline_topology_report",
        "current_sidecars": ("papers/distributed_pipeline_topology_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track distributed-pipeline topology evidence.",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "controller queues, LLM sampler tasks, evaluator workers",
            },
        ),
        "validation_gate": "real async topology artifacts and queue/backpressure validation",
        "readiness_status": "local_sampler_evaluator_async_topology_partial",
    },
    {
        "criterion_id": "parallel_evaluation_throughput",
        "runtime_surface": "local stage-sample workers and candidate-evaluation workers",
        "current_scope": "configured-stage sample fan-out plus bounded local async sampling and candidate evaluation",
        "missing_readiness": "compute-hour budgets, distributed nodes, cross-generation overlap, and pending-work resume",
        "roadmap_required_phrase": "runtime.history.parallel_evaluation_readiness_report",
        "current_sidecars": ("papers/parallel_evaluation_readiness_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Parallelized evaluation and asynchronous throughput.",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add unified expensive-evaluation compute budgets and resumable state.",
            },
        ),
        "validation_gate": "paper-visible worker fan-out, queue state, and cadence reports",
        "readiness_status": "local_sampler_evaluator_async_partial",
    },
    {
        "criterion_id": "controller_pending_work_resume",
        "runtime_surface": "controller queues and pending work",
        "current_scope": "terminal drained synchronous or local sampler/evaluator-async controller snapshot",
        "missing_readiness": "queued/running proposals, in-flight LLM calls, evaluator state, and mid-generation resume",
        "roadmap_required_phrase": "controller and pending-evaluation checkpoint state",
        "current_sidecars": ("papers/controller_pending_work_resume_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add async/pending-work controller resume state for archive restores.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Model migration replay and async/pending-work controller resume",
            },
        ),
        "validation_gate": "controller queue and pending-evaluation checkpoint restore",
        "readiness_status": "terminal_drained_snapshot_only",
    },
    {
        "criterion_id": "archive_event_replay",
        "runtime_surface": "MAP-Elites archive and island migration events",
        "current_scope": "cursor/full archive snapshot restore plus audit-only migration reconciliation",
        "missing_readiness": "ordered archive_events replay as a restore engine",
        "roadmap_required_phrase": "archive_event_replay_boundary.json",
        "current_sidecars": ("papers/archive_event_replay_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Replay archive event logs as an ordered migration restore engine.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "apply or explicitly model migration-event replay",
            },
        ),
        "validation_gate": "ordered migration replay or explicit modeled non-replay branch",
        "readiness_status": "snapshot_restore_with_audit_only_events",
    },
    {
        "criterion_id": "rng_lineage_replay",
        "runtime_surface": "framework RNG, deterministic ids, and lineage policy",
        "current_scope": "validated RNG snapshot and deterministic lineage-id boundary",
        "missing_readiness": "end-to-end parent/inspiration/prompt/island/MAP-Elites replay proof",
        "roadmap_required_phrase": "framework RNG snapshot can already be restored",
        "current_sidecars": (
            "papers/runtime_rng_replay_boundary.json",
            "papers/lineage_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Compose framework RNG restore with resumed-trace replay.",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Define lineage replay contract for direct UUIDs and provider boundaries.",
            },
        ),
        "validation_gate": "end-to-end resumed sampling and lineage trace",
        "readiness_status": "component_restore_without_resumed_trace",
    },
    {
        "criterion_id": "provider_plugin_nondeterminism",
        "runtime_surface": "provider outputs, plugin RNG/state, and direct custom plugins",
        "current_scope": "explicit provider-output non-replay and direct-plugin provenance boundaries",
        "missing_readiness": "provider output replay/capture, plugin-owned RNG policy, and direct constructor-value schema policy",
        "roadmap_required_phrase": "provider/plugin output replay",
        "current_sidecars": (
            "papers/provider_diagnostics_replay_boundary.json",
            "papers/roadmap_plugin_extensibility_boundary.json",
            "papers/lineage_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Add remaining full-run replay, lineage, provider, and custom-plugin",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "provider-output replay",
            },
        ),
        "validation_gate": "provider-output replay or explicit resumed-trace non-replay proof",
        "readiness_status": "nondeterminism_boundaries_without_replay",
    },
    {
        "criterion_id": "budget_resume_accounting",
        "runtime_surface": "runtime, evaluator, LLM, controller, and worker budgets",
        "current_scope": "terminal cooperative counters and ordered local async sampler/evaluator accounting",
        "missing_readiness": "async queue budgets, worker/accelerator leases, pending-work budget restore, and equal-budget runs",
        "roadmap_required_phrase": "synchronous controller-budget event replay",
        "current_sidecars": (
            "papers/llm_budget_policy_boundary.json",
            "papers/expensive_evaluation_budget_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add accelerator and worker budget stops plus budget resume state.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Connect LLM budget reports to async/pending-work resume and",
            },
        ),
        "validation_gate": "async worker budget accounting and pending-work budget resume",
        "readiness_status": "terminal_budget_replay_without_worker_lease_state",
    },
    {
        "criterion_id": "environment_replay",
        "runtime_surface": "validator, evaluator, worker, and external environment state",
        "current_scope": "local subprocess and artifact provenance boundaries",
        "missing_readiness": "external environment snapshots, accelerator/worker lease replay, and long-evaluation checkpoint restore",
        "roadmap_required_phrase": "compute-hour accounting",
        "current_sidecars": (
            "papers/expensive_evaluation_budget_boundary.json",
            "papers/release_artifact_reproducibility_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "account for per-candidate compute-hours",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "validator subprocess boundaries",
            },
        ),
        "validation_gate": "environment snapshot and worker/accelerator replay policy",
        "readiness_status": "local_environment_provenance_without_replay",
    },
    {
        "criterion_id": "resumed_trace_proof",
        "runtime_surface": "composed full-runtime resume bundle",
        "current_scope": "validated compatible bundle with full_replay_ready false",
        "missing_readiness": "end-to-end resumed trace proving prompt/archive/controller/provider continuity",
        "roadmap_required_phrase": "resumed-trace proof",
        "current_sidecars": (
            "papers/controller_pending_work_resume_boundary.json",
            "papers/runtime_rng_replay_boundary.json",
            "papers/lineage_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "no end-to-end resumed trace proving parent/inspiration",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "resumed-trace proof marked unavailable",
            },
        ),
        "validation_gate": "direct and CLI resumed trace proof across all compatible surfaces",
        "readiness_status": "compatible_bundle_without_full_replay",
    },
)


@dataclass(frozen=True)
class RoadmapAsyncResumableRuntimeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapAsyncResumableRuntimeBoundaryValidation:
    ok: bool
    boundary_status: str | None
    criterion_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapAsyncResumableRuntimeBoundaryIssue]


def roadmap_async_resumable_runtime_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP async/resumable-runtime criteria map."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    records = [_criterion_record(root_path, roadmap_text, spec) for spec in CRITERION_SPECS]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["current_sidecar_refs"]) for record in records)
    return {
        "schema": ROADMAP_ASYNC_RESUMABLE_RUNTIME_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "roadmap_heading": EXPECTED_ROADMAP_HEADING,
        "roadmap_heading_present": _contains_phrase(roadmap_text, EXPECTED_ROADMAP_HEADING),
        "criterion_count": len(records),
        "active_todo_ref_count": active_todo_ref_count,
        "sidecar_ref_count": sidecar_ref_count,
        "criterion_records": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a ROADMAP-level async/resumable-runtime "
            "criteria map for topology, parallel evaluation, controller "
            "pending work, archive-event replay, RNG/lineage replay, provider "
            "and plugin nondeterminism, budget resume, environment replay, and "
            "resumed-trace proof. It does not claim an async-state inventory, "
            "replay/resume acceptance checklist, controller queue checkpoints, "
            "LLM sampler task state, evaluator pending state, deterministic "
            "async merge/admission replay, ordered migration restore engine, "
            "provider-output replay, plugin RNG replay, async budget "
            "accounting, external environment replay, end-to-end resumed trace "
            "proof, or owner review signoff."
        ),
    }


def validate_roadmap_async_resumable_runtime_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapAsyncResumableRuntimeBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_async_resumable_runtime_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapAsyncResumableRuntimeBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = roadmap_async_resumable_runtime_boundary_record(root)
    issues: list[RoadmapAsyncResumableRuntimeBoundaryIssue] = []
    if data.get("schema") != ROADMAP_ASYNC_RESUMABLE_RUNTIME_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP async/resumable runtime boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP async/resumable runtime boundary must not claim full replay readiness"))
    for key in (
        "roadmap_heading",
        "roadmap_heading_present",
        "criterion_count",
        "active_todo_ref_count",
        "sidecar_ref_count",
        "criterion_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP/TODO inputs"))
    if data.get("roadmap_heading_present") is not True:
        issues.append(_issue("missing_roadmap_heading", "async and resumable runtime heading was not found"))
    if data.get("criterion_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_criterion_count", "criterion count changed"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim an async-state inventory" not in boundary_text
        or "controller queue checkpoints" not in boundary_text
        or "end-to-end resumed trace proof" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded criteria from async/resume readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapAsyncResumableRuntimeBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        criterion_count=data.get("criterion_count") if isinstance(data.get("criterion_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_async_resumable_runtime_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_async_resumable_runtime_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP async resumable runtime boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| criterion_count | {validation.criterion_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _criterion_record(root: Path, roadmap_text: str, spec: dict[str, Any]) -> dict[str, Any]:
    todo_refs = [_local_ref_record(root, todo_ref) for todo_ref in spec["active_todos"]]
    sidecar_refs = [{"path": path, "exists": (root / path).exists()} for path in spec["current_sidecars"]]
    return {
        "criterion_id": spec["criterion_id"],
        "runtime_surface": spec["runtime_surface"],
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "roadmap_required_phrase": spec["roadmap_required_phrase"],
        "roadmap_phrase_present": _contains_phrase(roadmap_text, spec["roadmap_required_phrase"]),
        "current_sidecar_refs": sidecar_refs,
        "active_todo_refs": todo_refs,
        "active_todo_ref_count": len(todo_refs),
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _local_ref_record(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": spec["required_phrase"],
        "required_phrase_present": _contains_phrase(text, spec["required_phrase"]),
        "exists": (root / path).exists(),
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _contains_phrase(text: str, phrase: str) -> bool:
    normalized_text = " ".join(text.casefold().split())
    normalized_phrase = " ".join(phrase.casefold().split())
    return normalized_phrase in normalized_text


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapAsyncResumableRuntimeBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP async/resumable runtime boundary must be a JSON object")]


def _validate_required_fields(value: object, issues: list[RoadmapAsyncResumableRuntimeBoundaryIssue]) -> int:
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


def _validate_missing_evidence(value: object, issues: list[RoadmapAsyncResumableRuntimeBoundaryIssue]) -> int:
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


def _issue(code: str, message: str) -> RoadmapAsyncResumableRuntimeBoundaryIssue:
    return RoadmapAsyncResumableRuntimeBoundaryIssue(code=code, message=message)
