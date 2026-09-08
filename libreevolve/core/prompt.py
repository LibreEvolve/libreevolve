from __future__ import annotations

import hashlib
import json
import math
import random
import re
import string
import unicodedata
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
from pathlib import Path

from libreevolve.core.candidate import MUTATION_MODES, normalize_candidate_path
from libreevolve.core.redaction import redact_sensitive_text
from libreevolve.population.program import Program, validate_program_metrics
from libreevolve.problems.loader import Problem
from libreevolve.core.prompt_context_policy import *  # noqa: F401,F403
from libreevolve.core.prompt_context_policy import (
    PromptTemplateError,
    _unsafe_direct_context_label_char,
    _validate_direct_context_label,
)


PROMPT_TEMPLATE_FIELDS = {
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
REQUIRED_PROMPT_TEMPLATE_FIELDS = {"task"}
PROMPT_VARIANT_SEMANTIC_POLICIES = {"alphaevolve", "compatibility"}
ALPHAEVOLVE_REQUIRED_PROMPT_CHANNELS = frozenset(
    {"task", "parent_code", "mutation_instructions"}
)
ALPHAEVOLVE_FEEDBACK_PROMPT_CHANNELS = frozenset(
    {"parent_feedback", "parent_metrics", "parent_score"}
)
ALPHAEVOLVE_CONTEXT_PROMPT_CHANNELS = frozenset(
    {"context", "inspirations", "extra_context", "recent_failures"}
)
_PROMPT_TEMPLATE_DRY_RUN_VALUES = {
    "task": "task",
    "context": "context",
    "parent_score": 1.0,
    "parent_metrics": "score=1.0",
    "parent_feedback": "feedback",
    "parent_code": "code",
    "inspirations": "inspirations",
    "extra_context": "extra context",
    "recent_failures": "recent failures",
    "mutation_mode": "diff",
    "mutation_instructions": "mutation instructions",
}
_MAX_FEEDBACK_TEXT_CHARS = 1800
_MAX_FEEDBACK_FIELD_CHARS = 400
_MAX_FEEDBACK_ITEMS = 3
_MAX_VALIDATOR_METADATA_ITEMS = 3
_MAX_VALIDATOR_METADATA_VALUE_CHARS = 500
_VALIDATOR_METADATA_SPECIAL_KEYS = frozenset(
    {
        "artifacts",
        "attempts",
        "configured_stage_results",
        "diagnostic_output",
        "evaluator_dependency_policy",
        "llm_feedback",
        "malformed_metrics",
        "materialization_error",
        "metric_aggregation",
        "metric_bound_diagnostics",
        "primary_file",
        "program_outputs",
        "files",
        "sample_count",
        "sample_budget",
        "stage",
        "stage_budget",
        "synthetic_metrics",
        "syntax_errors",
        "timeout_cleanup",
        "validate_path",
        "validate_path_hash",
        "validate_path_redacted",
        "validate_path_scope",
        "validator_boundary",
        "validator_env",
        "stdin",
    }
)
PROMPT_ARTIFACT_CONTENT_MODES = {"excerpt", "bounded_file", "off"}
PROMPT_CONTEXT_POLICY_SCHEMA = "libreevolve.prompt_context_policy.v1"
PROMPT_SECTION_BUDGET_SCHEMA = "libreevolve.prompt_section_budget.v1"
PROMPT_SECTION_BUDGET_POLICY = (
    "deterministic_section_priority_packing_heuristic_token_estimates_final_prompt_cap"
)
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
DEFAULT_PROMPT_ARTIFACT_CONTENT_MAX_BYTES = 4096
DEFAULT_PROMPT_ARTIFACT_CONTENT_MAX_CHARS = 1000
_MAX_EXTRA_CONTEXT_CHARS = 4000
_MAX_DIRECT_CONTEXT_CHARS = 6000
_MAX_DIRECT_CONTEXT_LABEL_CHARS = 1024
_MAX_TASK_DESCRIPTION_CHARS = 20000
_MAX_METRIC_FIELD_CHARS = 160
_METRIC_LABEL_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_.-]{0,127}")
_PROMPT_FORMAT_MARKER_RE = re.compile(r"\[\[prompt:([A-Za-z][A-Za-z0-9_-]{0,63})\]\]")
_PROMPT_FORMAT_NAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9_-]{0,63}")
_PROMPT_SECTION_PRIORITIES = {
    "task": 0,
    "mutation_instructions": 1,
    "parent_code": 2,
    "parent_score": 3,
    "parent_metrics": 4,
    "parent_feedback": 5,
    "context": 6,
    "extra_context": 7,
    "inspirations": 8,
    "recent_failures": 9,
    "mutation_mode": 10,
}


@dataclass(frozen=True)
class _PromptScore:
    value: object

    def __format__(self, format_spec: str) -> str:
        if _is_finite_non_bool_number(self.value):
            return format(float(self.value), format_spec or ".4f")
        return _invalid_score_text(self.value)

    def __str__(self) -> str:
        return format(self, ".4f")


@dataclass
class PromptSampler:
    """Configurable prompt sampler for AlphaEvolve-style context assembly."""

    variants: list[str] = field(default_factory=list)
    rng: random.Random = field(default_factory=random.Random)
    max_prompt_chars: int | None = None
    max_prompt_estimated_tokens: int | None = None
    artifact_base_dir: Path | str | None = None
    artifact_content_mode: str = "excerpt"
    artifact_content_max_bytes: int = DEFAULT_PROMPT_ARTIFACT_CONTENT_MAX_BYTES
    artifact_content_max_chars: int = DEFAULT_PROMPT_ARTIFACT_CONTENT_MAX_CHARS
    prompt_format_options: dict[str, list[dict[str, object]]] = field(default_factory=dict)
    prompt_variant_semantic_policy: str = "compatibility"
    prompt_token_counter: Callable[[str], int] | None = None
    prompt_token_counter_name: str = "provider"
    last_metadata: dict = field(default_factory=dict, init=False)
    last_context_text: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.prompt_format_options = validate_prompt_format_options(
            self.prompt_format_options
        )
        self.variants = validate_prompt_variants(
            self.variants,
            prompt_format_options=self.prompt_format_options,
            semantic_policy=self.prompt_variant_semantic_policy,
        )
        self.prompt_variant_semantic_policy = validate_prompt_variant_semantic_policy(
            self.prompt_variant_semantic_policy
        )
        self.prompt_token_counter = validate_prompt_token_counter(
            self.prompt_token_counter
        )
        self.prompt_token_counter_name = validate_prompt_token_counter_name(
            self.prompt_token_counter_name
        )
        self.max_prompt_chars = validate_prompt_max_chars(self.max_prompt_chars)
        self.max_prompt_estimated_tokens = validate_prompt_max_estimated_tokens(
            self.max_prompt_estimated_tokens
        )
        self.artifact_base_dir = validate_prompt_artifact_base_dir(self.artifact_base_dir)
        self.artifact_content_mode = validate_prompt_artifact_content_mode(
            self.artifact_content_mode
        )
        self.artifact_content_max_bytes = validate_prompt_artifact_content_limit(
            "artifact_content_max_bytes",
            self.artifact_content_max_bytes,
        )
        self.artifact_content_max_chars = validate_prompt_artifact_content_limit(
            "artifact_content_max_chars",
            self.artifact_content_max_chars,
        )

    def build(
        self,
        parent: Program,
        inspirations: list[Program],
        problem: Problem,
        extra_context: str,
        recent_failures: list[dict | tuple[str, float]] | None = None,
        template: str | None = None,
        mutation_mode: str = "diff",
        capture_proposal_metadata: bool = False,
        context_policy: Mapping[str, object] | None = None,
    ) -> str:
        parent = validate_prompt_parent(parent)
        inspirations = validate_prompt_inspirations(inspirations)
        self.prompt_format_options = validate_prompt_format_options(
            self.prompt_format_options
        )
        variants = validate_prompt_variants(
            self.variants,
            prompt_format_options=self.prompt_format_options,
            semantic_policy=self.prompt_variant_semantic_policy,
        )
        capture_proposal_metadata = validate_capture_proposal_metadata(
            capture_proposal_metadata
        )
        extra_context = validate_prompt_extra_context(extra_context)
        prompt_context_policy = validate_prompt_context_policy(context_policy)
        proposal_metadata_enabled = prompt_context_policy["proposal_metadata_enabled"]
        if proposal_metadata_enabled is not None:
            capture_proposal_metadata = proposal_metadata_enabled
        if template is None:
            variant = self.rng.choice(variants) if variants else _DEFAULT_TEMPLATE
        else:
            variant = template
        validate_prompt_format_markers(variant, self.prompt_format_options)
        variant, format_metadata = render_prompt_format_options(
            variant,
            self.prompt_format_options,
            self.rng,
            weight_overrides=prompt_context_policy["prompt_format_weights"],
        )
        validate_prompt_template(variant)
        mutation_mode = validate_prompt_mutation_mode(mutation_mode)
        task = validate_direct_task_description(problem.task_description)
        context, context_metadata = _render_context_with_metadata(
            problem,
            selected_paths=prompt_context_policy["context_source_paths"],
            required_terms=prompt_context_policy["context_source_required_terms"],
            excluded_terms=prompt_context_policy["context_source_excluded_terms"],
            ranking_terms=prompt_context_policy["context_source_ranking_terms"],
            source_limit=prompt_context_policy["context_source_limit"],
            source_max_chars=prompt_context_policy["context_source_max_chars"],
            truncation=prompt_context_policy["context_source_truncation"],
            order_policy=prompt_context_policy["context_source_order_policy"],
        )
        extra_context, extra_context_policy_metadata = _apply_extra_context_policy(
            extra_context,
            prompt_context_policy["extra_context_max_chars"],
        )
        artifact_content_mode = (
            prompt_context_policy["validator_artifact_content_mode"]
            or self.artifact_content_mode
        )
        artifact_content_max_bytes = (
            prompt_context_policy["validator_artifact_content_max_bytes"]
            or self.artifact_content_max_bytes
        )
        artifact_content_max_chars = (
            prompt_context_policy["validator_artifact_content_max_chars"]
            or self.artifact_content_max_chars
        )
        self.last_context_text = context
        parent_code, parent_code_paths_metadata = _render_program_files_with_metadata(
            parent,
            selected_paths=prompt_context_policy["parent_code_paths"],
            required_terms=prompt_context_policy["parent_code_required_terms"],
            excluded_terms=prompt_context_policy["parent_code_excluded_terms"],
            ranking_terms=prompt_context_policy["parent_code_ranking_terms"],
            order_policy=prompt_context_policy["parent_code_order_policy"],
            file_limit=prompt_context_policy["parent_code_limit"],
            max_chars_by_path=prompt_context_policy["parent_code_max_chars_by_path"],
            query_text=task,
        )
        parent_code, parent_code_policy_metadata = _apply_parent_code_policy(
            parent_code,
            prompt_context_policy["parent_code_max_chars"],
            prompt_context_policy["parent_code_truncation"],
            path_metadata=parent_code_paths_metadata,
        )
        render_values = {
            "task": task,
            "context": context,
            "parent_score": _PromptScore(parent.fitness),
            "parent_metrics": _render_metrics(
                parent,
                problem,
                selected_names=prompt_context_policy["parent_metric_names"],
                max_chars_by_name=prompt_context_policy[
                    "parent_metrics_max_chars_by_name"
                ],
            ),
            "parent_feedback": _render_feedback(
                parent,
                artifact_base_dir=self.artifact_base_dir,
                artifact_content_mode=artifact_content_mode,
                artifact_content_max_bytes=artifact_content_max_bytes,
                artifact_content_max_chars=artifact_content_max_chars,
                feedback_sections=prompt_context_policy["feedback_sections"],
                feedback_section_order=prompt_context_policy["feedback_section_order"],
                feedback_section_max_chars_by_name=prompt_context_policy[
                    "feedback_section_max_chars_by_name"
                ],
                llm_feedback_fields=prompt_context_policy["llm_feedback_fields"],
                llm_feedback_max_chars_by_field=prompt_context_policy[
                    "llm_feedback_max_chars_by_field"
                ],
                proposal_fields=prompt_context_policy["proposal_fields"],
                proposal_max_chars_by_field=prompt_context_policy[
                    "proposal_max_chars_by_field"
                ],
                stage_summary_fields=prompt_context_policy["stage_summary_fields"],
                stage_summary_max_chars_by_field=prompt_context_policy[
                    "stage_summary_max_chars_by_field"
                ],
                execution_output_fields=prompt_context_policy[
                    "execution_output_fields"
                ],
                execution_output_max_chars_by_field=prompt_context_policy[
                    "execution_output_max_chars_by_field"
                ],
                sample_retry_fields=prompt_context_policy["sample_retry_fields"],
                sample_retry_max_chars_by_field=prompt_context_policy[
                    "sample_retry_max_chars_by_field"
                ],
                program_output_fields=prompt_context_policy["program_output_fields"],
                program_output_max_chars_by_field=prompt_context_policy[
                    "program_output_max_chars_by_field"
                ],
                validator_artifact_fields=prompt_context_policy[
                    "validator_artifact_fields"
                ],
                validator_artifact_max_chars_by_field=prompt_context_policy[
                    "validator_artifact_max_chars_by_field"
                ],
                validator_artifact_content_fields=prompt_context_policy[
                    "validator_artifact_content_fields"
                ],
                validator_skipped_artifact_fields=prompt_context_policy[
                    "validator_skipped_artifact_fields"
                ],
                validator_skipped_artifact_max_chars_by_field=prompt_context_policy[
                    "validator_skipped_artifact_max_chars_by_field"
                ],
                validator_diagnostic_groups=prompt_context_policy[
                    "validator_diagnostic_groups"
                ],
                validator_metadata_keys=prompt_context_policy[
                    "validator_metadata_keys"
                ],
                validator_metadata_limit=prompt_context_policy[
                    "validator_metadata_limit"
                ],
                validator_metadata_max_chars_by_key=prompt_context_policy[
                    "validator_metadata_max_chars_by_key"
                ],
                evaluator_path_fields=prompt_context_policy["evaluator_path_fields"],
                evaluator_path_max_chars_by_field=prompt_context_policy[
                    "evaluator_path_max_chars_by_field"
                ],
                evaluator_dependency_fields=prompt_context_policy[
                    "evaluator_dependency_fields"
                ],
                evaluator_dependency_max_chars_by_field=prompt_context_policy[
                    "evaluator_dependency_max_chars_by_field"
                ],
                evaluator_stage_fields=prompt_context_policy["evaluator_stage_fields"],
                evaluator_stage_max_chars_by_field=prompt_context_policy[
                    "evaluator_stage_max_chars_by_field"
                ],
                evaluator_workspace_fields=prompt_context_policy[
                    "evaluator_workspace_fields"
                ],
                evaluator_workspace_max_chars_by_field=prompt_context_policy[
                    "evaluator_workspace_max_chars_by_field"
                ],
                syntax_error_fields=prompt_context_policy["syntax_error_fields"],
                syntax_error_max_chars_by_field=prompt_context_policy[
                    "syntax_error_max_chars_by_field"
                ],
                metric_bound_fields=prompt_context_policy["metric_bound_fields"],
                metric_bound_max_chars_by_field=prompt_context_policy[
                    "metric_bound_max_chars_by_field"
                ],
                configured_stage_check_fields=prompt_context_policy[
                    "configured_stage_check_fields"
                ],
                configured_stage_check_max_chars_by_field=prompt_context_policy[
                    "configured_stage_check_max_chars_by_field"
                ],
                stage_metric_threshold_fields=prompt_context_policy[
                    "stage_metric_threshold_fields"
                ],
                stage_metric_threshold_max_chars_by_field=prompt_context_policy[
                    "stage_metric_threshold_max_chars_by_field"
                ],
                artifact_output_check_fields=prompt_context_policy[
                    "artifact_output_check_fields"
                ],
                artifact_output_check_max_chars_by_field=prompt_context_policy[
                    "artifact_output_check_max_chars_by_field"
                ],
                malformed_metric_fields=prompt_context_policy[
                    "malformed_metric_fields"
                ],
                malformed_metric_max_chars_by_field=prompt_context_policy[
                    "malformed_metric_max_chars_by_field"
                ],
                materialization_error_fields=prompt_context_policy[
                    "materialization_error_fields"
                ],
                materialization_error_max_chars_by_field=prompt_context_policy[
                    "materialization_error_max_chars_by_field"
                ],
                metric_aggregation_fields=prompt_context_policy[
                    "metric_aggregation_fields"
                ],
                metric_aggregation_max_chars_by_field=prompt_context_policy[
                    "metric_aggregation_max_chars_by_field"
                ],
                synthetic_metric_fields=prompt_context_policy[
                    "synthetic_metric_fields"
                ],
                synthetic_metric_max_chars_by_field=prompt_context_policy[
                    "synthetic_metric_max_chars_by_field"
                ],
                execution_diagnostic_groups=prompt_context_policy[
                    "execution_diagnostic_groups"
                ],
                validator_boundary_fields=prompt_context_policy[
                    "validator_boundary_fields"
                ],
                validator_boundary_max_chars_by_field=prompt_context_policy[
                    "validator_boundary_max_chars_by_field"
                ],
                validator_budget_fields=prompt_context_policy[
                    "validator_budget_fields"
                ],
                validator_budget_max_chars_by_field=prompt_context_policy[
                    "validator_budget_max_chars_by_field"
                ],
                validator_env_fields=prompt_context_policy["validator_env_fields"],
                validator_env_max_chars_by_field=prompt_context_policy[
                    "validator_env_max_chars_by_field"
                ],
                validator_resource_limit_fields=prompt_context_policy[
                    "validator_resource_limit_fields"
                ],
                validator_resource_limit_max_chars_by_field=prompt_context_policy[
                    "validator_resource_limit_max_chars_by_field"
                ],
                validator_stdin_fields=prompt_context_policy[
                    "validator_stdin_fields"
                ],
                validator_stdin_max_chars_by_field=prompt_context_policy[
                    "validator_stdin_max_chars_by_field"
                ],
                diagnostic_output_fields=prompt_context_policy[
                    "diagnostic_output_fields"
                ],
                diagnostic_output_max_chars_by_field=prompt_context_policy[
                    "diagnostic_output_max_chars_by_field"
                ],
                timeout_cleanup_fields=prompt_context_policy[
                    "timeout_cleanup_fields"
                ],
                timeout_cleanup_max_chars_by_field=prompt_context_policy[
                    "timeout_cleanup_max_chars_by_field"
                ],
            ),
            "parent_code": parent_code,
            "inspirations": _render_inspirations(
                inspirations,
                problem,
                limit=prompt_context_policy["inspiration_limit"],
                artifact_base_dir=self.artifact_base_dir,
                artifact_content_mode=artifact_content_mode,
                artifact_content_max_bytes=artifact_content_max_bytes,
                artifact_content_max_chars=artifact_content_max_chars,
                llm_feedback_fields=prompt_context_policy["llm_feedback_fields"],
                llm_feedback_max_chars_by_field=prompt_context_policy[
                    "llm_feedback_max_chars_by_field"
                ],
                proposal_fields=prompt_context_policy["proposal_fields"],
                proposal_max_chars_by_field=prompt_context_policy[
                    "proposal_max_chars_by_field"
                ],
                stage_summary_fields=prompt_context_policy["stage_summary_fields"],
                stage_summary_max_chars_by_field=prompt_context_policy[
                    "stage_summary_max_chars_by_field"
                ],
                execution_output_fields=prompt_context_policy[
                    "execution_output_fields"
                ],
                execution_output_max_chars_by_field=prompt_context_policy[
                    "execution_output_max_chars_by_field"
                ],
                sample_retry_fields=prompt_context_policy["sample_retry_fields"],
                sample_retry_max_chars_by_field=prompt_context_policy[
                    "sample_retry_max_chars_by_field"
                ],
                program_output_fields=prompt_context_policy["program_output_fields"],
                program_output_max_chars_by_field=prompt_context_policy[
                    "program_output_max_chars_by_field"
                ],
                validator_artifact_fields=prompt_context_policy[
                    "validator_artifact_fields"
                ],
                validator_artifact_max_chars_by_field=prompt_context_policy[
                    "validator_artifact_max_chars_by_field"
                ],
                validator_artifact_content_fields=prompt_context_policy[
                    "validator_artifact_content_fields"
                ],
                validator_skipped_artifact_fields=prompt_context_policy[
                    "validator_skipped_artifact_fields"
                ],
                validator_skipped_artifact_max_chars_by_field=prompt_context_policy[
                    "validator_skipped_artifact_max_chars_by_field"
                ],
                validator_diagnostic_groups=prompt_context_policy[
                    "validator_diagnostic_groups"
                ],
                validator_metadata_keys=prompt_context_policy[
                    "validator_metadata_keys"
                ],
                validator_metadata_limit=prompt_context_policy[
                    "validator_metadata_limit"
                ],
                validator_metadata_max_chars_by_key=prompt_context_policy[
                    "validator_metadata_max_chars_by_key"
                ],
                evaluator_path_fields=prompt_context_policy["evaluator_path_fields"],
                evaluator_path_max_chars_by_field=prompt_context_policy[
                    "evaluator_path_max_chars_by_field"
                ],
                evaluator_dependency_fields=prompt_context_policy[
                    "evaluator_dependency_fields"
                ],
                evaluator_dependency_max_chars_by_field=prompt_context_policy[
                    "evaluator_dependency_max_chars_by_field"
                ],
                evaluator_stage_fields=prompt_context_policy["evaluator_stage_fields"],
                evaluator_stage_max_chars_by_field=prompt_context_policy[
                    "evaluator_stage_max_chars_by_field"
                ],
                evaluator_workspace_fields=prompt_context_policy[
                    "evaluator_workspace_fields"
                ],
                evaluator_workspace_max_chars_by_field=prompt_context_policy[
                    "evaluator_workspace_max_chars_by_field"
                ],
                syntax_error_fields=prompt_context_policy["syntax_error_fields"],
                syntax_error_max_chars_by_field=prompt_context_policy[
                    "syntax_error_max_chars_by_field"
                ],
                metric_bound_fields=prompt_context_policy["metric_bound_fields"],
                metric_bound_max_chars_by_field=prompt_context_policy[
                    "metric_bound_max_chars_by_field"
                ],
                configured_stage_check_fields=prompt_context_policy[
                    "configured_stage_check_fields"
                ],
                configured_stage_check_max_chars_by_field=prompt_context_policy[
                    "configured_stage_check_max_chars_by_field"
                ],
                stage_metric_threshold_fields=prompt_context_policy[
                    "stage_metric_threshold_fields"
                ],
                stage_metric_threshold_max_chars_by_field=prompt_context_policy[
                    "stage_metric_threshold_max_chars_by_field"
                ],
                artifact_output_check_fields=prompt_context_policy[
                    "artifact_output_check_fields"
                ],
                artifact_output_check_max_chars_by_field=prompt_context_policy[
                    "artifact_output_check_max_chars_by_field"
                ],
                malformed_metric_fields=prompt_context_policy[
                    "malformed_metric_fields"
                ],
                malformed_metric_max_chars_by_field=prompt_context_policy[
                    "malformed_metric_max_chars_by_field"
                ],
                materialization_error_fields=prompt_context_policy[
                    "materialization_error_fields"
                ],
                materialization_error_max_chars_by_field=prompt_context_policy[
                    "materialization_error_max_chars_by_field"
                ],
                metric_aggregation_fields=prompt_context_policy[
                    "metric_aggregation_fields"
                ],
                metric_aggregation_max_chars_by_field=prompt_context_policy[
                    "metric_aggregation_max_chars_by_field"
                ],
                synthetic_metric_fields=prompt_context_policy[
                    "synthetic_metric_fields"
                ],
                synthetic_metric_max_chars_by_field=prompt_context_policy[
                    "synthetic_metric_max_chars_by_field"
                ],
                execution_diagnostic_groups=prompt_context_policy[
                    "execution_diagnostic_groups"
                ],
                validator_boundary_fields=prompt_context_policy[
                    "validator_boundary_fields"
                ],
                validator_boundary_max_chars_by_field=prompt_context_policy[
                    "validator_boundary_max_chars_by_field"
                ],
                validator_budget_fields=prompt_context_policy[
                    "validator_budget_fields"
                ],
                validator_budget_max_chars_by_field=prompt_context_policy[
                    "validator_budget_max_chars_by_field"
                ],
                validator_env_fields=prompt_context_policy["validator_env_fields"],
                validator_env_max_chars_by_field=prompt_context_policy[
                    "validator_env_max_chars_by_field"
                ],
                validator_resource_limit_fields=prompt_context_policy[
                    "validator_resource_limit_fields"
                ],
                validator_resource_limit_max_chars_by_field=prompt_context_policy[
                    "validator_resource_limit_max_chars_by_field"
                ],
                validator_stdin_fields=prompt_context_policy[
                    "validator_stdin_fields"
                ],
                validator_stdin_max_chars_by_field=prompt_context_policy[
                    "validator_stdin_max_chars_by_field"
                ],
                diagnostic_output_fields=prompt_context_policy[
                    "diagnostic_output_fields"
                ],
                diagnostic_output_max_chars_by_field=prompt_context_policy[
                    "diagnostic_output_max_chars_by_field"
                ],
                timeout_cleanup_fields=prompt_context_policy[
                    "timeout_cleanup_fields"
                ],
                timeout_cleanup_max_chars_by_field=prompt_context_policy[
                    "timeout_cleanup_max_chars_by_field"
                ],
            ),
            "extra_context": extra_context,
            "recent_failures": _render_failures(
                recent_failures,
                limit=prompt_context_policy["recent_failure_limit"],
                selection_policy=prompt_context_policy[
                    "recent_failure_selection_policy"
                ],
                required_errors=prompt_context_policy[
                    "recent_failure_required_errors"
                ],
                excluded_errors=prompt_context_policy[
                    "recent_failure_excluded_errors"
                ],
                required_changed_files=prompt_context_policy[
                    "recent_failure_required_changed_files"
                ],
                excluded_changed_files=prompt_context_policy[
                    "recent_failure_excluded_changed_files"
                ],
                required_stage_names=prompt_context_policy[
                    "recent_failure_required_stage_names"
                ],
                excluded_stage_names=prompt_context_policy[
                    "recent_failure_excluded_stage_names"
                ],
                required_terms=prompt_context_policy[
                    "recent_failure_required_terms"
                ],
                excluded_terms=prompt_context_policy[
                    "recent_failure_excluded_terms"
                ],
                repetition_threshold=prompt_context_policy[
                    "recent_failure_repetition_threshold"
                ],
                score_threshold=prompt_context_policy[
                    "recent_failure_score_threshold"
                ],
                max_chars_by_field=prompt_context_policy[
                    "recent_failure_max_chars_by_field"
                ],
            ),
            "mutation_mode": mutation_mode,
            "mutation_instructions": _render_mutation_instructions(
                mutation_mode,
                capture_proposal_metadata=capture_proposal_metadata,
                instruction_variant=prompt_context_policy[
                    "mutation_instruction_variant"
                ],
                include_example=prompt_context_policy[
                    "mutation_instruction_include_example"
                ],
            ),
        }
        render_values, context_policy_metadata = apply_prompt_context_policy(
            render_values,
            prompt_context_policy,
        )
        unpacked_rendered = variant.format(**render_values)
        effective_max_chars = _effective_prompt_max_chars(
            self.max_prompt_chars,
            self.max_prompt_estimated_tokens,
            exact_token_counter_configured=self.prompt_token_counter is not None,
        )
        render_values, packing_metadata = _pack_prompt_sections(
            variant,
            render_values,
            rendered_chars=len(unpacked_rendered),
            max_chars=effective_max_chars,
            max_tokens=self.max_prompt_estimated_tokens,
            token_counter=self.prompt_token_counter,
            token_counter_name=self.prompt_token_counter_name,
            section_priorities=prompt_context_policy["section_priorities"],
        )
        rendered = variant.format(**render_values)
        section_budget = _prompt_section_budget_report(
            variant,
            render_values,
            rendered_chars=len(rendered),
            max_chars=effective_max_chars,
            configured_max_chars=self.max_prompt_chars,
            max_estimated_tokens=self.max_prompt_estimated_tokens,
            token_counter=self.prompt_token_counter,
            token_counter_name=self.prompt_token_counter_name,
            packing_metadata=packing_metadata,
            section_priorities=prompt_context_policy["section_priorities"],
        )
        rendered, metadata = apply_prompt_budget(rendered, effective_max_chars)
        if self.prompt_token_counter is not None:
            metadata["provider_tokens"] = _count_prompt_tokens(
                rendered,
                self.prompt_token_counter,
            )
            metadata["provider_token_counter"] = self.prompt_token_counter_name
        metadata.update(context_metadata)
        metadata["prompt_context_policy"] = context_policy_metadata
        metadata["failure_memory_policy"] = _failure_memory_policy_metadata(
            recent_failures,
            prompt_context_policy["recent_failure_limit"],
            prompt_context_policy["recent_failure_selection_policy"],
            prompt_context_policy["recent_failure_required_errors"],
            prompt_context_policy["recent_failure_excluded_errors"],
            prompt_context_policy["recent_failure_required_changed_files"],
            prompt_context_policy["recent_failure_excluded_changed_files"],
            prompt_context_policy["recent_failure_required_stage_names"],
            prompt_context_policy["recent_failure_excluded_stage_names"],
            prompt_context_policy["recent_failure_required_terms"],
            prompt_context_policy["recent_failure_excluded_terms"],
            prompt_context_policy["recent_failure_repetition_threshold"],
            prompt_context_policy["recent_failure_score_threshold"],
            prompt_context_policy["recent_failure_max_chars_by_field"],
        )
        metadata["inspiration_policy"] = _inspiration_policy_metadata(
            inspirations,
            prompt_context_policy["inspiration_limit"],
        )
        metadata["parent_code_policy"] = parent_code_policy_metadata
        metadata["extra_context_policy"] = extra_context_policy_metadata
        metadata["section_budget"] = section_budget
        if format_metadata["enabled"]:
            metadata["stochastic_formatting"] = format_metadata
        metadata["prompt_sha256"] = hashlib.sha256(rendered.encode("utf-8")).hexdigest()
        metadata["prompt_sha256_scope"] = "rendered_prompt"
        self.last_metadata = metadata
        return rendered


