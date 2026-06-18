from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_BACKEND_SCHEDULING_CRITIQUE_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_backend_scheduling_critique_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_backend_scheduling_critique_matrix_with_role_capability_inventory"
)
EXPECTED_ROADMAP_HEADING = "### 7. Backend scheduling and critique"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "track_records",
    "roadmap_section_presence",
    "backend_role_capability_matrix",
    "critique_control_checklist",
    "reward_assumption_policy",
    "role_budget_quota_policy",
    "provider_pricing_default_rate_evidence",
    "diagnostics_replay_policy",
    "cancellation_resume_policy",
    "equal_budget_comparator_evidence",
    "gemini_substitution_policy",
    "stale_readiness_detector",
)
EXPECTED_MISSING_EVIDENCE = {
    "calibrated_reward_policy": "not_recorded_locally",
    "role_quota_ownership": "not_recorded_locally",
    "live_provider_pricing_defaults": "not_recorded_locally",
    "raw_provider_replay": "not_recorded_locally",
    "live_hard_cancellation": "not_recorded_locally",
    "equal_budget_scheduler_comparators": "not_recorded_locally",
    "first_class_gemini_lanes": "not_recorded_locally",
    "async_reviewer_isolation": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}
EXPECTED_RESOLVED_EVIDENCE = {
    "backend_role_capability_matrix": (
        "recorded_from_roadmap_backend_scheduling_track_records"
    ),
    "critique_control_checklist": (
        "recorded_from_critique_reviewer_pool_track_boundary"
    ),
}


