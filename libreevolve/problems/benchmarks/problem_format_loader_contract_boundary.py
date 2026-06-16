from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PROBLEM_FORMAT_LOADER_CONTRACT_BOUNDARY_SCHEMA = (
    "libreevolve.problem_format_loader_contract_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "problem_format_structural_map_without_semantic_loader_contract_proof"
)
PROBLEM_FORMAT_PATH = "docs/problem-format.md"
README_TODO_PATH = "docs/todo/readme.md"
CODE_TODO_PATH = "docs/todo/code.md"
PAPERS_TODO_PATH = "docs/todo/papers.md"
LOADER_PATH = "libreevolve/problems/loader.py"
CONFIG_PATH = "libreevolve/core/config.py"
EVALUATOR_PATH = "libreevolve/core/evaluator.py"
TEST_LOADER_PATH = "tests/core/test_loader.py"
TEST_EVALUATOR_PATH = "tests/core/test_evaluator.py"
TEST_EXAMPLES_PATH = "tests/test_examples.py"
WORKSPACE_MATH_PATH = "libreevolve/problems/examples/workspace_math"
EMBEDDED_EVALUATE_PATH = "libreevolve/problems/examples/embedded_evaluate_math"
README_PROBLEM_LAYOUT_PATH = "papers/readme_problem_layout_boundary.json"
VALIDATOR_EXECUTION_PATH = "papers/validator_execution_boundary.json"
EMBEDDED_EVALUATOR_PATH = "papers/embedded_evaluator_boundary.json"
WORKSPACE_MATERIALIZATION_PATH = "papers/workspace_materialization_boundary.json"
CANDIDATE_LANGUAGE_RUNNER_PATH = "papers/candidate_language_runner_boundary.json"
BENCHMARK_FIXTURE_READINESS_PATH = "papers/benchmark_fixture_readiness_boundary.json"
PROBLEM_FORMULATION_PATH = "papers/problem_formulation_provenance_boundary.json"

