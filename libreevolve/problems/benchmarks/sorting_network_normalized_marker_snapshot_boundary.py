from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SORTING_NETWORK_NORMALIZED_MARKER_SNAPSHOT_BOUNDARY_SCHEMA = (
    "libreevolve.sorting_network_normalized_marker_snapshot_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "codish_publication_normalized_marker_snapshot_recorded"
EXPECTED_SNAPSHOT_DATE = "2026-06-18"
EXPECTED_SOURCE_ID = "codish_publication"
EXPECTED_SOURCE_URL = (
    "https://pure.itu.dk/en/publications/"
    "sorting-nine-inputs-requires-twenty-five-comparisons/"
)
EXPECTED_MARKERS = {
    "title": "Sorting nine inputs requires twenty-five comparisons",
    "doi": "10.1016/j.jcss.2015.11.014",
    "venue": "Journal of Computer and System Sciences",
    "target_comparators": "25",
    "author_marker": "Codish",
}
EXPECTED_NORMALIZED_PAYLOAD_BYTES = 350
EXPECTED_NORMALIZED_PAYLOAD_SHA256 = (
    "5e58af11168018d97f35d0b5c7d6a31d11fbde8f646d2b371e722badafe6d27c"
)
EXPECTED_MISSING_EVIDENCE = {
    "updated_source_snapshot_metadata": "not_recorded_locally",
    "scheduled_ci_refresh_run_history": "not_recorded_locally",
    "full_raw_source_response_artifacts": "not_recorded_locally",
    "independent_target_proof_extraction": "not_recorded_locally",
    "repeated_seed_run_tables": "not_recorded_locally",
    "run_tied_paper_certification": "not_recorded_locally",
}


@dataclass(frozen=True)
class SortingNetworkNormalizedMarkerSnapshotBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SortingNetworkNormalizedMarkerSnapshotBoundaryValidation:
    ok: bool
    boundary_status: str | None
    marker_count: int
    missing_evidence_count: int
    issues: list[SortingNetworkNormalizedMarkerSnapshotBoundaryIssue]


def sorting_network_normalized_marker_snapshot_boundary_record() -> dict[str, Any]:
    """Return normalized marker snapshot evidence for the dynamic Codish page."""

    payload = normalized_marker_payload()
    return {
        "schema": SORTING_NETWORK_NORMALIZED_MARKER_SNAPSHOT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "snapshot_date": EXPECTED_SNAPSHOT_DATE,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "source_id": EXPECTED_SOURCE_ID,
        "source_url": EXPECTED_SOURCE_URL,
        "normalization_scope": (
            "Records only stable citation markers needed for comparator-target "
            "calibration, not the dynamic full HTML page."
        ),
        "normalized_payload": payload,
        "normalized_payload_bytes": EXPECTED_NORMALIZED_PAYLOAD_BYTES,
        "normalized_payload_sha256": EXPECTED_NORMALIZED_PAYLOAD_SHA256,
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a stable normalized marker snapshot for the "
            "dynamic Codish publication page. It does not claim updated source "
            "snapshot metadata, scheduled CI refresh-run history, full raw "
            "source-body retention, independent proof extraction, repeated "
            "LibreEvolve runs, paper certification, or novel SOTA results."
        ),
    }


def normalized_marker_payload() -> dict[str, Any]:
    return {
        "source_id": EXPECTED_SOURCE_ID,
        "source_url": EXPECTED_SOURCE_URL,
        "markers": dict(EXPECTED_MARKERS),
    }


def validate_sorting_network_normalized_marker_snapshot_boundary(
    boundary: object | str | Path | None = None,
) -> SortingNetworkNormalizedMarkerSnapshotBoundaryValidation:
    data, read_issues = _load_boundary(
        sorting_network_normalized_marker_snapshot_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return SortingNetworkNormalizedMarkerSnapshotBoundaryValidation(
            False, None, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[SortingNetworkNormalizedMarkerSnapshotBoundaryIssue] = []
    if data.get("schema") != SORTING_NETWORK_NORMALIZED_MARKER_SNAPSHOT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported normalized marker snapshot schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("snapshot_date") != EXPECTED_SNAPSHOT_DATE:
        issues.append(_issue("invalid_snapshot_date", f"snapshot_date must be {EXPECTED_SNAPSHOT_DATE}"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "normalized markers alone must not claim benchmark certification"))
    if data.get("source_id") != EXPECTED_SOURCE_ID:
        issues.append(_issue("invalid_source_id", f"source_id must be {EXPECTED_SOURCE_ID}"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must match the Codish publication source"))
    marker_count = _validate_normalized_payload(data.get("normalized_payload"), issues)
    if data.get("normalized_payload_bytes") != EXPECTED_NORMALIZED_PAYLOAD_BYTES:
        issues.append(_issue("invalid_normalized_payload_bytes", f"normalized_payload_bytes must be {EXPECTED_NORMALIZED_PAYLOAD_BYTES}"))
    if data.get("normalized_payload_sha256") != EXPECTED_NORMALIZED_PAYLOAD_SHA256:
        issues.append(_issue("invalid_normalized_payload_sha256", f"normalized_payload_sha256 must be {EXPECTED_NORMALIZED_PAYLOAD_SHA256}"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "stable normalized marker snapshot" not in boundary_text
        or "does not claim updated source snapshot metadata" not in boundary_text
        or "paper certification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate normalized marker evidence from source freshness and certification"))
    return SortingNetworkNormalizedMarkerSnapshotBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        marker_count=marker_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_sorting_network_normalized_marker_snapshot_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_sorting_network_normalized_marker_snapshot_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Sorting-network normalized marker snapshot boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| marker_count | {validation.marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[SortingNetworkNormalizedMarkerSnapshotBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "normalized marker snapshot boundary must be a JSON object")]


def _validate_normalized_payload(
    value: object,
    issues: list[SortingNetworkNormalizedMarkerSnapshotBoundaryIssue],
) -> int:
    if value != normalized_marker_payload():
        issues.append(_issue("invalid_normalized_payload", "normalized_payload must match expected Codish marker payload"))
    digest = _canonical_sha256(value)
    if digest != EXPECTED_NORMALIZED_PAYLOAD_SHA256:
        issues.append(_issue("normalized_payload_digest_mismatch", "normalized_payload digest does not match expected SHA-256"))
    markers = value.get("markers") if isinstance(value, dict) else None
    return len(markers) if isinstance(markers, dict) else 0


def _validate_missing_evidence(
    value: object,
    issues: list[SortingNetworkNormalizedMarkerSnapshotBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_missing_evidence", "missing_evidence must be an object"))
        return 0
    actual_keys = set(value)
    expected_keys = set(EXPECTED_MISSING_EVIDENCE)
    if actual_keys != expected_keys:
        issues.append(_issue("invalid_missing_evidence_keys", "missing_evidence must preserve the expected absence boundary"))
    for key, expected_value in EXPECTED_MISSING_EVIDENCE.items():
        if value.get(key) != expected_value:
            issues.append(_issue(f"invalid_missing_evidence_{key}", f"missing_evidence.{key} must be {expected_value}"))
    return len(actual_keys)


def _canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _issue(code: str, message: str) -> SortingNetworkNormalizedMarkerSnapshotBoundaryIssue:
    return SortingNetworkNormalizedMarkerSnapshotBoundaryIssue(code, message)
