from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SYSTEM_CONTRIBUTION_PROVENANCE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_system_contribution_provenance_boundary.v1"
)
SYSTEM_CONTRIBUTION_RUNTIME_REPORT_SCHEMA = (
    "libreevolve.system_contribution_provenance_report.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "system_contribution_claim_ready"
EXPECTED_FIXTURE_PATH = "libreevolve/problems/examples/matrix_multiplication/system_contributions.yaml"
EXPECTED_REQUIRED_PHASES = (
    "initial_design",
    "project_vision_scoping",
    "first_benchmark_iteration",
    "final_system",
    "infrastructure",
    "code_review",
    "team_coordination",
    "supervision",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "metadata_present",
    "all_required_phases_recorded",
    "artifact_or_module_links_recorded",
    "source_pages_recorded",
    "review_scopes_recorded",
    "privacy_policy_recorded",
    "contribution_roles_review_or_owner_signoff",
    "git_history_boundary_separated",
    "package_metadata_boundary_separated",
    "publication_author_boundary_separated",
    "alphaevolve_system_contribution_parity",
    "reviewed_matrix_fixture_system_contribution_records",
    "source_pages_22_23_recorded",
)
EXPECTED_EXCLUDED_CLAIMS = {
    "generic_git_history_or_commit_authorship": "out_of_scope",
    "package_metadata_or_distribution_authorship": "out_of_scope",
    "publication_author_metadata": "separate_runtime_report",
    "acknowledgement_role_provenance": "separate_runtime_report",
    "local_validation_or_benchmark_success": "not_claimed",
    "deployment_or_production_operation_evidence": "not_claimed",
}


@dataclass(frozen=True)
class SystemContributionProvenanceBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SystemContributionProvenanceBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    excluded_claim_count: int
    issues: list[SystemContributionProvenanceBoundaryIssue]


def system_contribution_provenance_boundary_record() -> dict[str, Any]:
    """Return the paper-facing AlphaEvolve system-contribution boundary."""

    return {
        "schema": SYSTEM_CONTRIBUTION_PROVENANCE_BOUNDARY_SCHEMA,
        "runtime_report_schema": SYSTEM_CONTRIBUTION_RUNTIME_REPORT_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve Contributions pages 22-23 record system-development "
            "roles for initial design, project vision and scoping, first "
            "benchmark iteration, final system, infrastructure, code review, "
            "team coordination, and supervision"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "system_contribution_provenance_report_available",
        "claim_ready": True,
        "claim_ready_fixture": EXPECTED_FIXTURE_PATH,
        "source_pages": [22, 23],
        "required_phases": list(EXPECTED_REQUIRED_PHASES),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "excluded_claims": dict(EXPECTED_EXCLUDED_CLAIMS),
        "claim_boundary": (
            "This boundary records that the matrix_multiplication fixture has "
            "reviewed paper-attributed system-development contribution metadata "
            "covering required phases, artifact/module labels, source pages, "
            "review scopes, privacy policy, and review status. It does not "
            "claim generic git history or commit authorship, package metadata "
            "or distribution authorship, publication-author metadata, "
            "acknowledgement-role provenance, local validation or benchmark "
            "success, or deployment or production operation evidence."
        ),
    }


def validate_system_contribution_provenance_boundary(
    boundary: object | str | Path | None = None,
) -> SystemContributionProvenanceBoundaryValidation:
    data, read_issues = _load_boundary(
        system_contribution_provenance_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SystemContributionProvenanceBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[SystemContributionProvenanceBoundaryIssue] = []
    if data.get("schema") != SYSTEM_CONTRIBUTION_PROVENANCE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported system-contribution provenance boundary schema"))
    if data.get("runtime_report_schema") != SYSTEM_CONTRIBUTION_RUNTIME_REPORT_SCHEMA:
        issues.append(_issue("invalid_runtime_report_schema", "runtime report schema must identify system-contribution provenance reports"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "Contributions pages 22-23" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify AlphaEvolve Contributions pages 22-23"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "system_contribution_provenance_report_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to system-contribution reports"))
    if data.get("claim_ready") is not True:
        issues.append(_issue("claim_ready_underclaim", "system-contribution boundary should remain claim-ready for the reviewed fixture"))
    if data.get("claim_ready_fixture") != EXPECTED_FIXTURE_PATH:
        issues.append(_issue("invalid_claim_ready_fixture", f"claim_ready_fixture must be {EXPECTED_FIXTURE_PATH}"))
    if data.get("source_pages") != [22, 23]:
        issues.append(_issue("invalid_source_pages", "source_pages must identify AlphaEvolve pages 22 and 23"))
    _validate_phases(data.get("required_phases"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    excluded_count = _validate_excluded_claims(data.get("excluded_claims"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim generic git history" not in boundary_text
        or "deployment or production operation evidence" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate contribution roles from git, package, validation, and deployment claims"))
    return SystemContributionProvenanceBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        excluded_claim_count=excluded_count,
        issues=issues,
    )


def render_system_contribution_provenance_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_system_contribution_provenance_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve system-contribution provenance boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| excluded_claim_count | {validation.excluded_claim_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[SystemContributionProvenanceBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "system-contribution provenance boundary must be a JSON object")]


def _validate_phases(
    value: object,
    issues: list[SystemContributionProvenanceBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_required_phases", "required_phases must be a list"))
        return 0
    seen = {item for item in value if isinstance(item, str)}
    expected = set(EXPECTED_REQUIRED_PHASES)
    missing = sorted(expected - seen)
    extra = sorted(seen - expected)
    if missing:
        issues.append(_issue("missing_required_phase", f"missing phases: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_required_phase", f"unknown phases: {', '.join(extra)}"))
    if len(seen) != len(value):
        issues.append(_issue("invalid_required_phase", "required phases must be strings"))
    return len(seen)


def _validate_required_fields(
    value: object,
    issues: list[SystemContributionProvenanceBoundaryIssue],
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


def _validate_excluded_claims(
    value: object,
    issues: list[SystemContributionProvenanceBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_excluded_claims", "excluded_claims must be an object"))
        return 0
    expected_keys = set(EXPECTED_EXCLUDED_CLAIMS)
    actual_keys = set(value)
    missing = sorted(expected_keys - actual_keys)
    extra = sorted(actual_keys - expected_keys)
    if missing:
        issues.append(_issue("missing_excluded_claim_key", f"excluded_claims lacks keys: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_excluded_claim_key", f"excluded_claims has unknown keys: {', '.join(extra)}"))
    for key, expected_value in EXPECTED_EXCLUDED_CLAIMS.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_excluded_claim_{key}", f"excluded_claims.{key} must be {expected_value}"))
    return len(actual_keys)


def _issue(code: str, message: str) -> SystemContributionProvenanceBoundaryIssue:
    return SystemContributionProvenanceBoundaryIssue(code, message)
