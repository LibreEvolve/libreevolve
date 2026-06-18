from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.sorting_network_source_refresh_gate_boundary import (
    EXPECTED_SCRIPT_BYTES,
    EXPECTED_SCRIPT_PATH,
    EXPECTED_SCRIPT_SHA256,
)
from libreevolve.tools.sorting_network_source_refresh_gate import REPORT_SCHEMA


SORTING_NETWORK_SOURCE_REFRESH_RUN_BOUNDARY_SCHEMA = (
    "libreevolve.sorting_network_source_refresh_run_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "live_source_refresh_run_archived_with_source_drift"
EXPECTED_RUN_DATE = "2026-06-18"
EXPECTED_RUN_CONTEXT = "manual_local_network_run"
EXPECTED_RUN_MODE = "live_network"
EXPECTED_DRIFT_SOURCE_ID = "codish_publication"
EXPECTED_SOURCE_DRIFT_TRIAGE_SIDECAR = "papers/sorting_network_source_drift_triage_boundary.json"
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
class SortingNetworkSourceRefreshRunBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SortingNetworkSourceRefreshRunBoundaryValidation:
    ok: bool
    boundary_status: str | None
    run_report_checked: bool
    source_count: int
    drift_count: int
    missing_evidence_count: int
    issues: list[SortingNetworkSourceRefreshRunBoundaryIssue]


def sorting_network_source_refresh_run_boundary_record() -> dict[str, Any]:
    """Return the archived sorting-network live source-refresh run boundary."""

    run_report = expected_live_run_report()
    return {
        "schema": SORTING_NETWORK_SOURCE_REFRESH_RUN_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "Sorting-network citation source metadata should retain live "
            "refresh-run outcomes, including source drift, before citations "
            "are treated as fresh paper evidence."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "run_date": EXPECTED_RUN_DATE,
        "run_context": EXPECTED_RUN_CONTEXT,
        "refresh_gate_artifact": {
            "path": EXPECTED_SCRIPT_PATH,
            "bytes": EXPECTED_SCRIPT_BYTES,
            "sha256": EXPECTED_SCRIPT_SHA256,
            "command": (
                "py -3.12 -m libreevolve.tools.sorting_network_source_refresh_gate "
                "--live --pretty"
            ),
        },
        "run_report_sha256": _canonical_sha256(run_report),
        "run_report": run_report,
        "drift_summary": {
            "drift_source_ids": [EXPECTED_DRIFT_SOURCE_ID],
            "drift_status": "source_metadata_drift_detected",
            "triage_required": True,
        },
        "source_drift_triage_sidecar": EXPECTED_SOURCE_DRIFT_TRIAGE_SIDECAR,
        "source_drift_triage_status": "full_page_hash_unstable_markers_present",
        "normalized_marker_snapshot_sidecar": EXPECTED_NORMALIZED_MARKER_SNAPSHOT_SIDECAR,
        "normalized_marker_snapshot_status": "recorded",
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary archives one manual live-network sorting-network "
            "source refresh run where the Codish publication page drifted from "
            "the committed source snapshot metadata, plus a triage sidecar "
            "classifying the drift as full-page-hash instability with citation "
            "markers present and the normalized marker snapshot sidecar. It "
            "does not claim source freshness, updated source snapshot "
            "metadata, scheduled CI refresh-run history, full raw source-body "
            "retention, repeated LibreEvolve runs, paper certification, or "
            "novel SOTA results."
        ),
    }


