from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


INITIAL_PROGRAM_SEED_VARIANT_MATRIX_SCHEMA = (
    "libreevolve.alphaevolve_initial_program_seed_variant_matrix.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.1", "3.1")
EXPECTED_MATRIX_STATUS = "design_matrix_without_equal_budget_seed_results"
EXPECTED_VARIANT_IDS = (
    "simple_initial_program",
    "random_initial_program",
    "researcher_idea_initial_program",
    "stochastic_evaluation_idea",
    "evolutionary_approach_idea",
)
EXPECTED_COMPARISON_FIELDS = (
    "seed_variant_id",
    "idea_origin",
    "paper_role",
    "prompt_context_linkage",
    "generation_zero_metric_linkage",
    "equal_budget_result_table",
    "human_contribution_review",
    "benchmark_scope",
)
EXPECTED_MISSING_EVIDENCE = {
    "prompt_context_linkage": "not_recorded_locally",
    "equal_budget_seed_variant_results": "not_recorded_locally",
    "simple_random_researcher_comparison": "not_recorded_locally",
    "matrix_seed_variant_result_tables": "not_recorded_locally",
    "constructive_math_seed_variant_result_tables": "not_recorded_locally",
    "human_contribution_review_or_signoff": "not_recorded_locally",
    "alphaevolve_human_seeded_benchmark_parity": "not_recorded_locally",
}


@dataclass(frozen=True)
class InitialProgramSeedVariantMatrixIssue:
    code: str
    message: str


@dataclass(frozen=True)
class InitialProgramSeedVariantMatrixValidation:
    ok: bool
    matrix_status: str | None
    variant_count: int
    comparison_field_count: int
    missing_evidence_count: int
    issues: list[InitialProgramSeedVariantMatrixIssue]


def initial_program_seed_variant_matrix_record() -> dict[str, Any]:
    """Return the current seed-variant comparison design matrix."""

    return {
        "schema": INITIAL_PROGRAM_SEED_VARIANT_MATRIX_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "matrix_status": EXPECTED_MATRIX_STATUS,
        "claim_ready": False,
        "comparison_fields": list(EXPECTED_COMPARISON_FIELDS),
        "seed_variants": [
            {
                "seed_variant_id": "simple_initial_program",
                "idea_origin": "simple_baseline",
                "paper_role": "most Table 2 matrix results used a simple initial program",
                "prompt_context_linkage": "not_recorded_locally",
                "generation_zero_metric_linkage": "metadata_contract_only",
                "equal_budget_result_table": "not_recorded_locally",
                "human_contribution_review": "not_recorded_locally",
                "benchmark_scope": "matrix_and_constructive_math_future_comparison_axis",
            },
            {
                "seed_variant_id": "random_initial_program",
                "idea_origin": "random_or_uninformed_start",
                "paper_role": "comparison baseline for seed sensitivity",
                "prompt_context_linkage": "not_recorded_locally",
                "generation_zero_metric_linkage": "metadata_contract_only",
                "equal_budget_result_table": "not_recorded_locally",
                "human_contribution_review": "not_recorded_locally",
                "benchmark_scope": "matrix_and_constructive_math_future_comparison_axis",
            },
            {
                "seed_variant_id": "researcher_idea_initial_program",
                "idea_origin": "researcher_seeded_idea",
                "paper_role": "researchers seeded some initial programs with their own ideas",
                "prompt_context_linkage": "not_recorded_locally",
                "generation_zero_metric_linkage": "metadata_contract_only",
                "equal_budget_result_table": "not_recorded_locally",
                "human_contribution_review": "not_recorded_locally",
                "benchmark_scope": "matrix_seed_variant_future_comparison_axis",
            },
            {
                "seed_variant_id": "stochastic_evaluation_idea",
                "idea_origin": "researcher_seeded_stochastic_evaluation",
                "paper_role": "one reported researcher idea class for improved matrix parameters",
                "prompt_context_linkage": "not_recorded_locally",
                "generation_zero_metric_linkage": "metadata_contract_only",
                "equal_budget_result_table": "not_recorded_locally",
                "human_contribution_review": "not_recorded_locally",
                "benchmark_scope": "matrix_seed_variant_future_comparison_axis",
            },
            {
                "seed_variant_id": "evolutionary_approach_idea",
                "idea_origin": "researcher_seeded_evolutionary_approach",
                "paper_role": "one reported researcher idea class for improved matrix parameters",
                "prompt_context_linkage": "not_recorded_locally",
                "generation_zero_metric_linkage": "metadata_contract_only",
                "equal_budget_result_table": "not_recorded_locally",
                "human_contribution_review": "not_recorded_locally",
                "benchmark_scope": "matrix_seed_variant_future_comparison_axis",
            },
        ],
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This matrix records paper-derived initial-program seed-variant "
            "families and comparison axes for future simple, random, and "
            "researcher-idea start comparisons. It does not claim prompt "
            "context linkage, equal-budget seed-variant result tables, matrix "
            "or constructive-math seed-variant reports, human contribution "
            "review/signoff, or AlphaEvolve human-seeded benchmark parity."
        ),
    }


