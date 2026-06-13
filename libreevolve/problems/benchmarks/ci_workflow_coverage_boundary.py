from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


CI_WORKFLOW_COVERAGE_BOUNDARY_SCHEMA = (
    "libreevolve.ci_workflow_coverage_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "path_scoped_ubuntu_workflow_only"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "workflow_dispatch_trigger",
    "push_pull_request_path_filters",
    "secret_scan_job",
    "python_311_unit_job",
    "python_312_unit_job",
    "optional_integration_job",
    "docs_papers_todo_path_filters",
    "workflow_shape_unit_tests",
    "paper_manifest_ci_job",
    "docs_semantic_claim_verifier",
    "wheel_sdist_ci_smoke",
    "cross_platform_ci_matrix",
    "branch_policy",
    "notification_policy",
)
EXPECTED_MISSING_EVIDENCE = {
    "paper_manifest_ci_job": "committed_manifest_only_no_local_pdf_cache",
    "docs_semantic_claim_verifier": "not_recorded_locally",
    "cross_platform_ci_matrix": "not_recorded_locally",
    "branch_policy": "not_recorded_locally",
    "notification_policy": "not_recorded_locally",
}
EXPECTED_PARTIAL_EVIDENCE = {
    "wheel_sdist_ci_smoke": "release_artifact_job_with_representative_package_data_smoke",
}


@dataclass(frozen=True)
class CiWorkflowCoverageBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class CiWorkflowCoverageBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[CiWorkflowCoverageBoundaryIssue]


def ci_workflow_coverage_boundary_record() -> dict[str, Any]:
    """Return the current CI workflow coverage boundary."""

    return {
        "schema": CI_WORKFLOW_COVERAGE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve-scale engineering evidence should be backed by "
            "repeatable validation over code, documentation, paper evidence, "
            "packaging, and supported runtime environments"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "github_actions_workflow_shape_tests_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "partial_evidence": dict(EXPECTED_PARTIAL_EVIDENCE),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has a path-scoped GitHub "
            "Actions workflow with manual dispatch, push/pull_request path "
            "filters, a secret scan job, Python 3.11/3.12 Ubuntu unit jobs, an "
            "optional credential-gated integration job, a committed-manifest "
            "paper/docs job that does not require the ignored local PDF cache, "
            "a release-artifact smoke job that builds a wheel and sdist and "
            "installs the wheel for CLI smoke checks with representative "
            "package-data inspection, and unit tests that check the workflow "
            "shape. It does not claim CI local-PDF paper-manifest checks, "
            "semantic documentation-claim verification, release provenance or "
            "complete package-data certification, cross-platform CI "
            "coverage, branch policy, or notification policy."
        ),
    }


def validate_ci_workflow_coverage_boundary(
    boundary: object | str | Path | None = None,
) -> CiWorkflowCoverageBoundaryValidation:
    data, read_issues = _load_boundary(
        ci_workflow_coverage_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return CiWorkflowCoverageBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[CiWorkflowCoverageBoundaryIssue] = []
    if data.get("schema") != CI_WORKFLOW_COVERAGE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported CI workflow coverage boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "repeatable validation" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify repeatable validation evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "github_actions_workflow_shape_tests_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to workflow-shape tests"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "CI workflow boundary must not claim full CI readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    _validate_partial_evidence(data.get("partial_evidence"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "committed-manifest paper/docs job" not in boundary_text
        or "release-artifact smoke job" not in boundary_text
        or "representative package-data inspection" not in boundary_text
        or "does not claim CI local-PDF paper-manifest checks" not in boundary_text
        or "cross-platform CI coverage" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must keep current path-scoped CI separate from full validation coverage"))
    return CiWorkflowCoverageBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_ci_workflow_coverage_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_ci_workflow_coverage_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "CI workflow coverage boundary",
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
) -> tuple[dict[str, Any] | None, list[CiWorkflowCoverageBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "CI workflow coverage boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[CiWorkflowCoverageBoundaryIssue],
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
    issues: list[CiWorkflowCoverageBoundaryIssue],
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


def _validate_partial_evidence(
    value: object,
    issues: list[CiWorkflowCoverageBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_partial_evidence", "partial_evidence must be an object"))
        return 0
    expected_keys = set(EXPECTED_PARTIAL_EVIDENCE)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_partial_evidence_key", f"partial_evidence lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_partial_evidence_key", f"partial_evidence has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_PARTIAL_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_partial_evidence_{key}", f"partial_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> CiWorkflowCoverageBoundaryIssue:
    return CiWorkflowCoverageBoundaryIssue(code, message)
