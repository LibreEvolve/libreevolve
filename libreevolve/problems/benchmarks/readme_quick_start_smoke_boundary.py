from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_QUICK_START_SMOKE_BOUNDARY_SCHEMA = (
    "libreevolve.readme_quick_start_smoke_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "readme_quick_start_smoke_test_recorded_without_ci_matrix"
)
README_PATH = "README.md"
SMOKE_TEST_PATH = "tests/test_readme_quick_start_smoke_boundary.py"
RUN_COMMAND = (
    "py -3.12 -m libreevolve run libreevolve/problems/examples/sorting "
    "--run-name readme_smoke_sorting --max-llm-calls 0 --overwrite"
)
SHOW_COMMAND = "py -3.12 -m libreevolve show runs/readme_smoke_sorting"
EXPECTED_README_MARKERS = (
    "## Quick Start",
    "Verify the CLI and artifact writer without making provider calls",
    RUN_COMMAND,
    SHOW_COMMAND,
    "That evaluates the bundled sorting seed",
    "It is a smoke check, not an evolution run.",
)
EXPECTED_TEST_MARKERS = (
    "test_readme_quick_start_smoke_executes_documented_no_provider_path",
    "readme_smoke_sorting",
    "max_llm_calls",
    "stop_reason",
    "max_llm_calls",
    "Best fitness:   1.000000",
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_quick_start_command_markers",
    "focused_smoke_test_file",
    "run_command_exit_code_check",
    "show_command_exit_code_check",
    "manifest_stop_reason_check",
    "show_best_fitness_check",
    "provider_preflight_skip_check",
    "ci_job_integration",
    "cross_platform_shell_transcript",
    "fresh_checkout_transcript",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "ci_job_integration": "not_recorded_locally",
    "cross_platform_shell_transcript": "not_recorded_locally",
    "fresh_checkout_transcript": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeQuickStartSmokeBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeQuickStartSmokeBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readme_marker_count: int
    missing_readme_marker_count: int
    missing_test_marker_count: int
    missing_evidence_count: int
    issues: list[ReadmeQuickStartSmokeBoundaryIssue]


def readme_quick_start_smoke_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the bounded README quick-start smoke proof inventory."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    test_text = _read_text(root_path / SMOKE_TEST_PATH)
    readme_marker_records = [
        _marker_record("readme_quick_start", README_PATH, readme_text, marker)
        for marker in EXPECTED_README_MARKERS
    ]
    test_marker_records = [
        _marker_record("focused_smoke_test", SMOKE_TEST_PATH, test_text, marker)
        for marker in EXPECTED_TEST_MARKERS
    ]
    missing_readme_markers = [
        record for record in readme_marker_records if record["marker_status"] != "marker_present"
    ]
    missing_test_markers = [
        record for record in test_marker_records if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": README_QUICK_START_SMOKE_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "smoke_test_path": SMOKE_TEST_PATH,
        "run_command": RUN_COMMAND,
        "show_command": SHOW_COMMAND,
        "readme_marker_count": len(readme_marker_records),
        "missing_readme_marker_count": len(missing_readme_markers),
        "missing_readme_marker_records": missing_readme_markers,
        "readme_marker_records": readme_marker_records,
        "test_marker_count": len(test_marker_records),
        "missing_test_marker_count": len(missing_test_markers),
        "missing_test_marker_records": missing_test_markers,
        "test_marker_records": test_marker_records,
        "expected_run_name": "readme_smoke_sorting",
        "expected_problem_path": "libreevolve/problems/examples/sorting",
        "expected_stop_reason": "max_llm_calls",
        "expected_best_fitness": "1.000000",
        "provider_call_policy": "max_llm_calls_zero_before_provider_construction",
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README Quick Start no-provider command "
            "markers, focused smoke-test file markers, expected run name, "
            "problem path, max_llm_calls stop reason, show-output best fitness, "
            "and provider-preflight skip policy. It does not claim CI job "
            "integration, a cross-platform shell transcript, fresh-checkout "
            "transcript retention, or owner review signoff."
        ),
    }


def validate_readme_quick_start_smoke_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeQuickStartSmokeBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_quick_start_smoke_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeQuickStartSmokeBoundaryValidation(False, None, 0, 0, 0, 0, read_issues)
    assert isinstance(data, dict)
    expected = readme_quick_start_smoke_boundary_record(root)
    issues: list[ReadmeQuickStartSmokeBoundaryIssue] = []
    if data.get("schema") != README_QUICK_START_SMOKE_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README quick-start smoke boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README quick-start smoke boundary must not claim CI/fresh-checkout proof"))
    for key in (
        "readme_path",
        "smoke_test_path",
        "run_command",
        "show_command",
        "readme_marker_count",
        "missing_readme_marker_count",
        "missing_readme_marker_records",
        "readme_marker_records",
        "test_marker_count",
        "missing_test_marker_count",
        "missing_test_marker_records",
        "test_marker_records",
        "expected_run_name",
        "expected_problem_path",
        "expected_stop_reason",
        "expected_best_fitness",
        "provider_call_policy",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from README quick-start smoke inputs"))
    if data.get("missing_readme_marker_count") != 0:
        issues.append(_issue("missing_readme_quick_start_marker", "README quick-start command markers are incomplete"))
    if data.get("missing_test_marker_count") != 0:
        issues.append(_issue("missing_smoke_test_marker", "focused quick-start smoke test markers are incomplete"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README Quick Start no-provider command markers" not in boundary_text
        or "max_llm_calls stop reason" not in boundary_text
        or "does not claim CI job integration" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate focused smoke proof from CI/fresh-checkout proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmeQuickStartSmokeBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readme_marker_count=data.get("readme_marker_count") if isinstance(data.get("readme_marker_count"), int) else 0,
        missing_readme_marker_count=(
            data.get("missing_readme_marker_count")
            if isinstance(data.get("missing_readme_marker_count"), int)
            else 0
        ),
        missing_test_marker_count=(
            data.get("missing_test_marker_count")
            if isinstance(data.get("missing_test_marker_count"), int)
            else 0
        ),
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_quick_start_smoke_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_quick_start_smoke_boundary(boundary)
    lines = [
        "README quick-start smoke boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| readme_marker_count | {validation.readme_marker_count} |",
        f"| missing_readme_marker_count | {validation.missing_readme_marker_count} |",
        f"| missing_test_marker_count | {validation.missing_test_marker_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


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
) -> tuple[dict[str, Any] | None, list[ReadmeQuickStartSmokeBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README quick-start smoke boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeQuickStartSmokeBoundaryIssue],
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
    issues: list[ReadmeQuickStartSmokeBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeQuickStartSmokeBoundaryIssue:
    return ReadmeQuickStartSmokeBoundaryIssue(code, message)
