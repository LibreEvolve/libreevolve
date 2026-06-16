from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


PLUGIN_GUIDE_CONTRACT_DRIFT_BOUNDARY_SCHEMA = (
    "libreevolve.plugin_guide_contract_drift_boundary.v1"
)
EXPECTED_BOUNDARY_STATUS = (
    "plugin_guide_structural_evidence_map_without_semantic_hook_proof"
)
PLUGINS_GUIDE_PATH = "docs/plugins.md"
README_TODO_PATH = "docs/todo/readme.md"
CODE_TODO_PATH = "docs/todo/code.md"
PLUGIN_BASE_PATH = "libreevolve/plugins/base.py"
PLUGIN_REGISTRY_PATH = "libreevolve/plugins/registry.py"
LOOP_PATH = "libreevolve/core/loop.py"
CONFIG_PATH = "libreevolve/core/config.py"
CAUSAL_PATH = "libreevolve/plugins/causal.py"
DEEP_RESEARCH_PATH = "libreevolve/plugins/deep_research.py"
MODULAR_PATH = "libreevolve/plugins/modular.py"
TTT_RL_PATH = "libreevolve/plugins/ttt_rl.py"
TEST_BASE_PATH = "tests/plugins/test_base.py"
TEST_CAUSAL_PATH = "tests/plugins/test_causal.py"
TEST_DEEP_RESEARCH_PATH = "tests/plugins/test_deep_research.py"
TEST_MODULAR_PATH = "tests/plugins/test_modular.py"
TEST_TTT_RL_PATH = "tests/plugins/test_ttt_rl.py"
TEST_LOOP_PATH = "tests/core/test_loop.py"
TEST_CONFIG_PATH = "tests/core/test_config.py"
ROADMAP_PLUGIN_EXTENSIBILITY_PATH = "papers/roadmap_plugin_extensibility_boundary.json"
ROADMAP_PLUGIN_READINESS_PATH = "papers/roadmap_plugin_readiness_boundary.json"
ROADMAP_NON_GOAL_PLUGIN_DOCSTRING_PATH = (
    "papers/roadmap_non_goal_plugin_docstring_boundary.json"
)

