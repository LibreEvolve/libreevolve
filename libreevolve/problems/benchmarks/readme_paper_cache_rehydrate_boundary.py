from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_PAPER_CACHE_REHYDRATE_BOUNDARY_SCHEMA = (
    "libreevolve.readme_paper_cache_rehydrate_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "readme_rehydrate_cli_and_test_markers_without_clean_checkout_transcript"
)
README_PATH = "README.md"
PAPERS_README_PATH = "papers/README.md"
PAPER_MANIFEST_TOOL_PATH = "libreevolve/tools/paper_manifest.py"
PAPER_MANIFEST_TEST_PATH = "tests/test_paper_manifest.py"
DOWNLOAD_MANIFEST_PATH = "papers/download_manifest.json"
EXPECTED_REHYDRATE_COMMAND = "py -3.12 -m libreevolve.tools.paper_manifest --rehydrate"
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_rehydrate_command",
    "papers_readme_rehydrate_command",
    "download_manifest_rows",
    "rehydrate_cli_flag",
    "rehydrate_force_flag",
    "rehydrate_timeout_flag",
    "rehydrate_report_fields",
    "missing_pdf_download_test",
    "existing_pdf_skip_test",
    "force_redownload_test",
    "redacted_network_failure_test",
    "clean_checkout_absent_cache_transcript",
    "network_outcome_matrix",
    "hash_verification_transcript",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "clean_checkout_absent_cache_transcript": "not_recorded_locally",
    "network_outcome_matrix": "not_recorded_locally",
    "hash_verification_transcript": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmePaperCacheRehydrateBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmePaperCacheRehydrateBoundaryValidation:
    ok: bool
    boundary_status: str | None
    manifest_row_count: int
    missing_marker_count: int
    missing_evidence_count: int
    issues: list[ReadmePaperCacheRehydrateBoundaryIssue]


