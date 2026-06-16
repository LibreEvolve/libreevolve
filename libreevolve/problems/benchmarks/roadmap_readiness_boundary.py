from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_READINESS_BOUNDARY_SCHEMA = "libreevolve.roadmap_readiness_boundary.v1"
EXPECTED_BOUNDARY_STATUS = "weighted_todo_ledger_without_semantic_alphaevolve_readiness"
TODO_CHECK_RE = re.compile(r"^- \[( |x)\]", flags=re.MULTILINE)
EXPECTED_CATEGORIES = (
    {
        "category_id": "technical_implementation_parity",
        "weight": 50,
        "ledger_paths": ("docs/todo/code.md", "docs/todo/Completed/code.md"),
        "scope": "Code-level AlphaEvolve architecture, runtime, search, evaluator, archive, provider, benchmark, and operational-maturity implementation gaps.",
    },
    {
        "category_id": "paper_source_and_benchmark_evidence",
        "weight": 25,
        "ledger_paths": ("docs/todo/papers.md", "docs/todo/Completed/papers.md"),
        "scope": "Paper-source rows, benchmark reproduction, figure/table provenance, and publication-facing evidence gaps.",
    },
    {
        "category_id": "documentation_truthfulness_and_user_scope",
        "weight": 15,
        "ledger_paths": ("docs/todo/readme.md", "docs/todo/Completed/readme.md"),
        "scope": "README/user-facing truthfulness, runnable-scope claims, setup guidance, and documentation drift gaps.",
    },
    {
        "category_id": "roadmap_priority_and_phase_evidence",
        "weight": 10,
        "ledger_paths": ("docs/todo/roadmap.md", "docs/todo/Completed/roadmap.md"),
        "scope": "ROADMAP readiness taxonomy, priority freshness, source-span disposition, and phase-boundary evidence gaps.",
    },
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "stable_readiness_categories",
    "category_weights_sum_to_100",
    "per_category_todo_ledger_counts",
    "weighted_todo_ledger_completion",
    "raw_todo_ledger_completion",
    "semantic_requirement_mapping",
    "canonical_gap_deduplication",
    "source_span_disposition_matrix",
    "category_test_gate_mapping",
    "benchmark_reproduction_certification",
    "operational_release_readiness_gate",
)
EXPECTED_MISSING_EVIDENCE = {
    "semantic_requirement_mapping": "not_recorded_locally",
    "canonical_gap_deduplication": "not_recorded_locally",
    "source_span_disposition_matrix": "not_recorded_locally",
    "category_test_gate_mapping": "not_recorded_locally",
    "benchmark_reproduction_certification": "not_recorded_locally",
    "operational_release_readiness_gate": "not_recorded_locally",
}


@dataclass(frozen=True)
class RoadmapReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    category_count: int
    missing_evidence_count: int
    weighted_todo_ledger_completion_percent: float | None
    issues: list[RoadmapReadinessBoundaryIssue]


