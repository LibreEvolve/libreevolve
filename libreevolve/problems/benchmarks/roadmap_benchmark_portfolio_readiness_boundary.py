from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.roadmap_representative_benchmark_portfolio_boundary import (
    roadmap_representative_benchmark_portfolio_boundary_record,
)


ROADMAP_BENCHMARK_PORTFOLIO_READINESS_BOUNDARY_SCHEMA = (
    "libreevolve.roadmap_benchmark_portfolio_readiness_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "bounded_benchmark_portfolio_readiness_matrix_without_representative_gate"
)
SOURCE_PORTFOLIO_BOUNDARY_INPUT = (
    "papers/roadmap_representative_benchmark_portfolio_boundary.json"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "domain_coverage_matrix",
    "benchmark_admission_checklist",
    "repeated_seed_run_matrix",
    "anti_gaming_certification",
    "sota_baseline_citation_sufficiency",
    "portfolio_balance_ci_freshness",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "domain_coverage_matrix": "not_recorded_locally",
    "benchmark_admission_checklist": "not_recorded_locally",
    "repeated_seed_run_matrix": "not_recorded_locally",
    "anti_gaming_certification": "not_recorded_locally",
    "sota_baseline_citation_sufficiency": "not_recorded_locally",
    "portfolio_balance_ci_freshness": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


CRITERION_SPECS = (
    {
        "criterion_id": "domain_coverage_matrix",
        "portfolio_surface": "benchmark families, domains, validators, and AlphaEvolve claim scope",
        "current_scope": "five static portfolio families with domain labels",
        "missing_readiness": "domain-coverage matrix proving the portfolio is balanced across algorithm, math, systems, and smoke-guardrail surfaces",
        "sidecars": (
            "papers/roadmap_representative_benchmark_portfolio_boundary.json",
            "papers/benchmark_coverage_inventory.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "domain-coverage matrix",
            },
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "benchmark coverage decisions",
            },
        ),
        "validation_gate": "representative benchmark domain-coverage matrix",
        "readiness_status": "family_domain_labels_without_coverage_matrix",
    },
    {
        "criterion_id": "benchmark_admission_checklist",
        "portfolio_surface": "candidate fixtures, smoke examples, benchmark candidates, and paper-comparable evidence",
        "current_scope": "static family readiness labels plus smoke-fixture guardrail",
        "missing_readiness": "admission checklist that prevents smoke fixtures from counting as representative benchmark coverage",
        "sidecars": (
            "papers/benchmark_fixture_readiness_boundary.json",
            "papers/example_benchmark_scope.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "benchmark admission checklist",
            },
            {
                "path": "docs/todo/readme.md",
                "required_phrase": "separating smoke fixtures, benchmark candidates, and paper-comparable",
            },
        ),
        "validation_gate": "benchmark admission checklist with smoke exclusion",
        "readiness_status": "smoke_guardrail_without_admission_checklist",
    },
    {
        "criterion_id": "repeated_seed_run_matrix",
        "portfolio_surface": "repeated-seed runs, sample-efficiency claims, and benchmark certification",
        "current_scope": "sidecars for repeated sampling and sample efficiency without per-family run matrix",
        "missing_readiness": "per-family repeated-seed matrix with target-hit, confidence, and run-budget evidence",
        "sidecars": (
            "papers/repeated_sampling_baseline_boundary.json",
            "papers/sample_efficiency_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "repeated-seed run matrix",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "repeated-seed evidence and exact binomial diagnostics",
            },
        ),
        "validation_gate": "repeated-seed benchmark run matrix",
        "readiness_status": "repeated_sampling_sidecars_without_portfolio_matrix",
    },
    {
        "criterion_id": "anti_gaming_certification",
        "portfolio_surface": "validators, evaluator oracles, incorrect suggestions, and hardening reports",
        "current_scope": "validator and audit sidecars without benchmark-level anti-gaming certification",
        "missing_readiness": "anti-gaming certification proving fixtures resist benchmark-specific hacks and evaluator leakage",
        "sidecars": (
            "papers/evaluator_oracle_boundary.json",
            "papers/incorrect_suggestion_audit_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "anti-gaming certification",
            },
            {
                "path": "docs/todo/code.md",
                "required_phrase": "Connect benchmark-grade fixtures to hardening and scope reports.",
            },
        ),
        "validation_gate": "anti-gaming benchmark certification",
        "readiness_status": "validator_sidecars_without_certification_bundle",
    },
    {
        "criterion_id": "sota_baseline_citation_sufficiency",
        "portfolio_surface": "baseline/SOTA targets, paper citations, and benchmark target thresholds",
        "current_scope": "baseline/SOTA target labels on each portfolio family",
        "missing_readiness": "citation sufficiency proof for every target baseline and benchmark threshold",
        "sidecars": (
            "papers/sorting_network_rediscovery_boundary.json",
            "papers/matrix_suite_publication_artifacts.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "SOTA/baseline citation sufficiency proof",
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": "benchmark harness for repeated seeds, SOTA thresholds",
            },
        ),
        "validation_gate": "baseline/SOTA citation sufficiency proof",
        "readiness_status": "target_labels_without_citation_sufficiency",
    },
    {
        "criterion_id": "portfolio_balance_ci_freshness",
        "portfolio_surface": "portfolio balance score, stale coverage detection, CI freshness, and owner signoff",
        "current_scope": "static portfolio family map without balance scoring or freshness enforcement",
        "missing_readiness": "portfolio-balance score and CI freshness gate with owner-reviewed readiness signoff",
        "sidecars": (
            "papers/sampling_balance_boundary.json",
            "papers/ci_workflow_coverage_boundary.json",
        ),
        "active_todos": (
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "portfolio-balance score",
            },
            {
                "path": "docs/todo/roadmap.md",
                "required_phrase": "CI freshness gate, or owner signoff",
            },
        ),
        "validation_gate": "portfolio balance and CI freshness gate",
        "readiness_status": "static_portfolio_without_balance_or_freshness",
    },
)


