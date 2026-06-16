from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_multi_objective_search_boundary import (
    roadmap_multi_objective_search_boundary_record,
)


ROADMAP_MULTI_OBJECTIVE_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_multi_objective_readiness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_multi_objective_readiness_matrix_without_primary_archive_gate"
)
SOURCE_MULTI_OBJECTIVE_BOUNDARY_INPUT = "papers/roadmap_multi_objective_search_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "primary_archive_policy_matrix",
    "durable_metric_storage_policy",
    "sampling_balance_and_metric_policy",
    "descriptor_authority_and_rebin_semantics",
    "duplicate_work_memory_semantics",
    "metric_drilldown_and_cli_policy",
    "equal_budget_benchmark_evidence",
    "stale_readiness_and_owner_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "primary_pareto_frontier_archive_replacement": "not_recorded_locally",
    "durable_cross_run_metric_database": "not_recorded_locally",
    "calibrated_parent_inspiration_balance": "not_recorded_locally",
    "stable_behavior_descriptor_contracts": "not_recorded_locally",
    "learned_or_evaluator_descriptor_models": "not_recorded_locally",
    "tested_archive_rebin_semantics": "not_recorded_locally",
    "durable_duplicate_work_memory": "not_recorded_locally",
    "semantic_near_duplicate_detection": "not_recorded_locally",
    "metric_specific_cli_drilldowns": "not_recorded_locally",
    "equal_budget_multi_objective_benchmarks": "not_recorded_locally",
    "stale_readiness_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "primary_archive_policy_matrix",
        "search_surface": "primary archive policy, Pareto/frontier replacement, and metric-cell retention",
        "current_scope": "scalar-primary MAP-Elites grid with bounded Pareto/frontier and metric-cell overlays",
        "missing_readiness": "archive-policy matrix proving primary Pareto/frontier archive replacement or an equivalent tested multi-objective policy",
        "sidecars": (
            "papers/roadmap_multi_objective_search_boundary.json",
            "papers/objective_archive_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "archive-policy matrix",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "primary Pareto/frontier archive replacement",
            },
        ),
        "validation_gate": "primary archive policy matrix",
        "readiness_status": "diagnostic_overlays_without_primary_archive_gate",
    },
    {
        "criterion_id": "durable_metric_storage_policy",
        "search_surface": "cross-run metric database, metric bundles, and persisted benchmark artifacts",
        "current_scope": "cross-run paper metric reports and selected summary artifacts",
        "missing_readiness": "durable cross-run metric database and persisted metric-specific optimization records",
        "sidecars": (
            "papers/benchmark_coverage_inventory.json",
            "papers/objective_archive_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "durable cross-run metric database",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "durable metric-specific optimization",
            },
        ),
        "validation_gate": "durable cross-run metric storage policy",
        "readiness_status": "reports_without_durable_metric_database",
    },
    {
        "criterion_id": "sampling_balance_and_metric_policy",
        "search_surface": "metric-diverse inspiration, parent selection, and prompt-policy comparisons",
        "current_scope": "current-run strategy counts and prompt-visible metric-niche evidence",
        "missing_readiness": "calibrated parent/inspiration balance and equal-budget prompt-policy evidence",
        "sidecars": (
            "papers/metric_diverse_prompt_boundary.json",
            "papers/sampling_balance_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "calibrated parent/inspiration balance",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "benchmark prompt-policy evidence",
            },
        ),
        "validation_gate": "calibrated sampling balance and prompt-policy benchmark",
        "readiness_status": "current_run_sampling_reports_without_calibration",
    },
    {
        "criterion_id": "descriptor_authority_and_rebin_semantics",
        "search_surface": "behavior descriptors, descriptor models, MAP-Elites axes, and archive rebinning",
        "current_scope": "insertion-time TF-IDF/default axes or configured numeric axes with false readiness flags",
        "missing_readiness": "stable behavior descriptor contracts, learned/evaluator descriptor models, and tested archive rebin semantics",
        "sidecars": (
            "papers/map_elites_descriptor_boundary.json",
            "papers/map_elites_illumination_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "stable behavior descriptor contracts",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "tested archive rebin semantics",
            },
        ),
        "validation_gate": "stable descriptor authority and rebin semantics",
        "readiness_status": "descriptor_snapshots_without_authority_gate",
    },
    {
        "criterion_id": "duplicate_work_memory_semantics",
        "search_surface": "duplicate-work cache, resurfacing indexes, semantic near-duplicates, and resume replay",
        "current_scope": "run-local exact-workspace evaluator cache and no-op cache-hit events",
        "missing_readiness": "durable duplicate-work memory and semantic near-duplicate detection",
        "sidecars": (
            "papers/duplicate_work_policy_boundary.json",
            "papers/objective_archive_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "durable duplicate-work memory",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "semantic near-duplicate detection",
            },
        ),
        "validation_gate": "durable duplicate-work memory with semantic near-duplicate policy",
        "readiness_status": "run_local_exact_cache_without_durable_memory",
    },
    {
        "criterion_id": "metric_drilldown_and_cli_policy",
        "search_surface": "metric-specific CLI drill-downs, selected-row summaries, and durable query surfaces",
        "current_scope": "selected-row show summaries and manifest-level metric archive summaries",
        "missing_readiness": "metric-specific CLI drill-downs and durable query/report surfaces",
        "sidecars": (
            "papers/objective_archive_boundary.json",
            "papers/benchmark_coverage_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "metric-specific CLI drill-downs",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "metric-specific reports",
            },
        ),
        "validation_gate": "metric-specific CLI drill-down and report policy",
        "readiness_status": "selected_row_summary_without_drilldowns",
    },
    {
        "criterion_id": "equal_budget_benchmark_evidence",
        "search_surface": "scalar baselines, single-metric baselines, and equal-budget multi-objective benchmarks",
        "current_scope": "boundary records without equal-budget multi-objective benchmark curves",
        "missing_readiness": "equal-budget multi-objective benchmarks with scalar-only and single-metric baselines",
        "sidecars": (
            "papers/metric_diverse_prompt_boundary.json",
            "papers/benchmark_coverage_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "equal-budget multi-objective benchmarks",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "full multi-objective search parity",
            },
        ),
        "validation_gate": "equal-budget multi-objective benchmark comparison",
        "readiness_status": "no_equal_budget_multi_objective_benchmarks",
    },
    {
        "criterion_id": "stale_readiness_and_owner_signoff",
        "search_surface": "README, ROADMAP, papers, archive reports, runtime metadata, and owner readiness claims",
        "current_scope": "bounded inventories and TODO ownership sidecars without owner signoff",
        "missing_readiness": "stale-readiness detector and owner signoff before multi-objective parity claims",
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
                "required_phrase": "owner review signoff",
            },
        ),
        "validation_gate": "stale-readiness detector and owner signoff",
        "readiness_status": "inventory_without_readiness_signoff",
    },
)


