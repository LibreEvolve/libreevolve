from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

ALPHAEVOLVE_SOURCE_REFRESH_GATE_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_source_refresh_gate_boundary.v1"
)
EXPECTED_REPORT_SCHEMA = "libreevolve.alphaevolve_source_refresh_gate_report.v1"
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_VERSION_ID = "2506.13131v1"
EXPECTED_BOUNDARY_STATUS = (
    "scheduled_live_source_refresh_gate_recorded_with_archived_manual_outcome"
)
EXPECTED_SCRIPT_PATH = "libreevolve/tools/alphaevolve_source_refresh_gate.py"
EXPECTED_SCRIPT_BYTES = 9543
EXPECTED_SCRIPT_SHA256 = (
    "40a5dd07f3f190204d8fb13622f7b05ec2b94b2b9a28b60ceacc7afb9071ffd5"
)
EXPECTED_WORKFLOW_PATH = ".github/workflows/tests.yml"
EXPECTED_WORKFLOW_MARKERS = {
    "manual_input": "run_source_refresh_gate",
    "weekly_schedule": 'cron: "17 6 * * 1"',
    "job_id": "source_refresh_gate:",
    "live_gate_command": (
        "python -m libreevolve.tools.alphaevolve_source_refresh_gate --live --pretty"
    ),
}
EXPECTED_ARCHIVED_OUTCOME_PATH = "papers/alphaevolve_source_refresh_run_2026-06-14.json"
EXPECTED_ARCHIVED_OUTCOME_SCHEMA = "libreevolve.alphaevolve_source_refresh_run_boundary.v1"
EXPECTED_MISSING_EVIDENCE = {
    "scheduled_ci_refresh_run_history": "not_recorded_locally",
    "per_source_refresh_ready_promotion": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveSourceRefreshGateBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveSourceRefreshGateBoundaryValidation:
    ok: bool
    boundary_status: str | None
    script_artifact_checked: bool
    workflow_artifact_checked: bool
    deterministic_gate_checked: bool
    source_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveSourceRefreshGateBoundaryIssue]


def alphaevolve_source_refresh_gate_boundary_record() -> dict[str, Any]:
    """Return the AlphaEvolve live source refresh-gate boundary."""

    expected_sources = [expectation["source_id"] for expectation in source_expectations()]
    return {
        "schema": ALPHAEVOLVE_SOURCE_REFRESH_GATE_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_version_id": EXPECTED_SOURCE_VERSION_ID,
        "source_claim": (
            "AlphaEvolve source metadata should have a reusable live source "
            "refresh gate that compares current network responses with "
            "committed source boundaries."
        ),
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "script_artifact": {
            "path": EXPECTED_SCRIPT_PATH,
            "bytes": EXPECTED_SCRIPT_BYTES,
            "sha256": EXPECTED_SCRIPT_SHA256,
            "entrypoint": "run_refresh_gate",
            "cli": (
                "py -3.12 -m libreevolve.tools.alphaevolve_source_refresh_gate "
                "--live --pretty"
            ),
            "deterministic_cli": (
                "py -3.12 -m libreevolve.tools.alphaevolve_source_refresh_gate "
                "--pretty"
            ),
        },
        "workflow_artifact": {
            "path": EXPECTED_WORKFLOW_PATH,
            "job_id": "source_refresh_gate",
            "schedule_cron": "17 6 * * 1",
            "manual_dispatch_input": "run_source_refresh_gate",
            "live_gate_command": EXPECTED_WORKFLOW_MARKERS["live_gate_command"],
        },
        "archived_outcome_artifact": {
            "path": EXPECTED_ARCHIVED_OUTCOME_PATH,
            "schema": EXPECTED_ARCHIVED_OUTCOME_SCHEMA,
            "run_date": "2026-06-14",
            "run_mode": "live_network",
        },
        "expected_report_schema": EXPECTED_REPORT_SCHEMA,
        "expected_source_ids": expected_sources,
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records a deterministic AlphaEvolve source refresh "
            "gate script plus scheduled and manual GitHub Actions live-network "
            "execution wiring and a committed manual live-run outcome sidecar. "
            "It does not claim that scheduled CI refresh-run history has been "
            "archived or that the older per-source sidecars themselves are "
            "individually promoted to refresh-ready evidence."
        ),
    }