EXPECTED_GUIDE_MARKERS = (
    ("overview", "# Plugins"),
    ("hook_contract", "## Hook contract"),
    ("execution_order", "## Execution order"),
    ("safe_operations", "## What plugins can safely do"),
    ("built_in_plugins", "## Built-in plugins"),
    ("custom_plugin", "## Adding a custom plugin"),
    ("configured_alias_validation", "Configured plugin aliases must be manifest-safe labels"),
    ("direct_plugin_validation", "Direct library calls validate explicit plugin objects"),
    ("config_resolution", "resolves\n`Config.plugins` through the built-in registry"),
    ("configured_order", "Plugins run in configured order"),
    ("prompt_context_metadata", "`prompt_context_metadata()` is stored with the plugin-context record"),
    ("score_composition", "plugin score adjustments are recorded under `metadata.score_composition`"),
    ("invalid_candidate_scope", "archive admission is still gated by `evaluation.is_valid`"),
    ("artifact_metadata", "`run_artifacts_metadata()` is called near manifest finalization"),
    ("fatal_hook_policy", "plugin hook exceptions are fatal run aborts"),
    ("metric_side_effect_policy", "Unsafe metric side effects are reverted"),
    ("metadata_side_effect_policy", "unsafe metadata side effects are reverted"),
    ("causal_section", "### `causal`"),
    ("deep_research_section", "### `deep_research`"),
    ("modular_section", "### `modular`"),
    ("ttt_rl_section", "### `ttt_rl`"),
    ("entry_point_group", "`libreevolve.plugins` Python entry-point group"),
    ("constructor_schema", "`libreevolve_constructor_option_schema` class attribute"),
    ("distribution_metadata", "hash-only distribution `RECORD` / `WHEEL` summaries"),
    ("direct_plugin_policy", "`libreevolve.direct_plugin_policy.v1`"),
)
EXPECTED_EVIDENCE_ANCHORS = (
    ("plugin_base_class", PLUGIN_BASE_PATH, "class PluginBase"),
    ("plugin_base_generation_start", PLUGIN_BASE_PATH, "def on_generation_start"),
    ("plugin_base_evaluated", PLUGIN_BASE_PATH, "def on_evaluated"),
    ("plugin_base_generation_end", PLUGIN_BASE_PATH, "def on_generation_end"),
    ("plugin_base_extra_context", PLUGIN_BASE_PATH, "def build_extra_context"),
    ("plugin_base_prompt_metadata", PLUGIN_BASE_PATH, "def prompt_context_metadata"),
    ("plugin_base_artifacts", PLUGIN_BASE_PATH, "def run_artifacts_metadata"),
    ("builtin_registry", PLUGIN_REGISTRY_PATH, "def builtin_plugin_registry"),
    ("entry_point_label", PLUGIN_REGISTRY_PATH, '_ENTRY_POINT_LABEL = "entry_point"'),
    ("entry_point_group_schema", PLUGIN_REGISTRY_PATH, '"group": {"type": "enum", "values": {"libreevolve.plugins"}}'),
    ("constructor_schema_attribute", PLUGIN_REGISTRY_PATH, "_CONSTRUCTOR_SCHEMA_ATTRIBUTE"),
    ("distribution_record_metadata", PLUGIN_REGISTRY_PATH, "def _entry_point_distribution_record_metadata"),
    ("distribution_wheel_metadata", PLUGIN_REGISTRY_PATH, "def _entry_point_distribution_wheel_metadata"),
    ("config_plugin_specs", CONFIG_PATH, "def _validate_plugin_config_specs"),
    ("loop_config_plugin_loader", LOOP_PATH, "load_config_plugins(config.plugins, run_dir=run_dir)"),
    ("loop_generation_start", LOOP_PATH, "plugin_on_generation_start"),
    ("loop_prompt_context_metadata", LOOP_PATH, '"prompt_context_metadata"'),
    ("loop_evaluated", LOOP_PATH, "plugin_on_evaluated"),
    ("loop_generation_end", LOOP_PATH, "plugin_on_generation_end"),
    ("loop_artifact_manifest", LOOP_PATH, "def _plugin_artifact_manifest"),
    ("loop_plugin_failures", LOOP_PATH, '"plugin_failures"'),
    ("loop_score_composition", LOOP_PATH, 'program.metadata["score_composition"] = composition'),
    ("causal_plugin", CAUSAL_PATH, "class CausalPlugin"),
    ("deep_research_plugin", DEEP_RESEARCH_PATH, "class DeepResearchPlugin"),
    ("modular_plugin", MODULAR_PATH, "class ModularPlugin"),
    ("ttt_rl_plugin", TTT_RL_PATH, "class TTTRLPlugin"),
    ("base_plugin_tests", TEST_BASE_PATH, "test_evaluated_passthrough"),
    ("causal_plugin_tests", TEST_CAUSAL_PATH, "CausalPlugin"),
    ("deep_research_plugin_tests", TEST_DEEP_RESEARCH_PATH, "DeepResearchPlugin"),
    ("modular_plugin_tests", TEST_MODULAR_PATH, "ModularPlugin"),
    ("ttt_rl_plugin_tests", TEST_TTT_RL_PATH, "TTTRLPlugin"),
    ("loop_plugin_tests", TEST_LOOP_PATH, "plugin"),
    ("config_plugin_tests", TEST_CONFIG_PATH, "plugins"),
    ("readme_todo_owner", README_TODO_PATH, "Add plugin-guide hook contract drift evidence."),
    ("code_todo_plugin_contract", CODE_TODO_PATH, "plugin"),
    ("plugin_extensibility_sidecar", ROADMAP_PLUGIN_EXTENSIBILITY_PATH, "plugin_extensibility"),
    ("plugin_readiness_sidecar", ROADMAP_PLUGIN_READINESS_PATH, "plugin_readiness"),
    ("plugin_docstring_sidecar", ROADMAP_NON_GOAL_PLUGIN_DOCSTRING_PATH, "plugin_docstring"),
)
EXPECTED_REQUIRED_EVIDENCE_FIELDS = (
    "plugin_guide_section_inventory",
    "plugin_guide_hook_marker_inventory",
    "plugin_guide_execution_order_markers",
    "plugin_guide_score_and_admission_markers",
    "plugin_guide_artifact_and_failure_markers",
    "plugin_guide_builtin_plugin_markers",
    "plugin_guide_entry_point_markers",
    "source_module_anchor_map",
    "focused_test_anchor_map",
    "sidecar_boundary_anchor_map",
    "active_todo_owner_anchor",
    "semantic_hook_contract_verifier",
    "per_hook_executable_trace",
    "per_builtin_plugin_capability_matrix",
    "plugin_docs_ci_drift_gate",
    "owner_review_signoff",
)
EXPECTED_MISSING_EVIDENCE = {
    "semantic_hook_contract_verifier": "not_recorded_locally",
    "per_hook_executable_trace": "not_recorded_locally",
    "per_builtin_plugin_capability_matrix": "not_recorded_locally",
    "plugin_docs_ci_drift_gate": "not_recorded_locally",
    "owner_review_signoff": "not_recorded_locally",
}


@dataclass(frozen=True)
class PluginGuideContractDriftBoundaryIssue:
    code: str
    message: str


