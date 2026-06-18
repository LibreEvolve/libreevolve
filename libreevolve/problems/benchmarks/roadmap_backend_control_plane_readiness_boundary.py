from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_backend_scheduling_critique_boundary import (
    roadmap_backend_scheduling_critique_boundary_record,
)


ROADMAP_BACKEND_CONTROL_PLANE_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_backend_control_plane_readiness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_backend_control_plane_readiness_matrix_without_scheduler_parity_gate"
)
SOURCE_BACKEND_BOUNDARY_INPUT = "papers/roadmap_backend_scheduling_critique_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "backend_role_capability_matrix",
    "calibrated_reward_quota_policy",
    "live_pricing_default_and_raw_replay",
    "hard_cancellation_and_resume",
    "equal_budget_scheduler_comparator",
    "gemini_lane_and_substitution",
    "critique_reviewer_isolation",
    "stale_readiness_and_owner_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "calibrated_reward_policy": "not_recorded_locally",
    "role_quota_ownership": "not_recorded_locally",
    "live_provider_pricing_default_evidence": "not_recorded_locally",
    "raw_provider_replay": "not_recorded_locally",
    "live_hard_cancellation": "not_recorded_locally",
    "equal_budget_scheduler_comparator": "not_recorded_locally",
    "first_class_gemini_lane_evidence": "not_recorded_locally",
    "async_reviewer_isolation": "not_recorded_locally",
    "stale_readiness_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_RESOLVED_EVIDENCE = {
    "backend_role_capability_matrix": (
        "recorded_in_source_backend_scheduling_critique_boundary"
    ),
    "critique_control_checklist": (
        "recorded_in_source_backend_scheduling_critique_boundary"
    ),
}


