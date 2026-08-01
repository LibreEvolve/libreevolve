from __future__ import annotations

import json
from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_source_inventory_boundary import (
    EXPECTED_NAMED_SOURCE_SPAN_IDS,
)


IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_implementation_evidence_map_boundary.v11"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = (
    "verified_core_anchors_plus_429_bounded_claims_without_whole_paper_exhaustiveness"
)
EXPECTED_SOURCE_INVENTORY_REF = "papers/alphaevolve_source_inventory_boundary.json"
EXPECTED_CONTEXT_CLAIM_INVENTORY_REF = (
    "papers/alphaevolve_context_claim_inventory_boundary.json"
)
EXPECTED_MATRIX_RESULT_CLAIM_INVENTORY_REF = (
    "papers/alphaevolve_matrix_result_claim_inventory_boundary.json"
)
EXPECTED_MATH_RESULT_CLAIM_INVENTORY_REF = (
    "papers/alphaevolve_math_result_claim_inventory_boundary.json"
)
EXPECTED_SCHEDULING_CLAIM_INVENTORY_REF = (
    "papers/alphaevolve_scheduling_claim_inventory_boundary.json"
)
EXPECTED_KERNEL_CLAIM_INVENTORY_REF = (
    "papers/alphaevolve_kernel_claim_inventory_boundary.json"
)
EXPECTED_HARDWARE_CLAIM_INVENTORY_REF = (
    "papers/alphaevolve_hardware_claim_inventory_boundary.json"
)
EXPECTED_COMPILER_CLAIM_INVENTORY_REF = (
    "papers/alphaevolve_compiler_claim_inventory_boundary.json"
)
EXPECTED_ABLATION_CLAIM_INVENTORY_REF = (
    "papers/alphaevolve_ablation_claim_inventory_boundary.json"
)
EXPECTED_SYSTEM_REQUIREMENT_INVENTORY_REF = (
    "papers/alphaevolve_system_requirement_inventory_boundary.json"
)
EXPECTED_RECORDED_EVIDENCE = {
    "named_source_structure_inventory": "55_pdf_verified_spans",
    "bounded_system_requirement_inventory": "50_pdf_anchored_table_1_and_section_2_requirements",
    "bounded_context_claim_inventory": (
        "41_pdf_anchored_abstract_introduction_discussion_and_collaborator_claims"
    ),
    "bounded_matrix_result_claim_inventory": (
        "41_pdf_anchored_section_3_1_table_2_figure_4_and_footnote_3_claims"
    ),
    "bounded_math_result_claim_inventory": (
        "63_pdf_anchored_section_3_2_and_figure_5_claims"
    ),
    "bounded_scheduling_claim_inventory": (
        "45_pdf_anchored_section_3_3_opening_section_3_3_1_and_figure_6_claims"
    ),
    "bounded_kernel_claim_inventory": (
        "59_pdf_anchored_section_3_3_2_and_figure_7_claims"
    ),
    "bounded_hardware_claim_inventory": (
        "35_pdf_anchored_section_3_3_3_claims"
    ),
    "bounded_compiler_claim_inventory": (
        "44_pdf_anchored_section_3_3_4_claims"
    ),
    "bounded_ablation_claim_inventory": (
        "51_pdf_anchored_section_4_and_figure_8_claims"
    ),
    "reference_existence_checks": (
        "module_test_sidecar_todo_paths_and_todo_phrases"
    ),
}
EXPECTED_MISSING_EVIDENCE = {
    "exhaustive_requirement_inventory": "section_5_remaining_figures_tables_and_appendices_not_fully_recorded",
    "claim_level_source_span_coverage_matrix": "429_bounded_claims_remaining_section_5_and_remaining_exhibits_appendices_not_recorded",
    "status_cell_semantic_verifier": "not_recorded_locally",
    "implemented_benchmark_bullet_semantic_verifier": "not_recorded_locally",
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
        "source_span_ids": ["section_2_1", "figure_3"],
        "claim_status": "partially_implemented",
        "module_refs": [
            "libreevolve/core/candidate.py",
            "libreevolve/core/diff.py",
            "libreevolve/problems/loader.py",
        ],
        "test_refs": [
            "tests/core/test_candidate.py",
            "tests/core/test_diff.py",
            "tests/core/test_loader.py",
            "tests/test_candidate_language_runner_boundary.py",
        ],
        "sidecar_refs": [
            "papers/existing_codebase_integration_boundary.json",
            "papers/candidate_language_runner_boundary.json",
        ],
        "todo_refs": [
            {
                "path": "docs/todo/code.md",
                "required_phrase": (
                    "Extend the task-primary local candidate runner beyond host C smoke to"
                ),
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": (
                    "Add AlphaEvolve-grade candidate language, build, and runner contracts."
                ),
            },
        ],
        "coverage_scope": "anchor_only",
    },
    {
        "requirement_id": "alphaevolve_evaluator_cascade",
        "source_refs": [
            "2506.13131:Section 2.4",
        ],
        "source_span_ids": ["section_2_4"],
        "claim_status": "partially_implemented",
        "module_refs": [
            "libreevolve/core/evaluator.py",
            "libreevolve/core/loop.py",
        ],
        "test_refs": [
            "tests/core/test_evaluator.py",
            "tests/core/test_loop.py",
            "tests/test_evaluation_cascade_boundary.py",
        ],
        "sidecar_refs": [
            "papers/evaluation_cascade_boundary.json",
            "papers/evaluator_oracle_boundary.json",
            "papers/cascade_hypothesis_test_boundary.json",
        ],
        "todo_refs": [
            {
                "path": "docs/todo/code.md",
                "required_phrase": (
                    "Finish paper-facing evaluation-cascade promotion and attrition evidence."
                ),
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": (
                    "Track evaluation-cascade promotion and attrition evidence."
                ),
            },
        ],
        "coverage_scope": "anchor_only",
    },
    {
        "requirement_id": "alphaevolve_llm_sampling_and_prompting",
        "source_refs": [
            "2506.13131:Section 2.2",
            "2506.13131:Section 2.3",
        ],
        "source_span_ids": ["section_2_2", "section_2_3"],
        "claim_status": "partially_implemented",
        "module_refs": [
            "libreevolve/core/prompt.py",
            "libreevolve/llm/ensemble.py",
            "libreevolve/llm/openai.py",
            "libreevolve/llm/anthropic.py",
            "libreevolve/llm/ollama.py",
        ],
        "test_refs": [
            "tests/core/test_prompt.py",
            "tests/llm/test_ensemble.py",
            "tests/llm/test_backends.py",
        ],
        "sidecar_refs": [
            "papers/fast_strong_model_mix_boundary.json",
            "papers/llm_role_scheduler_boundary.json",
            "papers/prompt_section_packing_boundary.json",
            "papers/gemini_provider_parity_boundary.json",
        ],
        "todo_refs": [
            {
                "path": "docs/todo/code.md",
                "required_phrase": (
                    "Complete provider-token prompt section fitting beyond mutation prompts"
                ),
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": (
                    "Independent per-role LLM scheduler state and reward policy."
                ),
            },
        ],
        "coverage_scope": "anchor_only",
    },
    {
        "requirement_id": "alphaevolve_evolutionary_database",
        "source_refs": [
            "2506.13131:Section 2.5",
            "2506.13131:Figure 2",
        ],
        "source_span_ids": ["section_2_5", "figure_2"],
        "claim_status": "partially_implemented",
        "module_refs": [
            "libreevolve/core/database.py",
            "libreevolve/population/islands.py",
            "libreevolve/population/map_elites.py",
        ],
        "test_refs": [
            "tests/population/test_database.py",
            "tests/population/test_islands.py",
            "tests/population/test_map_elites.py",
        ],
        "sidecar_refs": [
            "papers/sampling_balance_boundary.json",
            "papers/map_elites_descriptor_boundary.json",
            "papers/objective_archive_boundary.json",
        ],
        "todo_refs": [
            {
                "path": "docs/todo/code.md",
                "required_phrase": (
                    "Promote multi-objective overlays to primary archive optimization."
                ),
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": (
                    "Stable behavior descriptor models and archive rebin semantics."
                ),
            },
        ],
        "coverage_scope": "anchor_only",
    },
    {
        "requirement_id": "alphaevolve_async_distributed_pipeline",
        "source_refs": [
            "2506.13131:Figure 2",
            "2506.13131:Section 2.6",
        ],
        "source_span_ids": ["figure_2", "section_2_6"],
        "claim_status": "partially_implemented_without_distributed_alphaevolve_parity",
        "module_refs": [
            "libreevolve/core/loop.py",
            "libreevolve/core/async_evaluator.py",
            "libreevolve/core/async_sampler.py",
        ],
        "test_refs": [
            "tests/core/test_async_evaluator.py",
            "tests/core/test_async_sampler.py",
            "tests/test_distributed_pipeline_topology_boundary.py",
            "tests/test_parallel_evaluation_readiness_boundary.py",
        ],
        "sidecar_refs": [
            "papers/distributed_pipeline_topology_boundary.json",
            "papers/parallel_evaluation_readiness_boundary.json",
            "papers/expensive_evaluation_budget_boundary.json",
        ],
        "todo_refs": [
            {
                "path": "docs/todo/code.md",
                "required_phrase": (
                    "Complete asynchronous worker and concurrent proposal control beyond the"
                ),
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": (
                    "Parallelized evaluation and asynchronous throughput."
                ),
            },
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
        "source_span_ids": ["section_3", "appendix_a", "appendix_b"],
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
            "libreevolve/problems/benchmarks/alphaevolve_appendix_b.json",
            "papers/benchmark_fixture_readiness_boundary.json",
        ],
        "todo_refs": [
            {
                "path": "docs/todo/code.md",
                "required_phrase": (
                    "Connect benchmark-grade fixtures to hardening and scope reports."
                ),
            },
            {
                "path": "docs/todo/papers.md",
                "required_phrase": (
                    "Harden benchmark implementations beyond smoke-example fidelity."
                ),
            },
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
    reference_check_count: int
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
        "source_inventory_ref": EXPECTED_SOURCE_INVENTORY_REF,
        "context_claim_inventory_ref": EXPECTED_CONTEXT_CLAIM_INVENTORY_REF,
        "matrix_result_claim_inventory_ref": EXPECTED_MATRIX_RESULT_CLAIM_INVENTORY_REF,
        "math_result_claim_inventory_ref": EXPECTED_MATH_RESULT_CLAIM_INVENTORY_REF,
        "scheduling_claim_inventory_ref": EXPECTED_SCHEDULING_CLAIM_INVENTORY_REF,
        "kernel_claim_inventory_ref": EXPECTED_KERNEL_CLAIM_INVENTORY_REF,
        "hardware_claim_inventory_ref": EXPECTED_HARDWARE_CLAIM_INVENTORY_REF,
        "compiler_claim_inventory_ref": EXPECTED_COMPILER_CLAIM_INVENTORY_REF,
        "ablation_claim_inventory_ref": EXPECTED_ABLATION_CLAIM_INVENTORY_REF,
        "system_requirement_inventory_ref": EXPECTED_SYSTEM_REQUIREMENT_INVENTORY_REF,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "requirements": deepcopy(list(EXPECTED_REQUIREMENTS)),
        "recorded_evidence": dict(EXPECTED_RECORDED_EVIDENCE),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records corrected core AlphaEvolve requirement anchors "
            "with verified module, test, sidecar, and TODO links and connects them "
            "to the PDF-verified named source inventory, bounded 50-requirement "
            "Table 1/Section 2 inventory, and bounded 41-claim Abstract, "
            "Introduction, Discussion, and collaborator-context inventory, plus "
            "the bounded 41-claim Section 3.1, Table 2, Figure 4, and footnote 3 "
            "matrix-result inventory, and the bounded 63-claim Section 3.2 and "
            "Figure 5 constructive-math inventory, plus the bounded 45-claim "
            "Section 3.3 opening, Section 3.3.1, and Figure 6 scheduling "
            "inventory, plus the bounded 59-claim Section 3.3.2 and Figure 7 "
            "kernel-engineering inventory, plus the bounded 35-claim Section "
            "3.3.3 hardware-circuit-design inventory, plus the bounded "
            "44-claim Section 3.3.4 compiler-generated-code inventory, plus "
            "the bounded 51-claim Section 4 and Figure 8 ablation inventory. It "
            "does not claim a whole-paper "
            "exhaustive requirement inventory or whole-paper claim-level source-span coverage matrix, "
            "paper-index phrase evidence-link sufficiency, status-cell "
            "semantic verifier, implemented benchmark "
            "bullet semantic verifier, absence-sentence freshness matrix, module "
            "coverage detector, test/runtime-artifact coverage detector, "
            "generated code-audit report, CI exhaustiveness gate, or proof "
            "that every AlphaEvolve-facing implementation claim has been "
            "classified."
        ),
    }


