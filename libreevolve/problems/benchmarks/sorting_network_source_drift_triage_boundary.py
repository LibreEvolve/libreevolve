from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SORTING_NETWORK_SOURCE_DRIFT_TRIAGE_BOUNDARY_SCHEMA = (
    "libreevolve.sorting_network_source_drift_triage_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "codish_publication_hash_drift_triaged_as_dynamic_source"
EXPECTED_TRIAGE_DATE = "2026-06-18"
EXPECTED_DRIFT_SOURCE_ID = "codish_publication"
EXPECTED_SOURCE_URL = (
    "https://pure.itu.dk/en/publications/"
    "sorting-nine-inputs-requires-twenty-five-comparisons/"
)
EXPECTED_OBSERVED_SHA256 = (
    "d8ed91cebb616a0d1449ea10c377305ee2a86598bb88dc54ef037289de24f0c5"
)
EXPECTED_REPEATED_FETCH_SHA256 = (
    "abbb9c4ba3c3c5c72fa658bb30c5453e06e1948ffd0d0b59f1a00a4233c44494",
    "0c963d49de7e2a68732261d45cedf0db4a3e2019d53da57aa98f217812946b57",
    "8607f8c048bdaac6b26f58f1c0180973d40f586afd05c8a97b97a1fb6a65f4f8",
)
EXPECTED_STABLE_MARKERS = (
    "Sorting nine inputs requires twenty-five comparisons",
    "10.1016/j.jcss.2015.11.014",
    "Journal of Computer and System Sciences",
    "25",
    "Codish",
)
EXPECTED_NORMALIZED_MARKER_SNAPSHOT_SIDECAR = (
    "papers/sorting_network_normalized_marker_snapshot_boundary.json"
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
class SortingNetworkSourceDriftTriageBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SortingNetworkSourceDriftTriageBoundaryValidation:
    ok: bool
    boundary_status: str | None
    marker_count: int
    repeated_fetch_count: int
    missing_evidence_count: int
    issues: list[SortingNetworkSourceDriftTriageBoundaryIssue]


def sorting_network_source_drift_triage_boundary_record() -> dict[str, Any]:
    """Return the Codish publication source-drift triage boundary."""

    return {
        "schema": SORTING_NETWORK_SOURCE_DRIFT_TRIAGE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "triage_date": EXPECTED_TRIAGE_DATE,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "drift_source_id": EXPECTED_DRIFT_SOURCE_ID,
        "source_url": EXPECTED_SOURCE_URL,
        "triage_observation": {
            "http_status": 200,
            "content_type": "text/html;charset=UTF-8",
            "response_bytes": 43688,
            "response_sha256": EXPECTED_OBSERVED_SHA256,
            "stable_markers_present": list(EXPECTED_STABLE_MARKERS),
        },
        "repeated_fetch_probe": {
            "sample_count": len(EXPECTED_REPEATED_FETCH_SHA256),
            "response_bytes": [43688, 43688, 43688],
            "response_sha256": list(EXPECTED_REPEATED_FETCH_SHA256),
            "conclusion": "full_page_sha256_unstable_for_same_length_response",
        },
        "normalized_marker_snapshot_sidecar": EXPECTED_NORMALIZED_MARKER_SNAPSHOT_SIDECAR,
        "normalized_marker_snapshot_status": "recorded",
        "triage_resolution": (
            "The source page still contains the title, DOI, journal, numeric "
            "25-comparison marker, and Codish author marker used for citation "
            "calibration, but full-page SHA-256 is unstable across repeated "
            "fetches. Do not treat the old full-page hash as fresh; use the "
            "normalized marker snapshot sidecar or a more stable source before "
            "promoting source freshness."
        ),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary triages the Codish publication source drift as a "
            "dynamic full-page hash instability with citation markers still "
            "present and links the normalized marker snapshot sidecar. It "
            "does not claim updated source snapshot metadata, scheduled CI "
            "refresh-run history, full raw source-body retention, independent "
            "proof extraction, repeated LibreEvolve runs, paper certification, "
            "or novel SOTA results."
        ),
    }


def validate_sorting_network_source_drift_triage_boundary(
    boundary: object | str | Path | None = None,
) -> SortingNetworkSourceDriftTriageBoundaryValidation:
    data, read_issues = _load_boundary(
        sorting_network_source_drift_triage_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return SortingNetworkSourceDriftTriageBoundaryValidation(
            False, None, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[SortingNetworkSourceDriftTriageBoundaryIssue] = []
    if data.get("schema") != SORTING_NETWORK_SOURCE_DRIFT_TRIAGE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported sorting-network source drift triage schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("triage_date") != EXPECTED_TRIAGE_DATE:
        issues.append(_issue("invalid_triage_date", f"triage_date must be {EXPECTED_TRIAGE_DATE}"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "drift triage must not claim source freshness"))
    if data.get("drift_source_id") != EXPECTED_DRIFT_SOURCE_ID:
        issues.append(_issue("invalid_drift_source_id", f"drift_source_id must be {EXPECTED_DRIFT_SOURCE_ID}"))
    if data.get("source_url") != EXPECTED_SOURCE_URL:
        issues.append(_issue("invalid_source_url", "source_url must match the Codish publication source"))
    marker_count = _validate_triage_observation(data.get("triage_observation"), issues)
    repeated_count = _validate_repeated_fetch_probe(data.get("repeated_fetch_probe"), issues)
    if data.get("normalized_marker_snapshot_sidecar") != EXPECTED_NORMALIZED_MARKER_SNAPSHOT_SIDECAR:
        issues.append(_issue("invalid_normalized_marker_snapshot_sidecar", f"normalized_marker_snapshot_sidecar must be {EXPECTED_NORMALIZED_MARKER_SNAPSHOT_SIDECAR}"))
    if data.get("normalized_marker_snapshot_status") != "recorded":
        issues.append(_issue("invalid_normalized_marker_snapshot_status", "normalized_marker_snapshot_status must be recorded"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    resolution = data.get("triage_resolution")
    if (
        not isinstance(resolution, str)
        or "full-page SHA-256 is unstable" not in resolution
        or "normalized marker snapshot sidecar" not in resolution
    ):
        issues.append(_issue("invalid_triage_resolution", "triage_resolution must identify unstable full-page hashing and normalized-marker follow-up"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "dynamic full-page hash instability" not in boundary_text
        or "citation markers still present" not in boundary_text
        or "normalized marker snapshot sidecar" not in boundary_text
        or "does not claim updated source snapshot metadata" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must preserve non-freshness after triage"))
    return SortingNetworkSourceDriftTriageBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        marker_count=marker_count,
        repeated_fetch_count=repeated_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_sorting_network_source_drift_triage_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_sorting_network_source_drift_triage_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Sorting-network source drift triage boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| marker_count | {validation.marker_count} |",
        f"| repeated_fetch_count | {validation.repeated_fetch_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[SortingNetworkSourceDriftTriageBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "sorting-network source drift triage boundary must be a JSON object")]


def _validate_triage_observation(
    value: object,
    issues: list[SortingNetworkSourceDriftTriageBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_triage_observation", "triage_observation must be an object"))
        return 0
    expected = {
        "http_status": 200,
        "content_type": "text/html;charset=UTF-8",
        "response_bytes": 43688,
        "response_sha256": EXPECTED_OBSERVED_SHA256,
        "stable_markers_present": list(EXPECTED_STABLE_MARKERS),
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_triage_observation_{field}", f"triage_observation.{field} must be {expected_value!r}"))
    markers = value.get("stable_markers_present")
    return len(markers) if isinstance(markers, list) else 0


def _validate_repeated_fetch_probe(
    value: object,
    issues: list[SortingNetworkSourceDriftTriageBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_repeated_fetch_probe", "repeated_fetch_probe must be an object"))
        return 0
    expected = {
        "sample_count": len(EXPECTED_REPEATED_FETCH_SHA256),
        "response_bytes": [43688, 43688, 43688],
        "response_sha256": list(EXPECTED_REPEATED_FETCH_SHA256),
        "conclusion": "full_page_sha256_unstable_for_same_length_response",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_repeated_fetch_probe_{field}", f"repeated_fetch_probe.{field} must be {expected_value!r}"))
    if len(set(EXPECTED_REPEATED_FETCH_SHA256)) != len(EXPECTED_REPEATED_FETCH_SHA256):
        issues.append(_issue("invalid_repeated_fetch_probe_unique_hashes", "repeated fetch hashes must show instability"))
    return len(value.get("response_sha256", [])) if isinstance(value.get("response_sha256"), list) else 0


def _validate_missing_evidence(
    value: object,
    issues: list[SortingNetworkSourceDriftTriageBoundaryIssue],
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


def _issue(code: str, message: str) -> SortingNetworkSourceDriftTriageBoundaryIssue:
    return SortingNetworkSourceDriftTriageBoundaryIssue(code, message)
