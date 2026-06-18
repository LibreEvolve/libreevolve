from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.sorting_network_source_snapshot_boundary import (
    EXPECTED_SOURCE_SNAPSHOTS,
)
from libreevolve.tools.sorting_network_source_refresh_gate import (
    REPORT_SCHEMA,
    run_refresh_gate,
)


SORTING_NETWORK_SOURCE_REFRESH_GATE_BOUNDARY_SCHEMA = (
    "libreevolve.sorting_network_source_refresh_gate_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_BOUNDARY_STATUS = "deterministic_source_refresh_gate_recorded_without_ci_history"
EXPECTED_SCRIPT_PATH = "libreevolve/tools/sorting_network_source_refresh_gate.py"
EXPECTED_SCRIPT_BYTES = 6436
EXPECTED_SCRIPT_SHA256 = (
    "e94e09a5a2c2a443c92915a8029a53086ec032db09980cfd272ef16d3bd1d965"
)
EXPECTED_SOURCE_SNAPSHOT_SIDECAR = "papers/sorting_network_source_snapshot_boundary.json"
EXPECTED_MISSING_EVIDENCE = {
    "scheduled_ci_refresh_run_history": "not_recorded_locally",
    "archived_live_refresh_run_history": "not_recorded_locally",
    "full_raw_source_response_artifacts": "not_recorded_locally",
    "independent_target_proof_extraction": "not_recorded_locally",
    "repeated_seed_run_tables": "not_recorded_locally",
    "run_tied_paper_certification": "not_recorded_locally",
}


@dataclass(frozen=True)
class SortingNetworkSourceRefreshGateBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class SortingNetworkSourceRefreshGateBoundaryValidation:
    ok: bool
    boundary_status: str | None
    script_artifact_checked: bool
    deterministic_gate_checked: bool
    source_count: int
    missing_evidence_count: int
    issues: list[SortingNetworkSourceRefreshGateBoundaryIssue]


def sorting_network_source_refresh_gate_boundary_record() -> dict[str, Any]:
    """Return the sorting-network citation source refresh-gate boundary."""

    return {
        "schema": SORTING_NETWORK_SOURCE_REFRESH_GATE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_claim": (
            "Sorting-network citation source metadata should have a reusable "
            "refresh gate that compares current network responses with "
            "committed snapshot metadata."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "script_artifact": {
            "path": EXPECTED_SCRIPT_PATH,
            "bytes": EXPECTED_SCRIPT_BYTES,
            "sha256": EXPECTED_SCRIPT_SHA256,
            "entrypoint": "run_refresh_gate",
            "cli": (
                "py -3.12 -m libreevolve.tools.sorting_network_source_refresh_gate "
                "--live --pretty"
            ),
            "deterministic_cli": (
                "py -3.12 -m libreevolve.tools.sorting_network_source_refresh_gate "
                "--pretty"
            ),
        },
        "source_snapshot_metadata_sidecar": EXPECTED_SOURCE_SNAPSHOT_SIDECAR,
        "expected_report_schema": REPORT_SCHEMA,
        "expected_source_ids": list(EXPECTED_SOURCE_SNAPSHOTS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a deterministic sorting-network citation "
            "source refresh gate script tied to committed source snapshot "
            "metadata. It does not claim scheduled CI refresh-run history, "
            "archived live refresh-run history, full raw source-body "
            "retention, independent proof extraction, repeated LibreEvolve "
            "runs, run-tied hardening, paper certification, or novel SOTA "
            "results."
        ),
    }


def validate_sorting_network_source_refresh_gate_boundary(
    boundary: object | str | Path | None = None,
) -> SortingNetworkSourceRefreshGateBoundaryValidation:
    data, read_issues, base_dir = _load_boundary(
        sorting_network_source_refresh_gate_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return SortingNetworkSourceRefreshGateBoundaryValidation(
            False, None, False, False, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[SortingNetworkSourceRefreshGateBoundaryIssue] = []
    if data.get("schema") != SORTING_NETWORK_SOURCE_REFRESH_GATE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported sorting-network source refresh-gate boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "refresh gate" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must describe the source refresh gate"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "refresh-gate metadata must not claim certified benchmark evidence"))
    _validate_script_artifact(data.get("script_artifact"), issues)
    if data.get("source_snapshot_metadata_sidecar") != EXPECTED_SOURCE_SNAPSHOT_SIDECAR:
        issues.append(_issue("invalid_source_snapshot_metadata_sidecar", f"source_snapshot_metadata_sidecar must be {EXPECTED_SOURCE_SNAPSHOT_SIDECAR}"))
    if data.get("expected_report_schema") != REPORT_SCHEMA:
        issues.append(_issue("invalid_expected_report_schema", f"expected_report_schema must be {REPORT_SCHEMA}"))
    source_count = _validate_expected_source_ids(data.get("expected_source_ids"), issues)
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "deterministic sorting-network citation source refresh gate" not in boundary_text
        or "does not claim scheduled CI refresh-run history" not in boundary_text
        or "archived live refresh-run history" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate deterministic gate evidence from live/CI history"))

    script_checked = False
    deterministic_checked = False
    if base_dir is not None:
        script_checked = _validate_script_file(base_dir, issues)
        deterministic_checked = _validate_deterministic_gate(issues)

    return SortingNetworkSourceRefreshGateBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        script_artifact_checked=script_checked,
        deterministic_gate_checked=deterministic_checked,
        source_count=source_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_sorting_network_source_refresh_gate_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_sorting_network_source_refresh_gate_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "Sorting-network source refresh-gate boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| script_artifact_checked | {validation.script_artifact_checked} |",
        f"| deterministic_gate_checked | {validation.deterministic_gate_checked} |",
        f"| source_count | {validation.source_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[SortingNetworkSourceRefreshGateBoundaryIssue], Path | None]:
    if isinstance(boundary, dict):
        return dict(boundary), [], None
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            return json.loads(boundary), [], None
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")], None
    try:
        path = Path(boundary)
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")], None
    if isinstance(data, dict):
        return data, [], path.resolve().parents[1]
    return None, [_issue("invalid_shape", "sorting-network source refresh-gate boundary must be a JSON object")], None


def _validate_script_artifact(
    value: object,
    issues: list[SortingNetworkSourceRefreshGateBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_script_artifact", "script_artifact must be an object"))
        return
    expected = {
        "path": EXPECTED_SCRIPT_PATH,
        "bytes": EXPECTED_SCRIPT_BYTES,
        "sha256": EXPECTED_SCRIPT_SHA256,
        "entrypoint": "run_refresh_gate",
        "cli": "py -3.12 -m libreevolve.tools.sorting_network_source_refresh_gate --live --pretty",
        "deterministic_cli": "py -3.12 -m libreevolve.tools.sorting_network_source_refresh_gate --pretty",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_script_artifact_{field}", f"script_artifact.{field} must be {expected_value}"))


def _validate_script_file(
    base_dir: Path,
    issues: list[SortingNetworkSourceRefreshGateBoundaryIssue],
) -> bool:
    script_path = base_dir / EXPECTED_SCRIPT_PATH
    try:
        data = script_path.read_bytes()
    except OSError as exc:
        issues.append(_issue("script_artifact_unreadable", f"{EXPECTED_SCRIPT_PATH} could not be read: {exc}"))
        return False
    if len(data) != EXPECTED_SCRIPT_BYTES:
        issues.append(_issue("script_artifact_bytes_drift", f"{EXPECTED_SCRIPT_PATH} byte count drifted"))
    if hashlib.sha256(data).hexdigest() != EXPECTED_SCRIPT_SHA256:
        issues.append(_issue("script_artifact_sha256_drift", f"{EXPECTED_SCRIPT_PATH} sha256 drifted"))
    return True


def _validate_deterministic_gate(
    issues: list[SortingNetworkSourceRefreshGateBoundaryIssue],
) -> bool:
    report = run_refresh_gate()
    if report.get("schema") != REPORT_SCHEMA:
        issues.append(_issue("deterministic_gate_schema_drift", "deterministic gate report schema drifted"))
    if report.get("ok") is not True:
        issues.append(_issue("deterministic_gate_failed", "deterministic gate did not pass"))
    if report.get("source_count") != len(EXPECTED_SOURCE_SNAPSHOTS):
        issues.append(_issue("deterministic_gate_source_count_drift", "deterministic gate source_count drifted"))
    return True


def _validate_expected_source_ids(
    value: object,
    issues: list[SortingNetworkSourceRefreshGateBoundaryIssue],
) -> int:
    expected = list(EXPECTED_SOURCE_SNAPSHOTS)
    if value != expected:
        issues.append(_issue("invalid_expected_source_ids", "expected_source_ids must match the source snapshot boundary order"))
        return len(value) if isinstance(value, list) else 0
    return len(expected)


def _validate_missing_evidence(
    value: object,
    issues: list[SortingNetworkSourceRefreshGateBoundaryIssue],
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


def _issue(code: str, message: str) -> SortingNetworkSourceRefreshGateBoundaryIssue:
    return SortingNetworkSourceRefreshGateBoundaryIssue(code, message)