DEFAULT_TEMPLATE = """[SYSTEM]
You are an expert programmer evolving solutions for: {task}

[EXPLICIT CONTEXT]
{context}

[CURRENT PROGRAM - normalized fitness: {parent_score:.4f}]
Metrics: {parent_metrics}
Evaluation feedback:
{parent_feedback}
{parent_code}

[INSPIRATION PROGRAMS]
{inspirations}

[EXTRA CONTEXT]
{extra_context}
{recent_failures}
[TASK]
Propose a targeted improvement.
Mutation mode: {mutation_mode}
{mutation_instructions}
"""

_DEFAULT_TEMPLATE = DEFAULT_TEMPLATE


def validate_prompt_template(template: str) -> None:
    fields = prompt_template_fields(template)
    missing = sorted(REQUIRED_PROMPT_TEMPLATE_FIELDS - fields)
    if missing:
        raise PromptTemplateError(f"missing required prompt template fields {missing}")
    try:
        template.format(**_PROMPT_TEMPLATE_DRY_RUN_VALUES)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise PromptTemplateError(
            f"prompt template format spec is incompatible with render values: {exc}"
        ) from exc


def validate_prompt_variant_semantic_policy(value: object) -> str:
    if not isinstance(value, str) or value not in PROMPT_VARIANT_SEMANTIC_POLICIES:
        allowed = ", ".join(sorted(PROMPT_VARIANT_SEMANTIC_POLICIES))
        raise PromptTemplateError(
            f"prompt_variant_semantic_policy must be one of: {allowed}"
        )
    return value


def validate_configured_prompt_template_semantics(
    template: str,
    *,
    semantic_policy: str = "alphaevolve",
) -> None:
    policy = validate_prompt_variant_semantic_policy(semantic_policy)
    if policy == "compatibility":
        return
    fields = prompt_template_fields(template)
    missing_required = sorted(ALPHAEVOLVE_REQUIRED_PROMPT_CHANNELS - fields)
    if missing_required:
        raise PromptTemplateError(
            "configured prompt template missing AlphaEvolve prompt channels "
            f"{missing_required}; set prompt_variant_semantic_policy: compatibility "
            "to allow minimal externally managed templates"
        )
    if not fields.intersection(ALPHAEVOLVE_FEEDBACK_PROMPT_CHANNELS):
        raise PromptTemplateError(
            "configured prompt template must include at least one evaluator feedback "
            f"channel {sorted(ALPHAEVOLVE_FEEDBACK_PROMPT_CHANNELS)}; set "
            "prompt_variant_semantic_policy: compatibility to allow minimal templates"
        )
    if not fields.intersection(ALPHAEVOLVE_CONTEXT_PROMPT_CHANNELS):
        raise PromptTemplateError(
            "configured prompt template must include at least one context or "
            f"inspiration channel {sorted(ALPHAEVOLVE_CONTEXT_PROMPT_CHANNELS)}; "
            "set prompt_variant_semantic_policy: compatibility to allow minimal templates"
        )


def validate_prompt_template_fragment(fragment: str) -> None:
    prompt_template_fields(fragment)
    try:
        fragment.format(**_PROMPT_TEMPLATE_DRY_RUN_VALUES)
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        raise PromptTemplateError(
            f"prompt format option is incompatible with render values: {exc}"
        ) from exc


def prompt_template_fields(template: str) -> set[str]:
    if not isinstance(template, str) or not template.strip():
        raise PromptTemplateError("prompt template must be a non-empty string")
    fields: set[str] = set()
    try:
        parsed = list(string.Formatter().parse(template))
    except ValueError as exc:
        raise PromptTemplateError(f"malformed prompt template: {exc}") from exc
    for _, field_name, _, _ in parsed:
        if field_name is None:
            continue
        if not field_name:
            raise PromptTemplateError("prompt template contains an empty placeholder")
        root = field_name.split(".", 1)[0].split("[", 1)[0]
        if root != field_name:
            raise PromptTemplateError(
                f"prompt template field {field_name!r} must be a simple placeholder"
            )
        if field_name not in PROMPT_TEMPLATE_FIELDS:
            raise PromptTemplateError(f"unknown prompt template field {field_name!r}")
        fields.add(field_name)
    return fields


def validate_prompt_mutation_mode(value: object) -> str:
    if not isinstance(value, str) or value not in MUTATION_MODES:
        allowed = ", ".join(sorted(MUTATION_MODES))
        raise PromptTemplateError(f"mutation_mode must be one of: {allowed}")
    return value


