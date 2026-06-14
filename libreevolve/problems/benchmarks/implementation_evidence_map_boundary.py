from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_implementation_evidence_map_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = (
    "core_requirement_anchors_without_exhaustive_coverage"
)
EXPECTED_MISSING_EVIDENCE = {
    "exhaustive_requirement_inventory": "not_recorded_locally",
    "source_span_coverage_matrix": "not_recorded_locally",
    "paper_index_phrase_claim_inventory": "not_recorded_locally",
    "status_row_source_span_inventory": "not_recorded_locally",
    "status_cell_semantic_verifier": "not_recorded_locally",
    "implemented_benchmark_bullet_coverage_map": "not_recorded_locally",
    "absence_sentence_freshness_matrix": "not_recorded_locally",
    "module_coverage_detector": "not_recorded_locally",
    "test_and_runtime_artifact_coverage_detector": "not_recorded_locally",
    "generated_code_audit_report": "not_recorded_locally",
    "ci_exhaustiveness_gate": "not_recorded_locally",
}
EXPECTED_REQUIREMENTS = (
    {
        "requirement_id": "alphaevolve_program_markers",
        "source_refs": [
            "2506.13131:Section 2.1",
            "2506.13131:Figure 3",
        ],
        "claim_status": "partially_implemented",
        "module_refs": [
            "libreevolve/core/candidate.py",
            "libreevolve/core/diff.py",
            "libreevolve/problems/loader.py",
        ],
        "test_refs": [
            "tests/test_candidate.py",
            "tests/test_diff.py",
            "tests/test_problem_loader.py",
        ],
        "sidecar_refs": [
            "papers/existing_codebase_integration_boundary.json",
            "papers/candidate_language_runner_boundary.json",
        ],
        "todo_refs": [
            "docs/todo/code.md#candidate-workspace-fidelity",
            "docs/todo/papers.md#candidate-language-build-and-runner-contracts",
        ],
        "coverage_scope": "anchor_only",
    },
    {
        "requirement_id": "alphaevolve_evaluator_cascade",
        "source_refs": [
            "2506.13131:Section 2.2",
            "2506.13131:Section 2.3",
        ],
        "claim_status": "partially_implemented",
        "module_refs": [
            "libreevolve/core/evaluator.py",
            "libreevolve/core/loop.py",
        ],
        "test_refs": [
            "tests/test_evaluator.py",
            "tests/test_evolution.py",
        ],
        "sidecar_refs": [
            "papers/evaluation_cascade_boundary.json",
            "papers/evaluator_oracle_boundary.json",
            "papers/cascade_hypothesis_test_boundary.json",
        ],
        "todo_refs": [
            "docs/todo/code.md#evaluation-and-oracles",
            "docs/todo/papers.md#evaluation-cascade-promotion-and-attrition-evidence",
        ],
        "coverage_scope": "anchor_only",
    },
    {
        "requirement_id": "alphaevolve_llm_sampling_and_prompting",
        "source_refs": [
            "2506.13131:Section 2.4",
            "2506.13131:Section 2.5",
        ],
        "claim_status": "partially_implemented",
        "module_refs": [
            "libreevolve/core/prompt.py",
            "libreevolve/llm/ensemble.py",
            "libreevolve/llm/openai.py",
            "libreevolve/llm/anthropic.py",
            "libreevolve/llm/ollama.py",
        ],
        "test_refs": [
            "tests/test_prompt.py",
            "tests/test_llm_ensemble.py",
        ],
        "sidecar_refs": [
            "papers/fast_strong_model_mix_boundary.json",
            "papers/llm_role_scheduler_boundary.json",
            "papers/prompt_section_packing_boundary.json",
            "papers/gemini_provider_parity_boundary.json",
        ],
        "todo_refs": [
            "docs/todo/code.md#llm-and-prompting",
            "docs/todo/papers.md#independent-per-role-llm-scheduler-state-and-reward-policy",
        ],
        "coverage_scope": "anchor_only",
    },
    {
        "requirement_id": "alphaevolve_evolutionary_database",
        "source_refs": [
            "2506.13131:Section 2.6",
            "2506.13131:Figure 2",
        ],
        "claim_status": "partially_implemented",
        "module_refs": [
            "libreevolve/core/database.py",
            "libreevolve/population/islands.py",
            "libreevolve/population/map_elites.py",
        ],
        "test_refs": [
            "tests/test_database.py",
            "tests/test_islands.py",
            "tests/test_map_elites.py",
        ],
        "sidecar_refs": [
            "papers/sampling_balance_boundary.json",
            "papers/map_elites_descriptor_boundary.json",
            "papers/objective_archive_boundary.json",
        ],
        "todo_refs": [
            "docs/todo/code.md#archive-database-and-replay",
            "docs/todo/papers.md#stable-behavior-descriptor-models-and-archive-rebin-semantics",
        ],
        "coverage_scope": "anchor_only",
    },
    {
        "requirement_id": "alphaevolve_async_distributed_pipeline",
        "source_refs": [
            "2506.13131:Figure 2",
            "2506.13131:Section 4",
        ],
        "claim_status": "missing_alphaevolve_parity",
        "module_refs": [
            "libreevolve/core/loop.py",
        ],
        "test_refs": [
            "tests/test_distributed_pipeline_topology_boundary.py",
            "tests/test_parallel_evaluation_readiness_boundary.py",
        ],
        "sidecar_refs": [
            "papers/distributed_pipeline_topology_boundary.json",
            "papers/parallel_evaluation_readiness_boundary.json",
            "papers/expensive_evaluation_budget_boundary.json",
        ],
        "todo_refs": [
            "docs/todo/code.md#distributed-and-async-execution",
            "docs/todo/papers.md#parallelized-evaluation-and-asynchronous-throughput",
        ],
        "coverage_scope": "anchor_only",
    },
    {
        "requirement_id": "alphaevolve_published_benchmarks",
        "source_refs": [
            "2506.13131:Section 3",
            "2506.13131:Appendix A",
            "2506.13131:Appendix B",
        ],
        "claim_status": "mostly_missing_alphaevolve_result_reproduction",
        "module_refs": [
            "libreevolve/problems/examples/",
            "libreevolve/problems/benchmarks/",
        ],
        "test_refs": [
            "tests/test_matrix_results.py",
            "tests/test_appendix_a_matrix_registry.py",
            "tests/test_appendix_b_registry.py",
        ],
        "sidecar_refs": [
            "papers/matrix_suite_publication_artifacts.json",
            "papers/appendix_b_registry.json",
            "papers/benchmark_fixture_readiness_boundary.json",
        ],
        "todo_refs": [
            "docs/todo/code.md#benchmarks-and-paper-artifacts",
            "docs/todo/papers.md#benchmark-implementations",
        ],
        "coverage_scope": "anchor_only",
    },
)