CRITERION_SPECS = (
    {
        "criterion_id": "backend_role_capability_matrix",
        "control_plane_surface": "backend roles, provider lanes, and scheduler eligibility",
        "current_scope": "explicit backend-role capability matrix derived from nine ROADMAP backend/critique tracks with local sidecar and TODO links",
        "missing_readiness": "control-plane capability gate proving those role/lane capabilities are scheduler-ready, owner-reviewed, and parity-safe",
        "sidecars": (
            "papers/roadmap_backend_scheduling_critique_boundary.json",
            "papers/provider_diagnostics_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "backend-role capability matrix",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "role and provider lane",
            },
        ),
        "validation_gate": "backend-role capability matrix to scheduler-readiness gate",
        "readiness_status": "track_matrix_without_control_plane_capability_gate",
    },
    {
        "criterion_id": "calibrated_reward_quota_policy",
        "control_plane_surface": "role-scoped scheduler rewards, budgets, quotas, and backend choice",
        "current_scope": "heuristic reward accounting and role-scoped budget maps",
        "missing_readiness": "calibrated reward policy and explicit role quota ownership for each backend lane",
        "sidecars": (
            "papers/llm_role_scheduler_boundary.json",
            "papers/llm_budget_policy_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "calibrated reward policy",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "role quota ownership",
            },
        ),
        "validation_gate": "calibrated reward and quota ownership policy",
        "readiness_status": "heuristic_rewards_without_owned_role_quotas",
    },
    {
        "criterion_id": "live_pricing_default_and_raw_replay",
        "control_plane_surface": "provider telemetry, pricing defaults, and replayable request/response evidence",
        "current_scope": "configured token-cost estimates and bounded scalar diagnostics",
        "missing_readiness": "live provider pricing/default evidence plus raw provider replay policy",
        "sidecars": (
            "papers/provider_pricing_boundary.json",
            "papers/provider_diagnostics_replay_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "live provider pricing/default evidence",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "raw provider replay",
            },
        ),
        "validation_gate": "live pricing/default and raw replay evidence",
        "readiness_status": "configured_pricing_without_live_default_or_raw_replay",
    },
    {
        "criterion_id": "hard_cancellation_and_resume",
        "control_plane_surface": "provider timeout, hard cancellation, scheduler state, and resumed runs",
        "current_scope": "policy-only cancellation evidence and bounded pending-work resume surfaces",
        "missing_readiness": "live hard cancellation artifacts and resume semantics that preserve scheduler/provider state",
        "sidecars": (
            "papers/provider_cancellation_boundary.json",
            "papers/controller_pending_work_resume_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "live hard cancellation",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "resume semantics",
            },
        ),
        "validation_gate": "live cancellation and resumed scheduler trace evidence",
        "readiness_status": "policy_cancellation_without_live_hard_cancel_or_resume_gate",
    },
    {
        "criterion_id": "equal_budget_scheduler_comparator",
        "control_plane_surface": "fast/strong model mix, proposal budgets, and scheduler comparisons",
        "current_scope": "throughput/depth metadata, sample-efficiency boundaries, and no equal-budget comparator",
        "missing_readiness": "equal-budget scheduler comparator proving backend policy effects separately from call caps",
        "sidecars": (
            "papers/fast_strong_model_mix_boundary.json",
            "papers/sample_efficiency_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "equal-budget scheduler comparator",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "equal-budget comparator evidence",
            },
        ),
        "validation_gate": "equal-budget scheduler comparison report",
        "readiness_status": "metadata_and_curves_without_equal_budget_comparator",
    },
    {
        "criterion_id": "gemini_lane_and_substitution",
        "control_plane_surface": "Gemini provider lane, substitution rules, and self-training loop claims",
        "current_scope": "Gemini absence/parity boundaries and no first-class Gemini lane evidence",
        "missing_readiness": "first-class Gemini lane evidence and explicit Gemini substitution status",
        "sidecars": (
            "papers/gemini_provider_parity_boundary.json",
            "papers/gemini_self_training_loop_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "first-class Gemini lane evidence",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "Gemini substitution status",
            },
        ),
        "validation_gate": "Gemini lane and substitution policy evidence",
        "readiness_status": "absence_boundary_without_first_class_gemini_lane",
    },
    {
        "criterion_id": "critique_reviewer_isolation",
        "control_plane_surface": "critique reviewer pools, reviewer overlap, and critique-to-revision attribution",
        "current_scope": "structural critique-control checklist for synchronous first/last-valid reviewer aggregation without async isolation",
        "missing_readiness": "async reviewer isolation evidence and reviewer readiness gate",
        "sidecars": (
            "papers/critique_reviewer_pool_boundary.json",
            "papers/incorrect_suggestion_audit_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "critique-control checklist",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "critique/reviewer isolation",
            },
        ),
        "validation_gate": "critique-control checklist to reviewer isolation report",
        "readiness_status": "synchronous_aggregation_without_reviewer_isolation",
    },
    {
        "criterion_id": "stale_readiness_and_owner_signoff",
        "control_plane_surface": "README, papers, ROADMAP, generated inventories, and owner readiness claims",
        "current_scope": "bounded inventories and TODO ownership sidecars without owner signoff",
        "missing_readiness": "stale-readiness detector and owner signoff before backend-scheduler parity claims",
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
class RoadmapBackendControlPlaneReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapBackendControlPlaneReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readiness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapBackendControlPlaneReadinessBoundaryIssue]


