from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROADMAP_REPRESENTATIVE_BENCHMARK_PORTFOLIO_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_representative_benchmark_portfolio_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_benchmark_portfolio_map_without_representative_readiness_gate"
)
EXPECTED_ROADMAP_HEADING = "### 9. Representative benchmarks"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "portfolio_family_records",
    "roadmap_section_presence",
    "domain_coverage_matrix",
    "benchmark_admission_checklist",
    "validator_strength_labels",
    "baseline_sota_target_evidence",
    "repeated_run_evidence",
    "anti_gaming_certification",
    "artifact_output_contracts",
    "stale_coverage_detector",
)
EXPECTED_MISSING_EVIDENCE = {
    "domain_coverage_matrix": "not_recorded_locally",
    "benchmark_admission_checklist": "not_recorded_locally",
    "repeated_seed_run_matrix": "not_recorded_locally",
    "anti_gaming_certification": "not_recorded_locally",
    "sota_baseline_citations": "not_recorded_locally",
    "portfolio_balance_score": "not_recorded_locally",
    "ci_portfolio_freshness_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


PORTFOLIO_FAMILY_SPECS = (
    {
        "family_id": "sorting_network_rediscovery",
        "domain": "algorithm_discovery",
        "validator_strength": "exhaustive_boolean_inputs_candidate",
        "roadmap_required_phrase": "bounded sorting-network rediscovery fixture",
        "baseline_sota_target": "19 comparators for 8 inputs and 25 comparators for 9 inputs",
        "current_sidecars": ("papers/sorting_network_rediscovery_boundary.json",),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add a rigorous sorting-network rediscovery benchmark fixture.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Add paper-facing sorting-network rediscovery evidence as a realistic",
            },
        ),
        "readiness_status": "executable_candidate_without_repeated_run_certification",
    },
    {
        "family_id": "matrix_tensor_suite",
        "domain": "linear_algebra",
        "validator_strength": "schema_and_artifact_boundary_without_full_suite_execution",
        "roadmap_required_phrase": "matrix-multiplication variants",
        "baseline_sota_target": "Appendix A target ranks and hit fractions",
        "current_sidecars": (
            "papers/appendix_a_matrix_subset_scope_artifacts.json",
            "papers/matrix_suite_publication_artifacts.json",
            "papers/matrix_cascade_run_runtime_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Generate suite matrix tensor artifacts and per-seed hit-rate reports.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Generate AlphaEvolve-suite matrix-result publication artifacts.",
            },
        ),
        "readiness_status": "paper_evidence_boundary_without_full_tensor_suite_reports",
    },
    {
        "family_id": "constructive_math_geometry",
        "domain": "constructive_math",
        "validator_strength": "registry_and_boundary_without_construction_exports",
        "roadmap_required_phrase": "kissing/circle packing extensions",
        "baseline_sota_target": "Appendix B circle, rectangle, kissing, and related construction targets",
        "current_sidecars": (
            "papers/math_outcome_boundary.json",
            "papers/math_starting_construction_boundary.json",
            "papers/example_benchmark_scope.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Add Appendix B.12-B.13 circle/rectangle sum-of-radii provenance.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Track Appendix B.12-B.13 circle/rectangle sum-of-radii evidence.",
            },
        ),
        "readiness_status": "smoke_and_registry_boundary_without_colab_equivalent_exports",
    },
    {
        "family_id": "systems_kernel_scheduling",
        "domain": "systems_engineering",
        "validator_strength": "report_schema_without_real_heldout_fixture_runs",
        "roadmap_required_phrase": "compiler/hardware/systems/kernel/scheduling",
        "baseline_sota_target": "Section 3.3 scheduling, kernel, RTL, and compiler outcome claims",
        "current_sidecars": (
            "papers/systems_result_readiness_boundary.json",
            "papers/figure6_scheduling_exhibit_boundary.json",
            "papers/kernel_tiling_shape_corpus_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Connect real systems fixtures to held-out and reference-correctness",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Connect systems-style benchmarks to held-out and reference-correctness",
            },
        ),
        "readiness_status": "schema_ready_without_real_systems_fixture_runs",
    },
    {
        "family_id": "smoke_fixture_guardrail",
        "domain": "portfolio_governance",
        "validator_strength": "scope_registry_and_manifest_gate",
        "roadmap_required_phrase": "Separate smoke examples from benchmark fixtures",
        "baseline_sota_target": "not applicable; prevents smoke fixtures from being counted as representative results",
        "current_sidecars": (
            "papers/example_benchmark_scope.json",
            "papers/benchmark_fixture_readiness_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Connect benchmark-grade fixtures to hardening and scope reports.",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "Harden benchmark implementations beyond smoke-example fidelity.",
            },
        ),
        "readiness_status": "guardrail_present_without_representative_benchmark_admission",
    },
)


@dataclass(frozen=True)
class RoadmapRepresentativeBenchmarkPortfolioBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapRepresentativeBenchmarkPortfolioBoundaryValidation:
    ok: bool
    boundary_status: str | None
    family_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapRepresentativeBenchmarkPortfolioBoundaryIssue]


