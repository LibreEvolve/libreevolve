from __future__ import annotations

# Populated after the validators below; prompt.py re-exports this contract.

import math
import re
import unicodedata
from collections.abc import Mapping

from libreevolve.core.candidate import normalize_candidate_path
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.population.program import validate_program_metrics


try:
    PromptTemplateError
except NameError:
    class PromptTemplateError(ValueError):
        """Raised when a configured or evolved prompt template is not renderable."""


_PROMPT_POLICY_TEMPLATE_FIELDS = {
    "task",
    "context",
    "parent_score",
    "parent_metrics",
    "parent_feedback",
    "parent_code",
    "inspirations",
    "extra_context",
    "recent_failures",
    "mutation_mode",
    "mutation_instructions",
}

_PROMPT_POLICY_ARTIFACT_CONTENT_MODES = {"excerpt", "bounded_file", "off"}
PROMPT_CONTEXT_POLICY_SCHEMA = "libreevolve.prompt_context_policy.v1"
PROMPT_CONTEXT_POLICY_DISABLED_SECTIONS = frozenset(
    {
        "context",
        "parent_score",
        "parent_metrics",
        "parent_feedback",
        "inspirations",
        "extra_context",
        "recent_failures",
        "mutation_mode",
    }
)
PROMPT_CONTEXT_POLICY_MUTATION_INSTRUCTION_VARIANTS = frozenset(
    {"default", "minimal", "exploratory"}
)
PROMPT_CONTEXT_POLICY_INSPIRATION_STRATEGIES = frozenset(
    {
        "mixed",
        "random",
        "selection",
        "metric",
        "frontier",
        "lineage",
        "novelty",
        "recency",
    }
)
PROMPT_CONTEXT_POLICY_CONTEXT_SOURCE_TRUNCATION = frozenset(
    {"head", "head_tail"}
)
PROMPT_CONTEXT_POLICY_CONTEXT_SOURCE_ORDER_POLICIES = frozenset(
    {"path_order", "task_term_ranked"}
)
PROMPT_CONTEXT_POLICY_FEEDBACK_SECTIONS = frozenset(
    {
        "proposal",
        "stage_summary",
        "execution_output",
        "sample_retry_diagnostics",
        "validator_artifacts",
        "validator_diagnostics",
        "program_outputs",
        "llm_grader_feedback",
    }
)
PROMPT_CONTEXT_POLICY_FEEDBACK_SECTION_ORDER = (
    "proposal",
    "stage_summary",
    "execution_output",
    "sample_retry_diagnostics",
    "validator_artifacts",
    "validator_diagnostics",
    "program_outputs",
    "llm_grader_feedback",
)
PROMPT_CONTEXT_POLICY_LLM_FEEDBACK_FIELDS = (
    "name",
    "score",
    "discard",
    "error",
    "feedback",
)
PROMPT_CONTEXT_POLICY_RECENT_FAILURE_FIELDS = (
    "error",
    "diff_error",
    "changed_file",
    "mutation",
    "evaluation",
    "evaluation_error",
    "evaluation_stdout",
    "evaluation_stderr",
    "stage_name",
    "stage_error",
    "diagnostics",
    "llm_feedback",
)
PROMPT_CONTEXT_POLICY_PROPOSAL_FIELDS = (
    "idea",
    "rationale",
    "hypothesis",
)
PROMPT_CONTEXT_POLICY_STAGE_SUMMARY_FIELDS = (
    "name",
    "status",
    "score",
    "error",
    "io",
    "checks",
)
PROMPT_CONTEXT_POLICY_EXECUTION_OUTPUT_FIELDS = (
    "stdout",
    "stderr",
    "error",
)
PROMPT_CONTEXT_POLICY_SAMPLE_RETRY_FIELDS = (
    "status",
    "stage",
    "sample",
    "attempt",
    "fitness",
    "error",
)
PROMPT_CONTEXT_POLICY_PROGRAM_OUTPUT_FIELDS = (
    "source",
    "json_chars",
    "sha256",
    "redacted",
    "preview",
    "value",
)
PROMPT_CONTEXT_POLICY_VALIDATOR_ARTIFACT_FIELDS = (
    "path",
    "stored",
    "sha256",
    "redacted",
    "content_excerpt",
    "content_excerpt_truncated",
    "content_excerpt_status",
    "artifact_content",
)
PROMPT_CONTEXT_POLICY_VALIDATOR_ARTIFACT_CONTENT_FIELDS = (
    "status",
    "bytes",
    "max_bytes",
    "chars",
    "truncated",
    "content",
)
PROMPT_CONTEXT_POLICY_VALIDATOR_SKIPPED_ARTIFACT_FIELDS = (
    "path",
    "reason",
    "message",
    "size",
    "max_bytes",
    "redacted",
    "sha256",
    "value",
)
PROMPT_CONTEXT_POLICY_VALIDATOR_DIAGNOSTIC_GROUPS = (
    "evaluator_dependency",
    "evaluator_path",
    "evaluator_stage",
    "evaluator_workspace",
    "syntax_errors",
    "metric_bound_diagnostics",
    "configured_stage_checks",
    "malformed_metrics",
    "materialization_error",
    "metric_aggregation",
    "synthetic_metrics",
    "execution_diagnostics",
    "metadata_summary",
)
PROMPT_CONTEXT_POLICY_EXECUTION_DIAGNOSTIC_GROUPS = (
    "validator_boundary",
    "validator_budget",
    "validator_env",
    "stdin",
    "diagnostic_output",
    "timeout_cleanup",
)
PROMPT_CONTEXT_POLICY_VALIDATOR_BUDGET_FIELDS = (
    "policy",
    "max_stage_seconds",
    "max_sample_seconds",
    "elapsed_sec",
    "remaining_sec",
    "exhausted",
)
PROMPT_CONTEXT_POLICY_VALIDATOR_ENV_FIELDS = (
    "policy",
    "default_keys",
    "allowlist",
    "provided_keys",
    "values_redacted",
)
PROMPT_CONTEXT_POLICY_EVALUATOR_PATH_FIELDS = (
    "validate_path",
    "validate_path_scope",
    "validate_path_hash",
    "validate_path_redacted",
)
PROMPT_CONTEXT_POLICY_EVALUATOR_DEPENDENCY_FIELDS = (
    "policy",
    "allowed_scope",
    "outside_problem_policy",
    "file_count",
    "file_paths",
    "file_hashes",
    "file_redactions",
)
PROMPT_CONTEXT_POLICY_EVALUATOR_STAGE_FIELDS = (
    "name",
    "stage_index",
    "sample_index",
    "attempt",
    "seed",
    "validate_path",
    "stdin_policy",
    "evaluator_data_enabled",
    "evaluator_data_file_count",
)
PROMPT_CONTEXT_POLICY_EVALUATOR_WORKSPACE_FIELDS = (
    "primary_file",
    "file_count",
    "files",
)
PROMPT_CONTEXT_POLICY_SYNTAX_ERROR_FIELDS = (
    "path",
    "line",
    "offset",
    "message",
)
PROMPT_CONTEXT_POLICY_METRIC_BOUND_FIELDS = (
    "metric",
    "value",
    "bounds",
    "direction",
    "normalized",
    "clamped",
)
PROMPT_CONTEXT_POLICY_CONFIGURED_STAGE_CHECK_FIELDS = (
    "name",
    "local_valid",
    "threshold",
    "threshold_passed",
    "stop_reason",
    "threshold_result_passed",
    "metric_thresholds",
    "artifact_output_checks",
)
PROMPT_CONTEXT_POLICY_STAGE_METRIC_THRESHOLD_FIELDS = (
    "metric",
    "value",
    "min",
    "max",
    "passed",
    "reason",
)
PROMPT_CONTEXT_POLICY_ARTIFACT_OUTPUT_CHECK_FIELDS = (
    "type",
    "passed",
    "reason",
    "path",
    "expected",
    "actual",
    "pattern",
    "count",
    "min",
    "present",
)
PROMPT_CONTEXT_POLICY_MALFORMED_METRIC_FIELDS = (
    "reason",
    "message",
)
PROMPT_CONTEXT_POLICY_MATERIALIZATION_ERROR_FIELDS = (
    "exception_type",
    "reason",
    "paths",
    "message",
)
PROMPT_CONTEXT_POLICY_METRIC_AGGREGATION_FIELDS = (
    "sample_count",
    "attempt_count",
    "metric_aggregation",
)
PROMPT_CONTEXT_POLICY_SYNTHETIC_METRIC_FIELDS = (
    "schema",
    "policy",
    "penalty",
    "metric_names",
)
PROMPT_CONTEXT_POLICY_VALIDATOR_BOUNDARY_FIELDS = (
    "policy",
    "execution",
    "security_sandbox",
    "container",
    "filesystem",
    "network_policy",
    "network_egress",
    "network_denial",
    "network_denial_scope",
    "secret_boundary",
    "resource_limits",
)
PROMPT_CONTEXT_POLICY_VALIDATOR_RESOURCE_LIMIT_FIELDS = (
    "wall_clock_timeout",
    "cpu",
    "memory",
    "gpu",
    "disk",
    "process_count",
)
PROMPT_CONTEXT_POLICY_VALIDATOR_STDIN_FIELDS = (
    "policy",
    "interactive_input",
    "generated_input",
    "source",
    "chars",
    "bytes",
    "sha256",
    "text_retained",
)
PROMPT_CONTEXT_POLICY_DIAGNOSTIC_OUTPUT_FIELDS = (
    "encoding",
    "stdout_bytes",
    "stderr_bytes",
    "stdout_replacement_count",
    "stderr_replacement_count",
    "max_chars",
    "stdout_truncated",
    "stderr_truncated",
    "redacted",
)
PROMPT_CONTEXT_POLICY_TIMEOUT_CLEANUP_FIELDS = (
    "method",
    "status",
    "process_group",
    "job_object",
    "reported_child_pids",
    "error",
)

try:
    _VALIDATED_CONTEXT_POLICY_PATHS_UNSET
except NameError:
    _VALIDATED_CONTEXT_POLICY_PATHS_UNSET = object()
_MAX_DIRECT_CONTEXT_LABEL_CHARS = 1024
_PROMPT_POLICY_METRIC_LABEL_RE = re.compile(
    r"[A-Za-z_][A-Za-z0-9_.-]{0,127}"
)
_PROMPT_POLICY_FORMAT_NAME_RE = re.compile(
    r"[A-Za-z][A-Za-z0-9_-]{0,63}"
)