def validate_implementation_evidence_map_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ImplementationEvidenceMapBoundaryValidation:
    data, read_issues = _load_boundary(
        implementation_evidence_map_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return ImplementationEvidenceMapBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ImplementationEvidenceMapBoundaryIssue] = []
    if data.get("schema") != IMPLEMENTATION_EVIDENCE_MAP_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported implementation evidence map boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_inventory_ref") != EXPECTED_SOURCE_INVENTORY_REF:
        issues.append(_issue("invalid_source_inventory_ref", f"source_inventory_ref must be {EXPECTED_SOURCE_INVENTORY_REF}"))
    if data.get("context_claim_inventory_ref") != EXPECTED_CONTEXT_CLAIM_INVENTORY_REF:
        issues.append(_issue("invalid_context_claim_inventory_ref", f"context_claim_inventory_ref must be {EXPECTED_CONTEXT_CLAIM_INVENTORY_REF}"))
    if not (Path(root) / EXPECTED_CONTEXT_CLAIM_INVENTORY_REF).is_file():
        issues.append(_issue("missing_context_claim_inventory_ref", f"{EXPECTED_CONTEXT_CLAIM_INVENTORY_REF} is missing"))
    if data.get("matrix_result_claim_inventory_ref") != EXPECTED_MATRIX_RESULT_CLAIM_INVENTORY_REF:
        issues.append(_issue("invalid_matrix_result_claim_inventory_ref", f"matrix_result_claim_inventory_ref must be {EXPECTED_MATRIX_RESULT_CLAIM_INVENTORY_REF}"))
    if not (Path(root) / EXPECTED_MATRIX_RESULT_CLAIM_INVENTORY_REF).is_file():
        issues.append(_issue("missing_matrix_result_claim_inventory_ref", f"{EXPECTED_MATRIX_RESULT_CLAIM_INVENTORY_REF} is missing"))
    if data.get("math_result_claim_inventory_ref") != EXPECTED_MATH_RESULT_CLAIM_INVENTORY_REF:
        issues.append(_issue("invalid_math_result_claim_inventory_ref", f"math_result_claim_inventory_ref must be {EXPECTED_MATH_RESULT_CLAIM_INVENTORY_REF}"))
    if not (Path(root) / EXPECTED_MATH_RESULT_CLAIM_INVENTORY_REF).is_file():
        issues.append(_issue("missing_math_result_claim_inventory_ref", f"{EXPECTED_MATH_RESULT_CLAIM_INVENTORY_REF} is missing"))
    if data.get("scheduling_claim_inventory_ref") != EXPECTED_SCHEDULING_CLAIM_INVENTORY_REF:
        issues.append(_issue("invalid_scheduling_claim_inventory_ref", f"scheduling_claim_inventory_ref must be {EXPECTED_SCHEDULING_CLAIM_INVENTORY_REF}"))
    if not (Path(root) / EXPECTED_SCHEDULING_CLAIM_INVENTORY_REF).is_file():
        issues.append(_issue("missing_scheduling_claim_inventory_ref", f"{EXPECTED_SCHEDULING_CLAIM_INVENTORY_REF} is missing"))
    if data.get("kernel_claim_inventory_ref") != EXPECTED_KERNEL_CLAIM_INVENTORY_REF:
        issues.append(_issue("invalid_kernel_claim_inventory_ref", f"kernel_claim_inventory_ref must be {EXPECTED_KERNEL_CLAIM_INVENTORY_REF}"))
    if not (Path(root) / EXPECTED_KERNEL_CLAIM_INVENTORY_REF).is_file():
        issues.append(_issue("missing_kernel_claim_inventory_ref", f"{EXPECTED_KERNEL_CLAIM_INVENTORY_REF} is missing"))
    if data.get("hardware_claim_inventory_ref") != EXPECTED_HARDWARE_CLAIM_INVENTORY_REF:
        issues.append(_issue("invalid_hardware_claim_inventory_ref", f"hardware_claim_inventory_ref must be {EXPECTED_HARDWARE_CLAIM_INVENTORY_REF}"))
    if not (Path(root) / EXPECTED_HARDWARE_CLAIM_INVENTORY_REF).is_file():
        issues.append(_issue("missing_hardware_claim_inventory_ref", f"{EXPECTED_HARDWARE_CLAIM_INVENTORY_REF} is missing"))
    if data.get("compiler_claim_inventory_ref") != EXPECTED_COMPILER_CLAIM_INVENTORY_REF:
        issues.append(_issue("invalid_compiler_claim_inventory_ref", f"compiler_claim_inventory_ref must be {EXPECTED_COMPILER_CLAIM_INVENTORY_REF}"))
    if not (Path(root) / EXPECTED_COMPILER_CLAIM_INVENTORY_REF).is_file():
        issues.append(_issue("missing_compiler_claim_inventory_ref", f"{EXPECTED_COMPILER_CLAIM_INVENTORY_REF} is missing"))
    if data.get("ablation_claim_inventory_ref") != EXPECTED_ABLATION_CLAIM_INVENTORY_REF:
        issues.append(_issue("invalid_ablation_claim_inventory_ref", f"ablation_claim_inventory_ref must be {EXPECTED_ABLATION_CLAIM_INVENTORY_REF}"))
    if not (Path(root) / EXPECTED_ABLATION_CLAIM_INVENTORY_REF).is_file():
        issues.append(_issue("missing_ablation_claim_inventory_ref", f"{EXPECTED_ABLATION_CLAIM_INVENTORY_REF} is missing"))
    if data.get("system_requirement_inventory_ref") != EXPECTED_SYSTEM_REQUIREMENT_INVENTORY_REF:
        issues.append(_issue("invalid_system_requirement_inventory_ref", f"system_requirement_inventory_ref must be {EXPECTED_SYSTEM_REQUIREMENT_INVENTORY_REF}"))
    if not (Path(root) / EXPECTED_SYSTEM_REQUIREMENT_INVENTORY_REF).is_file():
        issues.append(_issue("missing_system_requirement_inventory_ref", f"{EXPECTED_SYSTEM_REQUIREMENT_INVENTORY_REF} is missing"))
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
    reference_check_count = _validate_references(data.get("requirements"), Path(root), issues)
    _validate_recorded_evidence(data.get("recorded_evidence"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim a whole-paper exhaustive requirement inventory" not in boundary_text
        or "whole-paper claim-level source-span coverage matrix" not in boundary_text
        or "paper-index phrase evidence-link sufficiency" not in boundary_text
        or "implemented benchmark bullet semantic verifier" not in boundary_text
        or "absence-sentence freshness matrix" not in boundary_text
        or "generated code-audit report" not in boundary_text
        or "every AlphaEvolve-facing implementation claim" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate core anchors from exhaustive implementation proof"))
    return ImplementationEvidenceMapBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        requirement_count=requirement_count,
        reference_check_count=reference_check_count,
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
        f"| reference_check_count | {validation.reference_check_count} |",
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


def _validate_references(
    value: object,
    root: Path,
    issues: list[ImplementationEvidenceMapBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        return 0
    check_count = 0
    source_span_ids = set(EXPECTED_NAMED_SOURCE_SPAN_IDS)
    inventory_path = root / EXPECTED_SOURCE_INVENTORY_REF
    check_count += 1
    if not inventory_path.is_file():
        issues.append(
            _issue(
                "missing_source_inventory_ref",
                f"source inventory does not exist: {EXPECTED_SOURCE_INVENTORY_REF}",
            )
        )
    for requirement in value:
        if not isinstance(requirement, dict):
            continue
        requirement_id = requirement.get("requirement_id", "<unknown>")
        for key in ("module_refs", "test_refs", "sidecar_refs"):
            refs = requirement.get(key)
            if not isinstance(refs, list):
                continue
            for ref in refs:
                check_count += 1
                if not isinstance(ref, str) or not (root / ref).exists():
                    issues.append(
                        _issue(
                            f"missing_{key[:-1]}",
                            f"{requirement_id}.{key} references a missing path: {ref}",
                        )
                    )
        spans = requirement.get("source_span_ids")
        if isinstance(spans, list):
            for span_id in spans:
                check_count += 1
                if not isinstance(span_id, str) or span_id not in source_span_ids:
                    issues.append(
                        _issue(
                            "unknown_source_span_id",
                            f"{requirement_id} references an unknown named source span: {span_id}",
                        )
                    )
        todos = requirement.get("todo_refs")
        if not isinstance(todos, list):
            continue
        for todo in todos:
            check_count += 1
            if not isinstance(todo, dict):
                issues.append(
                    _issue(
                        "invalid_todo_ref",
                        f"{requirement_id}.todo_refs must contain path/phrase objects",
                    )
                )
                continue
            path_value = todo.get("path")
            phrase = todo.get("required_phrase")
            if not isinstance(path_value, str) or not isinstance(phrase, str):
                issues.append(
                    _issue(
                        "invalid_todo_ref",
                        f"{requirement_id}.todo_refs must contain string path and required_phrase fields",
                    )
                )
                continue
            path = root / path_value
            try:
                text = path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                text = ""
            if not path.is_file() or phrase not in text:
                issues.append(
                    _issue(
                        "missing_todo_ref",
                        f"{requirement_id} TODO reference is missing or stale: {path_value}",
                    )
                )
    return check_count


def _validate_recorded_evidence(
    value: object,
    issues: list[ImplementationEvidenceMapBoundaryIssue],
) -> None:
    if value != EXPECTED_RECORDED_EVIDENCE:
        issues.append(
            _issue(
                "invalid_recorded_evidence",
                "recorded_evidence must preserve named inventory and reference checks",
            )
        )


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
