from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SORTING_NETWORK_SOURCE_SNAPSHOT_BOUNDARY_SCHEMA = (
    "libreevolve.sorting_network_source_snapshot_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_RETRIEVED_ON = "2026-06-18"
EXPECTED_BOUNDARY_STATUS = "source_snapshot_metadata_recorded_without_full_body_retention"
EXPECTED_SNAPSHOT_IDS = (
    "zero_one_clrs",
    "schneider_kamp_bounds",
    "dobbelaere_list",
    "codish_arxiv",
    "codish_publication",
)
EXPECTED_MISSING_EVIDENCE = {
    "source_drift_triage_resolution": "not_recorded_locally",
    "updated_source_snapshot_metadata": "not_recorded_locally",
    "full_raw_source_response_artifacts": "not_recorded_locally",
    "independent_target_proof_extraction": "not_recorded_locally",
    "scheduled_ci_refresh_run_history": "not_recorded_locally",
    "repeated_seed_run_tables": "not_recorded_locally",
    "run_tied_paper_certification": "not_recorded_locally",
}
EXPECTED_SOURCE_REFRESH_GATE_SIDECAR = "papers/sorting_network_source_refresh_gate_boundary.json"
EXPECTED_SOURCE_REFRESH_RUN_SIDECAR = "papers/sorting_network_source_refresh_run_2026-06-18.json"
EXPECTED_SOURCE_SNAPSHOTS: dict[str, dict[str, Any]] = {
    "zero_one_clrs": {
        "url": "https://bobson.ludost.net/books/algo/book6/chap28.htm",
        "final_url": "https://bobson.ludost.net/books/algo/book6/chap28.htm",
        "http_status": 200,
        "content_type": "text/html",
        "response_bytes": 57006,
        "response_sha256": "beab1350d286578063fb53f1e532547ee232acc5938046d43ea1cd7c0911531e",
        "used_for": "zero-one principle citation calibration",
    },
    "schneider_kamp_bounds": {
        "url": "https://imada.sdu.dk/u/petersk/sn/",
        "final_url": "https://imada.sdu.dk/u/petersk/sn/",
        "http_status": 200,
        "content_type": "text/html",
        "response_bytes": 3416,
        "response_sha256": "de9a6395ff4a0e0097f20a76afeb5cc549e6e18073e379eb381b79fd6135bbff",
        "used_for": "8-input comparator lower and upper bound citation",
    },
    "dobbelaere_list": {
        "url": "https://bertdobbelaere.github.io/sorting_networks.html",
        "final_url": "https://bertdobbelaere.github.io/sorting_networks.html",
        "http_status": 200,
        "content_type": "text/html; charset=utf-8",
        "response_bytes": 70392,
        "response_sha256": "71cf2352039b569c0686767de8a6d5b022a779453783a2719a5273af0835a3fe",
        "used_for": "8- and 9-input known network comparator target citation",
    },
    "codish_arxiv": {
        "url": "https://arxiv.org/abs/1405.5754",
        "final_url": "https://arxiv.org/abs/1405.5754",
        "http_status": 200,
        "content_type": "text/html; charset=utf-8",
        "response_bytes": 48157,
        "response_sha256": "94111c5590ddc589688a588e76d695a5bb1fd7540c207bbdf5fafe3f18f5a037",
        "used_for": "9-input 25-comparator optimality preprint citation",
    },
    "codish_publication": {
        "url": "https://pure.itu.dk/en/publications/sorting-nine-inputs-requires-twenty-five-comparisons/",
        "final_url": "https://pure.itu.dk/en/publications/sorting-nine-inputs-requires-twenty-five-comparisons/",
        "http_status": 200,
        "content_type": "text/html;charset=UTF-8",
        "response_bytes": 42968,
        "response_sha256": "585198c1225b08f1f2f58cd6cc8f764dd22445b1b88c361619af3313c321b52a",
        "used_for": "9-input 25-comparator peer-reviewed publication citation",
    },
}


@dataclass(frozen=True)
class SortingNetworkSourceSnapshotBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SortingNetworkSourceSnapshotBoundaryValidation:
    ok: bool
    boundary_status: str | None
    snapshot_count: int
    missing_evidence_count: int
    issues: list[SortingNetworkSourceSnapshotBoundaryIssue]


def sorting_network_source_snapshot_boundary_record() -> dict[str, Any]:
    """Return retained source snapshot metadata for sorting-network citations."""

    return {
        "schema": SORTING_NETWORK_SOURCE_SNAPSHOT_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "retrieved_on": EXPECTED_RETRIEVED_ON,
        "retrieval_mode": "manual_live_network_metadata_capture",
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "snapshot_scope": (
            "Records live response metadata and hashes for the sorting-network "
            "citation URLs without retaining full raw response bodies."
        ),
        "source_refresh_gate_sidecar": EXPECTED_SOURCE_REFRESH_GATE_SIDECAR,
        "latest_source_refresh_run_sidecar": EXPECTED_SOURCE_REFRESH_RUN_SIDECAR,
        "latest_source_refresh_status": "source_metadata_drift_detected",
        "source_snapshots": {
            source_id: dict(snapshot)
            for source_id, snapshot in EXPECTED_SOURCE_SNAPSHOTS.items()
        },
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This sidecar records sorting-network citation source snapshot "
            "metadata and links the deterministic source refresh-gate "
            "sidecar plus the latest archived live refresh-run drift outcome. "
            "It does not claim source-drift triage resolution, updated source "
            "snapshot metadata, full raw source-body retention, independent "
            "proof extraction from those sources, scheduled CI refresh-run "
            "history, repeated LibreEvolve runs, run-tied hardening, paper "
            "certification, or novel SOTA results."
        ),
    }