def _unsafe_direct_context_label_char(char: str) -> bool:
    category = unicodedata.category(char)
    return (
        ord(char) < 32
        or ord(char) == 127
        or category == "Cf"
        or category == "Cs"
        or (category == "Zs" and char != " ")
    )


def _validate_direct_context_label(label: str) -> str:
    if redact_sensitive_text(label) != label:
        raise PromptTemplateError(
            "problem.context_files path must not contain secret-like text"
        )
    if (
        not label
        or label != label.strip(" ")
        or len(label) > _MAX_DIRECT_CONTEXT_LABEL_CHARS
        or "\\" in label
        or label.startswith("/")
        or re.match(r"^[A-Za-z]:", label)
    ):
        raise PromptTemplateError(
            f"problem.context_files path must be a safe problem-relative label: {label!r}"
        )
    if unicodedata.normalize("NFC", label) != label or any(
        unicodedata.normalize("NFC", char) != char for char in label
    ):
        raise PromptTemplateError(
            "problem.context_files path must be Unicode-normalized and compatibility-stable"
        )
    normalized = unicodedata.normalize("NFC", label)
    if unicodedata.normalize("NFKC", normalized) != normalized:
        raise PromptTemplateError(
            "problem.context_files path must be Unicode-normalized and compatibility-stable"
        )
    parts = normalized.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        raise PromptTemplateError(
            f"problem.context_files path must be a safe problem-relative label: {label!r}"
        )
    if any(_unsafe_direct_context_label_char(char) for char in normalized):
        raise PromptTemplateError(
            "problem.context_files path contains unsafe control or Unicode separator characters"
        )
    return normalized


def _validate_prompt_context_source_paths(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.context_source_paths must be a list"
        )
    normalized = []
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise PromptTemplateError(
                "prompt context_policy.context_source_paths"
                f"[{index}] must be a safe problem-relative context path"
            )
        try:
            path = _validate_direct_context_label(item)
        except PromptTemplateError as exc:
            raise PromptTemplateError(
                "prompt context_policy.context_source_paths"
                f"[{index}] must be a safe problem-relative context path: {exc}"
            ) from exc
        if path not in seen:
            normalized.append(path)
            seen.add(path)
    return normalized


def _validate_prompt_context_recent_failure_required_changed_files(
    value: object,
) -> list[str]:
    try:
        return _validate_prompt_context_source_paths(value)
    except PromptTemplateError as exc:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_required_changed_files "
            "must be a list of safe problem-relative file paths"
        ) from exc


def _validate_prompt_context_recent_failure_excluded_changed_files(
    value: object,
) -> list[str]:
    try:
        return _validate_prompt_context_source_paths(value)
    except PromptTemplateError as exc:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_excluded_changed_files "
            "must be a list of safe problem-relative file paths"
        ) from exc


def _validated_context_policy_paths(
    raw_value: object,
    validated_value: object,
    field: str,
) -> list[str]:
    candidate = (
        raw_value
        if validated_value is _VALIDATED_CONTEXT_POLICY_PATHS_UNSET
        else validated_value
    )
    try:
        return _validate_prompt_context_source_paths(candidate)
    except PromptTemplateError as exc:
        if field == "context_source_paths":
            raise
        raise PromptTemplateError(
            f"prompt context_policy.{field} must be a list of safe problem-relative file paths"
        ) from exc


