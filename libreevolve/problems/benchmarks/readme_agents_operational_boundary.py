from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_AGENTS_OPERATIONAL_BOUNDARY_SCHEMA = (
    "libreevolve.readme_agents_operational_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "agents_operational_static_drift_record_without_complete_instruction_map"
)
AGENTS_PATH = "AGENTS.md"
README_PATH = "README.md"
RUN_ARTIFACTS_DOC_PATH = "docs/run-artifacts.md"
BACKENDS_DOC_PATH = "docs/backends.md"
CONFIGURATION_DOC_PATH = "docs/configuration.md"
PAPERS_README_PATH = "papers/README.md"
EXAMPLES_DIR = "libreevolve/problems/examples"
ARTIFACT_SCHEMA_PATH = "libreevolve/core/artifact_schema.py"
AGENTS_TEST_PATH = "tests/test_agents_docs.py"
WORKFLOW_PATH = ".github/workflows/tests.yml"
README_TODO_PATH = "docs/todo/readme.md"

EXPECTED_RUN_ARTIFACT_MARKERS = (
    ("manifest.json", "manifest.json"),
    ("history.jsonl", "history.jsonl"),
    ("failure_history.jsonl", "failure/quarantine JSONL streams"),
    ("archive_events.jsonl", "archive_events.jsonl"),
    ("controller_budget_events.jsonl", "controller_budget_events.jsonl"),
    ("evaluator_results.jsonl", "evaluator_results.jsonl"),
    ("llm_calls.jsonl", "llm_calls.jsonl"),
    ("prompt_current_binding_table.jsonl", "prompt_current_binding_table.jsonl"),
    ("prompt_history.jsonl", "prompt_history.jsonl"),
    ("prompt_prior_score_table.jsonl", "prompt_prior_score_table.jsonl"),
    ("task_specification.json", "task_specification.json"),
    ("best.py", "best.py"),
    ("best_workspace/", "best_workspace/"),
    ("evaluator_artifacts/", "evaluator_artifacts/"),
    ("plugin_artifacts/", "plugin_artifacts/"),
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("readme_agents_route", README_PATH, "[AGENTS.md](AGENTS.md)"),
    ("readme_agent_operating_contract", README_PATH, "agent-facing operating contract"),
    ("run_artifacts_doc_task_spec", RUN_ARTIFACTS_DOC_PATH, "task_specification.json"),
    ("run_artifacts_doc_controller_budget", RUN_ARTIFACTS_DOC_PATH, "controller_budget_events.jsonl"),
    ("artifact_schema_run_artifact_names", ARTIFACT_SCHEMA_PATH, "RUN_ARTIFACT_NAMES = frozenset("),
    ("backend_docs_route", BACKENDS_DOC_PATH, "# Backends"),
    ("configuration_sampling_strategy", CONFIGURATION_DOC_PATH, "parent_selection_strategy"),
    ("papers_index_route", PAPERS_README_PATH, "# Local Paper Cache"),
    ("agents_docs_tests", AGENTS_TEST_PATH, "test_agents_instructions"),
    ("agents_workflow_path_filter", WORKFLOW_PATH, '"AGENTS.md"'),
    ("readme_todo_owner", README_TODO_PATH, "Add AGENTS.md operational-instruction drift evidence."),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "agents_architecture_example_inventory",
    "actual_example_directory_inventory",
    "example_directory_drift_records",
    "agents_run_artifact_inventory",
    "run_artifact_drift_records",
    "agents_test_command_markers",
    "agents_backend_guidance_markers",
    "agents_threshold_and_sampling_markers",
    "agents_docs_test_anchors",
    "github_actions_agents_path_filter",
    "active_todo_owner_anchor",
    "complete_instruction_to_source_map",
    "dependency_list_semantic_check",
    "provider_guidance_semantic_check",
    "alphaevolve_scope_semantic_check",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "complete_instruction_to_source_map": "not_recorded_locally",
    "dependency_list_semantic_check": "not_recorded_locally",
    "provider_guidance_semantic_check": "not_recorded_locally",
    "alphaevolve_scope_semantic_check": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeAgentsOperationalBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeAgentsOperationalBoundaryValidation:
    ok: bool
    boundary_status: str | None
    actual_example_count: int
    listed_example_count: int
    missing_example_count: int
    run_artifact_record_count: int
    missing_run_artifact_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    missing_evidence_count: int
    issues: list[ReadmeAgentsOperationalBoundaryIssue]


def readme_agents_operational_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the AGENTS.md operational-instruction drift record."""

    root_path = Path(root)
    agents_text = _read_text(root_path / AGENTS_PATH)
    actual_examples = _actual_examples(root_path / EXAMPLES_DIR)
    listed_examples = _listed_examples(agents_text)
    missing_examples = [
        name for name in actual_examples if name not in set(listed_examples)
    ]
    stale_examples = [
        name for name in listed_examples if name not in set(actual_examples)
    ]
    run_artifact_records = [
        {
            "artifact_name": artifact_name,
            "expected_marker": marker,
            "marker_status": "marker_present" if marker in agents_text else "marker_missing",
        }
        for artifact_name, marker in EXPECTED_RUN_ARTIFACT_MARKERS
    ]
    missing_run_artifact_records = [
        record
        for record in run_artifact_records
        if record["marker_status"] != "marker_present"
    ]
    texts = {
        path: _read_text(root_path / path)
        for path in (
            README_PATH,
            RUN_ARTIFACTS_DOC_PATH,
            BACKENDS_DOC_PATH,
            CONFIGURATION_DOC_PATH,
            PAPERS_README_PATH,
            ARTIFACT_SCHEMA_PATH,
            AGENTS_TEST_PATH,
            WORKFLOW_PATH,
            README_TODO_PATH,
        )
    }
    evidence_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_EVIDENCE_ANCHORS
    ]
    missing_evidence_anchors = [
        record for record in evidence_anchor_records if record["marker_status"] != "marker_present"
    ]
    drift_present = bool(missing_examples or stale_examples or missing_run_artifact_records)
    return {
        "schema": README_AGENTS_OPERATIONAL_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "agents_path": AGENTS_PATH,
        "examples_dir": EXAMPLES_DIR,
        "run_artifacts_doc_path": RUN_ARTIFACTS_DOC_PATH,
        "readme_path": README_PATH,
        "docs_paths": [BACKENDS_DOC_PATH, CONFIGURATION_DOC_PATH],
        "paper_index_path": PAPERS_README_PATH,
        "test_paths": [AGENTS_TEST_PATH],
        "workflow_path": WORKFLOW_PATH,
        "todo_paths": [README_TODO_PATH],
        "actual_example_count": len(actual_examples),
        "actual_examples": actual_examples,
        "listed_example_count": len(listed_examples),
        "listed_examples": listed_examples,
        "missing_example_count": len(missing_examples),
        "missing_examples": missing_examples,
        "stale_example_count": len(stale_examples),
        "stale_examples": stale_examples,
        "run_artifact_record_count": len(run_artifact_records),
        "missing_run_artifact_count": len(missing_run_artifact_records),
        "missing_run_artifact_records": missing_run_artifact_records,
        "run_artifact_records": run_artifact_records,
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "agents_operational_drift_status": (
            "agents_operational_drift_recorded"
            if drift_present and not missing_evidence_anchors
            else "agents_operational_drift_record_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records AGENTS.md operational-instruction drift for "
            "example problem directories and run-artifact names, plus README "
            "routing, run-artifact guide anchors, backend/configuration/paper "
            "doc anchors, tests/test_agents_docs.py anchors, GitHub Actions "
            "AGENTS.md path-filter coverage, and active TODO ownership. It "
            "does not claim a complete instruction-to-source map, dependency "
            "list semantic check, provider guidance semantic check, full "
            "AlphaEvolve-scope semantic check, or owner review signoff."
        ),
    }


def validate_readme_agents_operational_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeAgentsOperationalBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_agents_operational_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeAgentsOperationalBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_agents_operational_boundary_record(root)
    issues: list[ReadmeAgentsOperationalBoundaryIssue] = []
    if data.get("schema") != README_AGENTS_OPERATIONAL_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README AGENTS operational boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "AGENTS operational boundary must not claim complete instruction drift proof"))
    for key in (
        "agents_path",
        "examples_dir",
        "run_artifacts_doc_path",
        "readme_path",
        "docs_paths",
        "paper_index_path",
        "test_paths",
        "workflow_path",
        "todo_paths",
        "actual_example_count",
        "actual_examples",
        "listed_example_count",
        "listed_examples",
        "missing_example_count",
        "missing_examples",
        "stale_example_count",
        "stale_examples",
        "run_artifact_record_count",
        "missing_run_artifact_count",
        "missing_run_artifact_records",
        "run_artifact_records",
        "evidence_anchor_count",
        "missing_evidence_anchor_count",
        "missing_evidence_anchor_records",
        "evidence_anchor_records",
        "agents_operational_drift_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current AGENTS operational inputs"))
    if data.get("missing_example_count") != 3:
        issues.append(_issue("invalid_missing_example_count", "current AGENTS.md example drift should record three missing example directories"))
    if data.get("missing_run_artifact_count") != 5:
        issues.append(_issue("invalid_missing_run_artifact_count", "current AGENTS.md run-artifact drift should record five missing artifacts"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_agents_operational_evidence_anchor", "AGENTS operational evidence anchors are incomplete"))
    if data.get("agents_operational_drift_status") != "agents_operational_drift_recorded":
        issues.append(_issue("invalid_agents_operational_drift_status", "AGENTS operational drift record must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "AGENTS.md operational-instruction drift" not in boundary_text
        or "example problem directories and run-artifact names" not in boundary_text
        or "does not claim a complete instruction-to-source map" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate AGENTS drift inventory from complete instruction proof"))
    return ReadmeAgentsOperationalBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        actual_example_count=data.get("actual_example_count") if isinstance(data.get("actual_example_count"), int) else 0,
        listed_example_count=data.get("listed_example_count") if isinstance(data.get("listed_example_count"), int) else 0,
        missing_example_count=data.get("missing_example_count") if isinstance(data.get("missing_example_count"), int) else 0,
        run_artifact_record_count=data.get("run_artifact_record_count") if isinstance(data.get("run_artifact_record_count"), int) else 0,
        missing_run_artifact_count=data.get("missing_run_artifact_count") if isinstance(data.get("missing_run_artifact_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_agents_operational_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_agents_operational_boundary(boundary)
    lines = [
        "README AGENTS operational boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| actual_example_count | {validation.actual_example_count} |",
        f"| listed_example_count | {validation.listed_example_count} |",
        f"| missing_example_count | {validation.missing_example_count} |",
        f"| run_artifact_record_count | {validation.run_artifact_record_count} |",
        f"| missing_run_artifact_count | {validation.missing_run_artifact_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_evidence_anchor_count | {validation.missing_evidence_anchor_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _actual_examples(path: Path) -> list[str]:
    try:
        return sorted(
            child.name
            for child in path.iterdir()
            if child.is_dir() and child.name != "__pycache__"
        )
    except OSError:
        return []


def _listed_examples(agents_text: str) -> list[str]:
    match = re.search(r"examples/\{([^}]+)\}/", agents_text)
    if match is None:
        return []
    return [item.strip() for item in match.group(1).split(",") if item.strip()]


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
) -> tuple[dict[str, Any] | None, list[ReadmeAgentsOperationalBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README AGENTS operational boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeAgentsOperationalBoundaryIssue],
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
    issues: list[ReadmeAgentsOperationalBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeAgentsOperationalBoundaryIssue:
    return ReadmeAgentsOperationalBoundaryIssue(code, message)
