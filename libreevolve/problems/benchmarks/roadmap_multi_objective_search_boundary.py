from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_MULTI_OBJECTIVE_SEARCH_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_multi_objective_search_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_multi_objective_search_matrix_without_primary_archive_readiness"
)
EXPECTED_ROADMAP_HEADING = "### 2. Strengthen multi-objective search"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "criterion_records",
    "roadmap_section_presence",
    "primary_archive_policy_matrix",
    "metric_normalization_policy",
    "pareto_frontier_replacement_policy",
    "durable_cross_run_storage_policy",
    "parent_inspiration_balance_policy",
    "descriptor_authority_policy",
    "duplicate_work_memory_policy",
    "metric_drilldown_report_policy",
    "benchmark_comparison_policy",
    "stale_readiness_detector",
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
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "paper_metric_bundles",
        "search_surface": "cross-run paper metric reports",
        "current_scope": "selected paper metric reports without persisted benchmark bundles",
        "missing_readiness": "persisted benchmark bundles and generated CSV/JSON artifacts",
        "roadmap_required_phrase": "persisted benchmark bundles and generated CSV/JSON artifacts",
        "current_sidecars": ("papers/benchmark_coverage_inventory.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "multi-objective",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "multi-objective diagnostic history bundle",
            },
        ),
        "validation_gate": "persisted benchmark bundle and artifact export evidence",
        "readiness_status": "report_rows_without_bundle_artifacts",
    },
    {
        "criterion_id": "objective_archive_policy",
        "search_surface": "archive ranking and retained objective overlays",
        "current_scope": "scalar primary MAP-Elites grid plus bounded Pareto/frontier and metric-cell retained overlays",
        "missing_readiness": "Pareto/frontier primary replacement or durable metric-specific optimization",
        "roadmap_required_phrase": "first-class multi-objective policy",
        "current_sidecars": ("papers/objective_archive_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Promote multi-objective overlays to primary archive optimization.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Pareto/frontier archive replacement and durable",
            },
        ),
        "validation_gate": "primary Pareto/frontier archive policy or equivalent tested policy",
        "readiness_status": "diagnostic_retained_overlays_only",
    },
    {
        "criterion_id": "metric_diverse_sampling_balance",
        "search_surface": "parent/inspiration sampling and metric-diverse prompt evidence",
        "current_scope": "current-run strategy counts and prompt-visible metric-niche evidence",
        "missing_readiness": "calibrated balance policy, fallback provenance, repetition tables, and equal-budget strategy comparisons",
        "roadmap_required_phrase": "runtime.history.metric_diverse_inspiration_report",
        "current_sidecars": (
            "papers/metric_diverse_prompt_boundary.json",
            "papers/sampling_balance_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "runtime.history.metric_diverse_inspiration_report",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "runtime.history.metric_diverse_inspiration_report",
            },
        ),
        "validation_gate": "calibrated parent/inspiration balance and equal-budget comparisons",
        "readiness_status": "current_run_counts_and_prompt_visibility_only",
    },
    {
        "criterion_id": "duplicate_work_memory",
        "search_surface": "workspace hashes, evaluator cache, and duplicate-work memory",
        "current_scope": "run-local exact workspace/evaluator-contract cache and no-op cache-hit events",
        "missing_readiness": "durable cross-run cache, resume replay, invalidation/migration, stochastic re-evaluation, and semantic near-duplicate detection",
        "roadmap_required_phrase": "AlphaEvolve-grade duplicate-work memory",
        "current_sidecars": ("papers/duplicate_work_policy_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Extend run-local duplicate-work cache into durable source/workspace",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Extend run-local duplicate-work cache into durable paper-visible memory.",
            },
        ),
        "validation_gate": "durable duplicate-work and near-duplicate memory",
        "readiness_status": "run_local_exact_cache_only",
    },
    {
        "criterion_id": "descriptor_authority",
        "search_surface": "MAP-Elites descriptor axes and descriptor model snapshots",
        "current_scope": "insertion-time TF-IDF/default axes or configured numeric axes with false readiness flags",
        "missing_readiness": "stable task descriptors, learned/evaluator models, descriptor training inputs, and tested rebin semantics",
        "roadmap_required_phrase": "evaluator-provided behavior descriptors",
        "current_sidecars": ("papers/map_elites_descriptor_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Promote MAP-Elites descriptor modeling beyond insertion-time TF-IDF",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Stable behavior descriptor models and archive rebin semantics.",
            },
        ),
        "validation_gate": "stable descriptor contract and rebin/snapshot compatibility",
        "readiness_status": "insertion_time_descriptor_snapshot_only",
    },
    {
        "criterion_id": "map_elites_illumination",
        "search_surface": "quality-diversity map exports and illumination evidence",
        "current_scope": "local MAP-Elites archive with source-specific illumination absence boundary",
        "missing_readiness": "explicit b(x)/f(x), P/X map exports, illumination metrics, visualizations, lineage artifacts, and paper-domain reproductions",
        "roadmap_required_phrase": "MAP-Elites illumination boundary",
        "current_sidecars": ("papers/map_elites_illumination_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "feature-descriptor schema",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "MAP-Elites illumination",
            },
        ),
        "validation_gate": "paper-visible illumination map and descriptor/performance contracts",
        "readiness_status": "local_archive_without_illumination_exports",
    },
    {
        "criterion_id": "metric_specific_drilldowns",
        "search_surface": "CLI and runtime reports for metric-specific archives",
        "current_scope": "selected-row show summaries and manifest-level metric archive summaries",
        "missing_readiness": "metric-specific CLI/report drill-downs and durable query surfaces",
        "roadmap_required_phrase": "CLI/report drill-downs for metric-specific archives",
        "current_sidecars": ("papers/objective_archive_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "ProgramDatabase.resurface_candidates(target_metric=...)",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "multi-objective diagnostic history bundle",
            },
        ),
        "validation_gate": "metric-specific drill-down commands and reports",
        "readiness_status": "selected_row_summary_only",
    },
    {
        "criterion_id": "benchmark_comparison_evidence",
        "search_surface": "multi-objective search benchmark comparisons",
        "current_scope": "boundary records without equal-budget multi-objective benchmark curves",
        "missing_readiness": "scalar-only baselines, single-metric baselines, equal-budget comparisons, and benchmark prompt-policy enforcement",
        "roadmap_required_phrase": "equal-budget comparison reports",
        "current_sidecars": (
            "papers/metric_diverse_prompt_boundary.json",
            "papers/objective_archive_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "equal-budget comparisons",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "equal-budget comparison",
            },
        ),
        "validation_gate": "equal-budget multi-objective benchmark comparisons",
        "readiness_status": "no_equal_budget_multi_objective_benchmarks",
    },
)