@dataclass(frozen=True)
class ImplementationEvidenceMapBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ImplementationEvidenceMapBoundaryValidation:
    ok: bool
    boundary_status: str | None
    requirement_count: int
    missing_evidence_count: int
    issues: list[ImplementationEvidenceMapBoundaryIssue]


def implementation_evidence_map_boundary_record() -> dict[str, Any]:
    """Return the current implementation-evidence map boundary."""

    return {
        "schema": IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve alignment needs traceable evidence from paper "
            "requirements to implementation modules, tests, runtime artifacts, "
            "sidecars, active TODOs, and every paper-index implementation "
            "status claim."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "requirements": [dict(requirement) for requirement in EXPECTED_REQUIREMENTS],
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records core AlphaEvolve requirement anchors with "
            "module, test, sidecar, and TODO links. It does not claim an "
            "exhaustive requirement inventory, source-span coverage matrix, "
            "paper-index phrase-claim inventory, status-row source-span "
            "inventory, status-cell semantic verifier, implemented benchmark "
            "bullet coverage map, absence-sentence freshness matrix, module "
            "coverage detector, test/runtime-artifact coverage detector, "
            "generated code-audit report, CI exhaustiveness gate, or proof "
            "that every AlphaEvolve-facing implementation claim has been "
            "classified."
        ),
    }


def validate_implementation_evidence_map_boundary(
    boundary: object | str | Path | None = None,
) -> ImplementationEvidenceMapBoundaryValidation:
    data, read_issues = _load_boundary(
        implementation_evidence_map_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ImplementationEvidenceMapBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ImplementationEvidenceMapBoundaryIssue] = []
    if data.get("schema") != IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported implementation evidence map boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "traceable evidence" not in source_claim
        or "paper-index implementation status claim" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify traceable implementation evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "implementation evidence map must not claim exhaustive coverage"))
    requirement_count = _validate_requirements(data.get("requirements"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim an exhaustive requirement inventory" not in boundary_text
        or "paper-index phrase-claim inventory" not in boundary_text
        or "implemented benchmark bullet coverage map" not in boundary_text
        or "absence-sentence freshness matrix" not in boundary_text
        or "generated code-audit report" not in boundary_text
        or "every AlphaEvolve-facing implementation claim" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate core anchors from exhaustive implementation proof"))
    return ImplementationEvidenceMapBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        requirement_count=requirement_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_implementation_evidence_map_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_implementation_evidence_map_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Implementation evidence map boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| requirement_count | {validation.requirement_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ImplementationEvidenceMapBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "implementation evidence map boundary must be a JSON object")]


def _validate_requirements(
    value: object,
    issues: list[ImplementationEvidenceMapBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_requirements", "requirements must be a list"))
        return 0
    requirements = [item for item in value if isinstance(item, dict)]
    if len(requirements) != len(value):
        issues.append(_issue("invalid_requirement", "each requirement must be an object"))
    expected_by_id = {
        requirement["requirement_id"]: requirement
        for requirement in EXPECTED_REQUIREMENTS
    }
    actual_by_id = {
        requirement.get("requirement_id"): requirement
        for requirement in requirements
        if isinstance(requirement.get("requirement_id"), str)
    }
    missing = sorted(set(expected_by_id) - set(actual_by_id))
    extra = sorted(set(actual_by_id) - set(expected_by_id))
    if missing:
        issues.append(_issue("missing_requirement_id", f"missing requirement ids: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_requirement_id", f"unknown requirement ids: {', '.join(extra)}"))
    for requirement_id, expected in expected_by_id.items():
        actual = actual_by_id.get(requirement_id)
        if not actual:
            continue
        for key, expected_value in expected.items():
            if actual.get(key) != expected_value:
                issues.append(_issue(f"invalid_{requirement_id}_{key}", f"{requirement_id}.{key} does not match the expected evidence anchor"))
    return len(requirements)


def _validate_missing_evidence(
    value: object,
    issues: list[ImplementationEvidenceMapBoundaryIssue],
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


def _issue(code: str, message: str) -> ImplementationEvidenceMapBoundaryIssue:
    return ImplementationEvidenceMapBoundaryIssue(code, message)