def validate_prompt_context_policy(
    value: object | None,
    *,
    validated_context_source_paths: object = _VALIDATED_CONTEXT_POLICY_PATHS_UNSET,
    validated_recent_failure_required_changed_files: object = (
        _VALIDATED_CONTEXT_POLICY_PATHS_UNSET
    ),
    validated_recent_failure_excluded_changed_files: object = (
        _VALIDATED_CONTEXT_POLICY_PATHS_UNSET
    ),
) -> dict[str, object]:
    if value is None:
        value = {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError("prompt context_policy must be a mapping")
    supported = {
        "schema",
        "disabled_sections",
        "section_priorities",
        "mutation_instruction_variant",
        "mutation_instruction_include_example",
        "proposal_metadata_enabled",
        "parent_metric_names",
        "parent_metrics_max_chars_by_name",
        "parent_code_paths",
        "parent_code_required_terms",
        "parent_code_excluded_terms",
        "parent_code_ranking_terms",
        "parent_code_order_policy",
        "parent_code_limit",
        "parent_code_max_chars_by_path",
        "parent_code_max_chars",
        "parent_code_truncation",
        "inspiration_strategy",
        "inspiration_required_metric",
        "inspiration_excluded_metrics",
        "inspiration_fitness_threshold",
        "inspiration_metric_thresholds",
        "inspiration_metric_ranking",
        "feedback_sections",
        "feedback_section_order",
        "feedback_section_max_chars_by_name",
        "llm_feedback_fields",
        "llm_feedback_max_chars_by_field",
        "proposal_fields",
        "proposal_max_chars_by_field",
        "stage_summary_fields",
        "stage_summary_max_chars_by_field",
        "execution_output_fields",
        "execution_output_max_chars_by_field",
        "sample_retry_fields",
        "sample_retry_max_chars_by_field",
        "program_output_fields",
        "program_output_max_chars_by_field",
        "validator_artifact_fields",
        "validator_artifact_max_chars_by_field",
        "validator_artifact_content_fields",
        "validator_artifact_content_mode",
        "validator_artifact_content_max_bytes",
        "validator_artifact_content_max_chars",
        "validator_skipped_artifact_fields",
        "validator_skipped_artifact_max_chars_by_field",
        "validator_diagnostic_groups",
        "validator_metadata_keys",
        "validator_metadata_limit",
        "validator_metadata_max_chars_by_key",
        "evaluator_path_fields",
        "evaluator_path_max_chars_by_field",
        "evaluator_dependency_fields",
        "evaluator_dependency_max_chars_by_field",
        "evaluator_stage_fields",
        "evaluator_stage_max_chars_by_field",
        "evaluator_workspace_fields",
        "evaluator_workspace_max_chars_by_field",
        "syntax_error_fields",
        "syntax_error_max_chars_by_field",
        "metric_bound_fields",
        "metric_bound_max_chars_by_field",
        "configured_stage_check_fields",
        "configured_stage_check_max_chars_by_field",
        "stage_metric_threshold_fields",
        "stage_metric_threshold_max_chars_by_field",
        "artifact_output_check_fields",
        "artifact_output_check_max_chars_by_field",
        "malformed_metric_fields",
        "malformed_metric_max_chars_by_field",
        "materialization_error_fields",
        "materialization_error_max_chars_by_field",
        "metric_aggregation_fields",
        "metric_aggregation_max_chars_by_field",
        "synthetic_metric_fields",
        "synthetic_metric_max_chars_by_field",
        "execution_diagnostic_groups",
        "validator_boundary_fields",
        "validator_boundary_max_chars_by_field",
        "validator_budget_fields",
        "validator_budget_max_chars_by_field",
        "validator_env_fields",
        "validator_env_max_chars_by_field",
        "validator_resource_limit_fields",
        "validator_resource_limit_max_chars_by_field",
        "validator_stdin_fields",
        "validator_stdin_max_chars_by_field",
        "diagnostic_output_fields",
        "diagnostic_output_max_chars_by_field",
        "timeout_cleanup_fields",
        "timeout_cleanup_max_chars_by_field",
        "prompt_format_weights",
        "context_source_paths",
        "context_source_required_terms",
        "context_source_excluded_terms",
        "context_source_ranking_terms",
        "context_source_limit",
        "context_source_max_chars",
        "context_source_truncation",
        "context_source_order_policy",
        "recent_failure_limit",
        "recent_failure_selection_policy",
        "recent_failure_required_errors",
        "recent_failure_excluded_errors",
        "recent_failure_required_changed_files",
        "recent_failure_excluded_changed_files",
        "recent_failure_required_stage_names",
        "recent_failure_excluded_stage_names",
        "recent_failure_required_terms",
        "recent_failure_excluded_terms",
        "recent_failure_repetition_threshold",
        "recent_failure_score_threshold",
        "recent_failure_max_chars_by_field",
        "inspiration_limit",
        "inspiration_sample_count",
        "extra_context_max_chars",
    }
    unsupported = sorted(
        str(key)
        for key in value
        if key not in supported
    )
    if unsupported:
        raise PromptTemplateError(
            f"prompt context_policy has unsupported fields {unsupported}"
        )
    schema = value.get("schema", PROMPT_CONTEXT_POLICY_SCHEMA)
    if schema != PROMPT_CONTEXT_POLICY_SCHEMA:
        raise PromptTemplateError(
            "prompt context_policy.schema must be "
            f"{PROMPT_CONTEXT_POLICY_SCHEMA!r}"
        )
    disabled_sections = _validate_prompt_context_disabled_sections(
        value.get("disabled_sections", [])
    )
    section_priorities = _validate_prompt_context_section_priorities(
        value.get("section_priorities", {})
    )
    mutation_instruction_variant = _validate_prompt_context_mutation_instruction_variant(
        value.get("mutation_instruction_variant", "default")
    )
    mutation_instruction_include_example = (
        _validate_prompt_context_mutation_instruction_include_example(
            value.get("mutation_instruction_include_example", True)
        )
    )
    proposal_metadata_enabled = _validate_prompt_context_proposal_metadata_enabled(
        value.get("proposal_metadata_enabled")
    )
    parent_metric_names = _validate_prompt_context_parent_metric_names(
        value.get("parent_metric_names")
    )
    parent_metrics_max_chars_by_name = (
        _validate_prompt_context_parent_metrics_max_chars_by_name(
            value.get("parent_metrics_max_chars_by_name")
        )
    )
    parent_code_paths = _validate_prompt_context_parent_code_paths(
        value.get("parent_code_paths")
    )
    parent_code_required_terms = _validate_prompt_context_source_terms(
        value.get("parent_code_required_terms"),
        "parent_code_required_terms",
    )
    parent_code_excluded_terms = _validate_prompt_context_source_terms(
        value.get("parent_code_excluded_terms"),
        "parent_code_excluded_terms",
    )
    parent_code_ranking_terms = _validate_prompt_context_source_terms(
        value.get("parent_code_ranking_terms"),
        "parent_code_ranking_terms",
    )
    parent_code_order_policy = _validate_prompt_context_parent_code_order_policy(
        value.get("parent_code_order_policy", "path_order")
    )
    parent_code_limit = _validate_prompt_context_parent_code_limit(
        value.get("parent_code_limit")
    )
    parent_code_max_chars_by_path = _validate_prompt_context_parent_code_max_chars_by_path(
        value.get("parent_code_max_chars_by_path")
    )
    parent_code_max_chars = _validate_prompt_context_parent_code_max_chars(
        value.get("parent_code_max_chars")
    )
    parent_code_truncation = _validate_prompt_context_parent_code_truncation(
        value.get("parent_code_truncation", "head")
    )
    inspiration_strategy = _validate_prompt_context_inspiration_strategy(
        value.get("inspiration_strategy")
    )
    inspiration_required_metric = _validate_prompt_context_inspiration_required_metric(
        value.get("inspiration_required_metric")
    )
    inspiration_excluded_metrics = (
        _validate_prompt_context_inspiration_excluded_metrics(
            value.get("inspiration_excluded_metrics")
        )
    )
    inspiration_fitness_threshold = (
        _validate_prompt_context_inspiration_fitness_threshold(
            value.get("inspiration_fitness_threshold")
        )
    )
    inspiration_metric_thresholds = (
        _validate_prompt_context_inspiration_metric_thresholds(
            value.get("inspiration_metric_thresholds", {})
        )
    )
    inspiration_metric_ranking = _validate_prompt_context_inspiration_metric_ranking(
        value.get("inspiration_metric_ranking")
    )
    feedback_sections = _validate_prompt_context_feedback_sections(
        value.get("feedback_sections")
    )
    feedback_section_order = _validate_prompt_context_feedback_section_order(
        value.get("feedback_section_order")
    )
    feedback_section_max_chars_by_name = (
        _validate_prompt_context_feedback_section_max_chars_by_name(
            value.get("feedback_section_max_chars_by_name")
        )
    )
    llm_feedback_fields = _validate_prompt_context_llm_feedback_fields(
        value.get("llm_feedback_fields")
    )
    llm_feedback_max_chars_by_field = (
        _validate_prompt_context_llm_feedback_max_chars_by_field(
            value.get("llm_feedback_max_chars_by_field")
        )
    )
    proposal_fields = _validate_prompt_context_proposal_fields(
        value.get("proposal_fields")
    )
    proposal_max_chars_by_field = _validate_prompt_context_proposal_max_chars_by_field(
        value.get("proposal_max_chars_by_field")
    )
    stage_summary_fields = _validate_prompt_context_stage_summary_fields(
        value.get("stage_summary_fields")
    )
    stage_summary_max_chars_by_field = (
        _validate_prompt_context_stage_summary_max_chars_by_field(
            value.get("stage_summary_max_chars_by_field")
        )
    )
    execution_output_fields = _validate_prompt_context_execution_output_fields(
        value.get("execution_output_fields")
    )
    execution_output_max_chars_by_field = (
        _validate_prompt_context_execution_output_max_chars_by_field(
            value.get("execution_output_max_chars_by_field")
        )
    )
    sample_retry_fields = _validate_prompt_context_sample_retry_fields(
        value.get("sample_retry_fields")
    )
    sample_retry_max_chars_by_field = (
        _validate_prompt_context_sample_retry_max_chars_by_field(
            value.get("sample_retry_max_chars_by_field")
        )
    )
    program_output_fields = _validate_prompt_context_program_output_fields(
        value.get("program_output_fields")
    )
    program_output_max_chars_by_field = (
        _validate_prompt_context_program_output_max_chars_by_field(
            value.get("program_output_max_chars_by_field")
        )
    )
    validator_artifact_fields = _validate_prompt_context_validator_artifact_fields(
        value.get("validator_artifact_fields")
    )
    validator_artifact_max_chars_by_field = (
        _validate_prompt_context_validator_artifact_max_chars_by_field(
            value.get("validator_artifact_max_chars_by_field")
        )
    )
    validator_artifact_content_fields = (
        _validate_prompt_context_validator_artifact_content_fields(
            value.get("validator_artifact_content_fields")
        )
    )
    validator_artifact_content_mode = (
        _validate_prompt_context_validator_artifact_content_mode(
            value.get("validator_artifact_content_mode")
        )
    )
    validator_artifact_content_max_bytes = (
        _validate_prompt_context_validator_artifact_content_limit(
            "validator_artifact_content_max_bytes",
            value.get("validator_artifact_content_max_bytes"),
        )
    )
    validator_artifact_content_max_chars = (
        _validate_prompt_context_validator_artifact_content_limit(
            "validator_artifact_content_max_chars",
            value.get("validator_artifact_content_max_chars"),
        )
    )
    validator_skipped_artifact_fields = (
        _validate_prompt_context_validator_skipped_artifact_fields(
            value.get("validator_skipped_artifact_fields")
        )
    )
    validator_skipped_artifact_max_chars_by_field = (
        _validate_prompt_context_validator_skipped_artifact_max_chars_by_field(
            value.get("validator_skipped_artifact_max_chars_by_field")
        )
    )
    validator_diagnostic_groups = _validate_prompt_context_validator_diagnostic_groups(
        value.get("validator_diagnostic_groups")
    )
    validator_metadata_keys = _validate_prompt_context_validator_metadata_keys(
        value.get("validator_metadata_keys")
    )
    validator_metadata_limit = _validate_prompt_context_validator_metadata_limit(
        value.get("validator_metadata_limit")
    )
    validator_metadata_max_chars_by_key = (
        _validate_prompt_context_validator_metadata_max_chars_by_key(
            value.get("validator_metadata_max_chars_by_key")
        )
    )
    evaluator_path_fields = _validate_prompt_context_evaluator_path_fields(
        value.get("evaluator_path_fields")
    )
    evaluator_path_max_chars_by_field = (
        _validate_prompt_context_evaluator_path_max_chars_by_field(
            value.get("evaluator_path_max_chars_by_field")
        )
    )
    evaluator_dependency_fields = (
        _validate_prompt_context_evaluator_dependency_fields(
            value.get("evaluator_dependency_fields")
        )
    )
    evaluator_dependency_max_chars_by_field = (
        _validate_prompt_context_evaluator_dependency_max_chars_by_field(
            value.get("evaluator_dependency_max_chars_by_field")
        )
    )
    evaluator_stage_fields = _validate_prompt_context_evaluator_stage_fields(
        value.get("evaluator_stage_fields")
    )
    evaluator_stage_max_chars_by_field = (
        _validate_prompt_context_evaluator_stage_max_chars_by_field(
            value.get("evaluator_stage_max_chars_by_field")
        )
    )
    evaluator_workspace_fields = (
        _validate_prompt_context_evaluator_workspace_fields(
            value.get("evaluator_workspace_fields")
        )
    )
    evaluator_workspace_max_chars_by_field = (
        _validate_prompt_context_evaluator_workspace_max_chars_by_field(
            value.get("evaluator_workspace_max_chars_by_field")
        )
    )
    syntax_error_fields = _validate_prompt_context_syntax_error_fields(
        value.get("syntax_error_fields")
    )
    syntax_error_max_chars_by_field = (
        _validate_prompt_context_syntax_error_max_chars_by_field(
            value.get("syntax_error_max_chars_by_field")
        )
    )
    metric_bound_fields = _validate_prompt_context_metric_bound_fields(
        value.get("metric_bound_fields")
    )
    metric_bound_max_chars_by_field = (
        _validate_prompt_context_metric_bound_max_chars_by_field(
            value.get("metric_bound_max_chars_by_field")
        )
    )
    configured_stage_check_fields = (
        _validate_prompt_context_configured_stage_check_fields(
            value.get("configured_stage_check_fields")
        )
    )
    configured_stage_check_max_chars_by_field = (
        _validate_prompt_context_configured_stage_check_max_chars_by_field(
            value.get("configured_stage_check_max_chars_by_field")
        )
    )
    stage_metric_threshold_fields = (
        _validate_prompt_context_stage_metric_threshold_fields(
            value.get("stage_metric_threshold_fields")
        )
    )
    stage_metric_threshold_max_chars_by_field = (
        _validate_prompt_context_stage_metric_threshold_max_chars_by_field(
            value.get("stage_metric_threshold_max_chars_by_field")
        )
    )
    artifact_output_check_fields = (
        _validate_prompt_context_artifact_output_check_fields(
            value.get("artifact_output_check_fields")
        )
    )
    artifact_output_check_max_chars_by_field = (
        _validate_prompt_context_artifact_output_check_max_chars_by_field(
            value.get("artifact_output_check_max_chars_by_field")
        )
    )
    malformed_metric_fields = _validate_prompt_context_malformed_metric_fields(
        value.get("malformed_metric_fields")
    )
    malformed_metric_max_chars_by_field = (
        _validate_prompt_context_malformed_metric_max_chars_by_field(
            value.get("malformed_metric_max_chars_by_field")
        )
    )
    materialization_error_fields = (
        _validate_prompt_context_materialization_error_fields(
            value.get("materialization_error_fields")
        )
    )
    materialization_error_max_chars_by_field = (
        _validate_prompt_context_materialization_error_max_chars_by_field(
            value.get("materialization_error_max_chars_by_field")
        )
    )
    metric_aggregation_fields = (
        _validate_prompt_context_metric_aggregation_fields(
            value.get("metric_aggregation_fields")
        )
    )
    metric_aggregation_max_chars_by_field = (
        _validate_prompt_context_metric_aggregation_max_chars_by_field(
            value.get("metric_aggregation_max_chars_by_field")
        )
    )
    synthetic_metric_fields = _validate_prompt_context_synthetic_metric_fields(
        value.get("synthetic_metric_fields")
    )
    synthetic_metric_max_chars_by_field = (
        _validate_prompt_context_synthetic_metric_max_chars_by_field(
            value.get("synthetic_metric_max_chars_by_field")
        )
    )
    execution_diagnostic_groups = (
        _validate_prompt_context_execution_diagnostic_groups(
            value.get("execution_diagnostic_groups")
        )
    )
    validator_boundary_fields = _validate_prompt_context_validator_boundary_fields(
        value.get("validator_boundary_fields")
    )
    validator_boundary_max_chars_by_field = (
        _validate_prompt_context_validator_boundary_max_chars_by_field(
            value.get("validator_boundary_max_chars_by_field")
        )
    )
    validator_budget_fields = _validate_prompt_context_validator_budget_fields(
        value.get("validator_budget_fields")
    )
    validator_budget_max_chars_by_field = (
        _validate_prompt_context_validator_budget_max_chars_by_field(
            value.get("validator_budget_max_chars_by_field")
        )
    )
    validator_env_fields = _validate_prompt_context_validator_env_fields(
        value.get("validator_env_fields")
    )
    validator_env_max_chars_by_field = (
        _validate_prompt_context_validator_env_max_chars_by_field(
            value.get("validator_env_max_chars_by_field")
        )
    )
    validator_resource_limit_fields = (
        _validate_prompt_context_validator_resource_limit_fields(
            value.get("validator_resource_limit_fields")
        )
    )
    validator_resource_limit_max_chars_by_field = (
        _validate_prompt_context_validator_resource_limit_max_chars_by_field(
            value.get("validator_resource_limit_max_chars_by_field")
        )
    )
    validator_stdin_fields = _validate_prompt_context_validator_stdin_fields(
        value.get("validator_stdin_fields")
    )
    validator_stdin_max_chars_by_field = (
        _validate_prompt_context_validator_stdin_max_chars_by_field(
            value.get("validator_stdin_max_chars_by_field")
        )
    )
    diagnostic_output_fields = _validate_prompt_context_diagnostic_output_fields(
        value.get("diagnostic_output_fields")
    )
    diagnostic_output_max_chars_by_field = (
        _validate_prompt_context_diagnostic_output_max_chars_by_field(
            value.get("diagnostic_output_max_chars_by_field")
        )
    )
    timeout_cleanup_fields = _validate_prompt_context_timeout_cleanup_fields(
        value.get("timeout_cleanup_fields")
    )
    timeout_cleanup_max_chars_by_field = (
        _validate_prompt_context_timeout_cleanup_max_chars_by_field(
            value.get("timeout_cleanup_max_chars_by_field")
        )
    )
    prompt_format_weights = _validate_prompt_context_prompt_format_weights(
        value.get("prompt_format_weights", {})
    )
    context_source_paths = _validated_context_policy_paths(
        value.get("context_source_paths"),
        validated_context_source_paths,
        "context_source_paths",
    )
    context_source_required_terms = _validate_prompt_context_source_terms(
        value.get("context_source_required_terms"),
        "context_source_required_terms",
    )
    context_source_excluded_terms = _validate_prompt_context_source_terms(
        value.get("context_source_excluded_terms"),
        "context_source_excluded_terms",
    )
    context_source_ranking_terms = _validate_prompt_context_source_terms(
        value.get("context_source_ranking_terms"),
        "context_source_ranking_terms",
    )
    context_source_limit = _validate_prompt_context_source_limit(
        value.get("context_source_limit")
    )
    context_source_max_chars = _validate_prompt_context_source_max_chars(
        value.get("context_source_max_chars")
    )
    context_source_truncation = _validate_prompt_context_source_truncation(
        value.get("context_source_truncation", "head")
    )
    context_source_order_policy = _validate_prompt_context_source_order_policy(
        value.get("context_source_order_policy", "path_order")
    )
    recent_failure_limit = _validate_prompt_context_recent_failure_limit(
        value.get("recent_failure_limit")
    )
    recent_failure_selection_policy = (
        _validate_prompt_context_recent_failure_selection_policy(
            value.get("recent_failure_selection_policy", "recent")
        )
    )
    recent_failure_required_errors = (
        _validate_prompt_context_recent_failure_required_errors(
            value.get("recent_failure_required_errors")
        )
    )
    recent_failure_excluded_errors = (
        _validate_prompt_context_recent_failure_excluded_errors(
            value.get("recent_failure_excluded_errors")
        )
    )
    recent_failure_required_changed_files = _validated_context_policy_paths(
        value.get("recent_failure_required_changed_files"),
        validated_recent_failure_required_changed_files,
        "recent_failure_required_changed_files",
    )
    recent_failure_excluded_changed_files = _validated_context_policy_paths(
        value.get("recent_failure_excluded_changed_files"),
        validated_recent_failure_excluded_changed_files,
        "recent_failure_excluded_changed_files",
    )
    recent_failure_required_stage_names = (
        _validate_prompt_context_recent_failure_required_stage_names(
            value.get("recent_failure_required_stage_names")
        )
    )
    recent_failure_excluded_stage_names = (
        _validate_prompt_context_recent_failure_excluded_stage_names(
            value.get("recent_failure_excluded_stage_names")
        )
    )
    recent_failure_required_terms = _validate_prompt_context_source_terms(
        value.get("recent_failure_required_terms"),
        "recent_failure_required_terms",
    )
    recent_failure_excluded_terms = _validate_prompt_context_source_terms(
        value.get("recent_failure_excluded_terms"),
        "recent_failure_excluded_terms",
    )
    recent_failure_repetition_threshold = (
        _validate_prompt_context_recent_failure_repetition_threshold(
            value.get("recent_failure_repetition_threshold")
        )
    )
    recent_failure_score_threshold = (
        _validate_prompt_context_recent_failure_score_threshold(
            value.get("recent_failure_score_threshold")
        )
    )
    recent_failure_max_chars_by_field = (
        _validate_prompt_context_recent_failure_max_chars_by_field(
            value.get("recent_failure_max_chars_by_field")
        )
    )
    inspiration_limit = _validate_prompt_context_inspiration_limit(
        value.get("inspiration_limit")
    )
    inspiration_sample_count = _validate_prompt_context_inspiration_sample_count(
        value.get("inspiration_sample_count")
    )
    extra_context_max_chars = _validate_prompt_context_extra_context_max_chars(
        value.get("extra_context_max_chars")
    )
    return {
        "schema": PROMPT_CONTEXT_POLICY_SCHEMA,
        "disabled_sections": disabled_sections,
        "section_priorities": section_priorities,
        "mutation_instruction_variant": mutation_instruction_variant,
        "mutation_instruction_include_example": mutation_instruction_include_example,
        "proposal_metadata_enabled": proposal_metadata_enabled,
        "parent_metric_names": parent_metric_names,
        "parent_metrics_max_chars_by_name": parent_metrics_max_chars_by_name,
        "parent_code_paths": parent_code_paths,
        "parent_code_required_terms": parent_code_required_terms,
        "parent_code_excluded_terms": parent_code_excluded_terms,
        "parent_code_ranking_terms": parent_code_ranking_terms,
        "parent_code_order_policy": parent_code_order_policy,
        "parent_code_limit": parent_code_limit,
        "parent_code_max_chars_by_path": parent_code_max_chars_by_path,
        "parent_code_max_chars": parent_code_max_chars,
        "parent_code_truncation": parent_code_truncation,
        "inspiration_strategy": inspiration_strategy,
        "inspiration_required_metric": inspiration_required_metric,
        "inspiration_excluded_metrics": inspiration_excluded_metrics,
        "inspiration_fitness_threshold": inspiration_fitness_threshold,
        "inspiration_metric_thresholds": inspiration_metric_thresholds,
        "inspiration_metric_ranking": inspiration_metric_ranking,
        "feedback_sections": feedback_sections,
        "feedback_section_order": feedback_section_order,
        "feedback_section_max_chars_by_name": feedback_section_max_chars_by_name,
        "llm_feedback_fields": llm_feedback_fields,
        "llm_feedback_max_chars_by_field": llm_feedback_max_chars_by_field,
        "proposal_fields": proposal_fields,
        "proposal_max_chars_by_field": proposal_max_chars_by_field,
        "stage_summary_fields": stage_summary_fields,
        "stage_summary_max_chars_by_field": stage_summary_max_chars_by_field,
        "execution_output_fields": execution_output_fields,
        "execution_output_max_chars_by_field": execution_output_max_chars_by_field,
        "sample_retry_fields": sample_retry_fields,
        "sample_retry_max_chars_by_field": sample_retry_max_chars_by_field,
        "program_output_fields": program_output_fields,
        "program_output_max_chars_by_field": program_output_max_chars_by_field,
        "validator_artifact_fields": validator_artifact_fields,
        "validator_artifact_max_chars_by_field": validator_artifact_max_chars_by_field,
        "validator_artifact_content_fields": validator_artifact_content_fields,
        "validator_artifact_content_mode": validator_artifact_content_mode,
        "validator_artifact_content_max_bytes": validator_artifact_content_max_bytes,
        "validator_artifact_content_max_chars": validator_artifact_content_max_chars,
        "validator_skipped_artifact_fields": validator_skipped_artifact_fields,
        "validator_skipped_artifact_max_chars_by_field": (
            validator_skipped_artifact_max_chars_by_field
        ),
        "validator_diagnostic_groups": validator_diagnostic_groups,
        "validator_metadata_keys": validator_metadata_keys,
        "validator_metadata_limit": validator_metadata_limit,
        "validator_metadata_max_chars_by_key": validator_metadata_max_chars_by_key,
        "evaluator_path_fields": evaluator_path_fields,
        "evaluator_path_max_chars_by_field": evaluator_path_max_chars_by_field,
        "evaluator_dependency_fields": evaluator_dependency_fields,
        "evaluator_dependency_max_chars_by_field": (
            evaluator_dependency_max_chars_by_field
        ),
        "evaluator_stage_fields": evaluator_stage_fields,
        "evaluator_stage_max_chars_by_field": evaluator_stage_max_chars_by_field,
        "evaluator_workspace_fields": evaluator_workspace_fields,
        "evaluator_workspace_max_chars_by_field": (
            evaluator_workspace_max_chars_by_field
        ),
        "syntax_error_fields": syntax_error_fields,
        "syntax_error_max_chars_by_field": syntax_error_max_chars_by_field,
        "metric_bound_fields": metric_bound_fields,
        "metric_bound_max_chars_by_field": metric_bound_max_chars_by_field,
        "configured_stage_check_fields": configured_stage_check_fields,
        "configured_stage_check_max_chars_by_field": (
            configured_stage_check_max_chars_by_field
        ),
        "stage_metric_threshold_fields": stage_metric_threshold_fields,
        "stage_metric_threshold_max_chars_by_field": (
            stage_metric_threshold_max_chars_by_field
        ),
        "artifact_output_check_fields": artifact_output_check_fields,
        "artifact_output_check_max_chars_by_field": (
            artifact_output_check_max_chars_by_field
        ),
        "malformed_metric_fields": malformed_metric_fields,
        "malformed_metric_max_chars_by_field": malformed_metric_max_chars_by_field,
        "materialization_error_fields": materialization_error_fields,
        "materialization_error_max_chars_by_field": (
            materialization_error_max_chars_by_field
        ),
        "metric_aggregation_fields": metric_aggregation_fields,
        "metric_aggregation_max_chars_by_field": (
            metric_aggregation_max_chars_by_field
        ),
        "synthetic_metric_fields": synthetic_metric_fields,
        "synthetic_metric_max_chars_by_field": synthetic_metric_max_chars_by_field,
        "execution_diagnostic_groups": execution_diagnostic_groups,
        "validator_boundary_fields": validator_boundary_fields,
        "validator_boundary_max_chars_by_field": validator_boundary_max_chars_by_field,
        "validator_budget_fields": validator_budget_fields,
        "validator_budget_max_chars_by_field": validator_budget_max_chars_by_field,
        "validator_env_fields": validator_env_fields,
        "validator_env_max_chars_by_field": validator_env_max_chars_by_field,
        "validator_resource_limit_fields": validator_resource_limit_fields,
        "validator_resource_limit_max_chars_by_field": (
            validator_resource_limit_max_chars_by_field
        ),
        "validator_stdin_fields": validator_stdin_fields,
        "validator_stdin_max_chars_by_field": validator_stdin_max_chars_by_field,
        "diagnostic_output_fields": diagnostic_output_fields,
        "diagnostic_output_max_chars_by_field": diagnostic_output_max_chars_by_field,
        "timeout_cleanup_fields": timeout_cleanup_fields,
        "timeout_cleanup_max_chars_by_field": timeout_cleanup_max_chars_by_field,
        "prompt_format_weights": prompt_format_weights,
        "context_source_paths": context_source_paths,
        "context_source_required_terms": context_source_required_terms,
        "context_source_excluded_terms": context_source_excluded_terms,
        "context_source_ranking_terms": context_source_ranking_terms,
        "context_source_limit": context_source_limit,
        "context_source_max_chars": context_source_max_chars,
        "context_source_truncation": context_source_truncation,
        "context_source_order_policy": context_source_order_policy,
        "recent_failure_limit": recent_failure_limit,
        "recent_failure_selection_policy": recent_failure_selection_policy,
        "recent_failure_required_errors": recent_failure_required_errors,
        "recent_failure_excluded_errors": recent_failure_excluded_errors,
        "recent_failure_required_changed_files": recent_failure_required_changed_files,
        "recent_failure_excluded_changed_files": recent_failure_excluded_changed_files,
        "recent_failure_required_stage_names": recent_failure_required_stage_names,
        "recent_failure_excluded_stage_names": recent_failure_excluded_stage_names,
        "recent_failure_required_terms": recent_failure_required_terms,
        "recent_failure_excluded_terms": recent_failure_excluded_terms,
        "recent_failure_repetition_threshold": recent_failure_repetition_threshold,
        "recent_failure_score_threshold": recent_failure_score_threshold,
        "recent_failure_max_chars_by_field": recent_failure_max_chars_by_field,
        "inspiration_limit": inspiration_limit,
        "inspiration_sample_count": inspiration_sample_count,
        "extra_context_max_chars": extra_context_max_chars,
    }


def _validate_prompt_context_disabled_sections(value: object) -> list[str]:
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.disabled_sections must be a list"
        )
    normalized = []
    seen = set()
    for index, item in enumerate(value):
        if (
            not isinstance(item, str)
            or item not in PROMPT_CONTEXT_POLICY_DISABLED_SECTIONS
        ):
            allowed = ", ".join(sorted(PROMPT_CONTEXT_POLICY_DISABLED_SECTIONS))
            raise PromptTemplateError(
                "prompt context_policy.disabled_sections"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_section_priorities(value: object) -> dict[str, int]:
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.section_priorities must be a mapping"
        )
    normalized = {}
    for raw_name, raw_priority in value.items():
        if (
            not isinstance(raw_name, str)
            or raw_name not in _PROMPT_POLICY_TEMPLATE_FIELDS
        ):
            allowed = ", ".join(sorted(_PROMPT_POLICY_TEMPLATE_FIELDS))
            raise PromptTemplateError(
                "prompt context_policy.section_priorities keys must be "
                f"one of: {allowed}"
            )
        if (
            isinstance(raw_priority, bool)
            or not isinstance(raw_priority, int)
            or raw_priority < 0
            or raw_priority > 999
        ):
            raise PromptTemplateError(
                "prompt context_policy.section_priorities"
                f"[{raw_name!r}] must be an integer between 0 and 999"
            )
        normalized[raw_name] = raw_priority
    return normalized


