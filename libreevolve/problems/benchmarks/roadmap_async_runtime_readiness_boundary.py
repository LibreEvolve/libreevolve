from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_async_resumable_runtime_boundary import (
    roadmap_async_resumable_runtime_boundary_record,
)


ROADMAP_ASYNC_RUNTIME_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_async_runtime_readiness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_async_runtime_readiness_matrix_without_full_replay_gate"
)
SOURCE_ASYNC_BOUNDARY_INPUT = "papers/roadmap_async_resumable_runtime_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "async_state_inventory",
    "replay_resume_acceptance_checklist",
    "controller_sampler_task_checkpoints",
    "evaluator_pending_work_and_merge_order",
    "archive_migration_restore_engine",
    "provider_plugin_replay_policy",
    "async_budget_environment_replay",
    "stale_readiness_and_owner_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "async_state_inventory": "not_recorded_locally",
    "replay_resume_acceptance_checklist": "not_recorded_locally",
    "controller_queue_checkpoint": "not_recorded_locally",
    "llm_sampler_task_state": "not_recorded_locally",
    "evaluator_pending_work_state": "not_recorded_locally",
    "deterministic_async_merge_admission_replay": "not_recorded_locally",
    "ordered_migration_restore_engine": "not_recorded_locally",
    "provider_output_replay": "not_recorded_locally",
    "plugin_rng_replay": "not_recorded_locally",
    "async_budget_accounting": "not_recorded_locally",
    "external_environment_replay": "not_recorded_locally",
    "end_to_end_resumed_trace_proof": "not_recorded_locally",
    "stale_readiness_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "async_state_inventory",
        "runtime_surface": "controller, sampler, evaluator, archive, budget, provider, plugin, and environment state",
        "current_scope": "nine async/resumable boundary criteria with sidecar and TODO links",
        "missing_readiness": "one inventory classifying every state surface as checkpointed, replayed, reconstructed, or explicitly non-replayable",
        "sidecars": (
            "papers/roadmap_async_resumable_runtime_boundary.json",
            "papers/distributed_pipeline_topology_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "async-state inventory",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "controller queues",
            },
        ),
        "validation_gate": "async state inventory",
        "readiness_status": "criterion_map_without_state_inventory",
    },
    {
        "criterion_id": "replay_resume_acceptance_checklist",
        "runtime_surface": "full run resume bundle and acceptance gates",
        "current_scope": "component restore reports and full_replay_ready false boundary",
        "missing_readiness": "replay-resume acceptance checklist tied to a passing end-to-end resumed trace proof",
        "sidecars": (
            "papers/controller_pending_work_resume_boundary.json",
            "papers/runtime_rng_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "replay-resume acceptance checklist",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "end-to-end resumed trace proof",
            },
        ),
        "validation_gate": "replay-resume acceptance checklist and trace proof",
        "readiness_status": "component_restore_without_acceptance_checklist",
    },
    {
        "criterion_id": "controller_sampler_task_checkpoints",
        "runtime_surface": "controller queues and LLM sampler task state",
        "current_scope": "terminal drained synchronous or local sampler/evaluator-async controller snapshot with worker-owned sampler calls",
        "missing_readiness": "controller queue checkpoints and in-flight LLM sampler task state",
        "sidecars": (
            "papers/controller_pending_work_resume_boundary.json",
            "papers/distributed_pipeline_topology_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "controller queue checkpoint",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "LLM sampler task state",
            },
        ),
        "validation_gate": "controller queue and sampler task checkpoint restore",
        "readiness_status": "terminal_snapshot_without_inflight_task_state",
    },
    {
        "criterion_id": "evaluator_pending_work_and_merge_order",
        "runtime_surface": "evaluator workers, pending work, and admission order",
        "current_scope": "bounded local candidate-evaluation queue with deterministic submission-order merge/admission",
        "missing_readiness": "evaluator pending-work checkpoint/restore and deterministic merge/admission replay",
        "sidecars": (
            "papers/parallel_evaluation_readiness_boundary.json",
            "papers/controller_pending_work_resume_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "evaluator pending-work restore",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "deterministic merge/admission order",
            },
        ),
        "validation_gate": "evaluator pending-work and deterministic admission replay",
        "readiness_status": "local_async_admission_without_pending_work_replay",
    },
    {
        "criterion_id": "archive_migration_restore_engine",
        "runtime_surface": "archive events, island migration, and restore ordering",
        "current_scope": "archive snapshots plus audit-only migration reconciliation",
        "missing_readiness": "ordered archive/event replay and ordered migration restore engine",
        "sidecars": (
            "papers/archive_event_replay_boundary.json",
            "papers/lineage_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "archive/event replay",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "ordered migration restore engine",
            },
        ),
        "validation_gate": "ordered archive and migration restore engine",
        "readiness_status": "snapshot_restore_without_ordered_event_engine",
    },
    {
        "criterion_id": "provider_plugin_replay_policy",
        "runtime_surface": "provider outputs, plugin RNG, plugin state, and direct plugin provenance",
        "current_scope": "explicit provider-output non-replay and plugin provenance boundaries",
        "missing_readiness": "provider-output replay and plugin RNG replay policy",
        "sidecars": (
            "papers/provider_diagnostics_replay_boundary.json",
            "papers/roadmap_plugin_extensibility_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "provider-output replay",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "plugin RNG replay",
            },
        ),
        "validation_gate": "provider-output and plugin RNG replay policy",
        "readiness_status": "nondeterminism_boundary_without_replay_policy",
    },
    {
        "criterion_id": "async_budget_environment_replay",
        "runtime_surface": "async budgets, worker leases, validators, and external environments",
        "current_scope": "ordered local async sampler/evaluator budget counters, controller budget-event replay, and local subprocess provenance",
        "missing_readiness": "async budget accounting and external environment replay",
        "sidecars": (
            "papers/llm_budget_policy_boundary.json",
            "papers/expensive_evaluation_budget_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "worker/compute-hour budget",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "external environment replay",
            },
        ),
        "validation_gate": "async budget accounting and environment replay",
        "readiness_status": "serialized_async_budget_and_local_environment_only",
    },
    {
        "criterion_id": "stale_readiness_and_owner_signoff",
        "runtime_surface": "README, ROADMAP, papers, generated inventories, and owner readiness claims",
        "current_scope": "bounded inventories and TODO ownership sidecars without owner signoff",
        "missing_readiness": "stale-readiness detector and owner signoff before async/resumable parity claims",
        "sidecars": (
            "papers/documentation_claim_inventory.json",
            "papers/todo_ledger_ownership_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "stale-readiness detector",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "owner signoff",
            },
        ),
        "validation_gate": "stale-readiness detector and owner signoff",
        "readiness_status": "inventory_without_readiness_signoff",
    },
)


