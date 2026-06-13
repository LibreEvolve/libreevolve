from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


RELEASE_ARTIFACT_REPRODUCIBILITY_BOUNDARY_SCHEMA = (
    "libreevolve.release_artifact_reproducibility_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "ci_release_artifact_smoke_available"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "pyproject_metadata_recorded",
    "console_script_declared",
    "runtime_environment_provenance_recorded",
    "installed_distribution_metadata_recorded",
    "wheel_metadata_snapshot_recorded",
    "direct_url_installer_record_snapshot",
    "pip_freeze_config_hashes",
    "wheel_build_check",
    "sdist_build_check",
    "install_from_wheel_cli_smoke",
    "package_data_inclusion_check",
    "release_artifact_provenance",
    "release_checklist",
    "signed_release_provenance",
    "published_index_verification",
)
EXPECTED_MISSING_EVIDENCE = {
    "signed_release_provenance": "not_recorded_locally",
    "published_index_verification": "not_recorded_locally",
}
EXPECTED_PARTIAL_EVIDENCE = {
    "wheel_build_check": "ci_smoke",
    "sdist_build_check": "ci_smoke",
    "install_from_wheel_cli_smoke": "ci_smoke",
    "package_data_inclusion_check": "complete_libreevolve_package_tree_wheel_and_sdist_inventory",
    "release_artifact_provenance": "ci_dist_artifact_and_source_hash_manifest",
    "release_checklist": "documented_unsigned_unpublished_release_smoke_checklist",
}


@dataclass(frozen=True)
class ReleaseArtifactReproducibilityBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReleaseArtifactReproducibilityBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ReleaseArtifactReproducibilityBoundaryIssue]


def release_artifact_reproducibility_boundary_record() -> dict[str, Any]:
    """Return the editable-install versus verified-release boundary."""

    return {
        "schema": RELEASE_ARTIFACT_REPRODUCIBILITY_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "AlphaEvolve-style long-running experiments require reproducible "
            "code and dependency environments; local editable package metadata "
            "does not by itself prove a verified release distribution"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "runtime_report_status": "environment_package_and_ci_release_smoke_available",
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "partial_evidence": dict(EXPECTED_PARTIAL_EVIDENCE),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve has pyproject metadata, a "
            "console-script declaration, and runtime environment/package "
            "provenance for editable or locally installed use, including "
            "bounded wheel metadata snapshots, direct_url/INSTALLER/RECORD "
            "evidence, and pip freeze/config hashes. CI also builds one wheel "
            "and one sdist, installs the wheel into an isolated virtual "
            "environment, smokes the console script, and checks every file "
            "under the libreevolve package tree inside the wheel and sdist. "
            "CI also writes release_artifact_provenance.json with wheel/sdist "
            "hashes and selected source-file hashes, then uploads the release "
            "smoke artifacts as GitHub Actions artifacts. "
            "docs/release-checklist.md records the local release-smoke "
            "checklist. It does not claim signed release provenance, "
            "published-index verification, or maintainer-approved release "
            "readiness."
        ),
    }


def validate_release_artifact_reproducibility_boundary(
    boundary: object | str | Path | None = None,
) -> ReleaseArtifactReproducibilityBoundaryValidation:
    data, read_issues = _load_boundary(
        release_artifact_reproducibility_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return ReleaseArtifactReproducibilityBoundaryValidation(
            False,
            None,
            0,
            0,
            read_issues,
        )
    assert isinstance(data, dict)
    issues: list[ReleaseArtifactReproducibilityBoundaryIssue] = []
    if data.get("schema") != RELEASE_ARTIFACT_REPRODUCIBILITY_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported release-artifact reproducibility boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "reproducible" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must identify reproducible experiment environment evidence"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("runtime_report_status") != "environment_package_and_ci_release_smoke_available":
        issues.append(_issue("invalid_runtime_report_status", "runtime report status must stay scoped to environment/package provenance"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "release-artifact boundary must not claim release readiness"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    _validate_partial_evidence(data.get("partial_evidence"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "CI also builds one wheel and one sdist" not in boundary_text
        or "installs the wheel into an isolated virtual environment" not in boundary_text
        or "checks every file under the libreevolve package tree inside the wheel and sdist" not in boundary_text
        or "release_artifact_provenance.json with wheel/sdist hashes" not in boundary_text
        or "uploads the release smoke artifacts as GitHub Actions artifacts" not in boundary_text
        or "docs/release-checklist.md records the local release-smoke checklist" not in boundary_text
        or "does not claim signed release provenance" not in boundary_text
        or "published-index verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must keep editable/local installs separate from verified release artifacts"))
    return ReleaseArtifactReproducibilityBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_release_artifact_reproducibility_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_release_artifact_reproducibility_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Release artifact reproducibility boundary",
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
) -> tuple[dict[str, Any] | None, list[ReleaseArtifactReproducibilityBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "release-artifact reproducibility boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReleaseArtifactReproducibilityBoundaryIssue],
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
    issues: list[ReleaseArtifactReproducibilityBoundaryIssue],
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
    issues: list[ReleaseArtifactReproducibilityBoundaryIssue],
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


def _issue(code: str, message: str) -> ReleaseArtifactReproducibilityBoundaryIssue:
    return ReleaseArtifactReproducibilityBoundaryIssue(code, message)
