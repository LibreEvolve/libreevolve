from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


VALIDATOR_ARTIFACT_PROMOTION_BOUNDARY_SCHEMA = (
    "libreevolve.validator_artifact_promotion_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_SECTION_IDS = ("2.4", "2.6", "4")
EXPECTED_RUNTIME_VALIDATION_SCHEMA = (
    "libreevolve.run_artifact_validator_boundary_consistency.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "cli_inspection_gate_without_promotion_time_enforcement"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "run_artifact_validator_boundary_consistency_schema",
    "manifest_validator_execution_policy_check",
    "history_jsonl_attempt_scan",
    "failure_history_jsonl_attempt_scan",
    "missing_boundary_rejection",
    "mismatched_boundary_rejection",
    "legacy_manifest_backed_row_rejection",
    "show_command_gate",
    "stream_line_diagnostics",
    "run_finalization_gate",
    "ci_artifact_promotion_gate",
    "release_artifact_promotion_gate",
    "historical_bundle_batch_enforcement",
    "archival_blocking_policy",
)
EXPECTED_MISSING_EVIDENCE = {
    "run_finalization_gate": "not_recorded_locally",
    "ci_artifact_promotion_gate": "not_recorded_locally",
    "release_artifact_promotion_gate": "not_recorded_locally",
    "historical_bundle_batch_enforcement": "not_recorded_locally",
    "archival_blocking_policy": "not_recorded_locally",
}


@dataclass(frozen=True)
class ValidatorArtifactPromotionBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ValidatorArtifactPromotionBoundaryValidation:
    ok: bool
    boundary_status: str | None
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[ValidatorArtifactPromotionBoundaryIssue]


def validator_artifact_promotion_boundary_record() -> dict[str, Any]:
    """Return the validator-boundary artifact promotion boundary."""

    return {
        "schema": VALIDATOR_ARTIFACT_PROMOTION_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_section_ids": list(EXPECTED_SOURCE_SECTION_IDS),
        "source_claim": (
            "AlphaEvolve-scale evaluation artifacts should be promotion-ready "
            "evidence, so validator-boundary consistency checks must be "
            "distinguished from optional CLI inspection when archival or "
            "release gates are not enforced."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "run_artifact_validator_boundary_consistency_schema": (
            EXPECTED_RUNTIME_VALIDATION_SCHEMA
        ),
        "claim_ready": False,
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records that LibreEvolve validates manifest-backed "
            "run artifacts with libreevolve.run_artifact_validator_boundary_"
            "consistency.v1, checks policies.validator_execution, scans "
            "history.jsonl and failure_history.jsonl attempts, rejects missing "
            "validator_boundary metadata, rejects mismatched policy/boundary "
            "claims, rejects manifest-backed legacy rows, runs the gate through "
            "libreevolve show, and reports stream/line diagnostics. It does not "
            "claim run-finalization enforcement, CI artifact-promotion "
            "enforcement, release-artifact promotion enforcement, historical "
            "bundle batch enforcement, or archival blocking policy."
        ),
    }


def validate_validator_artifact_promotion_boundary(
    boundary: object | str | Path | None = None,
) -> ValidatorArtifactPromotionBoundaryValidation:
    data, read_issues = _load_boundary(
        validator_artifact_promotion_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return ValidatorArtifactPromotionBoundaryValidation(
            False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[ValidatorArtifactPromotionBoundaryIssue] = []
    if data.get("schema") != VALIDATOR_ARTIFACT_PROMOTION_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported validator artifact promotion boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_section_ids") != list(EXPECTED_SOURCE_SECTION_IDS):
        issues.append(_issue("invalid_source_section_ids", "source_section_ids must be 2.4, 2.6, and 4"))
    source_claim = data.get("source_claim")
    if (
        not isinstance(source_claim, str)
        or "promotion-ready evidence" not in source_claim
        or "optional CLI inspection" not in source_claim
        or "release gates are not enforced" not in source_claim
    ):
        issues.append(_issue("invalid_source_claim", "source_claim must separate artifact consistency checks from promotion gates"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if (
        data.get("run_artifact_validator_boundary_consistency_schema")
        != EXPECTED_RUNTIME_VALIDATION_SCHEMA
    ):
        issues.append(_issue("invalid_run_artifact_validator_boundary_consistency_schema", f"runtime validation schema must be {EXPECTED_RUNTIME_VALIDATION_SCHEMA}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "validator artifact boundary must not claim promotion-time enforcement"))
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "does not claim run-finalization enforcement" not in boundary_text
        or "release-artifact promotion enforcement" not in boundary_text
        or "archival blocking policy" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate CLI artifact checks from promotion-time enforcement"))
    return ValidatorArtifactPromotionBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_validator_artifact_promotion_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_validator_artifact_promotion_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Validator artifact promotion boundary",
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
) -> tuple[dict[str, Any] | None, list[ValidatorArtifactPromotionBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "validator artifact promotion boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ValidatorArtifactPromotionBoundaryIssue],
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
    issues: list[ValidatorArtifactPromotionBoundaryIssue],
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


def _issue(
    code: str,
    message: str,
) -> ValidatorArtifactPromotionBoundaryIssue:
    return ValidatorArtifactPromotionBoundaryIssue(code, message)
