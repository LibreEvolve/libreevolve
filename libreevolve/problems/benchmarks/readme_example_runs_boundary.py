from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_EXAMPLE_RUNS_BOUNDARY_SCHEMA = "libreevolve.readme_example_runs_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "example_runs_readme_structural_fixture_map_without_reproducibility_proof"
)
EXAMPLE_RUNS_README_PATH = "examples/runs/README.md"
README_TODO_PATH = "docs/todo/readme.md"
RUN_ARTIFACTS_DOC_PATH = "docs/run-artifacts.md"
CLI_PATH = "libreevolve/cli.py"
CLI_TEST_PATH = "tests/test_cli.py"
EXPECTED_FIXTURES = {
    "hello_world_ensemble": {
        "readme_marker": "`hello_world_ensemble/`: 11 records",
        "record_count": 11,
        "expected_best_fitness": 1.0,
        "expected_best_code_marker": 'return f"Hello, {name}!"',
        "expected_behavior_marker": "reaches the correct greeting in generation 0",
        "show_command": "py -3.12 -m libreevolve show examples/runs/hello_world_ensemble",
    },
    "sorting_ttt_rl": {
        "readme_marker": "`sorting_ttt_rl/`: 56 records",
        "record_count": 56,
        "expected_best_fitness": 1.0,
        "expected_best_code_marker": "for i in range(len(lst)):",
        "expected_behavior_marker": "neutral drift and implementation diversity at constant fitness",
        "show_command": "py -3.12 -m libreevolve show examples/runs/sorting_ttt_rl",
    },
}
EXPECTED_MISSING_MODERN_ARTIFACTS = (
    "manifest.json",
    "archive_events.jsonl",
    "llm_calls.jsonl",
    "prompt_history.jsonl",
    "failure_history.jsonl",
    "best_workspace",
)
EXPECTED_README_MARKERS = (
    ("title", "# Example Runs"),
    ("curated_examples", "curated examples"),
    ("legacy_history_fixtures", "legacy history fixtures"),
    ("history_jsonl", "`history.jsonl`"),
    ("best_py", "`best.py`"),
    ("missing_manifest", "`manifest.json`"),
    ("missing_archive_events", "`archive_events.jsonl`"),
    ("missing_llm_calls", "`llm_calls.jsonl`"),
    ("missing_prompt_history", "`prompt_history.jsonl`"),
    ("missing_failure_history", "`failure_history.jsonl`"),
    ("missing_best_workspace", "`best_workspace/`"),
    ("kept_examples", "## Kept examples"),
    ("inspect_heading", "## How to inspect them"),
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("run_artifacts_doc_route", RUN_ARTIFACTS_DOC_PATH, "[`examples/runs/`](../examples/runs/README.md)"),
    ("run_artifacts_show_hello", RUN_ARTIFACTS_DOC_PATH, "py -3.12 -m libreevolve show examples/runs/hello_world_ensemble"),
    ("run_artifacts_show_sorting", RUN_ARTIFACTS_DOC_PATH, "py -3.12 -m libreevolve show examples/runs/sorting_ttt_rl"),
    ("run_artifacts_legacy_boundary", RUN_ARTIFACTS_DOC_PATH, "Those checked-in examples are legacy history fixtures."),
    ("run_artifacts_fallback", RUN_ARTIFACTS_DOC_PATH, "falls back to the highest top-level `fitness`"),
    ("cli_legacy_status", CLI_PATH, "legacy history-only (manifest.json missing)"),
    ("cli_test_legacy_status", CLI_TEST_PATH, "test_show_prints_best"),
    ("cli_test_legacy_highest", CLI_TEST_PATH, "legacy highest-fitness"),
    ("readme_todo_owner", README_TODO_PATH, "Add example-runs README fixture-claim drift evidence."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "example_runs_readme_markers",
    "fixture_history_row_counts",
    "fixture_best_program_markers",
    "legacy_artifact_presence",
    "modern_artifact_absence",
    "documented_show_commands",
    "cli_legacy_show_status_anchor",
    "run_artifacts_guide_anchor",
    "focused_cli_show_test_anchor",
    "active_todo_owner_anchor",
    "show_command_execution_transcript",
    "per_fixture_behavior_semantic_verifier",
    "current_run_artifact_parity_check",
    "alphaevolve_reproducibility_boundary",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "show_command_execution_transcript": "not_recorded_locally",
    "per_fixture_behavior_semantic_verifier": "not_recorded_locally",
    "current_run_artifact_parity_check": "not_recorded_locally",
    "alphaevolve_reproducibility_boundary": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeExampleRunsBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeExampleRunsBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readme_marker_count: int
    missing_readme_marker_count: int
    fixture_count: int
    fixture_drift_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    missing_evidence_count: int
    issues: list[ReadmeExampleRunsBoundaryIssue]


def readme_example_runs_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the examples/runs README structural fixture-claim evidence map."""

    root_path = Path(root)
    readme_text = _read_text(root_path / EXAMPLE_RUNS_README_PATH)
    texts = {
        path: _read_text(root_path / path)
        for path in (RUN_ARTIFACTS_DOC_PATH, CLI_PATH, CLI_TEST_PATH, README_TODO_PATH)
    }
    readme_marker_records = [
        _marker_record(record_id, EXAMPLE_RUNS_README_PATH, readme_text, marker)
        for record_id, marker in EXPECTED_README_MARKERS
    ]
    evidence_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_EVIDENCE_ANCHORS
    ]
    fixture_records = [
        _fixture_record(root_path, fixture_id, expected, readme_text)
        for fixture_id, expected in EXPECTED_FIXTURES.items()
    ]
    fixture_drift_records = [
        record for record in fixture_records if record["fixture_status"] != "fixture_claims_match"
    ]
    missing_readme_markers = [
        record for record in readme_marker_records if record["marker_status"] != "marker_present"
    ]
    missing_evidence_anchors = [
        record for record in evidence_anchor_records if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": README_EXAMPLE_RUNS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "example_runs_readme_path": EXAMPLE_RUNS_README_PATH,
        "fixture_ids": list(EXPECTED_FIXTURES),
        "source_paths": [EXAMPLE_RUNS_README_PATH, RUN_ARTIFACTS_DOC_PATH, CLI_PATH],
        "test_paths": [CLI_TEST_PATH],
        "todo_paths": [README_TODO_PATH],
        "readme_marker_count": len(readme_marker_records),
        "missing_readme_marker_count": len(missing_readme_markers),
        "missing_readme_marker_records": missing_readme_markers,
        "readme_marker_records": readme_marker_records,
        "fixture_count": len(fixture_records),
        "fixture_drift_count": len(fixture_drift_records),
        "fixture_drift_records": fixture_drift_records,
        "fixture_records": fixture_records,
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "example_runs_readme_map_status": (
            "example_runs_readme_structural_fixture_map_present"
            if not missing_readme_markers
            and not missing_evidence_anchors
            and not fixture_drift_records
            else "example_runs_readme_structural_fixture_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records examples/runs README markers, fixture "
            "history row counts, best-program markers, legacy artifact "
            "presence, modern artifact absence, documented show commands, CLI "
            "legacy-show anchors, run-artifacts guide anchors, focused CLI show "
            "test anchors, and active TODO ownership. It does not claim retained "
            "show-command execution transcripts, per-fixture behavior semantic "
            "verification, current run-artifact parity, AlphaEvolve-level "
            "reproducibility evidence, or owner review signoff."
        ),
    }


def validate_readme_example_runs_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeExampleRunsBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_example_runs_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeExampleRunsBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_example_runs_boundary_record(root)
    issues: list[ReadmeExampleRunsBoundaryIssue] = []
    if data.get("schema") != README_EXAMPLE_RUNS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README example-runs boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README example-runs boundary must not claim reproducibility proof"))
    for key in (
        "example_runs_readme_path",
        "fixture_ids",
        "source_paths",
        "test_paths",
        "todo_paths",
        "readme_marker_count",
        "missing_readme_marker_count",
        "missing_readme_marker_records",
        "readme_marker_records",
        "fixture_count",
        "fixture_drift_count",
        "fixture_drift_records",
        "fixture_records",
        "evidence_anchor_count",
        "missing_evidence_anchor_count",
        "missing_evidence_anchor_records",
        "evidence_anchor_records",
        "example_runs_readme_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current example-runs inputs"))
    if data.get("missing_readme_marker_count") != 0:
        issues.append(_issue("missing_example_runs_readme_marker", "examples/runs README markers are incomplete"))
    if data.get("fixture_drift_count") != 0:
        issues.append(_issue("example_runs_fixture_drift", "checked-in example-run fixtures drifted from README claims"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_example_runs_evidence_anchor", "example-runs evidence anchors are incomplete"))
    if data.get("example_runs_readme_map_status") != "example_runs_readme_structural_fixture_map_present":
        issues.append(_issue("invalid_example_runs_readme_map_status", "example-runs structural fixture map must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "fixture history row counts" not in boundary_text
        or "does not claim retained show-command execution transcripts" not in boundary_text
        or "AlphaEvolve-level reproducibility evidence" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate fixture evidence from reproducibility proof"))
    return ReadmeExampleRunsBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readme_marker_count=data.get("readme_marker_count") if isinstance(data.get("readme_marker_count"), int) else 0,
        missing_readme_marker_count=data.get("missing_readme_marker_count") if isinstance(data.get("missing_readme_marker_count"), int) else 0,
        fixture_count=data.get("fixture_count") if isinstance(data.get("fixture_count"), int) else 0,
        fixture_drift_count=data.get("fixture_drift_count") if isinstance(data.get("fixture_drift_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_example_runs_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_example_runs_boundary(boundary)
    lines = [
        "README example-runs boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| readme_marker_count | {validation.readme_marker_count} |",
        f"| missing_readme_marker_count | {validation.missing_readme_marker_count} |",
        f"| fixture_count | {validation.fixture_count} |",
        f"| fixture_drift_count | {validation.fixture_drift_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_evidence_anchor_count | {validation.missing_evidence_anchor_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _fixture_record(root: Path, fixture_id: str, expected: dict[str, Any], readme_text: str) -> dict[str, Any]:
    fixture_path = Path("examples/runs") / fixture_id
    history_path = fixture_path / "history.jsonl"
    best_path = fixture_path / "best.py"
    rows = _read_jsonl(root / history_path)
    best_code = _read_text(root / best_path)
    best_row = _best_row(rows)
    present_artifacts = sorted(
        item.name
        for item in (root / fixture_path).iterdir()
        if (root / fixture_path).exists()
    )
    missing_modern = [
        name
        for name in EXPECTED_MISSING_MODERN_ARTIFACTS
        if not (root / fixture_path / name).exists()
    ]
    status_checks = {
        "readme_marker_present": expected["readme_marker"] in readme_text,
        "behavior_marker_present": expected["expected_behavior_marker"] in readme_text,
        "show_command_present": expected["show_command"] in readme_text,
        "record_count_matches": len(rows) == expected["record_count"],
        "best_fitness_matches": (
            best_row is not None
            and best_row.get("fitness") == expected["expected_best_fitness"]
        ),
        "best_code_marker_present": expected["expected_best_code_marker"] in best_code,
        "legacy_artifacts_present": set(present_artifacts) == {"best.py", "history.jsonl"},
        "modern_artifacts_absent": missing_modern == list(EXPECTED_MISSING_MODERN_ARTIFACTS),
    }
    return {
        "fixture_id": fixture_id,
        "path": fixture_path.as_posix(),
        "history_path": history_path.as_posix(),
        "best_path": best_path.as_posix(),
        "expected_record_count": expected["record_count"],
        "actual_record_count": len(rows),
        "expected_best_fitness": expected["expected_best_fitness"],
        "actual_best_fitness": best_row.get("fitness") if best_row else None,
        "actual_best_generation": best_row.get("generation") if best_row else None,
        "best_code_marker": expected["expected_best_code_marker"],
        "present_artifacts": present_artifacts,
        "expected_missing_modern_artifacts": list(EXPECTED_MISSING_MODERN_ARTIFACTS),
        "actual_missing_modern_artifacts": missing_modern,
        "show_command": expected["show_command"],
        "status_checks": status_checks,
        "fixture_status": (
            "fixture_claims_match"
            if all(status_checks.values())
            else "fixture_claims_drifted"
        ),
    }


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            value = json.loads(line)
            if isinstance(value, dict):
                rows.append(value)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError):
        return []
    return rows


def _best_row(rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    numeric = [
        row
        for row in rows
        if isinstance(row.get("fitness"), (int, float))
        and not isinstance(row.get("fitness"), bool)
    ]
    if not numeric:
        return None
    return max(numeric, key=lambda row: row["fitness"])


def _marker_record(record_id: str, path: str, text: str, marker: str) -> dict[str, Any]:
    return {
        "record_id": record_id,
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
) -> tuple[dict[str, Any] | None, list[ReadmeExampleRunsBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README example-runs boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeExampleRunsBoundaryIssue],
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
    issues: list[ReadmeExampleRunsBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeExampleRunsBoundaryIssue:
    return ReadmeExampleRunsBoundaryIssue(code, message)