@dataclass(frozen=True)
class RoadmapMultiObjectiveReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapMultiObjectiveReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readiness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapMultiObjectiveReadinessBoundaryIssue]


def roadmap_multi_objective_readiness_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP multi-objective readiness matrix."""

    root_path = Path(root)
    source_boundary = roadmap_multi_objective_search_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_MULTI_OBJECTIVE_READINESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_multi_objective_boundary_input": SOURCE_MULTI_OBJECTIVE_BOUNDARY_INPUT,
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
            "This boundary records multi-objective readiness criteria tied to "
            "the bounded multi-objective search matrix. It does not claim "
            "primary Pareto/frontier archive replacement, durable cross-run "
            "metric database, calibrated parent/inspiration balance, stable "
            "behavior descriptor contracts, learned or evaluator-provided "
            "descriptor models, tested archive rebin semantics, durable "
            "duplicate-work memory, semantic near-duplicate detection, "
            "metric-specific CLI drill-downs, equal-budget multi-objective "
            "benchmarks, stale-readiness detector, or owner review signoff."
        ),
    }


def validate_roadmap_multi_objective_readiness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapMultiObjectiveReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_multi_objective_readiness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapMultiObjectiveReadinessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_multi_objective_readiness_boundary_record(root)
    issues: list[RoadmapMultiObjectiveReadinessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_MULTI_OBJECTIVE_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP multi-objective readiness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP multi-objective readiness boundary must not claim multi-objective readiness"))
    for key in (
        "source_multi_objective_boundary_input",
        "source_criterion_count",
        "source_active_todo_ref_count",
        "source_sidecar_ref_count",
        "readiness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "readiness_criteria",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP multi-objective inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim primary Pareto/frontier archive replacement" not in boundary_text
        or "equal-budget multi-objective benchmarks" not in boundary_text
        or "stale-readiness detector" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness matrix from multi-objective parity"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapMultiObjectiveReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readiness_criterion_count=data.get("readiness_criterion_count") if isinstance(data.get("readiness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_multi_objective_readiness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_multi_objective_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP multi objective readiness boundary",
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
        "search_surface": spec["search_surface"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapMultiObjectiveReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP multi-objective readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapMultiObjectiveReadinessBoundaryIssue],
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
    issues: list[RoadmapMultiObjectiveReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapMultiObjectiveReadinessBoundaryIssue:
    return RoadmapMultiObjectiveReadinessBoundaryIssue(code=code, message=message)