def _validate_prompt_context_mutation_instruction_variant(value: object) -> str:
    if (
        not isinstance(value, str)
        or value not in PROMPT_CONTEXT_POLICY_MUTATION_INSTRUCTION_VARIANTS
    ):
        allowed = ", ".join(
            sorted(PROMPT_CONTEXT_POLICY_MUTATION_INSTRUCTION_VARIANTS)
        )
        raise PromptTemplateError(
            "prompt context_policy.mutation_instruction_variant "
            f"must be one of: {allowed}"
        )
    return value


def _validate_prompt_context_mutation_instruction_include_example(
    value: object,
) -> bool:
    if not isinstance(value, bool):
        raise PromptTemplateError(
            "prompt context_policy.mutation_instruction_include_example "
            "must be boolean"
        )
    return value


def _validate_prompt_context_proposal_metadata_enabled(
    value: object,
) -> bool | None:
    if value is None:
        return None
    if not isinstance(value, bool):
        raise PromptTemplateError(
            "prompt context_policy.proposal_metadata_enabled "
            "must be boolean or null"
        )
    return value


def _validate_prompt_context_parent_metric_names(value: object) -> list[str] | None:
    if value is None:
        return None
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.parent_metric_names must be a list or null"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if (
            not isinstance(item, str)
            or not _PROMPT_POLICY_METRIC_LABEL_RE.fullmatch(item)
        ):
            raise PromptTemplateError(
                "prompt context_policy.parent_metric_names"
                f"[{index}] must match [A-Za-z_][A-Za-z0-9_.-]{{0,127}}"
            )
        if redact_sensitive_text(item) != item:
            raise PromptTemplateError(
                "prompt context_policy.parent_metric_names"
                f"[{index}] must not look secret-like"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_parent_metrics_max_chars_by_name(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.parent_metrics_max_chars_by_name must be a mapping"
        )
    normalized: dict[str, int] = {}
    for raw_name, raw_limit in value.items():
        if (
            not isinstance(raw_name, str)
            or not _PROMPT_POLICY_METRIC_LABEL_RE.fullmatch(raw_name)
        ):
            raise PromptTemplateError(
                "prompt context_policy.parent_metrics_max_chars_by_name "
                "keys must be manifest-safe metric labels"
            )
        if redact_sensitive_text(raw_name) != raw_name:
            raise PromptTemplateError(
                "prompt context_policy.parent_metrics_max_chars_by_name "
                "keys must not look secret-like"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.parent_metrics_max_chars_by_name"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_parent_code_paths(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.parent_code_paths must be a list"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise PromptTemplateError(
                "prompt context_policy.parent_code_paths"
                f"[{index}] must be a safe candidate-relative file path"
            )
        try:
            path = normalize_candidate_path(item)
        except ValueError as exc:
            raise PromptTemplateError(
                "prompt context_policy.parent_code_paths"
                f"[{index}] must be a safe candidate-relative file path: {exc}"
            ) from exc
        if path not in seen:
            normalized.append(path)
            seen.add(path)
    return normalized


def _validate_prompt_context_parent_code_order_policy(value: object) -> str:
    if (
        not isinstance(value, str)
        or value not in PROMPT_CONTEXT_POLICY_CONTEXT_SOURCE_ORDER_POLICIES
    ):
        allowed = ", ".join(
            sorted(PROMPT_CONTEXT_POLICY_CONTEXT_SOURCE_ORDER_POLICIES)
        )
        raise PromptTemplateError(
            "prompt context_policy.parent_code_order_policy "
            f"must be one of: {allowed}"
        )
    return value


def _validate_prompt_context_parent_code_limit(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromptTemplateError(
            "prompt context_policy.parent_code_limit "
            "must be a non-negative integer or null"
        )
    return value


def _validate_prompt_context_parent_code_max_chars_by_path(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.parent_code_max_chars_by_path must be a mapping"
        )
    normalized: dict[str, int] = {}
    for raw_path, raw_limit in value.items():
        if not isinstance(raw_path, str):
            raise PromptTemplateError(
                "prompt context_policy.parent_code_max_chars_by_path "
                "keys must be safe candidate-relative file paths"
            )
        try:
            path = normalize_candidate_path(raw_path)
        except ValueError as exc:
            raise PromptTemplateError(
                "prompt context_policy.parent_code_max_chars_by_path "
                f"keys must be safe candidate-relative file paths: {exc}"
            ) from exc
        if isinstance(raw_limit, bool) or not isinstance(raw_limit, int) or raw_limit < 0:
            raise PromptTemplateError(
                "prompt context_policy.parent_code_max_chars_by_path "
                "values must be non-negative integers"
            )
        normalized[path] = raw_limit
    return normalized


def _validate_prompt_context_parent_code_max_chars(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromptTemplateError(
            "prompt context_policy.parent_code_max_chars "
            "must be a non-negative integer or null"
        )
    return value


def _validate_prompt_context_parent_code_truncation(value: object) -> str:
    if (
        not isinstance(value, str)
        or value not in PROMPT_CONTEXT_POLICY_CONTEXT_SOURCE_TRUNCATION
    ):
        allowed = ", ".join(sorted(PROMPT_CONTEXT_POLICY_CONTEXT_SOURCE_TRUNCATION))
        raise PromptTemplateError(
            "prompt context_policy.parent_code_truncation "
            f"must be one of: {allowed}"
        )
    return value


def _validate_prompt_context_inspiration_strategy(value: object) -> str | None:
    if value is None:
        return None
    if (
        not isinstance(value, str)
        or value not in PROMPT_CONTEXT_POLICY_INSPIRATION_STRATEGIES
    ):
        allowed = ", ".join(sorted(PROMPT_CONTEXT_POLICY_INSPIRATION_STRATEGIES))
        raise PromptTemplateError(
            "prompt context_policy.inspiration_strategy "
            f"must be null or one of: {allowed}"
        )
    return value


def _validate_prompt_context_inspiration_required_metric(
    value: object,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise PromptTemplateError(
            "prompt context_policy.inspiration_required_metric "
            "must be null or a manifest-safe metric name"
        )
    try:
        validate_program_metrics({value: 0.0})
    except ValueError as exc:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_required_metric "
            "must be null or a manifest-safe metric name"
        ) from exc
    if redact_sensitive_text(value) != value:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_required_metric "
            "must not look secret-like"
        )
    return value


def _validate_prompt_context_inspiration_excluded_metrics(
    value: object,
) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.inspiration_excluded_metrics "
            "must be a list"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise PromptTemplateError(
                "prompt context_policy.inspiration_excluded_metrics"
                f"[{index}] must be a manifest-safe metric name"
            )
        try:
            validate_program_metrics({item: 0.0})
        except ValueError as exc:
            raise PromptTemplateError(
                "prompt context_policy.inspiration_excluded_metrics"
                f"[{index}] must be a manifest-safe metric name"
            ) from exc
        if redact_sensitive_text(item) != item:
            raise PromptTemplateError(
                "prompt context_policy.inspiration_excluded_metrics"
                f"[{index}] must not look secret-like"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_inspiration_fitness_threshold(
    value: object,
) -> dict[str, float | None] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.inspiration_fitness_threshold "
            "must be null or a mapping"
        )
    unsupported = sorted(str(key) for key in value if key not in {"min", "max"})
    if unsupported:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_fitness_threshold "
            f"has unsupported fields {unsupported}"
        )
    minimum = _validate_prompt_context_inspiration_fitness_bound(
        "min",
        value.get("min"),
    )
    maximum = _validate_prompt_context_inspiration_fitness_bound(
        "max",
        value.get("max"),
    )
    if minimum is None and maximum is None:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_fitness_threshold "
            "must set min or max"
        )
    if minimum is not None and maximum is not None and minimum > maximum:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_fitness_threshold min must be <= max"
        )
    return {"min": minimum, "max": maximum}