EXPECTED_GUIDE_MARKERS = (
    ("title", "# Problem Format"),
    ("loader_route", "[`libreevolve/problems/loader.py`](../libreevolve/problems/loader.py)"),
    ("required_layout", "## Required layout"),
    ("context_manifest_tree", "Optional context files can be placed in:"),
    ("codebase_integration_section", "## `codebase_integration.yaml`"),
    ("task_description_section", "## `task_description.txt`"),
    ("metrics_section", "## `metrics.yaml`"),
    ("validate_section", "## `validate.py`"),
    ("candidate_runner_section", "## Candidate Runner Declarations"),
    ("evaluation_semantics_section", "## Evaluation semantics"),
    ("initial_programs_section", "## `initial_programs`"),
    ("multi_file_seeds", "### Multi-file seeds"),
    ("mutation_modes_section", "## Mutation modes"),
    ("design_guidance_section", "## Design guidance"),
    ("context_manifest_keys", "Context manifests accept\nonly `include`, `exclude`"),
    ("codebase_manifest_exclusivity", "Use either `codebase_integration.yaml` or `codebase_integration.yml`, not both."),
    ("validator_signatures", "`validate.py` must expose either the legacy one-argument signature"),
    ("configured_eval_stages", "Problem `config.yaml` stages accept\nonly the documented `eval_stages` keys"),
    ("candidate_runner_declarations", "`config.yaml` can declare future candidate-language and build-system runner"),
    ("evaluation_validity_gate", "The evaluator treats `is_valid` as a required boolean validity gate"),
    ("seed_policy", "add `initial_programs/seed_policy.yaml`"),
    ("unsupported_runner_scope", "These records are manifest metadata only."),
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("loader_problem_dataclass", LOADER_PATH, "class Problem:"),
    ("loader_load_problem", LOADER_PATH, "def load_problem(problem_dir: str | Path) -> Problem:"),
    ("loader_task_file", LOADER_PATH, "task_path = d / \"task_description.txt\""),
    ("loader_metrics_file", LOADER_PATH, "metrics_path = d / \"metrics.yaml\""),
    ("loader_validate_file", LOADER_PATH, "validate_path = d / \"validate.py\""),
    ("loader_seed_dir", LOADER_PATH, "seed_dir = d / \"initial_programs\""),
    ("loader_context_manifest_names", LOADER_PATH, "_CONTEXT_MANIFEST_NAMES = (\"context.yaml\", \"context.yml\")"),
    ("loader_seed_policy_names", LOADER_PATH, "_SEED_POLICY_MANIFEST_NAMES = (\"seed_policy.yaml\", \"seed_policy.yml\")"),
    ("loader_codebase_integration_names", LOADER_PATH, "_CODEBASE_INTEGRATION_METADATA_NAMES"),
    ("loader_context_files", LOADER_PATH, "def _load_context_files"),
    ("loader_initial_workspaces", LOADER_PATH, "def _load_initial_workspaces"),
    ("loader_seed_policy", LOADER_PATH, "def _load_seed_workspace_policy"),
    ("loader_metric_schema", LOADER_PATH, "def _normalize_metric_schema"),
    ("loader_config_embedded_only", LOADER_PATH, "def _problem_config_declares_embedded_only_evaluation"),
    ("config_eval_stages", CONFIG_PATH, "eval_stages:            list[dict] = field(default_factory=list)"),
    ("config_candidate_language_runners", CONFIG_PATH, "candidate_language_runners: list[dict] = field(default_factory=list)"),
    ("config_candidate_build_systems", CONFIG_PATH, "candidate_build_systems: list[dict] = field(default_factory=list)"),
    ("config_eval_stage_validation", CONFIG_PATH, "def _validate_eval_stages"),
    ("config_candidate_runner_validation", CONFIG_PATH, "def _validate_candidate_language_runners"),
    ("evaluator_cascade", EVALUATOR_PATH, "class CascadeEvaluator:"),
    ("evaluator_stage_preflight", EVALUATOR_PATH, "preflight_evaluator_contracts"),
    ("evaluator_validate_path_metadata", EVALUATOR_PATH, "\"validate_path\""),
    ("loader_tests_minimal", TEST_LOADER_PATH, "assert isinstance(load_problem(_make(t)), Problem)"),
    ("loader_tests_context", TEST_LOADER_PATH, "context.yaml"),
    ("loader_tests_seed_policy", TEST_LOADER_PATH, "seed_policy"),
    ("loader_tests_embedded_only", TEST_LOADER_PATH, "test_allows_missing_validate_py_for_embedded_only_problem_config"),
    ("evaluator_tests_stage_validate", TEST_EVALUATOR_PATH, "stage_validate.py"),
    ("examples_workspace_math", TEST_EXAMPLES_PATH, "test_workspace_math_loader_records_nested_static_seed_workspace"),
    ("examples_embedded_evaluate", TEST_EXAMPLES_PATH, "test_embedded_evaluate_example_loads_without_external_validate_py"),
    ("workspace_math_example", WORKSPACE_MATH_PATH, "codebase_integration.yaml"),
    ("embedded_evaluate_example", EMBEDDED_EVALUATE_PATH, "config.yaml"),
    ("readme_problem_layout_sidecar", README_PROBLEM_LAYOUT_PATH, "readme_problem_layout"),
    ("validator_execution_sidecar", VALIDATOR_EXECUTION_PATH, "validator_execution_boundary"),
    ("embedded_evaluator_sidecar", EMBEDDED_EVALUATOR_PATH, "embedded_entrypoint_without_full_figure3_parity"),
    ("workspace_materialization_sidecar", WORKSPACE_MATERIALIZATION_PATH, "workspace_materialization_boundary"),
    ("candidate_language_sidecar", CANDIDATE_LANGUAGE_RUNNER_PATH, "candidate_language_runner_boundary"),
    ("benchmark_fixture_sidecar", BENCHMARK_FIXTURE_READINESS_PATH, "benchmark_fixture_readiness_boundary"),
    ("problem_formulation_sidecar", PROBLEM_FORMULATION_PATH, "problem_formulation_provenance_boundary"),
    ("readme_todo_owner", README_TODO_PATH, "Add problem-format guide loader-contract drift evidence."),
    ("code_todo_candidate_workspace", CODE_TODO_PATH, "Candidate Workspace Fidelity"),
    ("papers_todo_validator", PAPERS_TODO_PATH, "validator"),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "problem_format_section_inventory",
    "required_layout_file_markers",
    "context_manifest_semantics_markers",
    "codebase_integration_metadata_markers",
    "task_and_metrics_contract_markers",
    "validator_signature_and_stage_markers",
    "candidate_runner_declaration_markers",
    "evaluation_semantics_markers",
    "initial_program_and_seed_policy_markers",
    "mutation_mode_markers",
    "loader_source_anchor_map",
    "config_and_evaluator_anchor_map",
    "focused_loader_evaluator_example_tests",
    "sidecar_boundary_anchor_map",
    "active_todo_owner_anchor",
    "semantic_problem_format_claim_verifier",
    "per_manifest_key_executable_trace",
    "problem_format_docs_ci_drift_gate",
    "new_problem_surface_detector",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "semantic_problem_format_claim_verifier": "not_recorded_locally",
    "per_manifest_key_executable_trace": "not_recorded_locally",
    "problem_format_docs_ci_drift_gate": "not_recorded_locally",
    "new_problem_surface_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ProblemFormatLoaderContractBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ProblemFormatLoaderContractBoundaryValidation:
    ok: bool
    boundary_status: str | None
    guide_marker_count: int
    missing_guide_marker_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    missing_evidence_count: int
    issues: list[ProblemFormatLoaderContractBoundaryIssue]


def problem_format_loader_contract_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the problem-format structural loader-contract evidence map."""

    root_path = Path(root)
    paths = {
        PROBLEM_FORMAT_PATH,
        README_TODO_PATH,
        CODE_TODO_PATH,
        PAPERS_TODO_PATH,
        LOADER_PATH,
        CONFIG_PATH,
        EVALUATOR_PATH,
        TEST_LOADER_PATH,
        TEST_EVALUATOR_PATH,
        TEST_EXAMPLES_PATH,
        WORKSPACE_MATH_PATH,
        EMBEDDED_EVALUATE_PATH,
        README_PROBLEM_LAYOUT_PATH,
        VALIDATOR_EXECUTION_PATH,
        EMBEDDED_EVALUATOR_PATH,
        WORKSPACE_MATERIALIZATION_PATH,
        CANDIDATE_LANGUAGE_RUNNER_PATH,
        BENCHMARK_FIXTURE_READINESS_PATH,
        PROBLEM_FORMULATION_PATH,
    }
    texts = {path: _read_text(root_path / path) for path in paths}
    guide_marker_records = [
        _marker_record(record_id, PROBLEM_FORMAT_PATH, texts[PROBLEM_FORMAT_PATH], marker)
        for record_id, marker in EXPECTED_GUIDE_MARKERS
    ]
    evidence_anchor_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_EVIDENCE_ANCHORS
    ]
    missing_guide_markers = [
        record for record in guide_marker_records if record["marker_status"] != "marker_present"
    ]
    missing_evidence_anchors = [
        record for record in evidence_anchor_records if record["marker_status"] != "marker_present"
    ]
    return {
        "schema": PROBLEM_FORMAT_LOADER_CONTRACT_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "problem_format_path": PROBLEM_FORMAT_PATH,
        "source_paths": [LOADER_PATH, CONFIG_PATH, EVALUATOR_PATH],
        "test_paths": [TEST_LOADER_PATH, TEST_EVALUATOR_PATH, TEST_EXAMPLES_PATH],
        "example_paths": [WORKSPACE_MATH_PATH, EMBEDDED_EVALUATE_PATH],
        "sidecar_paths": [
            README_PROBLEM_LAYOUT_PATH,
            VALIDATOR_EXECUTION_PATH,
            EMBEDDED_EVALUATOR_PATH,
            WORKSPACE_MATERIALIZATION_PATH,
            CANDIDATE_LANGUAGE_RUNNER_PATH,
            BENCHMARK_FIXTURE_READINESS_PATH,
            PROBLEM_FORMULATION_PATH,
        ],
        "todo_paths": [README_TODO_PATH, CODE_TODO_PATH, PAPERS_TODO_PATH],
        "guide_marker_count": len(guide_marker_records),
        "missing_guide_marker_count": len(missing_guide_markers),
        "missing_guide_marker_records": missing_guide_markers,
        "guide_marker_records": guide_marker_records,
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "problem_format_contract_map_status": (
            "problem_format_structural_loader_contract_map_present"
            if not missing_guide_markers and not missing_evidence_anchors
            else "problem_format_structural_loader_contract_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records docs/problem-format.md section and claim "
            "markers for required layout, context manifests, codebase "
            "integration metadata, task and metrics files, validator "
            "signatures, configured evaluator stages, candidate runner "
            "declarations, evaluation semantics, seed workspaces, seed policy, "
            "mutation modes, and unsupported runner scope. It also records "
            "loader/config/evaluator source anchors, focused loader/evaluator/"
            "example test anchors, example path anchors, sidecar anchors, and "
            "active TODO ownership. It does not claim semantic problem-format "
            "claim verification, per-manifest-key executable traces, a problem-"
            "format docs CI drift gate, a new problem-surface detector, or "
            "owner review signoff."
        ),
    }


def validate_problem_format_loader_contract_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ProblemFormatLoaderContractBoundaryValidation:
    data, read_issues = _load_boundary(
        problem_format_loader_contract_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return ProblemFormatLoaderContractBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = problem_format_loader_contract_boundary_record(root)
    issues: list[ProblemFormatLoaderContractBoundaryIssue] = []
    if data.get("schema") != PROBLEM_FORMAT_LOADER_CONTRACT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported problem-format loader-contract boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "problem-format boundary must not claim semantic loader-contract proof"))
    for key in (
        "problem_format_path",
        "source_paths",
        "test_paths",
        "example_paths",
        "sidecar_paths",
        "todo_paths",
        "guide_marker_count",
        "missing_guide_marker_count",
        "missing_guide_marker_records",
        "guide_marker_records",
        "evidence_anchor_count",
        "missing_evidence_anchor_count",
        "missing_evidence_anchor_records",
        "evidence_anchor_records",
        "problem_format_contract_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current problem-format inputs"))
    if data.get("guide_marker_count") != len(EXPECTED_GUIDE_MARKERS):
        issues.append(_issue("invalid_guide_marker_count", "all expected problem-format guide markers must be recorded"))
    if data.get("missing_guide_marker_count") != 0:
        issues.append(_issue("missing_problem_format_guide_marker", "problem-format guide markers are incomplete"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_problem_format_evidence_anchor", "problem-format evidence anchors are incomplete"))
    if data.get("problem_format_contract_map_status") != "problem_format_structural_loader_contract_map_present":
        issues.append(_issue("invalid_problem_format_contract_map_status", "problem-format structural loader-contract map must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "docs/problem-format.md section and claim markers" not in boundary_text
        or "loader/config/evaluator source anchors" not in boundary_text
        or "does not claim semantic problem-format claim verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate structural problem-format evidence from semantic proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ProblemFormatLoaderContractBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        guide_marker_count=data.get("guide_marker_count") if isinstance(data.get("guide_marker_count"), int) else 0,
        missing_guide_marker_count=data.get("missing_guide_marker_count") if isinstance(data.get("missing_guide_marker_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_problem_format_loader_contract_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_problem_format_loader_contract_boundary(boundary)
    lines = [
        "Problem-format loader contract boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| guide_marker_count | {validation.guide_marker_count} |",
        f"| missing_guide_marker_count | {validation.missing_guide_marker_count} |",
        f"| evidence_anchor_count | {validation.evidence_anchor_count} |",
        f"| missing_evidence_anchor_count | {validation.missing_evidence_anchor_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _marker_record(record_id: str, path: str, text: str, marker: str) -> dict[str, Any]:
    return {
        "record_id": record_id,
        "path": path,
        "required_marker": marker,
        "marker_status": "marker_present" if marker in text else "marker_missing",
    }


def _read_text(path: Path) -> str:
    try:
        if path.is_dir():
            return "\n".join(sorted(item.name for item in path.iterdir()))
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[ProblemFormatLoaderContractBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "problem-format loader-contract boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ProblemFormatLoaderContractBoundaryIssue],
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
    issues: list[ProblemFormatLoaderContractBoundaryIssue],
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


def _issue(code: str, message: str) -> ProblemFormatLoaderContractBoundaryIssue:
    return ProblemFormatLoaderContractBoundaryIssue(code, message)
