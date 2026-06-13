from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CANDIDATE_ABSTRACTION_BIAS_MATRIX_SCHEMA = (
    "libreevolve.alphaevolve_candidate_abstraction_bias_matrix.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.1", "Discussion")
EXPECTED_MATRIX_STATUS = "design_matrix_without_executed_bias_benchmarks"
EXPECTED_ABSTRACTION_IDS = (
    "direct_solution",
    "constructor_function",
    "bespoke_search_algorithm",
    "coevolved_solution_and_search",
)
EXPECTED_COMPARISON_FIELDS = (
    "candidate_abstraction_family",
    "problem_structure_rationale",
    "symmetry_structure_assumption",
    "expected_bias_direction",
    "representation_payload_contract",
    "runner_or_materializer_contract",
    "equal_budget_comparison_metric",
    "paired_solution_search_linkage",
)
EXPECTED_MISSING_EVIDENCE = {
    "executed_equal_budget_bias_benchmarks": "not_recorded_locally",
    "problem_defined_serializer_materializer_runner_hooks": "not_configured",
    "paired_solution_search_runtime_support": "not_supported",
    "benchmark_result_tables": "not_recorded_locally",
    "human_abstraction_choice_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class CandidateAbstractionBiasMatrixIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CandidateAbstractionBiasMatrixValidation:
    ok: bool
    matrix_status: str | None
    abstraction_count: int
    comparison_field_count: int
    missing_evidence_count: int
    issues: list[CandidateAbstractionBiasMatrixIssue]


def candidate_abstraction_bias_matrix_record() -> dict[str, Any]:
    """Return the current candidate-abstraction bias matrix boundary."""

    return {
        "schema": CANDIDATE_ABSTRACTION_BIAS_MATRIX_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "matrix_status": EXPECTED_MATRIX_STATUS,
        "claim_ready": False,
        "comparison_fields": list(EXPECTED_COMPARISON_FIELDS),
        "abstraction_families": [
            {
                "abstraction_id": "direct_solution",
                "paper_role": "search for solutions directly",
                "problem_structure_rationale": "simple or directly encodable candidate objects",
                "symmetry_structure_assumption": "not_specialized_for_high_symmetry",
                "expected_bias_direction": "least_inductive_bias_from_constructor_or_search_code",
                "representation_payload_contract": "not_configured_beyond_code_file_set",
                "runner_or_materializer_contract": "python_workspace_validator_only",
                "equal_budget_comparison_metric": "not_recorded_locally",
                "paired_solution_search_linkage": "not_applicable",
            },
            {
                "abstraction_id": "constructor_function",
                "paper_role": "evolve constructor functions",
                "problem_structure_rationale": "may suit highly symmetric or rule-generated solutions",
                "symmetry_structure_assumption": "constructor_functions_can_bias_toward_symmetric_solutions",
                "expected_bias_direction": "stronger_structure_bias_than_direct_solution",
                "representation_payload_contract": "not_configured_beyond_code_file_set",
                "runner_or_materializer_contract": "not_distinguished_from_python_workspace",
                "equal_budget_comparison_metric": "not_recorded_locally",
                "paired_solution_search_linkage": "not_applicable",
            },
            {
                "abstraction_id": "bespoke_search_algorithm",
                "paper_role": "evolve bespoke search algorithms",
                "problem_structure_rationale": "may suit non-symmetric or search-intensive solution spaces",
                "symmetry_structure_assumption": "customized_search_can_bias_toward_non_symmetric_solutions",
                "expected_bias_direction": "search_process_bias_rather_than_solution_encoding_bias",
                "representation_payload_contract": "not_configured_beyond_code_file_set",
                "runner_or_materializer_contract": "not_distinguished_from_python_workspace",
                "equal_budget_comparison_metric": "not_recorded_locally",
                "paired_solution_search_linkage": "not_applicable",
            },
            {
                "abstraction_id": "coevolved_solution_and_search",
                "paper_role": "co-evolve intermediate solutions and search algorithms",
                "problem_structure_rationale": "may expose interaction between solution state and generated search procedure",
                "symmetry_structure_assumption": "requires_explicit_solution_search_pair_model",
                "expected_bias_direction": "unknown_until_pair_runtime_and_metrics_exist",
                "representation_payload_contract": "unsupported",
                "runner_or_materializer_contract": "unsupported",
                "equal_budget_comparison_metric": "not_recorded_locally",
                "paired_solution_search_linkage": "not_supported",
            },
        ],
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This matrix records paper-derived abstraction-family roles, "
            "problem-structure rationale fields, and expected bias directions "
            "for future comparisons. It does not claim problem-defined "
            "abstraction hooks, paired solution/search runtime support, "
            "executed equal-budget benchmark results, human signoff, or "
            "AlphaEvolve-style abstraction-selection evidence."
        ),
    }