def _validate_prompt_context_inspiration_fitness_bound(
    bound_name: str,
    value: object,
) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PromptTemplateError(
            "prompt context_policy.inspiration_fitness_threshold"
            f".{bound_name} must be a finite number or null"
        )
    bound = float(value)
    if not math.isfinite(bound):
        raise PromptTemplateError(
            "prompt context_policy.inspiration_fitness_threshold"
            f".{bound_name} must be a finite number or null"
        )
    return bound


def _validate_prompt_context_inspiration_metric_thresholds(
    value: object,
) -> dict[str, dict[str, float | None]]:
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.inspiration_metric_thresholds must be a mapping"
        )
    normalized: dict[str, dict[str, float | None]] = {}
    for raw_name, raw_thresholds in value.items():
        if not isinstance(raw_name, str):
            raise PromptTemplateError(
                "prompt context_policy.inspiration_metric_thresholds keys "
                "must be manifest-safe metric names"
            )
        try:
            validate_program_metrics({raw_name: 0.0})
        except ValueError as exc:
            raise PromptTemplateError(
                "prompt context_policy.inspiration_metric_thresholds keys "
                "must be manifest-safe metric names"
            ) from exc
        if redact_sensitive_text(raw_name) != raw_name:
            raise PromptTemplateError(
                "prompt context_policy.inspiration_metric_thresholds keys "
                "must not look secret-like"
            )
        if not isinstance(raw_thresholds, Mapping):
            raise PromptTemplateError(
                "prompt context_policy.inspiration_metric_thresholds"
                f"[{raw_name!r}] must be a mapping"
            )
        unsupported = sorted(str(key) for key in raw_thresholds if key not in {"min", "max"})
        if unsupported:
            raise PromptTemplateError(
                "prompt context_policy.inspiration_metric_thresholds"
                f"[{raw_name!r}] has unsupported fields {unsupported}"
            )
        minimum = _validate_prompt_context_inspiration_metric_bound(
            raw_name,
            "min",
            raw_thresholds.get("min"),
        )
        maximum = _validate_prompt_context_inspiration_metric_bound(
            raw_name,
            "max",
            raw_thresholds.get("max"),
        )
        if minimum is None and maximum is None:
            raise PromptTemplateError(
                "prompt context_policy.inspiration_metric_thresholds"
                f"[{raw_name!r}] must set min or max"
            )
        if minimum is not None and maximum is not None and minimum > maximum:
            raise PromptTemplateError(
                "prompt context_policy.inspiration_metric_thresholds"
                f"[{raw_name!r}] min must be <= max"
            )
        normalized[raw_name] = {"min": minimum, "max": maximum}
    return normalized


