from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_readiness_boundary import (
    roadmap_readiness_boundary_record,
)


ROADMAP_READINESS_PUBLICATION_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_readiness_publication_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_readiness_publication_gate_without_semantic_alphaevolve_certification"
)
SOURCE_READINESS_BOUNDARY_INPUT = "papers/roadmap_readiness_boundary.json"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "semantic_requirement_source_mapping",
    "canonical_gap_completion_policy",
    "per_category_evidence_gate",
    "benchmark_reproduction_certification",
    "operational_release_readiness_gate",
    "uncertainty_and_percentage_labels",
    "stale_count_detector",
    "publication_claim_boundary",
)
EXPECTED_MISSING_EVIDENCE = {
    "requirement_level_source_span_mapping": "not_recorded_locally",
    "canonical_underlying_gap_deduplication": "not_recorded_locally",
    "per_category_code_test_runtime_artifact_proof_map": "not_recorded_locally",
    "benchmark_reproduction_certification": "not_recorded_locally",
    "operational_release_readiness_gate": "not_recorded_locally",
    "readiness_uncertainty_labels": "not_recorded_locally",
    "stale_count_detector": "not_recorded_locally",
    "readiness_percentage_publication_policy": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "semantic_requirement_source_mapping",
        "search_surface": "source requirements, ROADMAP readiness categories, and AlphaEvolve requirement spans",
        "current_scope": "weighted TODO-ledger categories without requirement-level source-span proof",
        "missing_readiness": "requirement-level source-span mapping tied to readiness categories",
        "sidecars": (
            "papers/roadmap_readiness_boundary.json",
            "papers/implementation_evidence_map_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "source requirements",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "level source-span mapping",
            },
        ),
        "validation_gate": "semantic requirement to source-span readiness map",
        "readiness_status": "todo_categories_without_requirement_level_source_map",
    },
    {
        "criterion_id": "canonical_gap_completion_policy",
        "search_surface": "canonical underlying gaps, duplicate TODOs, and published completion percentages",
        "current_scope": "raw owner-ledger counts and exact duplicate-title diagnostics",
        "missing_readiness": "canonical underlying-gap deduplication before publishing completion percentages as capability progress",
        "sidecars": (
            "papers/todo_canonical_gap_boundary.json",
            "papers/todo_ledger_ownership_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "canonical underlying-gap deduplication",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "project-completion percentages",
            },
        ),
        "validation_gate": "canonical gap rollup before percent publication",
        "readiness_status": "raw_todo_counts_without_canonical_gap_completion",
    },
    {
        "criterion_id": "per_category_evidence_gate",
        "search_surface": "TODO, sidecar, code, test, and runtime-artifact evidence links",
        "current_scope": "structural sidecar refs without per-category semantic sufficiency proof",
        "missing_readiness": "per-category code/test/runtime-artifact proof map",
        "sidecars": (
            "papers/implementation_evidence_map_boundary.json",
            "papers/roadmap_claim_evidence_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "TODO/sidecar/test evidence links",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "per-category code/test/runtime-artifact proof map",
            },
        ),
        "validation_gate": "per-category evidence sufficiency map",
        "readiness_status": "structural_refs_without_evidence_sufficiency_gate",
    },
    {
        "criterion_id": "benchmark_reproduction_certification",
        "search_surface": "benchmark reproduction, paper-source metadata readiness, and representative benchmark claims",
        "current_scope": "benchmark coverage inventories and readiness sidecars without reproduction certification",
        "missing_readiness": "benchmark reproduction certification that separates paper-source metadata readiness from technical reproduction",
        "sidecars": (
            "papers/benchmark_coverage_inventory.json",
            "papers/roadmap_benchmark_portfolio_readiness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "benchmark reproduction certification",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "paper-source metadata readiness",
            },
        ),
        "validation_gate": "benchmark reproduction certification gate",
        "readiness_status": "coverage_inventory_without_reproduction_certification",
    },
    {
        "criterion_id": "operational_release_readiness_gate",
        "search_surface": "operational/release maturity, fixture-level provenance, and release artifacts",
        "current_scope": "operational readiness boundaries and reproducibility sidecars without release-readiness gate",
        "missing_readiness": "operational release-readiness gate that prevents fixture-level provenance from inflating implementation readiness",
        "sidecars": (
            "papers/roadmap_operational_readiness_boundary.json",
            "papers/release_artifact_reproducibility_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "operational release-readiness gate",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "fixture-level provenance",
            },
        ),
        "validation_gate": "operational release-readiness publication gate",
        "readiness_status": "release_sidecars_without_operational_readiness_certification",
    },
    {
        "criterion_id": "uncertainty_and_percentage_labels",
        "search_surface": "uncertainty labels, raw TODO percentages, and weighted AlphaEvolve implementation readiness",
        "current_scope": "raw and weighted TODO-ledger percentages with non-readiness status labels",
        "missing_readiness": "uncertainty labels that distinguish ledger completion from weighted AlphaEvolve implementation readiness",
        "sidecars": (
            "papers/roadmap_readiness_boundary.json",
            "papers/documentation_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "uncertainty labels",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "weighted AlphaEvolve implementation readiness",
            },
        ),
        "validation_gate": "readiness percentage uncertainty-label gate",
        "readiness_status": "todo_percentages_without_uncertainty_model",
    },
    {
        "criterion_id": "stale_count_detector",
        "search_surface": "stale TODO counts, raw TODO completion, and weighted readiness calculation",
        "current_scope": "regenerated structural sidecars without semantic stale-count detector",
        "missing_readiness": "stale-count detector that validates raw TODO completion separately from weighted AlphaEvolve readiness",
        "sidecars": (
            "papers/documentation_claim_inventory.json",
            "papers/todo_ledger_ownership_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "stale-count detector",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "raw TODO completion separately from weighted AlphaEvolve",
            },
        ),
        "validation_gate": "stale-count and percent freshness detector",
        "readiness_status": "regenerated_counts_without_stale_count_semantics",
    },
    {
        "criterion_id": "publication_claim_boundary",
        "search_surface": "README, ROADMAP, status, papers index, and user-facing project-completion percentages",
        "current_scope": "documentation that scopes TODO percentages as ledger statistics",
        "missing_readiness": "publication policy forbidding weighted TODO completion from being presented as semantic AlphaEvolve implementation parity",
        "sidecars": (
            "papers/roadmap_readiness_boundary.json",
            "papers/documentation_claim_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "semantic AlphaEvolve implementation parity",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "more than a ledger statistic",
            },
        ),
        "validation_gate": "readiness percentage publication claim boundary",
        "readiness_status": "ledger_statistic_claim_boundary_without_semantic_readiness",
    },
)