def validate_initial_program_seed_variant_matrix(
    matrix: object | str | Path | None = None,
) -> InitialProgramSeedVariantMatrixValidation:
    data, read_issues = _load_matrix(
        initial_program_seed_variant_matrix_record() if matrix is None else matrix
    )
    if read_issues:
        return InitialProgramSeedVariantMatrixValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[InitialProgramSeedVariantMatrixIssue] = []
    if data.get("schema") != INITIAL_PROGRAM_SEED_VARIANT_MATRIX_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported initial-program seed-variant matrix schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.1', '3.1']"))
    status = data.get("matrix_status")
    if status != EXPECTED_MATRIX_STATUS:
        issues.append(_issue("invalid_matrix_status", f"matrix_status must be {EXPECTED_MATRIX_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "seed-variant matrix must not claim benchmark readiness"))
    comparison_count = _validate_comparison_fields(data.get("comparison_fields"), issues)
    variant_count = _validate_seed_variants(data.get("seed_variants"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim prompt context linkage" not in boundary_text
        or "equal-budget seed-variant result tables" not in boundary_text
        or "AlphaEvolve human-seeded benchmark parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate seed-variant design matrix from benchmark parity"))
    return InitialProgramSeedVariantMatrixValidation(
        ok=not issues,
        matrix_status=status if isinstance(status, str) else None,
        variant_count=variant_count,
        comparison_field_count=comparison_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_initial_program_seed_variant_matrix_summary(
    matrix: dict[str, Any],
) -> str:
    validation = validate_initial_program_seed_variant_matrix(matrix)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Initial-program seed-variant matrix",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| matrix_status | {validation.matrix_status or '<unknown>'} |",
        f"| variant_count | {validation.variant_count} |",
        f"| comparison_field_count | {validation.comparison_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_matrix(
    matrix: object | str | Path,
) -> tuple[dict[str, Any] | None, list[InitialProgramSeedVariantMatrixIssue]]:
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
    return None, [_issue("invalid_shape", "initial-program seed-variant matrix must be a JSON object")]


def _validate_comparison_fields(
    value: object,
    issues: list[InitialProgramSeedVariantMatrixIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_comparison_fields", "comparison_fields must be a list"))
        return 0
    if value != list(EXPECTED_COMPARISON_FIELDS):
        issues.append(_issue("invalid_comparison_fields", "comparison_fields must preserve the required seed-variant axes"))
    return len(value)


def _validate_seed_variants(
    value: object,
    issues: list[InitialProgramSeedVariantMatrixIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_seed_variants", "seed_variants must be a list"))
        return 0
    expected = {
        item["seed_variant_id"]: item
        for item in initial_program_seed_variant_matrix_record()["seed_variants"]
    }
    actual = {
        item.get("seed_variant_id"): item
        for item in value
        if isinstance(item, dict) and isinstance(item.get("seed_variant_id"), str)
    }
    if tuple(actual) != EXPECTED_VARIANT_IDS:
        issues.append(_issue("invalid_seed_variant_ids", "seed_variants must preserve the paper-derived seed variant order"))
    for variant_id, expected_item in expected.items():
        actual_item = actual.get(variant_id)
        if actual_item is None:
            issues.append(_issue("missing_seed_variant", f"missing seed variant {variant_id}"))
            continue
        for field, expected_value in expected_item.items():
            if actual_item.get(field) != expected_value:
                issues.append(_issue(f"invalid_{variant_id}_{field}", f"{variant_id}.{field} must match the seed-variant matrix boundary"))
    return len(value)


def _validate_missing_evidence(
    value: object,
    issues: list[InitialProgramSeedVariantMatrixIssue],
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


def _issue(code: str, message: str) -> InitialProgramSeedVariantMatrixIssue:
    return InitialProgramSeedVariantMatrixIssue(code, message)