@dataclass(frozen=True)
class PluginGuideContractDriftBoundaryValidation:
    ok: bool
    boundary_status: str | None
    guide_marker_count: int
    missing_guide_marker_count: int
    evidence_anchor_count: int
    missing_evidence_anchor_count: int
    missing_evidence_count: int
    issues: list[PluginGuideContractDriftBoundaryIssue]


def plugin_guide_contract_drift_boundary_record(root: str | Path = ".") -> dict[str, Any]:
    """Return the plugin-guide structural evidence-map boundary."""

    root_path = Path(root)
    paths = {
        PLUGINS_GUIDE_PATH,
        README_TODO_PATH,
        CODE_TODO_PATH,
        PLUGIN_BASE_PATH,
        PLUGIN_REGISTRY_PATH,
        LOOP_PATH,
        CONFIG_PATH,
        CAUSAL_PATH,
        DEEP_RESEARCH_PATH,
        MODULAR_PATH,
        TTT_RL_PATH,
        TEST_BASE_PATH,
        TEST_CAUSAL_PATH,
        TEST_DEEP_RESEARCH_PATH,
        TEST_MODULAR_PATH,
        TEST_TTT_RL_PATH,
        TEST_LOOP_PATH,
        TEST_CONFIG_PATH,
        ROADMAP_PLUGIN_EXTENSIBILITY_PATH,
        ROADMAP_PLUGIN_READINESS_PATH,
        ROADMAP_NON_GOAL_PLUGIN_DOCSTRING_PATH,
    }
    texts = {path: _read_text(root_path / path) for path in paths}
    guide_marker_records = [
        _marker_record(record_id, PLUGINS_GUIDE_PATH, texts[PLUGINS_GUIDE_PATH], marker)
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
        "schema": PLUGIN_GUIDE_CONTRACT_DRIFT_BOUNDARY_SCHEMA,
        "boundary_status": EXPECTED_BOUNDARY_STATUS,
        "claim_ready": False,
        "plugin_guide_path": PLUGINS_GUIDE_PATH,
        "source_paths": [
            PLUGIN_BASE_PATH,
            PLUGIN_REGISTRY_PATH,
            LOOP_PATH,
            CONFIG_PATH,
            CAUSAL_PATH,
            DEEP_RESEARCH_PATH,
            MODULAR_PATH,
            TTT_RL_PATH,
        ],
        "test_paths": [
            TEST_BASE_PATH,
            TEST_CAUSAL_PATH,
            TEST_DEEP_RESEARCH_PATH,
            TEST_MODULAR_PATH,
            TEST_TTT_RL_PATH,
            TEST_LOOP_PATH,
            TEST_CONFIG_PATH,
        ],
        "sidecar_paths": [
            ROADMAP_PLUGIN_EXTENSIBILITY_PATH,
            ROADMAP_PLUGIN_READINESS_PATH,
            ROADMAP_NON_GOAL_PLUGIN_DOCSTRING_PATH,
        ],
        "todo_paths": [README_TODO_PATH, CODE_TODO_PATH],
        "guide_marker_count": len(guide_marker_records),
        "missing_guide_marker_count": len(missing_guide_markers),
        "missing_guide_marker_records": missing_guide_markers,
        "guide_marker_records": guide_marker_records,
        "evidence_anchor_count": len(evidence_anchor_records),
        "missing_evidence_anchor_count": len(missing_evidence_anchors),
        "missing_evidence_anchor_records": missing_evidence_anchors,
        "evidence_anchor_records": evidence_anchor_records,
        "plugin_guide_contract_map_status": (
            "plugin_guide_structural_evidence_map_present"
            if not missing_guide_markers and not missing_evidence_anchors
            else "plugin_guide_structural_evidence_map_incomplete"
        ),
        "required_evidence_fields": list(EXPECTED_REQUIRED_EVIDENCE_FIELDS),
        "missing_evidence": dict(EXPECTED_MISSING_EVIDENCE),
        "claim_boundary": (
            "This boundary records docs/plugins.md section, hook, execution-order, "
            "score/admission, artifact, fatal-failure, built-in plugin, "
            "entry-point, constructor-schema, package-provenance, and "
            "direct-plugin policy markers. It also records source-module, "
            "focused-test, sidecar, and active TODO anchors. It separates "
            "local synchronous hook support from AlphaEvolve-style plugin or "
            "agent parity. It does not claim semantic hook-contract "
            "verification, per-hook executable traces, a per-built-in plugin "
            "capability matrix, a plugin-docs CI drift gate, or owner review "
            "signoff."
        ),
    }