TRACK_SPECS = (
    {
        "track_id": "heuristic_ucb_rewards",
        "role_or_lane": "global backend selection",
        "selection_policy": "heuristic UCB-style routing",
        "reward_assumptions": "bounded improvement telemetry without canonical finite-time regret proof",
        "budget_quota_ownership": "global logical/provider budget counters",
        "pricing_default_rate_evidence": "not applicable to reward theorem scope",
        "diagnostics_replay_support": "selected-index and reward evidence boundary only",
        "cancellation_behavior": "inherits provider cancellation policy",
        "resume_semantics": "scheduler state can be snapshotted/restored, not theorem replay",
        "equal_budget_evidence": "not recorded",
        "critique_reviewer_isolation": "not applicable",
        "gemini_substitution_status": "not applicable",
        "roadmap_required_phrase": "Normalize/document UCB rewards against bounded assumptions",
        "current_sidecars": (
            "papers/ucb1_boundary.json",
            "papers/llm_role_scheduler_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Implement canonical UCB1 finite-time scheduler evidence beyond the",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Implement UCB1 finite-time bandit paper evidence beyond the source",
            },
        ),
        "validation_gate": "canonical reward assumptions and regret evidence before UCB1 claims",
        "readiness_status": "heuristic_not_canonical_ucb1",
    },
    {
        "track_id": "role_scoped_routing",
        "role_or_lane": "mutation, critique, feedback, and meta-prompt roles",
        "selection_policy": "opt-in role-scoped scheduler state and backend eligibility",
        "reward_assumptions": "local reward-accounted role selection without calibrated role rewards",
        "budget_quota_ownership": "role budget maps exist without experiment-owned quota policy",
        "pricing_default_rate_evidence": "configured estimates only",
        "diagnostics_replay_support": "role scheduler audit state and runtime snapshots",
        "cancellation_behavior": "role failure policy can quarantine in-run pairs",
        "resume_semantics": "restorable scheduler failure-policy state without cross-run proof",
        "equal_budget_evidence": "not recorded",
        "critique_reviewer_isolation": "reviewer roles can be routed but not isolated as independent reviewers",
        "gemini_substitution_status": "not first-class",
        "roadmap_required_phrase": "role-scoped backend eligibility",
        "current_sidecars": (
            "papers/llm_role_scheduler_boundary.json",
            "papers/llm_budget_policy_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Promote role-scoped LLM routing from shared-bandit audit evidence",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "role-scoped scheduler state",
            },
        ),
        "validation_gate": "calibrated per-role reward, quota, and budget reports",
        "readiness_status": "local_role_scoped_audit_boundary",
    },
    {
        "track_id": "provider_diagnostics_pricing",
        "role_or_lane": "provider call telemetry",
        "selection_policy": "provider diagnostics do not select by themselves",
        "reward_assumptions": "not applicable",
        "budget_quota_ownership": "provider attempts, tokens, configured cost, and latency stops",
        "pricing_default_rate_evidence": "configured token-cost estimates only",
        "diagnostics_replay_support": "bounded scalar diagnostics without raw payload replay",
        "cancellation_behavior": "request timeout telemetry only",
        "resume_semantics": "controller budget-event replay for provider budget counters",
        "equal_budget_evidence": "not recorded",
        "critique_reviewer_isolation": "role labels retained in telemetry",
        "gemini_substitution_status": "generic provider labels only",
        "roadmap_required_phrase": "raw provider diagnostics, live provider pricing/default-rate capture",
        "current_sidecars": (
            "papers/provider_pricing_boundary.json",
            "papers/provider_diagnostics_replay_boundary.json",
            "papers/llm_stochastic_reproducibility_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "live provider pricing/default-rate capture beyond configured",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "provider diagnostics, and scheduler telemetry",
            },
        ),
        "validation_gate": "live pricing/default evidence and raw replay policy",
        "readiness_status": "configured_pricing_and_bounded_diagnostics_only",
    },
    {
        "track_id": "provider_cancellation_quarantine",
        "role_or_lane": "mutation, critique, feedback, and meta-prompt provider calls",
        "selection_policy": "retry/fallback/quarantine audit policy",
        "reward_assumptions": "zero-reward penalties for exhausted reward-accounted failures",
        "budget_quota_ownership": "role-scoped budget actions in cancellation policy",
        "pricing_default_rate_evidence": "inherits configured-cost telemetry",
        "diagnostics_replay_support": "policy observations without raw provider replay",
        "cancellation_behavior": "policy/audit evidence, not live SDK hard cancellation",
        "resume_semantics": "restorable scheduler failure state without cross-run quarantine proof",
        "equal_budget_evidence": "not recorded",
        "critique_reviewer_isolation": "reviewer roles can be labeled but not isolated",
        "gemini_substitution_status": "not applicable",
        "roadmap_required_phrase": "live provider SDK cancellation",
        "current_sidecars": ("papers/provider_cancellation_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Complete live hard provider cancellation and timeout-stop policy.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "not live provider SDK hard cancellation",
            },
        ),
        "validation_gate": "live hard cancellation and timeout-stop artifacts",
        "readiness_status": "policy_audit_without_live_hard_cancel",
    },
    {
        "track_id": "fast_strong_model_mix",
        "role_or_lane": "fast breadth and strong depth lanes",
        "selection_policy": "throughput_depth metadata tests and heuristic routing",
        "reward_assumptions": "no lane-specific calibrated reward model",
        "budget_quota_ownership": "no lane quota schedule",
        "pricing_default_rate_evidence": "configured estimates only",
        "diagnostics_replay_support": "metadata trace boundary",
        "cancellation_behavior": "inherits provider policy",
        "resume_semantics": "no resume replay experiment report",
        "equal_budget_evidence": "not recorded",
        "critique_reviewer_isolation": "not applicable",
        "gemini_substitution_status": "not first-class Flash/Pro lanes",
        "roadmap_required_phrase": "fast/strong model-mix reports",
        "current_sidecars": ("papers/fast_strong_model_mix_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Validate fast/strong model-mix scheduling beyond local metadata tests.",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "fast/strong model-mix scheduling",
            },
        ),
        "validation_gate": "fixed-budget lane traces and equal-budget comparisons",
        "readiness_status": "metadata_trace_without_lane_policy",
    },
    {
        "track_id": "sample_efficiency",
        "role_or_lane": "LLM proposal budget",
        "selection_policy": "single-run proposal lifecycle counts",
        "reward_assumptions": "target hit and replicate statistics absent",
        "budget_quota_ownership": "logical/provider/cost/latency budgets recorded",
        "pricing_default_rate_evidence": "configured estimates only",
        "diagnostics_replay_support": "bounded cumulative best-score curve",
        "cancellation_behavior": "inherits provider policy",
        "resume_semantics": "budget replay exists without benchmark-level sample curves",
        "equal_budget_evidence": "not recorded",
        "critique_reviewer_isolation": "not applicable",
        "gemini_substitution_status": "not separated from sample-efficiency reports",
        "roadmap_required_phrase": "proposal-count curves, target-hit evidence",
        "current_sidecars": ("papers/sample_efficiency_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add sample-efficiency reporting for AlphaEvolve-scale LLM proposal",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track AlphaEvolve sample-efficiency evidence separately from call caps.",
            },
        ),
        "validation_gate": "target-hit sample curves, replicates, and matched budgets",
        "readiness_status": "single_run_counts_without_benchmark_curves",
    },
    {
        "track_id": "repeated_sampling_baseline",
        "role_or_lane": "base-model repeated-sampling comparator",
        "selection_policy": "absence boundary only",
        "reward_assumptions": "controlled base-model comparator absent",
        "budget_quota_ownership": "equal LLM-call budget not enforced by comparator runner",
        "pricing_default_rate_evidence": "configured estimates only",
        "diagnostics_replay_support": "observed sample counts linked to missing controls",
        "cancellation_behavior": "not applicable",
        "resume_semantics": "not recorded",
        "equal_budget_evidence": "not recorded",
        "critique_reviewer_isolation": "disabled critique proof absent",
        "gemini_substitution_status": "not applicable",
        "roadmap_required_phrase": "repeated-sampling boundary report",
        "current_sidecars": ("papers/repeated_sampling_baseline_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add repeated-sampling baseline reports for test-time-compute uplift",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track repeated-sampling baselines for test-time-compute uplift claims.",
            },
        ),
        "validation_gate": "controlled equal-budget repeated-sampling runner",
        "readiness_status": "comparator_absence_boundary",
    },
    {
        "track_id": "gemini_provider_parity",
        "role_or_lane": "Gemini Flash/Pro provider lanes",
        "selection_policy": "custom-backend detection only",
        "reward_assumptions": "not applicable",
        "budget_quota_ownership": "no Flash/Pro quota or lane integration",
        "pricing_default_rate_evidence": "no Gemini account/model pricing evidence",
        "diagnostics_replay_support": "no Gemini-native usage/default/error telemetry",
        "cancellation_behavior": "no Gemini-native cancellation evidence",
        "resume_semantics": "not recorded",
        "equal_budget_evidence": "not recorded",
        "critique_reviewer_isolation": "not applicable",
        "gemini_substitution_status": "first-class provider absent",
        "roadmap_required_phrase": "first-class Google/Gemini adapter",
        "current_sidecars": ("papers/gemini_provider_parity_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add first-class Google/Gemini backend parity for AlphaEvolve model-mix",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track Google/Gemini provider-parity evidence separately from generic",
            },
        ),
        "validation_gate": "Gemini adapter or explicit substitution contract",
        "readiness_status": "custom_backend_detection_without_gemini_provider",
    },
    {
        "track_id": "critique_reviewer_pool",
        "role_or_lane": "critique reviewer roles",
        "selection_policy": "synchronous first-valid or last-valid mutation replacement",
        "reward_assumptions": "no calibrated reviewer score-to-selection policy",
        "budget_quota_ownership": "role budget routing possible without reviewer quota policy",
        "pricing_default_rate_evidence": "configured estimates only",
        "diagnostics_replay_support": "inline reviewer telemetry boundary",
        "cancellation_behavior": "inherits provider timeout policy",
        "resume_semantics": "reviewer-specific replay absent",
        "equal_budget_evidence": "no no-reviewer comparator",
        "critique_reviewer_isolation": "no async overlap or independent reviewer isolation",
        "gemini_substitution_status": "not applicable",
        "roadmap_required_phrase": "synchronous configurable critique reviewer pools",
        "current_sidecars": ("papers/critique_reviewer_pool_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Extend critique reviewer pools beyond synchronous first/last-valid",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Validate critique reviewer pools beyond synchronous replacement filters.",
            },
        ),
        "validation_gate": "async reviewer overlap, calibrated scoring, isolation, and no-reviewer ablations",
        "readiness_status": "synchronous_replacement_filter_boundary",
    },
)