@dataclass(frozen=True)
class RoadmapMultiObjectiveSearchBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapMultiObjectiveSearchBoundaryValidation:
    ok: bool
    boundary_status: str | None
    criterion_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapMultiObjectiveSearchBoundaryIssue]


def roadmap_multi_objective_search_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded ROADMAP multi-objective search criteria map."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    records = [_criterion_record(root_path, roadmap_text, spec) for spec in CRITERION_SPECS]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["current_sidecar_refs"]) for record in records)
    return {
        "schema": ROADMAP_MULTI_OBJECTIVE_SEARCH_BOUNDARY_SCHEMA,
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
            "This boundary records a ROADMAP-level multi-objective search "
            "criteria map for metric bundles, objective-archive policy, "
            "metric-diverse sampling, duplicate-work memory, descriptor "
            "authority, MAP-Elites illumination, metric-specific drill-downs, "
            "and benchmark comparison evidence. It does not claim primary "
            "Pareto/frontier archive replacement, durable cross-run metric "
            "databases, calibrated parent/inspiration balance, stable behavior "
            "descriptor contracts, learned or evaluator-provided descriptor "
            "models, tested archive rebin semantics, durable duplicate-work "
            "memory, semantic near-duplicate detection, metric-specific CLI "
            "drill-downs, equal-budget multi-objective benchmarks, or owner "
            "review signoff."
        ),
    }


def validate_roadmap_multi_objective_search_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapMultiObjectiveSearchBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_multi_objective_search_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapMultiObjectiveSearchBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = roadmap_multi_objective_search_boundary_record(root)
    issues: list[RoadmapMultiObjectiveSearchBoundaryIssue] = []
    if data.get("schema") != ROADMAP_MULTI_OBJECTIVE_SEARCH_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP multi-objective search boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP multi-objective search boundary must not claim full readiness"))
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
        issues.append(_issue("missing_roadmap_heading", "multi-objective search heading was not found"))
    if data.get("criterion_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_criterion_count", "criterion count changed"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim primary Pareto/frontier archive replacement" not in boundary_text
        or "durable duplicate-work memory" not in boundary_text
        or "equal-budget multi-objective benchmarks" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded criteria from multi-objective readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapMultiObjectiveSearchBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        criterion_count=data.get("criterion_count") if isinstance(data.get("criterion_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_multi_objective_search_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_multi_objective_search_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP multi objective search boundary",
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
        "search_surface": spec["search_surface"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapMultiObjectiveSearchBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP multi-objective search boundary must be a JSON object")]


def _validate_required_fields(value: object, issues: list[RoadmapMultiObjectiveSearchBoundaryIssue]) -> int:
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


def _validate_missing_evidence(value: object, issues: list[RoadmapMultiObjectiveSearchBoundaryIssue]) -> int:
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


def _issue(code: str, message: str) -> RoadmapMultiObjectiveSearchBoundaryIssue:
    return RoadmapMultiObjectiveSearchBoundaryIssue(code=code, message=message)