def validate_alphaevolve_source_refresh_gate_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveSourceRefreshGateBoundaryValidation:
    data, read_issues, base_dir = _load_boundary(
        alphaevolve_source_refresh_gate_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveSourceRefreshGateBoundaryValidation(
            False, None, False, False, False, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveSourceRefreshGateBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_SOURCE_REFRESH_GATE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported source refresh-gate boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_version_id") != EXPECTED_SOURCE_VERSION_ID:
        issues.append(_issue("invalid_source_version_id", "source_version_id must be 2506.13131v1"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "live source refresh gate" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must describe the live source refresh gate"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "source refresh-gate boundary must not claim archived live-run readiness"))
    _validate_script_artifact(data.get("script_artifact"), issues)
    _validate_workflow_artifact(data.get("workflow_artifact"), issues)
    _validate_archived_outcome_artifact(data.get("archived_outcome_artifact"), issues)
    source_count = _validate_expected_source_ids(data.get("expected_source_ids"), issues)
    if data.get("expected_report_schema") != EXPECTED_REPORT_SCHEMA:
        issues.append(_issue("invalid_expected_report_schema", f"expected_report_schema must be {EXPECTED_REPORT_SCHEMA}"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "scheduled and manual GitHub Actions live-network execution" not in boundary_text
        or "committed manual live-run outcome sidecar" not in boundary_text
        or "does not claim that scheduled CI refresh-run history has been archived" not in boundary_text
        or "per-source sidecars" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate refresh-gate wiring from archived live-run evidence"))

    script_checked = False
    workflow_checked = False
    deterministic_checked = False
    if base_dir is not None:
        script_checked = _validate_script_file(base_dir, issues)
        workflow_checked = _validate_workflow_file(base_dir, issues)
        deterministic_checked = _validate_deterministic_gate(issues)

    return AlphaEvolveSourceRefreshGateBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        script_artifact_checked=script_checked,
        workflow_artifact_checked=workflow_checked,
        deterministic_gate_checked=deterministic_checked,
        source_count=source_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_source_refresh_gate_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_source_refresh_gate_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve source refresh-gate boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| script_artifact_checked | {validation.script_artifact_checked} |",
        f"| workflow_artifact_checked | {validation.workflow_artifact_checked} |",
        f"| deterministic_gate_checked | {validation.deterministic_gate_checked} |",
        f"| source_count | {validation.source_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _validate_script_artifact(
    value: object,
    issues: list[AlphaEvolveSourceRefreshGateBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_script_artifact", "script_artifact must be an object"))
        return
    expected = {
        "path": EXPECTED_SCRIPT_PATH,
        "bytes": EXPECTED_SCRIPT_BYTES,
        "sha256": EXPECTED_SCRIPT_SHA256,
        "entrypoint": "run_refresh_gate",
        "cli": "py -3.12 -m libreevolve.tools.alphaevolve_source_refresh_gate --live --pretty",
        "deterministic_cli": "py -3.12 -m libreevolve.tools.alphaevolve_source_refresh_gate --pretty",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_script_artifact_{field}", f"script_artifact.{field} must be {expected_value}"))


def _validate_workflow_artifact(
    value: object,
    issues: list[AlphaEvolveSourceRefreshGateBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_workflow_artifact", "workflow_artifact must be an object"))
        return
    expected = {
        "path": EXPECTED_WORKFLOW_PATH,
        "job_id": "source_refresh_gate",
        "schedule_cron": "17 6 * * 1",
        "manual_dispatch_input": "run_source_refresh_gate",
        "live_gate_command": EXPECTED_WORKFLOW_MARKERS["live_gate_command"],
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_workflow_artifact_{field}", f"workflow_artifact.{field} must be {expected_value}"))


def _validate_archived_outcome_artifact(
    value: object,
    issues: list[AlphaEvolveSourceRefreshGateBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_archived_outcome_artifact", "archived_outcome_artifact must be an object"))
        return
    expected = {
        "path": EXPECTED_ARCHIVED_OUTCOME_PATH,
        "schema": EXPECTED_ARCHIVED_OUTCOME_SCHEMA,
        "run_date": "2026-06-14",
        "run_mode": "live_network",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_archived_outcome_artifact_{field}", f"archived_outcome_artifact.{field} must be {expected_value}"))


def _validate_expected_source_ids(
    value: object,
    issues: list[AlphaEvolveSourceRefreshGateBoundaryIssue],
) -> int:
    if not isinstance(value, list):
        issues.append(_issue("invalid_expected_source_ids", "expected_source_ids must be a list"))
        return 0
    expected = [expectation["source_id"] for expectation in source_expectations()]
    if value != expected:
        issues.append(_issue("invalid_expected_source_ids", "expected_source_ids must match source refresh gate expectations"))
    if not all(isinstance(item, str) for item in value):
        issues.append(_issue("invalid_expected_source_id", "expected_source_ids entries must be strings"))
    return len(value)


def _validate_missing_evidence(
    value: object,
    issues: list[AlphaEvolveSourceRefreshGateBoundaryIssue],
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


def _validate_script_file(
    base_dir: Path,
    issues: list[AlphaEvolveSourceRefreshGateBoundaryIssue],
) -> bool:
    path = base_dir / EXPECTED_SCRIPT_PATH
    try:
        data = path.read_bytes()
    except OSError as exc:
        issues.append(_issue("unreadable_script_artifact_file", f"script artifact file could not be read: {exc}"))
        return False
    if len(data) != EXPECTED_SCRIPT_BYTES:
        issues.append(_issue("invalid_script_artifact_file_bytes", f"script artifact file must be {EXPECTED_SCRIPT_BYTES} bytes"))
    digest = hashlib.sha256(data).hexdigest()
    if digest != EXPECTED_SCRIPT_SHA256:
        issues.append(_issue("invalid_script_artifact_file_sha256", f"script artifact file SHA-256 must be {EXPECTED_SCRIPT_SHA256}"))
    return True


def _validate_workflow_file(
    base_dir: Path,
    issues: list[AlphaEvolveSourceRefreshGateBoundaryIssue],
) -> bool:
    path = base_dir / EXPECTED_WORKFLOW_PATH
    try:
        workflow_text = path.read_text(encoding="utf-8")
    except OSError as exc:
        issues.append(_issue("unreadable_workflow_artifact_file", f"workflow artifact file could not be read: {exc}"))
        return False
    for marker_id, marker in EXPECTED_WORKFLOW_MARKERS.items():
        if marker not in workflow_text:
            issues.append(_issue(f"missing_workflow_marker_{marker_id}", f"workflow file must contain {marker}"))
    return True


def _validate_deterministic_gate(
    issues: list[AlphaEvolveSourceRefreshGateBoundaryIssue],
) -> bool:
    from libreevolve.tools.alphaevolve_source_refresh_gate import run_refresh_gate

    report = run_refresh_gate(live=False)
    if report.get("schema") != EXPECTED_REPORT_SCHEMA:
        issues.append(_issue("invalid_deterministic_gate_schema", "deterministic gate report schema is incorrect"))
    if report.get("ok") is not True:
        issues.append(_issue("invalid_deterministic_gate_status", "deterministic gate report must be ok"))
    if report.get("source_count") != len(source_expectations()):
        issues.append(_issue("invalid_deterministic_gate_source_count", "deterministic gate must cover all source expectations"))
    return True


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveSourceRefreshGateBoundaryIssue], Path | None]:
    base_dir: Path | None = None
    if isinstance(boundary, dict):
        return dict(boundary), [], None
    if isinstance(boundary, str) and boundary.strip().startswith("{"):
        try:
            data = json.loads(boundary)
        except json.JSONDecodeError as exc:
            return None, [_issue("invalid_json", f"boundary JSON is invalid: {exc}")], None
    else:
        try:
            path = Path(boundary)
            data = json.loads(path.read_text(encoding="utf-8"))
            base_dir = path.parent.parent
        except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
            return None, [_issue("unreadable_boundary", f"boundary could not be loaded: {exc}")], None
    if isinstance(data, dict):
        return data, [], base_dir
    return None, [_issue("invalid_shape", "source refresh-gate boundary must be a JSON object")], base_dir


def _issue(
    code: str,
    message: str,
) -> AlphaEvolveSourceRefreshGateBoundaryIssue:
    return AlphaEvolveSourceRefreshGateBoundaryIssue(code, message)


def source_expectations() -> list[dict[str, Any]]:
    from libreevolve.tools.alphaevolve_source_refresh_gate import source_expectations as _source_expectations

    return _source_expectations()
