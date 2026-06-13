from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_candidate_language_runner_boundary.v1"
)
CANDIDATE_LANGUAGE_POLICY_SCHEMA = "libreevolve.candidate_language_policy.v1"
CANDIDATE_LANGUAGE_RUNNER_CONTRACT_REPORT_SCHEMA = (
    "libreevolve.candidate_language_runner_contract_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.1", "2.2")
EXPECTED_BOUNDARY_STATUS = "python_primary_without_arbitrary_language_runner_evidence"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "candidate_language",
    "runner_id",
    "runner_kind",
    "marker_grammar_id",
    "validator_runner_contract",
    "build_system_contract",
    "build_command",
    "runtime_command",
    "dependency_manifest",
    "declared_workspace_path_match",
    "generated_artifact_path",
    "generated_artifact_hash",
    "language_runner_ready",
    "build_runner_ready",
    "task_abstraction_hook",
    "runner_environment_provenance",
)
EXPECTED_MISSING_EVIDENCE = {
    "configured_non_python_language_runners": (
        "metadata_declarations_and_workspace_matches_recorded_execution_not_supported"
    ),
    "build_system_runner_contracts": (
        "metadata_declarations_and_workspace_matches_recorded_runner_contract_not_supported"
    ),
    "language_aware_marker_grammars": "not_recorded_locally",
    "arbitrary_language_validator_contracts": "not_recorded_locally",
    "task_defined_candidate_abstraction_hooks": "not_recorded_locally",
    "runner_environment_artifacts": (
        "current_python_runner_environment_link_recorded_arbitrary_runner_artifacts_not_recorded"
    ),
    "generated_build_artifact_records": "not_recorded_locally",
}


@dataclass(frozen=True)
class CandidateLanguageRunnerBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CandidateLanguageRunnerBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CandidateLanguageRunnerBoundaryIssue]


def candidate_language_runner_boundary_record() -> dict[str, Any]:
    """Return the current arbitrary-language/build-runner absence boundary."""

    return {
        "schema": CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_SCHEMA,
        "policy_schema": CANDIDATE_LANGUAGE_POLICY_SCHEMA,
        "runtime_report_schema": CANDIDATE_LANGUAGE_RUNNER_CONTRACT_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "tasks define the program artifact and evaluator interface, and "
            "AlphaEvolve can operate on existing codebases and task-specific "
            "program representations rather than only one Python-primary "
            "workspace shape"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "candidate_language_runner_contract_report_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
        "This boundary records that LibreEvolve has a validated "
        "Python-primary candidate-language policy and runtime runner "
        "contract report with metadata-only non-Python language and build "
        "declaration evidence plus retained-workspace path-match evidence "
        "when configured and current Python-runner environment linkage, but "
        "does not claim AlphaEvolve-style "
        "arbitrary language or build-system runner execution evidence with "
            "language-aware marker grammars, executable build contracts, "
            "task-defined abstraction hooks, arbitrary-runner environment "
            "artifacts, or generated build artifacts."
        ),
    }


def validate_candidate_language_runner_boundary(
    boundary: object | str | Path | None = None,
) -> CandidateLanguageRunnerBoundaryValidation:
    data, read_issues = _load_boundary(
        candidate_language_runner_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CandidateLanguageRunnerBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CandidateLanguageRunnerBoundaryIssue] = []
    if data.get("schema") != CANDIDATE_LANGUAGE_RUNNER_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported candidate language runner boundary schema"))
    if data.get("policy_schema") != CANDIDATE_LANGUAGE_POLICY_SCHEMA:
        issues.append(_issue("invalid_policy_schema", "policy schema must identify candidate-language policies"))
    if data.get("runtime_report_schema") != CANDIDATE_LANGUAGE_RUNNER_CONTRACT_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify candidate-language runner reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be ['2.1', '2.2']"))
    if not isinstance(data.get("source_claim"), str) or "existing codebases" not in data["source_claim"]:
        issues.append(_issue("invalid_source_claim", "source_claim must identify existing-codebase program artifacts"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "candidate_language_runner_contract_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to candidate-language runner contract reports"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "candidate language runner boundary must not claim paper readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if not isinstance(boundary_text, str) or "does not claim" not in boundary_text:
        issues.append(_issue("missing_claim_boundary", "claim_boundary must state that this does not claim arbitrary-language runner evidence"))
    return CandidateLanguageRunnerBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_candidate_language_runner_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_candidate_language_runner_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve candidate language runner boundary",
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
) -> tuple[dict[str, Any] | None, list[CandidateLanguageRunnerBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "candidate language runner boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[CandidateLanguageRunnerBoundaryIssue],
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
    issues: list[CandidateLanguageRunnerBoundaryIssue],
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


def _issue(code: str, message: str) -> CandidateLanguageRunnerBoundaryIssue:
    return CandidateLanguageRunnerBoundaryIssue(code, message)