def roadmap_backend_control_plane_readiness_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP backend control-plane readiness matrix."""

    root_path = Path(root)
    source_boundary = roadmap_backend_scheduling_critique_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    claim_guard = [_claim_guard_record(record) for record in records]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_BACKEND_CONTROL_PLANE_READINESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_backend_boundary_input": SOURCE_BACKEND_BOUNDARY_INPUT,
        "source_track_count": source_boundary["track_count"],
        "source_active_todo_ref_count": source_boundary["active_todo_ref_count"],
        "source_sidecar_ref_count": source_boundary["sidecar_ref_count"],
        "readiness_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "readiness_criteria": records,
        "backend_control_plane_claim_guard": claim_guard,
        "backend_control_plane_claim_guard_count": len(claim_guard),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "resolved_evidence": dict(EXPECTED_RESOLVED_EVIDENCE),
        "claim_boundary": (
            "This boundary records backend control-plane readiness criteria tied "
            "to the bounded backend scheduling and critique matrix, including "
            "the recorded backend-role capability matrix from that source "
            "boundary, the recorded critique-control checklist, and a claim "
            "guard for each control-plane surface. It does not claim "
            "calibrated reward policy, role quota ownership, live provider "
            "pricing/default evidence, raw provider replay, live hard "
            "cancellation, equal-budget scheduler comparator, first-class "
            "Gemini lane evidence, async reviewer isolation, stale-readiness "
            "detector, owner review signoff, or full backend scheduler parity."
        ),
    }


def validate_roadmap_backend_control_plane_readiness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapBackendControlPlaneReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        (
            roadmap_backend_control_plane_readiness_boundary_record(root)
            if boundary is None
            else boundary
        )
    )
    if read_issues:
        return RoadmapBackendControlPlaneReadinessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_backend_control_plane_readiness_boundary_record(root)
    issues: list[RoadmapBackendControlPlaneReadinessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_BACKEND_CONTROL_PLANE_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP backend control-plane readiness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP backend control-plane readiness boundary must not claim scheduler parity readiness"))
    for key in (
        "source_backend_boundary_input",
        "source_track_count",
        "source_active_todo_ref_count",
        "source_sidecar_ref_count",
        "readiness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "readiness_criteria",
        "backend_control_plane_claim_guard",
        "backend_control_plane_claim_guard_count",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP backend control-plane inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    _validate_resolved_evidence(data.get("resolved_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "recorded backend-role capability matrix" not in boundary_text
        or "recorded critique-control checklist" not in boundary_text
        or "claim guard for each control-plane surface" not in boundary_text
        or "full backend scheduler parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness matrix from backend scheduler parity"))
    if data.get("backend_control_plane_claim_guard_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_backend_control_plane_claim_guard_count", "backend control-plane claim guard count changed"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapBackendControlPlaneReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readiness_criterion_count=data.get("readiness_criterion_count") if isinstance(data.get("readiness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_backend_control_plane_readiness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_backend_control_plane_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP backend control-plane readiness boundary",
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
        "control_plane_surface": spec["control_plane_surface"],
        "current_scope": spec["current_scope"],
        "missing_readiness": spec["missing_readiness"],
        "sidecar_refs": [_sidecar_ref(root, path) for path in spec["sidecars"]],
        "active_todo_refs": [
            _active_todo_ref(root, todo) for todo in spec["active_todos"]
        ],
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _claim_guard_record(record: dict[str, Any]) -> dict[str, str]:
    return {
        "criterion_id": record["criterion_id"],
        "control_plane_surface": record["control_plane_surface"],
        "allowed_current_claim": record["current_scope"],
        "missing_before_scheduler_parity_claim": record["missing_readiness"],
        "validation_gate": record["validation_gate"],
        "readiness_status": record["readiness_status"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapBackendControlPlaneReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP backend control-plane readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapBackendControlPlaneReadinessBoundaryIssue],
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
    issues: list[RoadmapBackendControlPlaneReadinessBoundaryIssue],
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


def _validate_resolved_evidence(
    value: object,
    issues: list[RoadmapBackendControlPlaneReadinessBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_resolved_evidence", "resolved_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_RESOLVED_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_resolved_evidence_key", f"resolved_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_resolved_evidence_key", f"resolved_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_RESOLVED_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_resolved_evidence_{key}", f"resolved_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(
    code: str,
    message: str,
) -> RoadmapBackendControlPlaneReadinessBoundaryIssue:
    return RoadmapBackendControlPlaneReadinessBoundaryIssue(code=code, message=message)
