from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


README_PROBLEM_LAYOUT_BOUNDARY_SCHEMA = (
    "libreevolve.readme_problem_layout_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "readme_problem_layout_structural_map_without_semantic_loader_proof"
)
README_PATH = "README.md"
PROBLEM_FORMAT_PATH = "docs/problem-format.md"
README_TODO_PATH = "docs/todo/readme.md"
CODE_TODO_PATH = "docs/todo/code.md"
PAPERS_TODO_PATH = "docs/todo/papers.md"
LOADER_PATH = "libreevolve/problems/loader.py"
CONFIG_PATH = "libreevolve/core/config.py"
EVALUATOR_PATH = "libreevolve/core/evaluator.py"
TEST_LOADER_PATH = "tests/core/test_loader.py"
TEST_EXAMPLES_PATH = "tests/test_examples.py"
HELLO_WORLD_PATH = "libreevolve/problems/examples/hello_world"
WORKSPACE_MATH_PATH = "libreevolve/problems/examples/workspace_math"
EMBEDDED_EVALUATE_PATH = "libreevolve/problems/examples/embedded_evaluate_math"
VALIDATOR_EXECUTION_PATH = "papers/validator_execution_boundary.json"
EMBEDDED_EVALUATOR_PATH = "papers/embedded_evaluator_boundary.json"
WORKSPACE_MATERIALIZATION_PATH = "papers/workspace_materialization_boundary.json"
CANDIDATE_LANGUAGE_RUNNER_PATH = "papers/candidate_language_runner_boundary.json"
BENCHMARK_FIXTURE_READINESS_PATH = "papers/benchmark_fixture_readiness_boundary.json"
PROBLEM_FORMULATION_PATH = "papers/problem_formulation_provenance_boundary.json"