def readme_paper_cache_rehydrate_boundary_record(
    root: str | Path = ".",
) -> dict[str, Any]:
    """Return the README paper-cache rehydrate boundary record."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    papers_readme_text = _read_text(root_path / PAPERS_README_PATH)
    tool_text = _read_text(root_path / PAPER_MANIFEST_TOOL_PATH)
    test_text = _read_text(root_path / PAPER_MANIFEST_TEST_PATH)
    manifest_rows = _manifest_rows(root_path / DOWNLOAD_MANIFEST_PATH)
    marker_records = [
        _marker_record("readme_rehydrate_command", README_PATH, readme_text, EXPECTED_REHYDRATE_COMMAND),
        _marker_record("papers_readme_rehydrate_command", PAPERS_README_PATH, papers_readme_text, EXPECTED_REHYDRATE_COMMAND),
        _marker_record("tool_rehydrate_function", PAPER_MANIFEST_TOOL_PATH, tool_text, "def rehydrate_paper_cache("),
        _marker_record("tool_rehydrate_flag", PAPER_MANIFEST_TOOL_PATH, tool_text, '"--rehydrate"'),
        _marker_record("tool_force_flag", PAPER_MANIFEST_TOOL_PATH, tool_text, '"--force"'),
        _marker_record("tool_timeout_flag", PAPER_MANIFEST_TOOL_PATH, tool_text, '"--timeout"'),
        _marker_record("tool_report_row_count", PAPER_MANIFEST_TOOL_PATH, tool_text, "row_count=len(rows)"),
        _marker_record("tool_report_downloaded_count", PAPER_MANIFEST_TOOL_PATH, tool_text, "downloaded_count=downloaded_count"),
        _marker_record("tool_report_existing_count", PAPER_MANIFEST_TOOL_PATH, tool_text, "verified_existing_count=verified_existing_count"),
        _marker_record("tool_report_failed_count", PAPER_MANIFEST_TOOL_PATH, tool_text, "failed_count=failed_count"),
        _marker_record("tool_sanitize_download_message", PAPER_MANIFEST_TOOL_PATH, tool_text, "def _sanitize_download_message"),
        _marker_record("test_missing_pdf_download", PAPER_MANIFEST_TEST_PATH, test_text, "test_rehydrate_paper_cache_downloads_missing_pdf_and_validates_hash"),
        _marker_record("test_existing_pdf_skip", PAPER_MANIFEST_TEST_PATH, test_text, "test_rehydrate_paper_cache_skips_existing_matching_pdf"),
        _marker_record("test_force_redownload", PAPER_MANIFEST_TEST_PATH, test_text, "test_rehydrate_paper_cache_force_redownloads_matching_pdf"),
        _marker_record("test_redacted_network_failure", PAPER_MANIFEST_TEST_PATH, test_text, "test_paper_manifest_rehydrate_json_reports_redacted_network_failure"),
    ]
    missing_marker_records = [
        record for record in marker_records if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": README_PAPER_CACHE_REHYDRATE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "papers_readme_path": PAPERS_README_PATH,
        "paper_manifest_tool_path": PAPER_MANIFEST_TOOL_PATH,
        "paper_manifest_test_path": PAPER_MANIFEST_TEST_PATH,
        "download_manifest_path": DOWNLOAD_MANIFEST_PATH,
        "readme_rehydrate_command": EXPECTED_REHYDRATE_COMMAND,
        "manifest_row_count": len(manifest_rows),
        "marker_record_count": len(marker_records),
        "missing_marker_count": len(missing_marker_records),
        "missing_marker_records": missing_marker_records,
        "marker_records": marker_records,
        "rehydrate_marker_status": (
            "readme_rehydrate_cli_and_tests_present"
            if not missing_marker_records and manifest_rows
            else "readme_rehydrate_cli_and_tests_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README and papers-index rehydrate "
            "commands, manifest row count, paper-manifest CLI flags, rehydrate "
            "report fields, missing-PDF download test, existing-PDF skip test, "
            "force-redownload test, and redacted network-failure test. It does "
            "not claim a clean-checkout absent-cache transcript, live network "
            "outcome matrix, full hash-verification transcript, or owner review "
            "signoff."
        ),
    }


def validate_readme_paper_cache_rehydrate_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmePaperCacheRehydrateBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_paper_cache_rehydrate_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return ReadmePaperCacheRehydrateBoundaryValidation(False, None, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = readme_paper_cache_rehydrate_boundary_record(root)
    issues: list[ReadmePaperCacheRehydrateBoundaryIssue] = []
    if data.get("schema") != README_PAPER_CACHE_REHYDRATE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README paper-cache rehydrate boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README rehydrate boundary must not claim clean-checkout proof"))
    for key in (
        "readme_path",
        "papers_readme_path",
        "paper_manifest_tool_path",
        "paper_manifest_test_path",
        "download_manifest_path",
        "readme_rehydrate_command",
        "manifest_row_count",
        "marker_record_count",
        "missing_marker_count",
        "missing_marker_records",
        "marker_records",
        "rehydrate_marker_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current rehydrate inputs"))
    if data.get("manifest_row_count", 0) <= 0:
        issues.append(_issue("missing_manifest_rows", "download manifest rows must be recorded"))
    if data.get("missing_marker_count") != 0:
        issues.append(_issue("missing_rehydrate_marker", "README rehydrate markers are incomplete"))
    if data.get("rehydrate_marker_status") != "readme_rehydrate_cli_and_tests_present":
        issues.append(_issue("invalid_rehydrate_marker_status", "README rehydrate markers must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README and papers-index rehydrate commands" not in boundary_text
        or "redacted network-failure test" not in boundary_text
        or "does not claim a clean-checkout absent-cache transcript" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate rehydrate markers from clean-checkout proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmePaperCacheRehydrateBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        manifest_row_count=data.get("manifest_row_count") if isinstance(data.get("manifest_row_count"), int) else 0,
        missing_marker_count=data.get("missing_marker_count") if isinstance(data.get("missing_marker_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_paper_cache_rehydrate_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_paper_cache_rehydrate_boundary(boundary)
    lines = [
        "README paper-cache rehydrate boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| manifest_row_count | {validation.manifest_row_count} |",
        f"| missing_marker_count | {validation.missing_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _manifest_rows(path: Path) -> list[dict[str, Any]]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    if not isinstance(data, list):
        return []
    return [row for row in data if isinstance(row, dict)]


def _marker_record(kind: str, path: str, text: str, marker: str) -> dict[str, Any]:
    return {
        "record_kind": kind,
        "path": path,
        "required_marker": marker,
        "marker_status": "marker_present" if marker in text else "marker_missing",
    }


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ReadmePaperCacheRehydrateBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README paper-cache rehydrate boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmePaperCacheRehydrateBoundaryIssue],
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
    issues: list[ReadmePaperCacheRehydrateBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmePaperCacheRehydrateBoundaryIssue:
    return ReadmePaperCacheRehydrateBoundaryIssue(code, message)
