from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


INITIAL_PROGRAM_VALIDITY_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_initial_program_validity_boundary.v1"
)
INITIAL_PROGRAM_VALIDITY_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.initial_program_validity_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "strict_policy_available"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "initial_program_validity_policy_recorded",
    "generation_zero_seed_validity_recorded",
    "declared_metric_presence_recorded",
    "archive_admission_state_recorded",
    "strict_policy_available",
    "strict_stop_reason_recorded",
    "all_selected_seeds_evaluator_valid",
    "all_selected_seeds_declared_metrics_present",
    "alphaevolve_complete_initial_program_parity",
    "strict_policy_fixture_report",
    "paper_facing_certification_rows",
)
EXPECTED_MISSING_EVIDENCE = {
    "repo_default_strict_policy": "not_default",
    "benchmark_suite_strict_policy_runs": "embedded_evaluate_math_smoke_only",
    "paper_facing_certification_rows": "not_recorded_locally",
    "alphaevolve_complete_initial_program_parity_default_run": "not_recorded_locally",
}


@dataclass(frozen=True)
class InitialProgramValidityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class InitialProgramValidityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[InitialProgramValidityBoundaryIssue]


def initial_program_validity_boundary_record() -> dict[str, Any]:
    """Return the paper-facing initial-program validity boundary."""

    return {
        "schema": INITIAL_PROGRAM_VALIDITY_BOUNDARY_SCHEMA,
        "runtime_report_schema": INITIAL_PROGRAM_VALIDITY_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve Section 2.1 describes the user-provided code inside "
            "evolvable blocks as a complete initial solution that is runnable "
            "through the supplied task skeleton and evaluator before evolution"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "initial_program_validity_report_available",
        "claim_ready": False,
        "strict_policy": "alphaevolve_strict",
        "default_policy": "permissive_baseline",
        "strict_stop_reason": "invalid_initial_programs",
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve exposes an "
            "alphaevolve_strict initial-program validity policy and runtime "
            "report for seed evaluator validity, declared metric presence, "
            "archive admission state, strict valid/invalid counts, and strict "
            "stop evidence. The embedded_evaluate_math fixture is a strict "
            "single-seed smoke fixture, not a benchmark-suite certification "
            "row. Strict runtime reports can be claim-ready only for configured "
            "strict runs where every selected seed is evaluator-valid and "
            "metric-complete. The default permissive baseline keeps invalid "
            "seeds as diagnostics and does not claim AlphaEvolve complete "
            "initial-program parity."
        ),
    }


def validate_initial_program_validity_boundary(
    boundary: object | str | Path | None = None,
) -> InitialProgramValidityBoundaryValidation:
    data, read_issues = _load_boundary(
        initial_program_validity_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return InitialProgramValidityBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[InitialProgramValidityBoundaryIssue] = []
    if data.get("schema") != INITIAL_PROGRAM_VALIDITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported initial-program validity boundary schema"))
    if data.get("runtime_report_schema") != INITIAL_PROGRAM_VALIDITY_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify initial-program validity reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "Section 2.1" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve complete initial solution evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "initial_program_validity_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to initial-program validity reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "initial-program validity boundary must not claim paper readiness by default"))
    if data.get("strict_policy") != "alphaevolve_strict":
        issues.append(_issue("invalid_strict_policy", "strict_policy must be alphaevolve_strict"))
    if data.get("default_policy") != "permissive_baseline":
        issues.append(_issue("invalid_default_policy", "default_policy must remain permissive_baseline"))
    if data.get("strict_stop_reason") != "invalid_initial_programs":
        issues.append(_issue("invalid_strict_stop_reason", "strict_stop_reason must be invalid_initial_programs"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "default permissive baseline" not in boundary_text
        or "does not claim AlphaEvolve complete initial-program parity" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must keep default permissive runs outside AlphaEvolve initial-program parity"))
    return InitialProgramValidityBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_initial_program_validity_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_initial_program_validity_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve initial-program validity boundary",
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
) -> tuple[dict[str, Any] | None, list[InitialProgramValidityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "initial-program validity boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[InitialProgramValidityBoundaryIssue],
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
    issues: list[InitialProgramValidityBoundaryIssue],
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


def _issue(code: str, message: str) -> InitialProgramValidityBoundaryIssue:
    return InitialProgramValidityBoundaryIssue(code, message)