def validate_candidate_abstraction_bias_matrix(
    matrix: object | str | Path | None = None,
) -> CandidateAbstractionBiasMatrixValidation:
    data, read_issues = _load_matrix(
        candidate_abstraction_bias_matrix_record() if matrix is None else matrix
    )
    if read_issues:
        return CandidateAbstractionBiasMatrixValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CandidateAbstractionBiasMatrixIssue] = []
    if data.get("schema") != CANDIDATE_ABSTRACTION_BIAS_MATRIX_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported candidate-abstraction bias matrix schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.1', 'Discussion']"))
    status = data.get("matrix_status")
    if status != EXPECTED_MATRIX_STATUS:
        issues.append(_issue("invalid_matrix_status", f"matrix_status must be {EXPECTED_MATRIX_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "candidate-abstraction bias matrix must not claim benchmark readiness"))
    comparison_count = _validate_comparison_fields(data.get("comparison_fields"), issues)
    abstraction_count = _validate_abstraction_families(data.get("abstraction_families"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim problem-defined abstraction hooks" not in boundary_text
        or "executed equal-budget benchmark results" not in boundary_text
        or "AlphaEvolve-style abstraction-selection evidence" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate design matrix from executed abstraction evidence"))
    return CandidateAbstractionBiasMatrixValidation(
        ok=not issues,
        matrix_status=status if isinstance(status, str) else None,
        abstraction_count=abstraction_count,
        comparison_field_count=comparison_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_candidate_abstraction_bias_matrix_summary(matrix: dict[str, Any]) -> str:
    validation = validate_candidate_abstraction_bias_matrix(matrix)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Candidate abstraction bias matrix",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| matrix_status | {validation.matrix_status or '<unknown>'} |",
        f"| abstraction_count | {validation.abstraction_count} |",
        f"| comparison_field_count | {validation.comparison_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_matrix(
    matrix: object | str | Path,
) -> tuple[dict[str, Any] | None, list[CandidateAbstractionBiasMatrixIssue]]:
    if isinstance(matrix, dict):
        return dict(matrix), []
    if isinstance(matrix, str) and matrix.strip().startswith("{"):
        try:
            data = json.loads(matrix)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"matrix JSON is invalid: {exc}")]
    else:
        try:
            data = json.loads(Path(matrix).read_text(encoding="utf-8"))
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_matrix", f"matrix could not be loaded: {exc}")]
    if isinstance(data, dict):
        return data, []
    return None, [_issue("invalid_shape", "candidate-abstraction bias matrix must be a JSON object")]


def _validate_comparison_fields(
    value: object,
    issues: list[CandidateAbstractionBiasMatrixIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_comparison_fields", "comparison_fields must be a list"))
        return 0
    if value != list(EXPECTED_COMPARISON_FIELDS):
        issues.append(_issue("invalid_comparison_fields", "comparison_fields must preserve the required comparison axes"))
    return len(value)


def _validate_abstraction_families(
    value: object,
    issues: list[CandidateAbstractionBiasMatrixIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_abstraction_families", "abstraction_families must be a list"))
        return 0
    expected = {
        item["abstraction_id"]: item
        for item in candidate_abstraction_bias_matrix_record()["abstraction_families"]
    }
    actual = {
        item.get("abstraction_id"): item
        for item in value
        if isinstance(item, dict) and isinstance(item.get("abstraction_id"), str)
    }
    if tuple(actual) != EXPECTED_ABSTRACTION_IDS:
        issues.append(_issue("invalid_abstraction_family_ids", "abstraction_families must preserve the AlphaEvolve abstraction option order"))
    for abstraction_id, expected_item in expected.items():
        actual_item = actual.get(abstraction_id)
        if actual_item is None:
            issues.append(_issue("missing_abstraction_family", f"missing abstraction family {abstraction_id}"))
            continue
        for field, expected_value in expected_item.items():
            if actual_item.get(field) != expected_value:
                issues.append(_issue(f"invalid_{abstraction_id}_{field}", f"{abstraction_id}.{field} must match the design matrix boundary"))
    return len(value)


def _validate_missing_evidence(
    value: object,
    issues: list[CandidateAbstractionBiasMatrixIssue],
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


def _issue(code: str, message: str) -> CandidateAbstractionBiasMatrixIssue:
    return CandidateAbstractionBiasMatrixIssue(code, message)
