from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CANDIDATE_ABSTRACTION_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_candidate_abstraction_boundary.v1"
CANDIDATE_ABSTRACTION_RUNTIME_REPORT_SCHEMA = "libreevolve.candidate_abstraction_choice_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_ID = "2.1"
EXPECTED_SOURCE_SECTION_IDS = ("2.1", "Discussion")
EXPECTED_BOUNDARY_STATUS = "not_configured_as_problem_defined_abstractions"
EXPECTED_SELECTED_ABSTRACTION = "code_file_set"
EXPECTED_ABSTRACTION_OPTION_IDS = (
    "direct_solution",
    "constructor_function",
    "bespoke_search_algorithm",
    "coevolved_solution_and_search",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "problem_abstraction_rationale",
    "symmetry_structure_assumptions",
    "problem_defined_serializer_hook",
    "problem_defined_materializer_hook",
    "problem_defined_runner_hook",
    "paired_solution_search_representation",
    "direct_solution_benchmark_report",
    "constructor_function_benchmark_report",
    "bespoke_search_algorithm_benchmark_report",
    "equal_budget_bias_comparison_report",
)
EXPECTED_MISSING_EVIDENCE = {
    "problem_abstraction_rationale": "not_recorded_locally",
    "symmetry_structure_assumptions": "not_recorded_locally",
    "problem_defined_candidate_abstraction_hooks": "not_configured",
    "paired_solution_search_representation": "not_supported",
    "direct_constructor_search_equal_budget_comparisons": "not_recorded_locally",
    "benchmark_bias_report": "not_recorded_locally",
}


@dataclass(frozen=True)
class CandidateAbstractionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CandidateAbstractionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    selected_abstraction: str | None
    abstraction_option_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CandidateAbstractionBoundaryIssue]


def candidate_abstraction_boundary_record() -> dict[str, Any]:
    """Return the current candidate-abstraction and bias-evidence boundary."""

    return {
        "schema": CANDIDATE_ABSTRACTION_BOUNDARY_SCHEMA,
        "runtime_report_schema": CANDIDATE_ABSTRACTION_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_id": EXPECTED_SOURCE_SECTION_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_discussion_ref": "Discussion",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "candidate_abstraction_choice_report_available",
        "selected_abstraction": EXPECTED_SELECTED_ABSTRACTION,
        "selected_representation": "python_primary_code_file_set",
        "claim_ready": False,
        "abstraction_options": [
            {
                "option_id": "direct_solution",
                "paper_role": "search for solutions directly",
                "local_status": "supported_as_python_file_or_workspace",
                "typed_abstraction_api": "not_configured",
                "bias_evidence": "not_recorded_locally",
                "equal_budget_benchmark": "not_recorded_locally",
            },
            {
                "option_id": "constructor_function",
                "paper_role": "evolve constructor functions",
                "local_status": "not_distinguished_from_python_workspace",
                "typed_abstraction_api": "not_configured",
                "bias_evidence": "not_recorded_locally",
                "equal_budget_benchmark": "not_recorded_locally",
            },
            {
                "option_id": "bespoke_search_algorithm",
                "paper_role": "evolve bespoke search algorithms",
                "local_status": "not_distinguished_from_python_workspace",
                "typed_abstraction_api": "not_configured",
                "bias_evidence": "not_recorded_locally",
                "equal_budget_benchmark": "not_recorded_locally",
            },
            {
                "option_id": "coevolved_solution_and_search",
                "paper_role": "co-evolve intermediate solutions and search algorithms",
                "local_status": "unsupported",
                "typed_abstraction_api": "not_configured",
                "bias_evidence": "not_recorded_locally",
                "equal_budget_benchmark": "not_recorded_locally",
            },
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records LibreEvolve's current code-file-set candidate "
            "representation and runtime abstraction-choice report, but does not "
            "claim AlphaEvolve-style problem-defined candidate abstractions, "
            "paired solution/search representations, abstraction-rationale "
            "metadata, symmetry/bias evidence, or equal-budget comparisons across "
            "direct-solution, constructor-function, and bespoke-search-algorithm "
            "approaches."
        ),
    }


def validate_candidate_abstraction_boundary(
    boundary: object | str | Path | None = None,
) -> CandidateAbstractionBoundaryValidation:
    data, read_issues = _load_boundary(
        candidate_abstraction_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CandidateAbstractionBoundaryValidation(False, None, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CandidateAbstractionBoundaryIssue] = []
    if data.get("schema") != CANDIDATE_ABSTRACTION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported candidate-abstraction boundary schema"))
    if data.get("runtime_report_schema") != CANDIDATE_ABSTRACTION_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify candidate-abstraction reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_id") != EXPECTED_SOURCE_SECTION_ID:
        issues.append(_issue("invalid_source_section_id", "source_section_id must be 2.1"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.1', 'Discussion']"))
    if data.get("source_discussion_ref") != "Discussion":
        issues.append(_issue("invalid_source_discussion_ref", "source_discussion_ref must identify the Discussion"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "candidate_abstraction_choice_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to abstraction-choice reports"))
    selected = data.get("selected_abstraction")
    if selected != EXPECTED_SELECTED_ABSTRACTION:
        issues.append(_issue("invalid_selected_abstraction", "selected_abstraction must remain code_file_set"))
    if data.get("selected_representation") != "python_primary_code_file_set":
        issues.append(_issue("invalid_selected_representation", "selected_representation must remain python_primary_code_file_set"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "candidate-abstraction boundary must not claim paper readiness"))
    option_count = _validate_abstraction_options(data.get("abstraction_options"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim AlphaEvolve abstraction parity"))
    return CandidateAbstractionBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        selected_abstraction=selected if isinstance(selected, str) else None,
        abstraction_option_count=option_count,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_candidate_abstraction_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_candidate_abstraction_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve candidate-abstraction boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| selected_abstraction | {validation.selected_abstraction or '<unknown>'} |",
        f"| abstraction_option_count | {validation.abstraction_option_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[CandidateAbstractionBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "candidate-abstraction boundary must be a JSON object")]


def _validate_abstraction_options(
    value: object,
    issues: list[CandidateAbstractionBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_abstraction_options", "abstraction_options must be a list"))
        return 0
    ids = [item.get("option_id") for item in value if isinstance(item, dict)]
    if tuple(ids) != EXPECTED_ABSTRACTION_OPTION_IDS:
        issues.append(_issue("invalid_abstraction_option_ids", "abstraction_options must preserve the paper abstraction option set"))
    for item in value:
        if not isinstance(item, dict):
            issues.append(_issue("invalid_abstraction_option", "abstraction options must be objects"))
            continue
        option_id = item.get("option_id")
        if option_id not in EXPECTED_ABSTRACTION_OPTION_IDS:
            continue
        if item.get("typed_abstraction_api") != "not_configured":
            issues.append(_issue("typed_abstraction_api_overclaim", "typed abstraction APIs must remain not_configured"))
        if item.get("bias_evidence") != "not_recorded_locally":
            issues.append(_issue("bias_evidence_overclaim", "bias evidence must remain not_recorded_locally"))
        if item.get("equal_budget_benchmark") != "not_recorded_locally":
            issues.append(_issue("equal_budget_benchmark_overclaim", "equal-budget benchmarks must remain not_recorded_locally"))
    return len(value)


def _validate_required_fields(
    value: object,
    issues: list[CandidateAbstractionBoundaryIssue],
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
    issues: list[CandidateAbstractionBoundaryIssue],
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


def _issue(code: str, message: str) -> CandidateAbstractionBoundaryIssue:
    return CandidateAbstractionBoundaryIssue(code, message)