def _validate_prompt_context_inspiration_metric_bound(
    metric_name: str,
    bound_name: str,
    value: object,
) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PromptTemplateError(
            "prompt context_policy.inspiration_metric_thresholds"
            f"[{metric_name!r}].{bound_name} must be a finite number or null"
        )
    bound = float(value)
    if not math.isfinite(bound):
        raise PromptTemplateError(
            "prompt context_policy.inspiration_metric_thresholds"
            f"[{metric_name!r}].{bound_name} must be a finite number or null"
        )
    return bound


def _validate_prompt_context_inspiration_metric_ranking(
    value: object,
) -> dict[str, str] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.inspiration_metric_ranking must be null or a mapping"
        )
    unsupported = sorted(
        str(key) for key in value if key not in {"metric", "direction"}
    )
    if unsupported:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_metric_ranking "
            f"has unsupported fields {unsupported}"
        )
    metric = value.get("metric")
    if not isinstance(metric, str):
        raise PromptTemplateError(
            "prompt context_policy.inspiration_metric_ranking.metric "
            "must be a manifest-safe metric name"
        )
    try:
        validate_program_metrics({metric: 0.0})
    except ValueError as exc:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_metric_ranking.metric "
            "must be a manifest-safe metric name"
        ) from exc
    if redact_sensitive_text(metric) != metric:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_metric_ranking.metric "
            "must not look secret-like"
        )
    direction = value.get("direction", "maximize")
    if direction not in {"maximize", "minimize"}:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_metric_ranking.direction "
            "must be one of: maximize, minimize"
        )
    return {"metric": metric, "direction": str(direction)}