EXPECTED_LAYOUT_ITEMS = (
    {
        "item_id": "initial_programs",
        "path_label": "initial_programs/",
        "readme_marker": "`initial_programs/`: one or more seed programs.",
        "problem_format_markers": (
            "└── initial_programs/",
            "All `*.py` files in `initial_programs/` are loaded",
            "`seed_source_path` such as `initial_programs/seed.py`",
        ),
        "loader_markers": (
            "seed_dir = d / \"initial_programs\"",
            "workspaces, seed_sources, seed_skipped, seed_policy = _load_initial_workspaces(seed_dir)",
            "def _load_initial_workspaces",
        ),
        "example_paths": (
            "libreevolve/problems/examples/hello_world/initial_programs",
            "libreevolve/problems/examples/workspace_math/initial_programs/baseline",
        ),
        "test_markers": (
            "assert len(p.initial_programs) == 1 and \"x = 1\" in p.initial_programs[0]",
            "test_workspace_math_loader_records_nested_static_seed_workspace",
        ),
        "status": "required_with_file_or_directory_seed_support",
    },
    {
        "item_id": "validate_py",
        "path_label": "validate.py",
        "readme_marker": "`validate.py`: evaluator entrypoint.",
        "problem_format_markers": (
            "├── validate.py",
            "`validate.py` must expose either the legacy one-argument signature",
            "`validate.py` in a subprocess, calls the compatible `evaluate(...)` signature",
        ),
        "loader_markers": (
            "validate_path = d / \"validate.py\"",
            "_problem_config_declares_embedded_only_evaluation",
            "_require_problem_file(validate_path, \"validate.py\")",
        ),
        "example_paths": (
            "libreevolve/problems/examples/hello_world/validate.py",
            "libreevolve/problems/examples/workspace_math/validate.py",
        ),
        "test_markers": (
            "test_allows_missing_validate_py_for_embedded_only_problem_config",
            "test_requires_validate_py_when_problem_config_has_external_stage",
        ),
        "status": "required_for_external_validator_with_embedded_only_exception",
    },
    {
        "item_id": "metrics_yaml",
        "path_label": "metrics.yaml",
        "readme_marker": "`metrics.yaml`: metric names, directions, bounds, and primary metric.",
        "problem_format_markers": (
            "├── metrics.yaml",
            "## `metrics.yaml`",
            "primary metric name from `metrics.yaml`",
        ),
        "loader_markers": (
            "metrics_path = d / \"metrics.yaml\"",
            "raw = _load_metrics_yaml(metrics_path)",
            "metrics, primary_metric, primary_bounds = _normalize_metric_schema(metrics, d)",
        ),
        "example_paths": (
            "libreevolve/problems/examples/hello_world/metrics.yaml",
            "libreevolve/problems/examples/workspace_math/metrics.yaml",
            "libreevolve/problems/examples/embedded_evaluate_math/metrics.yaml",
        ),
        "test_markers": (
            "test_raises_on_malformed_metrics_yaml",
            "test_rejects_unsupported_top_level_metrics_yaml_keys_with_path",
        ),
        "status": "required_metric_schema_file",
    },
    {
        "item_id": "task_description",
        "path_label": "task_description.txt",
        "readme_marker": "`task_description.txt`: task instructions for the mutation prompt.",
        "problem_format_markers": (
            "├── task_description.txt",
            "## `task_description.txt`",
            "task_description.txt`, `metrics.yaml`, and `validate.py` must be",
        ),
        "loader_markers": (
            "task_path = d / \"task_description.txt\"",
            "task = _read_problem_text(task_path)",
            "must contain a non-empty task description",
        ),
        "example_paths": (
            "libreevolve/problems/examples/hello_world/task_description.txt",
            "libreevolve/problems/examples/workspace_math/task_description.txt",
            "libreevolve/problems/examples/embedded_evaluate_math/task_description.txt",
        ),
        "test_markers": (
            "assert load_problem(_make(t)).task_description == \"test task\"",
            "non-empty task description",
        ),
        "status": "required_prompt_task_file",
    },
    {
        "item_id": "config_yaml",
        "path_label": "config.yaml",
        "readme_marker": "optional `config.yaml`: backend, archive, prompt, and evaluator settings.",
        "problem_format_markers": (
            "Problem `config.yaml` stages accept",
            "`config.yaml` can declare candidate-language and build-system records.",
            "`Config.eval_stages` can run configured `external_validator`",
        ),
        "loader_markers": (
            "config_source:    dict = field(",
            "path = problem_dir / \"config.yaml\"",
            "raw = safe_load_unique(text) if text.strip() else {}",
        ),
        "example_paths": (
            "libreevolve/problems/examples/embedded_evaluate_math/config.yaml",
            "libreevolve/problems/examples/candidate_runner_expression/config.yaml",
            "libreevolve/problems/examples/candidate_runner_c/config.yaml",
            "libreevolve/problems/examples/candidate_runner_python_oci/config.yaml",
        ),
        "test_markers": (
            "test_allows_missing_validate_py_for_embedded_only_problem_config",
            "test_requires_validate_py_when_problem_config_has_external_stage",
        ),
        "status": "optional_problem_runtime_configuration",
    },
    {
        "item_id": "seed_policy_yaml",
        "path_label": "initial_programs/seed_policy.yaml",
        "readme_marker": "optional `initial_programs/seed_policy.yaml`: hidden/cache path policy",
        "problem_format_markers": (
            "add `initial_programs/seed_policy.yaml`",
            "When `seed_policy.yaml` sets `primary_file`",
            "`primary_file` is a normalized candidate path, not a glob",
        ),
        "loader_markers": (
            "_SEED_POLICY_MANIFEST_NAMES = (\"seed_policy.yaml\", \"seed_policy.yml\")",
            "def _load_seed_workspace_policy",
            "def _seed_policy_primary_file",
        ),
        "example_paths": (
            "libreevolve/problems/examples/candidate_runner_expression/initial_programs/seed_policy.yaml",
            "libreevolve/problems/examples/candidate_runner_c/initial_programs/seed_policy.yaml",
            "libreevolve/problems/examples/candidate_runner_python_oci/initial_programs/seed_policy.yaml",
        ),
        "test_markers": (
            "test_seed_policy_selects_non_python_primary_file_for_workspace",
            "test_seed_policy_rejects_missing_configured_primary_file",
        ),
        "status": "optional_seed_workspace_policy_and_primary_selection",
    },
)
EXPECTED_CONTRACT_MARKERS = (
    ("readme_problem_directory_scope", README_PATH, "Problem directories live under `libreevolve/problems/examples/`."),
    ("readme_problem_format_route", README_PATH, "[docs/problem-format.md](docs/problem-format.md)"),
    ("problem_format_loader_route", PROBLEM_FORMAT_PATH, "[`libreevolve/problems/loader.py`](../libreevolve/problems/loader.py)"),
    ("problem_format_context_manifest", PROBLEM_FORMAT_PATH, "Optional context files can be placed in:"),
    ("problem_format_codebase_integration", PROBLEM_FORMAT_PATH, "codebase_integration.yaml"),
    ("problem_format_seed_policy", PROBLEM_FORMAT_PATH, "initial_programs/seed_policy.yaml"),
    ("problem_format_candidate_runner", PROBLEM_FORMAT_PATH, "## Candidate Runner Declarations"),
    ("problem_format_candidate_toolchain", PROBLEM_FORMAT_PATH, "toolchain_candidates: [\"clang\", \"gcc\", \"cc\"]"),
    ("loader_context_manifest_names", LOADER_PATH, "_CONTEXT_MANIFEST_NAMES = (\"context.yaml\", \"context.yml\")"),
    ("loader_seed_policy_names", LOADER_PATH, "_SEED_POLICY_MANIFEST_NAMES = (\"seed_policy.yaml\", \"seed_policy.yml\")"),
    ("loader_codebase_integration_names", LOADER_PATH, "_CODEBASE_INTEGRATION_METADATA_NAMES"),
    ("config_eval_stages", CONFIG_PATH, "eval_stages:            list[dict] = field(default_factory=list)"),
    ("config_candidate_language_runners", CONFIG_PATH, "candidate_language_runners: list[dict] = field(default_factory=list)"),
    ("config_candidate_runner_stage_bindings", CONFIG_PATH, "def _validate_candidate_runner_stage_bindings"),
    ("config_candidate_toolchain_contract", CONFIG_PATH, "def _validate_candidate_toolchain_contract"),
    ("config_candidate_execution_environment", CONFIG_PATH, "def _validate_candidate_execution_environment"),
    ("evaluator_cascade", EVALUATOR_PATH, "class CascadeEvaluator"),
    ("evaluator_candidate_runner", EVALUATOR_PATH, "def _run_candidate_runner_subprocess"),
    ("evaluator_candidate_toolchain", EVALUATOR_PATH, "def _prepare_candidate_build_toolchain"),
    ("evaluator_candidate_container", EVALUATOR_PATH, "def _prepare_candidate_container_environment"),
    ("loader_seed_primary_file", LOADER_PATH, "def _seed_workspace_primary_file"),
    ("examples_loader_smoke", TEST_EXAMPLES_PATH, "problem = load_problem(SORTING_NETWORK_8_EXAMPLE_DIR)"),
    ("examples_c_toolchain_smoke", TEST_EXAMPLES_PATH, "def test_candidate_runner_c_example_loads_compiles_and_scores"),
    ("examples_oci_toolchain_smoke", TEST_EXAMPLES_PATH, "def test_candidate_runner_python_oci_example_loads_with_immutable_contract"),
    ("readme_todo_owner", README_TODO_PATH, "Add README problem-layout contract drift evidence."),
    ("code_todo_candidate_workspace", CODE_TODO_PATH, "Candidate Workspace Fidelity"),
    ("papers_todo_evaluator_contract", PAPERS_TODO_PATH, "validator"),
    ("validator_execution_sidecar", VALIDATOR_EXECUTION_PATH, "validator_execution_boundary"),
    ("embedded_evaluator_sidecar", EMBEDDED_EVALUATOR_PATH, "embedded_entrypoint_without_full_figure3_parity"),
    ("workspace_materialization_sidecar", WORKSPACE_MATERIALIZATION_PATH, "workspace_materialization_boundary"),
    ("candidate_language_runner_sidecar", CANDIDATE_LANGUAGE_RUNNER_PATH, "candidate_language_runner_boundary"),
    ("benchmark_fixture_sidecar", BENCHMARK_FIXTURE_READINESS_PATH, "benchmark_fixture_readiness_boundary"),
    ("problem_formulation_sidecar", PROBLEM_FORMULATION_PATH, "problem_formulation_provenance_boundary"),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "readme_problem_layout_block_inventory",
    "readme_required_optional_file_markers",
    "problem_format_route_marker",
    "loader_required_file_anchor_map",
    "loader_optional_config_anchor_map",
    "example_problem_path_existence_checks",
    "focused_loader_and_example_test_anchors",
    "alphaevolve_problem_surface_sidecar_anchors",
    "active_todo_owner_anchor",
    "semantic_loader_contract_verifier",
    "minimal_problem_smoke_fixture",
    "problem_format_long_contract_drift_gate",
    "new_problem_surface_detector",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "semantic_loader_contract_verifier": "not_recorded_locally",
    "minimal_problem_smoke_fixture": "not_recorded_locally",
    "problem_format_long_contract_drift_gate": "not_recorded_locally",
    "new_problem_surface_detector": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class ReadmeProblemLayoutBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class ReadmeProblemLayoutBoundaryValidation:
    ok: bool
    boundary_status: str | None
    layout_item_count: int
    missing_layout_item_count: int
    contract_marker_count: int
    missing_contract_marker_count: int
    missing_example_path_count: int
    missing_evidence_count: int
    issues: list[ReadmeProblemLayoutBoundaryIssue]


def readme_problem_layout_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the README Problem Layout structural evidence-map boundary."""

    root_path = Path(root)
    paths = {
        README_PATH,
        PROBLEM_FORMAT_PATH,
        README_TODO_PATH,
        CODE_TODO_PATH,
        PAPERS_TODO_PATH,
        LOADER_PATH,
        CONFIG_PATH,
        EVALUATOR_PATH,
        TEST_LOADER_PATH,
        TEST_EXAMPLES_PATH,
        VALIDATOR_EXECUTION_PATH,
        EMBEDDED_EVALUATOR_PATH,
        WORKSPACE_MATERIALIZATION_PATH,
        CANDIDATE_LANGUAGE_RUNNER_PATH,
        BENCHMARK_FIXTURE_READINESS_PATH,
        PROBLEM_FORMULATION_PATH,
    }
    texts = {path: _read_text(root_path / path) for path in paths}
    problem_layout_block = _extract_problem_layout_block(texts[README_PATH])
    item_records = [
        _layout_item_record(root_path, problem_layout_block, texts, item)
        for item in EXPECTED_LAYOUT_ITEMS
    ]
    contract_marker_records = [
        _marker_record(record_id, path, texts[path], marker)
        for record_id, path, marker in EXPECTED_CONTRACT_MARKERS
    ]
    missing_items = [
        record for record in item_records if record["item_status"] != "item_markers_and_examples_present"
    ]
    missing_contract_markers = [
        record for record in contract_marker_records if record["marker_status"] != "marker_present"
    ]
    missing_example_paths = sorted(
        {
            path
            for record in item_records
            for path in record["missing_example_paths"]
        }
    )
    return {
        "schema": README_PROBLEM_LAYOUT_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "readme_path": README_PATH,
        "problem_format_path": PROBLEM_FORMAT_PATH,
        "source_paths": [LOADER_PATH, CONFIG_PATH, EVALUATOR_PATH],
        "test_paths": [TEST_LOADER_PATH, TEST_EXAMPLES_PATH],
        "sidecar_paths": [
            VALIDATOR_EXECUTION_PATH,
            EMBEDDED_EVALUATOR_PATH,
            WORKSPACE_MATERIALIZATION_PATH,
            CANDIDATE_LANGUAGE_RUNNER_PATH,
            BENCHMARK_FIXTURE_READINESS_PATH,
            PROBLEM_FORMULATION_PATH,
        ],
        "todo_paths": [README_TODO_PATH, CODE_TODO_PATH, PAPERS_TODO_PATH],
        "problem_layout_block_status": (
            "problem_layout_block_present"
            if problem_layout_block
            else "problem_layout_block_missing"
        ),
        "layout_item_count": len(item_records),
        "missing_layout_item_count": len(missing_items),
        "missing_layout_item_records": missing_items,
        "layout_item_records": item_records,
        "contract_marker_count": len(contract_marker_records),
        "missing_contract_marker_count": len(missing_contract_markers),
        "missing_contract_marker_records": missing_contract_markers,
        "contract_marker_records": contract_marker_records,
        "missing_example_path_count": len(missing_example_paths),
        "missing_example_paths": missing_example_paths,
        "readme_problem_layout_map_status": (
            "readme_problem_layout_structural_map_present"
            if not missing_items and not missing_contract_markers and not missing_example_paths
            else "readme_problem_layout_structural_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records the README Problem Layout block, required "
            "and optional file markers, docs/problem-format.md route, loader "
            "anchors, example problem path existence checks, focused "
            "loader/example test anchors, AlphaEvolve problem-surface sidecar "
            "anchors, and active TODO ownership. It does not claim semantic "
            "loader-contract verification, a dedicated minimal-problem smoke "
            "fixture, full problem-format long-contract drift validation, a "
            "new problem-surface detector, or owner review signoff."
        ),
    }


def validate_readme_problem_layout_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> ReadmeProblemLayoutBoundaryValidation:
    data, read_issues = _load_boundary(
        readme_problem_layout_boundary_record(root) if boundary is None else boundary
    )
    if read_issues:
        return ReadmeProblemLayoutBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = readme_problem_layout_boundary_record(root)
    issues: list[ReadmeProblemLayoutBoundaryIssue] = []
    if data.get("schema") != README_PROBLEM_LAYOUT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported README problem-layout boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "README problem-layout boundary must not claim semantic loader proof"))
    for key in (
        "readme_path",
        "problem_format_path",
        "source_paths",
        "test_paths",
        "sidecar_paths",
        "todo_paths",
        "problem_layout_block_status",
        "layout_item_count",
        "missing_layout_item_count",
        "missing_layout_item_records",
        "layout_item_records",
        "contract_marker_count",
        "missing_contract_marker_count",
        "missing_contract_marker_records",
        "contract_marker_records",
        "missing_example_path_count",
        "missing_example_paths",
        "readme_problem_layout_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current README problem-layout inputs"))
    if data.get("problem_layout_block_status") != "problem_layout_block_present":
        issues.append(_issue("missing_problem_layout_block", "README must keep the Problem Layout section"))
    if data.get("missing_layout_item_count") != 0:
        issues.append(_issue("missing_problem_layout_item", "README Problem Layout item markers are incomplete"))
    if data.get("missing_contract_marker_count") != 0:
        issues.append(_issue("missing_problem_layout_contract_marker", "README Problem Layout contract anchors are incomplete"))
    if data.get("missing_example_path_count") != 0:
        issues.append(_issue("missing_problem_layout_example_path", "README Problem Layout example anchors are missing"))
    if data.get("readme_problem_layout_map_status") != "readme_problem_layout_structural_map_present":
        issues.append(_issue("invalid_readme_problem_layout_map_status", "README problem-layout structural map must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "README Problem Layout block" not in boundary_text
        or "docs/problem-format.md route" not in boundary_text
        or "does not claim semantic loader-contract verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate structural README problem-layout evidence from semantic proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return ReadmeProblemLayoutBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        layout_item_count=data.get("layout_item_count") if isinstance(data.get("layout_item_count"), int) else 0,
        missing_layout_item_count=(
            data.get("missing_layout_item_count")
            if isinstance(data.get("missing_layout_item_count"), int)
            else 0
        ),
        contract_marker_count=data.get("contract_marker_count") if isinstance(data.get("contract_marker_count"), int) else 0,
        missing_contract_marker_count=(
            data.get("missing_contract_marker_count")
            if isinstance(data.get("missing_contract_marker_count"), int)
            else 0
        ),
        missing_example_path_count=(
            data.get("missing_example_path_count")
            if isinstance(data.get("missing_example_path_count"), int)
            else 0
        ),
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_readme_problem_layout_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_readme_problem_layout_boundary(boundary)
    lines = [
        "README Problem Layout boundary",
        "",
        "| Field | Value |",
        "|---|---|",
        f"| schema_status | {'ok' if validation.ok else 'invalid'} |",
        f"| boundary_status | {validation.boundary_status or '<unknown>'} |",
        f"| layout_item_count | {validation.layout_item_count} |",
        f"| missing_layout_item_count | {validation.missing_layout_item_count} |",
        f"| contract_marker_count | {validation.contract_marker_count} |",
        f"| missing_contract_marker_count | {validation.missing_contract_marker_count} |",
        f"| missing_example_path_count | {validation.missing_example_path_count} |",
        f"| missing_evidence_count | {validation.missing_evidence_count} |",
    ]
    if validation.issues:
        lines.extend(["", "Issues:"])
        lines.extend(f"- {issue.code}: {issue.message}" for issue in validation.issues)
    return "\n".join(lines)


def _extract_problem_layout_block(readme_text: str) -> str:
    marker = "## Problem Layout"
    marker_index = readme_text.find(marker)
    if marker_index < 0:
        return ""
    next_section = readme_text.find("\n## ", marker_index + len(marker))
    if next_section < 0:
        return readme_text[marker_index:]
    return readme_text[marker_index:next_section]


def _layout_item_record(
    root: Path,
    problem_layout_block: str,
    texts: dict[str, str],
    item: dict[str, Any],
) -> dict[str, Any]:
    problem_format_records = [
        _marker_record(
            f"{item['item_id']}:problem_format:{index}",
            PROBLEM_FORMAT_PATH,
            texts[PROBLEM_FORMAT_PATH],
            marker,
        )
        for index, marker in enumerate(item["problem_format_markers"])
    ]
    loader_records = [
        _marker_record(
            f"{item['item_id']}:loader:{index}",
            LOADER_PATH,
            texts[LOADER_PATH],
            marker,
        )
        for index, marker in enumerate(item["loader_markers"])
    ]
    test_text = "\n".join([texts[TEST_LOADER_PATH], texts[TEST_EXAMPLES_PATH]])
    test_records = [
        _marker_record(
            f"{item['item_id']}:test:{index}",
            "tests/core/test_loader.py;tests/test_examples.py",
            test_text,
            marker,
        )
        for index, marker in enumerate(item["test_markers"])
    ]
    example_paths = [str(path) for path in item["example_paths"]]
    missing_example_paths = [
        path for path in example_paths if not (root / path).exists()
    ]
    readme_marker_present = item["readme_marker"] in problem_layout_block
    missing_problem_format_markers = [
        record for record in problem_format_records if record["marker_status"] != "marker_present"
    ]
    missing_loader_markers = [
        record for record in loader_records if record["marker_status"] != "marker_present"
    ]
    missing_test_markers = [
        record for record in test_records if record["marker_status"] != "marker_present"
    ]
    item_status = (
        "item_markers_and_examples_present"
        if readme_marker_present
        and not missing_problem_format_markers
        and not missing_loader_markers
        and not missing_test_markers
        and not missing_example_paths
        else "item_markers_or_examples_missing"
    )
    return {
        "item_id": item["item_id"],
        "path_label": item["path_label"],
        "status": item["status"],
        "readme_marker": item["readme_marker"],
        "readme_marker_status": (
            "marker_present" if readme_marker_present else "marker_missing"
        ),
        "problem_format_marker_records": problem_format_records,
        "missing_problem_format_marker_records": missing_problem_format_markers,
        "loader_marker_records": loader_records,
        "missing_loader_marker_records": missing_loader_markers,
        "test_marker_records": test_records,
        "missing_test_marker_records": missing_test_markers,
        "example_paths": example_paths,
        "missing_example_paths": missing_example_paths,
        "item_status": item_status,
    }


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
) -> tuple[dict[str, Any] | None, list[ReadmeProblemLayoutBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "README problem-layout boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[ReadmeProblemLayoutBoundaryIssue],
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
    issues: list[ReadmeProblemLayoutBoundaryIssue],
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


def _issue(code: str, message: str) -> ReadmeProblemLayoutBoundaryIssue:
    return ReadmeProblemLayoutBoundaryIssue(code, message)
