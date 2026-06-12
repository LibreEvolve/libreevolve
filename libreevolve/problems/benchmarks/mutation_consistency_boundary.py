from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


MUTATION_CONSISTENCY_BOUNDARY_SCHEMA = "libreevolve.mutation_consistency_boundary.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RUNTIME_REPORT_SCHEMA = "libreevolve.mutation_consistency_report.v1"
EXPECTED_BOUNDARY_STATUS = "diagnostic_multi_edit_consistency_scan_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "multi_edit_candidate_inventory",
    "changed_structured_edit_units",
    "changed_file_or_block_ids",
    "diagnostic_cochange_links",
    "best_effort_python_symbol_scan",
    "unresolved_reference_diagnostics",
    "evaluator_failure_taxonomy_linkage",
    "candidate_status_and_admission_records",
    "language_aware_scope_resolution",
    "config_resource_dependency_models",
    "required_companion_edit_inference",
    "cross_file_dataflow_or_import_resolution",
    "benchmark_calibrated_consistency_failures",
    "hard_or_configurable_acceptance_gate",
    "semantic_consistency_proof",
)
EXPECTED_MISSING_EVIDENCE = {
    "language_aware_scope_resolution": "not_recorded_locally",
    "config_resource_dependency_models": "not_recorded_locally",
    "required_companion_edit_inference": "not_recorded_locally",
    "cross_file_dataflow_or_import_resolution": "not_recorded_locally",
    "benchmark_calibrated_consistency_failures": "not_recorded_locally",
    "hard_or_configurable_acceptance_gate": "not_recorded_locally",
    "semantic_consistency_proof": "not_recorded_locally",
}


@dataclass(frozen=True)
class MutationConsistencyBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class MutationConsistencyBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[MutationConsistencyBoundaryIssue]


def mutation_consistency_boundary_record() -> dict[str, Any]:
    """Return the mutation consistency diagnostics versus proof/gating boundary."""

    return {
        "schema": MUTATION_CONSISTENCY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve prompts require proposed SEARCH/REPLACE edits to be "
            "consistent with each other, including companion edits such as "
            "adding a config variable when another replacement uses it"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_schema": EXPECTED_RUNTIME_REPORT_SCHEMA,
        "runtime_report_status": "mutation_consistency_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve manifests include "
            "runtime.history.mutation_consistency_report for generated "
            "multi-edit candidate inventories, changed structured edit units, "
            "changed file or block ids, diagnostic cochange links, best-effort "
            "Python symbol scans, unresolved-reference diagnostics, evaluator "
            "failure-taxonomy linkage, and candidate status/admission records. "
            "It does not claim language-aware scope resolution, config or "
            "resource dependency models, required companion-edit inference, "
            "cross-file dataflow or import resolution, benchmark-calibrated "
            "consistency failures, hard or configurable acceptance gates, or "
            "semantic consistency proof."
        ),
    }


def validate_mutation_consistency_boundary(
    boundary: object | str | Path | None = None,
) -> MutationConsistencyBoundaryValidation:
    data, read_issues = _load_boundary(
        mutation_consistency_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return MutationConsistencyBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[MutationConsistencyBoundaryIssue] = []
    if data.get("schema") != MUTATION_CONSISTENCY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported mutation consistency boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "SEARCH/REPLACE edits" not in source_claim
        or "companion edits" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must identify cross-edit consistency and companion edits"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_schema") != EXPECTED_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", f"runtime_report_schema must be {EXPECTED_RUNTIME_REPORT_SCHEMA}"))
    if data.get("runtime_report_status") != "mutation_consistency_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to mutation consistency diagnostics"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "mutation consistency boundary must not claim complete consistency proof"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim language-aware scope resolution" not in boundary_text
        or "required companion-edit inference" not in boundary_text
        or "semantic consistency proof" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate diagnostics from semantic consistency proof and gating"))
    return MutationConsistencyBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_mutation_consistency_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_mutation_consistency_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Mutation consistency boundary",
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
) -> tuple[dict[str, Any] | None, list[MutationConsistencyBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "mutation consistency boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[MutationConsistencyBoundaryIssue],
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
    issues: list[MutationConsistencyBoundaryIssue],
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


def _issue(code: str, message: str) -> MutationConsistencyBoundaryIssue:
    return MutationConsistencyBoundaryIssue(code, message)