@dataclass(frozen=True)
class RoadmapBenchmarkPortfolioReadinessBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class RoadmapBenchmarkPortfolioReadinessBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readiness_criterion_count: int
    sidecar_ref_count: int
    active_todo_ref_count: int
    missing_evidence_count: int
    issues: list[RoadmapBenchmarkPortfolioReadinessBoundaryIssue]


def roadmap_benchmark_portfolio_readiness_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the bounded ROADMAP representative-benchmark readiness matrix."""

    root_path = Path(root)
    source_boundary = roadmap_representative_benchmark_portfolio_boundary_record(
        root_path
    )
    records = [_criterion_record(root_path, spec) for spec in CRITERION_SPECS]
    claim_guard = [_claim_guard_record(record) for record in records]
    sidecar_ref_count = sum(len(record["sidecar_refs"]) for record in records)
    active_todo_ref_count = sum(len(record["active_todo_refs"]) for record in records)
    return {
        "schema": ROADMAP_BENCHMARK_PORTFOLIO_READINESS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_portfolio_boundary_input": SOURCE_PORTFOLIO_BOUNDARY_INPUT,
        "source_family_count": source_boundary["family_count"],
        "source_active_todo_ref_count": source_boundary["active_todo_ref_count"],
        "source_sidecar_ref_count": source_boundary["sidecar_ref_count"],
        "readiness_criterion_count": len(records),
        "sidecar_ref_count": sidecar_ref_count,
        "active_todo_ref_count": active_todo_ref_count,
        "readiness_criteria": records,
        "benchmark_portfolio_claim_guard": claim_guard,
        "benchmark_portfolio_claim_guard_count": len(claim_guard),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records representative-benchmark portfolio "
            "readiness criteria tied to the bounded static portfolio map, plus "
            "a claim guard for each portfolio surface. It does not claim a "
            "domain-coverage matrix, benchmark admission checklist, "
            "repeated-seed run matrix, anti-gaming certification, "
            "SOTA/baseline citation sufficiency, portfolio-balance CI "
            "freshness, or owner review signoff."
        ),
    }


def validate_roadmap_benchmark_portfolio_readiness_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> RoadmapBenchmarkPortfolioReadinessBoundaryValidation:
    data, read_issues = _load_boundary(
        roadmap_benchmark_portfolio_readiness_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return RoadmapBenchmarkPortfolioReadinessBoundaryValidation(
            False, None, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = roadmap_benchmark_portfolio_readiness_boundary_record(root)
    issues: list[RoadmapBenchmarkPortfolioReadinessBoundaryIssue] = []
    if data.get("schema") != ROADMAP_BENCHMARK_PORTFOLIO_READINESS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported ROADMAP benchmark portfolio readiness boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "ROADMAP benchmark portfolio readiness boundary must not claim representative-readiness"))
    for key in (
        "source_portfolio_boundary_input",
        "source_family_count",
        "source_active_todo_ref_count",
        "source_sidecar_ref_count",
        "readiness_criterion_count",
        "sidecar_ref_count",
        "active_todo_ref_count",
        "readiness_criteria",
        "benchmark_portfolio_claim_guard",
        "benchmark_portfolio_claim_guard_count",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current ROADMAP benchmark-portfolio readiness inputs"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a domain-coverage matrix" not in boundary_text
        or "claim guard for each portfolio surface" not in boundary_text
        or "benchmark admission checklist" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate readiness matrix from representative benchmark gate"))
    if data.get("benchmark_portfolio_claim_guard_count") != len(CRITERION_SPECS):
        issues.append(_issue("invalid_benchmark_portfolio_claim_guard_count", "benchmark portfolio claim guard count changed"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return RoadmapBenchmarkPortfolioReadinessBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readiness_criterion_count=data.get("readiness_criterion_count") if isinstance(data.get("readiness_criterion_count"), int) else 0,
        sidecar_ref_count=data.get("sidecar_ref_count") if isinstance(data.get("sidecar_ref_count"), int) else 0,
        active_todo_ref_count=data.get("active_todo_ref_count") if isinstance(data.get("active_todo_ref_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_roadmap_benchmark_portfolio_readiness_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_roadmap_benchmark_portfolio_readiness_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "ROADMAP benchmark portfolio readiness boundary",
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
        "portfolio_surface": spec["portfolio_surface"],
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
        "portfolio_surface": record["portfolio_surface"],
        "allowed_current_claim": record["current_scope"],
        "missing_before_representative_claim": record["missing_readiness"],
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
) -> tuple[dict[str, Any] | None, list[RoadmapBenchmarkPortfolioReadinessBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "ROADMAP benchmark portfolio readiness boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[RoadmapBenchmarkPortfolioReadinessBoundaryIssue],
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
    issues: list[RoadmapBenchmarkPortfolioReadinessBoundaryIssue],
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


def _issue(code: str, message: str) -> RoadmapBenchmarkPortfolioReadinessBoundaryIssue:
    return RoadmapBenchmarkPortfolioReadinessBoundaryIssue(code=code, message=message)
