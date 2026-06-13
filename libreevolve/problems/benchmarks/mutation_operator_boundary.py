from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MUTATION_OPERATOR_BOUNDARY_SCHEMA = "libreevolve.alphaevolve_mutation_operator_boundary.v1"
MUTATION_OPERATOR_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.mutation_operator_boundary_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.3", "5")
EXPECTED_BOUNDARY_STATUS = "fixed_edit_payload_grammar_without_operator_family_evidence"
EXPECTED_FIXED_SURFACES = (
    "search_replace_diff",
    "full_replacement",
    "file_sections",
    "block_sections",
    "topology_commands",
    "static_or_binary_sections",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "runtime_report_schema",
    "configured_mutation_mode",
    "payload_surface_counts",
    "sample_generated_candidate_records",
    "proposal_metadata_fields",
    "fixed_edit_grammar_policy",
    "operator_family_declaration_schema",
    "proposal_level_operator_family_provenance",
    "task_or_failure_aware_operator_construction",
    "adaptive_operator_family_selection",
    "operator_family_scoring",
    "operator_family_benchmark_telemetry",
)
EXPECTED_MISSING_EVIDENCE = {
    "operator_family_declaration_schema": "not_recorded_locally",
    "proposal_level_operator_family_provenance": "not_recorded_locally",
    "task_or_failure_aware_operator_construction": "not_recorded_locally",
    "adaptive_operator_family_selection": "not_recorded_locally",
    "operator_family_scoring": "not_recorded_locally",
    "operator_family_benchmark_telemetry": "not_recorded_locally",
}


@dataclass(frozen=True)
class MutationOperatorBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MutationOperatorBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[MutationOperatorBoundaryIssue]


def mutation_operator_boundary_record() -> dict[str, Any]:
    """Return the current AlphaEvolve mutation-operator boundary."""

    return {
        "schema": MUTATION_OPERATOR_BOUNDARY_SCHEMA,
        "runtime_report_schema": MUTATION_OPERATOR_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve Section 2.3 describes LLM-guided creative program "
            "mutation, and Section 5 contrasts that with systems depending on "
            "fixed handwritten mutation or crossover operator sets"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "mutation_operator_boundary_report_available",
        "claim_ready": False,
        "fixed_local_parser_surfaces": list(EXPECTED_FIXED_SURFACES),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve reports configured mutation "
            "mode, fixed edit payload grammar surfaces, proposal metadata "
            "fields, and generated-candidate samples. It does not claim "
            "proposal-level operator-family provenance, LLM-constructed "
            "operator families, task or failure aware operator construction, "
            "adaptive operator-family selection, operator-family scoring, or "
            "benchmark operator telemetry."
        ),
    }


def validate_mutation_operator_boundary(
    boundary: object | str | Path | None = None,
) -> MutationOperatorBoundaryValidation:
    data, read_issues = _load_boundary(
        mutation_operator_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MutationOperatorBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MutationOperatorBoundaryIssue] = []
    if data.get("schema") != MUTATION_OPERATOR_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported mutation-operator boundary schema"))
    if data.get("runtime_report_schema") != MUTATION_OPERATOR_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify mutation-operator reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.3', '5']"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "fixed handwritten mutation" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify the handwritten-operator contrast"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "mutation_operator_boundary_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to mutation-operator reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "mutation-operator boundary must not claim operator-family readiness"))
    _validate_fixed_surfaces(data.get("fixed_local_parser_surfaces"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that operator-family evidence is not claimed"))
    return MutationOperatorBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_mutation_operator_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_mutation_operator_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve mutation-operator boundary",
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
) -> tuple[dict[str, Any] | None, list[MutationOperatorBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "mutation-operator boundary must be a JSON object")]


def _validate_fixed_surfaces(
    value: object,
    issues: list[MutationOperatorBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_fixed_local_parser_surfaces", "fixed_local_parser_surfaces must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_FIXED_SURFACES)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_fixed_local_parser_surface", f"fixed parser surfaces lack entries: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_fixed_local_parser_surface", f"fixed parser surfaces have unknown entries: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_fixed_local_parser_surface", "fixed parser surfaces must be strings"))
    return len(seen)


def _validate_required_fields(
    value: object,
    issues: list[MutationOperatorBoundaryIssue],
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
    issues: list[MutationOperatorBoundaryIssue],
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


def _issue(code: str, message: str) -> MutationOperatorBoundaryIssue:
    return MutationOperatorBoundaryIssue(code, message)
