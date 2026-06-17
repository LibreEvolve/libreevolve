from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_2026_impact_boundary import (
    EXPECTED_ARTICLE_URL,
    EXPECTED_CLAIM_IDS,
    EXPECTED_HTML_SHA256,
    alphaevolve_2026_impact_boundary_record,
)


ALPHAEVOLVE_IMPACT_VERIFICATION_MATRIX_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_impact_verification_matrix_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "impact_claim_and_source_matrix_without_local_benchmark_or_independent_verification"
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "row_id",
    "row_type",
    "canonical_claim_or_source_id",
    "source_url",
    "source_retrieval_hash",
    "source_artifact_status",
    "fixture_path",
    "local_benchmark_status",
    "benchmark_report_path",
    "benchmark_report_hash",
    "independent_verifier",
    "verification_date",
    "verification_outcome",
    "blocker_or_failure_reason",
    "customer_confirmation_status",
    "unsupported_local_benchmark_flag",
    "release_note_eligibility",
    "downgrade_wording",
)
EXPECTED_MISSING_EVIDENCE = {
    "claim_source_snapshot_matrix": "impact_article_snapshot_only_for_claim_rows",
    "outbound_source_snapshot_matrix": "not_recorded_for_all_outbound_sources",
    "local_benchmark_reports": "not_implemented_locally",
    "benchmark_report_hashes": "not_recorded_locally",
    "independent_verification_attempts": "not_recorded_locally",
    "customer_confirmations": "not_recorded_locally",
    "release_note_eligibility": "not_eligible",
}


@dataclass(frozen=True)
class AlphaEvolveImpactVerificationMatrixBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveImpactVerificationMatrixBoundaryValidation:
    ok: bool
    boundary_status: str | None
    claim_row_count: int
    source_row_count: int
    release_note_eligible_count: int
    required_evidence_field_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveImpactVerificationMatrixBoundaryIssue]


def alphaevolve_impact_verification_matrix_boundary_record() -> dict[str, Any]:
    """Return the aggregate 2026 impact verification/report absence matrix."""

    impact = alphaevolve_2026_impact_boundary_record()
    return {
        "schema": ALPHAEVOLVE_IMPACT_VERIFICATION_MATRIX_BOUNDARY_SCHEMA,
        "source_id": "google-deepmind-alphaevolve-impact-2026-verification-matrix",
        "source_family": "official_google_deepmind_alphaevolve_impact_article",
        "source_relation": (
            "aggregate absence matrix for source snapshots, local benchmark "
            "reports, and independent verification across 2026 impact claims "
            "and outbound sources"
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "matrix_version": "2026-06-17",
        "claim_rows": [
            _claim_matrix_row(claim)
            for claim in impact["claim_registry"]
        ],
        "outbound_source_rows": [
            _outbound_source_row(link)
            for link in impact["outbound_links"]
        ],
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a machine-checkable absence matrix for the "
            "official 2026 AlphaEvolve impact claims and outbound sources. It "
            "does not claim local benchmark reports, benchmark report hashes, "
            "independent verification attempts, customer confirmations, or "
            "release-note eligibility for any row."
        ),
    }


