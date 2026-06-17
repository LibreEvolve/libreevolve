from __future__ import annotations

import ast
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_RUN_ARTIFACTS_BOUNDARY_SCHEMA = "libreevolve.readme_run_artifacts_boundary.v1"
EXPECTED_BOUNDARY_STATUS = (
    "readme_run_artifacts_structural_list_without_lifecycle_parity"
)
README_PATH = "README.md"
README_TODO_PATH = "docs/todo/readme.md"
RUN_ARTIFACTS_DOC_PATH = "docs/run-artifacts.md"
ARTIFACT_SCHEMA_PATH = "libreevolve/core/artifact_schema.py"
DATABASE_PATH = "libreevolve/core/database.py"
DATABASE_TEST_PATH = "tests/population/test_database.py"
CLI_TEST_PATH = "tests/test_cli.py"
QUICK_START_TEST_PATH = "tests/test_readme_quick_start_smoke_boundary.py"
DOCUMENTATION_CLAIM_INVENTORY_PATH = "papers/documentation_claim_inventory.json"
TASK_SPEC_BOUNDARY_PATH = "papers/task_specification_boundary.json"

EXPECTED_README_COMMON_ARTIFACTS = (
    "manifest.json",
    "archive_events.jsonl",
    "controller_budget_events.jsonl",
    "evaluator_results.jsonl",
    "failure_history.jsonl",
    "history.jsonl",
    "llm_calls.jsonl",
    "prompt_current_binding_table.jsonl",
    "prompt_history.jsonl",
    "prompt_prior_score_table.jsonl",
    "best.py",
    "best_workspace",
    "evaluator_artifacts",
    "plugin_artifacts",
)
EXPECTED_SCOPE_OMISSIONS = (
    "task_specification.json",
    "history_invalid.jsonl",
    "failure_history_invalid.jsonl",
    "archive_events_invalid.jsonl",
    "controller_budget_events_invalid.jsonl",
    "llm_calls_invalid.jsonl",
    "manifest_invalid.jsonl",
    "prompt_history_invalid.jsonl",
    "paper_artifacts",
)
EXPECTED_README_MARKERS = (
    ("heading", "## Run Artifacts"),
    ("run_path", "Runs write to `runs/<run-name>/`, which is gitignored."),
    ("common_outputs_intro", "Common outputs include:"),
    ("run_artifacts_route", "[docs/run-artifacts.md](docs/run-artifacts.md)"),
    ("quarantine_streams_route", "quarantine\nstreams"),
    ("restore_behavior_route", "restore behavior"),
    ("inspection_details_route", "inspection details"),
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("run_artifacts_doc_title", RUN_ARTIFACTS_DOC_PATH, "# Run Artifacts"),
    ("run_artifacts_task_spec", RUN_ARTIFACTS_DOC_PATH, "task_specification.json"),
    ("run_artifacts_invalid_streams", RUN_ARTIFACTS_DOC_PATH, "history_invalid.jsonl"),
    ("run_artifacts_paper_artifacts", RUN_ARTIFACTS_DOC_PATH, "paper_artifacts/"),
    ("run_artifacts_collision_policy", RUN_ARTIFACTS_DOC_PATH, "Reusing an existing run directory"),
    ("run_artifacts_overwrite_known", RUN_ARTIFACTS_DOC_PATH, "delete only those known artifacts"),
    ("artifact_schema_run_artifact_names", ARTIFACT_SCHEMA_PATH, "RUN_ARTIFACT_NAMES = frozenset("),
    ("database_prepare_run_directory", DATABASE_PATH, "def prepare_run_directory"),
    ("artifact_schema_task_spec_path", ARTIFACT_SCHEMA_PATH, "task_specification.json"),
    ("artifact_schema_prompt_table_artifacts", ARTIFACT_SCHEMA_PATH, "prompt_current_binding_table.jsonl"),
    ("artifact_schema_paper_artifacts", ARTIFACT_SCHEMA_PATH, "paper_artifacts"),
    ("cli_overwrite_test", CLI_TEST_PATH, "test_run_overwrite_clears_target_artifacts"),
    ("database_prompt_table_overwrite_test", DATABASE_TEST_PATH, "prompt_current_binding_table.jsonl"),
    ("database_paper_artifacts_overwrite_test", DATABASE_TEST_PATH, "paper_artifacts"),
    ("quick_start_smoke_test", QUICK_START_TEST_PATH, "test_readme_quick_start_smoke_executes_documented_no_provider_path"),
    ("documentation_claim_inventory", DOCUMENTATION_CLAIM_INVENTORY_PATH, "run_artifact_documented_count"),
    ("task_spec_boundary", TASK_SPEC_BOUNDARY_PATH, "task_specification_json_artifact_recorded"),
    ("readme_todo_owner", README_TODO_PATH, "Add README run-artifact list drift and scope evidence."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_run_artifact_markers",
    "readme_common_output_records",
    "run_artifacts_guide_anchor_records",
    "run_artifact_cleanup_set_records",
    "readme_vs_cleanup_alignment",
    "documented_scope_omission_records",
    "task_specification_scope_anchor",
    "invalid_quarantine_stream_scope_anchor",
    "paper_artifacts_scope_anchor",
    "overwrite_cleanup_test_anchor",
    "prompt_table_cleanup_test_anchor",
    "paper_artifacts_cleanup_test_anchor",
    "quick_start_smoke_artifact_anchor",
    "active_todo_owner_anchor",
    "fresh_smoke_run_artifact_presence_matrix",
    "artifact_writer_reader_schema_map",
    "restore_and_show_lifecycle_proof",
    "optional_artifact_classification_gate",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "fresh_smoke_run_artifact_presence_matrix": "not_recorded_locally",
    "artifact_writer_reader_schema_map": "not_recorded_locally",
    "restore_and_show_lifecycle_proof": "not_recorded_locally",
    "optional_artifact_classification_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeRunArtifactsBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeRunArtifactsBoundaryValidation:
    ok: bool
    boundary_status: str | None
    readme_marker_count: int
    missing_readme_marker_count: int
    common_artifact_count: int
    missing_common_artifact_count: int
    cleanup_artifact_count: int
    scoped_omission_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    missing_evidence_count: int
    issues: list[ReadmeRunArtifactsBoundaryIssue]


def readme_run_artifacts_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the README run-artifacts structural list evidence map."""

    root_path = Path(root)
    readme_text = _read_text(root_path / README_PATH)
    docs_text = _read_text(root_path / RUN_ARTIFACTS_DOC_PATH)
    texts = {
        path: _read_text(root_path / path)
        for path in (
            RUN_ARTIFACTS_DOC_PATH,
            ARTIFACT_SCHEMA_PATH,
            DATABASE_PATH,
            DATABASE_TEST_PATH,
            CLI_TEST_PATH,
            QUICK_START_TEST_PATH,
            DOCUMENTATION_CLAIM_INVENTORY_PATH,
            TASK_SPEC_BOUNDARY_PATH,
            README_TODO_PATH,
        )
    }
    readme_marker_records = [
        _marker_record(record_id, README_PATH, readme_text, marker)
        for record_id, marker in EXPECTED_README_MARKERS
    ]
    common_artifact_records = [
        _artifact_record(name, readme_text, docs_text)
        for name in EXPECTED_README_COMMON_ARTIFACTS
    ]
    cleanup_names = _cleanup_artifact_names(root_path / ARTIFACT_SCHEMA_PATH)
    cleanup_records = [
        {
            "name": name,
            "present_in_readme_common_list": name in EXPECTED_README_COMMON_ARTIFACTS,
            "present_in_run_artifacts_doc": name in docs_text,
        }
        for name in cleanup_names
    ]
    scope_omission_records = [
        {
            "name": name,
            "present_in_readme_common_list": name in EXPECTED_README_COMMON_ARTIFACTS,
            "present_in_run_artifacts_doc": name in docs_text,
            "present_in_cleanup_set": name in cleanup_names,
            "scope_status": (
                "documented_outside_readme_common_list"
                if name not in EXPECTED_README_COMMON_ARTIFACTS and name in docs_text
                else "scope_omission_anchor_missing"
            ),
        }
        for name in EXPECTED_SCOPE_OMISSIONS
    ]
    evidence_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_EVIDENCE_ANCHORS
    ]
    missing_readme_markers = [
        record for record in readme_marker_records if record["marker_status"] != "marker_present"
    ]
    missing_common_artifacts = [
        record for record in common_artifact_records if record["readme_status"] != "listed_in_readme"
    ]
    missing_evidence_anchors = [
        record for record in evidence_anchor_records if record["marker_status"] != "marker_present"
    ]
    scope_omission_drift = [
        record for record in scope_omission_records if record["scope_status"] != "documented_outside_readme_common_list"
    ]
    return {
        "schema": README_RUN_ARTIFACTS_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "run_artifacts_doc_path": RUN_ARTIFACTS_DOC_PATH,
        "cleanup_source_path": ARTIFACT_SCHEMA_PATH,
        "test_paths": [CLI_TEST_PATH, QUICK_START_TEST_PATH],
        "sidecar_paths": [DOCUMENTATION_CLAIM_INVENTORY_PATH, TASK_SPEC_BOUNDARY_PATH],
        "todo_paths": [README_TODO_PATH],
        "readme_marker_count": len(readme_marker_records),
        "missing_readme_marker_count": len(missing_readme_markers),
        "missing_readme_marker_records": missing_readme_markers,
        "readme_marker_records": readme_marker_records,
        "common_artifact_count": len(common_artifact_records),
        "missing_common_artifact_count": len(missing_common_artifacts),
        "missing_common_artifact_records": missing_common_artifacts,
        "common_artifact_records": common_artifact_records,
        "cleanup_artifact_count": len(cleanup_records),
        "cleanup_artifact_names": cleanup_names,
        "cleanup_artifact_records": cleanup_records,
        "readme_common_without_cleanup_names": sorted(
            set(EXPECTED_README_COMMON_ARTIFACTS) - set(cleanup_names)
        ),
        "cleanup_without_readme_common_names": sorted(
            set(cleanup_names) - set(EXPECTED_README_COMMON_ARTIFACTS)
        ),
        "scoped_omission_count": len(scope_omission_records),
        "scope_omission_drift_count": len(scope_omission_drift),
        "scope_omission_drift_records": scope_omission_drift,
        "scope_omission_records": scope_omission_records,
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "readme_run_artifacts_map_status": (
            "readme_run_artifacts_structural_list_map_present"
            if not missing_readme_markers
            and not missing_common_artifacts
            and not missing_evidence_anchors
            and not scope_omission_drift
            else "readme_run_artifacts_structural_list_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README Run Artifacts markers, the 14 "
            "README common output records, run-artifacts guide anchors, the "
            "RUN_ARTIFACT_NAMES cleanup set, README-vs-cleanup mismatch lists, "
            "documented scope omissions for task_specification.json, invalid/"
            "quarantine streams, and paper_artifacts, overwrite cleanup test "
            "anchors, quick-start smoke artifact anchors, sidecar anchors, and "
            "active TODO ownership. It does not claim a fresh smoke-run artifact "
            "presence matrix, complete artifact writer/reader/schema mapping, "
            "restore/show lifecycle proof, optional artifact classification "
            "gating, or owner review signoff."
        ),
    }


def validate_readme_run_artifacts_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeRunArtifactsBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_run_artifacts_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeRunArtifactsBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_run_artifacts_boundary_record(root)
    issues: list[ReadmeRunArtifactsBoundaryIssue] = []
    if data.get("schema") != README_RUN_ARTIFACTS_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README run-artifacts boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README run-artifacts boundary must not claim lifecycle parity"))
    for key in (
        "readme_path",
        "run_artifacts_doc_path",
        "cleanup_source_path",
        "test_paths",
        "sidecar_paths",
        "todo_paths",
        "readme_marker_count",
        "missing_readme_marker_count",
        "missing_readme_marker_records",
        "readme_marker_records",
        "common_artifact_count",
        "missing_common_artifact_count",
        "missing_common_artifact_records",
        "common_artifact_records",
        "cleanup_artifact_count",
        "cleanup_artifact_names",
        "cleanup_artifact_records",
        "readme_common_without_cleanup_names",
        "cleanup_without_readme_common_names",
        "scoped_omission_count",
        "scope_omission_drift_count",
        "scope_omission_drift_records",
        "scope_omission_records",
        "evidence_anchor_count",
        "missing_evidence_anchor_count",
        "missing_evidence_anchor_records",
        "evidence_anchor_records",
        "readme_run_artifacts_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current README run-artifacts inputs"))
    if data.get("missing_readme_marker_count") != 0:
        issues.append(_issue("missing_readme_run_artifacts_marker", "README run-artifacts markers are incomplete"))
    if data.get("missing_common_artifact_count") != 0:
        issues.append(_issue("missing_readme_common_artifact", "README common artifact list is incomplete"))
    if data.get("scope_omission_drift_count") != 0:
        issues.append(_issue("invalid_scope_omission_records", "README-scoped omissions must remain documented in the detailed guide"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_readme_run_artifacts_evidence_anchor", "README run-artifacts evidence anchors are incomplete"))
    if data.get("readme_run_artifacts_map_status") != "readme_run_artifacts_structural_list_map_present":
        issues.append(_issue("invalid_readme_run_artifacts_map_status", "README run-artifacts structural list map must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "14 README common output records" not in boundary_text
        or "does not claim a fresh smoke-run artifact presence matrix" not in boundary_text
        or "restore/show lifecycle proof" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate structural artifact-list evidence from lifecycle proof"))
    return ReadmeRunArtifactsBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        readme_marker_count=data.get("readme_marker_count") if isinstance(data.get("readme_marker_count"), int) else 0,
        missing_readme_marker_count=data.get("missing_readme_marker_count") if isinstance(data.get("missing_readme_marker_count"), int) else 0,
        common_artifact_count=data.get("common_artifact_count") if isinstance(data.get("common_artifact_count"), int) else 0,
        missing_common_artifact_count=data.get("missing_common_artifact_count") if isinstance(data.get("missing_common_artifact_count"), int) else 0,
        cleanup_artifact_count=data.get("cleanup_artifact_count") if isinstance(data.get("cleanup_artifact_count"), int) else 0,
        scoped_omission_count=data.get("scoped_omission_count") if isinstance(data.get("scoped_omission_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_run_artifacts_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_run_artifacts_boundary(boundary)
    lines = [
        "README run-artifacts boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| readme_marker_count | {validation.readme_marker_count} |",
        f"| missing_readme_marker_count | {validation.missing_readme_marker_count} |",
        f"| common_artifact_count | {validation.common_artifact_count} |",
        f"| missing_common_artifact_count | {validation.missing_common_artifact_count} |",
        f"| cleanup_artifact_count | {validation.cleanup_artifact_count} |",
        f"| scoped_omission_count | {validation.scoped_omission_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_evidence_anchor_count | {validation.missing_evidence_anchor_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _artifact_record(name: str, readme_text: str, docs_text: str) -> dict[str, Any]:
    readme_marker = f"`{name}/`" if "." not in name else f"`{name}`"
    return {
        "name": name,
        "readme_marker": readme_marker,
        "readme_status": "listed_in_readme" if readme_marker in readme_text else "missing_from_readme",
        "present_in_run_artifacts_doc": name in docs_text,
        "entry_kind": "directory" if "." not in name else "file",
    }


def _cleanup_artifact_names(path: Path) -> list[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "RUN_ARTIFACT_NAMES"
            for target in node.targets
        ):
            continue
        try:
            value_node = node.value
            if (
                isinstance(value_node, ast.Call)
                and isinstance(value_node.func, ast.Name)
                and value_node.func.id == "frozenset"
                and len(value_node.args) == 1
            ):
                value_node = value_node.args[0]
            value = ast.literal_eval(value_node)
        except (TypeError, ValueError):
            return []
        if isinstance(value, (frozenset, set)):
            return sorted(name for name in value if isinstance(name, str))
    return []


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
) -> tuple[dict[str, Any] | None, list[ReadmeRunArtifactsBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README run-artifacts boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeRunArtifactsBoundaryIssue],
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
    issues: list[ReadmeRunArtifactsBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeRunArtifactsBoundaryIssue:
    return ReadmeRunArtifactsBoundaryIssue(code, message)