@dataclass(frozen=True)
class RoadmapReadinessPublicationBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapReadinessPublicationBoundaryValidation:
    ok: bool
    boundary_status: str | None
    publication_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapReadinessPublicationBoundaryIssue]


def roadmap_readiness_publication_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP readiness publication/certification gate."""

    root_path = Path(root)
    source_boundary = roadmap_readiness_boundary_record(root_path)
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_READINESS_PUBLICATION_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_readiness_boundary_input": SOURCE_READINESS_BOUNDARY_INPUT,
        "source_category_count": source_boundary["category_count"],
        "source_category_weight_total": source_boundary["category_weight_total"],
        "source_missing_evidence_count": len(source_boundary["missing_evidence"]),
        "source_readiness_percent_status": source_boundary["readiness_percent_status"],
        "publication_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "publication_criteria": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the publication gate for ROADMAP readiness "
            "percentages. It does not claim requirement-level source-span "
            "mapping, canonical underlying-gap deduplication, per-category "
            "code/test/runtime-artifact proof maps, benchmark reproduction "
            "certification, operational release-readiness gate, readiness "
            "uncertainty labels, stale-count detector, or a policy allowing "
            "weighted TODO completion to be published as semantic AlphaEvolve "
            "implementation parity."
        ),
    }


def validate_roadmap_readiness_publication_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapReadinessPublicationBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_readiness_publication_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapReadinessPublicationBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_readiness_publication_boundary_record(root)
    issues: list[RoadmapReadinessPublicationBoundaryIssue] = []
    if data.get("schema") != ROADMAP_READINESS_PUBLICATION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP readiness publication boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP readiness publication boundary must not claim semantic AlphaEvolve readiness"))
    for key in (
        "source_readiness_boundary_input",
        "source_category_count",
        "source_category_weight_total",
        "source_missing_evidence_count",
        "source_readiness_percent_status",
        "publication_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "publication_criteria",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP readiness inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim requirement-level source-span mapping" not in boundary_text
        or "stale-count detector" not in boundary_text
        or "semantic AlphaEvolve implementation parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness percentage publication from semantic readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapReadinessPublicationBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        publication_criterion_count=data.get("publication_criterion_count") if isinstance(data.get("publication_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_readiness_publication_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_readiness_publication_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP readiness publication boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| publication_criterion_count | {validation.publication_criterion_count} |",
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
) -> tuple[dict[str, Any] | None, list[RoadmapReadinessPublicationBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP readiness publication boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapReadinessPublicationBoundaryIssue],
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
    issues: list[RoadmapReadinessPublicationBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapReadinessPublicationBoundaryIssue:
    return RoadmapReadinessPublicationBoundaryIssue(code=code, message=message)