def validate_plugin_guide_contract_drift_boundary(
    boundary: object | str | Path | None = None,
    *,
    root: str | Path = ".",
) -> PluginGuideContractDriftBoundaryValidation:
    data, read_issues = _load_boundary(
        plugin_guide_contract_drift_boundary_record(root)
        if boundary is None
        else boundary
    )
    if read_issues:
        return PluginGuideContractDriftBoundaryValidation(
            False, None, 0, 0, 0, 0, 0, read_issues
        )
    assert isinstance(data, dict)
    expected = plugin_guide_contract_drift_boundary_record(root)
    issues: list[PluginGuideContractDriftBoundaryIssue] = []
    if data.get("schema") != PLUGIN_GUIDE_CONTRACT_DRIFT_BOUNDARY_SCHEMA:
        issues.append(_issue("invalid_schema", "unsupported plugin-guide contract drift boundary schema"))
    if data.get("boundary_status") != EXPECTED_BOUNDARY_STATUS:
        issues.append(_issue("invalid_boundary_status", f"boundary_status must be {EXPECTED_BOUNDARY_STATUS}"))
    if data.get("claim_ready") is not False:
        issues.append(_issue("claim_ready_overclaim", "plugin-guide contract map must not claim semantic hook proof"))
    for key in (
        "plugin_guide_path",
        "source_paths",
        "test_paths",
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
        "plugin_guide_contract_map_status",
    ):
        if data.get(key) != expected[key]:
            issues.append(_issue(f"invalid_{key}", f"{key} drifted from current plugin-guide inputs"))
    if data.get("guide_marker_count") != len(EXPECTED_GUIDE_MARKERS):
        issues.append(_issue("invalid_guide_marker_count", "all expected plugin-guide markers must be recorded"))
    if data.get("missing_guide_marker_count") != 0:
        issues.append(_issue("missing_plugin_guide_marker", "plugin-guide markers are incomplete"))
    if data.get("missing_evidence_anchor_count") != 0:
        issues.append(_issue("missing_plugin_evidence_anchor", "plugin-guide evidence anchors are incomplete"))
    if data.get("plugin_guide_contract_map_status") != "plugin_guide_structural_evidence_map_present":
        issues.append(_issue("invalid_plugin_guide_contract_map_status", "plugin-guide structural evidence map must be present"))
    missing_count = _validate_missing_evidence(data.get("missing_evidence"), issues)
    required_count = _validate_required_fields(data.get("required_evidence_fields"), issues)
    boundary_text = data.get("claim_boundary")
    if (
        not isinstance(boundary_text, str)
        or "docs/plugins.md section, hook, execution-order" not in boundary_text
        or "source-module, focused-test, sidecar, and active TODO anchors" not in boundary_text
        or "local synchronous hook support from AlphaEvolve-style plugin or agent parity" not in boundary_text
        or "does not claim semantic hook-contract verification" not in boundary_text
    ):
        issues.append(_issue("missing_claim_boundary", "claim_boundary must separate structural plugin-guide evidence from semantic proof"))
    if required_count != len(EXPECTED_REQUIRED_EVIDENCE_FIELDS):
        issues.append(_issue("invalid_required_evidence_field_count", "required evidence field count changed"))
    return PluginGuideContractDriftBoundaryValidation(
        ok=not issues,
        boundary_status=data.get("boundary_status") if isinstance(data.get("boundary_status"), str) else None,
        guide_marker_count=data.get("guide_marker_count") if isinstance(data.get("guide_marker_count"), int) else 0,
        missing_guide_marker_count=data.get("missing_guide_marker_count") if isinstance(data.get("missing_guide_marker_count"), int) else 0,
        evidence_anchor_count=data.get("evidence_anchor_count") if isinstance(data.get("evidence_anchor_count"), int) else 0,
        missing_evidence_anchor_count=data.get("missing_evidence_anchor_count") if isinstance(data.get("missing_evidence_anchor_count"), int) else 0,
        missing_evidence_count=missing_count,
        issues=issues,
    )


def render_plugin_guide_contract_drift_boundary_summary(boundary: dict[str, Any]) -> str:
    validation = validate_plugin_guide_contract_drift_boundary(boundary)
    lines = [
        "Plugin guide contract drift boundary",
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
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return ""


def _load_boundary(
    boundary: object | str | Path,
) -> tuple[dict[str, Any] | None, list[PluginGuideContractDriftBoundaryIssue]]:
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
    return None, [_issue("invalid_shape", "plugin-guide contract drift boundary must be a JSON object")]


def _validate_required_fields(
    value: object,
    issues: list[PluginGuideContractDriftBoundaryIssue],
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
    issues: list[PluginGuideContractDriftBoundaryIssue],
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


def _issue(code: str, message: str) -> PluginGuideContractDriftBoundaryIssue:
    return PluginGuideContractDriftBoundaryIssue(code, message)