def validate_alphaevolve_impact_verification_matrix_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveImpactVerificationMatrixBoundaryValidation:
    data, read_issues = _load_boundary(
        alphaevolve_impact_verification_matrix_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveImpactVerificationMatrixBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveImpactVerificationMatrixBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_IMPACT_VERIFICATION_MATRIX_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported impact verification matrix schema"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "verification matrix must not claim impact reproduction readiness"))
    if data.get("matrix_version") != "2026-06-17":
        issues.append(_issue("invalid_matrix_version", "matrix_version must record the audit date"))
    claim_count, claim_eligible = _validate_claim_rows(data.get("claim_rows"), issues)
    source_count, source_eligible = _validate_source_rows(data.get("outbound_source_rows"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "machine-checkable absence matrix" not in boundary_text
        or "does not claim local benchmark reports" not in boundary_text
        or "release-note eligibility for any row" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must prevent verification/report overclaims"))
    return AlphaEvolveImpactVerificationMatrixBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        claim_row_count=claim_count,
        source_row_count=source_count,
        release_note_eligible_count=claim_eligible + source_eligible,
        required_evidence_field_count=required_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_impact_verification_matrix_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_impact_verification_matrix_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve impact verification matrix boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| claim_row_count | {validation.claim_row_count} |",
        f"| source_row_count | {validation.source_row_count} |",
        f"| release_note_eligible_count | {validation.release_note_eligible_count} |",
        f"| required_evidence_field_count | {validation.required_evidence_field_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _claim_matrix_row(claim: dict[str, Any]) -> dict[str, Any]:
    customer = str(claim["evidence_status"]) == "customer_source_required"
    return {
        "row_id": f"claim:{claim['claim_id']}",
        "row_type": "impact_claim",
        "canonical_claim_or_source_id": claim["claim_id"],
        "source_url": EXPECTED_ARTICLE_URL,
        "source_retrieval_hash": EXPECTED_HTML_SHA256,
        "source_artifact_status": "impact_article_snapshot_recorded",
        "fixture_path": None,
        "local_benchmark_status": "not_implemented_locally",
        "benchmark_report_path": None,
        "benchmark_report_hash": None,
        "independent_verifier": "not_recorded_locally",
        "verification_date": None,
        "verification_outcome": "not_verified_locally",
        "blocker_or_failure_reason": "missing_local_fixture_report_and_independent_verification",
        "customer_confirmation_status": "not_recorded_locally" if customer else "not_applicable",
        "unsupported_local_benchmark_flag": True,
        "release_note_eligible": False,
        "downgrade_wording": "source-scoped only; not reproduced by LibreEvolve",
    }


def _outbound_source_row(link: dict[str, Any]) -> dict[str, Any]:
    status = str(link["status"])
    source_status = (
        "source_snapshot_required"
        if status != "outbound_reference_only"
        else "outbound_reference_only"
    )
    return {
        "row_id": f"source:{link['link_id']}",
        "row_type": "outbound_source",
        "canonical_claim_or_source_id": link["link_id"],
        "source_url": link["url"],
        "source_retrieval_hash": None,
        "source_artifact_status": source_status,
        "fixture_path": None,
        "local_benchmark_status": "not_implemented_locally",
        "benchmark_report_path": None,
        "benchmark_report_hash": None,
        "independent_verifier": "not_recorded_locally",
        "verification_date": None,
        "verification_outcome": "not_verified_locally",
        "blocker_or_failure_reason": "missing_source_snapshot_fixture_report_and_independent_verification",
        "customer_confirmation_status": (
            "not_recorded_locally" if link["category"] == "customer_case" else "not_applicable"
        ),
        "unsupported_local_benchmark_flag": True,
        "release_note_eligible": False,
        "downgrade_wording": "outbound source-scoped only; not reproduced by LibreEvolve",
    }


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveImpactVerificationMatrixBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "impact verification matrix boundary must be a JSON object")]


def _validate_claim_rows(
    value: object,
    issues: list[AlphaEvolveImpactVerificationMatrixBoundaryIssue],
) -> tuple[int, int]:
    if not isinstance(value, list):
        issues.append(_issue("invalid_claim_rows", "claim_rows must be a list"))
        return 0, 0
    ids = []
    eligible = 0
    for row in value:
        if not isinstance(row, dict):
            issues.append(_issue("invalid_claim_row", "claim rows must be objects"))
            continue
        claim_id = row.get("canonical_claim_or_source_id")
        if isinstance(claim_id, str):
            ids.append(claim_id)
        eligible += _validate_matrix_row(row, "impact_claim", True, issues)
        if row.get("source_url") != EXPECTED_ARTICLE_URL:
            issues.append(_issue("invalid_claim_source_url", "claim rows must point at the impact article"))
        if row.get("source_retrieval_hash") != EXPECTED_HTML_SHA256:
            issues.append(_issue("invalid_claim_source_hash", "claim rows must preserve the impact article hash"))
        if row.get("source_artifact_status") != "impact_article_snapshot_recorded":
            issues.append(_issue("invalid_claim_source_artifact_status", "claim rows must record only the impact article snapshot"))
    if tuple(ids) != EXPECTED_CLAIM_IDS:
        issues.append(_issue("claim_id_mismatch", "claim rows must cover every official 2026 impact claim id"))
    return len(ids), eligible


def _validate_source_rows(
    value: object,
    issues: list[AlphaEvolveImpactVerificationMatrixBoundaryIssue],
) -> tuple[int, int]:
    expected_links = alphaevolve_2026_impact_boundary_record()["outbound_links"]
    expected_ids = tuple(link["link_id"] for link in expected_links)
    if not isinstance(value, list):
        issues.append(_issue("invalid_source_rows", "outbound_source_rows must be a list"))
        return 0, 0
    ids = []
    eligible = 0
    for row in value:
        if not isinstance(row, dict):
            issues.append(_issue("invalid_source_row", "source rows must be objects"))
            continue
        source_id = row.get("canonical_claim_or_source_id")
        if isinstance(source_id, str):
            ids.append(source_id)
        eligible += _validate_matrix_row(row, "outbound_source", False, issues)
        if row.get("source_artifact_status") not in {"outbound_reference_only", "source_snapshot_required"}:
            issues.append(_issue("invalid_source_artifact_status", "source rows must remain reference/snapshot-required only"))
        if row.get("source_retrieval_hash") is not None:
            issues.append(_issue("source_hash_overclaim", "outbound source rows must not claim retrieval hashes here"))
    if tuple(ids) != expected_ids:
        issues.append(_issue("source_id_mismatch", "source rows must cover every outbound link in order"))
    return len(ids), eligible


def _validate_matrix_row(
    row: dict[str, Any],
    expected_type: str,
    hash_required: bool,
    issues: list[AlphaEvolveImpactVerificationMatrixBoundaryIssue],
) -> int:
    if row.get("row_type") != expected_type:
        issues.append(_issue("invalid_row_type", f"matrix row must have row_type {expected_type}"))
    required_text = (
        "row_id",
        "canonical_claim_or_source_id",
        "source_url",
        "source_artifact_status",
        "local_benchmark_status",
        "independent_verifier",
        "verification_outcome",
        "blocker_or_failure_reason",
        "customer_confirmation_status",
        "downgrade_wording",
    )
    for key in required_text:
        if not isinstance(row.get(key), str) or not row[key]:
            issues.append(_issue("invalid_matrix_row_field", f"matrix row must include {key}"))
            break
    if hash_required and not isinstance(row.get("source_retrieval_hash"), str):
        issues.append(_issue("missing_matrix_row_hash", "claim rows must include source retrieval hash"))
    if row.get("fixture_path") is not None:
        issues.append(_issue("fixture_path_overclaim", "matrix rows must not claim fixture paths"))
    if row.get("local_benchmark_status") != "not_implemented_locally":
        issues.append(_issue("local_benchmark_status_overclaim", "matrix rows must not claim local benchmark implementation"))
    if row.get("benchmark_report_path") is not None or row.get("benchmark_report_hash") is not None:
        issues.append(_issue("benchmark_report_overclaim", "matrix rows must not claim benchmark reports"))
    if row.get("independent_verifier") != "not_recorded_locally":
        issues.append(_issue("independent_verifier_overclaim", "matrix rows must not claim independent verifier identity"))
    if row.get("verification_date") is not None:
        issues.append(_issue("verification_date_overclaim", "matrix rows must not claim verification date"))
    if row.get("verification_outcome") != "not_verified_locally":
        issues.append(_issue("verification_outcome_overclaim", "matrix rows must not claim verification"))
    if row.get("unsupported_local_benchmark_flag") is not True:
        issues.append(_issue("missing_unsupported_local_benchmark_flag", "matrix rows must flag unsupported local benchmark evidence"))
    if row.get("release_note_eligible") is True:
        issues.append(_issue("release_note_eligibility_overclaim", "matrix rows must not be release-note eligible"))
        return 1
    return 0


def _validate_required_fields(
    value: object,
    issues: list[AlphaEvolveImpactVerificationMatrixBoundaryIssue],
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
    issues: list[AlphaEvolveImpactVerificationMatrixBoundaryIssue],
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


def _issue(code: str, message: str) -> AlphaEvolveImpactVerificationMatrixBoundaryIssue:
    return AlphaEvolveImpactVerificationMatrixBoundaryIssue(code, message)