def validate_sorting_network_source_snapshot_boundary(
    boundary: object | str | Path | None = None,
) -> SortingNetworkSourceSnapshotBoundaryValidation:
    data, read_issues = _load_boundary(
        sorting_network_source_snapshot_boundary_record() if boundary is None else boundary
    )
    if read_issues:
        return SortingNetworkSourceSnapshotBoundaryValidation(False, None, 0, 0, read_issues)
    assert isinstance(data, dict)
    issues: list[SortingNetworkSourceSnapshotBoundaryIssue] = []
    if data.get("schema") != SORTING_NETWORK_SOURCE_SNAPSHOT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported sorting-network source snapshot boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("retrieved_on") != EXPECTED_RETRIEVED_ON:
        issues.append(_issue("invalid_retrieved_on", f"retrieved_on must be {EXPECTED_RETRIEVED_ON}"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "source metadata must not claim certified benchmark evidence"))
    if data.get("source_refresh_gate_sidecar") != EXPECTED_SOURCE_REFRESH_GATE_SIDECAR:
        issues.append(_issue("invalid_source_refresh_gate_sidecar", f"source_refresh_gate_sidecar must be {EXPECTED_SOURCE_REFRESH_GATE_SIDECAR}"))
    if data.get("latest_source_refresh_run_sidecar") != EXPECTED_SOURCE_REFRESH_RUN_SIDECAR:
        issues.append(_issue("invalid_latest_source_refresh_run_sidecar", f"latest_source_refresh_run_sidecar must be {EXPECTED_SOURCE_REFRESH_RUN_SIDECAR}"))
    if data.get("latest_source_refresh_status") != "source_metadata_drift_detected":
        issues.append(_issue("invalid_latest_source_refresh_status", "latest_source_refresh_status must record source_metadata_drift_detected"))
    snapshot_count = _validate_source_snapshots(data.get("source_snapshots"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "source-drift triage resolution" not in boundary_text
        or "updated source snapshot metadata" not in boundary_text
        or "full raw source-body retention" not in boundary_text
        or "repeated LibreEvolve runs" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate metadata from full retention and run evidence"))
    return SortingNetworkSourceSnapshotBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        snapshot_count=snapshot_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_sorting_network_source_snapshot_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_sorting_network_source_snapshot_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Sorting-network source snapshot boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| snapshot_count | {validation.snapshot_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[SortingNetworkSourceSnapshotBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "sorting-network source snapshot boundary must be a JSON object")]


def _validate_source_snapshots(
    value: object,
    issues: list[SortingNetworkSourceSnapshotBoundaryIssue],
) -> int:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_source_snapshots", "source_snapshots must be an object"))
        return 0
    actual_ids = set(value)
    expected_ids = set(EXPECTED_SNAPSHOT_IDS)
    if actual_ids != expected_ids:
        issues.append(_issue("invalid_source_snapshot_ids", "source_snapshots must include the expected citation source ids"))
    for source_id, expected in EXPECTED_SOURCE_SNAPSHOTS.items():
        snapshot = value.get(source_id)
        if not isinstance(snapshot, dict):
            issues.append(_issue(f"missing_source_snapshot_{source_id}", f"source snapshot missing {source_id}"))
            continue
        for field, expected_value in expected.items():
            if snapshot.get(field) != expected_value:
                issues.append(_issue(f"invalid_source_snapshot_{source_id}_{field}", f"{source_id}.{field} must be {expected_value!r}"))
    return len(actual_ids)


def _validate_missing_evidence(
    value: object,
    issues: list[SortingNetworkSourceSnapshotBoundaryIssue],
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


def _issue(code: str, message: str) -> SortingNetworkSourceSnapshotBoundaryIssue:
    return SortingNetworkSourceSnapshotBoundaryIssue(code, message)