@dataclass(frozen=True)
class RoadmapBackendSchedulingCritiqueBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapBackendSchedulingCritiqueBoundaryValidation:
    ok: bool
    boundary_status: str | None
    track_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapBackendSchedulingCritiqueBoundaryIssue]


def roadmap_backend_scheduling_critique_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP backend-scheduling and critique matrix."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    records = [_track_record(root_path, roadmap_text, spec) for spec in TRACK_SPECS]
    backend_role_capability_matrix = [
        _backend_role_capability_record(record) for record in records
    ]
    critique_control_checklist = _critique_control_checklist(records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["current_sidecar_refs"]) for record in records)
    return {
        "schema": ROADMAP_BACKEND_SCHEDULING_CRITIQUE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "roadmap_heading": EXPECTED_ROADMAP_HEADING,
        "roadmap_heading_present": _contains_phrase(roadmap_text, EXPECTED_ROADMAP_HEADING),
        "track_count": len(records),
        "active_todo_ref_count": active_todo_ref_count,
        "sidecar_ref_count": sidecar_ref_count,
        "track_records": records,
        "backend_role_capability_matrix": backend_role_capability_matrix,
        "backend_role_capability_matrix_count": len(backend_role_capability_matrix),
        "critique_control_checklist": critique_control_checklist,
        "critique_control_checklist_count": len(critique_control_checklist),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "resolved_evidence": dict(EXPECTED_RESOLVED_EVIDENCE),
        "claim_boundary": (
            "This boundary records a ROADMAP-level backend-scheduling and "
            "critique matrix across heuristic UCB rewards, role-scoped routing, "
            "provider diagnostics/pricing, cancellation/quarantine, fast/strong "
            "model mix, sample efficiency, repeated sampling, Gemini parity, "
            "and critique reviewer pools, with an explicit backend-role "
            "capability inventory and critique-control checklist derived from "
            "those tracks. It does not claim calibrated reward policy, role "
            "quota ownership, live provider pricing/defaults, raw provider "
            "replay, live hard cancellation, equal-budget scheduler "
            "comparators, first-class Gemini lanes, async reviewer isolation, "
            "stale-readiness detector, or owner review signoff."
        ),
    }