def _validate_prompt_context_feedback_sections(value: object) -> list[str]:
    default = sorted(PROMPT_CONTEXT_POLICY_FEEDBACK_SECTIONS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.feedback_sections must be a list"
        )
    normalized = []
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in PROMPT_CONTEXT_POLICY_FEEDBACK_SECTIONS:
            allowed = ", ".join(sorted(PROMPT_CONTEXT_POLICY_FEEDBACK_SECTIONS))
            raise PromptTemplateError(
                "prompt context_policy.feedback_sections"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_feedback_section_order(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_FEEDBACK_SECTION_ORDER)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.feedback_section_order must be a list"
        )
    normalized = []
    seen = set()
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in PROMPT_CONTEXT_POLICY_FEEDBACK_SECTIONS:
            allowed = ", ".join(sorted(PROMPT_CONTEXT_POLICY_FEEDBACK_SECTIONS))
            raise PromptTemplateError(
                "prompt context_policy.feedback_section_order"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    for item in default:
        if item not in seen:
            normalized.append(item)
    return normalized


def _validate_prompt_context_feedback_section_max_chars_by_name(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.feedback_section_max_chars_by_name must be a mapping"
        )
    if len(value) > len(PROMPT_CONTEXT_POLICY_FEEDBACK_SECTIONS):
        raise PromptTemplateError(
            "prompt context_policy.feedback_section_max_chars_by_name has too many entries"
        )
    normalized: dict[str, int] = {}
    for raw_name, raw_max_chars in value.items():
        if (
            not isinstance(raw_name, str)
            or raw_name not in PROMPT_CONTEXT_POLICY_FEEDBACK_SECTIONS
        ):
            allowed = ", ".join(sorted(PROMPT_CONTEXT_POLICY_FEEDBACK_SECTIONS))
            raise PromptTemplateError(
                "prompt context_policy.feedback_section_max_chars_by_name "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_max_chars, bool)
            or not isinstance(raw_max_chars, int)
            or raw_max_chars < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.feedback_section_max_chars_by_name"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_max_chars
    return dict(sorted(normalized.items()))


def _validate_prompt_context_llm_feedback_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_LLM_FEEDBACK_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.llm_feedback_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_LLM_FEEDBACK_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_LLM_FEEDBACK_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.llm_feedback_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_llm_feedback_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.llm_feedback_max_chars_by_field must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_LLM_FEEDBACK_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_LLM_FEEDBACK_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.llm_feedback_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.llm_feedback_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_proposal_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_PROPOSAL_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.proposal_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_PROPOSAL_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_PROPOSAL_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.proposal_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_proposal_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.proposal_max_chars_by_field must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_PROPOSAL_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_PROPOSAL_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.proposal_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.proposal_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_stage_summary_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_STAGE_SUMMARY_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.stage_summary_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_STAGE_SUMMARY_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_STAGE_SUMMARY_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.stage_summary_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_stage_summary_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.stage_summary_max_chars_by_field must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_STAGE_SUMMARY_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_STAGE_SUMMARY_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.stage_summary_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.stage_summary_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_execution_output_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_EXECUTION_OUTPUT_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.execution_output_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_EXECUTION_OUTPUT_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EXECUTION_OUTPUT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.execution_output_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_execution_output_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.execution_output_max_chars_by_field must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_EXECUTION_OUTPUT_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EXECUTION_OUTPUT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.execution_output_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.execution_output_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_sample_retry_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_SAMPLE_RETRY_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.sample_retry_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_SAMPLE_RETRY_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_SAMPLE_RETRY_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.sample_retry_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_sample_retry_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.sample_retry_max_chars_by_field must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_SAMPLE_RETRY_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_SAMPLE_RETRY_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.sample_retry_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.sample_retry_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_program_output_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_PROGRAM_OUTPUT_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.program_output_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_PROGRAM_OUTPUT_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_PROGRAM_OUTPUT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.program_output_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_program_output_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.program_output_max_chars_by_field must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_PROGRAM_OUTPUT_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_PROGRAM_OUTPUT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.program_output_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.program_output_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_validator_artifact_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_VALIDATOR_ARTIFACT_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.validator_artifact_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_ARTIFACT_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_ARTIFACT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_artifact_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_artifact_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.validator_artifact_max_chars_by_field must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_ARTIFACT_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_ARTIFACT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_artifact_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.validator_artifact_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_validator_artifact_content_fields(
    value: object,
) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_VALIDATOR_ARTIFACT_CONTENT_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.validator_artifact_content_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_ARTIFACT_CONTENT_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_ARTIFACT_CONTENT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_artifact_content_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_artifact_content_mode(
    value: object,
) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or value not in _PROMPT_POLICY_ARTIFACT_CONTENT_MODES:
        allowed = ", ".join(sorted(_PROMPT_POLICY_ARTIFACT_CONTENT_MODES))
        raise PromptTemplateError(
            "prompt context_policy.validator_artifact_content_mode "
            f"must be null or one of: {allowed}"
        )
    return value


def _validate_prompt_context_validator_artifact_content_limit(
    label: str,
    value: object,
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PromptTemplateError(
            f"prompt context_policy.{label} must be null or an integer >= 1"
        )
    return value


def _validate_prompt_context_validator_skipped_artifact_fields(
    value: object,
) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_VALIDATOR_SKIPPED_ARTIFACT_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.validator_skipped_artifact_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_SKIPPED_ARTIFACT_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_SKIPPED_ARTIFACT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_skipped_artifact_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_skipped_artifact_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.validator_skipped_artifact_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_SKIPPED_ARTIFACT_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(
                PROMPT_CONTEXT_POLICY_VALIDATOR_SKIPPED_ARTIFACT_FIELDS
            )
            raise PromptTemplateError(
                "prompt context_policy.validator_skipped_artifact_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.validator_skipped_artifact_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_validator_diagnostic_groups(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_VALIDATOR_DIAGNOSTIC_GROUPS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.validator_diagnostic_groups must be a list"
        )
    normalized = []
    seen = set()
    allowed_groups = set(PROMPT_CONTEXT_POLICY_VALIDATOR_DIAGNOSTIC_GROUPS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_groups:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_DIAGNOSTIC_GROUPS)
            raise PromptTemplateError(
                "prompt context_policy.validator_diagnostic_groups"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_metadata_keys(value: object) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.validator_metadata_keys must be a list"
        )
    normalized = []
    seen = set()
    for index, item in enumerate(value):
        if (
            not isinstance(item, str)
            or not _PROMPT_POLICY_METRIC_LABEL_RE.fullmatch(item)
        ):
            raise PromptTemplateError(
                "prompt context_policy.validator_metadata_keys"
                f"[{index}] must match [A-Za-z_][A-Za-z0-9_.-]{{0,127}}"
            )
        if redact_sensitive_text(item) != item:
            raise PromptTemplateError(
                "prompt context_policy.validator_metadata_keys"
                f"[{index}] must not look secret-like"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_metadata_limit(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromptTemplateError(
            "prompt context_policy.validator_metadata_limit must be a "
            "non-negative integer or null"
        )
    return value


def _validate_prompt_context_validator_metadata_max_chars_by_key(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.validator_metadata_max_chars_by_key "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    for raw_name, raw_limit in value.items():
        if (
            not isinstance(raw_name, str)
            or not _PROMPT_POLICY_METRIC_LABEL_RE.fullmatch(raw_name)
        ):
            raise PromptTemplateError(
                "prompt context_policy.validator_metadata_max_chars_by_key "
                "keys must be manifest-safe metric labels"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.validator_metadata_max_chars_by_key"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_syntax_error_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_SYNTAX_ERROR_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.syntax_error_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_SYNTAX_ERROR_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_SYNTAX_ERROR_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.syntax_error_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_syntax_error_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.syntax_error_max_chars_by_field must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_SYNTAX_ERROR_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_SYNTAX_ERROR_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.syntax_error_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.syntax_error_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_metric_bound_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_METRIC_BOUND_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.metric_bound_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_METRIC_BOUND_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_METRIC_BOUND_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.metric_bound_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_metric_bound_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.metric_bound_max_chars_by_field must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_METRIC_BOUND_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_METRIC_BOUND_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.metric_bound_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.metric_bound_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_configured_stage_check_fields(
    value: object,
) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_CONFIGURED_STAGE_CHECK_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.configured_stage_check_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_CONFIGURED_STAGE_CHECK_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_CONFIGURED_STAGE_CHECK_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.configured_stage_check_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_configured_stage_check_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.configured_stage_check_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_CONFIGURED_STAGE_CHECK_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_CONFIGURED_STAGE_CHECK_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.configured_stage_check_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.configured_stage_check_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_stage_metric_threshold_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_STAGE_METRIC_THRESHOLD_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.stage_metric_threshold_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_STAGE_METRIC_THRESHOLD_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_STAGE_METRIC_THRESHOLD_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.stage_metric_threshold_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_stage_metric_threshold_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.stage_metric_threshold_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_STAGE_METRIC_THRESHOLD_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_STAGE_METRIC_THRESHOLD_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.stage_metric_threshold_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.stage_metric_threshold_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_artifact_output_check_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_ARTIFACT_OUTPUT_CHECK_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.artifact_output_check_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_ARTIFACT_OUTPUT_CHECK_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_ARTIFACT_OUTPUT_CHECK_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.artifact_output_check_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_artifact_output_check_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.artifact_output_check_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_ARTIFACT_OUTPUT_CHECK_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_ARTIFACT_OUTPUT_CHECK_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.artifact_output_check_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.artifact_output_check_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_malformed_metric_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_MALFORMED_METRIC_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.malformed_metric_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_MALFORMED_METRIC_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_MALFORMED_METRIC_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.malformed_metric_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_malformed_metric_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.malformed_metric_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_MALFORMED_METRIC_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_MALFORMED_METRIC_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.malformed_metric_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.malformed_metric_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_materialization_error_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_MATERIALIZATION_ERROR_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.materialization_error_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_MATERIALIZATION_ERROR_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_MATERIALIZATION_ERROR_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.materialization_error_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_materialization_error_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.materialization_error_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_MATERIALIZATION_ERROR_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_MATERIALIZATION_ERROR_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.materialization_error_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.materialization_error_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_evaluator_path_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_EVALUATOR_PATH_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.evaluator_path_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_EVALUATOR_PATH_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EVALUATOR_PATH_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.evaluator_path_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_evaluator_path_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.evaluator_path_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_EVALUATOR_PATH_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EVALUATOR_PATH_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.evaluator_path_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.evaluator_path_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_evaluator_dependency_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_EVALUATOR_DEPENDENCY_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.evaluator_dependency_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_EVALUATOR_DEPENDENCY_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EVALUATOR_DEPENDENCY_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.evaluator_dependency_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_evaluator_dependency_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.evaluator_dependency_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_EVALUATOR_DEPENDENCY_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EVALUATOR_DEPENDENCY_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.evaluator_dependency_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.evaluator_dependency_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_evaluator_stage_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_EVALUATOR_STAGE_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.evaluator_stage_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_EVALUATOR_STAGE_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EVALUATOR_STAGE_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.evaluator_stage_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_evaluator_stage_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.evaluator_stage_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_EVALUATOR_STAGE_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EVALUATOR_STAGE_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.evaluator_stage_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.evaluator_stage_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_evaluator_workspace_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_EVALUATOR_WORKSPACE_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.evaluator_workspace_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_EVALUATOR_WORKSPACE_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EVALUATOR_WORKSPACE_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.evaluator_workspace_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_evaluator_workspace_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.evaluator_workspace_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_EVALUATOR_WORKSPACE_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EVALUATOR_WORKSPACE_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.evaluator_workspace_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.evaluator_workspace_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_metric_aggregation_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_METRIC_AGGREGATION_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.metric_aggregation_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_METRIC_AGGREGATION_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_METRIC_AGGREGATION_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.metric_aggregation_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_metric_aggregation_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.metric_aggregation_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_METRIC_AGGREGATION_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_METRIC_AGGREGATION_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.metric_aggregation_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.metric_aggregation_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_synthetic_metric_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_SYNTHETIC_METRIC_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.synthetic_metric_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_SYNTHETIC_METRIC_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_SYNTHETIC_METRIC_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.synthetic_metric_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_synthetic_metric_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.synthetic_metric_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_SYNTHETIC_METRIC_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_SYNTHETIC_METRIC_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.synthetic_metric_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.synthetic_metric_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_execution_diagnostic_groups(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_EXECUTION_DIAGNOSTIC_GROUPS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.execution_diagnostic_groups must be a list"
        )
    normalized = []
    seen = set()
    allowed_groups = set(PROMPT_CONTEXT_POLICY_EXECUTION_DIAGNOSTIC_GROUPS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_groups:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_EXECUTION_DIAGNOSTIC_GROUPS)
            raise PromptTemplateError(
                "prompt context_policy.execution_diagnostic_groups"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_boundary_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_VALIDATOR_BOUNDARY_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.validator_boundary_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_BOUNDARY_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_BOUNDARY_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_boundary_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_boundary_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.validator_boundary_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_BOUNDARY_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_BOUNDARY_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_boundary_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.validator_boundary_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_validator_budget_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_VALIDATOR_BUDGET_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.validator_budget_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_BUDGET_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_BUDGET_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_budget_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_budget_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.validator_budget_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_BUDGET_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_BUDGET_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_budget_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.validator_budget_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_validator_env_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_VALIDATOR_ENV_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.validator_env_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_ENV_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_ENV_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_env_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_env_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.validator_env_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_ENV_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_ENV_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_env_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.validator_env_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_validator_resource_limit_fields(
    value: object,
) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_VALIDATOR_RESOURCE_LIMIT_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.validator_resource_limit_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_RESOURCE_LIMIT_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_RESOURCE_LIMIT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_resource_limit_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_resource_limit_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.validator_resource_limit_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_RESOURCE_LIMIT_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_RESOURCE_LIMIT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_resource_limit_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.validator_resource_limit_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_validator_stdin_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_VALIDATOR_STDIN_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.validator_stdin_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_STDIN_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_STDIN_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_stdin_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_validator_stdin_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.validator_stdin_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_VALIDATOR_STDIN_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_VALIDATOR_STDIN_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.validator_stdin_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.validator_stdin_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_diagnostic_output_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_DIAGNOSTIC_OUTPUT_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.diagnostic_output_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_DIAGNOSTIC_OUTPUT_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_DIAGNOSTIC_OUTPUT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.diagnostic_output_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_diagnostic_output_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.diagnostic_output_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_DIAGNOSTIC_OUTPUT_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_DIAGNOSTIC_OUTPUT_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.diagnostic_output_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.diagnostic_output_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_timeout_cleanup_fields(value: object) -> list[str]:
    default = list(PROMPT_CONTEXT_POLICY_TIMEOUT_CLEANUP_FIELDS)
    if value is None:
        return default
    if not isinstance(value, list):
        raise PromptTemplateError(
            "prompt context_policy.timeout_cleanup_fields must be a list"
        )
    normalized = []
    seen = set()
    allowed_fields = set(PROMPT_CONTEXT_POLICY_TIMEOUT_CLEANUP_FIELDS)
    for index, item in enumerate(value):
        if not isinstance(item, str) or item not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_TIMEOUT_CLEANUP_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.timeout_cleanup_fields"
                f"[{index}] must be one of: {allowed}"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_timeout_cleanup_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.timeout_cleanup_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_TIMEOUT_CLEANUP_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_TIMEOUT_CLEANUP_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.timeout_cleanup_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.timeout_cleanup_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_prompt_format_weights(value: object) -> dict[str, list[float]]:
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.prompt_format_weights must be a mapping"
        )
    normalized: dict[str, list[float]] = {}
    for raw_name, raw_weights in value.items():
        if (
            not isinstance(raw_name, str)
            or not _PROMPT_POLICY_FORMAT_NAME_RE.fullmatch(raw_name)
        ):
            raise PromptTemplateError(
                "prompt context_policy.prompt_format_weights keys must match "
                "[A-Za-z][A-Za-z0-9_-]{0,63}"
            )
        if redact_sensitive_text(raw_name) != raw_name:
            raise PromptTemplateError(
                "prompt context_policy.prompt_format_weights keys must not look secret-like"
            )
        if not isinstance(raw_weights, list) or not raw_weights:
            raise PromptTemplateError(
                "prompt context_policy.prompt_format_weights"
                f"[{raw_name!r}] must be a non-empty list"
            )
        weights: list[float] = []
        for index, raw_weight in enumerate(raw_weights):
            if isinstance(raw_weight, bool) or not isinstance(raw_weight, (int, float)):
                raise PromptTemplateError(
                    "prompt context_policy.prompt_format_weights"
                    f"[{raw_name!r}][{index}] must be a positive finite number"
                )
            weight = float(raw_weight)
            if not math.isfinite(weight) or weight <= 0.0:
                raise PromptTemplateError(
                    "prompt context_policy.prompt_format_weights"
                    f"[{raw_name!r}][{index}] must be a positive finite number"
                )
            weights.append(weight)
        normalized[raw_name] = weights
    return normalized


def _validate_prompt_context_source_terms(value: object, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PromptTemplateError(f"prompt context_policy.{field} must be a list")
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if (
            not isinstance(item, str)
            or redact_sensitive_text(item) != item
            or re.fullmatch(r"[A-Za-z0-9_]{3,64}", item) is None
        ):
            raise PromptTemplateError(
                f"prompt context_policy.{field}[{index}] "
                "must be a safe alphanumeric context source term"
            )
        term = item.lower()
        if term not in seen:
            normalized.append(term)
            seen.add(term)
    return normalized


def _validate_prompt_context_source_max_chars(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromptTemplateError(
            "prompt context_policy.context_source_max_chars must be a non-negative integer or null"
        )
    return value


def _validate_prompt_context_source_limit(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromptTemplateError(
            "prompt context_policy.context_source_limit must be a non-negative integer or null"
        )
    return value


def _validate_prompt_context_source_truncation(value: object) -> str:
    if (
        not isinstance(value, str)
        or value not in PROMPT_CONTEXT_POLICY_CONTEXT_SOURCE_TRUNCATION
    ):
        allowed = ", ".join(sorted(PROMPT_CONTEXT_POLICY_CONTEXT_SOURCE_TRUNCATION))
        raise PromptTemplateError(
            "prompt context_policy.context_source_truncation "
            f"must be one of: {allowed}"
        )
    return value


def _validate_prompt_context_source_order_policy(value: object) -> str:
    if (
        not isinstance(value, str)
        or value not in PROMPT_CONTEXT_POLICY_CONTEXT_SOURCE_ORDER_POLICIES
    ):
        allowed = ", ".join(
            sorted(PROMPT_CONTEXT_POLICY_CONTEXT_SOURCE_ORDER_POLICIES)
        )
        raise PromptTemplateError(
            "prompt context_policy.context_source_order_policy "
            f"must be one of: {allowed}"
        )
    return value


def _validate_prompt_context_recent_failure_limit(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_limit must be a non-negative integer or null"
        )
    return value


def _validate_prompt_context_recent_failure_selection_policy(value: object) -> str:
    allowed = {"recent", "oldest", "lowest_score", "highest_repetition"}
    if not isinstance(value, str) or value not in allowed:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_selection_policy "
            f"must be one of: {', '.join(sorted(allowed))}"
        )
    return value


def _validate_prompt_context_recent_failure_required_errors(
    value: object,
) -> list[str]:
    return _validate_prompt_context_recent_failure_error_list(
        value, "recent_failure_required_errors"
    )


def _validate_prompt_context_recent_failure_excluded_errors(
    value: object,
) -> list[str]:
    return _validate_prompt_context_recent_failure_error_list(
        value, "recent_failure_excluded_errors"
    )


def _validate_prompt_context_recent_failure_error_list(
    value: object,
    field: str,
) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PromptTemplateError(
            f"prompt context_policy.{field} must be a list"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if not isinstance(item, str):
            raise PromptTemplateError(
                f"prompt context_policy.{field}[{index}] "
                "must be a manifest-safe error label"
            )
        try:
            validate_program_metrics({item: 0.0})
        except ValueError as exc:
            raise PromptTemplateError(
                f"prompt context_policy.{field}[{index}] "
                "must be a manifest-safe error label"
            ) from exc
        if redact_sensitive_text(item) != item:
            raise PromptTemplateError(
                f"prompt context_policy.{field}[{index}] "
                "must not look secret-like"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_recent_failure_required_stage_names(
    value: object,
) -> list[str]:
    return _validate_prompt_context_recent_failure_stage_name_list(
        value, "recent_failure_required_stage_names"
    )


def _validate_prompt_context_recent_failure_excluded_stage_names(
    value: object,
) -> list[str]:
    return _validate_prompt_context_recent_failure_stage_name_list(
        value, "recent_failure_excluded_stage_names"
    )


def _validate_prompt_context_recent_failure_stage_name_list(
    value: object,
    field: str,
) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise PromptTemplateError(
            f"prompt context_policy.{field} must be a list"
        )
    normalized: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        if (
            not isinstance(item, str)
            or redact_sensitive_text(item) != item
            or re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:\-\[\]]{0,191}", item)
            is None
        ):
            raise PromptTemplateError(
                f"prompt context_policy.{field}[{index}] "
                "must be a manifest-safe stage label"
            )
        if item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def _validate_prompt_context_recent_failure_repetition_threshold(
    value: object,
) -> dict[str, int | None] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_repetition_threshold "
            "must be null or a mapping"
        )
    unsupported = sorted(str(key) for key in value if key not in {"min", "max"})
    if unsupported:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_repetition_threshold "
            f"has unsupported fields {unsupported}"
        )
    minimum = _validate_prompt_context_recent_failure_repetition_bound(
        value.get("min"), "min"
    )
    maximum = _validate_prompt_context_recent_failure_repetition_bound(
        value.get("max"), "max"
    )
    if minimum is None and maximum is None:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_repetition_threshold "
            "must set min or max"
        )
    if minimum is not None and maximum is not None and minimum > maximum:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_repetition_threshold min must be <= max"
        )
    return {"min": minimum, "max": maximum}


def _validate_prompt_context_recent_failure_repetition_bound(
    value: object,
    name: str,
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_repetition_threshold"
            f".{name} must be an integer >= 1 or null"
        )
    return value


def _validate_prompt_context_recent_failure_score_threshold(
    value: object,
) -> dict[str, float | None] | None:
    if value is None:
        return None
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_score_threshold "
            "must be null or a mapping"
        )
    unsupported = sorted(str(key) for key in value if key not in {"min", "max"})
    if unsupported:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_score_threshold "
            f"has unsupported fields {unsupported}"
        )
    minimum = _validate_prompt_context_recent_failure_score_bound(
        value.get("min"), "min"
    )
    maximum = _validate_prompt_context_recent_failure_score_bound(
        value.get("max"), "max"
    )
    if minimum is None and maximum is None:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_score_threshold "
            "must set min or max"
        )
    if minimum is not None and maximum is not None and minimum > maximum:
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_score_threshold min must be <= max"
        )
    return {"min": minimum, "max": maximum}