def expected_live_run_report() -> dict[str, Any]:
    return {
        "schema": REPORT_SCHEMA,
        "mode": EXPECTED_RUN_MODE,
        "source_count": 5,
        "ok": False,
        "claim_boundary": (
            "Compares live response status, content type, byte count, and "
            "SHA-256 digest against committed sorting-network citation source "
            "snapshot metadata."
        ),
        "checks": [
            _check(
                "zero_one_clrs",
                "https://bobson.ludost.net/books/algo/book6/chap28.htm",
                "text/html",
                57006,
                "beab1350d286578063fb53f1e532547ee232acc5938046d43ea1cd7c0911531e",
                [],
            ),
            _check(
                "schneider_kamp_bounds",
                "https://imada.sdu.dk/u/petersk/sn/",
                "text/html",
                3416,
                "de9a6395ff4a0e0097f20a76afeb5cc549e6e18073e379eb381b79fd6135bbff",
                [],
            ),
            _check(
                "dobbelaere_list",
                "https://bertdobbelaere.github.io/sorting_networks.html",
                "text/html; charset=utf-8",
                70392,
                "71cf2352039b569c0686767de8a6d5b022a779453783a2719a5273af0835a3fe",
                [],
            ),
            _check(
                "codish_arxiv",
                "https://arxiv.org/abs/1405.5754",
                "text/html; charset=utf-8",
                48157,
                "94111c5590ddc589688a588e76d695a5bb1fd7540c207bbdf5fafe3f18f5a037",
                [],
            ),
            _check(
                "codish_publication",
                "https://pure.itu.dk/en/publications/sorting-nine-inputs-requires-twenty-five-comparisons/",
                "text/html;charset=UTF-8",
                42968,
                "585198c1225b08f1f2f58cd6cc8f764dd22445b1b88c361619af3313c321b52a",
                ["bytes_drift", "sha256_drift"],
                observed_bytes=43688,
                observed_sha256="6a7f83772c77aa97592ef706ecd55bef33be69bf51cecb820822c0b8fbb6dbca",
            ),
        ],
    }