def roadmap_representative_benchmark_portfolio_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP representative-benchmark portfolio map."""

    root_path = Path(root)
    roadmap_text = _read_text(root_path / "ROADMAP.md")
    records = [
        _portfolio_family_record(root_path, roadmap_text, spec)
        for spec in PORTFOLIO_FAMILY_SPECS
    ]
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    sidecar_ref_count = sum(len(record["current_sidecar_refs"]) for record in records)
    return {
        "schema": ROADMAP_REPRESENTATIVE_BENCHMARK_PORTFOLIO_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "roadmap_heading": EXPECTED_ROADMAP_HEADING,
        "roadmap_heading_present": _contains_phrase(roadmap_text, EXPECTED_ROADMAP_HEADING),
        "family_count": len(records),
        "active_todo_ref_count": active_todo_ref_count,
        "sidecar_ref_count": sidecar_ref_count,
        "portfolio_family_records": records,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a ROADMAP-level representative-benchmark "
            "portfolio map across sorting networks, matrix tensor targets, "
            "constructive-math geometry, systems/kernel/scheduling work, and "
            "smoke-fixture guardrails. It does not claim a domain-coverage "
            "matrix, benchmark admission checklist, repeated-seed run matrix, "
            "anti-gaming certification, SOTA/baseline citation sufficiency, "
            "portfolio balance score, CI freshness gate, or owner review "
            "signoff."
        ),
    }


def validate_roadmap_representative_benchmark_portfolio_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapRepresentativeBenchmarkPortfolioBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_representative_benchmark_portfolio_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapRepresentativeBenchmarkPortfolioBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_representative_benchmark_portfolio_boundary_record(root)
    issues: list[RoadmapRepresentativeBenchmarkPortfolioBoundaryIssue] = []
    if data.get("schema") != ROADMAP_REPRESENTATIVE_BENCHMARK_PORTFOLIO_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP representative benchmark portfolio boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP representative benchmark portfolio boundary must not claim readiness"))
    for key in (
        "roadmap_heading",
        "roadmap_heading_present",
        "family_count",
        "active_todo_ref_count",
        "sidecar_ref_count",
        "portfolio_family_records",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP/TODO inputs"))
    if data.get("roadmap_heading_present") is not True:
        issues.append(_issue("missing_roadmap_heading", "representative benchmarks heading was not found"))
    if data.get("family_count") != len(PORTFOLIO_FAMILY_SPECS):
        issues.append(_issue("invalid_family_count", "portfolio family count changed"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a domain-coverage matrix" not in boundary_text
        or "benchmark admission checklist" not in boundary_text
        or "repeated-seed run matrix" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate bounded portfolio mapping from readiness"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapRepresentativeBenchmarkPortfolioBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        family_count=data.get("family_count") if isinstance(data.get("family_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_representative_benchmark_portfolio_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_representative_benchmark_portfolio_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP representative benchmark portfolio boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| family_count | {validation.family_count} |",
        f"| active_todo_ref_count | {validation.active_todo_ref_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _portfolio_family_record(
    root: Path,
    roadmap_text: str,
    spec: dict[str, Any],
) -> dict[str, Any]:
    todo_refs = [_todo_ref_record(root, todo_ref) for todo_ref in spec["active_todos"]]
    sidecar_refs = [
        {
            "path": path,
            "exists": (root / path).exists(),
        }
        for path in spec["current_sidecars"]
    ]
    return {
        "family_id": spec["family_id"],
        "domain": spec["domain"],
        "validator_strength": spec["validator_strength"],
        "roadmap_required_phrase": spec["roadmap_required_phrase"],
        "roadmap_phrase_present": _contains_phrase(roadmap_text, spec["roadmap_required_phrase"]),
        "baseline_sota_target": spec["baseline_sota_target"],
        "current_sidecar_refs": sidecar_refs,
        "active_todo_refs": todo_refs,
        "active_todo_ref_count": len(todo_refs),
        "artifact_output_contract": "required_before_representative_claim",
        "readiness_status": spec["readiness_status"],
    }


def _todo_ref_record(root: Path, spec: dict[str, str]) -> dict[str, Any]:
    path = spec["path"]
    text = _read_text(root / path)
    return {
        "path": path,
        "required_phrase": spec["required_phrase"],
        "required_phrase_present": _contains_phrase(text, spec["required_phrase"]),
        "active_marker_present": "- [ ]" in text,
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
) -> tuple[dict[str, Any] | None, list[RoadmapRepresentativeBenchmarkPortfolioBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP representative benchmark portfolio boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapRepresentativeBenchmarkPortfolioBoundaryIssue],
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
    issues: list[RoadmapRepresentativeBenchmarkPortfolioBoundaryIssue],
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


def _issue(
    code: str,
    message: str,
) -> RoadmapRepresentativeBenchmarkPortfolioBoundaryIssue:
    return RoadmapRepresentativeBenchmarkPortfolioBoundaryIssue(code=code, message=message)