def validate_roadmap_backend_scheduling_critique_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapBackendSchedulingCritiqueBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_backend_scheduling_critique_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapBackendSchedulingCritiqueBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_backend_scheduling_critique_boundary_record(root)
    issues: list[RoadmapBackendSchedulingCritiqueBoundaryIssue] = []
    if data.get("schema") != ROADMAP_BACKEND_SCHEDULING_CRITIQUE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP backend scheduling/critique boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP backend scheduling/critique boundary must not claim control-plane readiness"))
    for key in (
        "roadmap_heading",
        "roadmap_heading_present",
        "track_count",
        "active_todo_ref_count",
        "sidecar_ref_count",
        "track_records",
        "backend_role_capability_matrix",
        "backend_role_capability_matrix_count",
        "critique_control_checklist",
        "critique_control_checklist_count",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP/TODO inputs"))
    if data.get("roadmap_heading_present") is not True:
        issues.append(_issue("missing_roadmap_heading", "backend scheduling and critique heading was not found"))
    if data.get("track_count") != len(TRACK_SPECS):
        issues.append(_issue("invalid_track_count", "backend scheduling/critique track count changed"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    _validate_resolved_evidence(data.get("resolved_evidence"), issues)
    if data.get("backend_role_capability_matrix_count") != len(TRACK_SPECS):
        issues.append(_issue("invalid_backend_role_capability_matrix_count", "backend role capability matrix count changed"))
    if data.get("critique_control_checklist_count") != 8:
        issues.append(_issue("invalid_critique_control_checklist_count", "critique control checklist count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "backend-role capability inventory" not in boundary_text
        or "critique-control checklist" not in boundary_text
        or "first-class Gemini lanes" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded matrix from control-plane readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapBackendSchedulingCritiqueBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        track_count=data.get("track_count") if isinstance(data.get("track_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_backend_scheduling_critique_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_backend_scheduling_critique_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP backend scheduling and critique boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| track_count | {validation.track_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _track_record(root: Path, roadmap_text: str, spec: dict[str, Any]) -> dict[str, Any]:
    todo_refs = [_local_ref_record(root, todo_ref) for todo_ref in spec["active_todos"]]
    sidecar_refs = [{"path": path, "exists": (root / path).exists()} for path in spec["current_sidecars"]]
    return {
        "track_id": spec["track_id"],
        "role_or_lane": spec["role_or_lane"],
        "selection_policy": spec["selection_policy"],
        "reward_assumptions": spec["reward_assumptions"],
        "budget_quota_ownership": spec["budget_quota_ownership"],
        "pricing_default_rate_evidence": spec["pricing_default_rate_evidence"],
        "diagnostics_replay_support": spec["diagnostics_replay_support"],
        "cancellation_behavior": spec["cancellation_behavior"],
        "resume_semantics": spec["resume_semantics"],
        "equal_budget_evidence": spec["equal_budget_evidence"],
        "critique_reviewer_isolation": spec["critique_reviewer_isolation"],
        "gemini_substitution_status": spec["gemini_substitution_status"],
        "roadmap_required_phrase": spec["roadmap_required_phrase"],
        "roadmap_phrase_present": _contains_phrase(roadmap_text, spec["roadmap_required_phrase"]),
        "current_sidecar_refs": sidecar_refs,
        "active_todo_refs": todo_refs,
        "active_todo_ref_count": len(todo_refs),
        "validation_gate": spec["validation_gate"],
        "readiness_status": spec["readiness_status"],
    }


def _backend_role_capability_record(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "track_id": record["track_id"],
        "role_or_lane": record["role_or_lane"],
        "selection_policy": record["selection_policy"],
        "reward_assumptions": record["reward_assumptions"],
        "budget_quota_ownership": record["budget_quota_ownership"],
        "pricing_default_rate_evidence": record["pricing_default_rate_evidence"],
        "diagnostics_replay_support": record["diagnostics_replay_support"],
        "cancellation_behavior": record["cancellation_behavior"],
        "resume_semantics": record["resume_semantics"],
        "equal_budget_evidence": record["equal_budget_evidence"],
        "critique_reviewer_isolation": record["critique_reviewer_isolation"],
        "gemini_substitution_status": record["gemini_substitution_status"],
        "validation_gate": record["validation_gate"],
        "readiness_status": record["readiness_status"],
    }


def _critique_control_checklist(records: list[dict[str, Any]]) -> list[dict[str, str]]:
    critique_record = next(
        record for record in records if record["track_id"] == "critique_reviewer_pool"
    )
    return [
        {
            "check_id": "reviewer_pool_selection_policy",
            "current_evidence": critique_record["selection_policy"],
            "readiness_gap": "async reviewer overlap and calibrated score-to-selection policy absent",
        },
        {
            "check_id": "reviewer_reward_policy",
            "current_evidence": critique_record["reward_assumptions"],
            "readiness_gap": "calibrated reviewer reliability and score calibration absent",
        },
        {
            "check_id": "reviewer_budget_quota_policy",
            "current_evidence": critique_record["budget_quota_ownership"],
            "readiness_gap": "reviewer-owned quota policy absent",
        },
        {
            "check_id": "reviewer_diagnostics_replay",
            "current_evidence": critique_record["diagnostics_replay_support"],
            "readiness_gap": "reviewer-specific raw replay and reliability report absent",
        },
        {
            "check_id": "reviewer_cancellation_timeout",
            "current_evidence": critique_record["cancellation_behavior"],
            "readiness_gap": "external reviewer timeout artifacts and hard cancellation absent",
        },
        {
            "check_id": "reviewer_resume_semantics",
            "current_evidence": critique_record["resume_semantics"],
            "readiness_gap": "reviewer-specific replay and resumed trace proof absent",
        },
        {
            "check_id": "no_reviewer_comparator",
            "current_evidence": critique_record["equal_budget_evidence"],
            "readiness_gap": "equal-budget no-reviewer comparison absent",
        },
        {
            "check_id": "reviewer_isolation",
            "current_evidence": critique_record["critique_reviewer_isolation"],
            "readiness_gap": critique_record["validation_gate"],
        },
    ]


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
) -> tuple[dict[str, Any] | None, list[RoadmapBackendSchedulingCritiqueBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP backend scheduling/critique boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapBackendSchedulingCritiqueBoundaryIssue],
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
    issues: list[RoadmapBackendSchedulingCritiqueBoundaryIssue],
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
    issues: list[RoadmapBackendSchedulingCritiqueBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapBackendSchedulingCritiqueBoundaryIssue:
    return RoadmapBackendSchedulingCritiqueBoundaryIssue(code=code, message=message)
