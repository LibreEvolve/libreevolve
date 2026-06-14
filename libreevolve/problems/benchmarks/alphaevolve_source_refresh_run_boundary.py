from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from libreevolve.problems.benchmarks.alphaevolve_source_refresh_gate_boundary import (
    EXPECTED_REPORT_SCHEMA,
    EXPECTED_SCRIPT_BYTES,
    EXPECTED_SCRIPT_PATH,
    EXPECTED_SCRIPT_SHA256,
    source_expectations,
)


ALPHAEVOLVE_SOURCE_REFRESH_RUN_BOUNDARY_SCHEMA = (
    "libreevolve.alphaevolve_source_refresh_run_boundary.v1"
)
EXPECTED_SOURCE_PAPER_ID = "2506.13131"
EXPECTED_SOURCE_VERSION_ID = "2506.13131v1"
EXPECTED_BOUNDARY_STATUS = (
    "manual_live_source_refresh_run_archived_without_scheduled_history"
)
EXPECTED_RUN_DATE = "2026-06-14"
EXPECTED_RUN_MODE = "live_network"
EXPECTED_RUN_CONTEXT = "manual_local_network_run"
EXPECTED_OBSERVED_CONTENT_TYPES = {
    "versioned_abstract": "text/html; charset=utf-8",
    "current_abstract": "text/html; charset=utf-8",
    "floating_pdf": "application/pdf",
    "datacite_api": "application/json; charset=utf-8",
    "eprint_archive": "application/gzip",
    "license_page": "text/html",
}
EXPECTED_MISSING_EVIDENCE = {
    "scheduled_ci_refresh_run_history": "not_recorded_locally",
}


@dataclass(frozen=True)
class AlphaEvolveSourceRefreshRunBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class AlphaEvolveSourceRefreshRunBoundaryValidation:
    ok: bool
    boundary_status: str | None
    script_artifact_checked: bool
    run_report_checked: bool
    source_count: int
    missing_evidence_count: int
    issues: list[AlphaEvolveSourceRefreshRunBoundaryIssue]


def alphaevolve_source_refresh_run_boundary_record() -> dict[str, Any]:
    """Return the archived AlphaEvolve source refresh run boundary."""

    run_report = expected_live_run_report()
    return {
        "schema": ALPHAEVOLVE_SOURCE_REFRESH_RUN_BOUNDARY_SCHEMA,
        "source_paper_id": EXPECTED_SOURCE_PAPER_ID,
        "source_version_id": EXPECTED_SOURCE_VERSION_ID,
        "source_claim": (
            "AlphaEvolve source freshness evidence should retain successful "
            "live refresh run outcomes, not only the executable refresh gate."
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
                "py -3.12 -m libreevolve.tools.alphaevolve_source_refresh_gate "
                "--live --pretty"
            ),
        },
        "run_report_sha256": _canonical_sha256(run_report),
        "run_report": run_report,
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary archives one successful manual live-network source "
            "refresh run for AlphaEvolve. It does not claim scheduled CI "
            "refresh-run history or promote the older per-source snapshot "
            "sidecars to standalone refresh-ready evidence."
        ),
    }


def expected_live_run_report() -> dict[str, Any]:
    checks = []
    for expectation in source_expectations():
        source_id = expectation["source_id"]
        content_type = EXPECTED_OBSERVED_CONTENT_TYPES[source_id]
        checks.append(
            {
                "expected": {
                    "bytes": expectation["expected_bytes"],
                    "content_type": expectation["expected_content_type"],
                    "sha256": expectation["expected_sha256"],
                    "status": expectation["expected_status"],
                },
                "issues": [],
                "observed": {
                    "bytes": expectation["expected_bytes"],
                    "content_type": content_type,
                    "sha256": expectation["expected_sha256"],
                    "status": expectation["expected_status"],
                },
                "ok": True,
                "source_id": source_id,
                "url": expectation["url"],
            }
        )
    return {
        "checks": checks,
        "claim_boundary": (
            "Compares live response status, content type, byte count, and "
            "SHA-256 digest against committed AlphaEvolve source boundaries."
        ),
        "mode": EXPECTED_RUN_MODE,
        "ok": True,
        "schema": EXPECTED_REPORT_SCHEMA,
        "source_count": len(checks),
    }