@dataclass(frozen=True)
class RoadmapAsyncRuntimeReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapAsyncRuntimeReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readiness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapAsyncRuntimeReadinessBoundaryIssue]


def roadmap_async_runtime_readiness_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP async runtime readiness matrix."""

    root_path = Path(root)
    source_boundary = roadmap_async_resumable_runtime_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_ASYNC_RUNTIME_READINESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_async_boundary_input": SOURCE_ASYNC_BOUNDARY_INPUT,
        "source_criterion_count": source_boundary["criterion_count"],
        "source_active_todo_ref_count": source_boundary["active_todo_ref_count"],
        "source_sidecar_ref_count": source_boundary["sidecar_ref_count"],
        "readiness_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "readiness_criteria": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records async runtime readiness criteria tied to "
            "the bounded async/resumable-runtime matrix. It does not claim an "
            "async-state inventory, replay-resume acceptance checklist, "
            "controller queue checkpoint, LLM sampler task state, evaluator "
            "pending-work checkpoint/restore, deterministic async merge/"
            "admission replay, "
            "ordered migration restore engine, provider-output replay, plugin "
            "RNG replay, async budget accounting, external environment replay, "
            "end-to-end resumed trace proof, stale-readiness detector, or "
            "owner review signoff."
        ),
    }


def validate_roadmap_async_runtime_readiness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapAsyncRuntimeReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_async_runtime_readiness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapAsyncRuntimeReadinessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_async_runtime_readiness_boundary_record(root)
    issues: list[RoadmapAsyncRuntimeReadinessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_ASYNC_RUNTIME_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP async runtime readiness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP async runtime readiness boundary must not claim full replay readiness"))
    for key in (
        "source_async_boundary_input",
        "source_criterion_count",
        "source_active_todo_ref_count",
        "source_sidecar_ref_count",
        "readiness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "readiness_criteria",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP async runtime inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim an async-state inventory" not in boundary_text
        or "replay-resume acceptance checklist" not in boundary_text
        or "end-to-end resumed trace proof" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness matrix from async replay parity"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapAsyncRuntimeReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readiness_criterion_count=data.get("readiness_criterion_count") if isinstance(data.get("readiness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_async_runtime_readiness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_async_runtime_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP async runtime readiness boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| readiness_criterion_count | {validation.readiness_criterion_count} |",
        f"| sidecar_ref_count | {validation.sidecar_ref_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _criterion_record(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    return {
        "criterion_id": spec["criterion_id"],
        "runtime_surface": spec["runtime_surface"],
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "sidecar_refs": [_sidecar_ref(root, path) for path in spec["sidecars"]],
        "active_todo_refs": [
            _active_todo_ref(root, todo) for todo in spec["active_todos"]
        ],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _sidecar_ref(root: Path, path: str) -> dict[str, Any]:
    return {"path": path, "exists": (root / path).exists()}


def _active_todo_ref(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    required_phrase = spec["required_phrase"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": required_phrase,
        "required_phrase_present": _contains_phrase(text, required_phrase),
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
) -> tuple[dict[str, Any] | None, list[RoadmapAsyncRuntimeReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP async runtime readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapAsyncRuntimeReadinessBoundaryIssue],
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
    issues: list[RoadmapAsyncRuntimeReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapAsyncRuntimeReadinessBoundaryIssue:
    return RoadmapAsyncRuntimeReadinessBoundaryIssue(code=code, message=message)