def _validate_prompt_context_recent_failure_score_bound(
    value: object,
    name: str,
) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_score_threshold"
            f".{name} must be a finite number or null"
        )
    numeric = float(value)
    if not math.isfinite(numeric):
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_score_threshold"
            f".{name} must be finite"
        )
    return numeric


def _validate_prompt_context_recent_failure_max_chars_by_field(
    value: object,
) -> dict[str, int]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError(
            "prompt context_policy.recent_failure_max_chars_by_field "
            "must be a mapping"
        )
    normalized: dict[str, int] = {}
    allowed_fields = set(PROMPT_CONTEXT_POLICY_RECENT_FAILURE_FIELDS)
    for raw_name, raw_limit in value.items():
        if not isinstance(raw_name, str) or raw_name not in allowed_fields:
            allowed = ", ".join(PROMPT_CONTEXT_POLICY_RECENT_FAILURE_FIELDS)
            raise PromptTemplateError(
                "prompt context_policy.recent_failure_max_chars_by_field "
                f"keys must be one of: {allowed}"
            )
        if (
            isinstance(raw_limit, bool)
            or not isinstance(raw_limit, int)
            or raw_limit < 0
        ):
            raise PromptTemplateError(
                "prompt context_policy.recent_failure_max_chars_by_field"
                f"[{raw_name!r}] must be a non-negative integer"
            )
        normalized[raw_name] = raw_limit
    return normalized


def _validate_prompt_context_inspiration_limit(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_limit must be a non-negative integer or null"
        )
    return value


def _validate_prompt_context_inspiration_sample_count(
    value: object,
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromptTemplateError(
            "prompt context_policy.inspiration_sample_count must be a non-negative integer or null"
        )
    return value


def _validate_prompt_context_extra_context_max_chars(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromptTemplateError(
            "prompt context_policy.extra_context_max_chars must be a non-negative integer or null"
        )
    return value

__all__ = [
    "PromptTemplateError",
    "validate_prompt_context_policy",
    "_validate_direct_context_label",
    "_unsafe_direct_context_label_char",
    *sorted(name for name in globals() if name.startswith("_validate_prompt_context_")),
    *sorted(name for name in globals() if name.startswith("PROMPT_CONTEXT_POLICY_")),
]
