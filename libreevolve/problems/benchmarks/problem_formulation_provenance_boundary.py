from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROBLEM_FORMULATION_PROVENANCE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_problem_formulation_provenance_boundary.v1"
)
PROBLEM_FORMULATION_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.problem_formulation_provenance_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("3.2",)
EXPECTED_BOUNDARY_STATUS = "metadata_contract_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "metadata_present",
    "expert_contributor_roles_recorded",
    "formulation_notes_recorded",
    "objective_rationale_recorded",
    "evaluator_rationale_recorded",
    "parameter_scope_recorded",
    "background_knowledge_linkage_recorded",
    "expert_review_or_domain_owner_signoff",
    "alphaevolve_expert_guided_formulation_parity",
    "benchmark_fixture_linkage",
    "paper_facing_certification_rows",
    "constructive_math_fixture_formulation_records",
    "matrix_fixture_formulation_records",
    "review_signoff_artifact_links",
)
EXPECTED_MISSING_EVIDENCE = {
    "matrix_fixture_expert_reviewed_formulation": "not_recorded_locally",
    "constructive_math_fixture_expert_reviewed_formulation": "not_recorded_locally",
    "paper_facing_certification_rows": "not_recorded_locally",
    "review_signoff_artifact_links": "not_recorded_locally",
    "benchmark_fixture_formulation_result_linkage": "not_recorded_locally",
    "alphaevolve_expert_guided_formulation_parity": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProblemFormulationProvenanceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProblemFormulationProvenanceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ProblemFormulationProvenanceBoundaryIssue]


def problem_formulation_provenance_boundary_record() -> dict[str, Any]:
    """Return the current expert-formulation provenance boundary."""

    return {
        "schema": PROBLEM_FORMULATION_PROVENANCE_BOUNDARY_SCHEMA,
        "runtime_report_schema": PROBLEM_FORMULATION_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 3.2 reports external mathematicians suggesting "
            "problems and advising how to formulate them, so paper-facing "
            "mathematical benchmark claims need populated expert-guided "
            "formulation evidence rather than only a metadata schema"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "problem_formulation_provenance_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has an optional formulation "
            "metadata contract and runtime provenance report for contributor "
            "roles, formulation notes, objective/evaluator rationale, parameter "
            "scope, background references, and review/signoff readiness, but "
            "does not claim populated expert-reviewed matrix or constructive-"
            "math benchmark formulation records, paper-facing certification "
            "rows, review/signoff artifact links, benchmark-result linkage, or "
            "AlphaEvolve expert-guided formulation parity."
        ),
    }


def validate_problem_formulation_provenance_boundary(
    boundary: object | str | Path | None = None,
) -> ProblemFormulationProvenanceBoundaryValidation:
    data, read_issues = _load_boundary(
        problem_formulation_provenance_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return ProblemFormulationProvenanceBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[ProblemFormulationProvenanceBoundaryIssue] = []
    if data.get("schema") != PROBLEM_FORMULATION_PROVENANCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported problem formulation provenance boundary schema"))
    if data.get("runtime_report_schema") != PROBLEM_FORMULATION_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify problem formulation provenance reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['3.2']"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "Section 3.2" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve Section 3.2 formulation evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "problem_formulation_provenance_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to formulation provenance reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "problem formulation boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim expert-guided formulation parity"))
    return ProblemFormulationProvenanceBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_problem_formulation_provenance_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_problem_formulation_provenance_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve problem-formulation provenance boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ProblemFormulationProvenanceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "problem formulation provenance boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ProblemFormulationProvenanceBoundaryIssue],
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
    issues: list[ProblemFormulationProvenanceBoundaryIssue],
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


def _issue(code: str, message: str) -> ProblemFormulationProvenanceBoundaryIssue:
    return ProblemFormulationProvenanceBoundaryIssue(code, message)