def roadmap_readiness_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the ROADMAP readiness taxonomy versus semantic-readiness boundary."""

    root_path = Path(root)
    categories: list[dict[str, Any]] = []
    for category in EXPECTED_CATEGORIES:
        ledger_counts = [_todo_count_record(root_path, path) for path in category["ledger_paths"]]
        active_count = sum(record["active_count"] for record in ledger_counts)
        completed_count = sum(record["completed_count"] for record in ledger_counts)
        total_count = active_count + completed_count
        raw_percent = _percent(completed_count, total_count)
        categories.append(
            {
                "category_id": category["category_id"],
                "weight": category["weight"],
                "scope": category["scope"],
                "ledger_paths": list(category["ledger_paths"]),
                "ledger_counts": ledger_counts,
                "active_count": active_count,
                "completed_count": completed_count,
                "total_count": total_count,
                "raw_todo_completion_percent": raw_percent,
                "weighted_todo_completion_points": round(
                    category["weight"] * raw_percent / 100.0, 3
                ),
            }
        )
    active_count = sum(category["active_count"] for category in categories)
    completed_count = sum(category["completed_count"] for category in categories)
    total_count = active_count + completed_count
    weighted_percent = round(
        sum(category["weighted_todo_completion_points"] for category in categories), 3
    )
    return {
        "schema": ROADMAP_READINESS_BOUNDARY_SCHEMA,
        "source_document_path": "ROADMAP.md",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "category_count": len(categories),
        "category_weight_total": sum(category["weight"] for category in categories),
        "categories": categories,
        "raw_todo_ledger_active_count": active_count,
        "raw_todo_ledger_completed_count": completed_count,
        "raw_todo_ledger_total_count": total_count,
        "raw_todo_ledger_completion_percent": _percent(completed_count, total_count),
        "weighted_todo_ledger_completion_percent": weighted_percent,
        "readiness_percent_status": "todo_ledger_only_not_semantic_alphaevolve_readiness",
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records stable ROADMAP readiness categories, weights, "
            "per-category TODO-ledger counts, raw TODO-ledger completion, and "
            "weighted TODO-ledger completion. It does not claim semantic "
            "AlphaEvolve implementation readiness, canonical underlying-gap "
            "deduplication, source-span disposition completeness, per-category "
            "test-gate coverage, benchmark reproduction certification, or "
            "operational release readiness."
        ),
    }


def validate_roadmap_readiness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_readiness_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return RoadmapReadinessBoundaryValidation(False, None, 0, 0, None, read_issues)
    assert isinstance(data, dict)
    issues: list[RoadmapReadinessBoundaryIssue] = []
    expected = roadmap_readiness_boundary_record(root)
    if data.get("schema") != ROADMAP_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP readiness boundary schema"))
    if data.get("source_document_path") != "ROADMAP.md":
        issues.append(_issue("invalid_source_document_path", "source_document_path must be ROADMAP.md"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP readiness boundary must not claim semantic AlphaEvolve readiness"))
    _compare_key(data, expected, "category_count", issues)
    _compare_key(data, expected, "category_weight_total", issues)
    _compare_key(data, expected, "categories", issues)
    _compare_key(data, expected, "raw_todo_ledger_active_count", issues)
    _compare_key(data, expected, "raw_todo_ledger_completed_count", issues)
    _compare_key(data, expected, "raw_todo_ledger_total_count", issues)
    _compare_key(data, expected, "raw_todo_ledger_completion_percent", issues)
    _compare_key(data, expected, "weighted_todo_ledger_completion_percent", issues)
    if data.get("readiness_percent_status") != "todo_ledger_only_not_semantic_alphaevolve_readiness":
        issues.append(_issue("invalid_readiness_percent_status", "readiness percent must stay scoped to TODO-ledger evidence"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim semantic AlphaEvolve implementation readiness" not in boundary_text
        or "canonical underlying-gap deduplication" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must distinguish weighted TODO completion from semantic readiness"))
    weighted = data.get("weighted_todo_ledger_completion_percent")
    return RoadmapReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        category_count=data.get("category_count") if isinstance(data.get("category_count"), int) else 0,
        missing_evidence_count=missing_count,
        weighted_todo_ledger_completion_percent=weighted if isinstance(weighted, (int, float)) else None,
        issues=issues,
    )


def render_roadmap_readiness_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_roadmap_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP readiness boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| category_count | {validation.category_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
        f"| weighted_todo_ledger_completion_percent | {validation.weighted_todo_ledger_completion_percent} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _todo_count_record(root: Path, relative_path: str) -> dict[str, Any]:
    path = root / relative_path
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        text = ""
        exists = False
    else:
        exists = True
    active_count = 0
    completed_count = 0
    for match in TODO_CHECK_RE.finditer(text):
        if match.group(1) == " ":
            active_count += 1
        else:
            completed_count += 1
    return {
        "path": relative_path,
        "exists": exists,
        "active_count": active_count,
        "completed_count": completed_count,
        "total_count": active_count + completed_count,
    }


def _percent(numerator: int, denominator: int) -> float:
    if denominator <= 0:
        return 0.0
    return round((numerator / denominator) * 100.0, 3)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[RoadmapReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP readiness boundary must be a JSON object")]


def _compare_key(
    data: dict[str, Any],
    expected: dict[str, Any],
    key: str,
    issues: list[RoadmapReadinessBoundaryIssue],
) -> None:
    if data.get(key) != expected[key]:
        issues.append(_issue(f"invalid_{key}", f"{key} drifted from current TODO ledger"))


def _validate_required_fields(
    value: object,
    issues: list[RoadmapReadinessBoundaryIssue],
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
    issues: list[RoadmapReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapReadinessBoundaryIssue:
    return RoadmapReadinessBoundaryIssue(code=code, message=message)