def validate_alphaevolve_source_refresh_run_boundary(
    boundary: object | str | Path | None = None,
) -> AlphaEvolveSourceRefreshRunBoundaryValidation:
    data, read_issues, base_dir = _load_boundary(
        alphaevolve_source_refresh_run_boundary_record()
        if boundary is None
        else boundary
    )
    if read_issues:
        return AlphaEvolveSourceRefreshRunBoundaryValidation(
            False, None, False, False, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    issues: list[AlphaEvolveSourceRefreshRunBoundaryIssue] = []
    if data.get("schema") != ALPHAEVOLVE_SOURCE_REFRESH_RUN_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported source refresh-run boundary schema"))
    if data.get("source_paper_id") != EXPECTED_SOURCE_PAPER_ID:
        issues.append(_issue("invalid_source_paper_id", "source_paper_id must be 2506.13131"))
    if data.get("source_version_id") != EXPECTED_SOURCE_VERSION_ID:
        issues.append(_issue("invalid_source_version_id", "source_version_id must be 2506.13131v1"))
    source_claim = data.get("source_claim")
    if not isinstance(source_claim, str) or "live refresh run outcomes" not in source_claim:
        issues.append(_issue("invalid_source_claim", "source_claim must describe retained live refresh run outcomes"))
    status = data.get("boundary_status")
    if status != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "source refresh-run boundary must not claim scheduled CI history or per-source promotion"))
    if data.get("run_date") != EXPECTED_RUN_DATE:
        issues.append(_issue("invalid_run_date", f"run_date must be {EXPECTED_RUN_DATE}"))
    if data.get("run_context") != EXPECTED_RUN_CONTEXT:
        issues.append(_issue("invalid_run_context", f"run_context must be {EXPECTED_RUN_CONTEXT}"))
    _validate_refresh_gate_artifact(data.get("refresh_gate_artifact"), issues)
    run_report_checked, source_count = _validate_run_report(
        data.get("run_report"),
        data.get("run_report_sha256"),
        issues,
    )
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "archives one successful manual live-network source refresh run" not in boundary_text
        or "does not claim scheduled CI refresh-run history" not in boundary_text
        or "per-source snapshot sidecars" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate one manual live run from scheduled/per-source readiness"))
    script_checked = False
    if base_dir is not None:
        script_checked = _validate_script_file(base_dir, issues)
    return AlphaEvolveSourceRefreshRunBoundaryValidation(
        ok=not issues,
        boundary_status=status if isinstance(status, str) else None,
        script_artifact_checked=script_checked,
        run_report_checked=run_report_checked,
        source_count=source_count,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_alphaevolve_source_refresh_run_boundary_summary(
    boundary: dict[str, Any],
) -> str:
    validation = validate_alphaevolve_source_refresh_run_boundary(boundary)
    status = "ok" if validation.ok else "invalid"
    lines = [
        "AlphaEvolve source refresh-run boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {status} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| script_artifact_checked | {validation.script_artifact_checked} |",
        f"| run_report_checked | {validation.run_report_checked} |",
        f"| source_count | {validation.source_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _validate_refresh_gate_artifact(
    value: object,
    issues: list[AlphaEvolveSourceRefreshRunBoundaryIssue],
) -> None:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_refresh_gate_artifact", "refresh_gate_artifact must be an object"))
        return
    expected = {
        "path": EXPECTED_SCRIPT_PATH,
        "bytes": EXPECTED_SCRIPT_BYTES,
        "sha256": EXPECTED_SCRIPT_SHA256,
        "command": "py -3.12 -m libreevolve.tools.alphaevolve_source_refresh_gate --live --pretty",
    }
    for field, expected_value in expected.items():
        if value.get(field) != expected_value:
            issues.append(_issue(f"invalid_refresh_gate_artifact_{field}", f"refresh_gate_artifact.{field} must be {expected_value}"))


def _validate_run_report(
    value: object,
    digest_value: object,
    issues: list[AlphaEvolveSourceRefreshRunBoundaryIssue],
) -> tuple[bool, int]:
    if not isinstance(value, dict):
        issues.append(_issue("invalid_run_report", "run_report must be an object"))
        return False, 0
    expected_digest = _canonical_sha256(value)
    if digest_value != expected_digest:
        issues.append(_issue("invalid_run_report_sha256", f"run_report_sha256 must be {expected_digest}"))
    if value.get("schema") != EXPECTED_REPORT_SCHEMA:
        issues.append(_issue("invalid_run_report_schema", f"run_report schema must be {EXPECTED_REPORT_SCHEMA}"))
    if value.get("mode") != EXPECTED_RUN_MODE:
        issues.append(_issue("invalid_run_report_mode", f"run_report mode must be {EXPECTED_RUN_MODE}"))
    if value.get("ok") is not True:
        issues.append(_issue("invalid_run_report_status", "run_report must be ok"))
    checks = value.get("checks")
    if not isinstance(checks, list):
        issues.append(_issue("invalid_run_report_checks", "run_report checks must be a list"))
        return True, 0
    expected = {expectation["source_id"]: expectation for expectation in source_expectations()}
    if value.get("source_count") != len(expected):
        issues.append(_issue("invalid_run_report_source_count", f"run_report source_count must be {len(expected)}"))
    seen: set[str] = set()
    for check in checks:
        if not isinstance(check, dict):
            issues.append(_issue("invalid_run_report_check", "run_report checks entries must be objects"))
            continue
        source_id = check.get("source_id")
        if not isinstance(source_id, str) or source_id not in expected:
            issues.append(_issue("invalid_run_report_source_id", "run_report check source_id is not expected"))
            continue
        seen.add(source_id)
        _validate_check(source_id, expected[source_id], check, issues)
    missing = sorted(set(expected) - seen)
    extra = sorted(seen - set(expected))
    if missing:
        issues.append(_issue("missing_run_report_source", f"run_report lacks sources: {', '.join(missing)}"))
    if extra:
        issues.append(_issue("extra_run_report_source", f"run_report has unknown sources: {', '.join(extra)}"))
    return True, len(checks)


def _validate_check(
    source_id: str,
    expectation: dict[str, Any],
    check: dict[str, Any],
    issues: list[AlphaEvolveSourceRefreshRunBoundaryIssue],
) -> None:
    if check.get("ok") is not True:
        issues.append(_issue(f"invalid_{source_id}_check_status", f"{source_id} check must be ok"))
    if check.get("issues") != []:
        issues.append(_issue(f"invalid_{source_id}_check_issues", f"{source_id} check issues must be empty"))
    if check.get("url") != expectation["url"]:
        issues.append(_issue(f"invalid_{source_id}_url", f"{source_id} URL must match expectation"))
    expected = check.get("expected")
    observed = check.get("observed")
    if not isinstance(expected, dict) or not isinstance(observed, dict):
        issues.append(_issue(f"invalid_{source_id}_snapshot", f"{source_id} expected/observed snapshots must be objects"))
        return
    expected_snapshot = {
        "status": expectation["expected_status"],
        "content_type": expectation["expected_content_type"],
        "bytes": expectation["expected_bytes"],
        "sha256": expectation["expected_sha256"],
    }
    if expected != expected_snapshot:
        issues.append(_issue(f"invalid_{source_id}_expected_snapshot", f"{source_id} expected snapshot must match committed expectation"))
    if observed.get("status") != expectation["expected_status"]:
        issues.append(_issue(f"invalid_{source_id}_observed_status", f"{source_id} observed status drifted"))
    content_type = observed.get("content_type")
    if not isinstance(content_type, str) or not content_type.startswith(expectation["expected_content_type"]):
        issues.append(_issue(f"invalid_{source_id}_observed_content_type", f"{source_id} observed content type drifted"))
    if observed.get("bytes") != expectation["expected_bytes"]:
        issues.append(_issue(f"invalid_{source_id}_observed_bytes", f"{source_id} observed bytes drifted"))
    if observed.get("sha256") != expectation["expected_sha256"]:
        issues.append(_issue(f"invalid_{source_id}_observed_sha256", f"{source_id} observed SHA-256 drifted"))


def _validate_missing_evidence(
    value: object,
    issues: list[AlphaEvolveSourceRefreshRunBoundaryIssue],
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
    issues: list[AlphaEvolveSourceRefreshRunBoundaryIssue],
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


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[AlphaEvolveSourceRefreshRunBoundaryIssue], Path | None]:
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
    return None, [_issue("invalid_shape", "source refresh-run boundary must be a JSON object")], base_dir


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def _issue(code: str, message: str) -> AlphaEvolveSourceRefreshRunBoundaryIssue:
    return AlphaEvolveSourceRefreshRunBoundaryIssue(code, message)