def validate_sorting_network_source_refresh_run_boundary(
    boundary: object | str | Path | None = None,
) -> SortingNetworkSourceRefreshRunBoundaryValidation:
    data, read_issues = _load_boundary(
        sorting_network_source_refresh_run_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return SortingNetworkSourceRefreshRunBoundaryValidation(
            False, None, False, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[SortingNetworkSourceRefreshRunBoundaryIssue] = []
    if data.get("schema") != SORTING_NETWORK_SOURCE_REFRESH_RUN_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported sorting-network source refresh-run boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "live refresh-run outcomes" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must describe retained live refresh-run outcomes"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "drifted live refresh run must not claim source freshness"))
    if data.get("run_date") != EXPECTED_RUN_DATE:
        issues.append(_issue("invalid_run_date", f"run_date must be {EXPECTED_RUN_DATE}"))
    if data.get("run_context") != EXPECTED_RUN_CONTEXT:
        issues.append(_issue("invalid_run_context", f"run_context must be {EXPECTED_RUN_CONTEXT}"))
    _validate_refresh_gate_artifact(data.get("refresh_gate_artifact"), issues)
    run_report_checked, source_count, drift_count = _validate_run_report(
        data.get("run_report"),
        data.get("run_report_sha256"),
        issues,
    )
    _validate_drift_summary(data.get("drift_summary"), drift_count, issues)
    if data.get("source_drift_triage_sidecar") != EXPECTED_SOURCE_DRIFT_TRIAGE_SIDECAR:
        issues.append(_issue("invalid_source_drift_triage_sidecar", f"source_drift_triage_sidecar must be {EXPECTED_SOURCE_DRIFT_TRIAGE_SIDECAR}"))
    if data.get("source_drift_triage_status") != "full_page_hash_unstable_markers_present":
        issues.append(_issue("invalid_source_drift_triage_status", "source_drift_triage_status must record full_page_hash_unstable_markers_present"))
    if data.get("normalized_marker_snapshot_sidecar") != EXPECTED_NORMALIZED_MARKER_SNAPSHOT_SIDECAR:
        issues.append(_issue("invalid_normalized_marker_snapshot_sidecar", f"normalized_marker_snapshot_sidecar must be {EXPECTED_NORMALIZED_MARKER_SNAPSHOT_SIDECAR}"))
    if data.get("normalized_marker_snapshot_status") != "recorded":
        issues.append(_issue("invalid_normalized_marker_snapshot_status", "normalized_marker_snapshot_status must be recorded"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "archives one manual live-network sorting-network source refresh run" not in boundary_text
        or "Codish publication page drifted" not in boundary_text
        or "does not claim source freshness" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate archived drift evidence from source freshness"))
    return SortingNetworkSourceRefreshRunBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        run_report_checked=run_report_checked,
        source_count=source_count,
        drift_count=drift_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_sorting_network_source_refresh_run_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_sorting_network_source_refresh_run_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Sorting-network source refresh-run boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| run_report_checked | {validation.run_report_checked} |",
        f"| source_count | {validation.source_count} |",
        f"| drift_count | {validation.drift_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _check(
    source_id: str,
    url: str,
    content_type: str,
    expected_bytes: int,
    expected_sha256: str,
    issues: list[str],
    *,
    observed_bytes: int | None = None,
    observed_sha256: str | None = None,
) -> dict[str, Any]:
    observed_bytes = expected_bytes if observed_bytes is None else observed_bytes
    observed_sha256 = expected_sha256 if observed_sha256 is None else observed_sha256
    return {
        "source_id": source_id,
        "url": url,
        "ok": not issues,
        "issues": list(issues),
        "expected": {
            "status": 200,
            "content_type": content_type,
            "bytes": expected_bytes,
            "sha256": expected_sha256,
        },
        "observed": {
            "status": 200,
            "content_type": content_type,
            "bytes": observed_bytes,
            "sha256": observed_sha256,
        },
    }


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[SortingNetworkSourceRefreshRunBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "sorting-network source refresh-run boundary must be a JSON object")]


def _validate_refresh_gate_artifact(
    value: object,
    issues: list[SortingNetworkSourceRefreshRunBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_refresh_gate_artifact", "refresh_gate_artifact must be an object"))
        return
    expected = {
        "path": EXPECTED_SCRIPT_PATH,
        "bytes": EXPECTED_SCRIPT_BYTES,
        "sha256": EXPECTED_SCRIPT_SHA256,
        "command": "py -3.12 -m libreevolve.tools.sorting_network_source_refresh_gate --live --pretty",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_refresh_gate_artifact_{field}", f"refresh_gate_artifact.{field} must be {expected_value}"))


def _validate_run_report(
    value: object,
    digest_value: object,
    issues: list[SortingNetworkSourceRefreshRunBoundaryIssue],
) -> tuple[bool, int, int]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_run_report", "run_report must be an object"))
        return False, 0, 0
    expected = expected_live_run_report()
    if value != expected:
        issues.append(_issue("invalid_run_report", "run_report must match archived live drift outcome"))
    expected_digest = _canonical_sha256(expected)
    if digest_value != expected_digest:
        issues.append(_issue("invalid_run_report_sha256", f"run_report_sha256 must be {expected_digest}"))
    checks = value.get("checks")
    if not isinstance(checks, list):
        return False, 0, 0
    drift_count = sum(1 for check in checks if isinstance(check, dict) and check.get("ok") is False)
    if value.get("ok") is not False:
        issues.append(_issue("invalid_run_report_ok", "archived live run must preserve the drift failure"))
    return True, len(checks), drift_count


def _validate_drift_summary(
    value: object,
    drift_count: int,
    issues: list[SortingNetworkSourceRefreshRunBoundaryIssue],
) -> None:
    if value != {
        "drift_source_ids": [EXPECTED_DRIFT_SOURCE_ID],
        "drift_status": "source_metadata_drift_detected",
        "triage_required": True,
    }:
        issues.append(_issue("invalid_drift_summary", "drift_summary must record the Codish publication drift"))
    if drift_count != 1:
        issues.append(_issue("invalid_drift_count", "archived live run must have exactly one drifted source"))


def _validate_missing_evidence(
    value: object,
    issues: list[SortingNetworkSourceRefreshRunBoundaryIssue],
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


def _issue(code: str, message: str) -> SortingNetworkSourceRefreshRunBoundaryIssue:
    return SortingNetworkSourceRefreshRunBoundaryIssue(code, message)