def validate_prompt_max_chars(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PromptTemplateError("max_prompt_chars must be an integer >= 1 or None")
    return value


def validate_prompt_max_estimated_tokens(value: object) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PromptTemplateError(
            "max_prompt_estimated_tokens must be an integer >= 1 or None"
        )
    return value


def validate_prompt_token_counter(
    value: object,
) -> Callable[[str], int] | None:
    if value is None:
        return None
    if not callable(value):
        raise PromptTemplateError("prompt_token_counter must be callable or None")
    return value


def validate_prompt_token_counter_name(value: object) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PromptTemplateError(
            "prompt_token_counter_name must be a non-empty manifest-safe label"
        )
    label = value.strip()
    if len(label) > 80 or re.fullmatch(r"[A-Za-z0-9_.:/@+-]+", label) is None:
        raise PromptTemplateError(
            "prompt_token_counter_name must be a non-empty manifest-safe label"
        )
    if redact_sensitive_text(label) != label:
        raise PromptTemplateError("prompt_token_counter_name must not look secret-like")
    return label


def _effective_prompt_max_chars(
    max_chars: int | None,
    max_estimated_tokens: int | None,
    *,
    exact_token_counter_configured: bool = False,
) -> int | None:
    if exact_token_counter_configured:
        return max_chars
    token_chars = max_estimated_tokens * 4 if max_estimated_tokens is not None else None
    candidates = [value for value in (max_chars, token_chars) if value is not None]
    if not candidates:
        return None
    return min(candidates)


def validate_prompt_artifact_base_dir(value: object) -> Path | None:
    if value is None:
        return None
    if isinstance(value, Path):
        return value.resolve(strict=False)
    if isinstance(value, str) and value.strip():
        return Path(value).resolve(strict=False)
    raise PromptTemplateError("artifact_base_dir must be a path or None")


def validate_prompt_artifact_content_mode(value: object) -> str:
    if not isinstance(value, str) or value not in PROMPT_ARTIFACT_CONTENT_MODES:
        allowed = ", ".join(sorted(PROMPT_ARTIFACT_CONTENT_MODES))
        raise PromptTemplateError(f"artifact_content_mode must be one of: {allowed}")
    return value


def validate_prompt_artifact_content_limit(label: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise PromptTemplateError(f"{label} must be an integer >= 1")
    return value


def apply_prompt_context_policy(
    values: Mapping[str, object],
    context_policy: Mapping[str, object],
) -> tuple[dict[str, object], dict]:
    policy = validate_prompt_context_policy(context_policy)
    rendered = dict(values)
    disabled_sections = list(policy["disabled_sections"])
    disabled_metadata = []
    for name in disabled_sections:
        previous = _prompt_section_text(rendered.get(name))
        marker = _prompt_context_policy_disabled_marker(name, len(previous))
        rendered[name] = marker
        disabled_metadata.append(
            {
                "name": name,
                "original_chars": len(previous),
                "original_sha256": hashlib.sha256(
                    previous.encode("utf-8")
                ).hexdigest(),
                "replacement_chars": len(marker),
                "replacement_sha256": hashlib.sha256(
                    marker.encode("utf-8")
                ).hexdigest(),
            }
        )
    policy_sha256 = prompt_context_policy_sha256(policy)
    return rendered, {
        "schema": PROMPT_CONTEXT_POLICY_SCHEMA,
        "sha256": policy_sha256,
        "disabled_sections": disabled_sections,
        "section_priorities": dict(policy["section_priorities"]),
        "mutation_instruction_variant": policy["mutation_instruction_variant"],
        "mutation_instruction_include_example": policy[
            "mutation_instruction_include_example"
        ],
        "proposal_metadata_enabled": policy["proposal_metadata_enabled"],
        "parent_metric_names": (
            list(policy["parent_metric_names"])
            if policy["parent_metric_names"] is not None
            else None
        ),
        "parent_metrics_max_chars_by_name": dict(
            policy["parent_metrics_max_chars_by_name"]
        ),
        "parent_code_paths": list(policy["parent_code_paths"]),
        "parent_code_required_terms": list(policy["parent_code_required_terms"]),
        "parent_code_excluded_terms": list(policy["parent_code_excluded_terms"]),
        "parent_code_ranking_terms": list(policy["parent_code_ranking_terms"]),
        "parent_code_order_policy": policy["parent_code_order_policy"],
        "parent_code_limit": policy["parent_code_limit"],
        "parent_code_max_chars_by_path": dict(policy["parent_code_max_chars_by_path"]),
        "parent_code_max_chars": policy["parent_code_max_chars"],
        "parent_code_truncation": policy["parent_code_truncation"],
        "inspiration_strategy": policy["inspiration_strategy"],
        "inspiration_required_metric": policy["inspiration_required_metric"],
        "inspiration_excluded_metrics": list(policy["inspiration_excluded_metrics"]),
        "inspiration_fitness_threshold": (
            dict(policy["inspiration_fitness_threshold"])
            if policy["inspiration_fitness_threshold"] is not None
            else None
        ),
        "inspiration_metric_thresholds": {
            name: dict(thresholds)
            for name, thresholds in policy["inspiration_metric_thresholds"].items()
        },
        "inspiration_metric_ranking": (
            dict(policy["inspiration_metric_ranking"])
            if policy["inspiration_metric_ranking"] is not None
            else None
        ),
        "feedback_sections": list(policy["feedback_sections"]),
        "feedback_section_order": list(policy["feedback_section_order"]),
        "feedback_section_max_chars_by_name": dict(
            policy["feedback_section_max_chars_by_name"]
        ),
        "llm_feedback_fields": list(policy["llm_feedback_fields"]),
        "llm_feedback_max_chars_by_field": dict(
            policy["llm_feedback_max_chars_by_field"]
        ),
        "proposal_fields": list(policy["proposal_fields"]),
        "proposal_max_chars_by_field": dict(policy["proposal_max_chars_by_field"]),
        "stage_summary_fields": list(policy["stage_summary_fields"]),
        "stage_summary_max_chars_by_field": dict(
            policy["stage_summary_max_chars_by_field"]
        ),
        "execution_output_fields": list(policy["execution_output_fields"]),
        "execution_output_max_chars_by_field": dict(
            policy["execution_output_max_chars_by_field"]
        ),
        "sample_retry_fields": list(policy["sample_retry_fields"]),
        "sample_retry_max_chars_by_field": dict(
            policy["sample_retry_max_chars_by_field"]
        ),
        "program_output_fields": list(policy["program_output_fields"]),
        "program_output_max_chars_by_field": dict(
            policy["program_output_max_chars_by_field"]
        ),
        "validator_artifact_fields": list(policy["validator_artifact_fields"]),
        "validator_artifact_max_chars_by_field": dict(
            policy["validator_artifact_max_chars_by_field"]
        ),
        "validator_artifact_content_fields": list(
            policy["validator_artifact_content_fields"]
        ),
        "validator_artifact_content_mode": policy["validator_artifact_content_mode"],
        "validator_artifact_content_max_bytes": policy[
            "validator_artifact_content_max_bytes"
        ],
        "validator_artifact_content_max_chars": policy[
            "validator_artifact_content_max_chars"
        ],
        "validator_skipped_artifact_fields": list(
            policy["validator_skipped_artifact_fields"]
        ),
        "validator_skipped_artifact_max_chars_by_field": dict(
            policy["validator_skipped_artifact_max_chars_by_field"]
        ),
        "validator_diagnostic_groups": list(policy["validator_diagnostic_groups"]),
        "validator_metadata_keys": list(policy["validator_metadata_keys"]),
        "validator_metadata_limit": policy["validator_metadata_limit"],
        "validator_metadata_max_chars_by_key": dict(
            policy["validator_metadata_max_chars_by_key"]
        ),
        "evaluator_path_fields": list(policy["evaluator_path_fields"]),
        "evaluator_path_max_chars_by_field": dict(
            policy["evaluator_path_max_chars_by_field"]
        ),
        "evaluator_dependency_fields": list(policy["evaluator_dependency_fields"]),
        "evaluator_dependency_max_chars_by_field": dict(
            policy["evaluator_dependency_max_chars_by_field"]
        ),
        "evaluator_stage_fields": list(policy["evaluator_stage_fields"]),
        "evaluator_stage_max_chars_by_field": dict(
            policy["evaluator_stage_max_chars_by_field"]
        ),
        "evaluator_workspace_fields": list(policy["evaluator_workspace_fields"]),
        "evaluator_workspace_max_chars_by_field": dict(
            policy["evaluator_workspace_max_chars_by_field"]
        ),
        "syntax_error_fields": list(policy["syntax_error_fields"]),
        "syntax_error_max_chars_by_field": dict(
            policy["syntax_error_max_chars_by_field"]
        ),
        "metric_bound_fields": list(policy["metric_bound_fields"]),
        "metric_bound_max_chars_by_field": dict(
            policy["metric_bound_max_chars_by_field"]
        ),
        "configured_stage_check_fields": list(
            policy["configured_stage_check_fields"]
        ),
        "configured_stage_check_max_chars_by_field": dict(
            policy["configured_stage_check_max_chars_by_field"]
        ),
        "stage_metric_threshold_fields": list(
            policy["stage_metric_threshold_fields"]
        ),
        "stage_metric_threshold_max_chars_by_field": dict(
            policy["stage_metric_threshold_max_chars_by_field"]
        ),
        "artifact_output_check_fields": list(
            policy["artifact_output_check_fields"]
        ),
        "artifact_output_check_max_chars_by_field": dict(
            policy["artifact_output_check_max_chars_by_field"]
        ),
        "malformed_metric_fields": list(policy["malformed_metric_fields"]),
        "malformed_metric_max_chars_by_field": dict(
            policy["malformed_metric_max_chars_by_field"]
        ),
        "materialization_error_fields": list(policy["materialization_error_fields"]),
        "materialization_error_max_chars_by_field": dict(
            policy["materialization_error_max_chars_by_field"]
        ),
        "metric_aggregation_fields": list(policy["metric_aggregation_fields"]),
        "metric_aggregation_max_chars_by_field": dict(
            policy["metric_aggregation_max_chars_by_field"]
        ),
        "synthetic_metric_fields": list(policy["synthetic_metric_fields"]),
        "synthetic_metric_max_chars_by_field": dict(
            policy["synthetic_metric_max_chars_by_field"]
        ),
        "execution_diagnostic_groups": list(policy["execution_diagnostic_groups"]),
        "validator_boundary_fields": list(policy["validator_boundary_fields"]),
        "validator_boundary_max_chars_by_field": dict(
            policy["validator_boundary_max_chars_by_field"]
        ),
        "validator_budget_fields": list(policy["validator_budget_fields"]),
        "validator_budget_max_chars_by_field": dict(
            policy["validator_budget_max_chars_by_field"]
        ),
        "validator_env_fields": list(policy["validator_env_fields"]),
        "validator_env_max_chars_by_field": dict(
            policy["validator_env_max_chars_by_field"]
        ),
        "validator_resource_limit_fields": list(
            policy["validator_resource_limit_fields"]
        ),
        "validator_resource_limit_max_chars_by_field": dict(
            policy["validator_resource_limit_max_chars_by_field"]
        ),
        "validator_stdin_fields": list(policy["validator_stdin_fields"]),
        "validator_stdin_max_chars_by_field": dict(
            policy["validator_stdin_max_chars_by_field"]
        ),
        "diagnostic_output_fields": list(policy["diagnostic_output_fields"]),
        "diagnostic_output_max_chars_by_field": dict(
            policy["diagnostic_output_max_chars_by_field"]
        ),
        "timeout_cleanup_fields": list(policy["timeout_cleanup_fields"]),
        "timeout_cleanup_max_chars_by_field": dict(
            policy["timeout_cleanup_max_chars_by_field"]
        ),
        "prompt_format_weights": {
            name: list(weights)
            for name, weights in policy["prompt_format_weights"].items()
        },
        "context_source_paths": list(policy["context_source_paths"]),
        "context_source_required_terms": list(
            policy["context_source_required_terms"]
        ),
        "context_source_excluded_terms": list(
            policy["context_source_excluded_terms"]
        ),
        "context_source_ranking_terms": list(
            policy["context_source_ranking_terms"]
        ),
        "context_source_limit": policy["context_source_limit"],
        "context_source_max_chars": policy["context_source_max_chars"],
        "context_source_truncation": policy["context_source_truncation"],
        "context_source_order_policy": policy["context_source_order_policy"],
        "recent_failure_limit": policy["recent_failure_limit"],
        "recent_failure_selection_policy": policy[
            "recent_failure_selection_policy"
        ],
        "recent_failure_required_errors": list(
            policy["recent_failure_required_errors"]
        ),
        "recent_failure_excluded_errors": list(
            policy["recent_failure_excluded_errors"]
        ),
        "recent_failure_required_changed_files": list(
            policy["recent_failure_required_changed_files"]
        ),
        "recent_failure_excluded_changed_files": list(
            policy["recent_failure_excluded_changed_files"]
        ),
        "recent_failure_required_stage_names": list(
            policy["recent_failure_required_stage_names"]
        ),
        "recent_failure_excluded_stage_names": list(
            policy["recent_failure_excluded_stage_names"]
        ),
        "recent_failure_required_terms": list(policy["recent_failure_required_terms"]),
        "recent_failure_excluded_terms": list(policy["recent_failure_excluded_terms"]),
        "recent_failure_repetition_threshold": (
            dict(policy["recent_failure_repetition_threshold"])
            if policy["recent_failure_repetition_threshold"] is not None
            else None
        ),
        "recent_failure_score_threshold": (
            dict(policy["recent_failure_score_threshold"])
            if policy["recent_failure_score_threshold"] is not None
            else None
        ),
        "recent_failure_max_chars_by_field": dict(
            policy["recent_failure_max_chars_by_field"]
        ),
        "inspiration_limit": policy["inspiration_limit"],
        "inspiration_sample_count": policy["inspiration_sample_count"],
        "extra_context_max_chars": policy["extra_context_max_chars"],
        "applied_disabled_sections": disabled_metadata,
        "policy": (
            "structured_prompt_program_context_policy_channel_priority_and_instruction_control"
        ),
    }


def prompt_context_policy_sha256(value: object | None) -> str:
    policy = validate_prompt_context_policy(value)
    return _stable_json_sha256(policy)


def _prompt_context_policy_disabled_marker(field_name: str, original_chars: int) -> str:
    return (
        "[disabled by prompt context policy: "
        f"{field_name}, {original_chars} chars]"
    )


def _effective_section_priorities(
    overrides: Mapping[str, int] | None = None,
) -> dict[str, int]:
    priorities = dict(_PROMPT_SECTION_PRIORITIES)
    if overrides:
        priorities.update(validate_prompt_context_policy({"section_priorities": dict(overrides)})["section_priorities"])
    return priorities


def _prompt_section_priority(field_name: str, priorities: Mapping[str, int]) -> int:
    return int(priorities.get(field_name, 999))


def apply_prompt_budget(prompt: str, max_chars: int | None) -> tuple[str, dict]:
    if not isinstance(prompt, str):
        raise PromptTemplateError("rendered prompt must be text")
    original_chars = len(prompt)
    base_metadata = {
        "max_chars": max_chars,
        "original_chars": original_chars,
        "rendered_chars": original_chars,
        "estimated_tokens": _estimate_prompt_tokens(original_chars),
        "truncated": False,
        "strategy": "none",
    }
    if max_chars is None or original_chars <= max_chars:
        return prompt, base_metadata
    rendered, strategy = _truncate_prompt_middle(prompt, max_chars)
    metadata = dict(base_metadata)
    metadata.update(
        {
            "rendered_chars": len(rendered),
            "estimated_tokens": _estimate_prompt_tokens(len(rendered)),
            "truncated": True,
            "omitted_chars": original_chars - len(rendered),
            "strategy": strategy,
        }
    )
    return rendered, metadata


def _pack_prompt_sections(
    template: str,
    values: Mapping[str, object],
    *,
    rendered_chars: int,
    max_chars: int | None,
    max_tokens: int | None = None,
    token_counter: Callable[[str], int] | None = None,
    token_counter_name: str = "provider",
    section_priorities: Mapping[str, int] | None = None,
) -> tuple[dict[str, object], dict]:
    fields = prompt_template_field_occurrences(template)
    priorities = _effective_section_priorities(section_priorities)
    metadata = {
        "policy": "deterministic_section_priority_packing_heuristic_token_estimates_final_prompt_cap",
        "packing_status": (
            "not_configured"
            if max_chars is None and (max_tokens is None or token_counter is None)
            else "within_budget"
        ),
        "rendered_chars_before_packing": rendered_chars,
        "estimated_tokens_before_packing": _estimate_prompt_tokens(rendered_chars),
        "rendered_chars_after_packing": rendered_chars,
        "estimated_tokens_after_packing": _estimate_prompt_tokens(rendered_chars),
        "packed": False,
        "decisions": [],
    }
    rendered_prompt = template.format(**values)
    if token_counter is not None:
        metadata.update(
            {
                "token_count_policy": "provider_token_counter",
                "provider_token_counter": token_counter_name,
                "provider_tokens_before_packing": _count_prompt_tokens(
                    rendered_prompt,
                    token_counter,
                ),
                "provider_tokens_after_packing": _count_prompt_tokens(
                    rendered_prompt,
                    token_counter,
                ),
            }
        )
    else:
        metadata["token_count_policy"] = "heuristic_chars_per_token"
    if _rendered_prompt_within_budget(
        rendered_prompt,
        max_chars=max_chars,
        max_tokens=max_tokens,
        token_counter=token_counter,
    ):
        return dict(values), metadata

    packed_values = dict(values)
    decisions: list[dict] = []
    optional_fields = sorted(
        (
            field_name
            for field_name in fields
            if field_name not in ALPHAEVOLVE_REQUIRED_PROMPT_CHANNELS
        ),
        key=lambda name: (-_prompt_section_priority(name, priorities), name),
    )
    for field_name in optional_fields:
        raw_value = packed_values.get(field_name)
        if not isinstance(raw_value, str):
            continue
        current = _prompt_section_text(raw_value)
        if not current:
            continue
        marker = _prompt_section_packing_marker(field_name, len(current), max_chars)
        if len(marker) >= len(current):
            continue
        packed_values[field_name] = marker
        candidate = template.format(**packed_values)
        provider_tokens_after = (
            _count_prompt_tokens(candidate, token_counter)
            if token_counter is not None
            else None
        )
        decision = {
            "name": field_name,
            "priority": _prompt_section_priority(field_name, priorities),
            "action": "omit_optional_section",
            "original_chars": len(current),
            "rendered_chars_after": len(candidate),
            "estimated_tokens_after": _estimate_prompt_tokens(len(candidate)),
            "original_sha256": hashlib.sha256(current.encode("utf-8")).hexdigest(),
            "replacement_chars": len(marker),
            "replacement_sha256": hashlib.sha256(marker.encode("utf-8")).hexdigest(),
        }
        if provider_tokens_after is not None:
            decision["provider_tokens_after"] = provider_tokens_after
        decisions.append(decision)
        if _rendered_prompt_within_budget(
            candidate,
            max_chars=max_chars,
            max_tokens=max_tokens,
            token_counter=token_counter,
        ):
            metadata.update(
                {
                    "packing_status": "packed_optional_sections",
                    "rendered_chars_after_packing": len(candidate),
                    "estimated_tokens_after_packing": _estimate_prompt_tokens(
                        len(candidate)
                    ),
                    "packed": True,
                    "decisions": decisions,
                }
            )
            if provider_tokens_after is not None:
                metadata["provider_tokens_after_packing"] = provider_tokens_after
            return packed_values, metadata

    packed_rendered = template.format(**packed_values)
    required_with_overhead = _required_prompt_chars_with_overhead(
        template,
        packed_values,
        rendered_chars=len(packed_rendered),
    )
    provider_tokens_after = (
        _count_prompt_tokens(packed_rendered, token_counter)
        if token_counter is not None
        else None
    )
    status = (
        "required_sections_exceed_budget"
        if (
            (max_chars is not None and required_with_overhead > max_chars)
            or (
                max_tokens is not None
                and provider_tokens_after is not None
                and provider_tokens_after > max_tokens
            )
        )
        else "packed_optional_sections_still_over_budget"
    )
    metadata.update(
        {
            "packing_status": status,
            "rendered_chars_after_packing": len(packed_rendered),
            "estimated_tokens_after_packing": _estimate_prompt_tokens(
                len(packed_rendered)
            ),
            "packed": bool(decisions),
            "decisions": decisions,
        }
    )
    if provider_tokens_after is not None:
        metadata["provider_tokens_after_packing"] = provider_tokens_after
    return packed_values, metadata


def _rendered_prompt_within_budget(
    prompt: str,
    *,
    max_chars: int | None,
    max_tokens: int | None,
    token_counter: Callable[[str], int] | None,
) -> bool:
    if max_chars is not None and len(prompt) > max_chars:
        return False
    if max_tokens is not None and token_counter is not None:
        return _count_prompt_tokens(prompt, token_counter) <= max_tokens
    return True


def _count_prompt_tokens(
    prompt: str,
    token_counter: Callable[[str], int],
) -> int:
    try:
        value = token_counter(prompt)
    except Exception as exc:
        raise PromptTemplateError("prompt_token_counter failed") from exc
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise PromptTemplateError(
            "prompt_token_counter must return a non-negative integer"
        )
    return value


def _prompt_section_packing_marker(
    field_name: str,
    original_chars: int,
    max_chars: int,
) -> str:
    return (
        "[omitted by prompt section packer: "
        f"{field_name}, {original_chars} chars, prompt_max_chars={max_chars}]"
    )


def _apply_parent_code_policy(
    parent_code: str,
    max_chars: int | None,
    truncation: str,
    *,
    path_metadata: Mapping[str, object],
) -> tuple[str, dict]:
    if not isinstance(parent_code, str):
        parent_code = str(parent_code)
    original_chars = len(parent_code)
    path_policy_source = path_metadata.get("source")
    prompt_policy_active = max_chars is not None or path_policy_source == "prompt_context_policy"
    metadata = {
        "schema": "libreevolve.parent_code_policy.v1",
        "max_chars": max_chars,
        "truncation": truncation,
        "source": (
            "prompt_context_policy"
            if prompt_policy_active
            else "default_full_parent_workspace"
        ),
        "path_policy": dict(path_metadata),
        "original_chars": original_chars,
        "rendered_chars": original_chars,
        "omitted_chars": 0,
        "truncated": False,
        "original_sha256": hashlib.sha256(parent_code.encode("utf-8")).hexdigest(),
        "rendered_sha256": hashlib.sha256(parent_code.encode("utf-8")).hexdigest(),
        "policy": "required_parent_code_channel_char_cap_v1",
    }
    if max_chars is None or original_chars <= max_chars:
        return parent_code, metadata
    if max_chars == 0:
        rendered = (
            "[parent code omitted by prompt context policy: "
            f"{original_chars} chars]"
        )
        omitted_chars = original_chars
    else:
        rendered = _truncate_parent_code_text(
            parent_code,
            max_chars,
            truncation=truncation,
        )
        omitted_chars = max(0, original_chars - len(rendered))
    metadata.update(
        {
            "rendered_chars": len(rendered),
            "omitted_chars": omitted_chars,
            "truncated": True,
            "rendered_sha256": hashlib.sha256(rendered.encode("utf-8")).hexdigest(),
        }
    )
    return rendered, metadata


def _truncate_parent_code_text(
    text: str,
    max_chars: int,
    *,
    truncation: str,
) -> str:
    if truncation != "head_tail":
        return _truncate_text(text, max_chars)
    if len(text) <= max_chars:
        return text
    notice = f"...[truncated {len(text) - max_chars} chars]..."
    keep = max(0, max_chars - len(notice))
    head_chars = (keep + 1) // 2
    tail_chars = keep - head_chars
    if tail_chars <= 0:
        return text[:head_chars] + notice
    return text[:head_chars] + notice + text[-tail_chars:]


def _required_prompt_chars_with_overhead(
    template: str,
    values: Mapping[str, object],
    *,
    rendered_chars: int,
) -> int:
    fields = prompt_template_field_occurrences(template)
    accounted_chars = 0
    required_chars = 0
    for field_name, occurrences in fields.items():
        chars = len(_prompt_section_text(values.get(field_name)))
        rendered_estimate = chars * occurrences
        accounted_chars += rendered_estimate
        if field_name in ALPHAEVOLVE_REQUIRED_PROMPT_CHANNELS:
            required_chars += rendered_estimate
    template_overhead_chars = max(0, rendered_chars - accounted_chars)
    return required_chars + template_overhead_chars


def _prompt_section_budget_report(
    template: str,
    values: Mapping[str, object],
    *,
    rendered_chars: int,
    max_chars: int | None,
    configured_max_chars: int | None = None,
    max_estimated_tokens: int | None = None,
    token_counter: Callable[[str], int] | None = None,
    token_counter_name: str = "provider",
    packing_metadata: Mapping[str, object] | None = None,
    section_priorities: Mapping[str, int] | None = None,
) -> dict:
    fields = prompt_template_field_occurrences(template)
    priorities = _effective_section_priorities(section_priorities)
    sections = []
    accounted_chars = 0
    required_chars = 0
    optional_chars = 0
    for field_name in sorted(
        fields,
        key=lambda name: (_prompt_section_priority(name, priorities), name),
    ):
        text = _prompt_section_text(values.get(field_name))
        chars = len(text)
        occurrences = fields[field_name]
        rendered_estimate = chars * occurrences
        accounted_chars += rendered_estimate
        required = field_name in ALPHAEVOLVE_REQUIRED_PROMPT_CHANNELS
        if required:
            required_chars += rendered_estimate
        else:
            optional_chars += rendered_estimate
        sections.append(
            {
                "name": field_name,
                "priority": _prompt_section_priority(field_name, priorities),
                "required": required,
                "occurrences": occurrences,
                "chars": chars,
                "estimated_tokens": _estimate_prompt_tokens(chars),
                "rendered_estimate_chars": rendered_estimate,
                "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            }
        )
        if token_counter is not None:
            sections[-1]["provider_tokens"] = _count_prompt_tokens(
                text,
                token_counter,
            )
    template_overhead_chars = max(0, rendered_chars - accounted_chars)
    effective_max_estimated_tokens = (
        max_estimated_tokens
        if max_estimated_tokens is not None
        else _estimate_prompt_tokens(max_chars)
        if max_chars is not None
        else None
    )
    required_with_overhead = required_chars + template_overhead_chars
    packing = dict(packing_metadata or {})
    report = {
        "schema": PROMPT_SECTION_BUDGET_SCHEMA,
        "policy": packing.get(
            "policy",
            PROMPT_SECTION_BUDGET_POLICY,
        ),
        "section_priority_source": (
            "prompt_context_policy"
            if section_priorities
            else "default_prompt_section_priorities"
        ),
        "packing_status": packing.get("packing_status", "unknown"),
        "packing": packing,
        "max_chars": max_chars,
        "configured_max_chars": configured_max_chars,
        "max_estimated_tokens": effective_max_estimated_tokens,
        "max_estimated_tokens_source": (
            "config.prompt_max_estimated_tokens"
            if max_estimated_tokens is not None
            else "heuristic_from_effective_max_chars"
            if max_chars is not None
            else "not_configured"
        ),
        "rendered_chars_before_cap": rendered_chars,
        "estimated_tokens_before_cap": _estimate_prompt_tokens(rendered_chars),
        "template_overhead_chars": template_overhead_chars,
        "required_section_chars": required_chars,
        "optional_section_chars": optional_chars,
        "required_sections_fit": (
            True if max_chars is None else required_with_overhead <= max_chars
        ),
        "section_count": len(sections),
        "sections": sections,
    }
    if token_counter is not None:
        rendered_prompt = template.format(**values)
        report.update(
            {
                "token_count_policy": "provider_token_counter",
                "provider_token_counter": token_counter_name,
                "provider_tokens_before_cap": _count_prompt_tokens(
                    rendered_prompt,
                    token_counter,
                ),
                "provider_tokens_limit": max_estimated_tokens,
                "provider_tokens_fit": (
                    True
                    if max_estimated_tokens is None
                    else _count_prompt_tokens(rendered_prompt, token_counter)
                    <= max_estimated_tokens
                ),
            }
        )
    else:
        report["token_count_policy"] = "heuristic_chars_per_token"
    return report


def prompt_template_field_occurrences(template: str) -> dict[str, int]:
    occurrences: dict[str, int] = {}
    try:
        parsed = list(string.Formatter().parse(template))
    except ValueError as exc:
        raise PromptTemplateError(f"malformed prompt template: {exc}") from exc
    for _, field_name, _, _ in parsed:
        if field_name is None:
            continue
        root = field_name.split(".", 1)[0].split("[", 1)[0]
        if root not in PROMPT_TEMPLATE_FIELDS:
            raise PromptTemplateError(f"unknown prompt template field {root!r}")
        occurrences[root] = occurrences.get(root, 0) + 1
    return occurrences


def _prompt_section_text(value: object) -> str:
    if isinstance(value, _PromptScore):
        return str(value)
    if value is None:
        return ""
    return str(value)


def _truncate_prompt_middle(prompt: str, max_chars: int) -> tuple[str, str]:
    marker = f"\n[... prompt truncated to {max_chars} characters ...]\n"
    if max_chars <= len(marker) + 2:
        return prompt[:max_chars], "prefix_truncate"
    task_anchor = prompt.rfind("\n[TASK]")
    available = max_chars - len(marker)
    if task_anchor >= 0:
        tail_target = min(len(prompt) - task_anchor, max(1, (available * 2) // 3))
    else:
        tail_target = max(1, max_chars // 3)
    tail_chars = min(tail_target, max(0, available // 2 if task_anchor < 0 else available))
    head_chars = max(0, available - tail_chars)
    omitted = max(0, len(prompt) - head_chars - tail_chars)
    marker = (
        f"\n[... prompt truncated to {max_chars} characters; "
        f"omitted {omitted} middle characters ...]\n"
    )
    available = max_chars - len(marker)
    if available <= 0:
        return prompt[:max_chars], "prefix_truncate"
    tail_chars = min(tail_target, max(0, available // 2 if task_anchor < 0 else available))
    head_chars = available - tail_chars
    if tail_chars == 0 or task_anchor >= 0 and head_chars <= 0:
        return prompt[:head_chars] + marker, "middle_truncate"
    if task_anchor >= 0:
        task_tail = prompt[task_anchor : task_anchor + tail_chars]
        return prompt[:head_chars] + marker + task_tail, "middle_truncate_preserve_task"
    return prompt[:head_chars] + marker + prompt[-tail_chars:], "middle_truncate_preserve_tail"


def _estimate_prompt_tokens(chars: int) -> int:
    return max(1, math.ceil(chars / 4)) if chars > 0 else 0


def validate_capture_proposal_metadata(value: object) -> bool:
    if not isinstance(value, bool):
        raise PromptTemplateError("capture_proposal_metadata must be boolean")
    return value


def validate_prompt_extra_context(value: object) -> str:
    if not isinstance(value, str):
        raise PromptTemplateError("extra_context must be text")
    text = redact_sensitive_text(value)
    if len(text) <= _MAX_EXTRA_CONTEXT_CHARS:
        return text
    return text[:_MAX_EXTRA_CONTEXT_CHARS] + "...[truncated]"


def _apply_extra_context_policy(
    extra_context: str,
    max_chars: int | None,
) -> tuple[str, dict[str, object]]:
    input_chars = len(extra_context)
    if max_chars is None:
        rendered = extra_context
        truncated = False
    else:
        rendered = extra_context[:max_chars]
        truncated = input_chars > max_chars
    return rendered, {
        "schema": "libreevolve.extra_context_policy.v1",
        "max_chars": max_chars,
        "input_chars": input_chars,
        "rendered_chars": len(rendered),
        "omitted_chars": max(0, input_chars - len(rendered)),
        "truncated": truncated,
        "selection_policy": (
            "all_validated_extra_context"
            if max_chars is None
            else "prefix_chars_after_validation"
        ),
    }


def validate_prompt_parent(value: object) -> Program:
    if not isinstance(value, Program):
        raise PromptTemplateError("parent must be a Program")
    return value


def validate_prompt_inspirations(value: object) -> list[Program]:
    if not isinstance(value, list):
        raise PromptTemplateError("inspirations must be a list of Program objects")
    for index, item in enumerate(value):
        if not isinstance(item, Program):
            raise PromptTemplateError(
                f"inspirations[{index}] must be a Program"
            )
    return value


def validate_prompt_variants(
    variants: object,
    *,
    prompt_format_options: object | None = None,
    semantic_policy: str = "compatibility",
) -> list[str]:
    if not isinstance(variants, list):
        raise PromptTemplateError("prompt variants must be a list of template strings")
    options = validate_prompt_format_options(prompt_format_options or {})
    policy = validate_prompt_variant_semantic_policy(semantic_policy)
    normalized: list[str] = []
    for index, template in enumerate(variants):
        if not isinstance(template, str):
            raise PromptTemplateError(
                f"prompt variants[{index}] must be a template string"
            )
        try:
            validate_prompt_template(template)
            validate_configured_prompt_template_semantics(
                template,
                semantic_policy=policy,
            )
            validate_prompt_format_markers(template, options)
        except PromptTemplateError as exc:
            raise PromptTemplateError(f"prompt variants[{index}]: {exc}") from exc
        normalized.append(template)
    return normalized


def validate_prompt_format_options(options: object) -> dict[str, list[dict[str, object]]]:
    if options is None:
        return {}
    if not isinstance(options, Mapping):
        raise PromptTemplateError("prompt_format_options must be a mapping")
    normalized: dict[str, list[dict[str, object]]] = {}
    for raw_name, raw_alternatives in options.items():
        if not isinstance(raw_name, str) or not _PROMPT_FORMAT_NAME_RE.fullmatch(raw_name):
            raise PromptTemplateError(
                "prompt_format_options keys must match "
                "[A-Za-z][A-Za-z0-9_-]{0,63}"
            )
        if redact_sensitive_text(raw_name) != raw_name:
            raise PromptTemplateError("prompt_format_options keys must not look secret-like")
        if raw_name in normalized:
            raise PromptTemplateError(f"duplicate prompt format option {raw_name!r}")
        if not isinstance(raw_alternatives, list) or not raw_alternatives:
            raise PromptTemplateError(
                f"prompt_format_options[{raw_name!r}] must be a non-empty list"
            )
        alternatives: list[dict[str, object]] = []
        for index, raw_alternative in enumerate(raw_alternatives):
            alternatives.append(
                _validate_prompt_format_alternative(
                    f"prompt_format_options[{raw_name!r}][{index}]",
                    raw_alternative,
                )
            )
        normalized[raw_name] = alternatives
    return normalized


def _validate_prompt_format_alternative(label: str, value: object) -> dict[str, object]:
    if isinstance(value, str):
        text = value
        weight = 1.0
    elif isinstance(value, Mapping):
        unsupported = [key for key in value if key not in {"text", "weight"}]
        if unsupported:
            formatted = ", ".join(sorted(repr(key) for key in unsupported))
            raise PromptTemplateError(f"{label} has unsupported fields [{formatted}]")
        if "text" not in value:
            raise PromptTemplateError(f"{label}.text is required")
        text = value["text"]
        weight = value.get("weight", 1.0)
    else:
        raise PromptTemplateError(f"{label} must be a string or mapping")
    if not isinstance(text, str) or not text:
        raise PromptTemplateError(f"{label}.text must be a non-empty string")
    if "[[prompt:" in text:
        raise PromptTemplateError(f"{label}.text must not contain nested prompt markers")
    validate_prompt_template_fragment(text)
    if isinstance(weight, bool) or not isinstance(weight, (int, float)):
        raise PromptTemplateError(f"{label}.weight must be a positive finite number")
    numeric_weight = float(weight)
    if not math.isfinite(numeric_weight) or numeric_weight <= 0:
        raise PromptTemplateError(f"{label}.weight must be a positive finite number")
    return {"text": text, "weight": numeric_weight}


def validate_prompt_format_markers(template: str, options: object) -> None:
    if not isinstance(template, str):
        raise PromptTemplateError("prompt template must be a non-empty string")
    format_options = validate_prompt_format_options(options)
    malformed = _PROMPT_FORMAT_MARKER_RE.sub("", template)
    if "[[prompt:" in malformed:
        raise PromptTemplateError("malformed stochastic prompt marker")
    missing = sorted(set(_PROMPT_FORMAT_MARKER_RE.findall(template)) - set(format_options))
    if missing:
        raise PromptTemplateError(
            f"missing prompt_format_options for stochastic markers {missing}"
        )


def render_prompt_format_options(
    template: str,
    options: object,
    rng: random.Random,
    *,
    weight_overrides: object | None = None,
) -> tuple[str, dict]:
    format_options = validate_prompt_format_options(options)
    overrides = validate_prompt_format_weight_overrides(
        weight_overrides or {},
        format_options,
    )
    validate_prompt_format_markers(template, format_options)
    names = _PROMPT_FORMAT_MARKER_RE.findall(template)
    if not names:
        return template, {"enabled": False, "selections": []}
    selected: dict[str, dict[str, object]] = {}
    selections: list[dict[str, object]] = []
    for name in dict.fromkeys(names):
        alternatives = format_options[name]
        if name in overrides:
            alternatives = [
                {**alternative, "weight": overrides[name][index]}
                for index, alternative in enumerate(alternatives)
            ]
        index, alternative = _weighted_prompt_format_choice(alternatives, rng)
        text = str(alternative["text"])
        selected[name] = {"text": text}
        selections.append(
            {
                "name": name,
                "choice_index": index,
                "weight": alternative["weight"],
                "weight_source": (
                    "prompt_context_policy"
                    if name in overrides
                    else "prompt_format_options"
                ),
                "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
                "occurrences": names.count(name),
            }
        )

    def replace(match: re.Match[str]) -> str:
        return str(selected[match.group(1)]["text"])

    return _PROMPT_FORMAT_MARKER_RE.sub(replace, template), {
        "enabled": True,
        "marker_syntax": "[[prompt:name]]",
        "selection_policy": "weighted_run_rng_reuse_by_marker_name",
        "weight_override_names": sorted(overrides),
        "selections": selections,
    }


def validate_prompt_format_weight_overrides(
    value: object,
    format_options: Mapping[str, list[dict[str, object]]],
) -> dict[str, list[float]]:
    overrides = _validate_prompt_context_prompt_format_weights(value)
    for name, weights in overrides.items():
        if name not in format_options:
            raise PromptTemplateError(
                "prompt context_policy.prompt_format_weights"
                f"[{name!r}] references unknown prompt_format_options key"
            )
        if len(weights) != len(format_options[name]):
            raise PromptTemplateError(
                "prompt context_policy.prompt_format_weights"
                f"[{name!r}] must have {len(format_options[name])} weights"
            )
    return overrides


def _weighted_prompt_format_choice(
    alternatives: list[dict[str, object]],
    rng: random.Random,
) -> tuple[int, dict[str, object]]:
    total = sum(float(item["weight"]) for item in alternatives)
    threshold = rng.random() * total
    cumulative = 0.0
    for index, alternative in enumerate(alternatives):
        cumulative += float(alternative["weight"])
        if threshold < cumulative:
            return index, alternative
    return len(alternatives) - 1, alternatives[-1]


def validate_direct_task_description(value: object) -> str:
    if not isinstance(value, str):
        raise PromptTemplateError("problem.task_description must be a non-empty string")
    if not value.strip():
        raise PromptTemplateError("problem.task_description must be a non-empty string")
    if len(value) > _MAX_TASK_DESCRIPTION_CHARS:
        raise PromptTemplateError(
            "problem.task_description must be at most "
            f"{_MAX_TASK_DESCRIPTION_CHARS} characters"
        )
    if redact_sensitive_text(value) != value:
        raise PromptTemplateError("problem.task_description must not contain secret-like text")
    if any(_unsafe_task_description_char(char) for char in value):
        raise PromptTemplateError(
            "problem.task_description contains unsafe control or Unicode surrogate characters"
        )
    return value


def _unsafe_task_description_char(char: str) -> bool:
    if char in {"\n", "\r", "\t"}:
        return False
    return ord(char) < 32 or ord(char) == 127 or unicodedata.category(char) == "Cs"


def validate_direct_context_files(value: object) -> dict[str, str]:
    if not value:
        if isinstance(value, Mapping) or value is None:
            return {}
    if not isinstance(value, Mapping):
        raise PromptTemplateError("problem.context_files must be a mapping of path to text")
    normalized: dict[str, str] = {}
    for raw_name, content in value.items():
        if not isinstance(raw_name, str) or not isinstance(content, str):
            raise PromptTemplateError("problem.context_files must map text paths to text")
        name = _validate_direct_context_label(raw_name)
        if name in normalized:
            raise PromptTemplateError(f"problem.context_files contains duplicate path {name!r}")
        if len(content) > _MAX_DIRECT_CONTEXT_CHARS:
            raise PromptTemplateError(
                "problem.context_files values must be at most "
                f"{_MAX_DIRECT_CONTEXT_CHARS} characters"
            )
        normalized[name] = content
    return normalized


def _render_context_with_metadata(
    problem: Problem,
    *,
    selected_paths: object = None,
    required_terms: object = None,
    excluded_terms: object = None,
    ranking_terms: object = None,
    source_limit: object = None,
    source_max_chars: object = None,
    truncation: object = "head",
    order_policy: object = "path_order",
) -> tuple[str, dict]:
    context_files = validate_direct_context_files(problem.context_files)
    policy_paths = _validate_prompt_context_source_paths(selected_paths)
    source_required_terms = _validate_prompt_context_source_terms(
        required_terms,
        "context_source_required_terms",
    )
    source_excluded_terms = _validate_prompt_context_source_terms(
        excluded_terms,
        "context_source_excluded_terms",
    )
    source_ranking_terms = _validate_prompt_context_source_terms(
        ranking_terms,
        "context_source_ranking_terms",
    )
    limit = _validate_prompt_context_source_limit(source_limit)
    max_chars = _validate_prompt_context_source_max_chars(source_max_chars)
    truncation_policy = _validate_prompt_context_source_truncation(truncation)
    source_order_policy = _validate_prompt_context_source_order_policy(order_policy)
    sources, source_metadata = _context_sources_by_path(
        getattr(problem, "context_sources", [])
    )
    full_order = sorted(context_files, key=str)
    if policy_paths:
        candidate_order = [name for name in policy_paths if name in context_files]
        omitted = [name for name in full_order if name not in set(candidate_order)]
        missing_policy_paths = [
            name for name in policy_paths if name not in context_files
        ]
        order_policy = "prompt_context_policy_order"
    else:
        candidate_order = full_order
        omitted = []
        missing_policy_paths = []
        order_policy = "path_sort"
    candidate_order, term_filter_metadata = _filter_context_source_paths_by_terms(
        context_files,
        candidate_order,
        required_terms=source_required_terms,
        excluded_terms=source_excluded_terms,
    )
    order = candidate_order
    ranking_metadata = _context_source_path_order_policy_metadata(
        source_order_policy,
        candidate_order,
    )
    if source_order_policy == "task_term_ranked":
        order, ranking_metadata = _rank_context_source_paths_by_task_terms(
            context_files,
            candidate_order,
            query_text=problem.task_description,
            ranking_terms=source_ranking_terms,
            max_chars=max_chars,
            truncation=truncation_policy,
        )
        order_policy = (
            "prompt_context_policy_paths_task_term_ranked"
            if policy_paths
            else "task_term_ranked"
        )
    pre_limit_order = list(order)
    if limit is None:
        limit_omitted_paths: list[str] = []
    else:
        limit_omitted_paths = order[limit:]
        order = order[:limit]
        ranking_metadata = _context_source_limit_order_policy_metadata(
            ranking_metadata,
            selected_order=order,
            omitted_order=limit_omitted_paths,
            source_limit=limit,
        )
    metadata = {
        "context_order_policy": order_policy,
        "context_order": order,
        "context_order_sha256": _stable_json_sha256(order),
        "context_source_order_policy": ranking_metadata,
        "context_policy_source_paths": list(policy_paths),
        "context_policy_missing_paths": missing_policy_paths,
        "context_policy_omitted_paths": omitted,
        "context_source_content_policy": {
            "schema": "libreevolve.context_source_content_policy.v1",
            "max_chars": max_chars,
            "truncation": truncation_policy,
            "selection_policy": (
                "all_loaded_context_source_text"
                if max_chars is None
                else f"{truncation_policy}_chars_after_context_validation"
            ),
        },
        **source_metadata,
        "context_source_missing_paths": [
            name for name in order if name not in sources
        ],
        "context_source_extra_paths": [
            redact_sensitive_text(name)
            for name in sorted(set(sources) - set(context_files), key=str)
        ],
    }
    if source_required_terms or source_excluded_terms:
        metadata["context_source_term_policy"] = term_filter_metadata
    if limit is not None:
        metadata["context_policy_source_limit"] = limit
        metadata["context_policy_limit_omitted_paths"] = [
            redact_sensitive_text(name) for name in limit_omitted_paths
        ]
        metadata["context_policy_pre_limit_order"] = pre_limit_order
        metadata["context_policy_pre_limit_order_sha256"] = _stable_json_sha256(
            pre_limit_order
        )
    if not context_files:
        metadata["context_source_content_policy"]["sources"] = []
        return "(none)", metadata
    rendered = []
    rendered_sources = []
    for name in order:
        content = context_files[name]
        rendered_content, truncated = _rendered_context_source_content(
            content,
            max_chars=max_chars,
            truncation=truncation_policy,
        )
        rendered_sources.append(
            {
                "path": redact_sensitive_text(name),
                "original_chars": len(content),
                "rendered_chars": len(rendered_content),
                "omitted_chars": max(0, len(content) - len(rendered_content)),
                "truncated": truncated,
            }
        )
        rendered.append(
            "\n".join(
                [
                    _render_context_header(name, sources.get(name)),
                    f"Content-Characters: {len(rendered_content)}",
                    f"Original-Content-Characters: {len(content)}",
                    "Content-JSON:",
                    json.dumps(rendered_content),
                ]
            )
        )
    metadata["context_source_content_policy"]["sources"] = rendered_sources
    return "\n\n".join(rendered), metadata


def _rendered_context_source_content(
    content: str,
    *,
    max_chars: int | None,
    truncation: str,
) -> tuple[str, bool]:
    if max_chars is None:
        return content, False
    return (
        _truncate_context_source_content(
            content,
            max_chars=max_chars,
            truncation=truncation,
        ),
        len(content) > max_chars,
    )


def _filter_context_source_paths_by_terms(
    context_files: Mapping[str, str],
    order: list[str],
    *,
    required_terms: list[str],
    excluded_terms: list[str],
) -> tuple[list[str], dict]:
    required = set(required_terms)
    excluded = set(excluded_terms)
    required_filtered: list[str] = []
    required_omitted: list[str] = []
    for path in order:
        terms = _context_source_terms(context_files.get(path, ""))
        if required and not required.issubset(terms):
            required_omitted.append(path)
            continue
        required_filtered.append(path)
    final_order: list[str] = []
    excluded_omitted: list[str] = []
    for path in required_filtered:
        terms = _context_source_terms(context_files.get(path, ""))
        if excluded and terms.intersection(excluded):
            excluded_omitted.append(path)
            continue
        final_order.append(path)
    return final_order, {
        "schema": "libreevolve.context_source_term_policy.v1",
        "required_terms": list(required_terms),
        "excluded_terms": list(excluded_terms),
        "available_count": len(order),
        "required_matching_count": len(required_filtered),
        "required_filtered_count": len(required_omitted),
        "required_omitted_paths": [
            redact_sensitive_text(path) for path in required_omitted
        ],
        "required_policy": (
            "all_required_terms_in_loaded_source_v1" if required else "none"
        ),
        "excluded_matching_count": len(excluded_omitted),
        "excluded_filtered_count": len(excluded_omitted),
        "excluded_omitted_paths": [
            redact_sensitive_text(path) for path in excluded_omitted
        ],
        "excluded_policy": (
            "any_excluded_term_in_loaded_source_v1" if excluded else "none"
        ),
        "selected_count": len(final_order),
        "selection_sha256": _stable_json_sha256(
            {
                "selected_order": final_order,
                "required_omitted": required_omitted,
                "excluded_omitted": excluded_omitted,
                "required_terms": list(required_terms),
                "excluded_terms": list(excluded_terms),
            }
        ),
    }


def _context_source_path_order_policy_metadata(policy: str, order: list[str]) -> dict:
    return {
        "schema": "libreevolve.context_source_order_policy.v1",
        "policy": policy,
        "ranking_policy": "path_order_v1",
        "candidate_count": len(order),
        "selected_count": len(order),
        "query_terms_sha256": hashlib.sha256(b"").hexdigest(),
        "query_term_count": 0,
        "ranking_sha256": _stable_json_sha256(
            [
                {"path": redact_sensitive_text(path), "rank": index + 1}
                for index, path in enumerate(order)
            ]
        ),
        "selected_sources": [
            {
                "path": redact_sensitive_text(path),
                "rank": index + 1,
                "score": None,
                "original_index": index,
            }
            for index, path in enumerate(order)
        ],
    }


def _context_source_limit_order_policy_metadata(
    metadata: dict,
    *,
    selected_order: list[str],
    omitted_order: list[str],
    source_limit: int,
) -> dict:
    updated = dict(metadata)
    selected = set(selected_order)
    omitted = set(omitted_order)
    ranked_sources = [
        dict(source)
        for source in metadata.get("selected_sources", [])
        if isinstance(source, dict)
    ]
    updated["source_limit"] = source_limit
    updated["pre_limit_selected_count"] = len(ranked_sources)
    updated["selected_count"] = len(selected_order)
    updated["omitted_count"] = len(omitted_order)
    updated["selected_sources"] = [
        source for source in ranked_sources if source.get("path") in selected
    ]
    updated["omitted_sources"] = [
        source for source in ranked_sources if source.get("path") in omitted
    ]
    updated["selection_policy"] = "ranked_sources_limited_after_ordering_v1"
    updated["selection_sha256"] = _stable_json_sha256(
        {
            "selected_order": selected_order,
            "omitted_order": omitted_order,
            "source_limit": source_limit,
        }
    )
    return updated


def _rank_context_source_paths_by_task_terms(
    context_files: Mapping[str, str],
    order: list[str],
    *,
    query_text: str,
    ranking_terms: list[str],
    max_chars: int | None,
    truncation: str,
) -> tuple[list[str], dict]:
    if ranking_terms:
        query_terms = list(ranking_terms)
        query_source = "context_source_ranking_terms"
    else:
        query_terms = _context_source_order_query_terms(query_text)
        query_source = "task_description"
    query_hash = hashlib.sha256(" ".join(query_terms).encode("utf-8")).hexdigest()
    candidates = []
    for original_index, path in enumerate(order):
        rendered_content, _ = _rendered_context_source_content(
            context_files[path],
            max_chars=max_chars,
            truncation=truncation,
        )
        candidates.append(
            {
                "path": path,
                "score": _context_source_order_score(rendered_content, query_terms)
                if query_terms
                else 0,
                "original_index": original_index,
                "rendered_chars": len(rendered_content),
            }
        )
    ranked = sorted(
        candidates,
        key=lambda item: (-item["score"], item["original_index"], item["path"]),
    )
    ranked_paths = [str(item["path"]) for item in ranked]
    selected_sources = [
        {
            "path": redact_sensitive_text(str(item["path"])),
            "rank": rank,
            "score": int(item["score"]),
            "original_index": int(item["original_index"]),
            "rendered_chars": int(item["rendered_chars"]),
        }
        for rank, item in enumerate(ranked, start=1)
    ]
    metadata = {
        "schema": "libreevolve.context_source_order_policy.v1",
        "policy": "task_term_ranked",
        "ranking_policy": "term_overlap_rendered_context_v1",
        "query_source": query_source,
        "candidate_count": len(candidates),
        "selected_count": len(selected_sources),
        "query_terms_sha256": query_hash,
        "query_term_count": len(query_terms),
        "ranking_sha256": _stable_json_sha256(selected_sources),
        "selected_sources": selected_sources,
    }
    if ranking_terms:
        metadata["configured_query_terms"] = list(query_terms)
    if not query_terms:
        metadata["ranking_fallback"] = "empty_query_terms"
    return ranked_paths, metadata


def _context_source_order_query_terms(text: str) -> list[str]:
    terms = _context_source_terms(text)
    return sorted(terms)[:256]


def _context_source_terms(text: str) -> set[str]:
    return {
        match.group(0).lower()
        for match in re.finditer(r"[A-Za-z0-9_]{3,}", text)
    }


def _context_source_order_score(text: str, query_terms: list[str]) -> int:
    source_terms = _context_source_terms(text)
    return sum(1 for term in query_terms if term in source_terms)


def _truncate_context_source_content(
    content: str,
    *,
    max_chars: int,
    truncation: str,
) -> str:
    if len(content) <= max_chars:
        return content
    if max_chars <= 0:
        return ""
    if truncation == "head_tail":
        head_chars = (max_chars + 1) // 2
        tail_chars = max_chars - head_chars
        if tail_chars <= 0:
            return content[:head_chars]
        return content[:head_chars] + content[-tail_chars:]
    return content[:max_chars]


def _context_sources_by_path(value: object) -> tuple[dict[str, dict], dict]:
    grouped: dict[str, list[dict]] = {}
    if isinstance(value, list):
        for source in value:
            if not isinstance(source, dict):
                continue
            path = source.get("path")
            if not isinstance(path, str):
                continue
            grouped.setdefault(path, []).append(source)
    sources: dict[str, dict] = {}
    duplicate_paths: list[str] = []
    for path in sorted(grouped, key=str):
        candidates = sorted(grouped[path], key=_context_source_selection_key)
        sources[path] = candidates[0]
        if len(candidates) > 1:
            duplicate_paths.append(redact_sensitive_text(path))
    metadata = {
        "context_source_selection_policy": "path_sort_canonical_first",
        "context_source_paths": [
            redact_sensitive_text(path) for path in sorted(sources, key=str)
        ],
        "context_source_duplicate_paths": duplicate_paths,
    }
    return sources, metadata


def _context_source_selection_key(source: dict) -> str:
    return json.dumps(
        _stable_prompt_metadata_value(source),
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )


def _stable_prompt_metadata_value(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _stable_prompt_metadata_value(inner)
            for key, inner in sorted(value.items(), key=lambda item: str(item[0]))
        }
    if isinstance(value, list):
        return [_stable_prompt_metadata_value(item) for item in value]
    if isinstance(value, tuple):
        return [_stable_prompt_metadata_value(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def _stable_json_sha256(value: object) -> str:
    payload = json.dumps(
        _stable_prompt_metadata_value(value),
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _render_context_header(name: str, source: dict | None) -> str:
    name_text = _short(name, max_chars=160) or "context"
    if not source:
        return f"--- CONTEXT SOURCE: {name_text} ---"
    sha = _context_sha_text(source.get("sha256"))
    span = _context_excerpt_span_text(source)
    status = _short(source.get("extraction_status", "unknown"), max_chars=80) or "unknown"
    page_reference = _format_page_reference(source)
    pages = f", pages={page_reference}" if page_reference else ""
    role_reference = _context_source_role_reference(source)
    role = f", role={role_reference}" if role_reference else ""
    chars = _nonnegative_int_text(source.get("chars_original"))
    return (
        f"--- CONTEXT SOURCE: {name_text} "
        f"(sha256={sha}, chars={chars}, "
        f"excerpt={span}{pages}{role}, status={status}) ---"
    )


def _context_source_role_reference(source: dict) -> str:
    role = source.get("source_role")
    if not isinstance(role, Mapping):
        return ""
    role_name = _short(role.get("role"), max_chars=80)
    topic = _short(role.get("topic"), max_chars=120)
    if role_name and topic:
        return f"{role_name}:{topic}"
    return role_name


def _context_sha_text(value: object) -> str:
    text = _short(value, max_chars=64)
    if not text:
        return "unknown"
    return text[:12]


def _context_excerpt_span_text(source: dict) -> str:
    span_text = _format_excerpt_spans(source.get("excerpt_spans"))
    if span_text:
        return span_text
    start = source.get("excerpt_start", 0)
    end = source.get("excerpt_end")
    if (
        isinstance(start, int)
        and not isinstance(start, bool)
        and start >= 0
        and isinstance(end, int)
        and not isinstance(end, bool)
        and end >= start
    ):
        return f"{start}:{end}"
    if (
        isinstance(start, int)
        and not isinstance(start, bool)
        and start >= 0
        and end is None
    ):
        return f"{start}:?"
    return "?:?"


def _format_excerpt_spans(spans: object) -> str:
    if not isinstance(spans, list) or not spans:
        return ""
    parts: list[str] = []
    for span in spans:
        if not isinstance(span, dict):
            continue
        start = span.get("start")
        end = span.get("end")
        if (
            isinstance(start, int)
            and not isinstance(start, bool)
            and start >= 0
            and isinstance(end, int)
            and not isinstance(end, bool)
            and end >= start
        ):
            parts.append(f"{start}:{end}")
    return ",".join(parts)


def _nonnegative_int_text(value: object) -> str:
    if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
        return str(value)
    return "?"


def _format_page_reference(source: dict) -> str:
    span_reference = _format_page_spans(source.get("excerpt_page_spans"))
    if span_reference:
        return span_reference
    if "excerpt_pages" in source:
        return _format_page_list(source.get("excerpt_pages"))
    return _format_page_range(source.get("pages"))


def _format_page_spans(spans: object) -> str:
    if not isinstance(spans, list) or not spans:
        return ""
    parts: list[str] = []
    for span in spans:
        if not isinstance(span, dict):
            continue
        page = span.get("page")
        start = span.get("page_excerpt_start")
        end = span.get("page_excerpt_end")
        if start is None and end is None:
            start = span.get("excerpt_start")
            end = span.get("excerpt_end")
        if not _is_positive_int(page):
            continue
        if isinstance(start, int) and isinstance(end, int):
            if not isinstance(start, bool) and not isinstance(end, bool) and start >= 0 and end >= start:
                parts.append(f"{page}:{start}-{end}")
        else:
            parts.append(str(page))
    return ",".join(parts)


def _format_page_list(pages: object) -> str:
    if not isinstance(pages, list) or not pages:
        return ""
    numeric_pages = sorted({page for page in pages if _is_positive_int(page)})
    if not numeric_pages:
        return ""
    ranges: list[str] = []
    start = previous = numeric_pages[0]
    for page in numeric_pages[1:]:
        if page == previous + 1:
            previous = page
            continue
        ranges.append(_format_page_range_part(start, previous))
        start = previous = page
    ranges.append(_format_page_range_part(start, previous))
    return ",".join(ranges)


def _format_page_range(pages: object) -> str:
    if not isinstance(pages, list) or not pages:
        return ""
    numeric_pages = sorted({page for page in pages if _is_positive_int(page)})
    if not numeric_pages:
        return ""
    return _format_page_range_part(numeric_pages[0], numeric_pages[-1])


def _format_page_range_part(start: int, end: int) -> str:
    if start == end:
        return str(start)
    return f"{start}-{end}"


def _is_positive_int(value: object) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _render_mutation_instructions(
    mutation_mode: str,
    capture_proposal_metadata: bool = False,
    instruction_variant: str = "default",
    include_example: bool = True,
) -> str:
    instruction_variant = _validate_prompt_context_mutation_instruction_variant(
        instruction_variant
    )
    include_example = _validate_prompt_context_mutation_instruction_include_example(
        include_example
    )
    proposal = ""
    if capture_proposal_metadata:
        proposal = """Before the patch, include up to three proposal metadata sections.
Use short one-line fields when possible:
IDEA: one sentence naming the proposed improvement.
RATIONALE: one sentence explaining why it should help.
HYPOTHESIS: one sentence predicting the measured effect.
For multiline metadata, use bounded blocks such as:
[IDEA]
brief multiline idea text
[/IDEA]
Do not wrap colon-style metadata fields onto continuation lines.
If you add a separate explanation after metadata, put a blank line before it.
Then include the patch in the required format.
"""
    if mutation_mode == "full":
        if instruction_variant == "minimal":
            return proposal + """Return only the required full replacement content.
Use <<<FILE path ... >>>FILE for multi-file edits or topology commands.
For a single primary file, return the complete replacement file or changed
evolve-block body as appropriate.
Rules: No markdown fences. Optional brief leading explanation before the first
mutation marker is allowed. No prose between or after mutation markers. No
SEARCH/REPLACE blocks."""
        exploratory = ""
        if instruction_variant == "exploratory":
            exploratory = (
                "Prefer a coherent higher-upside change when the evidence supports it; "
                "include all matching helpers, imports, files, and block updates in the "
                "same response.\n"
            )
        return proposal + """Return full replacement code, not SEARCH/REPLACE diffs.
For multi-file candidates, wrap each changed file as:
<<<FILE path/to/file.py
complete replacement file content for files without evolve blocks; for files
with evolve blocks, include a raw one-block body or named <<<BLOCK ...>>>BLOCK
sections
>>>FILE
Use topology commands when needed:
<<<FILE DELETE path/to/obsolete.py
>>>FILE
<<<FILE MOVE old/path.py -> new/path.py
>>>FILE
<<<FILE PRIMARY path/to/main.py
>>>FILE
For a single-file candidate without evolve blocks, return only the complete
replacement primary file. If the file has one evolve block, return only the
replacement block body or a named block section. If it has multiple evolve
blocks, return one section per changed block:
<<<BLOCK block_name
replacement block body
>>>BLOCK
""" + exploratory + """\
Keep all proposed edits consistent with each other: if one replacement uses a
new helper, config value, file, import, or block name, include the matching
definition or topology change in the same response.
Rules: No markdown fences. Optional brief leading explanation before the first
mutation marker is allowed. No prose between or after mutation markers. No
SEARCH/REPLACE blocks."""
    if instruction_variant == "minimal":
        return proposal + """Return only the required patch.
Use SEARCH/REPLACE fences for ordinary edits and <<<FILE ... >>>FILE sections
for multi-file or topology changes.
Rules: No comments inside the patch. No markdown fences. Optional brief leading
explanation before the first mutation marker is allowed. No prose between or
after mutation markers."""
    exploratory = ""
    if instruction_variant == "exploratory":
        exploratory = (
            "Prefer a coherent higher-upside change when the evidence supports it; "
            "include all matching helpers, imports, files, and topology edits in the "
            "same response.\n"
        )
    instructions = proposal + """For multi-file candidates, wrap each file edit in
`<<<FILE path ... >>>FILE`; otherwise edit the current primary file.
Use either compact `<<<SEARCH` / `>>>REPLACE` fences or AlphaEvolve-style
`<<<<<<< SEARCH` / `>>>>>>> REPLACE` fences.
For workspace topology changes, use command file sections such as
`<<<FILE DELETE path/to/file.py ... >>>FILE`,
`<<<FILE MOVE old/path.py -> new/path.py ... >>>FILE`, or
`<<<FILE PRIMARY path/to/main.py ... >>>FILE`.
""" + exploratory + """\
Keep all proposed edits consistent with each other: if one replacement uses a
new helper, config value, file, import, or block name, include the matching
definition or topology change in the same response.
Rules: No comments inside the patch. No markdown fences. Optional brief leading
explanation before the first mutation marker is allowed. No prose between or
after mutation markers.
If metadata sections are requested, keep them outside the patch."""
    if not include_example:
        return instructions
    return instructions + """

Example format (do NOT copy this, use actual code from the program above):
<<<SEARCH
def foo():
    return 1
===
def foo():
    return 2
>>>REPLACE"""


def _render_metrics(
    program: Program,
    problem: Problem | None = None,
    *,
    selected_names: list[str] | tuple[str, ...] | None = None,
    max_chars_by_name: Mapping[str, int] | None = None,
) -> str:
    if not program.metrics:
        return "(none)"
    selected = set(selected_names) if selected_names is not None else None
    caps = dict(max_chars_by_name or {})
    ordered_keys = _prompt_metric_keys(program, problem)
    rendered: list[str] = []
    seen: dict[str, int] = {}
    for key in ordered_keys:
        raw_key = str(key)
        if selected is not None and raw_key not in selected:
            continue
        display_key = _metric_key_text(raw_key)
        count = seen.get(display_key, 0)
        seen[display_key] = count + 1
        if count:
            display_key = f"{display_key}__{count + 1}"
        entry = _render_metric_entry(
            program,
            problem,
            raw_key,
            display_key,
            program.metrics[key],
        )
        cap = caps.get(raw_key)
        if cap is not None:
            entry = _short(entry, max_chars=cap) if cap > 0 else ""
        if entry:
            rendered.append(entry)
    return ", ".join(rendered) or "(none)"


def _prompt_metric_keys(program: Program, problem: Problem | None) -> list[object]:
    if problem is None:
        return list(program.metrics)
    declared_order = _declared_metric_order(problem)
    allowed = set(declared_order)
    allowed.update(_feedback_metric_names(program))
    return [key for key in declared_order if key in program.metrics] + [
        key
        for key in program.metrics
        if str(key) in allowed and str(key) not in declared_order
    ]


def _feedback_metric_names(program: Program) -> set[str]:
    evaluation = program.evaluation if isinstance(program.evaluation, dict) else {}
    metadata = evaluation.get("metadata") if isinstance(evaluation.get("metadata"), dict) else {}
    feedback_records = metadata.get("llm_feedback")
    if not isinstance(feedback_records, list):
        return set()
    names: set[str] = set()
    for record in feedback_records:
        if not isinstance(record, dict):
            continue
        metric = record.get("metric")
        if isinstance(metric, str) and _METRIC_LABEL_RE.fullmatch(metric):
            names.add(metric)
    return names


def _render_metric_entry(
    program: Program,
    problem: Problem | None,
    raw_key: str,
    display_key: str,
    value: object,
) -> str:
    value_text = _metric_value_text(value)
    if raw_key == "is_valid":
        return f"{display_key}={value_text} (validity)"
    if raw_key == "feedback_adjusted_fitness":
        return f"{display_key}={value_text} (feedback-adjusted fitness)"
    metric = _problem_metric(problem, raw_key)
    if not metric:
        return f"{display_key}={value_text}"
    role = "primary" if metric.get("primary") else "secondary"
    direction = str(metric.get("direction", "maximize"))
    lo, hi = _metric_bounds_text(metric)
    normalized = _normalized_metric_text(program, problem, raw_key, value)
    bounds = metric["bounds"]
    range_status = _metric_range_status(value, float(bounds[0]), float(bounds[1]))
    return (
        f"{display_key}={value_text} "
        f"({role}, {direction}, bounds=[{lo}, {hi}], normalized={normalized}"
        f"{range_status})"
    )


def _declared_metric_order(problem: Problem | None) -> list[str]:
    if problem is None:
        return ["score", "is_valid", "feedback_adjusted_fitness"]
    names = [
        str(metric.get("name"))
        for metric in getattr(problem, "metrics", [])
        if isinstance(metric, Mapping) and metric.get("name") is not None
    ]
    return names + ["is_valid", "feedback_adjusted_fitness"]


def _problem_metric(problem: Problem | None, name: str) -> Mapping[str, object]:
    if problem is None:
        return {}
    try:
        return problem.metric(name)
    except KeyError:
        return {}


def _metric_key_text(value: str) -> str:
    redacted = _short(value, max_chars=_MAX_METRIC_FIELD_CHARS)
    if not redacted:
        return "metric"
    if _METRIC_LABEL_RE.fullmatch(redacted):
        return redacted
    return redacted.replace(",", "_").replace("\n", "_")


def _metric_value_text(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        numeric = float(value)
        if math.isfinite(numeric):
            return str(value)
        if math.isnan(numeric):
            return "<non_finite:nan>"
        if numeric > 0:
            return "<non_finite:infinity>"
        return "<non_finite:negative_infinity>"
    return _short(value, max_chars=_MAX_METRIC_FIELD_CHARS) or "<empty>"


def _metric_bounds_text(metric: Mapping[str, object]) -> tuple[str, str]:
    raw_bounds = metric.get("bounds", [0.0, 1.0])
    return (
        _metric_number_text(float(raw_bounds[0])),
        _metric_number_text(float(raw_bounds[1])),
    )


def _normalized_metric_text(
    program: Program,
    problem: Problem,
    name: str,
    value: object,
) -> str:
    metadata = program.metadata if isinstance(program.metadata, dict) else {}
    normalized_metrics = metadata.get("normalized_metrics")
    if isinstance(normalized_metrics, dict):
        normalized = normalized_metrics.get(name)
        if _is_finite_non_bool_number(normalized):
            return _metric_number_text(float(normalized), precision=4)
    if not _is_finite_non_bool_number(value):
        return "unavailable"
    return _metric_number_text(problem.normalize_metric(name, float(value)), precision=4)


def _metric_range_status(value: object, lo: float, hi: float) -> str:
    if not _is_finite_non_bool_number(value):
        return ", range=invalid"
    numeric = float(value)
    if numeric < lo or numeric > hi:
        return ", range=out_of_bounds"
    return ""


def _is_finite_non_bool_number(value: object) -> bool:
    return (
        not isinstance(value, bool)
        and isinstance(value, (int, float))
        and math.isfinite(float(value))
    )


def _metric_number_text(value: float, *, precision: int | None = None) -> str:
    if precision is not None:
        return f"{value:.{precision}f}"
    return f"{value:g}"


def _fitness_text(value: object) -> str:
    if _is_finite_non_bool_number(value):
        return f"{float(value):.4f}"
    return _invalid_score_text(value)


def _invalid_score_text(value: object) -> str:
    if isinstance(value, bool):
        return "<invalid_fitness:bool>"
    if isinstance(value, (int, float)):
        numeric = float(value)
        if math.isnan(numeric):
            return "<invalid_fitness:nan>"
        if numeric > 0:
            return "<invalid_fitness:infinity>"
        return "<invalid_fitness:negative_infinity>"
    if value is None:
        return "<invalid_fitness:none>"
    return f"<invalid_fitness:{type(value).__name__}>"


def _render_proposal(
    program: Program,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    proposal = program.metadata.get("proposal") if isinstance(program.metadata, dict) else None
    if not isinstance(proposal, dict):
        return ""
    selected_fields = _validate_prompt_context_proposal_fields(fields)
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_proposal_max_chars_by_field(
        max_chars_by_field
    )
    lines = []
    for field_name in selected_fields:
        value = _short_proposal_field(proposal.get(field_name), field_name, field_caps)
        if value:
            lines.append(f"- {field_name}={_json_text(value)}")
    return "\n".join(lines)


def _short_proposal_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(value, max_chars=max_chars if max_chars is not None else 240)


def _render_program_files(program: Program) -> str:
    rendered, _metadata = _render_program_files_with_metadata(program)
    return rendered


def _render_program_files_with_metadata(
    program: Program,
    *,
    selected_paths: object = None,
    required_terms: object = None,
    excluded_terms: object = None,
    ranking_terms: object = None,
    order_policy: object = "path_order",
    file_limit: object = None,
    max_chars_by_path: object = None,
    query_text: str = "",
) -> tuple[str, dict]:
    workspace = program.workspace()
    policy_paths = _validate_prompt_context_parent_code_paths(selected_paths)
    parent_required_terms = _validate_prompt_context_source_terms(
        required_terms,
        "parent_code_required_terms",
    )
    parent_excluded_terms = _validate_prompt_context_source_terms(
        excluded_terms,
        "parent_code_excluded_terms",
    )
    parent_ranking_terms = _validate_prompt_context_source_terms(
        ranking_terms,
        "parent_code_ranking_terms",
    )
    parent_order_policy = _validate_prompt_context_parent_code_order_policy(
        order_policy
    )
    parent_code_limit = _validate_prompt_context_parent_code_limit(file_limit)
    content_caps = _validate_prompt_context_parent_code_max_chars_by_path(
        max_chars_by_path
    )
    all_paths = sorted(workspace.files)
    if policy_paths:
        candidate_paths = [path for path in policy_paths if path in workspace.files]
        missing_paths = [path for path in policy_paths if path not in workspace.files]
        omitted_by_path_policy = [path for path in all_paths if path not in set(candidate_paths)]
        path_order_policy = "prompt_context_policy_order"
    else:
        candidate_paths = all_paths
        missing_paths = []
        omitted_by_path_policy = []
        path_order_policy = "path_sort"
    rendered_paths, term_filter_metadata = _filter_parent_code_paths_by_terms(
        workspace.files,
        candidate_paths,
        required_terms=parent_required_terms,
        excluded_terms=parent_excluded_terms,
    )
    parent_order_metadata = _parent_code_path_order_policy_metadata(
        "path_order",
        rendered_paths,
    )
    if parent_order_policy == "task_term_ranked":
        rendered_paths, parent_order_metadata = _rank_parent_code_paths_by_terms(
            workspace.files,
            rendered_paths,
            query_text=query_text,
            ranking_terms=parent_ranking_terms,
        )
        path_order_policy = (
            "prompt_context_policy_paths_task_term_ranked"
            if policy_paths
            else "task_term_ranked"
        )
    pre_limit_rendered_paths = list(rendered_paths)
    if parent_code_limit is None:
        omitted_by_limit: list[str] = []
    else:
        omitted_by_limit = rendered_paths[parent_code_limit:]
        rendered_paths = rendered_paths[:parent_code_limit]
        parent_order_metadata = _parent_code_limit_order_policy_metadata(
            parent_order_metadata,
            selected_order=rendered_paths,
            omitted_order=omitted_by_limit,
            parent_code_limit=parent_code_limit,
        )
    omitted_by_required_terms = list(
        term_filter_metadata["omitted_by_required_terms"]
    )
    omitted_by_excluded_terms = list(
        term_filter_metadata["omitted_by_excluded_terms"]
    )
    omitted_paths = (
        list(omitted_by_path_policy)
        + omitted_by_required_terms
        + omitted_by_excluded_terms
        + omitted_by_limit
    )
    policy_active = bool(
        policy_paths
        or parent_required_terms
        or parent_excluded_terms
        or parent_ranking_terms
        or parent_order_policy != "path_order"
        or parent_code_limit is not None
        or content_caps
    )
    content_policy_records: list[dict] = []
    metadata = {
        "schema": "libreevolve.parent_code_paths.v1",
        "source": "prompt_context_policy" if policy_active else "default_all_files",
        "requested_paths": list(policy_paths),
        "required_terms": list(parent_required_terms),
        "excluded_terms": list(parent_excluded_terms),
        "ranking_terms": list(parent_ranking_terms),
        "parent_code_order_policy": parent_order_metadata,
        "parent_code_limit": parent_code_limit,
        "max_chars_by_path": dict(content_caps),
        "unused_content_cap_paths": [
            path for path in sorted(content_caps) if path not in set(rendered_paths)
        ],
        "pre_limit_rendered_paths": pre_limit_rendered_paths,
        "rendered_paths": list(rendered_paths),
        "omitted_paths": omitted_paths,
        "omitted_by_path_policy": omitted_by_path_policy,
        "omitted_by_required_terms": omitted_by_required_terms,
        "omitted_by_excluded_terms": omitted_by_excluded_terms,
        "omitted_by_limit": omitted_by_limit,
        "missing_paths": missing_paths,
        "order_policy": path_order_policy,
        "term_filter": term_filter_metadata,
        "primary_file": workspace.primary_file,
        "file_count": len(workspace.files),
        "rendered_file_count": len(rendered_paths),
        "omitted_file_count": len(omitted_paths),
        "missing_file_count": len(missing_paths),
        "static_file_count": len(workspace.static_files),
    }
    rendered = [
        "[PROGRAM WORKSPACE]",
        f"Primary file: {_short(workspace.primary_file, max_chars=160)}",
        f"File count: {len(workspace.files)}",
    ]
    if policy_active:
        rendered.append(f"Rendered mutable file count: {len(rendered_paths)}")
    if workspace.static_files:
        rendered.append(f"Static file count: {len(workspace.static_files)}")
        for item in workspace.static_files:
            rendered.append(
                "--- STATIC FILE "
                f"path={_short(str(item['path']), max_chars=160)} "
                f"kind={_short(str(item['kind']), max_chars=40)} "
                f"source={_short(str(item.get('source_kind', 'unknown')), max_chars=80)} "
                f"mutation={_short(str(item.get('mutation_policy', 'immutable')), max_chars=80)} "
                f"bytes={item['bytes']} "
                f"sha256={item['sha256']} ---"
            )
            if item.get("source_path"):
                rendered.append(
                    f"Static source path: {_short(str(item['source_path']), max_chars=160)}"
                )
    for path in rendered_paths:
        content = workspace.files[path]
        role = "primary" if path == workspace.primary_file else "support"
        path_text = _short(path, max_chars=160) or "unknown"
        original_content_text = content if isinstance(content, str) else str(content)
        max_chars = content_caps.get(path)
        if max_chars is None:
            content_text = original_content_text
        elif max_chars == 0:
            content_text = ""
        else:
            content_text = _truncate_parent_file_content(
                original_content_text,
                max_chars,
            )
        content_policy_records.append(
            {
                "path": path,
                "max_chars": max_chars,
                "original_chars": len(original_content_text),
                "rendered_chars": len(content_text),
                "omitted_chars": max(0, len(original_content_text) - len(content_text)),
                "truncated": len(content_text) < len(original_content_text),
            }
        )
        rendered.extend(
            [
                f"--- FILE path={path_text} role={role} chars={len(original_content_text)} ---",
                "Content-JSON:",
                json.dumps(content_text),
            ]
        )
    if omitted_paths:
        rendered.append(
            "Omitted mutable files: "
            + json.dumps(omitted_paths, sort_keys=True)
        )
    if missing_paths:
        rendered.append(
            "Missing requested mutable files: "
            + json.dumps(missing_paths, sort_keys=True)
        )
    metadata["content_policy"] = content_policy_records
    return "\n".join(rendered), metadata


def _truncate_parent_file_content(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    notice = f"...[truncated {len(text) - max_chars} chars]"
    if len(notice) >= max_chars:
        return notice[:max_chars]
    keep = max_chars - len(notice)
    return text[:keep] + notice


def _filter_parent_code_paths_by_terms(
    files: Mapping[str, str],
    paths: list[str],
    *,
    required_terms: list[str],
    excluded_terms: list[str],
) -> tuple[list[str], dict]:
    selected: list[str] = []
    omitted_by_required_terms: list[str] = []
    omitted_by_excluded_terms: list[str] = []
    for path in paths:
        content = files.get(path, "")
        haystack = f"{path}\n{content}".lower()
        missing_required = [term for term in required_terms if term not in haystack]
        if missing_required:
            omitted_by_required_terms.append(path)
            continue
        matched_excluded = [term for term in excluded_terms if term in haystack]
        if matched_excluded:
            omitted_by_excluded_terms.append(path)
            continue
        selected.append(path)
    metadata = {
        "schema": "libreevolve.parent_code_term_filter.v1",
        "required_terms": list(required_terms),
        "excluded_terms": list(excluded_terms),
        "candidate_count": len(paths),
        "selected_count": len(selected),
        "omitted_by_required_terms": omitted_by_required_terms,
        "omitted_by_excluded_terms": omitted_by_excluded_terms,
        "omitted_count": len(omitted_by_required_terms)
        + len(omitted_by_excluded_terms),
        "selection_sha256": _stable_json_sha256(
            {
                "required_terms": required_terms,
                "excluded_terms": excluded_terms,
                "selected": selected,
                "omitted_by_required_terms": omitted_by_required_terms,
                "omitted_by_excluded_terms": omitted_by_excluded_terms,
            }
        ),
    }
    return selected, metadata


def _parent_code_path_order_policy_metadata(policy: str, order: list[str]) -> dict:
    return {
        "schema": "libreevolve.parent_code_order_policy.v1",
        "policy": policy,
        "ranking_policy": "path_order_v1",
        "candidate_count": len(order),
        "selected_count": len(order),
        "query_terms_sha256": hashlib.sha256(b"").hexdigest(),
        "query_term_count": 0,
        "ranking_sha256": _stable_json_sha256(
            [
                {"path": redact_sensitive_text(path), "rank": index + 1}
                for index, path in enumerate(order)
            ]
        ),
        "selected_files": [
            {
                "path": redact_sensitive_text(path),
                "rank": index + 1,
                "score": None,
                "original_index": index,
            }
            for index, path in enumerate(order)
        ],
    }


def _parent_code_limit_order_policy_metadata(
    metadata: dict,
    *,
    selected_order: list[str],
    omitted_order: list[str],
    parent_code_limit: int,
) -> dict:
    updated = dict(metadata)
    selected = set(selected_order)
    omitted = set(omitted_order)
    ranked_files = [
        dict(item)
        for item in metadata.get("selected_files", [])
        if isinstance(item, dict)
    ]
    updated["parent_code_limit"] = parent_code_limit
    updated["pre_limit_selected_count"] = len(ranked_files)
    updated["selected_count"] = len(selected_order)
    updated["omitted_count"] = len(omitted_order)
    updated["selected_files"] = [
        item for item in ranked_files if item.get("path") in selected
    ]
    updated["omitted_files"] = [
        item for item in ranked_files if item.get("path") in omitted
    ]
    updated["selection_policy"] = "ranked_parent_code_files_limited_after_ordering_v1"
    updated["selection_sha256"] = _stable_json_sha256(
        {
            "selected_order": selected_order,
            "omitted_order": omitted_order,
            "parent_code_limit": parent_code_limit,
        }
    )
    return updated


def _rank_parent_code_paths_by_terms(
    files: Mapping[str, str],
    order: list[str],
    *,
    query_text: str,
    ranking_terms: list[str],
) -> tuple[list[str], dict]:
    if ranking_terms:
        query_terms = list(ranking_terms)
        query_source = "parent_code_ranking_terms"
    else:
        query_terms = _context_source_order_query_terms(query_text)
        query_source = "task_description"
    query_hash = hashlib.sha256(" ".join(query_terms).encode("utf-8")).hexdigest()
    candidates = []
    for original_index, path in enumerate(order):
        content = files.get(path, "")
        candidate_text = f"{path}\n{content}"
        candidates.append(
            {
                "path": path,
                "score": _context_source_order_score(candidate_text, query_terms)
                if query_terms
                else 0,
                "original_index": original_index,
                "chars": len(candidate_text),
            }
        )
    ranked = sorted(
        candidates,
        key=lambda item: (-item["score"], item["original_index"], item["path"]),
    )
    ranked_paths = [str(item["path"]) for item in ranked]
    selected_files = [
        {
            "path": redact_sensitive_text(str(item["path"])),
            "rank": rank,
            "score": int(item["score"]),
            "original_index": int(item["original_index"]),
            "chars": int(item["chars"]),
        }
        for rank, item in enumerate(ranked, start=1)
    ]
    metadata = {
        "schema": "libreevolve.parent_code_order_policy.v1",
        "policy": "task_term_ranked",
        "ranking_policy": "term_overlap_parent_code_v1",
        "query_source": query_source,
        "candidate_count": len(candidates),
        "selected_count": len(selected_files),
        "query_terms_sha256": query_hash,
        "query_term_count": len(query_terms),
        "ranking_sha256": _stable_json_sha256(selected_files),
        "selected_files": selected_files,
    }
    if ranking_terms:
        metadata["configured_query_terms"] = list(query_terms)
    if not query_terms:
        metadata["ranking_fallback"] = "empty_query_terms"
    return ranked_paths, metadata


def _render_feedback(
    program: Program,
    *,
    artifact_base_dir: Path | None = None,
    artifact_content_mode: str = "excerpt",
    artifact_content_max_bytes: int = DEFAULT_PROMPT_ARTIFACT_CONTENT_MAX_BYTES,
    artifact_content_max_chars: int = DEFAULT_PROMPT_ARTIFACT_CONTENT_MAX_CHARS,
    feedback_sections: object = None,
    feedback_section_order: object = None,
    feedback_section_max_chars_by_name: object = None,
    llm_feedback_fields: object = None,
    llm_feedback_max_chars_by_field: object = None,
    proposal_fields: object = None,
    proposal_max_chars_by_field: object = None,
    stage_summary_fields: object = None,
    stage_summary_max_chars_by_field: object = None,
    execution_output_fields: object = None,
    execution_output_max_chars_by_field: object = None,
    sample_retry_fields: object = None,
    sample_retry_max_chars_by_field: object = None,
    program_output_fields: object = None,
    program_output_max_chars_by_field: object = None,
    validator_artifact_fields: object = None,
    validator_artifact_max_chars_by_field: object = None,
    validator_artifact_content_fields: object = None,
    validator_skipped_artifact_fields: object = None,
    validator_skipped_artifact_max_chars_by_field: object = None,
    validator_diagnostic_groups: object = None,
    validator_metadata_keys: object = None,
    validator_metadata_limit: object = None,
    validator_metadata_max_chars_by_key: object = None,
    evaluator_path_fields: object = None,
    evaluator_path_max_chars_by_field: object = None,
    evaluator_dependency_fields: object = None,
    evaluator_dependency_max_chars_by_field: object = None,
    evaluator_stage_fields: object = None,
    evaluator_stage_max_chars_by_field: object = None,
    evaluator_workspace_fields: object = None,
    evaluator_workspace_max_chars_by_field: object = None,
    syntax_error_fields: object = None,
    syntax_error_max_chars_by_field: object = None,
    metric_bound_fields: object = None,
    metric_bound_max_chars_by_field: object = None,
    configured_stage_check_fields: object = None,
    configured_stage_check_max_chars_by_field: object = None,
    stage_metric_threshold_fields: object = None,
    stage_metric_threshold_max_chars_by_field: object = None,
    artifact_output_check_fields: object = None,
    artifact_output_check_max_chars_by_field: object = None,
    malformed_metric_fields: object = None,
    malformed_metric_max_chars_by_field: object = None,
    materialization_error_fields: object = None,
    materialization_error_max_chars_by_field: object = None,
    metric_aggregation_fields: object = None,
    metric_aggregation_max_chars_by_field: object = None,
    synthetic_metric_fields: object = None,
    synthetic_metric_max_chars_by_field: object = None,
    execution_diagnostic_groups: object = None,
    validator_boundary_fields: object = None,
    validator_boundary_max_chars_by_field: object = None,
    validator_budget_fields: object = None,
    validator_budget_max_chars_by_field: object = None,
    validator_env_fields: object = None,
    validator_env_max_chars_by_field: object = None,
    validator_resource_limit_fields: object = None,
    validator_resource_limit_max_chars_by_field: object = None,
    validator_stdin_fields: object = None,
    validator_stdin_max_chars_by_field: object = None,
    diagnostic_output_fields: object = None,
    diagnostic_output_max_chars_by_field: object = None,
    timeout_cleanup_fields: object = None,
    timeout_cleanup_max_chars_by_field: object = None,
) -> str:
    evaluation = program.evaluation or {}
    stages = evaluation.get("stages", [])
    metadata = evaluation.get("metadata") if isinstance(evaluation.get("metadata"), dict) else {}
    enabled_sections = set(_validate_prompt_context_feedback_sections(feedback_sections))
    ordered_sections = _validate_prompt_context_feedback_section_order(
        feedback_section_order
    )
    section_max_chars = _validate_prompt_context_feedback_section_max_chars_by_name(
        feedback_section_max_chars_by_name
    )
    selected_llm_feedback_fields = _validate_prompt_context_llm_feedback_fields(
        llm_feedback_fields
    )
    llm_feedback_field_caps = _validate_prompt_context_llm_feedback_max_chars_by_field(
        llm_feedback_max_chars_by_field
    )
    selected_stage_summary_fields = set(
        _validate_prompt_context_stage_summary_fields(stage_summary_fields)
    )
    stage_summary_field_caps = (
        _validate_prompt_context_stage_summary_max_chars_by_field(
            stage_summary_max_chars_by_field
        )
    )
    execution_output_field_caps = (
        _validate_prompt_context_execution_output_max_chars_by_field(
            execution_output_max_chars_by_field
        )
    )
    selected_validator_diagnostic_groups = (
        _validate_prompt_context_validator_diagnostic_groups(
            validator_diagnostic_groups
        )
    )
    sections: dict[str, str] = {}
    proposal = _render_proposal(
        program,
        fields=proposal_fields,
        max_chars_by_field=proposal_max_chars_by_field,
    )
    if proposal and "proposal" in enabled_sections:
        sections["proposal"] = "[proposal]\n" + proposal
    if stages and "stage_summary" in enabled_sections:
        lines = []
        for stage in stages[-_MAX_FEEDBACK_ITEMS:]:
            if not isinstance(stage, dict):
                continue
            status = _prompt_status_text(stage.get("passed"))
            parts = []
            if "name" in selected_stage_summary_fields:
                name = _stage_summary_field_text(
                    stage.get("name") or "stage",
                    "name",
                    stage_summary_field_caps,
                )
                if name:
                    parts.append(f"name={_json_text(name)}")
            if "status" in selected_stage_summary_fields:
                status_text = _stage_summary_field_text(
                    status,
                    "status",
                    stage_summary_field_caps,
                )
                if status_text:
                    parts.append(f"status={status_text}")
            if "score" in selected_stage_summary_fields:
                if stage_summary_field_caps.get("score") == 0:
                    score = ""
                elif "score" in stage_summary_field_caps:
                    score = _stage_summary_field_text(
                        stage.get("score"),
                        "score",
                        stage_summary_field_caps,
                    )
                else:
                    raw_score = stage.get("score")
                    score = "" if raw_score is None else str(raw_score)
                if score or "score" not in stage_summary_field_caps:
                    parts.append(f"score={_json_text(score)}")
            error = _stage_summary_field_text(
                stage.get("error"),
                "error",
                stage_summary_field_caps,
                default_max_chars=_MAX_FEEDBACK_FIELD_CHARS,
            )
            if error and "error" in selected_stage_summary_fields:
                parts.append(f"error={_json_text(error)}")
            if parts:
                lines.append("- " + ", ".join(parts))
            stage_io = (
                _render_io_summary(
                    stage,
                    fields=execution_output_fields,
                    max_chars_by_field=execution_output_field_caps,
                )
                if "io" in selected_stage_summary_fields
                else ""
            )
            if stage_io:
                stage_io = _stage_summary_field_text(
                    stage_io,
                    "io",
                    stage_summary_field_caps,
                    escape_newlines=False,
                )
            if stage_io:
                lines.append(stage_io)
            stage_checks = (
                _render_stage_check_diagnostic(
                    stage,
                    stage_metric_threshold_fields=stage_metric_threshold_fields,
                    artifact_output_check_fields=artifact_output_check_fields,
                    artifact_output_check_max_chars_by_field=(
                        artifact_output_check_max_chars_by_field
                    ),
                )
                if "checks" in selected_stage_summary_fields
                else ""
            )
            if stage_checks:
                stage_checks = _stage_summary_field_text(
                    stage_checks,
                    "checks",
                    stage_summary_field_caps,
                    escape_newlines=False,
                )
            if stage_checks:
                lines.append("  " + stage_checks)
        if lines:
            sections["stage_summary"] = "[stage summary]\n" + "\n".join(lines)
    top_io = _render_io_summary(
        evaluation,
        fields=execution_output_fields,
        max_chars_by_field=execution_output_field_caps,
    )
    if top_io and "execution_output" in enabled_sections:
        sections["execution_output"] = "[execution output]\n" + top_io
    attempts = _render_attempts(
        metadata.get("attempts"),
        fields=sample_retry_fields,
        max_chars_by_field=sample_retry_max_chars_by_field,
    )
    if attempts and "sample_retry_diagnostics" in enabled_sections:
        sections["sample_retry_diagnostics"] = "[sample/retry diagnostics]\n" + attempts
    artifacts = _render_artifacts(
        metadata.get("artifacts"),
        artifact_base_dir=artifact_base_dir,
        artifact_content_mode=artifact_content_mode,
        artifact_content_max_bytes=artifact_content_max_bytes,
        artifact_content_max_chars=artifact_content_max_chars,
        fields=validator_artifact_fields,
        max_chars_by_field=validator_artifact_max_chars_by_field,
        artifact_content_fields=validator_artifact_content_fields,
        skipped_artifact_fields=validator_skipped_artifact_fields,
        skipped_artifact_max_chars_by_field=(
            validator_skipped_artifact_max_chars_by_field
        ),
    )
    if artifacts and "validator_artifacts" in enabled_sections:
        sections["validator_artifacts"] = "[validator artifacts]\n" + artifacts
    diagnostics = _render_validator_diagnostics(
        metadata,
        groups=selected_validator_diagnostic_groups,
        metadata_keys=validator_metadata_keys,
        metadata_limit=validator_metadata_limit,
        metadata_max_chars_by_key=validator_metadata_max_chars_by_key,
        evaluator_path_fields=evaluator_path_fields,
        evaluator_path_max_chars_by_field=evaluator_path_max_chars_by_field,
        evaluator_dependency_fields=evaluator_dependency_fields,
        evaluator_dependency_max_chars_by_field=(
            evaluator_dependency_max_chars_by_field
        ),
        evaluator_stage_fields=evaluator_stage_fields,
        evaluator_stage_max_chars_by_field=evaluator_stage_max_chars_by_field,
        evaluator_workspace_fields=evaluator_workspace_fields,
        evaluator_workspace_max_chars_by_field=evaluator_workspace_max_chars_by_field,
        syntax_error_fields=syntax_error_fields,
        syntax_error_max_chars_by_field=syntax_error_max_chars_by_field,
        metric_bound_fields=metric_bound_fields,
        metric_bound_max_chars_by_field=metric_bound_max_chars_by_field,
        configured_stage_check_fields=configured_stage_check_fields,
        configured_stage_check_max_chars_by_field=(
            configured_stage_check_max_chars_by_field
        ),
        stage_metric_threshold_fields=stage_metric_threshold_fields,
        stage_metric_threshold_max_chars_by_field=(
            stage_metric_threshold_max_chars_by_field
        ),
        artifact_output_check_fields=artifact_output_check_fields,
        artifact_output_check_max_chars_by_field=artifact_output_check_max_chars_by_field,
        malformed_metric_fields=malformed_metric_fields,
        malformed_metric_max_chars_by_field=malformed_metric_max_chars_by_field,
        materialization_error_fields=materialization_error_fields,
        materialization_error_max_chars_by_field=(
            materialization_error_max_chars_by_field
        ),
        metric_aggregation_fields=metric_aggregation_fields,
        metric_aggregation_max_chars_by_field=metric_aggregation_max_chars_by_field,
        synthetic_metric_fields=synthetic_metric_fields,
        synthetic_metric_max_chars_by_field=synthetic_metric_max_chars_by_field,
        execution_diagnostic_groups=execution_diagnostic_groups,
        validator_boundary_fields=validator_boundary_fields,
        validator_boundary_max_chars_by_field=validator_boundary_max_chars_by_field,
        validator_budget_fields=validator_budget_fields,
        validator_budget_max_chars_by_field=validator_budget_max_chars_by_field,
        validator_env_fields=validator_env_fields,
        validator_env_max_chars_by_field=validator_env_max_chars_by_field,
        validator_resource_limit_fields=validator_resource_limit_fields,
        validator_resource_limit_max_chars_by_field=(
            validator_resource_limit_max_chars_by_field
        ),
        validator_stdin_fields=validator_stdin_fields,
        validator_stdin_max_chars_by_field=validator_stdin_max_chars_by_field,
        diagnostic_output_fields=diagnostic_output_fields,
        diagnostic_output_max_chars_by_field=diagnostic_output_max_chars_by_field,
        timeout_cleanup_fields=timeout_cleanup_fields,
        timeout_cleanup_max_chars_by_field=timeout_cleanup_max_chars_by_field,
    )
    if diagnostics and "validator_diagnostics" in enabled_sections:
        sections["validator_diagnostics"] = "[validator diagnostics]\n" + diagnostics
    program_outputs = _render_program_outputs(
        metadata.get("program_outputs"),
        fields=program_output_fields,
        max_chars_by_field=program_output_max_chars_by_field,
    )
    if program_outputs and "program_outputs" in enabled_sections:
        sections["program_outputs"] = "[program outputs]\n" + program_outputs
    feedback = _render_llm_feedback(
        metadata.get("llm_feedback"),
        fields=selected_llm_feedback_fields,
        max_chars_by_field=llm_feedback_field_caps,
    )
    if feedback and "llm_grader_feedback" in enabled_sections:
        sections["llm_grader_feedback"] = "[llm grader feedback]\n" + feedback
    if not sections:
        return "(none)"
    rendered_sections = []
    for name in ordered_sections:
        section = sections.get(name)
        if section is None:
            continue
        capped = _apply_feedback_section_max_chars(name, section, section_max_chars)
        if capped:
            rendered_sections.append(capped)
    return _truncate_text("\n".join(rendered_sections), _MAX_FEEDBACK_TEXT_CHARS)


def _apply_feedback_section_max_chars(
    name: str,
    text: str,
    section_max_chars: Mapping[str, int],
) -> str:
    limit = section_max_chars.get(name)
    if limit is None:
        return text
    if limit == 0:
        return ""
    return _truncate_text(text, limit)


def _stage_summary_field_text(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int | None = None,
    escape_newlines: bool = True,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    if value is None:
        return ""
    text = str(value)
    if default_max_chars is None and max_chars is None:
        return text
    text = text.replace("\r\n", "\n").strip()
    if not text:
        return ""
    text = _redact_sensitive_text(text)
    text = _truncate_text(
        text,
        max_chars if max_chars is not None else default_max_chars,
    )
    if escape_newlines:
        text = text.replace("\n", "\\n")
    return text


def _render_io_summary(
    record: dict,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    selected_fields = set(_validate_prompt_context_execution_output_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_execution_output_max_chars_by_field(
        max_chars_by_field
    )
    lines = []
    stdout = _short_execution_output_field(
        record.get("stdout"),
        "stdout",
        field_caps,
    )
    stderr = _short_execution_output_field(
        record.get("stderr"),
        "stderr",
        field_caps,
    )
    if stdout and "stdout" in selected_fields:
        lines.append(f"  stdout={_json_text(stdout)}")
    if stderr and "stderr" in selected_fields:
        lines.append(f"  stderr={_json_text(stderr)}")
    error = _short_execution_output_field(
        record.get("error"),
        "error",
        field_caps,
    )
    if error and "error" in selected_fields and not lines:
        lines.append(f"  error={_json_text(error)}")
    return "\n".join(lines)


def _short_execution_output_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else _MAX_FEEDBACK_FIELD_CHARS,
    )


def _render_attempts(
    attempts: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(attempts, list) or not attempts:
        return ""
    selected_fields = set(_validate_prompt_context_sample_retry_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_sample_retry_max_chars_by_field(
        max_chars_by_field
    )
    lines = []
    for attempt in attempts[-_MAX_FEEDBACK_ITEMS:]:
        if not isinstance(attempt, dict):
            continue
        status = _prompt_status_text(attempt.get("passed"))
        stage_record = attempt.get("stage")
        stage = stage_record.get("name") if isinstance(stage_record, dict) else attempt.get("stage_name")
        stage = _short_sample_retry_field(stage, "stage", field_caps)
        sample = (
            stage_record.get("sample_index")
            if isinstance(stage_record, dict)
            else attempt.get("sample_index")
        )
        attempt_index = attempt.get("attempt")
        status = _short_sample_retry_field(status, "status", field_caps)
        sample_text = _short_sample_retry_field(sample, "sample", field_caps)
        attempt_text = _short_sample_retry_field(
            attempt_index,
            "attempt",
            field_caps,
        )
        detail = [
            f"stage={_json_text(stage)}"
            if stage and "stage" in selected_fields
            else "",
            f"sample={sample_text}"
            if sample_text and "sample" in selected_fields
            else "",
            f"attempt={attempt_text}"
            if attempt_text and "attempt" in selected_fields
            else "",
        ]
        prefix = ", ".join(item for item in detail if item)
        prefix = f" ({prefix})" if prefix else ""
        error = _short_sample_retry_field(
            attempt.get("error"),
            "error",
            field_caps,
        )
        parts = []
        if status and "status" in selected_fields:
            parts.append(f"status={status}{prefix}")
        elif prefix:
            parts.append(prefix.strip())
        if "fitness" in selected_fields:
            fitness = _short_sample_retry_field(
                attempt.get("fitness"),
                "fitness",
                field_caps,
            )
            if fitness:
                parts.append(f"fitness={_json_text(fitness)}")
        if error and "error" in selected_fields:
            parts.append(f"error={_json_text(error)}")
        if parts:
            lines.append("- " + ", ".join(parts))
    return "\n".join(lines)


def _short_sample_retry_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else _MAX_FEEDBACK_FIELD_CHARS,
    )


def _prompt_status_text(value: object) -> str:
    if value is True:
        return "passed"
    if value is False:
        return "failed"
    return "unknown"


def _render_artifacts(
    artifacts: object,
    *,
    artifact_base_dir: Path | None = None,
    artifact_content_mode: str = "excerpt",
    artifact_content_max_bytes: int = DEFAULT_PROMPT_ARTIFACT_CONTENT_MAX_BYTES,
    artifact_content_max_chars: int = DEFAULT_PROMPT_ARTIFACT_CONTENT_MAX_CHARS,
    fields: object = None,
    max_chars_by_field: object = None,
    artifact_content_fields: object = None,
    skipped_artifact_fields: object = None,
    skipped_artifact_max_chars_by_field: object = None,
) -> str:
    if not isinstance(artifacts, dict):
        return ""
    selected_fields = set(_validate_prompt_context_validator_artifact_fields(fields))
    field_caps = _validate_prompt_context_validator_artifact_max_chars_by_field(
        max_chars_by_field
    )
    files = artifacts.get("files")
    lines = []
    if selected_fields and isinstance(files, list):
        for artifact in files[:_MAX_FEEDBACK_ITEMS]:
            if not isinstance(artifact, dict):
                continue
            source = artifact.get("source_path") or artifact.get("relative_path") or artifact.get("path")
            stored = artifact.get("artifact_path") or artifact.get("stored_path")
            sha = _short(artifact.get("sha256"), max_chars=64)[:12]
            redacted = artifact.get("redacted")
            parts = []
            source_text = _short_validator_artifact_field(
                source,
                "path",
                field_caps,
                default_max_chars=160,
            )
            if source_text and "path" in selected_fields:
                parts.append(f"path={_json_text(source_text)}")
            stored_text = _short_validator_artifact_field(
                stored,
                "stored",
                field_caps,
                default_max_chars=160,
            )
            if stored_text and "stored" in selected_fields:
                parts.append(f"stored={_json_text(stored_text)}")
            if sha and "sha256" in selected_fields:
                parts.append(f"sha256={sha}")
            if redacted is not None and "redacted" in selected_fields:
                parts.append(f"redacted={_json_text(_short(redacted, max_chars=24))}")
            excerpt = _short_validator_artifact_field(
                artifact.get("content_excerpt"),
                "content_excerpt",
                field_caps,
                default_max_chars=300,
            )
            if excerpt and "content_excerpt" in selected_fields:
                parts.append(f"content_excerpt={_json_text(excerpt)}")
                if (
                    artifact.get("content_excerpt_truncated") is not None
                    and "content_excerpt_truncated" in selected_fields
                ):
                    parts.append(
                        "content_excerpt_truncated="
                        f"{_json_text(artifact.get('content_excerpt_truncated'))}"
                    )
            elif (
                artifact.get("content_excerpt_status")
                and "content_excerpt_status" in selected_fields
            ):
                status = _short_validator_artifact_field(
                    artifact.get("content_excerpt_status"),
                    "content_excerpt_status",
                    field_caps,
                    default_max_chars=40,
                )
                parts.append(f"content_excerpt_status={_json_text(status)}")
            if "artifact_content" in selected_fields:
                content = _artifact_prompt_content(
                    artifact,
                    artifact_base_dir=artifact_base_dir,
                    artifact_content_mode=artifact_content_mode,
                    artifact_content_max_bytes=artifact_content_max_bytes,
                    artifact_content_max_chars=artifact_content_max_chars,
                    fields=artifact_content_fields,
                )
                if content:
                    parts.append(content)
            if parts:
                lines.append("- " + ", ".join(parts))
        if len(files) > _MAX_FEEDBACK_ITEMS:
            lines.append(f"- files_omitted={len(files) - _MAX_FEEDBACK_ITEMS}")
    skipped = artifacts.get("skipped") or artifacts.get("skipped_files")
    skipped_lines = _render_skipped_artifacts(
        skipped,
        fields=skipped_artifact_fields,
        max_chars_by_field=skipped_artifact_max_chars_by_field,
    )
    if skipped_lines:
        lines.extend(skipped_lines)
    return "\n".join(lines)


def _short_validator_artifact_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _short_validator_skipped_artifact_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _short_validator_skipped_artifact_sha(
    value: object,
    max_chars_by_field: Mapping[str, int],
) -> str:
    max_chars = max_chars_by_field.get("sha256")
    if max_chars == 0:
        return ""
    text = _short(value, max_chars=64)
    if not text:
        return ""
    return text[: max_chars if max_chars is not None else 12]


def _artifact_prompt_content(
    artifact: dict,
    *,
    artifact_base_dir: Path | None,
    artifact_content_mode: str,
    artifact_content_max_bytes: int,
    artifact_content_max_chars: int,
    fields: object = None,
) -> str:
    selected_fields = set(
        _validate_prompt_context_validator_artifact_content_fields(fields)
    )
    if not selected_fields:
        return ""
    if artifact_content_mode == "off":
        return _artifact_prompt_content_parts(status="off", fields=selected_fields)
    if artifact_content_mode == "excerpt":
        return _artifact_prompt_content_parts(
            status="excerpt_only",
            fields=selected_fields,
        )
    if artifact_content_mode != "bounded_file":
        return _artifact_prompt_content_parts(
            status="unsupported_policy",
            fields=selected_fields,
        )
    if artifact_base_dir is None:
        return _artifact_prompt_content_parts(
            status="missing_artifact_base_dir",
            fields=selected_fields,
        )
    rel_path = artifact.get("artifact_path") or artifact.get("stored_path")
    if not isinstance(rel_path, str) or not rel_path.strip():
        return _artifact_prompt_content_parts(
            status="missing_artifact_path",
            fields=selected_fields,
        )
    try:
        path = Path(rel_path)
        if path.is_absolute():
            return _artifact_prompt_content_parts(
                status="absolute_path_rejected",
                fields=selected_fields,
            )
        base = artifact_base_dir.resolve(strict=False)
        target = (base / path).resolve(strict=False)
        if base != target and base not in target.parents:
            return _artifact_prompt_content_parts(
                status="path_escape_rejected",
                fields=selected_fields,
            )
        if target.is_symlink():
            return _artifact_prompt_content_parts(
                status="link_rejected",
                fields=selected_fields,
            )
        if not target.is_file():
            return _artifact_prompt_content_parts(
                status="missing_or_not_file",
                fields=selected_fields,
            )
        size = target.stat().st_size
        if size > artifact_content_max_bytes:
            return _artifact_prompt_content_parts(
                status="max_bytes",
                bytes_value=size,
                max_bytes=artifact_content_max_bytes,
                fields=selected_fields,
            )
        raw = target.read_bytes()
    except OSError:
        return _artifact_prompt_content_parts(status="read_error", fields=selected_fields)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        return _artifact_prompt_content_parts(
            status="binary_or_non_utf8",
            fields=selected_fields,
        )
    redacted = _redact_sensitive_text(text)
    truncated = len(redacted) > artifact_content_max_chars
    content = _truncate_text(redacted, artifact_content_max_chars).replace("\n", "\\n")
    return _artifact_prompt_content_parts(
        status="included",
        bytes_value=len(raw),
        chars=len(redacted),
        truncated=truncated,
        content=content,
        fields=selected_fields,
    )


def _artifact_prompt_content_parts(
    *,
    status: str,
    fields: set[str],
    bytes_value: object = None,
    max_bytes: object = None,
    chars: object = None,
    truncated: object = None,
    content: object = None,
) -> str:
    parts = []
    if "status" in fields:
        parts.append(f'artifact_content_status="{status}"')
    if bytes_value is not None and "bytes" in fields:
        parts.append(f'artifact_content_bytes="{bytes_value}"')
    if max_bytes is not None and "max_bytes" in fields:
        parts.append(f'artifact_content_max_bytes="{max_bytes}"')
    if chars is not None and "chars" in fields:
        parts.append(f'artifact_content_chars="{chars}"')
    if truncated is not None and "truncated" in fields:
        parts.append(f'artifact_content_truncated="{truncated}"')
    if content is not None and "content" in fields:
        parts.append(f"artifact_content={_json_text(content)}")
    return ", ".join(parts)


def _render_program_outputs(
    outputs: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(outputs, dict):
        return ""
    selected_fields = set(_validate_prompt_context_program_output_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_program_output_max_chars_by_field(
        max_chars_by_field
    )
    parts = []
    source = _short_program_output_field(
        outputs.get("source_key"),
        "source",
        field_caps,
        default_max_chars=40,
    )
    if source and "source" in selected_fields:
        parts.append(f"source={_json_text(source)}")
    if "json_chars" in selected_fields:
        parts.append(f"json_chars={_json_text(outputs.get('json_chars'))}")
    sha = _short(outputs.get("sha256"), max_chars=64)[:12]
    if sha and "sha256" in selected_fields:
        parts.append(f"sha256={sha}")
    if outputs.get("redacted") is not None and "redacted" in selected_fields:
        parts.append(f"redacted={_json_text(outputs.get('redacted'))}")
    if outputs.get("omitted") and "preview" in selected_fields:
        preview = _short_program_output_field(
            outputs.get("preview"),
            "preview",
            field_caps,
            default_max_chars=300,
        )
        if preview:
            parts.append(f"preview={_json_text(preview)}")
    elif "value" in outputs and "value" in selected_fields:
        value_text = _short_program_output_field(
            outputs.get("value"),
            "value",
            field_caps,
            default_max_chars=300,
        )
        if value_text:
            parts.append(f"value={_json_text(value_text)}")
    return "- " + ", ".join(parts) if parts else ""


def _short_program_output_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_skipped_artifacts(
    skipped: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> list[str]:
    if skipped in (None, "", [], ()):
        return []
    selected_fields = set(
        _validate_prompt_context_validator_skipped_artifact_fields(fields)
    )
    if not selected_fields:
        return []
    field_caps = _validate_prompt_context_validator_skipped_artifact_max_chars_by_field(
        max_chars_by_field
    )
    if isinstance(skipped, list | tuple):
        records = list(skipped)
    else:
        records = [skipped]
    lines: list[str] = []
    for record in records[:_MAX_FEEDBACK_ITEMS]:
        if isinstance(record, dict):
            parts = ["skipped_artifact"]
            path = record.get("path") or record.get("source_path") or record.get("relative_path")
            reason = record.get("reason") or record.get("status")
            message = record.get("message") or record.get("error")
            for label, value, max_chars in (
                ("path", path, 160),
                ("reason", reason, 80),
                ("message", message, 160),
                ("size", record.get("size"), 40),
                ("max_bytes", record.get("max_bytes"), 40),
                ("redacted", record.get("redacted"), 24),
            ):
                if label not in selected_fields:
                    continue
                text = _short_validator_skipped_artifact_field(
                    value,
                    label,
                    field_caps,
                    default_max_chars=max_chars,
                )
                if text:
                    parts.append(f"{label}={_json_text(text)}")
            sha = _short_validator_skipped_artifact_sha(
                record.get("sha256"),
                field_caps,
            )
            if sha and "sha256" in selected_fields:
                parts.append(f"sha256={sha}")
            if len(parts) > 1:
                lines.append("- " + ", ".join(parts))
            continue
        text = _short_validator_skipped_artifact_field(
            record,
            "value",
            field_caps,
            default_max_chars=200,
        )
        if text and "value" in selected_fields:
            lines.append(f"- skipped_artifact={_json_text(text)}")
    if len(records) > _MAX_FEEDBACK_ITEMS:
        lines.append(f"- skipped_artifacts_omitted={len(records) - _MAX_FEEDBACK_ITEMS}")
    return lines


def _render_llm_feedback(
    records: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(records, list) or not records:
        return ""
    selected_fields = set(_validate_prompt_context_llm_feedback_fields(fields))
    field_caps = _validate_prompt_context_llm_feedback_max_chars_by_field(
        max_chars_by_field
    )
    lines = []
    for record in records[-_MAX_FEEDBACK_ITEMS:]:
        if not isinstance(record, dict):
            continue
        name = _short_llm_feedback_field(
            record.get("name") or record.get("metric") or "grader",
            "name",
            field_caps,
            escape_newlines=False,
        )
        score = _short_llm_feedback_field(
            record.get("score"),
            "score",
            field_caps,
            default_max_chars=80,
        )
        discarded = _short_llm_feedback_field(
            record.get("discard"),
            "discard",
            field_caps,
            default_max_chars=40,
        )
        error = _short_llm_feedback_field(record.get("error"), "error", field_caps)
        feedback = _short_llm_feedback_field(
            record.get("feedback") or record.get("raw_response"),
            "feedback",
            field_caps,
        )
        parts = []
        if name and "name" in selected_fields:
            parts.append(f"name={_json_text(name)}")
        if score and "score" in selected_fields:
            parts.append(f"score={_json_text(score)}")
        if discarded and "discard" in selected_fields:
            parts.append(f"discard={_json_text(discarded)}")
        if error and "error" in selected_fields:
            parts.append(f"error={_json_text(error)}")
        if feedback and "feedback" in selected_fields:
            parts.append(f"feedback={_json_text(feedback)}")
        if parts:
            lines.append("- " + ", ".join(parts))
    return "\n".join(lines)


def _short_llm_feedback_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int = _MAX_FEEDBACK_FIELD_CHARS,
    escape_newlines: bool = True,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    if not escape_newlines:
        if value is None:
            return ""
        text = str(value).replace("\r\n", "\n").strip()
        if not text:
            return ""
        text = _redact_sensitive_text(text)
        return _truncate_text(
            text,
            max_chars if max_chars is not None else default_max_chars,
        )
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_validator_diagnostics(
    metadata: object,
    *,
    groups: object = None,
    metadata_keys: object = None,
    metadata_limit: object = None,
    metadata_max_chars_by_key: object = None,
    evaluator_path_fields: object = None,
    evaluator_path_max_chars_by_field: object = None,
    evaluator_dependency_fields: object = None,
    evaluator_dependency_max_chars_by_field: object = None,
    evaluator_stage_fields: object = None,
    evaluator_stage_max_chars_by_field: object = None,
    evaluator_workspace_fields: object = None,
    evaluator_workspace_max_chars_by_field: object = None,
    syntax_error_fields: object = None,
    syntax_error_max_chars_by_field: object = None,
    metric_bound_fields: object = None,
    metric_bound_max_chars_by_field: object = None,
    configured_stage_check_fields: object = None,
    configured_stage_check_max_chars_by_field: object = None,
    stage_metric_threshold_fields: object = None,
    stage_metric_threshold_max_chars_by_field: object = None,
    artifact_output_check_fields: object = None,
    artifact_output_check_max_chars_by_field: object = None,
    malformed_metric_fields: object = None,
    malformed_metric_max_chars_by_field: object = None,
    materialization_error_fields: object = None,
    materialization_error_max_chars_by_field: object = None,
    metric_aggregation_fields: object = None,
    metric_aggregation_max_chars_by_field: object = None,
    synthetic_metric_fields: object = None,
    synthetic_metric_max_chars_by_field: object = None,
    execution_diagnostic_groups: object = None,
    validator_boundary_fields: object = None,
    validator_boundary_max_chars_by_field: object = None,
    validator_budget_fields: object = None,
    validator_budget_max_chars_by_field: object = None,
    validator_env_fields: object = None,
    validator_env_max_chars_by_field: object = None,
    validator_resource_limit_fields: object = None,
    validator_resource_limit_max_chars_by_field: object = None,
    validator_stdin_fields: object = None,
    validator_stdin_max_chars_by_field: object = None,
    diagnostic_output_fields: object = None,
    diagnostic_output_max_chars_by_field: object = None,
    timeout_cleanup_fields: object = None,
    timeout_cleanup_max_chars_by_field: object = None,
) -> str:
    if not isinstance(metadata, dict):
        return ""
    selected_groups = set(
        _validate_prompt_context_validator_diagnostic_groups(groups)
    )
    lines: list[str] = []
    if "evaluator_dependency" in selected_groups:
        dependency = _render_evaluator_dependency_diagnostic(
            metadata.get("evaluator_dependency_policy"),
            fields=evaluator_dependency_fields,
            max_chars_by_field=evaluator_dependency_max_chars_by_field,
        )
        if dependency:
            lines.append(dependency)
    if "evaluator_path" in selected_groups:
        evaluator_path = _render_evaluator_path_diagnostic(
            metadata,
            fields=evaluator_path_fields,
            max_chars_by_field=evaluator_path_max_chars_by_field,
        )
        if evaluator_path:
            lines.append(evaluator_path)
    if "evaluator_stage" in selected_groups:
        evaluator_stage = _render_evaluator_stage_diagnostic(
            metadata.get("stage"),
            fields=evaluator_stage_fields,
            max_chars_by_field=evaluator_stage_max_chars_by_field,
        )
        if evaluator_stage:
            lines.append(evaluator_stage)
    if "evaluator_workspace" in selected_groups:
        evaluator_workspace = _render_evaluator_workspace_diagnostic(
            metadata,
            fields=evaluator_workspace_fields,
            max_chars_by_field=evaluator_workspace_max_chars_by_field,
        )
        if evaluator_workspace:
            lines.append(evaluator_workspace)
    if "syntax_errors" in selected_groups:
        lines.extend(
            _render_syntax_diagnostics(
                metadata.get("syntax_errors"),
                fields=syntax_error_fields,
                max_chars_by_field=syntax_error_max_chars_by_field,
            )
        )
    if "metric_bound_diagnostics" in selected_groups:
        lines.extend(
            _render_metric_bound_diagnostics(
                metadata.get("metric_bound_diagnostics"),
                fields=metric_bound_fields,
                max_chars_by_field=metric_bound_max_chars_by_field,
            )
        )
    if "configured_stage_checks" in selected_groups:
        lines.extend(
            _render_configured_stage_check_diagnostics(
                metadata.get("configured_stage_results"),
                fields=configured_stage_check_fields,
                max_chars_by_field=configured_stage_check_max_chars_by_field,
                stage_metric_threshold_fields=stage_metric_threshold_fields,
                stage_metric_threshold_max_chars_by_field=(
                    stage_metric_threshold_max_chars_by_field
                ),
                artifact_output_check_fields=artifact_output_check_fields,
                artifact_output_check_max_chars_by_field=(
                    artifact_output_check_max_chars_by_field
                ),
            )
        )
    if "malformed_metrics" in selected_groups:
        malformed = _render_malformed_metric_diagnostic(
            metadata.get("malformed_metrics"),
            fields=malformed_metric_fields,
            max_chars_by_field=malformed_metric_max_chars_by_field,
        )
        if malformed:
            lines.append(malformed)
    if "materialization_error" in selected_groups:
        materialization = _render_materialization_error_diagnostic(
            metadata.get("materialization_error"),
            fields=materialization_error_fields,
            max_chars_by_field=materialization_error_max_chars_by_field,
        )
        if materialization:
            lines.append(materialization)
    if "metric_aggregation" in selected_groups:
        aggregation = _render_metric_aggregation_diagnostic(
            metadata,
            fields=metric_aggregation_fields,
            max_chars_by_field=metric_aggregation_max_chars_by_field,
        )
        if aggregation:
            lines.append(aggregation)
    if "synthetic_metrics" in selected_groups:
        synthetic = _render_synthetic_metric_diagnostic(
            metadata.get("synthetic_metrics"),
            fields=synthetic_metric_fields,
            max_chars_by_field=synthetic_metric_max_chars_by_field,
        )
        if synthetic:
            lines.append(synthetic)
    if "execution_diagnostics" in selected_groups:
        lines.extend(
            _render_validator_execution_diagnostics(
                metadata,
                groups=execution_diagnostic_groups,
                validator_boundary_fields=validator_boundary_fields,
                validator_boundary_max_chars_by_field=(
                    validator_boundary_max_chars_by_field
                ),
                validator_budget_fields=validator_budget_fields,
                validator_budget_max_chars_by_field=(
                    validator_budget_max_chars_by_field
                ),
                validator_env_fields=validator_env_fields,
                validator_env_max_chars_by_field=validator_env_max_chars_by_field,
                validator_resource_limit_fields=validator_resource_limit_fields,
                validator_resource_limit_max_chars_by_field=(
                    validator_resource_limit_max_chars_by_field
                ),
                validator_stdin_fields=validator_stdin_fields,
                validator_stdin_max_chars_by_field=(
                    validator_stdin_max_chars_by_field
                ),
                diagnostic_output_fields=diagnostic_output_fields,
                diagnostic_output_max_chars_by_field=(
                    diagnostic_output_max_chars_by_field
                ),
                timeout_cleanup_fields=timeout_cleanup_fields,
                timeout_cleanup_max_chars_by_field=timeout_cleanup_max_chars_by_field,
            )
        )
    if "metadata_summary" in selected_groups:
        metadata_summary = _render_validator_metadata_summary(
            metadata,
            selected_keys=metadata_keys,
            limit=metadata_limit,
            max_chars_by_key=metadata_max_chars_by_key,
        )
        if metadata_summary:
            lines.append(metadata_summary)
    return "\n".join(lines)


def _render_validator_execution_diagnostics(
    metadata: dict,
    *,
    groups: object = None,
    validator_boundary_fields: object = None,
    validator_boundary_max_chars_by_field: object = None,
    validator_budget_fields: object = None,
    validator_budget_max_chars_by_field: object = None,
    validator_env_fields: object = None,
    validator_env_max_chars_by_field: object = None,
    validator_resource_limit_fields: object = None,
    validator_resource_limit_max_chars_by_field: object = None,
    validator_stdin_fields: object = None,
    validator_stdin_max_chars_by_field: object = None,
    diagnostic_output_fields: object = None,
    diagnostic_output_max_chars_by_field: object = None,
    timeout_cleanup_fields: object = None,
    timeout_cleanup_max_chars_by_field: object = None,
) -> list[str]:
    lines: list[str] = []
    selected_groups = set(_validate_prompt_context_execution_diagnostic_groups(groups))
    if "validator_boundary" in selected_groups:
        boundary = _render_validator_boundary_diagnostic(
            metadata.get("validator_boundary"),
            fields=validator_boundary_fields,
            max_chars_by_field=validator_boundary_max_chars_by_field,
            resource_limit_fields=validator_resource_limit_fields,
            resource_limit_max_chars_by_field=(
                validator_resource_limit_max_chars_by_field
            ),
        )
        if boundary:
            lines.append(boundary)
    if "validator_budget" in selected_groups:
        budget = _render_validator_budget_diagnostic(
            metadata.get("stage_budget"),
            metadata.get("sample_budget"),
            fields=validator_budget_fields,
            max_chars_by_field=validator_budget_max_chars_by_field,
        )
        if budget:
            lines.append(budget)
    if "validator_env" in selected_groups:
        env = _render_validator_env_diagnostic(
            metadata.get("validator_env"),
            fields=validator_env_fields,
            max_chars_by_field=validator_env_max_chars_by_field,
        )
        if env:
            lines.append(env)
    if "stdin" in selected_groups:
        stdin = _render_validator_stdin_diagnostic(
            metadata.get("stdin"),
            fields=validator_stdin_fields,
            max_chars_by_field=validator_stdin_max_chars_by_field,
        )
        if stdin:
            lines.append(stdin)
    if "diagnostic_output" in selected_groups:
        diagnostic_output = _render_diagnostic_output_policy(
            metadata.get("diagnostic_output"),
            fields=diagnostic_output_fields,
            max_chars_by_field=diagnostic_output_max_chars_by_field,
        )
        if diagnostic_output:
            lines.append(diagnostic_output)
    if "timeout_cleanup" in selected_groups:
        timeout_cleanup = _render_timeout_cleanup_diagnostic(
            metadata.get("timeout_cleanup"),
            fields=timeout_cleanup_fields,
            max_chars_by_field=timeout_cleanup_max_chars_by_field,
        )
        if timeout_cleanup:
            lines.append(timeout_cleanup)
    return lines


def _render_validator_metadata_summary(
    metadata: dict,
    *,
    selected_keys: object = None,
    limit: object = None,
    max_chars_by_key: object = None,
) -> str:
    if not isinstance(metadata, dict):
        return ""
    policy_keys = _validate_prompt_context_validator_metadata_keys(selected_keys)
    item_limit = _validate_prompt_context_validator_metadata_limit(limit)
    if item_limit == 0:
        return ""
    key_caps = _validate_prompt_context_validator_metadata_max_chars_by_key(
        max_chars_by_key
    )
    if policy_keys:
        candidates = [
            key
            for key in policy_keys
            if key in metadata
            and key not in _VALIDATOR_METADATA_SPECIAL_KEYS
            and _validator_metadata_value_is_prompt_safe(metadata.get(key))
        ]
    else:
        candidates = [
            key
            for key in sorted(metadata, key=str)
            if isinstance(key, str)
            and key not in _VALIDATOR_METADATA_SPECIAL_KEYS
            and _validator_metadata_value_is_prompt_safe(metadata.get(key))
        ]
    if not candidates:
        return ""
    effective_limit = (
        _MAX_VALIDATOR_METADATA_ITEMS if item_limit is None else item_limit
    )
    selected = candidates[:effective_limit]
    parts = ["validator_metadata"]
    for key in selected:
        max_chars = key_caps.get(key)
        if max_chars == 0:
            continue
        rendered = _validator_metadata_value_text(metadata[key], max_chars=max_chars)
        parts.append(
            f"{_validator_metadata_key_text(key)}={_json_text(rendered)}"
        )
        parts.append(
            f"{_validator_metadata_key_text(key)}_sha256="
            f"{hashlib.sha256(rendered.encode('utf-8')).hexdigest()[:12]}"
        )
    omitted = len(candidates) - len(selected)
    if omitted > 0:
        parts.append(f"omitted={omitted}")
    if len(parts) == 1:
        return ""
    return "- " + ", ".join(parts)


def _validator_metadata_value_is_prompt_safe(value: object) -> bool:
    if value is None or isinstance(value, bool):
        return True
    if isinstance(value, str):
        return True
    if isinstance(value, int) and not isinstance(value, bool):
        return True
    if isinstance(value, float):
        return math.isfinite(value)
    if isinstance(value, list):
        return all(_validator_metadata_value_is_prompt_safe(item) for item in value)
    if isinstance(value, dict):
        return all(
            isinstance(key, str) and _validator_metadata_value_is_prompt_safe(item)
            for key, item in value.items()
        )
    return False


def _validator_metadata_value_text(value: object, *, max_chars: int | None = None) -> str:
    redacted = redact_sensitive_text(
        json.dumps(
            _stable_prompt_metadata_value(value),
            sort_keys=True,
            ensure_ascii=True,
            separators=(",", ":"),
        )
    )
    return _truncate_text(
        redacted,
        max_chars
        if max_chars is not None
        else _MAX_VALIDATOR_METADATA_VALUE_CHARS,
    )


def _validator_metadata_key_text(value: str) -> str:
    text = _short(value, max_chars=80) or "metadata"
    if _METRIC_LABEL_RE.fullmatch(text):
        return text
    return text.replace(",", "_").replace("\n", "_")


def _render_configured_stage_check_diagnostics(
    records: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
    stage_metric_threshold_fields: object = None,
    stage_metric_threshold_max_chars_by_field: object = None,
    artifact_output_check_fields: object = None,
    artifact_output_check_max_chars_by_field: object = None,
) -> list[str]:
    if not isinstance(records, list) or not records:
        return []
    selected_fields = _validate_prompt_context_configured_stage_check_fields(fields)
    if not selected_fields:
        return []
    lines: list[str] = []
    for record in records[:_MAX_FEEDBACK_ITEMS]:
        if not isinstance(record, dict):
            continue
        diagnostic = _render_stage_check_diagnostic(
            record,
            fields=selected_fields,
            max_chars_by_field=max_chars_by_field,
            stage_metric_threshold_fields=stage_metric_threshold_fields,
            stage_metric_threshold_max_chars_by_field=(
                stage_metric_threshold_max_chars_by_field
            ),
            artifact_output_check_fields=artifact_output_check_fields,
            artifact_output_check_max_chars_by_field=(
                artifact_output_check_max_chars_by_field
            ),
        )
        if diagnostic:
            lines.append(diagnostic)
    if len(records) > _MAX_FEEDBACK_ITEMS:
        lines.append(
            f"- configured_stage_results_omitted={len(records) - _MAX_FEEDBACK_ITEMS}"
        )
    return lines


def _render_stage_check_diagnostic(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
    stage_metric_threshold_fields: object = None,
    stage_metric_threshold_max_chars_by_field: object = None,
    artifact_output_check_fields: object = None,
    artifact_output_check_max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(
        _validate_prompt_context_configured_stage_check_fields(fields)
    )
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_configured_stage_check_max_chars_by_field(
        max_chars_by_field
    )
    has_threshold = any(
        key in record
        for key in (
            "threshold",
            "threshold_passed",
            "threshold_result",
            "metric_thresholds",
            "artifact_output_checks",
        )
    )
    if not has_threshold:
        return ""
    parts = ["configured_stage_check"]
    for label, value, max_chars in (
        ("name", record.get("name"), 80),
        ("local_valid", record.get("local_valid"), 40),
        ("threshold", record.get("threshold"), 40),
        ("threshold_passed", record.get("threshold_passed"), 40),
        ("stop_reason", record.get("stop_reason"), 100),
    ):
        if label not in selected_fields:
            continue
        text = _short_configured_stage_check_field(
            value,
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    threshold_result = record.get("threshold_result")
    if "threshold_result_passed" in selected_fields and isinstance(
        threshold_result,
        dict,
    ):
        text = _short_configured_stage_check_field(
            threshold_result.get("passed"),
            "threshold_result_passed",
            field_caps,
            default_max_chars=40,
        )
        if text:
            parts.append(f"threshold_result_passed={_json_text(text)}")
    if "metric_thresholds" in selected_fields:
        metric_checks = _render_stage_metric_threshold_checks(
            record.get("metric_thresholds"),
            fields=stage_metric_threshold_fields,
            max_chars_by_field=stage_metric_threshold_max_chars_by_field,
        )
        metric_text = (
            _short_configured_stage_check_field(
                metric_checks,
                "metric_thresholds",
                field_caps,
                default_max_chars=180,
            )
            if "metric_thresholds" in field_caps
            else metric_checks
        )
        if metric_text:
            parts.append(f"metric_thresholds={_json_text(metric_text)}")
    if "artifact_output_checks" in selected_fields:
        artifact_checks = _render_artifact_output_checks(
            record.get("artifact_output_checks"),
            fields=artifact_output_check_fields,
            max_chars_by_field=artifact_output_check_max_chars_by_field,
        )
        artifact_text = (
            _short_configured_stage_check_field(
                artifact_checks,
                "artifact_output_checks",
                field_caps,
                default_max_chars=180,
            )
            if "artifact_output_checks" in field_caps
            else artifact_checks
        )
        if artifact_text:
            parts.append(f"artifact_output_checks={_json_text(artifact_text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_configured_stage_check_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_stage_metric_threshold_checks(
    records: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(records, list) or not records:
        return ""
    selected_fields = set(_validate_prompt_context_stage_metric_threshold_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_stage_metric_threshold_max_chars_by_field(
        max_chars_by_field
    )
    rendered: list[str] = []
    for record in records[:_MAX_FEEDBACK_ITEMS]:
        if not isinstance(record, dict):
            continue
        items = []
        metric = _short_stage_metric_threshold_field(
            record.get("metric"),
            "metric",
            field_caps,
            default_max_chars=60,
        )
        if metric and "metric" in selected_fields:
            items.append(metric)
        for key in ("value", "min", "max", "passed", "reason"):
            if key not in selected_fields:
                continue
            text = _short_stage_metric_threshold_field(
                record.get(key),
                key,
                field_caps,
                default_max_chars=60,
            )
            if text:
                items.append(f"{key}:{text}")
        if items:
            rendered.append("/".join(items))
    if len(records) > _MAX_FEEDBACK_ITEMS:
        rendered.append(f"omitted:{len(records) - _MAX_FEEDBACK_ITEMS}")
    return "|".join(rendered)


def _short_stage_metric_threshold_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_artifact_output_checks(
    records: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(records, list) or not records:
        return ""
    selected_fields = set(_validate_prompt_context_artifact_output_check_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_artifact_output_check_max_chars_by_field(
        max_chars_by_field
    )
    rendered: list[str] = []
    for record in records[:_MAX_FEEDBACK_ITEMS]:
        if not isinstance(record, dict):
            continue
        items = []
        check_type = _short_artifact_output_check_field(
            record.get("type"),
            "type",
            field_caps,
            default_max_chars=60,
        )
        if check_type and "type" in selected_fields:
            items.append(check_type)
        for key in (
            "passed",
            "reason",
            "path",
            "expected",
            "actual",
            "pattern",
            "count",
            "min",
            "present",
        ):
            if key not in selected_fields:
                continue
            text = _short_artifact_output_check_field(
                record.get(key),
                key,
                field_caps,
                default_max_chars=80,
            )
            if text:
                items.append(f"{key}:{text}")
        if items:
            rendered.append("/".join(items))
    if len(records) > _MAX_FEEDBACK_ITEMS:
        rendered.append(f"omitted:{len(records) - _MAX_FEEDBACK_ITEMS}")
    return "|".join(rendered)


def _short_artifact_output_check_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_validator_boundary_diagnostic(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
    resource_limit_fields: object = None,
    resource_limit_max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(_validate_prompt_context_validator_boundary_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_validator_boundary_max_chars_by_field(
        max_chars_by_field
    )
    parts = ["validator_boundary"]
    for label, value, max_chars in (
        ("policy", record.get("policy"), 80),
        ("execution", record.get("execution"), 80),
        ("security_sandbox", record.get("security_sandbox"), 60),
        ("container", record.get("container"), 60),
        ("filesystem", record.get("filesystem_capability_model"), 120),
        ("network_policy", record.get("network_policy"), 40),
        ("network_egress", record.get("network_egress"), 80),
        ("network_denial", record.get("network_denial"), 80),
        ("network_denial_scope", record.get("network_denial_scope"), 120),
        ("secret_boundary", record.get("secret_boundary"), 120),
    ):
        if label not in selected_fields:
            continue
        text = _short_validator_boundary_field(
            value,
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    limits = record.get("resource_limits")
    if "resource_limits" in selected_fields and isinstance(limits, dict):
        selected_limit_fields = set(
            _validate_prompt_context_validator_resource_limit_fields(
                resource_limit_fields
            )
        )
        limit_field_caps = (
            _validate_prompt_context_validator_resource_limit_max_chars_by_field(
                resource_limit_max_chars_by_field
            )
        )
        limit_parts = []
        for key in ("wall_clock_timeout", "cpu", "memory", "gpu", "disk", "process_count"):
            if key not in selected_limit_fields:
                continue
            text = _short_validator_resource_limit_field(
                limits.get(key),
                key,
                limit_field_caps,
                default_max_chars=60,
            )
            if text:
                limit_parts.append(f"{key}:{text}")
        if limit_parts:
            parts.append(f"resource_limits={_json_text('|'.join(limit_parts))}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _render_validator_stdin_diagnostic(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(_validate_prompt_context_validator_stdin_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_validator_stdin_max_chars_by_field(
        max_chars_by_field
    )
    parts = ["stdin"]
    for label, value, max_chars in (
        ("policy", record.get("policy"), 60),
        ("interactive_input", record.get("interactive_input"), 80),
        ("generated_input", record.get("generated_input"), 80),
        ("source", record.get("source"), 120),
        ("chars", record.get("chars"), 40),
        ("bytes", record.get("bytes"), 40),
        ("sha256", record.get("sha256"), 64),
        ("text_retained", record.get("text_retained"), 40),
    ):
        if label not in selected_fields:
            continue
        text = _short_validator_stdin_field(
            value,
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            if label == "sha256":
                text = text[:12]
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _render_validator_budget_diagnostic(
    stage_budget: object,
    sample_budget: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    selected_fields = set(_validate_prompt_context_validator_budget_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_validator_budget_max_chars_by_field(
        max_chars_by_field
    )
    parts: list[str] = []
    for prefix, record in (
        ("stage_budget", stage_budget),
        ("sample_budget", sample_budget),
    ):
        if not isinstance(record, dict):
            continue
        record_parts = [prefix]
        for label, value, max_chars in (
            ("policy", record.get("policy"), 80),
            ("max_stage_seconds", record.get("max_stage_seconds"), 40),
            ("max_sample_seconds", record.get("max_sample_seconds"), 40),
            ("elapsed_sec", record.get("elapsed_sec"), 40),
            ("remaining_sec", record.get("remaining_sec"), 40),
            ("exhausted", record.get("exhausted"), 40),
        ):
            if label not in selected_fields:
                continue
            text = _short_validator_budget_field(
                value,
                label,
                field_caps,
                default_max_chars=max_chars,
            )
            if text:
                record_parts.append(f"{label}={_json_text(text)}")
        if len(record_parts) > 1:
            parts.append(" ".join(record_parts))
    return "- validator_budget " + "; ".join(parts) if parts else ""


def _render_validator_env_diagnostic(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(_validate_prompt_context_validator_env_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_validator_env_max_chars_by_field(
        max_chars_by_field
    )
    parts = ["validator_env"]
    for label, value, max_chars in (
        ("policy", record.get("policy"), 80),
        ("default_keys", record.get("default_keys"), 160),
        ("allowlist", record.get("allowlist"), 160),
        ("provided_keys", record.get("provided_keys"), 240),
        ("values_redacted", record.get("values_redacted"), 40),
    ):
        if label not in selected_fields:
            continue
        text = _short_validator_env_field(
            value,
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_validator_boundary_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _short_validator_budget_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _short_validator_env_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _short_validator_stdin_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _short_validator_resource_limit_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_diagnostic_output_policy(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(_validate_prompt_context_diagnostic_output_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_diagnostic_output_max_chars_by_field(
        max_chars_by_field
    )
    parts = ["diagnostic_output"]
    for label, value, max_chars in (
        ("encoding", record.get("encoding"), 60),
        ("stdout_bytes", record.get("stdout_bytes"), 40),
        ("stderr_bytes", record.get("stderr_bytes"), 40),
        ("stdout_replacement_count", record.get("stdout_replacement_count"), 40),
        ("stderr_replacement_count", record.get("stderr_replacement_count"), 40),
        ("max_chars", record.get("max_chars"), 40),
        ("stdout_truncated", record.get("stdout_truncated"), 40),
        ("stderr_truncated", record.get("stderr_truncated"), 40),
        ("redacted", record.get("redacted"), 40),
    ):
        if label not in selected_fields:
            continue
        text = _short_diagnostic_output_field(
            value,
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_diagnostic_output_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_timeout_cleanup_diagnostic(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(_validate_prompt_context_timeout_cleanup_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_timeout_cleanup_max_chars_by_field(
        max_chars_by_field
    )
    parts = ["timeout_cleanup"]
    for label, value, max_chars in (
        ("method", record.get("method"), 80),
        ("status", record.get("status"), 80),
        ("process_group", record.get("process_group"), 60),
        ("job_object", record.get("job_object"), 80),
        ("reported_child_pids", record.get("reported_child_pids"), 120),
        ("error", record.get("error"), 160),
    ):
        if label not in selected_fields:
            continue
        text = _short_timeout_cleanup_field(
            value,
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_timeout_cleanup_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_syntax_diagnostics(
    records: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> list[str]:
    if not isinstance(records, list) or not records:
        return []
    selected_fields = set(_validate_prompt_context_syntax_error_fields(fields))
    field_caps = _validate_prompt_context_syntax_error_max_chars_by_field(
        max_chars_by_field
    )
    lines: list[str] = []
    for record in records[:_MAX_FEEDBACK_ITEMS]:
        if not isinstance(record, dict):
            continue
        parts = ["syntax_error"]
        for label, value, max_chars in (
            ("path", record.get("path"), 160),
            ("line", record.get("line"), 24),
            ("offset", record.get("offset"), 24),
            ("message", record.get("message"), 160),
        ):
            if label not in selected_fields:
                continue
            text = _short_syntax_error_field(
                value,
                label,
                field_caps,
                default_max_chars=max_chars,
            )
            if text:
                parts.append(f"{label}={_json_text(text)}")
        if len(parts) > 1:
            lines.append("- " + ", ".join(parts))
    if len(records) > _MAX_FEEDBACK_ITEMS:
        lines.append(f"- syntax_errors_omitted={len(records) - _MAX_FEEDBACK_ITEMS}")
    return lines


def _short_syntax_error_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_metric_bound_diagnostics(
    records: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> list[str]:
    if not isinstance(records, list) or not records:
        return []
    selected_fields = set(_validate_prompt_context_metric_bound_fields(fields))
    if not selected_fields:
        return []
    field_caps = _validate_prompt_context_metric_bound_max_chars_by_field(
        max_chars_by_field
    )
    lines: list[str] = []
    for record in records[:_MAX_FEEDBACK_ITEMS]:
        if not isinstance(record, dict):
            continue
        metric = _short_metric_bound_field(
            record.get("metric"),
            "metric",
            field_caps,
            default_max_chars=80,
        )
        parts = []
        if metric and "metric" in selected_fields:
            parts.append(f"metric_bound={_json_text(metric)}")
        for label, value, max_chars in (
            ("value", record.get("value"), 80),
            ("bounds", record.get("bounds"), 120),
            ("direction", record.get("direction"), 24),
            ("normalized", record.get("normalized"), 80),
            ("clamped", record.get("clamped"), 24),
        ):
            if label not in selected_fields:
                continue
            text = _short_metric_bound_field(
                value,
                label,
                field_caps,
                default_max_chars=max_chars,
            )
            if text:
                parts.append(f"{label}={_json_text(text)}")
        if parts:
            lines.append("- " + ", ".join(parts))
    if len(records) > _MAX_FEEDBACK_ITEMS:
        lines.append(f"- metric_bound_diagnostics_omitted={len(records) - _MAX_FEEDBACK_ITEMS}")
    return lines


def _short_metric_bound_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_malformed_metric_diagnostic(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(_validate_prompt_context_malformed_metric_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_malformed_metric_max_chars_by_field(
        max_chars_by_field
    )
    parts = ["malformed_metrics"]
    for label, value, max_chars in (
        ("reason", record.get("reason"), 80),
        ("message", record.get("message"), 220),
    ):
        if label not in selected_fields:
            continue
        text = _short_malformed_metric_field(
            value,
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_malformed_metric_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_evaluator_dependency_diagnostic(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(
        _validate_prompt_context_evaluator_dependency_fields(fields)
    )
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_evaluator_dependency_max_chars_by_field(
        max_chars_by_field
    )
    files = record.get("files")
    if not isinstance(files, list):
        files = []
    file_paths = [
        str(item.get("path"))
        for item in files
        if isinstance(item, dict) and item.get("path") is not None
    ]
    file_hashes = [
        str(item.get("path_hash"))
        for item in files
        if isinstance(item, dict) and item.get("path_hash") is not None
    ]
    file_redactions = [
        str(item.get("path_redacted"))
        for item in files
        if isinstance(item, dict) and item.get("path_redacted") is not None
    ]
    values = {
        "policy": record.get("policy"),
        "allowed_scope": record.get("allowed_scope"),
        "outside_problem_policy": record.get("outside_problem_policy"),
        "file_count": record.get("file_count"),
        "file_paths": file_paths,
        "file_hashes": file_hashes,
        "file_redactions": file_redactions,
    }
    parts = ["evaluator_dependency"]
    for label, max_chars in (
        ("policy", 120),
        ("allowed_scope", 160),
        ("outside_problem_policy", 120),
        ("file_count", 40),
        ("file_paths", 320),
        ("file_hashes", 320),
        ("file_redactions", 120),
    ):
        if label not in selected_fields:
            continue
        text = _short_evaluator_dependency_field(
            values.get(label),
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_evaluator_dependency_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_evaluator_stage_diagnostic(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(_validate_prompt_context_evaluator_stage_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_evaluator_stage_max_chars_by_field(
        max_chars_by_field
    )
    config = record.get("config") if isinstance(record.get("config"), dict) else {}
    stdin = config.get("stdin") if isinstance(config.get("stdin"), dict) else {}
    evaluator_data = (
        record.get("evaluator_data")
        if isinstance(record.get("evaluator_data"), dict)
        else {}
    )
    values = {
        "name": record.get("name"),
        "stage_index": record.get("stage_index"),
        "sample_index": record.get("sample_index"),
        "attempt": record.get("attempt"),
        "seed": record.get("seed"),
        "validate_path": config.get("validate_path"),
        "stdin_policy": stdin.get("policy"),
        "evaluator_data_enabled": evaluator_data.get("enabled"),
        "evaluator_data_file_count": evaluator_data.get("file_count"),
    }
    parts = ["evaluator_stage"]
    for label, max_chars in (
        ("name", 120),
        ("stage_index", 40),
        ("sample_index", 40),
        ("attempt", 40),
        ("seed", 80),
        ("validate_path", 240),
        ("stdin_policy", 100),
        ("evaluator_data_enabled", 40),
        ("evaluator_data_file_count", 40),
    ):
        if label not in selected_fields:
            continue
        text = _short_evaluator_stage_field(
            values.get(label),
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_evaluator_stage_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_evaluator_workspace_diagnostic(
    metadata: dict,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    selected_fields = set(_validate_prompt_context_evaluator_workspace_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_evaluator_workspace_max_chars_by_field(
        max_chars_by_field
    )
    files = metadata.get("files")
    if not isinstance(files, list):
        files = []
    values = {
        "primary_file": metadata.get("primary_file"),
        "file_count": len(files),
        "files": files,
    }
    parts = ["evaluator_workspace"]
    for label, max_chars in (
        ("primary_file", 160),
        ("file_count", 40),
        ("files", 320),
    ):
        if label not in selected_fields:
            continue
        text = _short_evaluator_workspace_field(
            values.get(label),
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_evaluator_workspace_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_evaluator_path_diagnostic(
    metadata: dict,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    selected_fields = set(_validate_prompt_context_evaluator_path_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_evaluator_path_max_chars_by_field(
        max_chars_by_field
    )
    parts = ["evaluator_path"]
    for label, value, max_chars in (
        ("validate_path", metadata.get("validate_path"), 240),
        ("validate_path_scope", metadata.get("validate_path_scope"), 80),
        ("validate_path_hash", metadata.get("validate_path_hash"), 80),
        ("validate_path_redacted", metadata.get("validate_path_redacted"), 40),
    ):
        if label not in selected_fields:
            continue
        text = _short_evaluator_path_field(
            value,
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_evaluator_path_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_materialization_error_diagnostic(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(_validate_prompt_context_materialization_error_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_materialization_error_max_chars_by_field(
        max_chars_by_field
    )
    parts = ["materialization_error"]
    for label, value, max_chars in (
        ("exception_type", record.get("exception_type"), 100),
        ("reason", record.get("reason"), 100),
        ("paths", record.get("paths"), 240),
        ("message", record.get("message"), 240),
    ):
        if label not in selected_fields:
            continue
        text = _short_materialization_error_field(
            value,
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_materialization_error_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_metric_aggregation_diagnostic(
    metadata: dict,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    selected_fields = set(
        _validate_prompt_context_metric_aggregation_fields(fields)
    )
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_metric_aggregation_max_chars_by_field(
        max_chars_by_field
    )
    parts: list[str] = []
    sample_count = _short_metric_aggregation_field(
        metadata.get("sample_count"),
        "sample_count",
        field_caps,
        default_max_chars=24,
    )
    if sample_count and "sample_count" in selected_fields:
        parts.append(f"sample_count={_json_text(sample_count)}")
    attempt_count = _short_metric_aggregation_field(
        metadata.get("attempt_count"),
        "attempt_count",
        field_caps,
        default_max_chars=24,
    )
    if attempt_count and "attempt_count" in selected_fields:
        parts.append(f"attempt_count={_json_text(attempt_count)}")
    aggregation = _short_metric_aggregation_field(
        metadata.get("metric_aggregation"),
        "metric_aggregation",
        field_caps,
        default_max_chars=220,
    )
    if aggregation and "metric_aggregation" in selected_fields:
        parts.append(f"metric_aggregation={_json_text(aggregation)}")
    return "- " + ", ".join(parts) if parts else ""


def _short_metric_aggregation_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _render_synthetic_metric_diagnostic(
    record: object,
    *,
    fields: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not isinstance(record, dict):
        return ""
    selected_fields = set(_validate_prompt_context_synthetic_metric_fields(fields))
    if not selected_fields:
        return ""
    field_caps = _validate_prompt_context_synthetic_metric_max_chars_by_field(
        max_chars_by_field
    )
    parts = ["synthetic_metrics"]
    for label, value, max_chars in (
        ("schema", record.get("schema"), 80),
        ("policy", record.get("policy"), 80),
        ("penalty", record.get("penalty"), 40),
        ("metric_names", record.get("metric_names"), 240),
    ):
        if label not in selected_fields:
            continue
        text = _short_synthetic_metric_field(
            value,
            label,
            field_caps,
            default_max_chars=max_chars,
        )
        if text:
            parts.append(f"{label}={_json_text(text)}")
    return "- " + ", ".join(parts) if len(parts) > 1 else ""


def _short_synthetic_metric_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _json_text(value: object) -> str:
    return json.dumps("" if value is None else str(value))


def _short(value: object, max_chars: int = _MAX_FEEDBACK_FIELD_CHARS) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r\n", "\n").strip()
    if not text:
        return ""
    text = _redact_sensitive_text(text)
    return _truncate_text(text, max_chars).replace("\n", "\\n")


def _truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    notice = f"...[truncated {len(text) - max_chars} chars]"
    keep = max(0, max_chars - len(notice))
    return text[:keep] + notice


def _redact_sensitive_text(text: str) -> str:
    return redact_sensitive_text(text)


def _render_inspirations(
    inspirations: list[Program],
    problem: Problem | None = None,
    *,
    limit: int | None = None,
    artifact_base_dir: Path | None = None,
    artifact_content_mode: str = "excerpt",
    artifact_content_max_bytes: int = DEFAULT_PROMPT_ARTIFACT_CONTENT_MAX_BYTES,
    artifact_content_max_chars: int = DEFAULT_PROMPT_ARTIFACT_CONTENT_MAX_CHARS,
    llm_feedback_fields: object = None,
    llm_feedback_max_chars_by_field: object = None,
    proposal_fields: object = None,
    proposal_max_chars_by_field: object = None,
    stage_summary_fields: object = None,
    stage_summary_max_chars_by_field: object = None,
    execution_output_fields: object = None,
    execution_output_max_chars_by_field: object = None,
    sample_retry_fields: object = None,
    sample_retry_max_chars_by_field: object = None,
    program_output_fields: object = None,
    program_output_max_chars_by_field: object = None,
    validator_artifact_fields: object = None,
    validator_artifact_max_chars_by_field: object = None,
    validator_artifact_content_fields: object = None,
    validator_skipped_artifact_fields: object = None,
    validator_skipped_artifact_max_chars_by_field: object = None,
    validator_diagnostic_groups: object = None,
    validator_metadata_keys: object = None,
    validator_metadata_limit: object = None,
    validator_metadata_max_chars_by_key: object = None,
    evaluator_path_fields: object = None,
    evaluator_path_max_chars_by_field: object = None,
    evaluator_dependency_fields: object = None,
    evaluator_dependency_max_chars_by_field: object = None,
    evaluator_stage_fields: object = None,
    evaluator_stage_max_chars_by_field: object = None,
    evaluator_workspace_fields: object = None,
    evaluator_workspace_max_chars_by_field: object = None,
    syntax_error_fields: object = None,
    syntax_error_max_chars_by_field: object = None,
    metric_bound_fields: object = None,
    metric_bound_max_chars_by_field: object = None,
    configured_stage_check_fields: object = None,
    configured_stage_check_max_chars_by_field: object = None,
    stage_metric_threshold_fields: object = None,
    stage_metric_threshold_max_chars_by_field: object = None,
    artifact_output_check_fields: object = None,
    artifact_output_check_max_chars_by_field: object = None,
    malformed_metric_fields: object = None,
    malformed_metric_max_chars_by_field: object = None,
    materialization_error_fields: object = None,
    materialization_error_max_chars_by_field: object = None,
    metric_aggregation_fields: object = None,
    metric_aggregation_max_chars_by_field: object = None,
    synthetic_metric_fields: object = None,
    synthetic_metric_max_chars_by_field: object = None,
    execution_diagnostic_groups: object = None,
    validator_boundary_fields: object = None,
    validator_boundary_max_chars_by_field: object = None,
    validator_budget_fields: object = None,
    validator_budget_max_chars_by_field: object = None,
    validator_env_fields: object = None,
    validator_env_max_chars_by_field: object = None,
    validator_resource_limit_fields: object = None,
    validator_resource_limit_max_chars_by_field: object = None,
    validator_stdin_fields: object = None,
    validator_stdin_max_chars_by_field: object = None,
    diagnostic_output_fields: object = None,
    diagnostic_output_max_chars_by_field: object = None,
    timeout_cleanup_fields: object = None,
    timeout_cleanup_max_chars_by_field: object = None,
) -> str:
    rendered_inspirations = _selected_inspirations(inspirations, limit)
    if not rendered_inspirations:
        return "(none)"
    rendered = []
    for i, inspiration in enumerate(rendered_inspirations):
        proposal = _render_proposal(
            inspiration,
            fields=proposal_fields,
            max_chars_by_field=proposal_max_chars_by_field,
        )
        proposal_text = f"Proposal:\n{proposal}\n" if proposal else ""
        feedback = _render_feedback(
            inspiration,
            artifact_base_dir=artifact_base_dir,
            artifact_content_mode=artifact_content_mode,
            artifact_content_max_bytes=artifact_content_max_bytes,
            artifact_content_max_chars=artifact_content_max_chars,
            llm_feedback_fields=llm_feedback_fields,
            llm_feedback_max_chars_by_field=llm_feedback_max_chars_by_field,
            proposal_fields=proposal_fields,
            proposal_max_chars_by_field=proposal_max_chars_by_field,
            stage_summary_fields=stage_summary_fields,
            stage_summary_max_chars_by_field=stage_summary_max_chars_by_field,
            execution_output_fields=execution_output_fields,
            execution_output_max_chars_by_field=execution_output_max_chars_by_field,
            sample_retry_fields=sample_retry_fields,
            sample_retry_max_chars_by_field=sample_retry_max_chars_by_field,
            program_output_fields=program_output_fields,
            program_output_max_chars_by_field=program_output_max_chars_by_field,
            validator_artifact_fields=validator_artifact_fields,
            validator_artifact_max_chars_by_field=validator_artifact_max_chars_by_field,
            validator_artifact_content_fields=validator_artifact_content_fields,
            validator_skipped_artifact_fields=validator_skipped_artifact_fields,
            validator_skipped_artifact_max_chars_by_field=(
                validator_skipped_artifact_max_chars_by_field
            ),
            validator_diagnostic_groups=validator_diagnostic_groups,
            validator_metadata_keys=validator_metadata_keys,
            validator_metadata_limit=validator_metadata_limit,
            validator_metadata_max_chars_by_key=validator_metadata_max_chars_by_key,
            evaluator_path_fields=evaluator_path_fields,
            evaluator_path_max_chars_by_field=evaluator_path_max_chars_by_field,
            evaluator_dependency_fields=evaluator_dependency_fields,
            evaluator_dependency_max_chars_by_field=(
                evaluator_dependency_max_chars_by_field
            ),
            evaluator_stage_fields=evaluator_stage_fields,
            evaluator_stage_max_chars_by_field=evaluator_stage_max_chars_by_field,
            evaluator_workspace_fields=evaluator_workspace_fields,
            evaluator_workspace_max_chars_by_field=(
                evaluator_workspace_max_chars_by_field
            ),
            syntax_error_fields=syntax_error_fields,
            syntax_error_max_chars_by_field=syntax_error_max_chars_by_field,
            metric_bound_fields=metric_bound_fields,
            metric_bound_max_chars_by_field=metric_bound_max_chars_by_field,
            configured_stage_check_fields=configured_stage_check_fields,
            configured_stage_check_max_chars_by_field=(
                configured_stage_check_max_chars_by_field
            ),
            stage_metric_threshold_fields=stage_metric_threshold_fields,
            stage_metric_threshold_max_chars_by_field=(
                stage_metric_threshold_max_chars_by_field
            ),
            artifact_output_check_fields=artifact_output_check_fields,
            artifact_output_check_max_chars_by_field=(
                artifact_output_check_max_chars_by_field
            ),
            malformed_metric_fields=malformed_metric_fields,
            malformed_metric_max_chars_by_field=malformed_metric_max_chars_by_field,
            materialization_error_fields=materialization_error_fields,
            materialization_error_max_chars_by_field=(
                materialization_error_max_chars_by_field
            ),
            metric_aggregation_fields=metric_aggregation_fields,
            metric_aggregation_max_chars_by_field=metric_aggregation_max_chars_by_field,
            synthetic_metric_fields=synthetic_metric_fields,
            synthetic_metric_max_chars_by_field=synthetic_metric_max_chars_by_field,
            execution_diagnostic_groups=execution_diagnostic_groups,
            validator_boundary_fields=validator_boundary_fields,
            validator_boundary_max_chars_by_field=validator_boundary_max_chars_by_field,
            validator_budget_fields=validator_budget_fields,
            validator_budget_max_chars_by_field=validator_budget_max_chars_by_field,
            validator_env_fields=validator_env_fields,
            validator_env_max_chars_by_field=validator_env_max_chars_by_field,
            validator_resource_limit_fields=validator_resource_limit_fields,
            validator_resource_limit_max_chars_by_field=(
                validator_resource_limit_max_chars_by_field
            ),
            validator_stdin_fields=validator_stdin_fields,
            validator_stdin_max_chars_by_field=validator_stdin_max_chars_by_field,
            diagnostic_output_fields=diagnostic_output_fields,
            diagnostic_output_max_chars_by_field=diagnostic_output_max_chars_by_field,
            timeout_cleanup_fields=timeout_cleanup_fields,
            timeout_cleanup_max_chars_by_field=timeout_cleanup_max_chars_by_field,
        )
        feedback_text = (
            f"Evaluation feedback:\n{feedback}\n" if feedback != "(none)" else ""
        )
        rendered.append(
            f"\n--- Inspiration {i + 1} "
            f"(fitness {_fitness_text(inspiration.fitness)}; metrics: "
            f"{_render_metrics(inspiration, problem)}) ---\n"
            f"{proposal_text}{feedback_text}{_render_program_files(inspiration)}\n"
        )
    return "".join(rendered)


def _selected_inspirations(inspirations: list[Program], limit: int | None) -> list[Program]:
    if limit is None:
        return list(inspirations)
    if limit <= 0:
        return []
    return list(inspirations)[:limit]


def _inspiration_policy_metadata(
    inspirations: list[Program], limit: int | None
) -> dict[str, object]:
    available = len(inspirations)
    selected = len(_selected_inspirations(inspirations, limit))
    return {
        "schema": "libreevolve.inspiration_policy.v1",
        "limit": limit,
        "available_count": available,
        "rendered_count": selected,
        "omitted_count": max(0, available - selected),
        "selection_policy": (
            "all_selected_inspirations"
            if limit is None
            else "first_n_selected_inspirations"
        ),
    }


def _render_failures(
    recent_failures: object,
    *,
    limit: int | None = None,
    selection_policy: object = "recent",
    required_errors: object = None,
    excluded_errors: object = None,
    required_changed_files: object = None,
    excluded_changed_files: object = None,
    required_stage_names: object = None,
    excluded_stage_names: object = None,
    required_terms: object = None,
    excluded_terms: object = None,
    repetition_threshold: object = None,
    score_threshold: object = None,
    max_chars_by_field: object = None,
) -> str:
    if not recent_failures:
        return ""
    failure_selection_policy = _validate_prompt_context_recent_failure_selection_policy(
        selection_policy
    )
    failure_required_errors = _validate_prompt_context_recent_failure_required_errors(
        required_errors
    )
    failure_excluded_errors = _validate_prompt_context_recent_failure_excluded_errors(
        excluded_errors
    )
    failure_required_changed_files = (
        _validate_prompt_context_recent_failure_required_changed_files(
            required_changed_files
        )
    )
    failure_excluded_changed_files = (
        _validate_prompt_context_recent_failure_excluded_changed_files(
            excluded_changed_files
        )
    )
    failure_required_stage_names = (
        _validate_prompt_context_recent_failure_required_stage_names(
            required_stage_names
        )
    )
    failure_excluded_stage_names = (
        _validate_prompt_context_recent_failure_excluded_stage_names(
            excluded_stage_names
        )
    )
    failure_required_terms = _validate_prompt_context_source_terms(
        required_terms,
        "recent_failure_required_terms",
    )
    failure_excluded_terms = _validate_prompt_context_source_terms(
        excluded_terms,
        "recent_failure_excluded_terms",
    )
    failure_repetition_threshold = (
        _validate_prompt_context_recent_failure_repetition_threshold(
            repetition_threshold
        )
    )
    failure_score_threshold = _validate_prompt_context_recent_failure_score_threshold(
        score_threshold
    )
    field_caps = _validate_prompt_context_recent_failure_max_chars_by_field(
        max_chars_by_field
    )
    if not isinstance(recent_failures, (list, tuple)):
        diagnostic = _render_malformed_failure_record(
            "expected a list or tuple of records", recent_failures
        )
        return f"\n[RECENTLY FAILED - do NOT repeat these]\n{diagnostic}\n"
    rendered_failures = _selected_recent_failures(
        recent_failures,
        limit,
        failure_selection_policy,
        failure_required_errors,
        failure_excluded_errors,
        failure_required_changed_files,
        failure_excluded_changed_files,
        failure_required_stage_names,
        failure_excluded_stage_names,
        failure_required_terms,
        failure_excluded_terms,
        failure_repetition_threshold,
        failure_score_threshold,
    )
    if not rendered_failures:
        return ""
    lines = "\n".join(
        _render_failure_line(failure, field_caps) for failure in rendered_failures
    )
    return f"\n[RECENTLY FAILED - do NOT repeat these]\n{lines}\n"


def _selected_recent_failures(
    recent_failures: object,
    limit: int | None,
    selection_policy: object = "recent",
    required_errors: object = None,
    excluded_errors: object = None,
    required_changed_files: object = None,
    excluded_changed_files: object = None,
    required_stage_names: object = None,
    excluded_stage_names: object = None,
    required_terms: object = None,
    excluded_terms: object = None,
    repetition_threshold: object = None,
    score_threshold: object = None,
) -> list:
    if not isinstance(recent_failures, (list, tuple)):
        return []
    failure_selection_policy = _validate_prompt_context_recent_failure_selection_policy(
        selection_policy
    )
    failure_required_errors = _validate_prompt_context_recent_failure_required_errors(
        required_errors
    )
    failure_excluded_errors = _validate_prompt_context_recent_failure_excluded_errors(
        excluded_errors
    )
    failure_required_changed_files = (
        _validate_prompt_context_recent_failure_required_changed_files(
            required_changed_files
        )
    )
    failure_excluded_changed_files = (
        _validate_prompt_context_recent_failure_excluded_changed_files(
            excluded_changed_files
        )
    )
    failure_required_stage_names = (
        _validate_prompt_context_recent_failure_required_stage_names(
            required_stage_names
        )
    )
    failure_excluded_stage_names = (
        _validate_prompt_context_recent_failure_excluded_stage_names(
            excluded_stage_names
        )
    )
    failure_required_terms = _validate_prompt_context_source_terms(
        required_terms,
        "recent_failure_required_terms",
    )
    failure_excluded_terms = _validate_prompt_context_source_terms(
        excluded_terms,
        "recent_failure_excluded_terms",
    )
    failure_repetition_threshold = (
        _validate_prompt_context_recent_failure_repetition_threshold(
            repetition_threshold
        )
    )
    failure_score_threshold = _validate_prompt_context_recent_failure_score_threshold(
        score_threshold
    )
    retained_failures = _filter_recent_failures_by_excluded_stage_names(
        _filter_recent_failures_by_required_stage_names(
            _filter_recent_failures_by_excluded_changed_files(
                _filter_recent_failures_by_required_changed_files(
                    _filter_recent_failures_by_excluded_errors(
                        _filter_recent_failures_by_required_errors(
                            list(recent_failures), failure_required_errors
                        ),
                        failure_excluded_errors,
                    ),
                    failure_required_changed_files,
                ),
                failure_excluded_changed_files,
            ),
            failure_required_stage_names,
        ),
        failure_excluded_stage_names,
    )
    retained_failures = _filter_recent_failures_by_excluded_terms(
        _filter_recent_failures_by_required_terms(
            retained_failures,
            failure_required_terms,
        ),
        failure_excluded_terms,
    )
    retained_failures = _filter_recent_failures_by_score_threshold(
        _filter_recent_failures_by_repetition_threshold(
            retained_failures,
            failure_repetition_threshold,
        ),
        failure_score_threshold,
    )
    if failure_selection_policy == "recent":
        if limit is None:
            return retained_failures
        if limit <= 0:
            return []
        return retained_failures[-limit:]
    if limit is None:
        return _ordered_recent_failures(retained_failures, failure_selection_policy)
    if limit <= 0:
        return []
    ordered = _ordered_recent_failures(retained_failures, failure_selection_policy)
    return ordered[:limit]


def _filter_recent_failures_by_required_errors(
    failures: list,
    required_errors: list[str],
) -> list:
    if not required_errors:
        return list(failures)
    required = set(required_errors)
    return [
        failure
        for failure in failures
        if _recent_failure_matches_required_error(failure, required)
    ]


def _recent_failure_matches_required_error(
    failure: object,
    required_errors: set[str],
) -> bool:
    if not isinstance(failure, dict):
        return False
    return any(
        label in required_errors
        for label in _recent_failure_error_labels(failure)
    )


def _filter_recent_failures_by_excluded_errors(
    failures: list,
    excluded_errors: list[str],
) -> list:
    if not excluded_errors:
        return list(failures)
    excluded = set(excluded_errors)
    return [
        failure
        for failure in failures
        if not _recent_failure_matches_required_error(failure, excluded)
    ]


def _recent_failure_error_labels(failure: Mapping[str, object]) -> list[str]:
    labels: list[str] = []
    for key in ("error", "diff_error"):
        value = failure.get(key)
        if isinstance(value, str) and value:
            labels.append(value)
    return labels


def _filter_recent_failures_by_required_changed_files(
    failures: list,
    required_changed_files: list[str],
) -> list:
    if not required_changed_files:
        return list(failures)
    required = set(required_changed_files)
    return [
        failure
        for failure in failures
        if _recent_failure_matches_required_changed_file(failure, required)
    ]


def _recent_failure_matches_required_changed_file(
    failure: object,
    required_changed_files: set[str],
) -> bool:
    if not isinstance(failure, dict):
        return False
    changed_files = failure.get("changed_files")
    if not isinstance(changed_files, (list, tuple)):
        return False
    return any(
        path in required_changed_files
        for path in changed_files
        if isinstance(path, str)
    )


def _filter_recent_failures_by_excluded_changed_files(
    failures: list,
    excluded_changed_files: list[str],
) -> list:
    if not excluded_changed_files:
        return list(failures)
    excluded = set(excluded_changed_files)
    return [
        failure
        for failure in failures
        if not _recent_failure_matches_required_changed_file(failure, excluded)
    ]


def _filter_recent_failures_by_required_stage_names(
    failures: list,
    required_stage_names: list[str],
) -> list:
    if not required_stage_names:
        return list(failures)
    required = set(required_stage_names)
    return [
        failure
        for failure in failures
        if _recent_failure_matches_required_stage_name(failure, required)
    ]


def _recent_failure_matches_required_stage_name(
    failure: object,
    required_stage_names: set[str],
) -> bool:
    if not isinstance(failure, dict):
        return False
    evaluation = failure.get("evaluation")
    if not isinstance(evaluation, dict):
        return False
    stages = evaluation.get("stages")
    if not isinstance(stages, (list, tuple)):
        return False
    return any(
        name in required_stage_names
        for name in (
            stage.get("name")
            for stage in stages
            if isinstance(stage, dict)
        )
        if isinstance(name, str)
    )


def _filter_recent_failures_by_excluded_stage_names(
    failures: list,
    excluded_stage_names: list[str],
) -> list:
    if not excluded_stage_names:
        return list(failures)
    excluded = set(excluded_stage_names)
    return [
        failure
        for failure in failures
        if not _recent_failure_matches_required_stage_name(failure, excluded)
    ]


def _filter_recent_failures_by_required_terms(
    failures: list,
    required_terms: list[str],
) -> list:
    if not required_terms:
        return list(failures)
    required = set(required_terms)
    return [
        failure
        for failure in failures
        if required.issubset(_recent_failure_terms(failure))
    ]


def _filter_recent_failures_by_excluded_terms(
    failures: list,
    excluded_terms: list[str],
) -> list:
    if not excluded_terms:
        return list(failures)
    excluded = set(excluded_terms)
    return [
        failure
        for failure in failures
        if not _recent_failure_terms(failure).intersection(excluded)
    ]


def _recent_failure_terms(failure: object) -> set[str]:
    return {
        match.group(0).lower()
        for match in re.finditer(
            r"[A-Za-z0-9_]{3,}",
            json.dumps(str(failure), ensure_ascii=True),
        )
    }


def _filter_recent_failures_by_score_threshold(
    failures: list,
    score_threshold: dict[str, float | None] | None,
) -> list:
    if score_threshold is None:
        return list(failures)
    return [
        failure
        for failure in failures
        if _recent_failure_matches_score_threshold(failure, score_threshold)
    ]


def _recent_failure_matches_score_threshold(
    failure: object,
    score_threshold: dict[str, float | None],
) -> bool:
    score = _recent_failure_selection_score(failure)
    if not math.isfinite(score):
        return False
    minimum = score_threshold.get("min")
    maximum = score_threshold.get("max")
    if minimum is not None and score < minimum:
        return False
    if maximum is not None and score > maximum:
        return False
    return True


def _filter_recent_failures_by_repetition_threshold(
    failures: list,
    repetition_threshold: dict[str, int | None] | None,
) -> list:
    if repetition_threshold is None:
        return list(failures)
    return [
        failure
        for failure in failures
        if _recent_failure_matches_repetition_threshold(
            failure, repetition_threshold
        )
    ]


def _recent_failure_matches_repetition_threshold(
    failure: object,
    repetition_threshold: dict[str, int | None],
) -> bool:
    if not isinstance(failure, dict):
        return False
    repetition = failure.get("repetition_count", 1)
    if (
        isinstance(repetition, bool)
        or not isinstance(repetition, int)
        or repetition < 1
    ):
        return False
    minimum = repetition_threshold.get("min")
    maximum = repetition_threshold.get("max")
    if minimum is not None and repetition < minimum:
        return False
    if maximum is not None and repetition > maximum:
        return False
    return True


def _ordered_recent_failures(
    failures: list,
    selection_policy: str,
) -> list:
    if selection_policy == "oldest":
        return list(failures)
    if selection_policy == "lowest_score":
        return [
            failure
            for _, failure in sorted(
                enumerate(failures),
                key=lambda item: (
                    _recent_failure_selection_score(item[1]),
                    item[0],
                ),
            )
        ]
    if selection_policy == "highest_repetition":
        return [
            failure
            for _, failure in sorted(
                enumerate(failures),
                key=lambda item: (
                    -_recent_failure_repetition_count(item[1]),
                    item[0],
                ),
            )
        ]
    raise PromptTemplateError(
        "prompt context_policy.recent_failure_selection_policy is unsupported"
    )


def _recent_failure_selection_score(failure: object) -> float:
    score: object
    if isinstance(failure, dict):
        score = failure.get("score", failure.get("fitness"))
    elif _is_legacy_failure_tuple(failure):
        score = failure[1]
    else:
        score = None
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return math.inf
    numeric = float(score)
    if not math.isfinite(numeric):
        return math.inf
    return numeric


def _recent_failure_repetition_count(failure: object) -> int:
    if not isinstance(failure, dict):
        return 0
    repetition = failure.get("repetition_count", 1)
    if (
        isinstance(repetition, bool)
        or not isinstance(repetition, int)
        or repetition < 1
    ):
        return 0
    return repetition


def _failure_memory_policy_metadata(
    recent_failures: object,
    limit: int | None,
    selection_policy: object = "recent",
    required_errors: object = None,
    excluded_errors: object = None,
    required_changed_files: object = None,
    excluded_changed_files: object = None,
    required_stage_names: object = None,
    excluded_stage_names: object = None,
    required_terms: object = None,
    excluded_terms: object = None,
    repetition_threshold: object = None,
    score_threshold: object = None,
    max_chars_by_field: object = None,
) -> dict:
    failure_selection_policy = _validate_prompt_context_recent_failure_selection_policy(
        selection_policy
    )
    failure_required_errors = _validate_prompt_context_recent_failure_required_errors(
        required_errors
    )
    failure_excluded_errors = _validate_prompt_context_recent_failure_excluded_errors(
        excluded_errors
    )
    failure_required_changed_files = (
        _validate_prompt_context_recent_failure_required_changed_files(
            required_changed_files
        )
    )
    failure_excluded_changed_files = (
        _validate_prompt_context_recent_failure_excluded_changed_files(
            excluded_changed_files
        )
    )
    failure_required_stage_names = (
        _validate_prompt_context_recent_failure_required_stage_names(
            required_stage_names
        )
    )
    failure_excluded_stage_names = (
        _validate_prompt_context_recent_failure_excluded_stage_names(
            excluded_stage_names
        )
    )
    failure_required_terms = _validate_prompt_context_source_terms(
        required_terms,
        "recent_failure_required_terms",
    )
    failure_excluded_terms = _validate_prompt_context_source_terms(
        excluded_terms,
        "recent_failure_excluded_terms",
    )
    failure_repetition_threshold = (
        _validate_prompt_context_recent_failure_repetition_threshold(
            repetition_threshold
        )
    )
    failure_score_threshold = _validate_prompt_context_recent_failure_score_threshold(
        score_threshold
    )
    available = (
        len(recent_failures)
        if isinstance(recent_failures, (list, tuple))
        else 0
    )
    matching = len(
        _filter_recent_failures_by_required_errors(
            list(recent_failures)
            if isinstance(recent_failures, (list, tuple))
            else [],
            failure_required_errors,
        )
    )
    error_filtered_failures = _filter_recent_failures_by_required_errors(
        list(recent_failures)
        if isinstance(recent_failures, (list, tuple))
        else [],
        failure_required_errors,
    )
    excluded_error_filtered_failures = _filter_recent_failures_by_excluded_errors(
        error_filtered_failures, failure_excluded_errors
    )
    changed_file_filtered_failures = _filter_recent_failures_by_required_changed_files(
        excluded_error_filtered_failures, failure_required_changed_files
    )
    excluded_changed_file_filtered_failures = (
        _filter_recent_failures_by_excluded_changed_files(
            changed_file_filtered_failures, failure_excluded_changed_files
        )
    )
    stage_name_filtered_failures = _filter_recent_failures_by_required_stage_names(
        excluded_changed_file_filtered_failures, failure_required_stage_names
    )
    excluded_stage_name_filtered_failures = (
        _filter_recent_failures_by_excluded_stage_names(
            stage_name_filtered_failures, failure_excluded_stage_names
        )
    )
    required_term_filtered_failures = _filter_recent_failures_by_required_terms(
        excluded_stage_name_filtered_failures,
        failure_required_terms,
    )
    excluded_term_filtered_failures = _filter_recent_failures_by_excluded_terms(
        required_term_filtered_failures,
        failure_excluded_terms,
    )
    repetition_matching_failures = _filter_recent_failures_by_repetition_threshold(
        excluded_term_filtered_failures, failure_repetition_threshold
    )
    score_matching = len(
        _filter_recent_failures_by_score_threshold(
            repetition_matching_failures, failure_score_threshold
        )
    )
    selected = len(
        _selected_recent_failures(
            recent_failures,
            limit,
            failure_selection_policy,
            failure_required_errors,
            failure_excluded_errors,
            failure_required_changed_files,
            failure_excluded_changed_files,
            failure_required_stage_names,
            failure_excluded_stage_names,
            failure_required_terms,
            failure_excluded_terms,
            failure_repetition_threshold,
            failure_score_threshold,
        )
    )
    metadata = {
        "schema": "libreevolve.failure_memory_policy.v1",
        "limit": limit,
        "selection_policy": failure_selection_policy,
        "required_errors": list(failure_required_errors),
        "required_error_matching_count": matching,
        "required_error_filtered_count": max(0, available - matching),
        "required_error_policy": (
            "error_or_diff_error_exact_match_v1"
            if failure_required_errors
            else "none"
        ),
        "excluded_errors": list(failure_excluded_errors),
        "excluded_error_matching_count": max(
            0, len(error_filtered_failures) - len(excluded_error_filtered_failures)
        ),
        "excluded_error_filtered_count": max(
            0, len(error_filtered_failures) - len(excluded_error_filtered_failures)
        ),
        "excluded_error_policy": (
            "error_or_diff_error_exact_exclusion_v1"
            if failure_excluded_errors
            else "none"
        ),
        "required_changed_files": list(failure_required_changed_files),
        "required_changed_file_matching_count": len(changed_file_filtered_failures),
        "required_changed_file_filtered_count": max(
            0,
            len(excluded_error_filtered_failures)
            - len(changed_file_filtered_failures),
        ),
        "required_changed_file_policy": (
            "changed_file_exact_match_v1"
            if failure_required_changed_files
            else "none"
        ),
        "excluded_changed_files": list(failure_excluded_changed_files),
        "excluded_changed_file_matching_count": max(
            0,
            len(changed_file_filtered_failures)
            - len(excluded_changed_file_filtered_failures),
        ),
        "excluded_changed_file_filtered_count": max(
            0,
            len(changed_file_filtered_failures)
            - len(excluded_changed_file_filtered_failures),
        ),
        "excluded_changed_file_policy": (
            "changed_file_exact_exclusion_v1"
            if failure_excluded_changed_files
            else "none"
        ),
        "required_stage_names": list(failure_required_stage_names),
        "required_stage_name_matching_count": len(stage_name_filtered_failures),
        "required_stage_name_filtered_count": max(
            0,
            len(excluded_changed_file_filtered_failures)
            - len(stage_name_filtered_failures),
        ),
        "required_stage_name_policy": (
            "evaluation_stage_name_exact_match_v1"
            if failure_required_stage_names
            else "none"
        ),
        "excluded_stage_names": list(failure_excluded_stage_names),
        "excluded_stage_name_matching_count": max(
            0,
            len(stage_name_filtered_failures)
            - len(excluded_stage_name_filtered_failures),
        ),
        "excluded_stage_name_filtered_count": max(
            0,
            len(stage_name_filtered_failures)
            - len(excluded_stage_name_filtered_failures),
        ),
        "excluded_stage_name_policy": (
            "evaluation_stage_name_exact_exclusion_v1"
            if failure_excluded_stage_names
            else "none"
        ),
        "repetition_threshold": (
            dict(failure_repetition_threshold)
            if failure_repetition_threshold is not None
            else None
        ),
        "repetition_threshold_matching_count": len(repetition_matching_failures),
        "repetition_threshold_filtered_count": max(
            0,
            len(excluded_changed_file_filtered_failures)
            - len(repetition_matching_failures),
        ),
        "repetition_threshold_policy": (
            "repetition_count_threshold_filter_v1"
            if failure_repetition_threshold is not None
            else "none"
        ),
        "score_threshold": (
            dict(failure_score_threshold)
            if failure_score_threshold is not None
            else None
        ),
        "score_threshold_matching_count": score_matching,
        "score_threshold_filtered_count": max(
            0, len(repetition_matching_failures) - score_matching
        ),
        "score_threshold_policy": (
            "finite_score_threshold_filter_v1"
            if failure_score_threshold is not None
            else "none"
        ),
        "max_chars_by_field": dict(
            _validate_prompt_context_recent_failure_max_chars_by_field(
                max_chars_by_field
            )
        ),
        "available_count": available,
        "rendered_count": selected,
        "omitted_count": max(0, available - selected),
        "selection_semantics": _recent_failure_selection_semantics(
            failure_selection_policy, limit
        ),
    }
    if failure_required_terms or failure_excluded_terms:
        metadata.update(
            {
                "required_terms": list(failure_required_terms),
                "required_term_matching_count": len(required_term_filtered_failures),
                "required_term_filtered_count": max(
                    0,
                    len(excluded_stage_name_filtered_failures)
                    - len(required_term_filtered_failures),
                ),
                "required_term_policy": (
                    "failure_record_all_terms_match_v1"
                    if failure_required_terms
                    else "none"
                ),
                "excluded_terms": list(failure_excluded_terms),
                "excluded_term_matching_count": max(
                    0,
                    len(required_term_filtered_failures)
                    - len(excluded_term_filtered_failures),
                ),
                "excluded_term_filtered_count": max(
                    0,
                    len(required_term_filtered_failures)
                    - len(excluded_term_filtered_failures),
                ),
                "excluded_term_policy": (
                    "failure_record_any_term_exclusion_v1"
                    if failure_excluded_terms
                    else "none"
                ),
            }
        )
    return metadata


def _recent_failure_selection_semantics(
    selection_policy: str,
    limit: int | None,
) -> str:
    if limit is None:
        suffix = "all_retained_failures"
    else:
        suffix = "limited_retained_failures"
    return f"{selection_policy}_{suffix}"


def _render_failure_line(
    failure: object,
    max_chars_by_field: Mapping[str, int],
) -> str:
    if isinstance(failure, dict):
        return _render_structured_failure_line(failure, max_chars_by_field)
    if _is_legacy_failure_tuple(failure):
        code, score = failure
        snippet = _short_recent_failure_field(
            code,
            "mutation",
            max_chars_by_field,
            default_max_chars=160,
        ) or "(empty)"
        return f"  Score {_failure_score_text(score)}: mutation={snippet}"
    return _render_malformed_failure_record(
        "expected mapping or 2-item legacy tuple", failure
    )


def _render_structured_failure_line(
    failure: dict,
    max_chars_by_field: Mapping[str, int],
) -> str:
    score = failure.get("score")
    score_text = _failure_score_text(score)
    error = _short_recent_failure_field(
        failure.get("error") or failure.get("diff_error") or "invalid",
        "error",
        max_chars_by_field,
        default_max_chars=120,
    )
    diff_error = _short_recent_failure_field(
        failure.get("diff_error"),
        "diff_error",
        max_chars_by_field,
        default_max_chars=120,
    )
    changed_text = _failure_changed_files_text(
        failure.get("changed_files"),
        max_chars_by_field,
    )
    repeat = _failure_repeat_text(failure.get("repetition_count", 1))
    mutation = _short_recent_failure_field(
        failure.get("mutation_text"),
        "mutation",
        max_chars_by_field,
        default_max_chars=160,
    )
    suffix = f"; diff_error={diff_error}" if diff_error else ""
    evaluation = _render_failure_evaluation(
        failure.get("evaluation"),
        max_chars_by_field,
    )
    eval_suffix = f"; eval={evaluation}" if evaluation else ""
    return (
        f"  Score {score_text}: error={error}{suffix}; "
        f"changed_files={changed_text}; repeats={repeat}; mutation={mutation}"
        f"{eval_suffix}"
    )


def _is_legacy_failure_tuple(failure: object) -> bool:
    if not isinstance(failure, tuple):
        return False
    return len(failure) == 2


def _render_malformed_failure_record(reason: str, value: object) -> str:
    return (
        "  malformed recent_failure record skipped: "
        f"{reason}; type={type(value).__name__}"
    )


def _short_recent_failure_field(
    value: object,
    field: str,
    max_chars_by_field: Mapping[str, int],
    *,
    default_max_chars: int,
) -> str:
    max_chars = max_chars_by_field.get(field)
    if max_chars == 0:
        return ""
    return _short(
        value,
        max_chars=max_chars if max_chars is not None else default_max_chars,
    )


def _failure_changed_files_text(
    changed_files: object,
    max_chars_by_field: Mapping[str, int],
) -> str:
    if not changed_files:
        return "(none)"
    if not isinstance(changed_files, (list, tuple)):
        return "(malformed)"
    files = [
        _short_recent_failure_field(
            path,
            "changed_file",
            max_chars_by_field,
            default_max_chars=80,
        )
        for path in changed_files
        if isinstance(path, str) and path.strip()
    ]
    return ",".join(files) if files else "(malformed)"


def _failure_repeat_text(repetition_count: object) -> str:
    if isinstance(repetition_count, bool) or not isinstance(repetition_count, int):
        return "unknown"
    if repetition_count < 1:
        return "unknown"
    return str(repetition_count)


def _failure_score_text(score: object) -> str:
    if isinstance(score, bool) or not isinstance(score, (int, float)):
        return "unknown"
    numeric = float(score)
    if not math.isfinite(numeric):
        return "unknown"
    return f"{numeric:.2f}"


def _render_failure_evaluation(
    evaluation: object,
    max_chars_by_field: Mapping[str, int],
) -> str:
    if not isinstance(evaluation, dict):
        return ""
    parts: list[str] = []
    error = _short_recent_failure_field(
        evaluation.get("error"),
        "evaluation_error",
        max_chars_by_field,
        default_max_chars=120,
    )
    if error:
        parts.append(f"error={error}")
    stdout = _short_recent_failure_field(
        evaluation.get("stdout"),
        "evaluation_stdout",
        max_chars_by_field,
        default_max_chars=160,
    )
    if stdout:
        parts.append(f"stdout={stdout}")
    stderr = _short_recent_failure_field(
        evaluation.get("stderr"),
        "evaluation_stderr",
        max_chars_by_field,
        default_max_chars=160,
    )
    if stderr:
        parts.append(f"stderr={stderr}")
    stages = evaluation.get("stages")
    if isinstance(stages, list):
        stage_parts = []
        for stage in stages[-_MAX_FEEDBACK_ITEMS:]:
            if not isinstance(stage, dict):
                continue
            name = _short_recent_failure_field(
                stage.get("name"),
                "stage_name",
                max_chars_by_field,
                default_max_chars=60,
            ) or "stage"
            passed = stage.get("passed")
            status = "passed" if passed is True else "failed" if passed is False else "unknown"
            score = stage.get("score")
            score_text = f",score={score}" if isinstance(score, (int, float)) else ""
            stage_error = _short_recent_failure_field(
                stage.get("error"),
                "stage_error",
                max_chars_by_field,
                default_max_chars=80,
            )
            error_text = f",error={stage_error}" if stage_error else ""
            stage_parts.append(f"{name}:{status}{score_text}{error_text}")
        if stage_parts:
            parts.append("stages=" + "|".join(stage_parts))
    metadata = evaluation.get("metadata")
    diagnostics = _render_validator_diagnostics(metadata)
    if diagnostics:
        diagnostics = _short_recent_failure_field(
            diagnostics,
            "diagnostics",
            max_chars_by_field,
            default_max_chars=240,
        )
        if diagnostics:
            parts.append("diagnostics=" + diagnostics)
    llm_feedback_records = evaluation.get("llm_feedback")
    if llm_feedback_records is None and isinstance(metadata, dict):
        llm_feedback_records = metadata.get("llm_feedback")
    llm_feedback = _render_llm_feedback(llm_feedback_records)
    if llm_feedback:
        llm_feedback = _short_recent_failure_field(
            llm_feedback,
            "llm_feedback",
            max_chars_by_field,
            default_max_chars=240,
        )
        if llm_feedback:
            parts.append("llm_feedback=" + llm_feedback)
    return _short_recent_failure_field(
        "; ".join(parts),
        "evaluation",
        max_chars_by_field,
        default_max_chars=360,
    )
